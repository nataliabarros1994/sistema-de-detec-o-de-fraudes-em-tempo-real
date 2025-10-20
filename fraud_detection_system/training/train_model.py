"""
Script de Treinamento do Modelo de Detecção de Fraudes
=======================================================
Este script treina o modelo Random Forest usando dados sintéticos
ou dados reais de transações.

Passos do treinamento:
1. Carrega ou gera dados de transações
2. Extrai features
3. Divide em treino/teste
4. Treina o modelo Random Forest
5. Avalia performance
6. Salva modelo treinado

Uso:
    python training/train_model.py

Autor: Natália Barros
Data: 2025
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from typing import Tuple, Dict, Any, List, Optional

# Adiciona o diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import Transaction
from app.ml_model import FraudDetectionModel
from app.features import batch_extract_features
from training.data_generator import TransactionDataGenerator
from sklearn.model_selection import train_test_split

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_or_generate_data(
    data_path: str = "data/transactions.csv",
    generate_if_missing: bool = True
) -> pd.DataFrame:
    """
    Carrega dados existentes ou gera novos se não existirem

    Args:
        data_path: Caminho para o arquivo de dados
        generate_if_missing: Se True, gera dados se arquivo não existir

    Returns:
        DataFrame com transações
    """
    if os.path.exists(data_path):
        logger.info(f"📂 Carregando dados de: {data_path}")
        df = pd.read_csv(data_path)
        logger.info(f"   {len(df):,} transações carregadas")
        return df

    elif generate_if_missing:
        logger.info("📂 Arquivo de dados não encontrado. Gerando dados sintéticos...")

        # Cria diretório se não existir
        os.makedirs(os.path.dirname(data_path), exist_ok=True)

        # Gera dados
        generator = TransactionDataGenerator(seed=42)
        df = generator.generate_dataset(
            num_users=1000,
            transactions_per_user=20,
            fraud_rate=0.10
        )

        # Salva para uso futuro
        df.to_csv(data_path, index=False)
        logger.info(f"💾 Dados salvos em: {data_path}")

        return df

    else:
        raise FileNotFoundError(f"Arquivo não encontrado: {data_path}")


def prepare_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepara dados para treinamento extraindo features

    Args:
        df: DataFrame com transações brutas

    Returns:
        Tupla (features_df, labels)
    """
    logger.info("🔧 Preparando dados para treinamento...")

    # Converte para objetos Transaction
    logger.info("   Convertendo para objetos Transaction...")
    transactions = []

    for _, row in df.iterrows():
        tx = Transaction(
            transaction_id=row['transaction_id'],
            user_id=row['user_id'],
            amount=float(row['amount']),
            merchant=row['merchant'],
            category=row['category'],
            location=row['location'],
            device=row['device'],
            timestamp=pd.to_datetime(row['timestamp']) if 'timestamp' in row else None
        )
        transactions.append(tx)

    # Extrai features (sem Redis - usando apenas features básicas)
    logger.info("   Extraindo features...")
    features_df = batch_extract_features(transactions, redis_client=None)

    # Remove coluna transaction_id
    if 'transaction_id' in features_df.columns:
        features_df = features_df.drop('transaction_id', axis=1)

    # Labels (0=legítimo, 1=fraude)
    labels = df['is_fraud']

    logger.info(f"✅ Dados preparados:")
    logger.info(f"   Features: {features_df.shape[1]}")
    logger.info(f"   Amostras: {len(features_df):,}")
    logger.info(f"   Fraudes: {labels.sum():,} ({labels.mean():.2%})")

    return features_df, labels


