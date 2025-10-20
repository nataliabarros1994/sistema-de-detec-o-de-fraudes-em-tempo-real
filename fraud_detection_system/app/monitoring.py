"""
Sistema de Monitoramento com Prometheus
========================================
Este módulo implementa métricas e monitoramento usando Prometheus
para acompanhar a saúde e performance do sistema em produção.

Métricas monitoradas:
- Total de predições realizadas
- Taxa de fraudes detectadas
- Tempo de resposta das predições
- Taxa de acerto do cache
- Status dos componentes (API, modelo, Redis)

Autor: Natália Barros
Data: 2025
"""

import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from functools import wraps
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, CONTENT_TYPE_LATEST
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== MÉTRICAS PROMETHEUS ====================

# Contador de predições totais
predictions_total = Counter(
    'fraud_detection_predictions_total',
    'Total de predições realizadas',
    ['result']  # Labels: 'fraud' ou 'legitimate'
)

# Contador de requisições HTTP
http_requests_total = Counter(
    'fraud_detection_http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status']
)

# Histograma de tempo de resposta das predições (em segundos)
prediction_duration_seconds = Histogram(
    'fraud_detection_prediction_duration_seconds',
    'Tempo de processamento das predições',
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0]
)

# Histograma de tempo de resposta HTTP (em segundos)
http_request_duration_seconds = Histogram(
    'fraud_detection_http_request_duration_seconds',
    'Duração das requisições HTTP',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0]
)

# Gauge para taxa de fraudes (%)
fraud_rate_gauge = Gauge(
    'fraud_detection_fraud_rate_percent',
    'Taxa de fraudes detectadas em porcentagem'
)

# Gauge para probabilidade média de fraude
avg_fraud_probability_gauge = Gauge(
    'fraud_detection_avg_fraud_probability',
    'Probabilidade média de fraude nas predições'
)

# Gauge para cache hit rate
cache_hit_rate_gauge = Gauge(
    'fraud_detection_cache_hit_rate',
    'Taxa de acerto do cache Redis'
)

# Gauge para status dos componentes (1=healthy, 0=unhealthy)
component_status_gauge = Gauge(
    'fraud_detection_component_status',
    'Status de saúde dos componentes',
    ['component']  # Labels: 'api', 'model', 'redis'
)

# Counter para erros
errors_total = Counter(
    'fraud_detection_errors_total',
    'Total de erros no sistema',
    ['error_type']
)

# Info sobre o modelo
model_info = Info(
    'fraud_detection_model_info',
    'Informações sobre o modelo ML'
)

# Gauge para métricas do modelo
model_accuracy_gauge = Gauge(
    'fraud_detection_model_accuracy',
    'Acurácia do modelo'
)

model_precision_gauge = Gauge(
    'fraud_detection_model_precision',
    'Precisão do modelo'
)

model_recall_gauge = Gauge(
    'fraud_detection_model_recall',
    'Recall do modelo'
)

model_f1_score_gauge = Gauge(
    'fraud_detection_model_f1_score',
    'F1-Score do modelo'
)


# ==================== CLASSES DE MONITORAMENTO ====================

