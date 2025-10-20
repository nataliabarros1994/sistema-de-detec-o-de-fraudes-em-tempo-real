#!/usr/bin/env python3
"""
Script de Diagnóstico do Sistema
=================================
Verifica todos os componentes necessários antes de iniciar a API

Uso:
    python diagnose_system.py

Autor: Natália Barros
"""

import sys
import os
from pathlib import Path

# Cores para output
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

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"ℹ️  {text}")

# 1. Verificar Python
def check_python():
    print_header("1. VERIFICANDO PYTHON")

    version = sys.version_info
    print_info(f"Versão do Python: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 10:
        print_success("Versão do Python compatível (>= 3.10)")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} incompatível. Necessário Python 3.10+")
        return False

# 2. Verificar dependências Python
def check_dependencies():
    print_header("2. VERIFICANDO DEPENDÊNCIAS PYTHON")

    required_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'),
        ('sklearn', 'Scikit-learn'),
        ('redis', 'Redis'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('prometheus_client', 'Prometheus Client')
    ]

    all_installed = True

    for package, name in required_packages:
        try:
            __import__(package)
            print_success(f"{name} instalado")
        except ImportError:
            print_error(f"{name} NÃO instalado")
            all_installed = False

    if not all_installed:
        print_warning("\nInstale as dependências com:")
        print("    pip install -r requirements.txt\n")
        return False

    return True

# 3. Verificar Redis
def check_redis():
    print_header("3. VERIFICANDO REDIS")

    try:
        import redis

        # Tenta conectar
        client = redis.Redis(host='localhost', port=6379, socket_connect_timeout=5)
        client.ping()

        print_success("Redis está rodando e acessível")
        print_info(f"   Host: localhost:6379")
        return True

    except redis.ConnectionError:
        print_error("Redis NÃO está rodando ou não acessível")
        print_warning("\nInicie o Redis com:")
        print("    docker-compose up -d redis")
        print("\nOu verifique se já está rodando:")
        print("    docker-compose ps\n")
        return False

    except ImportError:
        print_error("Biblioteca redis não instalada")
        return False

# 4. Verificar estrutura de diretórios
def check_directories():
    print_header("4. VERIFICANDO ESTRUTURA DE DIRETÓRIOS")

    required_dirs = [
        'app',
        'training',
        'models',
        'data'
    ]

    all_exist = True

    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print_success(f"Diretório '{dir_name}' existe")
        else:
            if dir_name in ['models', 'data']:
                print_warning(f"Diretório '{dir_name}' não existe (será criado)")
                os.makedirs(dir_name, exist_ok=True)
            else:
                print_error(f"Diretório '{dir_name}' NÃO existe")
                all_exist = False

    return all_exist

# 5. Verificar modelo treinado
def check_model():
    print_header("5. VERIFICANDO MODELO TREINADO")

    model_path = Path('models/fraud_model.pkl')
    scaler_path = Path('models/scaler.pkl')

    if model_path.exists() and scaler_path.exists():
        print_success("Modelo treinado encontrado")
        print_info(f"   Modelo: {model_path}")
        print_info(f"   Scaler: {scaler_path}")

        # Verifica tamanho
        model_size = model_path.stat().st_size / 1024  # KB
        print_info(f"   Tamanho: {model_size:.1f} KB")

        return True
    else:
        print_error("Modelo NÃO encontrado")
        print_warning("\nTreine o modelo com:")
        print("    python training/train_model.py\n")
        return False

# 6. Verificar porta 8000
def check_port():
    print_header("6. VERIFICANDO PORTA 8000")

    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()

    if result == 0:
        print_warning("Porta 8000 JÁ está em uso")
        print_info("A API pode já estar rodando, ou outro serviço está usando a porta")
        print_info("\nPara liberar a porta:")
        print("    • No Linux/Mac: lsof -ti:8000 | xargs kill -9")
        print("    • No Windows: netstat -ano | findstr :8000\n")
        return False
    else:
        print_success("Porta 8000 está livre")
        return True

# 7. Testar imports dos módulos
def check_app_imports():
    print_header("7. VERIFICANDO IMPORTS DA APLICAÇÃO")

    modules = [
        'app.models',
        'app.database',
        'app.features',
        'app.ml_model',
        'app.monitoring'
    ]

    all_ok = True

    for module in modules:
        try:
            __import__(module)
            print_success(f"Import OK: {module}")
        except Exception as e:
            print_error(f"Erro ao importar {module}: {str(e)}")
            all_ok = False

    return all_ok

# 8. Verificar variáveis de ambiente
def check_environment():
    print_header("8. VERIFICANDO VARIÁVEIS DE AMBIENTE")

    env_vars = {
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
        'LOG_LEVEL': 'info'
    }

    for var, default in env_vars.items():
        value = os.environ.get(var, default)
        print_info(f"{var} = {value}")

    print_success("Variáveis de ambiente configuradas")
    return True

# Resumo e recomendações
def print_summary(results):
    print_header("📊 RESUMO DO DIAGNÓSTICO")

    checks = [
        ("Python", results['python']),
        ("Dependências", results['dependencies']),
        ("Redis", results['redis']),
        ("Diretórios", results['directories']),
        ("Modelo Treinado", results['model']),
        ("Porta 8000", results['port']),
        ("Imports", results['imports']),
        ("Ambiente", results['environment'])
    ]

    passed = sum(1 for _, status in checks if status)
    total = len(checks)

    print(f"\nVerificações: {passed}/{total} passaram\n")

    for check_name, status in checks:
        if status:
            print_success(f"{check_name}")
        else:
            print_error(f"{check_name}")

    print("\n" + "="*60 + "\n")

    if passed == total:
        print(f"{Colors.GREEN}✅ SISTEMA PRONTO PARA INICIAR!{Colors.END}\n")
        print("Inicie a API com:")
        print(f"    {Colors.BLUE}python -m app.main{Colors.END}\n")
        return True
    else:
        print(f"{Colors.RED}❌ CORRIJA OS PROBLEMAS ACIMA ANTES DE INICIAR{Colors.END}\n")

        # Recomendações específicas
        if not results['dependencies']:
            print("1️⃣  Instale as dependências:")
            print("    pip install -r requirements.txt\n")

        if not results['redis']:
            print("2️⃣  Inicie o Redis:")
            print("    docker-compose up -d redis\n")

        if not results['model']:
            print("3️⃣  Treine o modelo:")
            print("    python training/train_model.py\n")

        return False

# Função principal
def main():
    print(f"""
{Colors.BLUE}╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🔍 DIAGNÓSTICO DO SISTEMA DE DETECÇÃO DE FRAUDES 🔍     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝{Colors.END}
    """)

    results = {
        'python': check_python(),
        'dependencies': check_dependencies(),
        'redis': check_redis(),
        'directories': check_directories(),
        'model': check_model(),
        'port': check_port(),
        'imports': check_app_imports(),
        'environment': check_environment()
    }

    system_ready = print_summary(results)

    return 0 if system_ready else 1

if __name__ == "__main__":
    sys.exit(main())
