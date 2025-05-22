"""
Configurações do servidor MCP
Este arquivo carrega variáveis de ambiente usando python-dotenv
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações de API
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
BRAVE_API_KEY = os.getenv('BRAVE_API_KEY', '')

# Outras configurações
MCP_SERVER_NAME = os.getenv('MCP_SERVER_NAME', 'custom_mcp_server')
