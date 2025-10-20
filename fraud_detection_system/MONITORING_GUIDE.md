# 📡 Guia de Monitoramento e Auto-Restart da API

**Data**: 2025-10-15
**Status**: ✅ **SISTEMA DE MONITORAMENTO COMPLETO**

---

## 🎯 Visão Geral

Este documento explica os **3 sistemas de monitoramento e auto-restart** criados para garantir que a API permaneça online e acessível.

---

## 🛠️ Ferramentas Disponíveis

### **1. check_api_status.py** - Verificador de Status

**Propósito**: Verifica se a API está acessível e funcionando

**Uso**:
```bash
python check_api_status.py
```

**O que verifica**:
- ✅ Resolução de DNS (localhost → 127.0.0.1)
- ✅ Porta 8000 está aberta (localhost, 127.0.0.1, 0.0.0.0)
- ✅ API está respondendo nos endpoints:
  - `/` (Root)
  - `/health` (Health check)
  - `/docs` (Documentação)
- ✅ Processos Python/uvicorn rodando

**Saída de exemplo**:
```
╔════════════════════════════════════════════════════════════╗
║   🔍 VERIFICAÇÃO DE STATUS DA API 🔍                       ║
╚════════════════════════════════════════════════════════════╝

1. VERIFICANDO RESOLUÇÃO DE NOME
✅ Localhost resolve para: 127.0.0.1

2. VERIFICANDO PORTA 8000
✅ Porta 8000 está ABERTA em localhost

3. VERIFICANDO RESPOSTA DA API
ℹ️  Testando: http://localhost:8000
✅ Root endpoint (/): Status 200
✅ Health check (/health): Status 200
✅ Documentation (/docs): Status 200

4. VERIFICANDO PROCESSOS
✅ Encontrados 1 processo(s) da API rodando

📊 RESUMO
✅ API ESTÁ ONLINE E ACESSÍVEL!
```

**Quando usar**:
- Para diagnosticar problemas de conexão
- Antes de iniciar a API
- Para verificar se a API já está rodando

---

### **2. api_monitor.py** - Monitor com Auto-Restart (Python)

**Propósito**: Monitora continuamente a API e reinicia automaticamente se ela cair

**Uso**:
```bash
python api_monitor.py
```

**Características**:
- 🔄 Verifica saúde da API a cada **10 segundos**
- 🚨 Detecta falhas consecutivas
- 🔧 Reinicia automaticamente após **2 falhas**
- 📊 Rastreia uptime e número de restarts
- 🛑 Parada graciosa com Ctrl+C

**Configurações** (pode ser alterado no código):
```python
monitor = APIMonitor(
    check_interval=10,  # Verifica a cada 10 segundos
    restart_delay=5     # Aguarda 5 segundos antes de reiniciar
)
```

**Saída de exemplo**:
```
╔════════════════════════════════════════════════════════════╗
║   📡 MONITOR DA API - AUTO RESTART ATIVADO 📡             ║
╚════════════════════════════════════════════════════════════╝

Configurações:
   • Intervalo de verificação: 10s
   • Delay para restart: 5s

[2025-10-15 14:30:15] 🚀 Iniciando API...
[2025-10-15 14:30:23] ✅ API iniciada com sucesso!
[2025-10-15 14:30:23] ✅ Monitor ativo - Verificando a cada 10s

[2025-10-15 14:30:33] ✅ API OK | Uptime: 0h 0m 10s | Restarts: 0
[2025-10-15 14:31:15] ❌ API parou de responder!
[2025-10-15 14:31:15] ⚠️  Falha #1 detectada
[2025-10-15 14:31:25] ⚠️  Falha #2 detectada
[2025-10-15 14:31:25] 🔄 Muitas falhas detectadas, reiniciando...
[2025-10-15 14:31:25] 🔄 Reiniciando API...
```

**Quando usar**:
- Em ambiente de desenvolvimento para testes
- Quando você quer monitoramento visual no terminal
- Para debugging com logs detalhados

---

### **3. robust_start.sh** - Monitor com Auto-Restart (Bash)

