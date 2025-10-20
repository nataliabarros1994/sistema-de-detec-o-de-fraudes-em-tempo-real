# 🚀 Guia Rápido de Início - 5 Minutos

Este guia vai te ajudar a ter o sistema funcionando em **menos de 5 minutos**!

---

## ⚡ Passo a Passo

### 1️⃣ Instalar Dependências (1 min)

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

---

### 2️⃣ Iniciar Redis (30 segundos)

```bash
docker-compose up -d redis
```

**Verificar**:
```bash
docker-compose ps
# Deve mostrar redis rodando
```

---

### 3️⃣ Treinar o Modelo (1-2 min)

```bash
python training/train_model.py
```

**O que acontece**:
- ✅ Gera 20.000 transações sintéticas
- ✅ Extrai 35+ features
- ✅ Treina Random Forest
- ✅ Salva modelo em `models/`

**Resultado esperado**:
```
✅ TREINAMENTO CONCLUÍDO COM SUCESSO!
📊 Performance do Modelo:
   • Acurácia: 96%
   • Precisão: 94%
   • Recall: 92%
   • F1-Score: 93%
   • AUC-ROC: 98%
```

---

### 4️⃣ Iniciar a API (10 segundos)

```bash
python -m app.main
```

**Acesse**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs ⭐

---

### 5️⃣ Testar a API (30 segundos)

#### Opção A: Navegador

1. Abra http://localhost:8000/docs
2. Clique em **POST /predict**
3. Clique em **Try it out**
4. Use o exemplo abaixo
5. Clique em **Execute**

#### Opção B: cURL

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_teste_001",
    "user_id": "user_999",
    "amount": 5000.00,
    "merchant": "Loja Suspeita",
    "category": "electronics",
    "location": "Lugar Desconhecido",
    "device": "new_device_123"
  }'
```

#### Opção C: Python

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "transaction_id": "tx_001",
        "user_id": "user_123",
        "amount": 1500.00,
        "merchant": "Magazine Tech",
        "category": "electronics",
        "location": "São Paulo, SP",
        "device": "device_mobile_001"
    }
)

print(response.json())
```

---

## 🎯 Próximos Passos

### Explorar a API

1. **Health Check**: http://localhost:8000/health
2. **Métricas**: http://localhost:8000/metrics
3. **Stats**: http://localhost:8000/stats

### Analisar o Modelo

```bash
# Ver métricas detalhadas e exemplos
python training/evaluate_model.py
```

### Testar Diferentes Cenários

**Transação Normal** (baixo risco):
```json
{
  "transaction_id": "tx_normal",
  "user_id": "user_123",
  "amount": 80.00,
  "merchant": "Supermercado",
  "category": "food",
  "location": "São Paulo, SP",
  "device": "device_mobile_001"
}
```

**Transação Suspeita** (alto risco):
```json
{
  "transaction_id": "tx_suspeita",
  "user_id": "user_123",
  "amount": 8000.00,
  "merchant": "Loja Internacional",
  "category": "travel",
  "location": "Miami, FL",
  "device": "new_device_unknown"
}
```

---

## ❓ Resolução de Problemas

### Redis não está rodando

```bash
# Parar e reiniciar
docker-compose down
docker-compose up -d redis

# Verificar logs
docker-compose logs redis
```

### Modelo não encontrado

```bash
# Treinar novamente
python training/train_model.py
```

### Porta 8000 já está em uso

```bash
# Mudar a porta no comando
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Erro de importação

```bash
# Verificar ambiente virtual está ativado
which python  # Deve mostrar path do venv

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Documentação Completa

Para mais detalhes, consulte o [README.md](README.md)

---

## 💬 Precisa de Ajuda?

- 📧 Email: natalia.barros@email.com
- 💼 LinkedIn: [linkedin.com/in/natalia-barros](https://linkedin.com/in/natalia-barros)

---

**✨ Bom uso do sistema! ✨**
