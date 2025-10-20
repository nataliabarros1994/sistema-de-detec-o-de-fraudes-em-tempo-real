"""
Cliente Redis para Cache e Storage
===================================
Este módulo gerencia a conexão com Redis para cache de predições e
armazenamento de histórico de transações.

Redis é usado para:
1. Cache de predições recentes (evita reprocessamento)
2. Storage de histórico de transações por usuário
3. Contadores de métricas em tempo real

Autor: Natália Barros
Data: 2025
"""

import redis
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.models import Transaction, FraudPrediction, UserHistory

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedisClient:
    """
    Cliente Redis para operações de cache e storage

    Gerencia:
    - Conexão com Redis
    - Cache de predições
    - Histórico de transações
    - Métricas de sistema
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True
    ):
        """
        Inicializa a conexão com Redis

        Args:
            host: Endereço do servidor Redis
            port: Porta do servidor Redis
            db: Número do database Redis (0-15)
            password: Senha para autenticação (opcional)
            decode_responses: Se True, retorna strings ao invés de bytes
        """
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Testa a conexão
            self.client.ping()
            logger.info(f"✅ Conectado ao Redis em {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"❌ Erro ao conectar ao Redis: {e}")
            raise

    def is_healthy(self) -> bool:
        """
        Verifica se a conexão com Redis está saudável

        Returns:
            True se conectado, False caso contrário
        """
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False

    # ==================== CACHE DE PREDIÇÕES ====================

    def cache_prediction(
        self,
        transaction_id: str,
        prediction: FraudPrediction,
        ttl: int = 3600
    ) -> bool:
        """
        Armazena uma predição no cache

        Args:
            transaction_id: ID da transação
            prediction: Objeto FraudPrediction
            ttl: Tempo de vida do cache em segundos (default: 1 hora)

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            key = f"prediction:{transaction_id}"
            value = prediction.model_dump_json()
            self.client.setex(key, ttl, value)
            logger.info(f"💾 Predição cacheada: {transaction_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao cachear predição: {e}")
            return False

    def get_cached_prediction(
        self,
        transaction_id: str
    ) -> Optional[FraudPrediction]:
        """
        Recupera uma predição do cache

        Args:
            transaction_id: ID da transação

        Returns:
            FraudPrediction se encontrado, None caso contrário
        """
        try:
            key = f"prediction:{transaction_id}"
            cached = self.client.get(key)

            if cached:
                logger.info(f"🎯 Cache hit: {transaction_id}")
                # Incrementa contador de cache hits
                self.client.incr("metrics:cache_hits")
                return FraudPrediction.model_validate_json(cached)
            else:
                logger.info(f"❌ Cache miss: {transaction_id}")
                # Incrementa contador de cache misses
                self.client.incr("metrics:cache_misses")
                return None

        except Exception as e:
            logger.error(f"❌ Erro ao recuperar cache: {e}")
            return None

    # ==================== HISTÓRICO DE TRANSAÇÕES ====================

    def save_transaction(
        self,
        user_id: str,
        transaction: Transaction,
        is_fraud: bool
    ) -> bool:
        """
        Salva uma transação no histórico do usuário

        Args:
            user_id: ID do usuário
            transaction: Objeto Transaction
            is_fraud: Se a transação foi classificada como fraude

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Chave para lista de transações do usuário
            key = f"user:{user_id}:transactions"

            # Adiciona metadados da transação
            tx_data = transaction.model_dump()
            tx_data['is_fraud'] = is_fraud
            tx_data['saved_at'] = datetime.now().isoformat()

            # Adiciona à lista (mantém últimas 1000 transações)
            self.client.lpush(key, json.dumps(tx_data))
            self.client.ltrim(key, 0, 999)  # Mantém apenas as 1000 mais recentes

            # Atualiza estatísticas do usuário
            self._update_user_stats(user_id, transaction, is_fraud)

            logger.info(f"💾 Transação salva para usuário {user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao salvar transação: {e}")
            return False

    def get_user_transactions(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Recupera transações de um usuário

        Args:
            user_id: ID do usuário
            limit: Número máximo de transações a retornar

        Returns:
            Lista de transações
        """
        try:
            key = f"user:{user_id}:transactions"
            transactions = self.client.lrange(key, 0, limit - 1)

            return [json.loads(tx) for tx in transactions]

        except Exception as e:
            logger.error(f"❌ Erro ao recuperar transações: {e}")
            return []

    def _update_user_stats(
        self,
        user_id: str,
        transaction: Transaction,
        is_fraud: bool
    ) -> None:
        """
        Atualiza estatísticas agregadas do usuário

        Args:
            user_id: ID do usuário
            transaction: Objeto Transaction
            is_fraud: Se foi fraude
        """
        try:
            stats_key = f"user:{user_id}:stats"

            # Incrementa contadores
            self.client.hincrby(stats_key, "total_transactions", 1)
            self.client.hincrbyfloat(stats_key, "total_amount", transaction.amount)

            if is_fraud:
                self.client.hincrby(stats_key, "fraud_count", 1)

            # Atualiza última transação
            self.client.hset(stats_key, "last_transaction", datetime.now().isoformat())

            # Adiciona categoria e localização aos conjuntos
            self.client.sadd(f"user:{user_id}:categories", transaction.category)
            self.client.sadd(f"user:{user_id}:locations", transaction.location)
            self.client.sadd(f"user:{user_id}:devices", transaction.device)

        except Exception as e:
            logger.error(f"❌ Erro ao atualizar stats: {e}")

    def get_user_history(self, user_id: str) -> Optional[UserHistory]:
        """
        Recupera histórico completo e estatísticas de um usuário

        Args:
            user_id: ID do usuário

        Returns:
            UserHistory com estatísticas agregadas
        """
        try:
            stats_key = f"user:{user_id}:stats"
            stats = self.client.hgetall(stats_key)

            if not stats:
                logger.warning(f"⚠️ Usuário {user_id} não encontrado")
                return None

            # Extrai estatísticas
            total_tx = int(stats.get('total_transactions', 0))
            total_amount = float(stats.get('total_amount', 0))
            fraud_count = int(stats.get('fraud_count', 0))

            # Calcula médias
            avg_amount = total_amount / total_tx if total_tx > 0 else 0
            fraud_rate = (fraud_count / total_tx * 100) if total_tx > 0 else 0

            # Recupera categorias, localizações e dispositivos mais comuns
            categories = self.client.smembers(f"user:{user_id}:categories")
            locations = self.client.smembers(f"user:{user_id}:locations")
            devices = list(self.client.smembers(f"user:{user_id}:devices"))

            # Pega a última transação
            last_tx = stats.get('last_transaction')
            last_tx_date = datetime.fromisoformat(last_tx) if last_tx else None

            return UserHistory(
                user_id=user_id,
                total_transactions=total_tx,
                total_amount=total_amount,
                average_amount=avg_amount,
                fraud_count=fraud_count,
                fraud_rate=fraud_rate,
                last_transaction_date=last_tx_date,
                most_common_category=list(categories)[0] if categories else None,
                most_common_location=list(locations)[0] if locations else None,
                known_devices=devices
            )

        except Exception as e:
            logger.error(f"❌ Erro ao recuperar histórico: {e}")
            return None

    # ==================== MÉTRICAS DO SISTEMA ====================

    def increment_predictions_count(self) -> None:
        """Incrementa contador total de predições"""
        try:
            self.client.incr("metrics:total_predictions")
        except Exception as e:
            logger.error(f"❌ Erro ao incrementar contador: {e}")

    def get_cache_hit_rate(self) -> float:
        """
        Calcula taxa de acerto do cache

        Returns:
            Taxa entre 0 e 1
        """
        try:
            hits = int(self.client.get("metrics:cache_hits") or 0)
            misses = int(self.client.get("metrics:cache_misses") or 0)
            total = hits + misses

            return hits / total if total > 0 else 0.0

        except Exception as e:
            logger.error(f"❌ Erro ao calcular hit rate: {e}")
            return 0.0

    def get_total_predictions(self) -> int:
        """
        Retorna total de predições realizadas

        Returns:
            Número de predições
        """
        try:
            return int(self.client.get("metrics:total_predictions") or 0)
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar total: {e}")
            return 0

    def record_response_time(self, time_ms: float) -> None:
        """
        Registra tempo de resposta para cálculo de média

        Args:
            time_ms: Tempo de resposta em milissegundos
        """
        try:
            # Usa uma lista circular com janela deslizante (últimas 1000 medições)
            key = "metrics:response_times"
            self.client.lpush(key, time_ms)
            self.client.ltrim(key, 0, 999)
        except Exception as e:
            logger.error(f"❌ Erro ao registrar tempo: {e}")

    def get_average_response_time(self) -> float:
        """
        Calcula tempo médio de resposta

        Returns:
            Tempo médio em milissegundos
        """
        try:
            key = "metrics:response_times"
            times = self.client.lrange(key, 0, -1)

            if not times:
                return 0.0

            times_float = [float(t) for t in times]
            return sum(times_float) / len(times_float)

        except Exception as e:
            logger.error(f"❌ Erro ao calcular média: {e}")
            return 0.0

    # ==================== UTILITÁRIOS ====================

    def clear_cache(self) -> bool:
        """
        Limpa todo o cache de predições

        Returns:
            True se sucesso
        """
        try:
            # Busca todas as chaves de predição
            keys = self.client.keys("prediction:*")

            if keys:
                self.client.delete(*keys)
                logger.info(f"🗑️ {len(keys)} predições removidas do cache")

            return True

        except Exception as e:
            logger.error(f"❌ Erro ao limpar cache: {e}")
            return False

    def reset_metrics(self) -> bool:
        """
        Reseta todas as métricas do sistema

        Returns:
            True se sucesso
        """
        try:
            metrics_keys = [
                "metrics:total_predictions",
                "metrics:cache_hits",
                "metrics:cache_misses",
                "metrics:response_times"
            ]

            for key in metrics_keys:
                self.client.delete(key)

            logger.info("🔄 Métricas resetadas")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao resetar métricas: {e}")
            return False

    def close(self) -> None:
        """Fecha a conexão com Redis"""
        try:
            self.client.close()
            logger.info("👋 Conexão com Redis fechada")
        except Exception as e:
            logger.error(f"❌ Erro ao fechar conexão: {e}")


# Instância global do cliente Redis (singleton)
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """
    Retorna instância singleton do cliente Redis

    Returns:
        RedisClient configurado
    """
    global _redis_client

    if _redis_client is None:
        # Em produção, essas variáveis viriam de environment variables
        _redis_client = RedisClient(
            host="localhost",
            port=6379,
            db=0
        )

    return _redis_client


def close_redis_connection() -> None:
    """Fecha a conexão global com Redis"""
    global _redis_client

    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
