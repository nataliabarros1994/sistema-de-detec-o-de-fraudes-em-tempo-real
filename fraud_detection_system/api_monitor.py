#!/usr/bin/env python3
"""
Monitor e Auto-Restart da API
==============================
Monitora a API e reinicia automaticamente se ela cair

Uso:
    python api_monitor.py

Autor: Natália Barros
"""

import requests
import subprocess
import time
import sys
import signal
from datetime import datetime
from typing import Optional

# Cores
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class APIMonitor:
    """Monitor que mantém a API rodando"""

    def __init__(self, check_interval: int = 10, restart_delay: int = 5):
        """
        Args:
            check_interval: Intervalo entre verificações (segundos)
            restart_delay: Delay antes de reiniciar (segundos)
        """
        self.check_interval = check_interval
        self.restart_delay = restart_delay
        self.api_process: Optional[subprocess.Popen] = None
        self.running = True
        self.restart_count = 0
        self.start_time = datetime.now()

        # Handler para Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        """Handler para interrupção (Ctrl+C)"""
        print(f"\n\n{Colors.YELLOW}⚠️  Recebido sinal de parada...{Colors.END}")
        self.running = False
        self.stop_api()
        sys.exit(0)

    def log(self, message: str, color: str = Colors.BLUE):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{color}[{timestamp}] {message}{Colors.END}")

    def check_api_health(self) -> bool:
        """Verifica se a API está respondendo"""
        try:
            response = requests.get(
                "http://localhost:8000/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def start_api(self):
        """Inicia a API"""
        self.log("🚀 Iniciando API...", Colors.BLUE)

        try:
            # Inicia processo da API
            self.api_process = subprocess.Popen(
                [sys.executable, "-m", "app.main"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Aguarda alguns segundos para API inicializar
            time.sleep(8)

            # Verifica se iniciou
            if self.check_api_health():
                self.log("✅ API iniciada com sucesso!", Colors.GREEN)
                return True
            else:
                self.log("⚠️  API iniciou mas não está respondendo ainda...", Colors.YELLOW)
                # Aguarda mais um pouco
                time.sleep(5)
                if self.check_api_health():
                    self.log("✅ API agora está respondendo!", Colors.GREEN)
                    return True
                else:
                    self.log("❌ API não está respondendo", Colors.RED)
                    return False

        except Exception as e:
            self.log(f"❌ Erro ao iniciar API: {e}", Colors.RED)
            return False

    def stop_api(self):
        """Para a API"""
        if self.api_process:
            self.log("🛑 Parando API...", Colors.YELLOW)
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=10)
                self.log("✅ API parada", Colors.GREEN)
            except subprocess.TimeoutExpired:
                self.log("⚠️  API não respondeu, forçando parada...", Colors.YELLOW)
                self.api_process.kill()
            self.api_process = None

    def restart_api(self):
        """Reinicia a API"""
        self.log("🔄 Reiniciando API...", Colors.YELLOW)
        self.restart_count += 1

        # Para API atual
        self.stop_api()

        # Aguarda antes de reiniciar
        self.log(f"⏳ Aguardando {self.restart_delay} segundos...", Colors.YELLOW)
        time.sleep(self.restart_delay)

        # Inicia novamente
        return self.start_api()

    def get_uptime(self) -> str:
        """Retorna tempo de execução"""
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def monitor(self):
        """Loop principal de monitoramento"""
        print(f"""
{Colors.BLUE}╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   📡 MONITOR DA API - AUTO RESTART ATIVADO 📡             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}Configurações:{Colors.END}
   • Intervalo de verificação: {self.check_interval}s
   • Delay para restart: {self.restart_delay}s

{Colors.GREEN}A API será monitorada continuamente e reiniciada automaticamente se cair.{Colors.END}
{Colors.YELLOW}Pressione Ctrl+C para parar o monitor.{Colors.END}

""")

        # Inicia API pela primeira vez
        if not self.start_api():
            self.log("❌ Falha ao iniciar API pela primeira vez!", Colors.RED)
            return

        self.log(f"✅ Monitor ativo - Verificando a cada {self.check_interval}s", Colors.GREEN)
        print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

        consecutive_failures = 0
        last_status = True

        # Loop de monitoramento
        while self.running:
            try:
                # Verifica saúde
                is_healthy = self.check_api_health()

                # Status mudou?
                if is_healthy != last_status:
                    if is_healthy:
                        self.log("✅ API voltou a responder!", Colors.GREEN)
                        consecutive_failures = 0
                    else:
                        self.log("❌ API parou de responder!", Colors.RED)

                last_status = is_healthy

                # API não está saudável
                if not is_healthy:
                    consecutive_failures += 1
                    self.log(f"⚠️  Falha #{consecutive_failures} detectada", Colors.YELLOW)

                    # Após 2 falhas consecutivas, reinicia
                    if consecutive_failures >= 2:
                        self.log("🔄 Muitas falhas detectadas, reiniciando...", Colors.YELLOW)

                        if not self.restart_api():
                            self.log("❌ Falha ao reiniciar API!", Colors.RED)
                            self.log("⏳ Tentando novamente em 30 segundos...", Colors.YELLOW)
                            time.sleep(30)
                            continue

                        consecutive_failures = 0
                else:
                    # Reset contador de falhas
                    if consecutive_failures > 0:
                        consecutive_failures = 0

                    # Log periódico de status OK (a cada 5 verificações)
                    if int(time.time()) % (self.check_interval * 5) < self.check_interval:
                        uptime = self.get_uptime()
                        self.log(
                            f"✅ API OK | Uptime: {uptime} | Restarts: {self.restart_count}",
                            Colors.GREEN
                        )

                # Aguarda próxima verificação
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"❌ Erro no monitor: {e}", Colors.RED)
                time.sleep(self.check_interval)

        # Cleanup
        self.stop_api()
        uptime = self.get_uptime()

        print(f"""
{Colors.BLUE}{'='*60}
📊 ESTATÍSTICAS FINAIS DO MONITOR
{'='*60}{Colors.END}

{Colors.GREEN}Tempo de execução:{Colors.END} {uptime}
{Colors.GREEN}Total de restarts:{Colors.END} {self.restart_count}

{Colors.YELLOW}Monitor encerrado.{Colors.END}
        """)

def main():
    """Função principal"""
    monitor = APIMonitor(
        check_interval=10,  # Verifica a cada 10 segundos
        restart_delay=5     # Aguarda 5 segundos antes de reiniciar
    )

    monitor.monitor()

if __name__ == "__main__":
    main()
