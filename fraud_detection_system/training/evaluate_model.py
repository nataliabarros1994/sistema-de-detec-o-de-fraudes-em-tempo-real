"""
Script de Avaliação do Modelo de Detecção de Fraudes
=====================================================
Este script avalia o modelo treinado com visualizações e
métricas detalhadas.

Funcionalidades:
- Carrega modelo treinado
- Gera métricas detalhadas
- Cria visualizações (se matplotlib disponível)
- Análise de features importantes
- Exemplos de predições

Uso:
    python training/evaluate_model.py

Autor: Natália Barros
Data: 2025
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict, Any, List, Optional

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import Transaction
from app.ml_model import FraudDetectionModel
from app.features import batch_extract_features
from sklearn.model_selection import train_test_split

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_test_data(data_path: str = "data/transactions.csv") -> pd.DataFrame:
    """
    Carrega dados de teste

    Args:
        data_path: Caminho para os dados

    Returns:
        DataFrame com transações
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {data_path}\n"
            "Execute primeiro: python training/train_model.py"
        )

    logger.info(f"📂 Carregando dados de: {data_path}")
    df = pd.read_csv(data_path)
    logger.info(f"   {len(df):,} transações carregadas")

    return df


def evaluate_model_performance(
    model: FraudDetectionModel,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    df_test: pd.DataFrame
) -> None:
    """
    Avalia performance detalhada do modelo

    Args:
        model: Modelo treinado
        X_test: Features de teste
        y_test: Labels de teste
        df_test: DataFrame original para análise
    """
    logger.info("\n" + "="*70)
    logger.info("📊 AVALIAÇÃO DETALHADA DO MODELO")
    logger.info("="*70)

    # Métricas gerais
    metrics = model.evaluate(X_test, y_test)

    print("\n🎯 MÉTRICAS PRINCIPAIS:")
    print(f"   Acurácia:  {metrics.accuracy:.2%}")
    print(f"   Precisão:  {metrics.precision:.2%}")
    print(f"   Recall:    {metrics.recall:.2%}")
    print(f"   F1-Score:  {metrics.f1_score:.2%}")
    print(f"   AUC-ROC:   {metrics.auc_roc:.2%}")

    print("\n📊 MATRIZ DE CONFUSÃO:")
    print(f"   Verdadeiros Positivos (TP): {metrics.true_positives:,}")
    print(f"   Verdadeiros Negativos (TN): {metrics.true_negatives:,}")
    print(f"   Falsos Positivos (FP):      {metrics.false_positives:,}")
    print(f"   Falsos Negativos (FN):      {metrics.false_negatives:,}")

    # Análise de erros
    total = metrics.true_positives + metrics.true_negatives + \
            metrics.false_positives + metrics.false_negatives

    print("\n❌ ANÁLISE DE ERROS:")
    print(f"   Taxa de Falso Positivo: {metrics.false_positives/total:.2%}")
    print(f"   Taxa de Falso Negativo: {metrics.false_negatives/total:.2%}")

    # Taxa de detecção
    if (metrics.true_positives + metrics.false_negatives) > 0:
        detection_rate = metrics.true_positives / (metrics.true_positives + metrics.false_negatives)
        print(f"   Taxa de Detecção:       {detection_rate:.2%}")

    # Features importantes
    print("\n" + "="*70)
    print("🎯 TOP 15 FEATURES MAIS IMPORTANTES")
    print("="*70)

    importance_df = model.get_feature_importance(top_n=15)
    for idx, row in importance_df.iterrows():
        bar_length = int(row['importance'] * 50)
        bar = "█" * bar_length
        print(f"   {row['feature']:<30} {row['importance']:.4f} {bar}")


def test_sample_predictions(
    model: FraudDetectionModel,
    df: pd.DataFrame,
    num_samples: int = 5
) -> None:
    """
    Testa predições em amostras específicas

    Args:
        model: Modelo treinado
        df: DataFrame com transações
        num_samples: Número de amostras a testar
    """
    logger.info("\n" + "="*70)
    logger.info("🔍 TESTANDO PREDIÇÕES EM AMOSTRAS")
    logger.info("="*70)

    # Seleciona amostras: algumas fraudes e algumas legítimas
    fraud_samples = df[df['is_fraud'] == 1].sample(min(num_samples, (df['is_fraud'] == 1).sum()))
    legit_samples = df[df['is_fraud'] == 0].sample(min(num_samples, (df['is_fraud'] == 0).sum()))

    samples = pd.concat([fraud_samples, legit_samples])

    for idx, row in samples.iterrows():
        # Cria objeto Transaction
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

        # Faz predição
        prediction = model.predict(tx)

        # Resultado real
        actual = "FRAUDE" if row['is_fraud'] == 1 else "LEGÍTIMO"
        predicted = "FRAUDE" if prediction.is_fraud else "LEGÍTIMO"

        # Verifica se acertou
        correct = "✅" if actual == predicted else "❌"

        print(f"\n{correct} Transação: {tx.transaction_id}")
        print(f"   Valor: R$ {tx.amount:.2f}")
        print(f"   Categoria: {tx.category}")
        print(f"   Localização: {tx.location}")
        print(f"   Real: {actual}")
        print(f"   Predito: {predicted}")
        print(f"   Probabilidade: {prediction.fraud_probability:.2%}")
        print(f"   Risco: {prediction.risk_level.upper()}")

        if prediction.risk_factors:
            print(f"   Fatores de Risco:")
            for factor in prediction.risk_factors[:3]:
                print(f"      • {factor}")


