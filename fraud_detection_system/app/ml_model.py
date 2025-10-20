"""
Modelo de Machine Learning para Detecção de Fraudes
====================================================
Este módulo implementa o modelo de Random Forest para classificação
de transações fraudulentas.

Funcionalidades:
- Treinamento do modelo com dados históricos
- Predição em tempo real
- Persistência e carregamento do modelo
- Explicabilidade das predições
- Versionamento do modelo

Autor: Natália Barros
Data: 2025
"""

import numpy as np
import pandas as pd
import joblib
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)

from app.models import Transaction, FraudPrediction, RiskLevel, ModelMetrics
from app.features import FeatureEngineer
from app.database import RedisClient

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FraudDetectionModel:
    """
    Modelo de detecção de fraudes usando Random Forest

    Gerencia todo o ciclo de vida do modelo:
    - Treinamento
    - Validação
    - Predição
    - Persistência
    """

    def __init__(
        self,
        redis_client: Optional[RedisClient] = None,
        model_path: str = "models/fraud_model.pkl",
        scaler_path: str = "models/scaler.pkl"
    ):
        """
        Inicializa o modelo de detecção de fraudes

        Args:
            redis_client: Cliente Redis para features comportamentais
            model_path: Caminho para salvar/carregar o modelo
            scaler_path: Caminho para salvar/carregar o scaler
        """
        self.redis_client = redis_client
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)

        # Componentes do modelo
        self.model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_engineer = FeatureEngineer(redis_client=redis_client)
        self.feature_names: Optional[List[str]] = None

        # Metadados do modelo
        self.model_version = "1.0.0"
        self.trained_at: Optional[datetime] = None
        self.metrics: Optional[ModelMetrics] = None

        logger.info("🤖 FraudDetectionModel inicializado")

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        n_estimators: int = 100,
        max_depth: int = 20,
        min_samples_split: int = 10,
        class_weight: str = 'balanced',
        random_state: int = 42
    ) -> Dict[str, float]:
        """
        Treina o modelo Random Forest

        Args:
            X_train: Features de treinamento
            y_train: Labels de treinamento (0=legítimo, 1=fraude)
            n_estimators: Número de árvores na floresta
            max_depth: Profundidade máxima das árvores
            min_samples_split: Mínimo de amostras para split
            class_weight: Peso das classes ('balanced' recomendado para dados desbalanceados)
            random_state: Seed para reprodutibilidade

        Returns:
            Dicionário com métricas de treinamento
        """
        logger.info("🎓 Iniciando treinamento do modelo...")

        # Salva nomes das features
        self.feature_names = list(X_train.columns)
        logger.info(f"📊 Features: {len(self.feature_names)}")

        # Normaliza as features
        logger.info("🔄 Normalizando features...")
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Cria e treina o modelo
        logger.info("🌲 Treinando Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            class_weight=class_weight,
            random_state=random_state,
            n_jobs=-1,  # Usa todos os cores disponíveis
            verbose=1
        )

        self.model.fit(X_train_scaled, y_train)

        # Avalia no conjunto de treinamento
        y_pred_train = self.model.predict(X_train_scaled)
        train_metrics = {
            'accuracy': accuracy_score(y_train, y_pred_train),
            'precision': precision_score(y_train, y_pred_train, zero_division=0),
            'recall': recall_score(y_train, y_pred_train, zero_division=0),
            'f1_score': f1_score(y_train, y_pred_train, zero_division=0)
        }

        self.trained_at = datetime.now()

        logger.info("✅ Treinamento concluído!")
        logger.info(f"   Acurácia: {train_metrics['accuracy']:.4f}")
        logger.info(f"   Precisão: {train_metrics['precision']:.4f}")
        logger.info(f"   Recall: {train_metrics['recall']:.4f}")
        logger.info(f"   F1-Score: {train_metrics['f1_score']:.4f}")

        return train_metrics

    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> ModelMetrics:
        """
        Avalia o modelo em um conjunto de teste

        Args:
            X_test: Features de teste
            y_test: Labels de teste

        Returns:
            ModelMetrics com todas as métricas
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Modelo não treinado! Execute train() primeiro.")

        logger.info("📈 Avaliando modelo...")

        # Normaliza features de teste
        X_test_scaled = self.scaler.transform(X_test)

        # Predições
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]

        # Calcula métricas
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc_roc = roc_auc_score(y_test, y_pred_proba)

        # Matriz de confusão
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

        # Cria objeto ModelMetrics
        self.metrics = ModelMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            auc_roc=auc_roc,
            true_positives=int(tp),
            true_negatives=int(tn),
            false_positives=int(fp),
            false_negatives=int(fn),
            evaluation_date=datetime.now(),
            dataset_size=len(y_test)
        )

        logger.info("✅ Avaliação concluída!")
        logger.info(f"   Acurácia: {accuracy:.4f}")
        logger.info(f"   Precisão: {precision:.4f}")
        logger.info(f"   Recall: {recall:.4f}")
        logger.info(f"   F1-Score: {f1:.4f}")
        logger.info(f"   AUC-ROC: {auc_roc:.4f}")

        return self.metrics

    def predict(
        self,
        transaction: Transaction
    ) -> FraudPrediction:
        """
        Realiza predição para uma transação

        Args:
            transaction: Objeto Transaction

        Returns:
            FraudPrediction com resultado completo
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Modelo não treinado ou carregado!")

        start_time = datetime.now()

        # Extrai features
        features_dict = self.feature_engineer.extract_features(transaction)

        # Garante ordem correta das features
        if self.feature_names:
            feature_vector = [features_dict.get(name, 0.0) for name in self.feature_names]
        else:
            feature_vector = [features_dict[k] for k in sorted(features_dict.keys())]

        X = np.array(feature_vector).reshape(1, -1)

        # Normaliza
        X_scaled = self.scaler.transform(X)

        # Predição
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        fraud_probability = float(probabilities[1])  # Probabilidade da classe 1 (fraude)

        # Determina nível de risco
        risk_level = self._determine_risk_level(fraud_probability)

        # Gera explicação
        explanation, risk_factors = self._generate_explanation(
            transaction,
            features_dict,
            fraud_probability,
            prediction
        )

        # Gera recomendações
        recommendations = self._generate_recommendations(risk_level, fraud_probability)

        # Calcula confiança (baseada na distância da probabilidade de 0.5)
        confidence_score = abs(fraud_probability - 0.5) * 2  # Normaliza para [0, 1]

        # Tempo de processamento
        processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Cria resposta
        fraud_prediction = FraudPrediction(
            transaction_id=transaction.transaction_id,
            is_fraud=bool(prediction),
            fraud_probability=fraud_probability,
            risk_level=risk_level,
            confidence_score=confidence_score,
            explanation=explanation,
            risk_factors=risk_factors,
            processing_time_ms=processing_time_ms,
            model_version=self.model_version,
            recommendations=recommendations
        )

        logger.info(
            f"🔍 Predição: {transaction.transaction_id} | "
            f"Fraude: {prediction} | "
            f"Prob: {fraud_probability:.2%} | "
            f"Tempo: {processing_time_ms:.1f}ms"
        )

        return fraud_prediction

    def predict_batch(
        self,
        transactions: List[Transaction]
    ) -> List[FraudPrediction]:
        """
        Realiza predições em lote

        Args:
            transactions: Lista de transações

        Returns:
            Lista de FraudPredictions
        """
        logger.info(f"📦 Processando lote de {len(transactions)} transações...")

        predictions = []
        for tx in transactions:
            pred = self.predict(tx)
            predictions.append(pred)

        logger.info(f"✅ Lote processado com sucesso!")

        return predictions

    def _determine_risk_level(self, fraud_probability: float) -> RiskLevel:
        """
        Determina o nível de risco baseado na probabilidade

        Args:
            fraud_probability: Probabilidade de fraude (0-1)

        Returns:
            RiskLevel enum
        """
        if fraud_probability < 0.3:
            return RiskLevel.LOW
        elif fraud_probability < 0.7:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    def _generate_explanation(
        self,
        transaction: Transaction,
        features: Dict[str, float],
        fraud_probability: float,
        prediction: int
    ) -> Tuple[str, List[str]]:
        """
        Gera explicação human-readable da predição

        Args:
            transaction: Transação analisada
            features: Features extraídas
            fraud_probability: Probabilidade de fraude
            prediction: Predição binária (0 ou 1)

        Returns:
            Tupla (explicação, lista de fatores de risco)
        """
        risk_factors = self.feature_engineer.explain_features(transaction, top_n=5)

        if prediction == 1:  # Fraude detectada
            if fraud_probability > 0.9:
                explanation = (
                    f"⚠️ FRAUDE ALTAMENTE SUSPEITA detectada com {fraud_probability:.1%} de confiança. "
                    f"Transação de R$ {transaction.amount:.2f} apresenta múltiplos indicadores de risco."
                )
            elif fraud_probability > 0.7:
                explanation = (
                    f"⚠️ FRAUDE PROVÁVEL detectada com {fraud_probability:.1%} de confiança. "
                    f"Recomenda-se verificação adicional desta transação."
                )
            else:
                explanation = (
                    f"⚠️ Possível fraude detectada com {fraud_probability:.1%} de confiança. "
                    f"Análise manual recomendada."
                )
        else:  # Transação legítima
            explanation = (
                f"✅ Transação considerada LEGÍTIMA com {(1-fraud_probability):.1%} de confiança. "
                f"Padrões normais de comportamento identificados."
            )

        return explanation, risk_factors

    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        fraud_probability: float
    ) -> List[str]:
        """
        Gera recomendações de ação baseadas no risco

        Args:
            risk_level: Nível de risco
            fraud_probability: Probabilidade de fraude

        Returns:
            Lista de recomendações
        """
        recommendations = []

        if risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "🚫 BLOQUEAR transação imediatamente",
                "📧 Notificar usuário via email e SMS",
                "🔒 Suspender temporariamente a conta",
                "👤 Solicitar verificação de identidade adicional",
                "📞 Contato telefônico com o titular"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "⏸️ RETER transação para análise",
                "📧 Notificar usuário para confirmação",
                "🔐 Solicitar autenticação de dois fatores",
                "👁️ Monitorar próximas transações de perto"
            ])
        else:  # LOW
            recommendations.extend([
                "✅ APROVAR transação",
                "📊 Continuar monitoramento normal",
                "💾 Registrar para análise de padrões"
            ])

        return recommendations

    def get_feature_importance(self, top_n: int = 15) -> pd.DataFrame:
        """
        Retorna as features mais importantes do modelo

        Args:
            top_n: Número de features a retornar

        Returns:
            DataFrame com features e suas importâncias
        """
        if self.model is None or self.feature_names is None:
            raise ValueError("Modelo não treinado!")

        # Obtém importâncias
        importances = self.model.feature_importances_

        # Cria DataFrame
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        })

        # Ordena por importância
        importance_df = importance_df.sort_values('importance', ascending=False)

        logger.info(f"🎯 Top {top_n} features mais importantes:")
        for idx, row in importance_df.head(top_n).iterrows():
            logger.info(f"   {row['feature']}: {row['importance']:.4f}")

        return importance_df.head(top_n)

    def save_model(self) -> bool:
        """
        Salva o modelo e scaler em disco

        Returns:
            True se sucesso, False caso contrário
        """
        if self.model is None or self.scaler is None:
            logger.error("❌ Não há modelo para salvar!")
            return False

        try:
            # Cria diretório se não existir
            self.model_path.parent.mkdir(parents=True, exist_ok=True)

            # Salva modelo
            model_data = {
                'model': self.model,
                'feature_names': self.feature_names,
                'model_version': self.model_version,
                'trained_at': self.trained_at,
                'metrics': self.metrics
            }
            joblib.dump(model_data, self.model_path)

            # Salva scaler
            joblib.dump(self.scaler, self.scaler_path)

            logger.info(f"💾 Modelo salvo em: {self.model_path}")
            logger.info(f"💾 Scaler salvo em: {self.scaler_path}")

            return True

        except Exception as e:
            logger.error(f"❌ Erro ao salvar modelo: {e}")
            return False

    def load_model(self) -> bool:
        """
        Carrega o modelo e scaler do disco

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            if not self.model_path.exists() or not self.scaler_path.exists():
                logger.error("❌ Arquivos de modelo não encontrados!")
                return False

            # Carrega modelo
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.model_version = model_data.get('model_version', '1.0.0')
            self.trained_at = model_data.get('trained_at')
            self.metrics = model_data.get('metrics')

            # Carrega scaler
            self.scaler = joblib.load(self.scaler_path)

            logger.info(f"✅ Modelo carregado: {self.model_path}")
            logger.info(f"   Versão: {self.model_version}")
            if self.trained_at:
                logger.info(f"   Treinado em: {self.trained_at}")

            return True

        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}")
            return False

    def is_loaded(self) -> bool:
        """
        Verifica se o modelo está carregado e pronto para uso

        Returns:
            True se modelo está carregado
        """
        return self.model is not None and self.scaler is not None
