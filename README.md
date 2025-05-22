# MCP Utilities

Servidor MCP personalizado com ferramentas para automação de tarefas, integração com Git/GitHub, manipulação de arquivos e acesso a APIs externas.

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## Instalação

### Método 1: Usando o Script de Instalação (Recomendado)

Execute o script de instalação que configura tudo automaticamente:

```bash
# Tornar o script executável
chmod +x install.sh

# Executar o script de instalação
./install.sh
```

O script irá:
1. Criar um ambiente virtual Python
2. Instalar todas as dependências
3. Criar um arquivo `.env` a partir do exemplo
4. Verificar a instalação

### Método 2: Instalação Manual

Se preferir instalar manualmente:

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

## Uso

### Iniciar o Servidor MCP

Para iniciar o servidor MCP, execute:

```bash
# Método simples (recomendado)
./start.sh
```

Ou manualmente:

```bash
# Ativar ambiente virtual (se ainda não estiver ativo)
source venv/bin/activate

# Iniciar o servidor
python custom_mcp_server.py
```

Para parar o servidor, pressione `Ctrl+C`.

Para desativar o ambiente virtual após o uso:

```bash
deactivate
```

### Configuração do Servidor MCP

O servidor MCP já vem com uma configuração padrão, mas você pode personalizá-la:

1. Copie o arquivo de exemplo para criar sua configuração personalizada:
   ```bash
   cp mcp_config.example.json mcp_config.json
   ```

2. Edite o arquivo `mcp_config.json` para ajustar caminhos e variáveis de ambiente:
   ```json
   {
       "mcpServers": {
           "custom_mcp_server": {
               "command": "./venv/bin/python3",
               "args": [
                   "./custom_mcp_server.py"
               ],
               "env": {
                   "GITHUB_TOKEN": "seu_token_github_aqui",
                   "BRAVE_API_KEY": "sua_chave_api_brave_aqui"
               }
           }
       }
   }
   ```

3. Inicie o servidor com as novas configurações usando `./start.sh`

## Ferramentas Disponíveis

O servidor MCP inclui:

- **Ferramentas de Sistema**: Execução de comandos shell, gerenciamento de processos
- **Ferramentas Git/GitHub**: Operações Git, integração com GitHub API
- **Ferramentas de Arquivo**: Manipulação de arquivos e diretórios
- **Ferramentas de API**: Requisições HTTP para APIs externas
- **Brave Search**: Pesquisas web e locais usando a API Brave Search

## Estrutura do Projeto

```
MCP_Utilities/
├── tools/                  # Pacote com ferramentas modulares
│   ├── brave_search/       # Ferramentas para API Brave Search
│   └── ... (outros módulos)
├── .env.example            # Exemplo de configuração de ambiente
├── .gitignore              # Padrões para ignorar no Git
├── mcp_config.example.json # Exemplo de configuração do servidor MCP
├── mcp_config.json         # Configuração do servidor MCP (personalizada)
├── config.py               # Configurações do servidor
├── custom_mcp_server.py    # Servidor MCP principal
├── install.sh              # Script de instalação
├── start.sh                # Script para iniciar o servidor
└── requirements.txt        # Dependências do projeto
```

## Resolução de Problemas

Se encontrar o erro "externally-managed-environment" ao tentar instalar pacotes com pip, isso ocorre porque você está tentando instalar pacotes no Python do sistema. Certifique-se de estar usando o ambiente virtual:

```bash
# Ativar o ambiente virtual
source venv/bin/activate

# Verificar que está usando o pip do ambiente virtual
which pip
# Deve mostrar algo como: /caminho/para/MCP_Utilities/venv/bin/pip
```

## Ferramentas Disponíveis

O servidor MCP inclui:

- **Ferramentas de Sistema**: Execução de comandos shell, gerenciamento de processos
- **Ferramentas Git/GitHub**: Operações Git, integração com GitHub API
- **Ferramentas de Arquivo**: Manipulação de arquivos e diretórios
- **Ferramentas de API**: Requisições HTTP para APIs externas
- **Brave Search**: Pesquisas web e locais usando a API Brave Search
├── config.py               # Configurações do servidor
├── custom_mcp_server.py    # Servidor MCP principal
├── install.sh              # Script de instalação
└── requirements.txt        # Dependências do projeto
```

## Resolução de Problemas

Se encontrar o erro "externally-managed-environment" ao tentar instalar pacotes com pip, isso ocorre porque você está tentando instalar pacotes no Python do sistema. Certifique-se de estar usando o ambiente virtual:

```bash
# Ativar o ambiente virtual
source venv/bin/activate

# Verificar que está usando o pip do ambiente virtual
which pip
# Deve mostrar algo como: /caminho/para/MCP_Utilities/venv/bin/pip
```

## Estrutura do Projeto

```
MCP_Utilities/
├── tools/                  # Pacote com ferramentas modulares
│   ├── brave_search/       # Ferramentas para API Brave Search
│   └── ... (outros módulos)
├── .env.example            # Exemplo de configuração de ambiente
├── .gitignore              # Padrões para ignorar no Git
├── claude_desktop_config.example.json  # Exemplo de configuração para Claude Desktop
├── config.py               # Configurações do servidor
├── custom_mcp_server.py    # Servidor MCP principal
└── requirements.txt        # Dependências do projeto
```

## Uso

### Iniciar o servidor MCP

```bash
python custom_mcp_server.py
```

### Configuração no Claude Desktop

Adicione a configuração a seguir ao arquivo de configuração do Claude Desktop:

```json
{
    "mcpServers": {
        "custom_mcp_server": {
            "command": "/caminho/para/python",
            "args": [
                "/caminho/para/custom_mcp_server.py"
            ]
        }
    }
}
```

## Ferramentas disponíveis

O servidor MCP inclui as seguintes categorias de ferramentas:

- **Sistema**: Execução de comandos shell, gerenciamento de processos
- **Git/GitHub**: Operações Git, integração com GitHub API
- **Arquivos**: Manipulação de arquivos e diretórios
- **API**: Requisições HTTP para APIs externas
- **Brave Search**: Integração com API de pesquisa Brave

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.
