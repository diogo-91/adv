"""
Entrypoint unificado - escolhe o modo baseado na variável SERVICE_TYPE
SERVICE_TYPE=dashboard → Roda só Flask
SERVICE_TYPE=worker → Roda só o loop de processamento
"""
import os
import sys
import subprocess
import time
import schedule
from dotenv import load_dotenv

load_dotenv()

SERVICE_TYPE = os.getenv('SERVICE_TYPE', 'worker').lower()

if SERVICE_TYPE == 'dashboard':
    print("=" * 70)
    print("  INICIANDO DASHBOARD SERVER")
    print("  Porta: 5000")
    print("=" * 70 + "\n")
    
    # Rodar apenas o dashboard_server.py
    subprocess.run([sys.executable, "dashboard_server.py"])
    
elif SERVICE_TYPE == 'worker':
    print("\n" + "="*70)
    print("  SISTEMA V10.0 - WORKER (MODO MANUAL)")
    print("   Aguardando comandos do Dashboard...")
    print("="*70 + "\n")
    
    # Importar funções do main
    from main_v10_fase3 import verificar_flags_manuais
    
    print("\n" + "="*70)
    print("  Rodando! Ctrl+C para parar.")
    print("   [MODO] Sistema aguardando comandos manuais via Dashboard...")
    print("   (Varredura automática desativada)")
    print("="*70 + "\n")
    
    while True:
        verificar_flags_manuais()
        schedule.run_pending()
        time.sleep(5)
else:
    print(f"ERRO: SERVICE_TYPE inválido: {SERVICE_TYPE}")
    print("Use SERVICE_TYPE=dashboard ou SERVICE_TYPE=worker")
    sys.exit(1)
