"""
Entrypoint para o serviço WORKER (processamento em background)
Roda apenas o loop de verificação de flags e processamento
"""
import os
import time
import schedule
from dotenv import load_dotenv

# Importar funções do main
import sys
sys.path.insert(0, os.path.dirname(__file__))

from main_v10_fase3 import verificar_flags_manuais

load_dotenv()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  SISTEMA V10.0 - WORKER (MODO MANUAL)")
    print("   Aguardando comandos do Dashboard...")
    print("="*70 + "\n")
    
    print("\n" + "="*70)
    print("  Rodando! Ctrl+C para parar.")
    print("   [MODO] Sistema aguardando comandos manuais via Dashboard...")
    print("   (Varredura automática desativada)")
    print("="*70 + "\n")
    
    while True:
        # Verificar flags manuais a cada ciclo
        verificar_flags_manuais()
        
        # Executar tarefas agendadas (se houver)
        schedule.run_pending()
        time.sleep(5)
