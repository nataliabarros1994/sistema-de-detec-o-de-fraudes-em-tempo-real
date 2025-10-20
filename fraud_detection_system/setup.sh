#!/bin/bash

# ===================================================================
# Script de Setup Automático - Sistema de Detecção de Fraudes
# ===================================================================
# Este script automatiza todo o processo de instalação e setup
# do sistema de detecção de fraudes.
#
# Uso:
#   chmod +x setup.sh
#   ./setup.sh
#
# Autor: Natália Barros
# Data: 2025
# ===================================================================

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de utilidade
print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

# Verificar requisitos
check_requirements() {
    print_header "VERIFICANDO REQUISITOS"

    # Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python encontrado: $PYTHON_VERSION"
    else
        print_error "Python 3 não encontrado!"
        print_info "Instale Python 3.10+ e tente novamente"
        exit 1
    fi

    # Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker encontrado: $DOCKER_VERSION"
    else
        print_error "Docker não encontrado!"
        print_info "Instale Docker Desktop e tente novamente"
        exit 1
    fi

    # Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f4 | cut -d',' -f1)
        print_success "Docker Compose encontrado: $COMPOSE_VERSION"
    else
        print_error "Docker Compose não encontrado!"
        print_info "Instale Docker Compose e tente novamente"
        exit 1
    fi
}

# Criar ambiente virtual
create_venv() {
    print_header "CONFIGURANDO AMBIENTE VIRTUAL"

    if [ -d "venv" ]; then
        print_info "Ambiente virtual já existe"
        read -p "Deseja recriar? (s/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            print_step "Removendo ambiente virtual antigo..."
            rm -rf venv
        else
            print_info "Mantendo ambiente virtual existente"
            return
        fi
    fi

    print_step "Criando novo ambiente virtual..."
    python3 -m venv venv

    print_success "Ambiente virtual criado!"
}

# Instalar dependências
install_dependencies() {
    print_header "INSTALANDO DEPENDÊNCIAS"

    print_step "Ativando ambiente virtual..."

    # Detecta o sistema operacional
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi

    print_step "Atualizando pip..."
    pip install --upgrade pip --quiet

    print_step "Instalando dependências do projeto..."
    pip install -r requirements.txt --quiet

    print_success "Dependências instaladas!"
}

# Iniciar Redis
start_redis() {
    print_header "INICIANDO REDIS"

    print_step "Verificando se Redis já está rodando..."

    if docker ps | grep -q "fraud-detection-redis"; then
        print_info "Redis já está rodando"
    else
        print_step "Iniciando container Redis..."
        docker-compose up -d redis

        print_step "Aguardando Redis inicializar..."
        sleep 5

        if docker ps | grep -q "fraud-detection-redis"; then
            print_success "Redis iniciado com sucesso!"
        else
            print_error "Falha ao iniciar Redis"
            exit 1
        fi
    fi
}

# Treinar modelo
train_model() {
    print_header "TREINANDO MODELO DE MACHINE LEARNING"

    if [ -f "models/fraud_model.pkl" ]; then
        print_info "Modelo já existe"
        read -p "Deseja retreinar? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_info "Mantendo modelo existente"
            return
        fi
    fi

    print_step "Gerando dados sintéticos e treinando modelo..."
    print_info "Isso pode levar 1-2 minutos..."

    python training/train_model.py

    if [ -f "models/fraud_model.pkl" ]; then
        print_success "Modelo treinado e salvo!"
    else
        print_error "Falha no treinamento do modelo"
        exit 1
    fi
}

# Resumo final
print_summary() {
    print_header "INSTALAÇÃO CONCLUÍDA COM SUCESSO!"

    echo -e "${GREEN}🎉 O sistema está pronto para uso!${NC}"
    echo ""
    echo -e "${BLUE}Próximos passos:${NC}"
    echo ""
    echo "1️⃣  Ativar o ambiente virtual:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2️⃣  Iniciar a API:"
    echo "   python -m app.main"
    echo ""
    echo "3️⃣  Acessar a documentação interativa:"
    echo "   http://localhost:8000/docs"
    echo ""
    echo -e "${BLUE}Documentação:${NC}"
    echo "   📖 README.md - Guia completo"
    echo "   ⚡ QUICKSTART.md - Início rápido"
    echo "   💡 EXAMPLES.md - Exemplos práticos"
    echo ""
    echo -e "${BLUE}Comandos úteis:${NC}"
    echo "   • Ver status: docker-compose ps"
    echo "   • Ver logs Redis: docker-compose logs redis"
    echo "   • Parar Redis: docker-compose down"
    echo "   • Avaliar modelo: python training/evaluate_model.py"
    echo ""
    echo -e "${GREEN}Desenvolvido com ❤️ por Natália Barros${NC}"
    echo ""
}

# Função principal
main() {
    clear

    cat << "EOF"
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║   🚀 Sistema de Detecção de Fraudes em Tempo Real 🚀      ║
    ║                                                            ║
    ║             Script de Instalação Automática                ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝

EOF

    print_info "Este script irá configurar todo o ambiente automaticamente"
    echo ""

    read -p "Deseja continuar? (S/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Instalação cancelada"
        exit 0
    fi

    # Executar passos
    check_requirements
    create_venv
    install_dependencies
    start_redis
    train_model
    print_summary
}

# Tratamento de erros
trap 'print_error "Erro durante a instalação. Verifique as mensagens acima."; exit 1' ERR

# Executar
main
