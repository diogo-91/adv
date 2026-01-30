#!/usr/bin/env python3
"""
Script de inicialização para rodar Dashboard + Worker no mesmo container
"""
import os
import sys
import subprocess
import time
import signal

def main():
    print("=" * 50)
    print("  INICIANDO SISTEMA DE PETIÇÕES")
    print("=" * 50)
    
    # Criar diretório de flags se não existir
    os.makedirs('/app/flags', exist_ok=True)
    print("✓ Diretório de flags criado")
    
    # Iniciar worker em background
    print("\nIniciando Worker (main_v10_fase3.py)...")
    worker_process = subprocess.Popen(
        [sys.executable, 'main_v10_fase3.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    print(f"✓ Worker iniciado (PID: {worker_process.pid})")
    
    # Aguardar 3 segundos para garantir que o worker iniciou
    time.sleep(3)
    
    # Iniciar dashboard em foreground
    print("\nIniciando Dashboard (dashboard_server.py)...")
    print("=" * 50)
    
    try:
        # Executar dashboard (bloqueia aqui)
        subprocess.run([sys.executable, 'dashboard_server.py'], check=True)
    except KeyboardInterrupt:
        print("\n\nRecebido sinal de interrupção...")
    finally:
        # Matar worker ao sair
        print("Encerrando worker...")
        worker_process.terminate()
        try:
            worker_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            worker_process.kill()
        print("✓ Sistema encerrado")

if __name__ == '__main__':
    main()
