#!/bin/bash

# ===================================================================
# Quick Start - Diagnóstico e Inicialização Rápida
# ===================================================================
# Este script verifica tudo e inicia a API automaticamente
#
# Uso:
#   chmod +x quick_start.sh
#   ./quick_start.sh
#
# Autor: Natália Barros
# ===================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funções
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}======================================"
    echo -e "$1"
    echo -e "======================================${NC}"
    echo ""
}

# Header
clear
cat << "EOF"
╔════════════════════════════════════════════════════╗
║                                                    ║
║   🚀 QUICK START - Sistema de Fraudes 🚀          ║
║                                                    ║
║   Diagnóstico e Inicialização Automática          ║
║                                                    ║
╚════════════════════════════════════════════════════╝

EOF

# 1. Verificar Python
print_header "1. Verificando Python"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python encontrado: $PYTHON_VERSION"
else
    print_error "Python 3 não encontrado!"
    exit 1
fi

# 2. Verificar dependências
print_header "2. Verificando Dependências"
if python3 -c "import fastapi" 2>/dev/null; then
    print_success "FastAPI instalado"
else
    print_error "FastAPI não instalado"
    print_info "Instalando dependências..."
    pip install -r requirements.txt
fi

# 3. Verificar Docker
print_header "3. Verificando Docker"
if command -v docker &> /dev/null; then
    print_success "Docker encontrado"
else
    print_error "Docker não encontrado!"
    print_info "Instale Docker e tente novamente"
    exit 1
fi

# 4. Verificar/Iniciar Redis
print_header "4. Verificando Redis"
if docker ps | grep -q "fraud-detection-redis"; then
    print_success "Redis já está rodando"
else
    print_info "Iniciando Redis..."
    docker-compose up -d redis
    sleep 3

    if docker ps | grep -q "fraud-detection-redis"; then
        print_success "Redis iniciado com sucesso"
    else
        print_error "Falha ao iniciar Redis"
        exit 1
    fi
fi

# 5. Verificar modelo
print_header "5. Verificando Modelo ML"
if [ -f "models/fraud_model.pkl" ]; then
    print_success "Modelo encontrado"
else
    print_error "Modelo não encontrado"
    print_info "Treinando modelo... (isso pode levar 1-2 minutos)"
    python3 training/train_model.py

    if [ -f "models/fraud_model.pkl" ]; then
        print_success "Modelo treinado com sucesso!"
    else
        print_error "Falha no treinamento"
        exit 1
    fi
fi

# 6. Verificar porta 8000
print_header "6. Verificando Porta 8000"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    print_error "Porta 8000 já está em uso"
    print_info "Matando processo..."
    kill -9 $(lsof -t -i:8000) 2>/dev/null || true
    sleep 2
fi
print_success "Porta 8000 está livre"

# 7. Tudo pronto!
print_header "✅ TUDO PRONTO!"

echo -e "${GREEN}"
cat << "EOF"
╔════════════════════════════════════════════════════╗
║                                                    ║
║   🎉 SISTEMA PRONTO PARA INICIAR! 🎉              ║
║                                                    ║
╚════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
print_info "Iniciando API em 3 segundos..."
echo ""
sleep 3

# 8. Iniciar API
print_header "🚀 INICIANDO API"

echo -e "${BLUE}"
echo "📡 Servidor: http://0.0.0.0:8000"
echo "📚 Documentação: http://localhost:8000/docs"
echo "📖 Redoc: http://localhost:8000/redoc"
echo ""
echo "💡 Pressione CTRL+C para parar"
echo -e "${NC}"
echo ""

# Executa API
python3 -m app.main