**Propósito**: Script bash simples que reinicia a API automaticamente se ela parar

**Uso**:
```bash
# Dar permissão de execução (já feito)
chmod +x robust_start.sh

# Executar
./robust_start.sh
```

**Características**:
- ♾️ Loop infinito de monitoramento
- 🔄 Reinicia automaticamente se a API cair
- 📊 Rastreia uptime e número de restarts
- 🚨 Detecta restart loops e aumenta delay
- 🛑 Parada graciosa com Ctrl+C
- 🎨 Logs coloridos com timestamps

**Saída de exemplo**:
```
╔════════════════════════════════════════════════════════════╗
║   🚀 INICIALIZAÇÃO ROBUSTA - API DE DETECÇÃO DE FRAUDES   ║
║        Auto-Restart Ativado - Monitoramento Contínuo       ║
╚════════════════════════════════════════════════════════════╝

[2025-10-15 14:30:15] ✅ Monitor ativo
[2025-10-15 14:30:15] 💡 Pressione Ctrl+C para parar o monitor

[2025-10-15 14:30:15] 🚀 Iniciando API...
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000

# Se a API cair:
[2025-10-15 15:45:30] ❌ API parou (código de saída: 1)
[2025-10-15 15:45:30] ⏳ Aguardando 5 segundos antes de reiniciar...
[2025-10-15 15:45:35] 🔄 Restart #1 - Uptime total: 1h 15m 20s
[2025-10-15 15:45:35] 🚀 Iniciando API...
```

**Proteção contra restart loops**:
- Se houver **5+ restarts em 1 minuto**, o delay aumenta para **30 segundos**
- Previne que a API fique em loop infinito de falhas

**Quando usar**:
- Em ambiente de produção/demonstração
- Quando você quer simplicidade
- Para rodar em background (com nohup ou screen)

---

## 🆚 Comparação das Ferramentas

| Ferramenta | Tipo | Auto-Restart | Monitoramento Contínuo | Melhor Para |
|------------|------|--------------|------------------------|-------------|
| **check_api_status.py** | Verificador único | ❌ Não | ❌ Não | Diagnóstico rápido |
| **api_monitor.py** | Monitor Python | ✅ Sim | ✅ Sim (10s) | Desenvolvimento/Debug |
| **robust_start.sh** | Monitor Bash | ✅ Sim | ✅ Sim (contínuo) | Produção/Simplicidade |

---

## 📋 Casos de Uso

### **Cenário 1: API não inicia**

1. Execute o diagnóstico:
   ```bash
   python check_api_status.py
   ```

2. Se mostrar problemas, execute o auto-fix:
   ```bash
   python auto_fix.py
   ```

3. Tente iniciar novamente:
   ```bash
   python start_api.py
   ```

---

### **Cenário 2: API cai frequentemente (Desenvolvimento)**

Use o monitor Python com logs detalhados:
```bash
python api_monitor.py
```

Vantagens:
- Ver exatamente quando e por que a API cai
- Logs com timestamps detalhados
- Estatísticas de uptime e restarts

---

### **Cenário 3: Demonstração em entrevista**

Use o script bash robusto:
```bash
./robust_start.sh
```

Vantagens:
- Garantia de que a API não vai cair durante a demo
- Restart automático se algo der errado
- Aparência profissional

---

### **Cenário 4: Rodar em background (servidor)**

Use o script bash com `nohup`:
```bash
nohup ./robust_start.sh > api_monitor.log 2>&1 &
```

Para verificar se está rodando:
```bash
ps aux | grep robust_start.sh
```

Para parar:
```bash
pkill -f robust_start.sh
```

---

## 🔧 Configurações Avançadas

### **Alterar intervalo de verificação (api_monitor.py)**

Edite o arquivo `api_monitor.py` linha 242-245:
```python
monitor = APIMonitor(
    check_interval=5,   # Verifica a cada 5 segundos (antes: 10)
    restart_delay=3     # Aguarda 3 segundos antes de reiniciar (antes: 5)
)
```

---

### **Alterar delay de restart (robust_start.sh)**

