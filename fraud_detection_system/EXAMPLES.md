# 💡 Exemplos Práticos de Uso

Este documento contém exemplos reais de como usar o sistema de detecção de fraudes.

---

## 📋 Índice

1. [Exemplos Básicos](#exemplos-básicos)
2. [Casos de Uso Reais](#casos-de-uso-reais)
3. [Análise em Lote](#análise-em-lote)
4. [Integração com Aplicações](#integração-com-aplicações)
5. [Monitoramento](#monitoramento)

---

## Exemplos Básicos

### Exemplo 1: Primeira Transação de um Novo Usuário

```python
import requests

# Novo usuário fazendo primeira compra pequena
transaction = {
    "transaction_id": "tx_new_user_001",
    "user_id": "user_novo_5000",
    "amount": 89.90,
    "merchant": "Amazon Brasil",
    "category": "electronics",
    "location": "São Paulo, SP",
    "device": "device_mobile_android_001"
}

response = requests.post(
    "http://localhost:8000/predict",
    json=transaction
)

result = response.json()

print(f"""
🔍 ANÁLISE DA TRANSAÇÃO
{'='*50}
Transação ID: {result['transaction_id']}
Usuário: {transaction['user_id']}
Valor: R$ {transaction['amount']:.2f}

📊 RESULTADO:
É Fraude?: {'❌ SIM' if result['is_fraud'] else '✅ NÃO'}
Probabilidade: {result['fraud_probability']:.2%}
Nível de Risco: {result['risk_level'].upper()}
Confiança: {result['confidence_score']:.2%}

💬 EXPLICAÇÃO:
{result['explanation']}

⚠️ FATORES DE RISCO:
""")

for factor in result['risk_factors']:
    print(f"   • {factor}")

print(f"\n🎯 RECOMENDAÇÕES:")
for rec in result['recommendations'][:3]:
    print(f"   {rec}")

print(f"\n⏱️ Tempo de Processamento: {result['processing_time_ms']:.1f}ms")
```

**Resultado Esperado**:
```
🔍 ANÁLISE DA TRANSAÇÃO
==================================================
Transação ID: tx_new_user_001
Usuário: user_novo_5000
Valor: R$ 89.90

📊 RESULTADO:
É Fraude?: ✅ NÃO
Probabilidade: 18.5%
Nível de Risco: LOW
Confiança: 63.0%

💬 EXPLICAÇÃO:
✅ Transação considerada LEGÍTIMA com 81.5% de confiança.
Padrões normais de comportamento identificados.

⚠️ FATORES DE RISCO:
   • Usuário novo no sistema

🎯 RECOMENDAÇÕES:
   ✅ APROVAR transação
   📊 Continuar monitoramento normal
   💾 Registrar para análise de padrões

⏱️ Tempo de Processamento: 42.3ms
```

---

### Exemplo 2: Compra Internacional Suspeita

```python
# Usuário brasileiro fazendo compra alta no exterior de madrugada
from datetime import datetime, timedelta

# Simula compra às 3h da manhã
timestamp_madrugada = (datetime.now() - timedelta(hours=9)).isoformat()

transaction = {
    "transaction_id": "tx_intl_suspicious",
    "user_id": "user_regular_1234",
    "amount": 7500.00,  # Valor muito alto
    "merchant": "Unknown Online Store",
    "category": "electronics",
    "location": "Miami, FL",  # Localização internacional
    "device": "new_device_999",  # Dispositivo desconhecido
    "timestamp": timestamp_madrugada
}

response = requests.post(
    "http://localhost:8000/predict",
    json=transaction
)

result = response.json()

# Análise detalhada
print(f"""
🚨 ALERTA DE TRANSAÇÃO SUSPEITA
{'='*50}

💳 DETALHES DA TRANSAÇÃO:
   ID: {transaction['transaction_id']}
   Valor: R$ {transaction['amount']:,.2f}
   Merchant: {transaction['merchant']}
   Local: {transaction['location']}
   Horário: {timestamp_madrugada}

🎯 ANÁLISE DE FRAUDE:
   Status: {'🚨 FRAUDE DETECTADA' if result['is_fraud'] else '✅ Legítima'}
   Probabilidade: {result['fraud_probability']:.1%}
   Risco: {result['risk_level'].upper()}

📋 FATORES DE RISCO IDENTIFICADOS:
""")

for i, factor in enumerate(result['risk_factors'], 1):
    print(f"   {i}. {factor}")

print(f"\n🛡️ AÇÕES RECOMENDADAS:")
for i, rec in enumerate(result['recommendations'], 1):
    print(f"   {i}. {rec}")
```

---

## Casos de Uso Reais

### Caso 1: E-commerce - Validação em Checkout

```python
class FraudChecker:
    """Integração com sistema de e-commerce"""

    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url

    def validate_purchase(self, order_data):
        """
        Valida uma compra antes de processar pagamento

        Args:
            order_data: Dados do pedido

        Returns:
            dict com decisão e detalhes
        """
        # Converte ordem para formato da API
        transaction = {
            "transaction_id": order_data['order_id'],
            "user_id": order_data['customer_id'],
            "amount": order_data['total_amount'],
            "merchant": order_data.get('store_name', 'Online Store'),
            "category": order_data['product_category'],
            "location": order_data['shipping_address']['city'],
            "device": order_data['device_info']
        }

        # Analisa fraude
        response = requests.post(
            f"{self.api_url}/predict",
            json=transaction
        )

        if response.status_code != 200:
            return {
                'approved': False,
                'reason': 'Erro na análise de fraude',
                'action': 'manual_review'
            }

        result = response.json()

        # Decisão baseada no risco
        if result['risk_level'] == 'high':
            return {
                'approved': False,
                'reason': 'Alto risco de fraude',
                'fraud_probability': result['fraud_probability'],
                'action': 'block_and_notify',
                'details': result['explanation']
            }

        elif result['risk_level'] == 'medium':
            return {
                'approved': False,
                'reason': 'Verificação adicional necessária',
                'fraud_probability': result['fraud_probability'],
                'action': 'require_2fa',
                'details': result['explanation']
            }

        else:  # low risk
            return {
                'approved': True,
                'reason': 'Transação aprovada',
                'fraud_probability': result['fraud_probability'],
                'action': 'process_payment',
                'details': result['explanation']
            }

# Uso
checker = FraudChecker()

order = {
    'order_id': 'ORD-2025-12345',
    'customer_id': 'CUST-9876',
    'total_amount': 459.90,
    'product_category': 'electronics',
    'store_name': 'TechStore Brasil',
    'shipping_address': {
        'city': 'São Paulo, SP',
        'state': 'SP'
    },
    'device_info': 'mobile_app_ios'
}

decision = checker.validate_purchase(order)

if decision['approved']:
    print(f"✅ Pedido {order['order_id']} APROVADO")
    print(f"   Probabilidade de fraude: {decision['fraud_probability']:.1%}")
    # Processar pagamento...
else:
    print(f"❌ Pedido {order['order_id']} BLOQUEADO")
    print(f"   Motivo: {decision['reason']}")
    print(f"   Ação: {decision['action']}")
    # Notificar cliente...
```

---

### Caso 2: Banco - Análise de Transações em Tempo Real

```python
import asyncio
import aiohttp
from typing import List

class BankFraudMonitor:
    """Monitor de fraudes para instituição financeira"""

    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url

    async def analyze_transaction_async(self, session, transaction):
        """Analisa transação de forma assíncrona"""
        async with session.post(
            f"{self.api_url}/predict",
            json=transaction
        ) as response:
            return await response.json()

    async def monitor_transactions(self, transactions: List[dict]):
        """
        Monitora múltiplas transações simultaneamente

        Args:
            transactions: Lista de transações a analisar
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.analyze_transaction_async(session, tx)
                for tx in transactions
            ]

            results = await asyncio.gather(*tasks)

            # Processa resultados
            for tx, result in zip(transactions, results):
                self._process_result(tx, result)

            return results

    def _process_result(self, transaction, result):
        """Processa resultado da análise"""
        if result['is_fraud'] and result['risk_level'] == 'high':
            # Bloqueia cartão imediatamente
            self._block_card(transaction['user_id'])
            self._send_sms_alert(transaction['user_id'])
            print(f"🚨 FRAUDE DETECTADA - Cartão bloqueado: {transaction['user_id']}")

        elif result['risk_level'] == 'medium':
            # Solicita confirmação
            self._request_confirmation(transaction)
            print(f"⚠️ CONFIRMAÇÃO NECESSÁRIA: {transaction['transaction_id']}")

        else:
            # Aprova transação
            print(f"✅ APROVADO: {transaction['transaction_id']}")

    def _block_card(self, user_id):
        """Bloqueia cartão (implementar integração real)"""
        print(f"   🔒 Bloqueando cartão do usuário {user_id}")

    def _send_sms_alert(self, user_id):
        """Envia SMS de alerta (implementar integração real)"""
        print(f"   📱 Enviando SMS para {user_id}")

    def _request_confirmation(self, transaction):
        """Solicita confirmação ao cliente (implementar integração real)"""
        print(f"   📧 Solicitando confirmação para {transaction['user_id']}")

# Uso
monitor = BankFraudMonitor()

# Simula stream de transações
transacoes_stream = [
    {
        "transaction_id": f"tx_bank_{i}",
        "user_id": f"card_{i % 100}",
        "amount": 100 + (i * 50),
        "merchant": "Merchant XYZ",
        "category": "food",
        "location": "São Paulo, SP",
        "device": f"pos_terminal_{i % 10}"
    }
    for i in range(10)
]

# Análise assíncrona
asyncio.run(monitor.monitor_transactions(transacoes_stream))
```

---

## Análise em Lote

### Exemplo: Análise de Transações do Dia Anterior

```python
def analyze_daily_transactions(transactions_file: str):
    """
    Analisa todas as transações do dia anterior

    Args:
        transactions_file: Arquivo CSV com transações
    """
    import pandas as pd

    # Carrega transações
    df = pd.read_csv(transactions_file)

    # Prepara lote (máximo 100 por vez)
    batch_size = 100
    all_results = []

    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]

        # Converte para formato da API
        transactions = batch.to_dict('records')

        # Envia lote
        response = requests.post(
            "http://localhost:8000/predict/batch",
            json={"transactions": transactions}
        )

        if response.status_code == 200:
            result = response.json()
            all_results.extend(result['predictions'])
            print(f"Lote {i//batch_size + 1}: {result['fraud_detected']} fraudes em {result['total_transactions']}")

    # Análise consolidada
    fraud_count = sum(1 for r in all_results if r['is_fraud'])
    total = len(all_results)

    print(f"\n📊 RELATÓRIO DIÁRIO")
    print(f"{'='*50}")
    print(f"Total de transações: {total:,}")
    print(f"Fraudes detectadas: {fraud_count:,} ({fraud_count/total:.2%})")
    print(f"Transações legítimas: {total - fraud_count:,}")

    # Exporta resultados
    results_df = pd.DataFrame(all_results)
    results_df.to_csv('fraud_analysis_results.csv', index=False)
    print(f"\n✅ Resultados salvos em: fraud_analysis_results.csv")

# Uso
analyze_daily_transactions('transactions_yesterday.csv')
```

---

## Integração com Aplicações

### Flask Web App

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
FRAUD_API = "http://localhost:8000"

@app.route('/checkout', methods=['POST'])
def checkout():
    """Endpoint de checkout com validação de fraude"""

    order = request.json

    # Prepara transação
    transaction = {
        "transaction_id": order['id'],
        "user_id": order['customer_id'],
        "amount": order['total'],
        "merchant": "My Store",
        "category": order['category'],
        "location": order['location'],
        "device": request.headers.get('User-Agent', 'unknown')
    }

    # Valida fraude
    response = requests.post(
        f"{FRAUD_API}/predict",
        json=transaction
    )

    if response.status_code != 200:
        return jsonify({
            'success': False,
            'error': 'Erro na validação'
        }), 500

    fraud_result = response.json()

    # Decisão
    if fraud_result['risk_level'] == 'high':
        return jsonify({
            'success': False,
            'message': 'Transação bloqueada por segurança',
            'requires_verification': True
        }), 403

    # Aprova e processa
    # ... processar pagamento ...

    return jsonify({
        'success': True,
        'order_id': order['id'],
        'fraud_check': {
            'passed': True,
            'risk_level': fraud_result['risk_level'],
            'probability': fraud_result['fraud_probability']
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## Monitoramento

### Script de Monitoramento Contínuo

```python
import time
import requests
from datetime import datetime

def monitor_system_health():
    """Monitora saúde do sistema continuamente"""

    while True:
        try:
            # Health check
            response = requests.get("http://localhost:8000/health")

            if response.status_code == 200:
                health = response.json()

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                print(f"\n[{timestamp}] 📊 STATUS DO SISTEMA")
                print(f"{'='*60}")
                print(f"Status Geral: {health['status'].upper()}")
                print(f"API: {health['api_status']}")
                print(f"Modelo: {health['model_status']}")
                print(f"Redis: {health['redis_status']}")
                print(f"\n📈 MÉTRICAS:")
                print(f"   Total de Predições: {health['total_predictions']:,}")
                print(f"   Cache Hit Rate: {health['cache_hit_rate']:.2%}")
                print(f"   Tempo Médio: {health['average_response_time_ms']:.1f}ms")

                # Alerta se houver problemas
                if health['status'] != 'healthy':
                    print(f"\n⚠️ ALERTA: Sistema não está totalmente saudável!")
                    # Enviar notificação...

            else:
                print(f"❌ ERRO: API não respondeu (status {response.status_code})")

        except Exception as e:
            print(f"❌ ERRO ao verificar saúde: {e}")

        # Aguarda 30 segundos
        time.sleep(30)

if __name__ == '__main__':
    print("🔍 Iniciando monitoramento do sistema...")
    print("   Pressione Ctrl+C para parar\n")
    try:
        monitor_system_health()
    except KeyboardInterrupt:
        print("\n\n👋 Monitoramento encerrado")
```

---

## 🎯 Mais Exemplos

Consulte também:
- [README.md](README.md) - Documentação completa
- [QUICKSTART.md](QUICKSTART.md) - Início rápido
- `/docs` - Documentação interativa da API

---

**Desenvolvido com ❤️ por Natália Barros**
