# 🔧 Guia de Troubleshooting

Este guia ajuda a resolver os problemas mais comuns ao executar o sistema.

---

## 🚨 Problema: "This site can't be reached" / ERR_CONNECTION_REFUSED

### Sintomas
```
localhost refused to connect
ERR_CONNECTION_REFUSED
```

### Diagnóstico

Execute o script de diagnóstico:
```bash
python diagnose_system.py
```

### Soluções

#### 1. API não está rodando

**Verificar**:
```bash
# Linux/Mac
ps aux | grep "uvicorn"

# Windows
tasklist | findstr "python"
```

**Solução**:
```bash
# Inicie a API
python start_api.py

# OU
python -m app.main

# OU usando start_api.py
python start_api.py
```

#### 2. API falhou no startup

**Verificar logs**:
Quando você executa `python -m app.main`, deve ver:
```
✅ Redis conectado
✅ Modelo carregado
✅ API iniciada
```

Se não ver isso, há um problema no startup.

**Soluções comuns**:

**a) Redis não está rodando**:
```bash
# Inicie o Redis
docker-compose up -d redis

# Verifique status
docker-compose ps

# Ver logs
docker-compose logs redis
```

**b) Modelo não foi treinado**:
```bash
# Treine o modelo
python training/train_model.py
```

**c) Dependências não instaladas**:
```bash
pip install -r requirements.txt
```

#### 3. Porta 8000 já está em uso

**Verificar**:
```bash
# Linux/Mac
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

**Solução A - Matar processo**:
```bash
# Linux/Mac
kill -9 $(lsof -ti:8000)

# Windows (use o PID do comando anterior)
taskkill /PID <PID> /F
```

**Solução B - Usar outra porta**:
```bash
# Edite start_api.py e mude port=8000 para port=8080
# Depois acesse http://localhost:8080/docs
```

---

## 🐛 Problema: Erro ao importar módulos

### Sintomas
```
ModuleNotFoundError: No module named 'app'
ImportError: cannot import name 'xxx'
```

### Soluções

#### 1. Execute do diretório correto

```bash
# Deve estar no diretório raiz do projeto
cd fraud_detection_system
pwd  # Deve mostrar .../fraud_detection_system

# Então execute
python -m app.main
```

#### 2. Verifique o PYTHONPATH

```bash
# Linux/Mac
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Windows
set PYTHONPATH=%PYTHONPATH%;%cd%
```

#### 3. Reinstale dependências

```bash
pip install -r requirements.txt --force-reinstall
```

---

## 🔴 Problema: Redis Connection Error

### Sintomas
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

### Diagnóstico

```bash
# Verificar se Docker está rodando
docker ps

# Verificar logs do Redis
docker-compose logs redis
```

### Soluções

#### 1. Redis não está rodando

```bash
# Inicie o Redis
docker-compose up -d redis

# Aguarde alguns segundos
sleep 5

# Teste conexão
docker exec -it fraud-detection-redis redis-cli ping
# Deve retornar: PONG
```

#### 2. Porta 6379 já está em uso

```bash
# Ver o que está usando a porta
lsof -i :6379

# Parar o processo
docker-compose down

# Reiniciar
docker-compose up -d redis
```

#### 3. Problema de rede Docker

```bash
# Recriar rede
docker-compose down
docker network prune
docker-compose up -d redis
```

---

## 📦 Problema: Modelo não carregado

### Sintomas
```
⚠️ Modelo não encontrado. Execute o treinamento primeiro!
```

ou ao fazer predict:
```
HTTPException: Modelo não está carregado
```

### Solução

```bash
# 1. Verifique se o modelo existe
ls -lh models/

# 2. Se não existir, treine
python training/train_model.py

# 3. Verifique novamente
ls -lh models/
# Deve mostrar: fraud_model.pkl e scaler.pkl

# 4. Reinicie a API
python -m app.main
```

---

## ⚠️ Problema: API inicia mas /docs não carrega

### Sintomas
- API parece estar rodando
- Mas http://localhost:8000/docs não carrega

### Soluções

#### 1. Verifique se a API realmente subiu

```bash
# Teste o endpoint raiz
curl http://localhost:8000/

# Deve retornar JSON com informações da API
```

#### 2. Tente outro endpoint

```bash
# Teste /health
curl http://localhost:8000/health

