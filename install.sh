#!/bin/bash
# Script de instalação para MCP Utilities

echo "Instalando MCP Utilities..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 não está instalado. Por favor, instale o Python 3 primeiro."
    exit 1
fi

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Erro ao criar ambiente virtual. Tentando com outra abordagem..."
        python3 -m pip install --user virtualenv
        python3 -m virtualenv venv
    fi
else
    echo "Ambiente virtual já existe."
fi

# Verificar se o ambiente virtual foi criado com sucesso
if [ ! -d "venv" ]; then
    echo "Erro: Não foi possível criar o ambiente virtual."
    echo "Tente executar manualmente: python3 -m venv venv"
    exit 1
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Verificar instalação do FastMCP
echo "Verificando instalação do FastMCP..."
if ! python -c "import fastmcp; print(f'FastMCP instalado com sucesso: versão {fastmcp.__version__}')"; then
    echo "Erro ao importar FastMCP. Tentando instalar novamente..."
    pip install -r requirements.txt
    
    # Verificar novamente
    if ! python -c "import fastmcp; print(f'FastMCP instalado com sucesso: versão {fastmcp.__version__}')"; then
        echo "Erro: FastMCP não pôde ser instalado. Tente instalar manualmente: pip install fastmcp"
        exit 1
    fi
fi

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "Criando arquivo .env a partir do exemplo..."
    cp .env.example .env
    echo "Por favor, edite o arquivo .env e adicione suas credenciais."
else
    echo "Arquivo .env já existe."
fi

echo "Instalação concluída!"
echo ""
echo "Para iniciar o servidor MCP, execute:"
echo "source venv/bin/activate && python custom_mcp_server.py"
echo ""
echo "Para desativar o ambiente virtual depois de usar:"
echo "deactivate"
