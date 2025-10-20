# 🚀 COMECE AQUI - Sistema de Detecção de Fraudes

**Olá, Natália!** Este é o guia definitivo para iniciar o sistema.

---

## ⚡ OPÇÃO 1: Início Super Rápido (RECOMENDADO)

Execute apenas **UM comando** que faz tudo automaticamente:

```bash
./quick_start.sh
```

Este script vai:
1. ✅ Verificar Python e dependências
2. ✅ Iniciar o Redis automaticamente
3. ✅ Treinar o modelo (se necessário)
4. ✅ Iniciar a API

**Pronto!** A API estará rodando em http://localhost:8000/docs

---

## 🔍 OPÇÃO 2: Diagnóstico Primeiro

Se quiser verificar tudo antes de iniciar:

```bash
# 1. Execute o diagnóstico
python diagnose_system.py

# 2. Se tudo estiver OK, inicie
python start_api.py
```

---

## 📝 OPÇÃO 3: Passo a Passo Manual

Se preferir controle total:

### Passo 1: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 2: Iniciar Redis
```bash
docker-compose up -d redis
```

### Passo 3: Treinar Modelo (primeira vez)
```bash
python training/train_model.py
```

### Passo 4: Iniciar API
```bash
python -m app.main
```

### Passo 5: Testar
Abra no navegador: http://localhost:8000/docs

---

## 🎯 Como Usar a API

### Teste Rápido no Navegador

1. Acesse: http://localhost:8000/docs
2. Clique em **POST /predict**
3. Clique em **Try it out**
4. Use este exemplo:

```json
{
  "transaction_id": "tx_teste_001",
  "user_id": "user_123",
  "amount": 1500.00,
  "merchant": "Loja Eletrônicos",
  "category": "electronics",
  "location": "São Paulo, SP",
  "device": "device_mobile_001"
}
```

5. Clique em **Execute**
6. Veja o resultado!

### Teste com cURL

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_001",
    "user_id": "user_123",
    "amount": 1500.00,
    "merchant": "Loja Teste",
    "category": "electronics",
    "location": "São Paulo, SP",
    "device": "device_001"
  }'
```

### Teste com Python

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "transaction_id": "tx_001",
        "user_id": "user_123",
        "amount": 1500.00,
        "merchant": "Loja Teste",
        "category": "electronics",
        "location": "São Paulo, SP",
        "device": "device_001"
    }
)

print(response.json())
```

---

## 🚨 Problemas Comuns e Soluções

### ❌ "This site can't be reached"

**Causa**: API não está rodando

**Solução**:
```bash
# Execute o diagnóstico
python diagnose_system.py

# Ou use o quick start
./quick_start.sh
```

---

### ❌ "Redis Connection Error"

**Causa**: Redis não está rodando

**Solução**:
```bash
# Inicie o Redis
docker-compose up -d redis

# Aguarde 5 segundos
sleep 5

# Teste
docker-compose ps
```

---

### ❌ "Modelo não está carregado"

**Causa**: Modelo não foi treinado

**Solução**:
```bash
# Treine o modelo
python training/train_model.py

# Reinicie a API
python start_api.py
```

---

### ❌ "Port 8000 already in use"

**Causa**: Algo já está usando a porta 8000

**Solução**:
```bash
# Linux/Mac
kill -9 $(lsof -t -i:8000)

# Então inicie novamente
python start_api.py
```

---

### ❌ "ModuleNotFoundError: No module named 'app'"

**Causa**: Executando do diretório errado

**Solução**:
```bash
# Vá para o diretório do projeto
cd fraud_detection_system

# Verifique que está no lugar certo
ls app/  # Deve mostrar: main.py, models.py, etc.

# Execute novamente
python -m app.main
```

---

## 📚 Documentação Completa

| Arquivo | Descrição |
|---------|-----------|
| **START_HERE.md** | 👈 Você está aqui! |
| **QUICKSTART.md** | Guia rápido 5 minutos |
| **README.md** | Documentação completa |
| **EXAMPLES.md** | Exemplos práticos de uso |
| **TROUBLESHOOTING.md** | Resolução de problemas detalhada |
| **PROJECT_SUMMARY.md** | Estatísticas do projeto |

---

## 🛠️ Scripts Disponíveis

| Script | Descrição | Uso |
|--------|-----------|-----|
| `quick_start.sh` | Inicia tudo automaticamente | `./quick_start.sh` |
| `diagnose_system.py` | Diagnóstico completo | `python diagnose_system.py` |
| `start_api.py` | Inicia apenas a API | `python start_api.py` |
| `setup.sh` | Setup completo inicial | `./setup.sh` |

---

## ✅ Checklist de Verificação

Antes de começar, certifique-se que tem:

- [ ] Python 3.10+ instalado
- [ ] Docker instalado e rodando
- [ ] Git (opcional, mas recomendado)
- [ ] Terminal/CMD aberto
- [ ] Navegador web (Chrome, Firefox, Edge, etc.)

---

## 🎯 Fluxo Recomendado

Para a primeira execução:

```bash
# 1. Vá para o diretório do projeto
cd fraud_detection_system

# 2. Execute o quick start
./quick_start.sh

# 3. Aguarde a API iniciar (você verá mensagens de log)

# 4. Abra o navegador em:
#    http://localhost:8000/docs

# 5. Teste a API!
```

Para execuções posteriores:

```bash
# Apenas certifique-se que o Redis está rodando
docker-compose up -d redis

# E inicie a API
python start_api.py
```

---

## 💡 Dicas Importantes

### 1. **Sempre execute do diretório correto**
```bash
pwd  # Deve mostrar: .../fraud_detection_system
```

### 2. **Use ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU: venv\Scripts\activate  # Windows
```

### 3. **Verifique logs para erros**
A API mostra logs detalhados no terminal

### 4. **Use o diagnóstico quando algo falhar**
```bash
python diagnose_system.py
```

---

## 🌐 URLs Importantes

Quando a API estiver rodando:

- **Documentação Interativa**: http://localhost:8000/docs
- **Documentação Alternativa**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Estatísticas**: http://localhost:8000/stats
- **Métricas Prometheus**: http://localhost:8000/metrics

---

## 🆘 Precisa de Ajuda?

1. **Primeiro**: Execute o diagnóstico
   ```bash
   python diagnose_system.py
   ```

2. **Depois**: Consulte o troubleshooting
   ```bash
   # Leia o guia completo
   cat TROUBLESHOOTING.md
   ```

3. **Se ainda tiver problemas**:
   - Verifique os logs da API
   - Veja os logs do Redis: `docker-compose logs redis`
   - Execute o quick_start.sh novamente

---

## 🚀 Próximos Passos

Depois que a API estiver funcionando:

1. ✅ Teste diferentes transações
2. ✅ Explore a documentação interativa
3. ✅ Leia os EXAMPLES.md para casos de uso
4. ✅ Avalie o modelo: `python training/evaluate_model.py`
5. ✅ Customize para suas necessidades

---

## 🎉 Pronto!

**Agora você tem um sistema completo de detecção de fraudes funcionando!**

Use para:
- 📊 Demonstrações
- 💼 Entrevistas
- 🎓 Aprendizado
- 🚀 Projetos reais

---

**Desenvolvido com ❤️ por Natália Barros**

**Bom uso do sistema!** 🚀✨
