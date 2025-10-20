"""
Gerador de Dados Sintéticos para Treinamento
=============================================
Este módulo gera dados sintéticos realistas de transações
para treinamento do modelo de detecção de fraudes.

Gera dois tipos de transações:
1. Legítimas: Padrões normais de compra
2. Fraudulentas: Padrões suspeitos e anômalos

Autor: Natália Barros
Data: 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import random
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransactionDataGenerator:
    """
    Gera dados sintéticos de transações para treinamento

    Simula comportamento realista de usuários e fraudadores
    """

    def __init__(self, seed: int = 42):
        """
        Inicializa o gerador de dados

        Args:
            seed: Seed para reprodutibilidade
        """
        random.seed(seed)
        np.random.seed(seed)

        # Dados de referência
        self.categories = [
            "electronics", "fashion", "food", "travel",
            "services", "entertainment", "health", "other"
        ]

        self.cities_brazil = [
            "São Paulo, SP", "Rio de Janeiro, RJ", "Brasília, DF",
            "Salvador, BA", "Fortaleza, CE", "Belo Horizonte, MG",
            "Manaus, AM", "Curitiba, PR", "Recife, PE", "Porto Alegre, RS",
            "Goiânia, GO", "Belém, PA", "Guarulhos, SP", "Campinas, SP",
            "São Luís, MA", "Maceió, AL", "Natal, RN", "Teresina, PI"
        ]

        self.merchants = {
            "electronics": [
                "Magazine Luiza", "Casas Bahia", "Fast Shop",
                "Kabum", "Pichau", "Amazon Brasil"
            ],
            "fashion": [
                "Renner", "C&A", "Zara", "Riachuelo",
                "Shein", "Mercado Livre Moda"
            ],
            "food": [
                "iFood", "Rappi", "Uber Eats", "Carrefour",
                "Pão de Açúcar", "Restaurante Local"
            ],
            "travel": [
                "Decolar", "CVC", "MaxMilhas", "Airbnb",
                "Hotel Urbano", "Booking.com"
            ],
            "services": [
                "Netflix", "Spotify", "Amazon Prime",
                "Disney+", "Uber", "99"
            ],
            "entertainment": [
                "Cinemark", "Ingresso.com", "Steam",
                "PlayStation Store", "Xbox Live"
            ],
            "health": [
                "Drogasil", "RaiaDrogasil", "Farmácia Popular",
                "Clínica Médica", "Laboratório"
            ],
            "other": [
                "Loja Variada", "Marketplace", "Serviço Geral"
            ]
        }

        logger.info("🎲 TransactionDataGenerator inicializado")

    def generate_legitimate_transaction(
        self,
        user_id: str,
        transaction_id: str,
        user_profile: Dict
    ) -> Dict:
        """
        Gera uma transação legítima baseada no perfil do usuário

        Args:
            user_id: ID do usuário
            transaction_id: ID da transação
            user_profile: Perfil do usuário com preferências

        Returns:
            Dicionário com dados da transação
        """
        # Categoria baseada nas preferências do usuário
        category = random.choice(user_profile['preferred_categories'])

        # Merchant da categoria
        merchant = random.choice(self.merchants[category])

        # Valor baseado no padrão de gasto do usuário
        avg_amount = user_profile['avg_spending']
        std_amount = avg_amount * 0.3  # Desvio padrão de 30%
        amount = max(10, np.random.normal(avg_amount, std_amount))

        # Localização preferida do usuário
        location = random.choice(user_profile['usual_locations'])

        # Dispositivo conhecido
        device = random.choice(user_profile['known_devices'])

        # Horário normal (8h-22h com maior probabilidade)
        hour = int(np.random.normal(15, 4))  # Média às 15h
        hour = max(6, min(23, hour))  # Limita entre 6h e 23h

        # Data aleatória nos últimos 90 dias
        days_ago = random.randint(0, 90)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=24-hour)

        return {
            'transaction_id': transaction_id,
            'user_id': user_id,
            'amount': round(amount, 2),
            'merchant': merchant,
            'category': category,
            'location': location,
            'device': device,
            'timestamp': timestamp.isoformat(),
            'is_fraud': 0  # Legítima
        }

    def generate_fraudulent_transaction(
        self,
        user_id: str,
        transaction_id: str,
        user_profile: Dict
    ) -> Dict:
        """
        Gera uma transação fraudulenta com padrões suspeitos

        Args:
            user_id: ID do usuário
            transaction_id: ID da transação
            user_profile: Perfil do usuário (para criar anomalias)

        Returns:
            Dicionário com dados da transação fraudulenta
        """
        # Tipos de fraude simulados
        fraud_types = [
            'high_value',      # Valor muito alto
            'unusual_location', # Localização incomum
            'new_device',      # Dispositivo desconhecido
            'unusual_hour',    # Horário suspeito
            'rapid_succession', # Múltiplas transações rápidas
            'unusual_category'  # Categoria incomum
        ]

        fraud_type = random.choice(fraud_types)

        # Categoria - pode ser incomum para o usuário
        if fraud_type == 'unusual_category':
            # Categoria que o usuário nunca usa
            all_categories = set(self.categories)
            preferred = set(user_profile['preferred_categories'])
            unusual_categories = list(all_categories - preferred)
            category = random.choice(unusual_categories) if unusual_categories else random.choice(self.categories)
        else:
            # Categoria suspeita comum em fraudes
            category = random.choice(['electronics', 'travel', 'other'])

        merchant = random.choice(self.merchants[category])

        # Valor - geralmente muito alto em fraudes
        if fraud_type == 'high_value':
            # 3 a 10 vezes o valor médio do usuário
            amount = user_profile['avg_spending'] * random.uniform(3, 10)
        else:
            # Valor alto mas não absurdo
            amount = user_profile['avg_spending'] * random.uniform(1.5, 4)

        # Localização - pode ser incomum
        if fraud_type == 'unusual_location':
            # Localização que o usuário nunca usa
            unusual_locations = [loc for loc in self.cities_brazil
                                if loc not in user_profile['usual_locations']]
            location = random.choice(unusual_locations) if unusual_locations else random.choice(self.cities_brazil)
        else:
            location = random.choice(self.cities_brazil)

        # Dispositivo - muitas vezes novo em fraudes
        if fraud_type == 'new_device':
            device = f"new_device_{random.randint(1000, 9999)}"
        else:
            device = random.choice(user_profile['known_devices'])

        # Horário - fraudes ocorrem mais na madrugada
        if fraud_type == 'unusual_hour':
            hour = random.randint(0, 5)  # Madrugada
        else:
            hour = random.randint(0, 23)

        # Data aleatória nos últimos 90 dias
        days_ago = random.randint(0, 90)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=24-hour)

        return {
            'transaction_id': transaction_id,
            'user_id': user_id,
            'amount': round(amount, 2),
            'merchant': merchant,
            'category': category,
            'location': location,
            'device': device,
            'timestamp': timestamp.isoformat(),
            'is_fraud': 1,  # Fraudulenta
            'fraud_type': fraud_type  # Para análise
        }

    def generate_user_profile(self, user_id: str) -> Dict:
        """
        Gera um perfil de usuário com comportamento consistente

        Args:
            user_id: ID do usuário

        Returns:
            Dicionário com perfil do usuário
        """
        # Nível de gasto (baixo, médio, alto)
        spending_level = random.choice(['low', 'medium', 'high'])

        if spending_level == 'low':
            avg_spending = random.uniform(50, 200)
        elif spending_level == 'medium':
            avg_spending = random.uniform(200, 800)
        else:  # high
            avg_spending = random.uniform(800, 3000)

        # Categorias preferidas (2-4 categorias)
        num_categories = random.randint(2, 4)
        preferred_categories = random.sample(self.categories, num_categories)

        # Localizações usuais (1-3 cidades)
        num_locations = random.randint(1, 3)
        usual_locations = random.sample(self.cities_brazil, num_locations)

        # Dispositivos conhecidos (1-3 dispositivos)
        num_devices = random.randint(1, 3)
        known_devices = [
            f"device_{'mobile' if random.random() > 0.5 else 'web'}_{random.randint(100, 999)}"
            for _ in range(num_devices)
        ]

        return {
            'user_id': user_id,
            'spending_level': spending_level,
            'avg_spending': avg_spending,
            'preferred_categories': preferred_categories,
            'usual_locations': usual_locations,
            'known_devices': known_devices
        }

    def generate_dataset(
        self,
        num_users: int = 1000,
        transactions_per_user: int = 20,
        fraud_rate: float = 0.1
    ) -> pd.DataFrame:
        """
        Gera dataset completo de transações

        Args:
            num_users: Número de usuários a gerar
            transactions_per_user: Transações por usuário (média)
            fraud_rate: Taxa de fraude desejada (0-1)

        Returns:
            DataFrame com todas as transações
        """
        logger.info(f"🎲 Gerando dataset...")
        logger.info(f"   Usuários: {num_users}")
        logger.info(f"   Transações/usuário: ~{transactions_per_user}")
        logger.info(f"   Taxa de fraude: {fraud_rate:.1%}")

        all_transactions = []
        transaction_counter = 1

        # Gera perfis de usuários
        logger.info("👥 Gerando perfis de usuários...")
        user_profiles = {
            f"user_{i:04d}": self.generate_user_profile(f"user_{i:04d}")
            for i in range(num_users)
        }

        # Gera transações para cada usuário
        logger.info("💳 Gerando transações...")
        for user_id, profile in user_profiles.items():
            # Número de transações para este usuário (variável)
            num_transactions = max(1, int(np.random.normal(transactions_per_user, 5)))

            for _ in range(num_transactions):
                transaction_id = f"tx_{transaction_counter:06d}"

                # Decide se é fraude baseado na taxa desejada
                is_fraud = random.random() < fraud_rate

                if is_fraud:
                    transaction = self.generate_fraudulent_transaction(
                        user_id, transaction_id, profile
                    )
                else:
                    transaction = self.generate_legitimate_transaction(
                        user_id, transaction_id, profile
                    )

                all_transactions.append(transaction)
                transaction_counter += 1

        # Cria DataFrame
        df = pd.DataFrame(all_transactions)

        # Ordena por timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)

        # Estatísticas
        total_transactions = len(df)
        total_frauds = df['is_fraud'].sum()
        actual_fraud_rate = total_frauds / total_transactions

        logger.info("✅ Dataset gerado com sucesso!")
        logger.info(f"   Total de transações: {total_transactions:,}")
        logger.info(f"   Transações legítimas: {total_transactions - total_frauds:,}")
        logger.info(f"   Transações fraudulentas: {total_frauds:,}")
        logger.info(f"   Taxa de fraude real: {actual_fraud_rate:.2%}")

        return df

    def save_dataset(
        self,
        df: pd.DataFrame,
        filepath: str = "data/transactions.csv"
    ) -> None:
        """
        Salva dataset em arquivo CSV

        Args:
            df: DataFrame com transações
            filepath: Caminho do arquivo
        """
        import os

        # Cria diretório se não existir
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Salva CSV
        df.to_csv(filepath, index=False)

        logger.info(f"💾 Dataset salvo em: {filepath}")
        logger.info(f"   Tamanho do arquivo: {os.path.getsize(filepath) / 1024:.1f} KB")


def main():
    """
    Função principal para gerar dataset de treinamento
    """
    print("=" * 60)
    print("🎲 GERADOR DE DADOS SINTÉTICOS PARA DETECÇÃO DE FRAUDES")
    print("=" * 60)
    print()

    # Cria gerador
    generator = TransactionDataGenerator(seed=42)

    # Gera dataset
    df = generator.generate_dataset(
        num_users=1000,          # 1000 usuários
        transactions_per_user=20, # ~20 transações por usuário
        fraud_rate=0.10          # 10% de fraudes
    )

    # Exibe amostra
    print("\n📊 AMOSTRA DO DATASET:\n")
    print(df.head(10))

    print("\n📈 ESTATÍSTICAS POR CATEGORIA:\n")
    print(df.groupby('category')['is_fraud'].agg(['count', 'sum', 'mean']))

    # Salva dataset
    generator.save_dataset(df, filepath="data/transactions.csv")

    print("\n✅ Processo concluído!")
    print("\nPróximo passo: Execute o treinamento do modelo")
    print("  python training/train_model.py")


if __name__ == "__main__":
    main()