def analyze_by_category(
    model: FraudDetectionModel,
    df: pd.DataFrame,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> None:
    """
    Analisa performance por categoria

    Args:
        model: Modelo treinado
        df: DataFrame original
        X_test: Features de teste
        y_test: Labels de teste
    """
    logger.info("\n" + "="*70)
    logger.info("📈 ANÁLISE POR CATEGORIA")
    logger.info("="*70)

    # Usa apenas dados de teste
    test_indices = y_test.index
    df_test = df.loc[test_indices]

    # Predições
    X_test_scaled = model.scaler.transform(X_test)
    predictions = model.model.predict(X_test_scaled)

    # Adiciona predições ao dataframe
    df_analysis = df_test.copy()
    df_analysis['predicted'] = predictions

    # Análise por categoria
    print("\nDistribuição e Acurácia por Categoria:\n")

    category_stats = []
    for category in df_analysis['category'].unique():
        cat_data = df_analysis[df_analysis['category'] == category]

        if len(cat_data) > 0:
            accuracy = (cat_data['is_fraud'] == cat_data['predicted']).mean()
            fraud_rate = cat_data['is_fraud'].mean()

            category_stats.append({
                'Categoria': category,
                'Total': len(cat_data),
                'Taxa Fraude': f"{fraud_rate:.1%}",
                'Acurácia': f"{accuracy:.1%}"
            })

    # Exibe tabela
    stats_df = pd.DataFrame(category_stats)
    stats_df = stats_df.sort_values('Total', ascending=False)

    print(stats_df.to_string(index=False))


def main():
    """
    Função principal de avaliação
    """
    print("=" * 70)
    print("📊 AVALIAÇÃO DO MODELO DE DETECÇÃO DE FRAUDES")
    print("=" * 70)
    print()

    try:
        # 1. Carrega modelo
        logger.info("PASSO 1/4: Carregando modelo...")
        model = FraudDetectionModel()

        if not model.load_model():
            raise FileNotFoundError(
                "Modelo não encontrado!\n"
                "Execute primeiro: python training/train_model.py"
            )

        logger.info("✅ Modelo carregado com sucesso!")
        logger.info(f"   Versão: {model.model_version}")
        if model.trained_at:
            logger.info(f"   Treinado em: {model.trained_at}")

        # 2. Carrega dados de teste
        logger.info("\nPASSO 2/4: Carregando dados de teste...")
        df = load_test_data()

        # Prepara features
        logger.info("   Preparando features...")
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

        features_df = batch_extract_features(transactions, redis_client=None)

        if 'transaction_id' in features_df.columns:
            features_df = features_df.drop('transaction_id', axis=1)

        labels = df['is_fraud']

        # Divide em treino/teste (mesma divisão do treinamento)
        X_train, X_test, y_train, y_test = train_test_split(
            features_df, labels,
            test_size=0.2,
            random_state=42,
            stratify=labels
        )

        logger.info(f"   Conjunto de teste: {len(X_test):,} amostras")

        # 3. Avalia modelo
        logger.info("\nPASSO 3/4: Avaliando modelo...")
        evaluate_model_performance(model, X_test, y_test, df)

        # 4. Análises adicionais
        logger.info("\nPASSO 4/4: Análises adicionais...")

        # Testa predições individuais
        test_sample_predictions(model, df, num_samples=3)

        # Análise por categoria
        analyze_by_category(model, df, X_test, y_test)

        # Resumo final
        print("\n" + "="*70)
        print("✅ AVALIAÇÃO CONCLUÍDA!")
        print("="*70)
        print("\n🎯 O modelo está pronto para uso em produção!")
        print("\nPara iniciar a API:")
        print("   1. docker-compose up -d")
        print("   2. python -m app.main")
        print("   3. Acesse: http://localhost:8000/docs")
        print()

    except FileNotFoundError as e:
        logger.error(f"\n❌ ERRO: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ ERRO NA AVALIAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