class MetricsCollector:
    """
    Coletor de métricas para o sistema de detecção de fraudes

    Centraliza todas as operações de coleta de métricas
    """

    def __init__(self):
        """Inicializa o coletor de métricas"""
        self.start_time = time.time()
        self.prediction_count = 0
        self.fraud_count = 0
        self.total_fraud_probability = 0.0

        logger.info("📊 MetricsCollector inicializado")

    def record_prediction(
        self,
        is_fraud: bool,
        fraud_probability: float,
        processing_time_seconds: float
    ) -> None:
        """
        Registra uma predição nas métricas

        Args:
            is_fraud: Se a predição foi fraude
            fraud_probability: Probabilidade de fraude (0-1)
            processing_time_seconds: Tempo de processamento em segundos
        """
        # Incrementa contadores
        self.prediction_count += 1

        if is_fraud:
            self.fraud_count += 1
            predictions_total.labels(result='fraud').inc()
        else:
            predictions_total.labels(result='legitimate').inc()

        # Registra tempo de processamento
        prediction_duration_seconds.observe(processing_time_seconds)

        # Atualiza probabilidade total para cálculo de média
        self.total_fraud_probability += fraud_probability

        # Atualiza gauges
        self._update_gauges()

    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_seconds: float
    ) -> None:
        """
        Registra uma requisição HTTP

        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint acessado
            status_code: Código de status HTTP
            duration_seconds: Duração da requisição em segundos
        """
        # Contador de requisições
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()

        # Histograma de duração
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration_seconds)

    def record_error(self, error_type: str) -> None:
        """
        Registra um erro

        Args:
            error_type: Tipo de erro (ex: 'prediction_error', 'redis_error')
        """
        errors_total.labels(error_type=error_type).inc()
        logger.error(f"❌ Erro registrado: {error_type}")

    def update_cache_metrics(self, hit_rate: float) -> None:
        """
        Atualiza métricas de cache

        Args:
            hit_rate: Taxa de acerto do cache (0-1)
        """
        cache_hit_rate_gauge.set(hit_rate)

    def update_component_status(
        self,
        component: str,
        is_healthy: bool
    ) -> None:
        """
        Atualiza status de um componente

        Args:
            component: Nome do componente ('api', 'model', 'redis')
            is_healthy: Se o componente está saudável
        """
        status_value = 1.0 if is_healthy else 0.0
        component_status_gauge.labels(component=component).set(status_value)

        status_emoji = "✅" if is_healthy else "❌"
        logger.info(f"{status_emoji} Status {component}: {'healthy' if is_healthy else 'unhealthy'}")

    def update_model_metrics(
        self,
        accuracy: float,
        precision: float,
        recall: float,
        f1_score: float
    ) -> None:
        """
        Atualiza métricas do modelo ML

        Args:
            accuracy: Acurácia do modelo
            precision: Precisão do modelo
            recall: Recall do modelo
            f1_score: F1-Score do modelo
        """
        model_accuracy_gauge.set(accuracy)
        model_precision_gauge.set(precision)
        model_recall_gauge.set(recall)
        model_f1_score_gauge.set(f1_score)

        logger.info(f"📈 Métricas do modelo atualizadas:")
        logger.info(f"   Acurácia: {accuracy:.4f}")
        logger.info(f"   Precisão: {precision:.4f}")
        logger.info(f"   Recall: {recall:.4f}")
        logger.info(f"   F1-Score: {f1_score:.4f}")

    def set_model_info(
        self,
        version: str,
        trained_at: Optional[str] = None,
        features_count: Optional[int] = None
    ) -> None:
        """
        Define informações sobre o modelo

        Args:
            version: Versão do modelo
            trained_at: Data de treinamento
            features_count: Número de features
        """
        info_dict = {'version': version}

        if trained_at:
            info_dict['trained_at'] = trained_at

        if features_count:
            info_dict['features_count'] = str(features_count)

        model_info.info(info_dict)

        logger.info(f"ℹ️ Info do modelo definida: {info_dict}")

    def _update_gauges(self) -> None:
        """Atualiza gauges calculados"""
        if self.prediction_count > 0:
            # Taxa de fraude em porcentagem
            fraud_rate = (self.fraud_count / self.prediction_count) * 100
            fraud_rate_gauge.set(fraud_rate)

            # Probabilidade média de fraude
            avg_probability = self.total_fraud_probability / self.prediction_count
            avg_fraud_probability_gauge.set(avg_probability)

    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo das métricas coletadas

        Returns:
            Dicionário com resumo das métricas
        """
        uptime_seconds = time.time() - self.start_time

        summary = {
            'uptime_seconds': uptime_seconds,
            'total_predictions': self.prediction_count,
            'fraud_detected': self.fraud_count,
            'fraud_rate_percent': (
                (self.fraud_count / self.prediction_count * 100)
                if self.prediction_count > 0 else 0.0
            ),
            'avg_fraud_probability': (
                self.total_fraud_probability / self.prediction_count
                if self.prediction_count > 0 else 0.0
            )
        }

        return summary

    def reset_metrics(self) -> None:
        """Reseta métricas de contador (usar com cuidado!)"""
        self.prediction_count = 0
        self.fraud_count = 0
        self.total_fraud_probability = 0.0
        logger.warning("⚠️ Métricas resetadas")


# Instância global do coletor
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """
    Retorna instância singleton do coletor de métricas

    Returns:
        MetricsCollector
    """
    global _metrics_collector

    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()

    return _metrics_collector


# ==================== DECORADORES ====================

def track_prediction_time(func):
    """
    Decorador para rastrear tempo de predição

    Usage:
        @track_prediction_time
        def predict(transaction):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            # Registra na métrica
            prediction_duration_seconds.observe(duration)

            return result

        except Exception as e:
            # Registra erro
            get_metrics_collector().record_error('prediction_error')
            raise

    return wrapper


