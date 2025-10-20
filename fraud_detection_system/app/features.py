"""
Engenharia de Features para Detecção de Fraudes
================================================
Este módulo implementa a extração e engenharia de features para
o modelo de Machine Learning.

Features extraídas:
1. Comportamentais: padrões do usuário
2. Temporais: hora, dia da semana, etc.
3. Transacionais: valor, categoria, etc.
4. Geográficas: localização e padrões de movimento
5. Dispositivo: histórico de dispositivos usados

Autor: Natália Barros
Data: 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, time
import logging
from app.models import Transaction
from app.database import RedisClient

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Classe responsável pela engenharia de features

    Transforma dados brutos de transações em features
    numéricas para o modelo de ML
    """

    def __init__(self, redis_client: Optional[RedisClient] = None):
        """
        Inicializa o engenheiro de features

        Args:
            redis_client: Cliente Redis para acessar histórico (opcional)
        """
        self.redis_client = redis_client

        # Mapeamento de categorias para códigos numéricos
        self.category_mapping = {
            "electronics": 0,
            "fashion": 1,
            "food": 2,
            "travel": 3,
            "services": 4,
            "entertainment": 5,
            "health": 6,
            "other": 7
        }

        # Faixas de horário
        self.time_periods = {
            "madrugada": (0, 6),      # 00:00 - 06:00
            "manha": (6, 12),          # 06:00 - 12:00
            "tarde": (12, 18),         # 12:00 - 18:00
            "noite": (18, 24)          # 18:00 - 24:00
        }

        logger.info("🔧 FeatureEngineer inicializado")

    def extract_features(
        self,
        transaction: Transaction
    ) -> Dict[str, float]:
        """
        Extrai todas as features de uma transação

        Args:
            transaction: Objeto Transaction

        Returns:
            Dicionário com features numéricas
        """
        features = {}

        # 1. Features Transacionais Básicas
        features.update(self._extract_transaction_features(transaction))

        # 2. Features Temporais
        features.update(self._extract_temporal_features(transaction))

        # 3. Features Comportamentais (requer histórico)
        if self.redis_client:
            features.update(self._extract_behavioral_features(transaction))
        else:
            # Features padrão quando não há histórico
            features.update(self._get_default_behavioral_features())

        # 4. Features de Localização
        features.update(self._extract_location_features(transaction))

        # 5. Features de Dispositivo
        features.update(self._extract_device_features(transaction))

        logger.info(f"✅ {len(features)} features extraídas para transação {transaction.transaction_id}")

        return features

    def _extract_transaction_features(
        self,
        transaction: Transaction
    ) -> Dict[str, float]:
        """
        Extrai features da transação em si

        Args:
            transaction: Objeto Transaction

        Returns:
            Dicionário com features transacionais
        """
        features = {}

        # Valor da transação (normalizado por log para reduzir outliers)
        features['amount'] = transaction.amount
        features['amount_log'] = np.log1p(transaction.amount)  # log(1 + x)

        # Faixas de valor
        features['is_high_value'] = 1.0 if transaction.amount > 1000 else 0.0
        features['is_very_high_value'] = 1.0 if transaction.amount > 5000 else 0.0
        features['is_low_value'] = 1.0 if transaction.amount < 50 else 0.0

        # Categoria (encoding numérico)
        features['category_code'] = float(
            self.category_mapping.get(transaction.category, 7)
        )

        # Categorias específicas (one-hot encoding parcial para as mais suspeitas)
        features['is_electronics'] = 1.0 if transaction.category == "electronics" else 0.0
        features['is_travel'] = 1.0 if transaction.category == "travel" else 0.0

        return features

    def _extract_temporal_features(
        self,
        transaction: Transaction
    ) -> Dict[str, float]:
        """
        Extrai features temporais da transação

        Args:
            transaction: Objeto Transaction

        Returns:
            Dicionário com features temporais
        """
        features = {}

        # Usa timestamp da transação ou horário atual
        timestamp = transaction.timestamp or datetime.now()

        # Hora do dia (0-23)
        features['hour'] = float(timestamp.hour)
        features['hour_sin'] = np.sin(2 * np.pi * timestamp.hour / 24)
        features['hour_cos'] = np.cos(2 * np.pi * timestamp.hour / 24)

        # Dia da semana (0=segunda, 6=domingo)
        features['day_of_week'] = float(timestamp.weekday())
        features['is_weekend'] = 1.0 if timestamp.weekday() >= 5 else 0.0

        # Período do dia
        hour = timestamp.hour
        features['is_madrugada'] = 1.0 if 0 <= hour < 6 else 0.0
        features['is_manha'] = 1.0 if 6 <= hour < 12 else 0.0
        features['is_tarde'] = 1.0 if 12 <= hour < 18 else 0.0
        features['is_noite'] = 1.0 if 18 <= hour < 24 else 0.0

        # Horários suspeitos (madrugada é mais arriscado)
        features['is_suspicious_hour'] = 1.0 if hour < 6 or hour > 23 else 0.0

        return features

    def _extract_behavioral_features(
        self,
        transaction: Transaction
    ) -> Dict[str, float]:
        """
        Extrai features comportamentais baseadas no histórico do usuário

        Args:
            transaction: Objeto Transaction

        Returns:
            Dicionário com features comportamentais
        """
        features = {}

        try:
            # Recupera histórico do usuário
            user_history = self.redis_client.get_user_history(transaction.user_id)

            if user_history and user_history.total_transactions > 0:
                # Desvio do valor médio
                avg_amount = user_history.average_amount
                features['amount_vs_avg'] = transaction.amount / avg_amount if avg_amount > 0 else 1.0
                features['amount_deviation'] = abs(transaction.amount - avg_amount)

                # Classificação em relação ao histórico
                features['is_above_avg'] = 1.0 if transaction.amount > avg_amount else 0.0
                features['is_much_above_avg'] = 1.0 if transaction.amount > avg_amount * 2 else 0.0
                features['is_way_above_avg'] = 1.0 if transaction.amount > avg_amount * 3 else 0.0

                # Taxa de fraude histórica do usuário
                features['user_fraud_rate'] = user_history.fraud_rate / 100.0

                # Experiência do usuário (número de transações)
                features['user_transaction_count'] = float(user_history.total_transactions)
                features['is_new_user'] = 1.0 if user_history.total_transactions < 5 else 0.0
                features['is_experienced_user'] = 1.0 if user_history.total_transactions > 50 else 0.0

                # Categoria usual vs atual
                most_common_category = user_history.most_common_category
                features['is_usual_category'] = 1.0 if transaction.category == most_common_category else 0.0

                # Localização usual vs atual
                most_common_location = user_history.most_common_location
                features['is_usual_location'] = 1.0 if transaction.location == most_common_location else 0.0

                # Dispositivo conhecido
                features['is_known_device'] = 1.0 if transaction.device in user_history.known_devices else 0.0

                # Tempo desde última transação (se disponível)
                if user_history.last_transaction_date:
                    time_diff = (transaction.timestamp or datetime.now()) - user_history.last_transaction_date
                    features['hours_since_last_tx'] = time_diff.total_seconds() / 3600
                    features['is_rapid_succession'] = 1.0 if time_diff.total_seconds() < 300 else 0.0  # < 5 min
                else:
                    features['hours_since_last_tx'] = 999.0  # Valor alto indicando primeira transação
                    features['is_rapid_succession'] = 0.0

            else:
                # Usuário sem histórico - features padrão
                features.update(self._get_default_behavioral_features())
                features['is_new_user'] = 1.0

        except Exception as e:
            logger.error(f"❌ Erro ao extrair features comportamentais: {e}")
            features.update(self._get_default_behavioral_features())

        return features

    def _get_default_behavioral_features(self) -> Dict[str, float]:
        """
        Retorna features comportamentais padrão quando não há histórico

        Returns:
            Dicionário com features padrão
        """
        return {
            'amount_vs_avg': 1.0,
            'amount_deviation': 0.0,
            'is_above_avg': 0.0,
            'is_much_above_avg': 0.0,
            'is_way_above_avg': 0.0,
            'user_fraud_rate': 0.0,
            'user_transaction_count': 0.0,
            'is_new_user': 1.0,
            'is_experienced_user': 0.0,
            'is_usual_category': 0.0,
            'is_usual_location': 0.0,
            'is_known_device': 0.0,
            'hours_since_last_tx': 999.0,
            'is_rapid_succession': 0.0
        }

    def _extract_location_features(
        self,
        transaction: Transaction
    ) -> Dict[str, float]:
        """
        Extrai features de localização

        Args:
            transaction: Objeto Transaction

        Returns:
            Dicionário com features de localização
        """
        features = {}

        location = transaction.location.lower()

        # Cidades grandes (geralmente menor risco)
        major_cities = ['são paulo', 'rio de janeiro', 'brasília', 'belo horizonte', 'curitiba']
        features['is_major_city'] = 1.0 if any(city in location for city in major_cities) else 0.0

        # Comprimento do nome (localizações desconhecidas tendem a ter nomes genéricos)
        features['location_name_length'] = float(len(transaction.location))

        # Hash simples da localização para criar um ID numérico
        features['location_hash'] = float(hash(transaction.location) % 10000)

        return features

    def _extract_device_features(
        self,
        transaction: Transaction
    ) -> Dict[str, float]:
        """
        Extrai features do dispositivo

        Args:
            transaction: Objeto Transaction

        Returns:
            Dicionário com features de dispositivo
        """
        features = {}

        device = transaction.device.lower()

        # Tipo de dispositivo (baseado em padrões comuns)
        features['is_mobile'] = 1.0 if 'mobile' in device or 'phone' in device else 0.0
        features['is_web'] = 1.0 if 'web' in device or 'browser' in device else 0.0
        features['is_tablet'] = 1.0 if 'tablet' in device or 'ipad' in device else 0.0

        # Dispositivo novo ou desconhecido (padrões suspeitos)
        features['is_new_device'] = 1.0 if 'new' in device or 'unknown' in device else 0.0

        # Hash do dispositivo
        features['device_hash'] = float(hash(transaction.device) % 10000)

        return features

    def create_feature_vector(
        self,
        transaction: Transaction,
        feature_names: Optional[List[str]] = None
    ) -> np.ndarray:
        """
        Cria um vetor de features na ordem correta para o modelo

        Args:
            transaction: Objeto Transaction
            feature_names: Lista de nomes de features na ordem esperada

        Returns:
            Array numpy com features
        """
        # Extrai todas as features
        features_dict = self.extract_features(transaction)

        if feature_names:
            # Garante a ordem correta das features
            feature_vector = [features_dict.get(name, 0.0) for name in feature_names]
        else:
            # Usa ordem alfabética se não especificado
            feature_vector = [features_dict[k] for k in sorted(features_dict.keys())]

        return np.array(feature_vector).reshape(1, -1)

    def get_feature_names(self, transaction: Transaction) -> List[str]:
        """
        Retorna lista ordenada de nomes das features

        Args:
            transaction: Transação de exemplo

        Returns:
            Lista de nomes de features
        """
        features_dict = self.extract_features(transaction)
        return sorted(features_dict.keys())

    def explain_features(
        self,
        transaction: Transaction,
        top_n: int = 5
    ) -> List[str]:
        """
        Gera explicações human-readable das features mais importantes

        Args:
            transaction: Objeto Transaction
            top_n: Número de features principais a explicar

        Returns:
            Lista de explicações
        """
        features = self.extract_features(transaction)
        explanations = []

        # Análise de valor
        if features.get('is_very_high_value', 0) == 1.0:
            explanations.append(f"Valor muito alto: R$ {transaction.amount:.2f}")
        elif features.get('is_high_value', 0) == 1.0:
            explanations.append(f"Valor alto: R$ {transaction.amount:.2f}")

        # Análise comportamental
        if features.get('is_way_above_avg', 0) == 1.0:
            explanations.append("Valor 3x acima da média do usuário")
        elif features.get('is_much_above_avg', 0) == 1.0:
            explanations.append("Valor 2x acima da média do usuário")

        # Análise temporal
        if features.get('is_suspicious_hour', 0) == 1.0:
            explanations.append(f"Horário suspeito: {transaction.timestamp.hour}h")

        if features.get('is_madrugada', 0) == 1.0:
            explanations.append("Transação durante a madrugada")

        # Análise de usuário
        if features.get('is_new_user', 0) == 1.0:
            explanations.append("Usuário novo no sistema")

        if features.get('user_fraud_rate', 0) > 0.05:  # > 5%
            fraud_rate = features.get('user_fraud_rate', 0) * 100
            explanations.append(f"Usuário com histórico de fraude: {fraud_rate:.1f}%")

        # Análise de dispositivo/localização
        if features.get('is_known_device', 0) == 0.0:
            explanations.append("Dispositivo desconhecido")

        if features.get('is_usual_location', 0) == 0.0:
            explanations.append("Localização incomum para este usuário")

        if features.get('is_new_device', 0) == 1.0:
            explanations.append("Novo dispositivo detectado")

        # Análise de rapidez
        if features.get('is_rapid_succession', 0) == 1.0:
            explanations.append("Transação em rápida sucessão (< 5 minutos)")

        # Retorna as top_n explicações
        return explanations[:top_n]


def batch_extract_features(
    transactions: List[Transaction],
    redis_client: Optional[RedisClient] = None
) -> pd.DataFrame:
    """
    Extrai features de múltiplas transações em lote

    Args:
        transactions: Lista de transações
        redis_client: Cliente Redis opcional

    Returns:
        DataFrame com features de todas as transações
    """
    engineer = FeatureEngineer(redis_client=redis_client)

    all_features = []
    for tx in transactions:
        features = engineer.extract_features(tx)
        features['transaction_id'] = tx.transaction_id
        all_features.append(features)

    df = pd.DataFrame(all_features)

    # Move transaction_id para primeira coluna
    cols = ['transaction_id'] + [col for col in df.columns if col != 'transaction_id']
    df = df[cols]

    logger.info(f"✅ Features extraídas de {len(transactions)} transações")

    return df
