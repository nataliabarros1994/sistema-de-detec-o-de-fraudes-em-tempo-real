#!/usr/bin/env python3
"""
Verificador de Status da API
=============================
Verifica se a API está rodando e acessível

Uso:
    python check_api_status.py

Autor: Natália Barros
"""

import requests
import socket
import sys
import subprocess
from typing import Dict, Tuple

# Cores
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_localhost_resolution() -> bool:
    """Verifica se localhost resolve corretamente"""
    try:
        ip = socket.gethostbyname('localhost')
        if ip == '127.0.0.1':
            print_success(f"Localhost resolve para: {ip}")
            return True
        else:
            print_warning(f"Localhost resolve para: {ip} (esperado: 127.0.0.1)")
            return True
    except Exception as e:
        print_error(f"Erro ao resolver localhost: {e}")
        return False

def check_port_open(host: str, port: int) -> bool:
    """Verifica se uma porta está aberta"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print_success(f"Porta {port} está ABERTA em {host}")
            return True
        else:
            print_error(f"Porta {port} está FECHADA em {host}")
            return False
    except Exception as e:
        print_error(f"Erro ao verificar porta {port}: {e}")
        return False

def check_api_responding(base_url: str) -> Tuple[bool, Dict]:
    """Verifica se a API está respondendo"""
    endpoints_to_test = [
        ('/', 'Root endpoint'),
        ('/health', 'Health check'),
        ('/docs', 'Documentation')
    ]

    results = {}

    for endpoint, description in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success(f"{description} ({endpoint}): Status {response.status_code}")
                results[endpoint] = True
            else:
                print_warning(f"{description} ({endpoint}): Status {response.status_code}")
                results[endpoint] = True  # Respondeu, mesmo que não seja 200
        except requests.exceptions.ConnectionError:
            print_error(f"{description} ({endpoint}): Conexão recusada")
            results[endpoint] = False
        except requests.exceptions.Timeout:
            print_error(f"{description} ({endpoint}): Timeout")
            results[endpoint] = False
        except Exception as e:
            print_error(f"{description} ({endpoint}): {e}")
            results[endpoint] = False

    return any(results.values()), results

def check_python_process() -> bool:
    """Verifica se há processo Python rodando (possível API)"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )

        lines = result.stdout.split('\n')
        api_processes = [
            line for line in lines
            if 'uvicorn' in line.lower() or
               ('python' in line.lower() and 'app.main' in line.lower())
        ]

        if api_processes:
            print_success(f"Encontrados {len(api_processes)} processo(s) da API rodando:")
            for proc in api_processes[:3]:  # Mostra até 3
                print(f"   {proc[:100]}...")
            return True
        else:
            print_error("Nenhum processo da API encontrado")
            return False
    except Exception as e:
        print_warning(f"Não foi possível verificar processos: {e}")
        return False

def main():
    """Função principal"""
    print(f"""
{Colors.BLUE}╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🔍 VERIFICAÇÃO DE STATUS DA API 🔍                       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝{Colors.END}
    """)

    all_ok = True

    # 1. Verificar resolução de localhost
    print(f"\n{Colors.BLUE}{'='*60}")
    print("1. VERIFICANDO RESOLUÇÃO DE NOME")
    print(f"{'='*60}{Colors.END}\n")
    if not check_localhost_resolution():
        all_ok = False

    # 2. Verificar porta 8000
    print(f"\n{Colors.BLUE}{'='*60}")
    print("2. VERIFICANDO PORTA 8000")
    print(f"{'='*60}{Colors.END}\n")

    hosts_to_check = [
        ('localhost', 8000),
        ('127.0.0.1', 8000),
        ('0.0.0.0', 8000)
    ]

    port_open = False
    for host, port in hosts_to_check:
        if check_port_open(host, port):
            port_open = True
            break

    if not port_open:
        all_ok = False

    # 3. Verificar se API está respondendo
    print(f"\n{Colors.BLUE}{'='*60}")
    print("3. VERIFICANDO RESPOSTA DA API")
    print(f"{'='*60}{Colors.END}\n")

    urls_to_check = [
        'http://localhost:8000',
        'http://127.0.0.1:8000'
    ]

    api_responding = False
    for url in urls_to_check:
        print_info(f"Testando: {url}")
        responding, results = check_api_responding(url)
        if responding:
            api_responding = True
            print_success(f"API está RESPONDENDO em {url}")
            break

    if not api_responding:
        all_ok = False

    # 4. Verificar processos Python
    print(f"\n{Colors.BLUE}{'='*60}")
    print("4. VERIFICANDO PROCESSOS")
    print(f"{'='*60}{Colors.END}\n")
    if not check_python_process():
        all_ok = False

    # Resumo final
    print(f"\n{Colors.BLUE}{'='*60}")
    print("📊 RESUMO")
    print(f"{'='*60}{Colors.END}\n")

    if all_ok:
        print(f"{Colors.GREEN}✅ API ESTÁ ONLINE E ACESSÍVEL!{Colors.END}\n")
        print("Você pode acessar:")
        print(f"   📚 Docs: {Colors.BLUE}http://localhost:8000/docs{Colors.END}")
        print(f"   🏥 Health: {Colors.BLUE}http://localhost:8000/health{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}❌ API NÃO ESTÁ ACESSÍVEL!{Colors.END}\n")
        print("Possíveis soluções:")
        print(f"   1. Inicie a API: {Colors.YELLOW}python start_api.py{Colors.END}")
        print(f"   2. Verifique Redis: {Colors.YELLOW}docker-compose ps{Colors.END}")
        print(f"   3. Execute diagnóstico: {Colors.YELLOW}python diagnose_system.py{Colors.END}")
        print(f"   4. Auto-fix: {Colors.YELLOW}python auto_fix.py{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