# Se funcionar, o problema é só com /docs
```

#### 3. Limpe o cache do navegador

- Chrome/Edge: Ctrl + Shift + Delete
- Firefox: Ctrl + Shift + Del
- Safari: Cmd + Option + E

#### 4. Tente outro navegador

- Chrome
- Firefox
- Edge

#### 5. Use o IP direto

```
http://127.0.0.1:8000/docs
```

---

## 🔥 Problema: Erros durante predição

### Sintomas
```
500 Internal Server Error
Erro ao processar predição
```

### Diagnóstico

Veja os logs da API para detalhes do erro.

### Soluções comuns

#### 1. Dados inválidos

**Erro**: `ValidationError`

**Solução**: Verifique o formato do JSON:
```json
{
  "transaction_id": "tx_001",
  "user_id": "user_123",
  "amount": 100.00,  // Deve ser número positivo
  "merchant": "Loja",
  "category": "electronics",  // Deve ser uma categoria válida
  "location": "São Paulo, SP",
  "device": "device_001"
}
```

Categorias válidas:
- electronics
- fashion
- food
- travel
- services
- entertainment
- health
- other

#### 2. Redis desconectou

**Solução**:
```bash
docker-compose restart redis
```

Então reinicie a API.

---

## 💻 Comandos de Diagnóstico Úteis

### Verificar tudo de uma vez

```bash
python diagnose_system.py
```

### Verificar processos

```bash
# Ver processos Python rodando
ps aux | grep python

# Ver processos usando porta 8000
lsof -i :8000
```

### Verificar Docker

```bash
# Status dos containers
docker-compose ps

# Logs do Redis
docker-compose logs -f redis

# Reiniciar tudo
docker-compose down && docker-compose up -d redis
```

### Verificar API manualmente

```bash
# Health check
curl http://localhost:8000/health

# Stats
curl http://localhost:8000/stats

# Root endpoint
curl http://localhost:8000/
```

### Testar predição via curl

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test_001",
    "user_id": "user_999",
    "amount": 100.00,
    "merchant": "Test Store",
    "category": "food",
    "location": "São Paulo, SP",
    "device": "device_test"
  }'
```

---

## 🆘 Checklist de Resolução de Problemas

Use este checklist quando algo não funcionar:

- [ ] 1. Executei o diagnóstico? `python diagnose_system.py`
- [ ] 2. O Redis está rodando? `docker-compose ps`
- [ ] 3. As dependências estão instaladas? `pip list`
- [ ] 4. O modelo foi treinado? `ls models/`
- [ ] 5. Estou no diretório correto? `pwd`
- [ ] 6. A porta 8000 está livre? `lsof -i :8000`
- [ ] 7. Testei o curl? `curl http://localhost:8000/`
- [ ] 8. Verifiquei os logs da API?
- [ ] 9. Tentei reiniciar tudo? `docker-compose restart redis`
- [ ] 10. Li a mensagem de erro completa?

---

## 🔄 Reset Completo do Sistema

Se nada funcionar, faça um reset completo:

```bash
# 1. Para tudo
docker-compose down
pkill -f uvicorn
pkill -f python

# 2. Limpa o ambiente
rm -rf venv/
rm -rf models/*
rm -rf data/*

# 3. Recria tudo
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU: venv\Scripts\activate  # Windows

pip install -r requirements.txt
docker-compose up -d redis
python training/train_model.py

# 4. Inicia API
python start_api.py
```

---

## 📞 Ainda com Problemas?

Se nada disto resolver:

1. **Execute o diagnóstico e salve a saída**:
   ```bash
   python diagnose_system.py > diagnostico.txt
   ```

2. **Capture os logs da API**:
   ```bash
   python -m app.main 2>&1 | tee api_logs.txt
   ```

3. **Verifique os logs do Redis**:
   ```bash
   docker-compose logs redis > redis_logs.txt
   ```

4. **Busque ajuda** com esses arquivos

---

## 💡 Dicas de Prevenção

### Sempre faça antes de iniciar

```bash
# Checklist rápido
python diagnose_system.py && python start_api.py
```

### Mantenha tudo atualizado

```bash
# Atualizar dependências
pip install -r requirements.txt --upgrade

# Atualizar Docker images
docker-compose pull
```

### Use um ambiente virtual

```bash
# Sempre ative o venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

---

**Desenvolvido por Natália Barros**
