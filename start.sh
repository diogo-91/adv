#!/bin/bash

# Script de inicialização para rodar Dashboard + Worker no mesmo container

echo "=========================================="
echo "  INICIANDO SISTEMA DE PETIÇÕES"
echo "=========================================="

# Criar diretório de flags se não existir
mkdir -p /app/flags

# Iniciar worker em background
echo "Iniciando Worker (main_v10_fase3.py)..."
python main_v10_fase3.py &
WORKER_PID=$!
echo "Worker iniciado (PID: $WORKER_PID)"

# Aguardar 3 segundos para garantir que o worker iniciou
sleep 3

# Iniciar dashboard em foreground (para manter container ativo)
echo "Iniciando Dashboard (dashboard_server.py)..."
python dashboard_server.py

# Se o dashboard parar, matar o worker também
kill $WORKER_PID 2>/dev/null
