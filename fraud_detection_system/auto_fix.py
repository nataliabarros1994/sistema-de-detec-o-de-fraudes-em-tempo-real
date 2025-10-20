#!/usr/bin/env python3
"""
Script de Correção Automática
==============================
Este script corrige automaticamente os problemas mais comuns do sistema

Uso:
    python auto_fix.py

Autor: Natália Barros
"""

import sys
import os
import subprocess
from pathlib import Path

# Cores
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.END}")

def run_command(cmd, description):
    """Executa comando e retorna True se bem-sucedido"""
    print_info(f"{description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print_success(f"{description} - OK")
            return True
        else:
            print_error(f"{description} - FALHOU")
            if result.stderr:
                print(f"   Erro: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"{description} - TIMEOUT")
        return False
    except Exception as e:
        print_error(f"{description} - ERRO: {e}")
        return False

def check_and_create_directories():
    """Cria diretórios necessários"""
    print_header("1. CRIANDO DIRETÓRIOS NECESSÁRIOS")

    dirs = ['models', 'data', 'tests']
    for dir_name in dirs:
        path = Path(dir_name)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Diretório '{dir_name}' criado")
        else:
            print_info(f"Diretório '{dir_name}' já existe")

    return True

def install_dependencies():
    """Instala dependências Python"""
    print_header("2. VERIFICANDO/INSTALANDO DEPENDÊNCIAS")

    # Verifica se requirements.txt existe
    if not Path('requirements.txt').exists():
        print_error("requirements.txt não encontrado!")
        return False

    # Instala dependências
    return run_command(
        "pip install -r requirements.txt --quiet",
        "Instalando dependências Python"
    )

def start_redis():
    """Inicia Redis se não estiver rodando"""
    print_header("3. VERIFICANDO REDIS")

    # Verifica se está rodando
    result = subprocess.run(
        "docker ps | grep fraud-detection-redis",
        shell=True,
        capture_output=True
    )

    if result.returncode == 0:
        print_success("Redis já está rodando")
        return True

    # Inicia Redis
    print_info("Iniciando Redis...")
    return run_command(
        "docker-compose up -d redis",
        "Iniciando container Redis"
    )

def check_model_or_train():
    """Verifica se modelo existe, senão treina"""
    print_header("4. VERIFICANDO/TREINANDO MODELO")

    model_path = Path('models/fraud_model.pkl')
    scaler_path = Path('models/scaler.pkl')

    if model_path.exists() and scaler_path.exists():
        print_success("Modelo já existe")
        return True

    print_info("Modelo não encontrado. Treinando...")
    print_info("Isso pode levar 1-2 minutos...")

    return run_command(
        "python training/train_model.py",
        "Treinando modelo de ML"
    )

def verify_system():
    """Verifica se tudo está funcionando"""
    print_header("5. VERIFICAÇÃO FINAL")

    checks = [
        ("Diretório models/", Path('models').exists()),
        ("Diretório data/", Path('data').exists()),
        ("Modelo treinado", Path('models/fraud_model.pkl').exists()),
        ("Scaler salvo", Path('models/scaler.pkl').exists())
    ]

    all_ok = True
    for check_name, result in checks:
        if result:
            print_success(check_name)
        else:
            print_error(check_name)
            all_ok = False

    return all_ok

def main():
    """Função principal"""
    print(f"""
{Colors.BLUE}╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🔧 AUTO-FIX - Sistema de Detecção de Fraudes 🔧         ║
║                                                            ║
║        Correção Automática de Problemas Comuns            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝{Colors.END}
    """)

    print_info("Este script vai corrigir automaticamente os problemas comuns\n")

    try:
        # 1. Criar diretórios
        if not check_and_create_directories():
            print_error("Falha ao criar diretórios")
            return False

        # 2. Instalar dependências
        if not install_dependencies():
            print_error("Falha ao instalar dependências")
            print_info("Execute manualmente: pip install -r requirements.txt")
            return False

        # 3. Iniciar Redis
        if not start_redis():
            print_error("Falha ao iniciar Redis")
            print_info("Verifique se Docker está instalado e rodando")
            return False

        # 4. Verificar/treinar modelo
        if not check_model_or_train():
            print_error("Falha no treinamento do modelo")
            return False

        # 5. Verificação final
        if not verify_system():
            print_error("Sistema ainda tem problemas")
            return False

        # Sucesso!
        print_header("✅ CORREÇÕES CONCLUÍDAS COM SUCESSO!")

        print(f"""
{Colors.GREEN}🎉 Todos os problemas foram corrigidos!{Colors.END}

{Colors.BLUE}Próximos passos:{Colors.END}

1️⃣  Inicie a API:
   {Colors.YELLOW}python start_api.py{Colors.END}

2️⃣  Acesse a documentação:
   {Colors.YELLOW}http://localhost:8000/docs{Colors.END}

3️⃣  Teste a API!

{Colors.GREEN}Sistema pronto para uso! 🚀{Colors.END}
        """)

        return True

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Processo cancelado pelo usuário{Colors.END}")
        return False

    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
