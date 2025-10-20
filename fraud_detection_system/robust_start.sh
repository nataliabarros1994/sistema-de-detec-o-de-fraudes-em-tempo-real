#!/bin/bash
################################################################################
# Script de Inicialização Robusta da API
################################################################################
# Este script inicia a API e reinicia automaticamente se ela cair
#
# Uso:
#   chmod +x robust_start.sh
#   ./robust_start.sh
#
# Autor: Natália Barros
################################################################################

# Cores
GREEN='\033[92m'
RED='\033[91m'
YELLOW='\033[93m'
BLUE='\033[94m'
END='\033[0m'

# Contador de restarts
RESTART_COUNT=0
START_TIME=$(date +%s)

# Função para calcular uptime
get_uptime() {
    CURRENT_TIME=$(date +%s)
    UPTIME=$((CURRENT_TIME - START_TIME))
    HOURS=$((UPTIME / 3600))
    MINUTES=$(((UPTIME % 3600) / 60))
    SECONDS=$((UPTIME % 60))
    echo "${HOURS}h ${MINUTES}m ${SECONDS}s"
}

# Função para log com timestamp
log_message() {
    local COLOR=$1
    local MESSAGE=$2
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${COLOR}[${TIMESTAMP}] ${MESSAGE}${END}"
}

# Função para cleanup ao sair
cleanup() {
    echo ""
    log_message "$YELLOW" "⚠️  Recebido sinal de parada..."
    log_message "$BLUE" "📊 Estatísticas finais:"
    log_message "$BLUE" "   • Uptime total: $(get_uptime)"
    log_message "$BLUE" "   • Total de restarts: ${RESTART_COUNT}"
    log_message "$GREEN" "✅ Monitor encerrado."
    exit 0
}

# Captura Ctrl+C
trap cleanup SIGINT SIGTERM

# Banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${END}"
echo -e "${BLUE}║                                                            ║${END}"
echo -e "${BLUE}║   🚀 INICIALIZAÇÃO ROBUSTA - API DE DETECÇÃO DE FRAUDES   ║${END}"
echo -e "${BLUE}║                                                            ║${END}"
echo -e "${BLUE}║        Auto-Restart Ativado - Monitoramento Contínuo       ║${END}"
echo -e "${BLUE}║                                                            ║${END}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${END}"
echo ""
log_message "$GREEN" "✅ Monitor ativo - API será reiniciada automaticamente se cair"
log_message "$YELLOW" "💡 Pressione Ctrl+C para parar o monitor"
echo -e "${BLUE}${'='*60}${END}\n"

# Loop infinito de monitoramento
while true; do
    if [ $RESTART_COUNT -gt 0 ]; then
        log_message "$YELLOW" "🔄 Restart #${RESTART_COUNT} - Uptime total: $(get_uptime)"
    fi

    log_message "$BLUE" "🚀 Iniciando API..."

    # Inicia a API
    python start_api.py

    # Se chegou aqui, a API caiu
    EXIT_CODE=$?
    RESTART_COUNT=$((RESTART_COUNT + 1))

    log_message "$RED" "❌ API parou (código de saída: ${EXIT_CODE})"

    # Verifica se foi parada intencionalmente (Ctrl+C)
    if [ $EXIT_CODE -eq 130 ] || [ $EXIT_CODE -eq 143 ]; then
        log_message "$YELLOW" "⚠️  API foi parada intencionalmente"
        cleanup
    fi

    # Aguarda antes de reiniciar
    DELAY=5
    log_message "$YELLOW" "⏳ Aguardando ${DELAY} segundos antes de reiniciar..."
    sleep $DELAY

    # Previne restart loop muito rápido
    # Se tiver mais de 5 restarts em 1 minuto, aumenta o delay
    if [ $RESTART_COUNT -ge 5 ]; then
        UPTIME_SECONDS=$(($(date +%s) - START_TIME))
        if [ $UPTIME_SECONDS -lt 60 ]; then
            log_message "$RED" "⚠️  ALERTA: Muitos restarts rápidos detectados!"
            log_message "$YELLOW" "⏳ Aumentando delay para 30 segundos..."
            sleep 25  # 5 já foram esperados
        fi
    fi

    echo ""
done
