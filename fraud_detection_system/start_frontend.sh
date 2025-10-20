#!/bin/bash
# ===================================================================
# Script de Inicialização do Frontend - Sistema de Detecção de Fraudes
# ===================================================================
# Inicia o backend (API) e o frontend (Streamlit) automaticamente
#
# Uso: ./start_frontend.sh
#
# Autor: Natália Barros
# Data: 2025
# ===================================================================

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo "================================================================="
echo -e "${BLUE}🚀 Sistema de Detecção de Fraudes - Inicialização${NC}"
echo "================================================================="
echo ""

# Verifica se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Erro: Execute este script na raiz do projeto${NC}"
    exit 1
fi

# Verifica ambiente virtual
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Ambiente virtual não encontrado!${NC}"
    echo -e "${YELLOW}💡 Execute: python -m venv venv${NC}"
    exit 1
fi

# Ativa ambiente virtual
echo -e "${BLUE}📦 Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Verifica dependências
echo -e "${BLUE}🔍 Verificando dependências...${NC}"
if ! python -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Streamlit não encontrado. Instalando dependências...${NC}"
    pip install -r requirements.txt
fi

# Verifica Redis
echo -e "${BLUE}🐳 Verificando Redis...${NC}"
if ! docker ps | grep -q redis; then
    echo -e "${YELLOW}📡 Iniciando Redis com Docker...${NC}"
    docker-compose up -d redis
    sleep 3
fi

# Verifica se a API já está rodando
echo -e "${BLUE}🔍 Verificando API...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API já está rodando${NC}"
else
    echo -e "${BLUE}🚀 Iniciando API em background...${NC}"
    nohup python start_api.py > logs/api.log 2>&1 &
    API_PID=$!
    echo $API_PID > .api.pid

    # Aguarda API iniciar
    echo -e "${BLUE}⏳ Aguardando API iniciar...${NC}"
    for i in {1..10}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API iniciada com sucesso!${NC}"
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""
fi

# Mostra informações
echo ""
echo "================================================================="
echo -e "${GREEN}✅ Sistema Pronto!${NC}"
echo "================================================================="
echo ""
echo -e "${BLUE}📡 API Backend:${NC}      http://localhost:8000"
echo -e "${BLUE}📚 Documentação:${NC}     http://localhost:8000/docs"
echo -e "${BLUE}🎨 Frontend:${NC}         http://localhost:8501"
echo ""
echo -e "${YELLOW}💡 Pressione CTRL+C para parar${NC}"
echo "================================================================="
echo ""

# Cria trap para cleanup
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Encerrando sistema...${NC}"

    if [ -f .api.pid ]; then
        API_PID=$(cat .api.pid)
        kill $API_PID 2>/dev/null
        rm .api.pid
        echo -e "${GREEN}✅ API encerrada${NC}"
    fi

    exit 0
}

trap cleanup INT TERM

# Inicia Frontend (Streamlit)
echo -e "${BLUE}🎨 Iniciando Dashboard Streamlit...${NC}"
echo ""
streamlit run frontend/app.py

# Cleanup ao encerrar
cleanup