def track_http_request(func):
    """
    Decorador para rastrear requisições HTTP

    Usage:
        @track_http_request
        async def endpoint():
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)
            return result

        finally:
            duration = time.time() - start_time
            # A requisição real será registrada no middleware

    return wrapper


# ==================== UTILITÁRIOS ====================

def get_prometheus_metrics() -> bytes:
    """
    Retorna métricas no formato Prometheus

    Returns:
        Bytes com métricas formatadas
    """
    return generate_latest()


def get_content_type() -> str:
    """
    Retorna o content type para métricas Prometheus

    Returns:
        String com content type
    """
    return CONTENT_TYPE_LATEST


# ==================== HEALTH CHECK ====================

class HealthChecker:
    """
    Verifica saúde dos componentes do sistema
    """

    @staticmethod
    def check_api() -> bool:
        """
        Verifica se a API está respondendo

        Returns:
            True se saudável
        """
        # A API está funcionando se este código está executando
        return True

    @staticmethod
    def check_model(model) -> bool:
        """
        Verifica se o modelo está carregado e funcional

        Args:
            model: Instância do FraudDetectionModel

        Returns:
            True se saudável
        """
        try:
            return model.is_loaded()
        except Exception:
            return False

    @staticmethod
    def check_redis(redis_client) -> bool:
        """
        Verifica se o Redis está acessível

        Args:
            redis_client: Instância do RedisClient

        Returns:
            True se saudável
        """
        try:
            return redis_client.is_healthy()
        except Exception:
            return False

    @staticmethod
    def perform_full_health_check(
        model=None,
        redis_client=None
    ) -> Dict[str, bool]:
        """
        Realiza verificação completa de saúde

        Args:
            model: FraudDetectionModel (opcional)
            redis_client: RedisClient (opcional)

        Returns:
            Dicionário com status de cada componente
        """
        health_status = {
            'api': HealthChecker.check_api(),
            'model': HealthChecker.check_model(model) if model else False,
            'redis': HealthChecker.check_redis(redis_client) if redis_client else False
        }

        # Atualiza métricas de status
        collector = get_metrics_collector()
        for component, is_healthy in health_status.items():
            collector.update_component_status(component, is_healthy)

        return health_status


# ==================== LOGGING ESTRUTURADO ====================

def log_prediction_result(
    transaction_id: str,
    is_fraud: bool,
    fraud_probability: float,
    processing_time_ms: float
) -> None:
    """
    Loga resultado de predição de forma estruturada

    Args:
        transaction_id: ID da transação
        is_fraud: Se é fraude
        fraud_probability: Probabilidade de fraude
        processing_time_ms: Tempo de processamento
    """
    result = "FRAUD" if is_fraud else "LEGITIMATE"
    emoji = "🚨" if is_fraud else "✅"

    logger.info(
        f"{emoji} Prediction | "
        f"TX: {transaction_id} | "
        f"Result: {result} | "
        f"Prob: {fraud_probability:.2%} | "
        f"Time: {processing_time_ms:.1f}ms"
    )


def log_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float
) -> None:
    """
    Loga requisição HTTP de forma estruturada

    Args:
        method: Método HTTP
        endpoint: Endpoint acessado
        status_code: Código de status
        duration_ms: Duração em ms
    """
    status_emoji = "✅" if 200 <= status_code < 300 else "❌"

    logger.info(
        f"{status_emoji} {method} {endpoint} | "
        f"Status: {status_code} | "
        f"Duration: {duration_ms:.1f}ms"
    )
