#!/bin/bash
# Script para iniciar o servidor MCP

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "Ambiente virtual não encontrado. Executando script de instalação primeiro..."
    ./install.sh
else
    # Ativar ambiente virtual
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
    
    # Iniciar o servidor
    echo "Iniciando servidor MCP..."
    python custom_mcp_server.py
fi
