"""
Entrypoint para o serviço DASHBOARD (somente Flask)
Roda apenas o servidor web na porta 5000
"""
import subprocess
import sys

if __name__ == "__main__":
    print("=" * 70)
    print("  INICIANDO DASHBOARD SERVER")
    print("  Porta: 5000")
    print("=" * 70 + "\n")
    
    # Rodar apenas o dashboard_server.py
    subprocess.run([sys.executable, "dashboard_server.py"])
