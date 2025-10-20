# 🚀 Sistema de Detecção de Fraudes em Tempo Real

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-7.0-red.svg)](https://redis.io/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Sistema completo de detecção de fraudes em transações financeiras usando Machine Learning, com API REST em tempo real, cache inteligente e monitoramento Prometheus.**

Desenvolvido por **Natália Barros** como projeto de portfólio para demonstração de habilidades em:
- Machine Learning (Random Forest)
- Desenvolvimento de APIs REST (FastAPI)
- Arquitetura de Microserviços
- Cache e Performance (Redis)
- Monitoramento e Observabilidade (Prometheus)
- Docker e DevOps

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#️-arquitetura)
- [Instalação](#-instalação)
- [Uso Rápido](#-uso-rápido)
- [Documentação da API](#-documentação-da-api)
- [Treinamento do Modelo](#-treinamento-do-modelo)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Monitoramento](#-monitoramento)
- [Testes](#-testes)
- [Deploy](#-deploy)
- [Roadmap](#-roadmap)
- [Contribuindo](#-contribuindo)
- [Contato](#-contato)

---

## 🎯 Visão Geral

Este sistema detecta fraudes em transações financeiras em **tempo real** utilizando um modelo de **Random Forest** treinado com features comportamentais, temporais e geográficas.

### Por que este projeto é único?

✨ **Production-Ready**: Código preparado para ambiente de produção
🚀 **Alta Performance**: Cache Redis com 70%+ de taxa de acerto
📊 **Explicabilidade**: Cada predição vem com explicação human-readable
🔍 **Monitoramento**: Métricas Prometheus para observabilidade completa
🎓 **Bem Documentado**: Comentários detalhados em português em todo o código
🐳 **Containerizado**: Docker Compose para setup em segundos

### Métricas do Modelo

| Métrica | Valor |
|---------|-------|
| **Acurácia** | ~96% |
| **Precisão** | ~94% |
| **Recall** | ~92% |
| **F1-Score** | ~93% |
| **AUC-ROC** | ~98% |

---

## ✨ Funcionalidades

### 🔍 Detecção de Fraudes

- ✅ Análise em tempo real (< 50ms por predição)
- ✅ Probabilidade de fraude com nível de risco (Low/Medium/High)
- ✅ Explicação detalhada das decisões
- ✅ Identificação de fatores de risco
- ✅ Recomendações de ação automáticas

### 🎯 Engenharia de Features

O sistema analisa **35+ features** incluindo:

#### Features Transacionais
- Valor da transação (normalizado e em faixas)
- Categoria da compra
- Estabelecimento

#### Features Temporais
- Hora do dia (com encoding cíclico)
- Dia da semana
- Período do dia (madrugada, manhã, tarde, noite)
- Horários suspeitos

#### Features Comportamentais
- Desvio do valor médio do usuário
- Categoria usual vs atual
- Localização usual vs atual
- Dispositivo conhecido vs desconhecido
- Tempo desde última transação
- Taxa de fraude histórica do usuário

#### Features Geográficas
- Localização (cidades grandes vs pequenas)
- Padrões de movimento

### 🚀 API REST

- **FastAPI** com documentação automática (Swagger/OpenAPI)
- **CORS** configurado
- **Health checks** para monitoramento
- **Middleware** para tracking de performance
- **Rate limiting** ready (implementável)

### 💾 Cache Inteligente

- **Redis** para cache de predições
- **TTL** configurável (default: 1 hora)
- **Storage** de histórico de transações
- **Métricas** de cache hit rate

### 📊 Monitoramento

- **Prometheus** metrics export
- **Métricas customizadas**:
  - Total de predições
  - Taxa de fraude detectada
  - Tempo de resposta
  - Cache hit rate
  - Status dos componentes
- **Health checks** automáticos

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        Cliente                              │
│                    (Aplicação/Browser)                      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Endpoints   │  │  Middleware  │  │    Models    │      │
│  │   /predict   │  │   Logging    │  │   Pydantic   │      │
│  │   /health    │  │   Metrics    │  │  Validation  │      │
│  │   /metrics   │  │    CORS      │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────┬──────────────────────────────────────────────────┘
           │
           ├─────────────────┬──────────────────┬─────────────
           ▼                 ▼                  ▼
    ┌────────────┐    ┌────────────┐    ┌────────────┐
    │   Redis    │    │ ML Model   │    │Prometheus  │
    │   Cache    │    │  Random    │    │  Metrics   │
    │  Storage   │    │  Forest    │    │ Collector  │
    └────────────┘    └────────────┘    └────────────┘
                      │
                      ▼
              ┌──────────────┐
              │   Feature    │
              │  Engineer    │
              │ 35+ Features │
              └──────────────┘
```

### Componentes Principais

1. **app/main.py**: API FastAPI com endpoints
2. **app/ml_model.py**: Modelo Random Forest
3. **app/features.py**: Engenharia de features
4. **app/database.py**: Cliente Redis
5. **app/monitoring.py**: Métricas Prometheus
6. **app/models.py**: Modelos Pydantic

---

## 🔧 Instalação

### Pré-requisitos

- **Python 3.10+**
- **Docker & Docker Compose** (para Redis)
- **Git**

### Passo 1: Clone o Repositório

```bash
git clone https://github.com/seu-usuario/fraud-detection-system.git
cd fraud-detection-system
```

### Passo 2: Crie um Ambiente Virtual

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Passo 3: Instale as Dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Inicie o Redis

```bash
docker-compose up -d redis
```

Verifique que o Redis está rodando:

```bash
docker-compose ps
```

### Passo 5: Treine o Modelo

```bash
python training/train_model.py
```

Este comando irá:
1. Gerar ~20.000 transações sintéticas
2. Extrair features
3. Treinar o modelo Random Forest
4. Avaliar performance
5. Salvar o modelo em `models/fraud_model.pkl`

**Tempo estimado**: 1-2 minutos

---

## ⚡ Uso Rápido

### Inicie a API

```bash
python -m app.main
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação Interativa**: http://localhost:8000/docs
- **Documentação Alternativa**: http://localhost:8000/redoc

### Teste a API

#### Usando cURL

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_001",
    "user_id": "user_123",
    "amount": 1500.00,
    "merchant": "Loja Suspeita",
    "category": "electronics",
    "location": "Cidade Desconhecida",
    "device": "new_device"
  }'
```

#### Usando Python

```python
import requests

transaction = {
    "transaction_id": "tx_001",
    "user_id": "user_123",
    "amount": 1500.00,
    "merchant": "Loja Eletrônicos",
    "category": "electronics",
    "location": "São Paulo, SP",
    "device": "device_mobile_001"
}

response = requests.post(
    "http://localhost:8000/predict",
    json=transaction
)

result = response.json()
print(f"Fraude: {result['is_fraud']}")
print(f"Probabilidade: {result['fraud_probability']:.2%}")
print(f"Risco: {result['risk_level']}")
print(f"Explicação: {result['explanation']}")
```

### Resposta Esperada

```json
{
  "transaction_id": "tx_001",
  "is_fraud": true,
  "fraud_probability": 0.87,
  "risk_level": "high",
  "confidence_score": 0.92,
  "explanation": "⚠️ FRAUDE ALTAMENTE SUSPEITA detectada com 87.0% de confiança...",
  "risk_factors": [
    "Valor 3x acima da média do usuário",
    "Localização nunca antes utilizada",
    "Dispositivo desconhecido"
  ],
  "processing_time_ms": 45.2,
  "model_version": "1.0.0",
  "recommendations": [
    "🚫 BLOQUEAR transação imediatamente",
    "📧 Notificar usuário via email e SMS",
    "🔒 Suspender temporariamente a conta"
  ]
}
```

---

## 📚 Documentação da API

### Endpoints Principais

#### POST /predict
Analisa uma transação e retorna predição de fraude.

**Request Body**:
```json
{
  "transaction_id": "string",
  "user_id": "string",
  "amount": 0,
  "merchant": "string",
  "category": "electronics",
  "location": "string",
  "device": "string"
}
```

**Response**: Objeto `FraudPrediction`

---

#### POST /predict/batch
Analisa múltiplas transações em lote (máximo 100).

**Request Body**:
```json
{
  "transactions": [...]
}
```

**Response**: Objeto `BatchPredictionResponse`

---

#### GET /user/{user_id}/history
Retorna histórico e estatísticas de um usuário.

**Response**: Objeto `UserHistory`

---

#### GET /health
Verifica status de saúde do sistema.

**Response**: Objeto `SystemHealth`

---

#### GET /metrics
Retorna métricas no formato Prometheus.

**Response**: Text (formato Prometheus)

---

### Categorias Suportadas

- `electronics`: Eletrônicos
- `fashion`: Moda
- `food`: Alimentação
- `travel`: Viagens
- `services`: Serviços
- `entertainment`: Entretenimento
- `health`: Saúde
- `other`: Outros

---

## 🎓 Treinamento do Modelo

### Gerar Dados Sintéticos

```bash
python training/data_generator.py
```

Gera dataset com:
- 1000 usuários
- ~20 transações por usuário
- 10% de taxa de fraude
- Padrões realistas de comportamento

### Treinar o Modelo

```bash
python training/train_model.py
```

Processo completo:
1. Carrega/gera dados
2. Extrai 35+ features
3. Divide treino/teste (80/20)
4. Treina Random Forest
5. Avalia performance
6. Salva modelo

**Parâmetros do Random Forest**:
- `n_estimators`: 100
- `max_depth`: 20
- `class_weight`: 'balanced'
- `random_state`: 42

### Avaliar o Modelo

```bash
python training/evaluate_model.py
```

Gera:
- Métricas detalhadas
- Matriz de confusão
- Features mais importantes
- Exemplos de predições
- Análise por categoria

---

## 💡 Exemplos de Uso

### Exemplo 1: Transação Legítima

```python
legitimate_transaction = {
    "transaction_id": "tx_legit_001",
    "user_id": "user_123",
    "amount": 150.00,  # Valor normal
    "merchant": "Supermercado",
    "category": "food",
    "location": "São Paulo, SP",  # Localização usual
    "device": "device_mobile_001"  # Dispositivo conhecido
}

response = requests.post(
    "http://localhost:8000/predict",
    json=legitimate_transaction
)

# Resultado esperado:
# is_fraud: false
# fraud_probability: ~0.15 (15%)
# risk_level: "low"
```

### Exemplo 2: Transação Fraudulenta

```python
fraud_transaction = {
    "transaction_id": "tx_fraud_001",
    "user_id": "user_123",
    "amount": 5000.00,  # Valor muito alto
    "merchant": "Loja Desconhecida",
    "category": "electronics",
    "location": "Cidade Distante",  # Localização incomum
    "device": "new_device_xyz"  # Dispositivo novo
}

response = requests.post(
    "http://localhost:8000/predict",
    json=fraud_transaction
)

# Resultado esperado:
# is_fraud: true
# fraud_probability: ~0.85 (85%)
# risk_level: "high"
```

### Exemplo 3: Análise em Lote

```python
batch_request = {
    "transactions": [
        transaction_1,
        transaction_2,
        transaction_3,
        # ... até 100 transações
    ]
}

response = requests.post(
    "http://localhost:8000/predict/batch",
    json=batch_request
)

result = response.json()
print(f"Total analisado: {result['total_transactions']}")
print(f"Fraudes detectadas: {result['fraud_detected']}")
```

### Exemplo 4: Consultar Histórico

```python
response = requests.get(
    "http://localhost:8000/user/user_123/history"
)

history = response.json()
print(f"Total de transações: {history['total_transactions']}")
print(f"Taxa de fraude: {history['fraud_rate']}%")
print(f"Categorias preferidas: {history['most_common_category']}")
```

---

## 📊 Monitoramento

### Métricas Disponíveis

O sistema exporta as seguintes métricas Prometheus:

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `fraud_detection_predictions_total` | Counter | Total de predições (por resultado) |
| `fraud_detection_prediction_duration_seconds` | Histogram | Tempo de processamento |
| `fraud_detection_fraud_rate_percent` | Gauge | Taxa de fraude detectada |
| `fraud_detection_cache_hit_rate` | Gauge | Taxa de acerto do cache |
| `fraud_detection_component_status` | Gauge | Status dos componentes |
| `fraud_detection_model_accuracy` | Gauge | Acurácia do modelo |

### Configurar Prometheus

Crie `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fraud-detection'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

Inicie Prometheus:

```bash
docker run -d \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

Acesse: http://localhost:9090

### Queries Úteis

```promql
# Taxa de fraude nas últimas 24h
rate(fraud_detection_predictions_total{result="fraud"}[24h])

# P95 tempo de resposta
histogram_quantile(0.95, fraud_detection_prediction_duration_seconds)

# Taxa de cache hit
fraud_detection_cache_hit_rate
```

---

## 🧪 Testes

### Executar Testes

```bash
# Instalar pytest
pip install pytest pytest-asyncio httpx

# Executar testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=app --cov-report=html
```

### Criar Testes

Exemplo de teste:

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_endpoint():
    transaction = {
        "transaction_id": "test_001",
        "user_id": "test_user",
        "amount": 100.00,
        "merchant": "Test Store",
        "category": "food",
        "location": "São Paulo, SP",
        "device": "test_device"
    }

    response = client.post("/predict", json=transaction)

    assert response.status_code == 200
    data = response.json()
    assert "is_fraud" in data
    assert "fraud_probability" in data
    assert 0 <= data["fraud_probability"] <= 1
```

---

## 🚀 Deploy

### Opção 1: Docker Compose (Recomendado)

```bash
# Descomente o serviço 'api' no docker-compose.yml

# Construir e iniciar
docker-compose up -d

# Verificar logs
docker-compose logs -f api

# Parar serviços
docker-compose down
```

### Opção 2: Deploy Manual

```bash
# Produção com Gunicorn
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Opção 3: Deploy em Cloud

#### AWS (EC2 + ECS)

```bash
# Criar imagem Docker
docker build -t fraud-detection:latest .

# Push para ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-url>
docker tag fraud-detection:latest <ecr-url>:latest
docker push <ecr-url>:latest

# Deploy com ECS
aws ecs update-service --cluster fraud-cluster --service fraud-api
```

#### Heroku

```bash
# Login
heroku login

# Criar app
heroku create fraud-detection-api

# Adicionar Redis
heroku addons:create heroku-redis:hobby-dev

# Deploy
git push heroku main
```

---

## 🗺️ Roadmap

### Em Desenvolvimento

- [ ] Testes unitários completos (coverage 80%+)
- [ ] Dockerfile otimizado multi-stage
- [ ] CI/CD com GitHub Actions
- [ ] Dashboard Grafana com métricas

### Próximas Features

- [ ] Autenticação JWT
- [ ] Rate limiting
- [ ] Modelo de Deep Learning (LSTM/Transformer)
- [ ] Feature Store (Feast)
- [ ] A/B Testing de modelos
- [ ] Retreinamento automático
- [ ] Integração com Kafka para streaming

### Melhorias Futuras

- [ ] GraphQL API
- [ ] WebSocket para notificações em tempo real
- [ ] SDK Python para clientes
- [ ] Suporte multi-idioma
- [ ] Explicabilidade com SHAP/LIME

---

## 📄 Estrutura do Projeto

```
fraud_detection_system/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── database.py          # Redis client
│   ├── ml_model.py          # Random Forest model
│   ├── features.py          # Feature engineering
│   └── monitoring.py        # Prometheus metrics
├── training/
│   ├── __init__.py
│   ├── data_generator.py    # Synthetic data generator
│   ├── train_model.py       # Training script
│   └── evaluate_model.py    # Evaluation script
├── tests/
│   └── (testes)
├── models/                  # Trained models (gitignored)
│   ├── fraud_model.pkl
│   └── scaler.pkl
├── data/                    # Data files (gitignored)
│   └── transactions.csv
├── docker-compose.yml       # Docker orchestration
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 👤 Contato

**Natália Barros**
Desenvolvedora Python | Machine Learning Engineer

- 💼 LinkedIn: [linkedin.com/in/natalia-barros](https://linkedin.com/in/natalia-barros)
- 📧 Email: natalia.barros@email.com
- 🐙 GitHub: [github.com/nataliabarros](https://github.com/nataliabarros)

---

## 🙏 Agradecimentos

- FastAPI pela excelente documentação
- Scikit-learn pela biblioteca robusta de ML
- Comunidade Python pelo suporte

---

## ⭐ Mostre seu Apoio

Se este projeto foi útil para você, considere dar uma estrela ⭐!

---

**Desenvolvido com ❤️ por Natália Barros**
