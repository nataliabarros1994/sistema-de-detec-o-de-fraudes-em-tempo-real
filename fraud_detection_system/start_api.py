#!/usr/bin/env python3
"""
Script de Inicialização da API
===============================
Inicia o servidor FastAPI com configurações corretas

Uso:
    python start_api.py

Autor: Natália Barros
"""

import uvicorn
import logging
import sys

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Função principal que inicia o servidor
    """
    try:
        logger.info("=" * 70)
        logger.info("🚀 INICIANDO API DE DETECÇÃO DE FRAUDES")
        logger.info("=" * 70)
        logger.info("")
        logger.info("📡 Servidor será iniciado em: http://0.0.0.0:8000")
        logger.info("📚 Documentação disponível em: http://localhost:8000/docs")
        logger.info("📖 Redoc disponível em: http://localhost:8000/redoc")
        logger.info("")
        logger.info("💡 Pressione CTRL+C para parar o servidor")
        logger.info("=" * 70)
        logger.info("")

        # Inicia o servidor Uvicorn
        uvicorn.run(
            "app.main:app",  # CORRETO: app.main:app
            host="0.0.0.0",   # Aceita conexões de qualquer IP
            port=8000,        # Porta padrão
            reload=True,      # Auto-reload em desenvolvimento
            log_level="info", # Nível de log
            access_log=True   # Log de acesso
        )

    except KeyboardInterrupt:
        logger.info("\n\n👋 Servidor encerrado pelo usuário")
        sys.exit(0)

    except Exception as e:
        logger.error(f"\n❌ Erro ao iniciar servidor: {e}")
        logger.error("\nVerifique se:")
        logger.error("  1. O Redis está rodando (docker-compose up -d redis)")
        logger.error("  2. As dependências estão instaladas (pip install -r requirements.txt)")
        logger.error("  3. O modelo foi treinado (python training/train_model.py)")
        logger.error("\nOu execute o diagnóstico:")
        logger.error("  python diagnose_system.py\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