def train_fraud_detection_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> FraudDetectionModel:
    """
    Treina e avalia o modelo de detecção de fraudes

    Args:
        X_train: Features de treino
        y_train: Labels de treino
        X_test: Features de teste
        y_test: Labels de teste

    Returns:
        Modelo treinado
    """
    logger.info("🎓 Iniciando treinamento do modelo...")

    # Cria modelo
    model = FraudDetectionModel()

    # Treina
    train_metrics = model.train(
        X_train=X_train,
        y_train=y_train,
        n_estimators=100,      # 100 árvores
        max_depth=20,          # Profundidade máxima
        min_samples_split=10,  # Mínimo para split
        class_weight='balanced', # Balanceia classes
        random_state=42
    )

    logger.info("\n" + "="*60)
    logger.info("📊 MÉTRICAS DE TREINAMENTO")
    logger.info("="*60)
    for metric, value in train_metrics.items():
        logger.info(f"   {metric}: {value:.4f}")

    # Avalia no conjunto de teste
    logger.info("\n" + "="*60)
    logger.info("📈 AVALIAÇÃO NO CONJUNTO DE TESTE")
    logger.info("="*60)

    test_metrics = model.evaluate(X_test, y_test)

    logger.info(f"\n✅ Modelo treinado com sucesso!")
    logger.info(f"   Acurácia (teste): {test_metrics.accuracy:.4f}")
    logger.info(f"   Precisão (teste): {test_metrics.precision:.4f}")
    logger.info(f"   Recall (teste): {test_metrics.recall:.4f}")
    logger.info(f"   F1-Score (teste): {test_metrics.f1_score:.4f}")
    logger.info(f"   AUC-ROC (teste): {test_metrics.auc_roc:.4f}")

    # Matriz de confusão
    logger.info("\n📊 MATRIZ DE CONFUSÃO:")
    logger.info(f"   Verdadeiros Positivos: {test_metrics.true_positives}")
    logger.info(f"   Verdadeiros Negativos: {test_metrics.true_negatives}")
    logger.info(f"   Falsos Positivos: {test_metrics.false_positives}")
    logger.info(f"   Falsos Negativos: {test_metrics.false_negatives}")

    # Features mais importantes
    logger.info("\n" + "="*60)
    logger.info("🎯 FEATURES MAIS IMPORTANTES")
    logger.info("="*60)
    importance_df = model.get_feature_importance(top_n=15)
    for idx, row in importance_df.iterrows():
        logger.info(f"   {row['feature']:<30} {row['importance']:.4f}")

    return model


def main():
    """
    Função principal do script de treinamento
    """
    print("=" * 70)
    print("🎓 TREINAMENTO DO MODELO DE DETECÇÃO DE FRAUDES")
    print("=" * 70)
    print()

    start_time = datetime.now()

    try:
        # 1. Carrega ou gera dados
        logger.info("PASSO 1/5: Carregando dados...")
        df = load_or_generate_data(
            data_path="data/transactions.csv",
            generate_if_missing=True
        )

        # Exibe estatísticas
        logger.info("\n📊 ESTATÍSTICAS DO DATASET:")
        logger.info(f"   Total de transações: {len(df):,}")
        logger.info(f"   Transações legítimas: {(df['is_fraud'] == 0).sum():,}")
        logger.info(f"   Transações fraudulentas: {(df['is_fraud'] == 1).sum():,}")
        logger.info(f"   Taxa de fraude: {df['is_fraud'].mean():.2%}")

        # 2. Prepara dados
        logger.info("\n" + "="*70)
        logger.info("PASSO 2/5: Preparando dados...")
        X, y = prepare_data(df)

        # 3. Divide em treino/teste
        logger.info("\n" + "="*70)
        logger.info("PASSO 3/5: Dividindo em treino/teste...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,      # 20% para teste
            random_state=42,
            stratify=y          # Mantém proporção de fraudes
        )

        logger.info(f"   Treino: {len(X_train):,} amostras")
        logger.info(f"   Teste: {len(X_test):,} amostras")

        # 4. Treina modelo
        logger.info("\n" + "="*70)
        logger.info("PASSO 4/5: Treinando modelo...")
        model = train_fraud_detection_model(X_train, y_train, X_test, y_test)

        # 5. Salva modelo
        logger.info("\n" + "="*70)
        logger.info("PASSO 5/5: Salvando modelo...")

        # Cria diretório se não existir
        os.makedirs("models", exist_ok=True)

        success = model.save_model()

        if success:
            logger.info("✅ Modelo salvo com sucesso!")
            logger.info(f"   Local: models/fraud_model.pkl")
            logger.info(f"   Scaler: models/scaler.pkl")
        else:
            logger.error("❌ Erro ao salvar modelo")

        # Tempo total
        elapsed_time = (datetime.now() - start_time).total_seconds()

        # Resumo final
        print("\n" + "=" * 70)
        print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print(f"\n⏱️  Tempo total: {elapsed_time:.1f} segundos")
        print(f"\n📊 Performance do Modelo:")
        print(f"   • Acurácia: {model.metrics.accuracy:.2%}")
        print(f"   • Precisão: {model.metrics.precision:.2%}")
        print(f"   • Recall: {model.metrics.recall:.2%}")
        print(f"   • F1-Score: {model.metrics.f1_score:.2%}")
        print(f"   • AUC-ROC: {model.metrics.auc_roc:.2%}")
        print(f"\n🎯 O modelo está pronto para uso!")
        print(f"\nPróximos passos:")
        print(f"   1. Inicie o Redis: docker-compose up -d")
        print(f"   2. Inicie a API: python -m app.main")
        print(f"   3. Acesse a documentação: http://localhost:8000/docs")
        print()

        return model

    except Exception as e:
        logger.error(f"\n❌ ERRO NO TREINAMENTO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Executa treinamento
    main()