Edite o arquivo `robust_start.sh` linha 71:
```bash
DELAY=10  # Aguarda 10 segundos antes de reiniciar (antes: 5)
```

---

## 🚨 Resolução de Problemas

### **Problema: Monitor não detecta API rodando**

**Solução**: Verifique se a porta 8000 está correta

1. Verifique qual porta a API usa:
   ```bash
   grep "port=" start_api.py
   ```

2. Se for diferente de 8000, edite:
   - `api_monitor.py` linha 63-65
   - `check_api_status.py` linha 156-159

---

### **Problema: API reinicia em loop infinito**

**Causa**: Erro crítico que impede a API de iniciar

**Solução**:
1. Pare o monitor (Ctrl+C)
2. Execute o diagnóstico:
   ```bash
   python diagnose_system.py
   ```
3. Execute o auto-fix:
   ```bash
   python auto_fix.py
   ```
4. Verifique os logs de erro do último start

---

### **Problema: Permissão negada ao executar robust_start.sh**

**Erro**:
```
bash: ./robust_start.sh: Permission denied
```

**Solução**:
```bash
chmod +x robust_start.sh
./robust_start.sh
```

---

## 📊 Estatísticas e Logs

### **Ver estatísticas do monitor Python**

Durante a execução do `api_monitor.py`, você verá periodicamente:
```
✅ API OK | Uptime: 2h 15m 30s | Restarts: 3
```

Ao parar (Ctrl+C):
```
📊 ESTATÍSTICAS FINAIS DO MONITOR
Tempo de execução: 2h 15m 30s
Total de restarts: 3
```

---

### **Ver estatísticas do monitor Bash**

Durante a execução do `robust_start.sh`:
```
🔄 Restart #3 - Uptime total: 2h 15m 30s
```

Ao parar (Ctrl+C):
```
📊 Estatísticas finais:
   • Uptime total: 2h 15m 30s
   • Total de restarts: 3
```

---

## 🎯 Recomendações

### **Para Desenvolvimento Local**
✅ Use: `python api_monitor.py`
- Logs detalhados
- Fácil de debugar
- Ver exatamente o que está acontecendo

### **Para Demonstrações**
✅ Use: `./robust_start.sh`
- Simples e robusto
- Aparência profissional
- Garantia de uptime

### **Para Diagnóstico Rápido**
✅ Use: `python check_api_status.py`
- Verificação instantânea
- Identifica problemas rapidamente
- Não inicia nada

---

## 🔄 Workflow Completo Recomendado

### **Passo 1: Verificação Inicial**
```bash
python check_api_status.py
```
Se mostrar problemas → Execute `python auto_fix.py`

### **Passo 2: Iniciar com Monitoramento**
```bash
# Para desenvolvimento:
python api_monitor.py

# OU para demonstração:
./robust_start.sh
```

### **Passo 3: Testar a API**
Em outro terminal:
```bash
curl http://localhost:8000/health
```

Ou acesse no navegador:
- http://localhost:8000/docs

---

## 📞 Referência Rápida de Comandos

```bash
# Verificar status
python check_api_status.py

# Corrigir problemas automaticamente
python auto_fix.py

# Iniciar API (simples)
python start_api.py

# Iniciar com monitor Python
python api_monitor.py

# Iniciar com monitor Bash
./robust_start.sh

# Diagnosticar sistema completo
python diagnose_system.py

# Rodar em background
nohup ./robust_start.sh > api_monitor.log 2>&1 &

# Ver processos rodando
ps aux | grep -E "uvicorn|python.*api"

# Parar tudo
pkill -f "uvicorn|robust_start"
```

---

## ✅ Conclusão

Agora você tem **3 ferramentas poderosas** para garantir que sua API de detecção de fraudes permaneça online:

1. ✅ **check_api_status.py** - Para diagnóstico rápido
2. ✅ **api_monitor.py** - Para monitoramento com logs detalhados
3. ✅ **robust_start.sh** - Para garantir uptime máximo

**Escolha a ferramenta adequada para cada situação e mantenha sua API sempre acessível!** 🚀

---

**Desenvolvido com ❤️ para Natália Barros**
**Data**: 2025-10-15
