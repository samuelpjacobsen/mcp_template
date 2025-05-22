import os
import subprocess
import sys
import json
import socket
import asyncio
import urllib.request
import urllib.parse
import urllib.error
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from pathlib import Path

try:
    from fastmcp import FastMCP
except ImportError:
    print("Erro: Não foi possível importar FastMCP. Execute 'pip install fastmcp' primeiro.")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Erro: Não foi possível importar dotenv. Execute 'pip install python-dotenv' primeiro.")
    sys.exit(1)

# Importar módulo de ferramentas Brave Search
try:
    from tools.brave_search.brave_search import register_brave_search_tools
except ImportError:
    print("Aviso: Módulo Brave Search não encontrado.")
    
    def register_brave_search_tools(mcp):
        print("Módulo Brave Search não está disponível.")
        return mcp

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter tokens de APIs das variáveis de ambiente
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
if not GITHUB_TOKEN:
    print("Aviso: GITHUB_TOKEN não configurado. Algumas ferramentas Git/GitHub não funcionarão.")

# Definir o token como variável de ambiente para subprocessos
os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN

# Funções de ajuda
def attempt_fix(command, error_msg):
    """
    Função que tenta corrigir automaticamente o comando.
    """
    if "not found" in error_msg:
        fixed_command = f"sudo {command}"
        try:
            result = subprocess.run(fixed_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode(), True
        except subprocess.CalledProcessError as e:
            return e.stderr.decode(), False
    return error_msg, False

# Ferramentas do sistema
def register_system_tools(mcp):
    @mcp.tool()
    def run_command(cmd: str, background: bool = False) -> str:
        """
        Executa um comando do shell.
        Se 'background' for True, o comando é iniciado sem esperar sua conclusão.
        Em caso de erro, tenta uma correção automática.
        
        Args:
            cmd: Comando a ser executado
            background: Se True, executa em background
        """
        if background:
            try:
                subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return f"Comando iniciado em background: {cmd}"
            except Exception as e:
                return f"Erro ao iniciar comando em background: {str(e)}"
        else:
            try:
                result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return result.stdout.decode()
            except subprocess.CalledProcessError as e:
                error_output = e.stderr.decode()
                fixed_output, success = attempt_fix(cmd, error_output)
                if success:
                    return f"Comando corrigido automaticamente:\n{fixed_output}"
                else:
                    return f"Erro na execução do comando: {error_output}"
    
    @mcp.tool()
    def execute_shell_script(script_content: str, save_as: str = "temp_script.sh") -> str:
        """
        Cria e executa um script shell.
        
        Args:
            script_content: Conteúdo do script shell
            save_as: Nome do arquivo temporário para salvar o script
        """
        try:
            # Salvar o script em um arquivo
            with open(save_as, "w") as f:
                f.write(script_content)
            
            # Tornar o script executável
            os.chmod(save_as, 0o755)
            
            # Executar o script
            result = subprocess.run(f"./{save_as}", shell=True, check=True, 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Opcionalmente remover o arquivo temporário
            os.remove(save_as)
            
            return result.stdout.decode()
        except Exception as e:
            return f"Erro ao executar script: {str(e)}"
    
    @mcp.tool()
    def check_process_running(process_name: str) -> str:
        """
        Verifica se um processo está em execução.
        
        Args:
            process_name: Nome do processo a verificar
        """
        try:
            result = subprocess.run(f"ps aux | grep -v grep | grep {process_name}", 
                                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0 and result.stdout:
                return f"Processo '{process_name}' está em execução:\n{result.stdout.decode()}"
            else:
                return f"Processo '{process_name}' não está em execução."
        except Exception as e:
            return f"Erro ao verificar processo: {str(e)}"
    
    @mcp.tool()
    def kill_process(process_name: str) -> str:
        """
        Mata um processo pelo nome.
        
        Args:
            process_name: Nome do processo a ser encerrado
        """
        try:
            result = subprocess.run(f"pkill -f {process_name}", 
                                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Processo '{process_name}' encerrado."
        except Exception as e:
            return f"Erro ao encerrar processo: {str(e)}"
            
    return mcp

# Ferramentas Git
def setup_git_credentials():
    """
    Configura as credenciais do Git usando o token do GitHub.
    """
    try:
        # Se não há token, não podemos configurar
        if not GITHUB_TOKEN:
            return "Token GitHub não configurado. Configure o token para usar as ferramentas Git."
        
        # Configurar git para usar o token na URL HTTPS
        git_username = "x-access-token"
        
        # Configurar credenciais para HTTPS
        subprocess.run(["git", "config", "--global", "credential.helper", "store"], check=True)
        
        # Criar/atualizar arquivo de credenciais
        home_dir = os.path.expanduser("~")
        with open(os.path.join(home_dir, ".git-credentials"), "w") as f:
            f.write(f"https://{git_username}:{GITHUB_TOKEN}@github.com\n")
            
        # Configurar nome e email para commits (usar valores genéricos se não configurados)
        try:
            subprocess.run(["git", "config", "--global", "user.name"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            subprocess.run(["git", "config", "--global", "user.name", "MCP Automation"], check=True)
            
        try:
            subprocess.run(["git", "config", "--global", "user.email"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            subprocess.run(["git", "config", "--global", "user.email", "mcp-auto@example.com"], check=True)
            
        return "Credenciais do Git configuradas com sucesso."
    except Exception as e:
        return f"Erro ao configurar credenciais do Git: {str(e)}"

def register_git_tools(mcp):
    @mcp.tool()
    def git_clone(repo_url: str, directory: str = ".") -> str:
        """
        Clona um repositório Git usando autenticação automática para GitHub.
        
        Args:
            repo_url: URL do repositório (HTTPS ou SSH)
            directory: Diretório onde o repositório será clonado
        """
        # Se é um repo GitHub via HTTPS, use o token para auth
        if "github.com" in repo_url and repo_url.startswith("https://"):
            if GITHUB_TOKEN:
                # Substituir a URL original com a URL contendo o token
                repo_path = repo_url.replace("https://github.com/", "").replace(".git", "")
                auth_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{repo_path}.git"
                cmd = f"git clone {auth_url} {directory}"
            else:
                cmd = f"git clone {repo_url} {directory}"
        else:
            cmd = f"git clone {repo_url} {directory}"
            
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Repositório clonado com sucesso em {directory}"
        except subprocess.CalledProcessError as e:
            return f"Erro ao clonar repositório: {e.stderr.decode()}"
    
    @mcp.tool()
    def git_add(path: str = ".") -> str:
        """
        Adiciona arquivos ao índice Git.
        
        Args:
            path: Caminho dos arquivos a serem adicionados ('.' para todos)
        """
        cmd = f"git add {path}"
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Arquivos adicionados ao índice Git: {path}"
        except subprocess.CalledProcessError as e:
            return f"Erro ao adicionar arquivos: {e.stderr.decode()}"
    
    @mcp.tool()
    def git_commit(message: str) -> str:
        """
        Realiza um commit das alterações.
        
        Args:
            message: Mensagem de commit
        """
        cmd = f'git commit -m "{message}"'
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Commit realizado: {message}"
        except subprocess.CalledProcessError as e:
            return f"Erro ao realizar commit: {e.stderr.decode()}"
    
    @mcp.tool()
    def git_push(branch: str = "", remote: str = "origin") -> str:
        """
        Envia alterações para o repositório remoto.
        
        Args:
            branch: Branch para push (vazio usa a branch atual)
            remote: Nome do remoto (padrão: origin)
        """
        # Obtém o URL do remoto
        get_remote_url = f"git config --get remote.{remote}.url"
        try:
            remote_url = subprocess.run(get_remote_url, shell=True, check=True, 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
        except:
            remote_url = ""
        
        # Se for GitHub e tivermos token, usar URL com autenticação
        if "github.com" in remote_url and GITHUB_TOKEN:
            repo_path = remote_url.replace("https://github.com/", "").replace(".git", "").strip()
            auth_url = f"https://x-access-token:{GITHUB_TOKEN}@github.com/{repo_path}.git"
            
            # Obter a branch atual se não especificada
            if not branch:
                try:
                    branch = subprocess.run("git symbolic-ref --short HEAD", shell=True, check=True, 
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
                except:
                    branch = "main"  # Fallback para main se não conseguir determinar
            
            cmd = f"git push {auth_url} {branch}"
        else:
            # Push normal
            cmd = f"git push {remote} {branch}".strip()
            if branch == "":
                cmd = f"git push {remote}".strip()
        
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return "Push realizado com sucesso"
        except subprocess.CalledProcessError as e:
            return f"Erro ao realizar push: {e.stderr.decode()}"
    
    @mcp.tool()
    def git_pull(branch: str = "", remote: str = "origin") -> str:
        """
        Puxa alterações do repositório remoto.
        
        Args:
            branch: Branch para pull (vazio usa a branch atual)
            remote: Nome do remoto (padrão: origin)
        """
        cmd = f"git pull {remote} {branch}".strip()
        if branch == "":
            cmd = f"git pull {remote}".strip()
            
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Pull realizado com sucesso: {result.stdout.decode()}"
        except subprocess.CalledProcessError as e:
            return f"Erro ao realizar pull: {e.stderr.decode()}"
    
    @mcp.tool()
    def git_checkout(branch: str, create: bool = False) -> str:
        """
        Muda para outra branch ou cria uma nova.
        
        Args:
            branch: Nome da branch
            create: Se True, cria uma nova branch
        """
        if create:
            cmd = f"git checkout -b {branch}"
        else:
            cmd = f"git checkout {branch}"
            
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if create:
                return f"Branch '{branch}' criada e alternada com sucesso"
            else:
                return f"Alternado para branch '{branch}' com sucesso"
        except subprocess.CalledProcessError as e:
            return f"Erro ao alternar branch: {e.stderr.decode()}"
    
    @mcp.tool()
    def git_status() -> str:
        """
        Retorna o status atual do repositório Git.
        """
        cmd = "git status"
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode()
        except subprocess.CalledProcessError as e:
            return f"Erro ao obter status Git: {e.stderr.decode()}"
    
    @mcp.tool()
    def git_log(count: int = 5) -> str:
        """
        Mostra o histórico de commits.
        
        Args:
            count: Número de commits a mostrar
        """
        cmd = f"git log --oneline -n {count}"
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode()
        except subprocess.CalledProcessError as e:
            return f"Erro ao obter log Git: {e.stderr.decode()}"
    
    @mcp.tool()
    def github_create_repo(name: str, private: bool = False, description: str = "") -> str:
        """
        Cria um novo repositório no GitHub.
        
        Args:
            name: Nome do repositório
            private: Se True, o repositório será privado
            description: Descrição do repositório
        """
        if not GITHUB_TOKEN:
            return "Token GitHub não configurado. Não é possível criar repositório."
        
        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        data = {
            "name": name,
            "private": private,
            "description": description
        }
        
        try:
            # Converte o dicionário data para JSON string
            data_bytes = json.dumps(data).encode('utf-8')
            
            # Cria a requisição
            req = Request(url, data=data_bytes, headers=headers, method="POST")
            
            # Faz a requisição
            with urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                repo = json.loads(response_data)
                return f"Repositório criado com sucesso: {repo.get('html_url')}"
        except HTTPError as e:
            error_message = e.read().decode('utf-8')
            return f"Erro ao criar repositório (HTTP {e.code}): {error_message}"
        except URLError as e:
            return f"Erro de conexão ao criar repositório: {str(e.reason)}"
        except Exception as e:
            return f"Erro ao criar repositório: {str(e)}"
    
    @mcp.tool()
    def github_create_pull_request(repo_owner: str, repo_name: str, title: str, 
                                head: str, base: str = "main", body: str = "") -> str:
        """
        Cria uma Pull Request no GitHub.
        
        Args:
            repo_owner: Dono do repositório (usuário ou organização)
            repo_name: Nome do repositório
            title: Título da Pull Request
            head: Branch de origem (suas alterações)
            base: Branch de destino (padrão: main)
            body: Descrição da Pull Request
        """
        if not GITHUB_TOKEN:
            return "Token GitHub não configurado. Não é possível criar Pull Request."
        
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        
        try:
            # Converte o dicionário data para JSON string
            data_bytes = json.dumps(data).encode('utf-8')
            
            # Cria a requisição
            req = Request(url, data=data_bytes, headers=headers, method="POST")
            
            # Faz a requisição
            with urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                pr = json.loads(response_data)
                return f"Pull Request criada com sucesso: {pr.get('html_url')}"
        except HTTPError as e:
            error_message = e.read().decode('utf-8')
            return f"Erro ao criar Pull Request (HTTP {e.code}): {error_message}"
        except URLError as e:
            return f"Erro de conexão ao criar Pull Request: {str(e.reason)}"
        except Exception as e:
            return f"Erro ao criar Pull Request: {str(e)}"
    
    @mcp.tool()
    def git_init(directory: str = ".") -> str:
        """
        Inicializa um novo repositório Git.
        
        Args:
            directory: Diretório onde inicializar o repositório
        """
        cmd = f"cd {directory} && git init"
        try:
            result = subprocess.run(cmd, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Repositório Git inicializado em {directory}"
        except subprocess.CalledProcessError as e:
            return f"Erro ao inicializar repositório: {e.stderr.decode()}"
        
    return mcp

# Ferramentas de Arquivo
def register_file_tools(mcp):
    @mcp.tool()
    def create_file(path: str, content: str) -> str:
        """
        Cria um novo arquivo com o conteúdo especificado.
        
        Args:
            path: Caminho completo do arquivo
            content: Conteúdo a ser escrito
        """
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"Arquivo criado com sucesso: {path}"
        except Exception as e:
            return f"Erro ao criar arquivo: {str(e)}"
    
    @mcp.tool()
    def read_file(path: str) -> str:
        """
        Lê o conteúdo de um arquivo.
        
        Args:
            path: Caminho do arquivo
        """
        try:
            with open(path, 'r') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"
    
    @mcp.tool()
    def edit_file(path: str, old_text: str, new_text: str) -> str:
        """
        Edita um arquivo substituindo texto.
        
        Args:
            path: Caminho do arquivo
            old_text: Texto a substituir
            new_text: Novo texto
        """
        try:
            with open(path, 'r') as f:
                content = f.read()
                
            if old_text not in content:
                return f"Texto a ser substituído não encontrado no arquivo."
                
            new_content = content.replace(old_text, new_text)
            
            with open(path, 'w') as f:
                f.write(new_content)
                
            return f"Arquivo editado com sucesso: {path}"
        except Exception as e:
            return f"Erro ao editar arquivo: {str(e)}"
    
    @mcp.tool()
    def append_to_file(path: str, content: str) -> str:
        """
        Adiciona conteúdo ao final de um arquivo.
        
        Args:
            path: Caminho do arquivo
            content: Conteúdo a adicionar
        """
        try:
            with open(path, 'a') as f:
                f.write(content)
            return f"Conteúdo adicionado ao arquivo: {path}"
        except Exception as e:
            return f"Erro ao adicionar conteúdo: {str(e)}"
    
    @mcp.tool()
    def create_directory(path: str) -> str:
        """
        Cria um novo diretório.
        
        Args:
            path: Caminho do diretório
        """
        try:
            os.makedirs(path, exist_ok=True)
            return f"Diretório criado: {path}"
        except Exception as e:
            return f"Erro ao criar diretório: {str(e)}"
    
    @mcp.tool()
    def list_directory(path: str = ".") -> str:
        """
        Lista o conteúdo de um diretório.
        
        Args:
            path: Caminho do diretório
        """
        try:
            items = os.listdir(path)
            result = []
            
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    result.append(f"[DIR] {item}")
                else:
                    result.append(f"[FILE] {item}")
                    
            return "\n".join(result)
        except Exception as e:
            return f"Erro ao listar diretório: {str(e)}"
            
    return mcp

# Ferramentas de API
def register_api_tools(mcp):
    @mcp.tool()
    def make_http_request(url: str, method: str = "GET", headers: dict = None, 
                          data: str = None, timeout: int = 30) -> str:
        """
        Realiza uma requisição HTTP e retorna a resposta.
        
        Args:
            url: URL para fazer a requisição
            method: Método HTTP (GET, POST, PUT, DELETE, etc)
            headers: Cabeçalhos da requisição em formato dict
            data: Corpo da requisição
            timeout: Tempo máximo de espera em segundos
        """
        headers = headers or {}
        
        try:
            # Prepara os dados se fornecidos
            data_bytes = None
            if data:
                if isinstance(data, dict):
                    data_bytes = json.dumps(data).encode('utf-8')
                    if 'Content-Type' not in headers:
                        headers['Content-Type'] = 'application/json'
                else:
                    data_bytes = data.encode('utf-8')
            
            # Cria a requisição
            req = Request(url, data=data_bytes, headers=headers, method=method)
            
            # Configura o timeout
            with urlopen(req, timeout=timeout) as response:
                # Lê o corpo da resposta
                response_body = response.read().decode('utf-8')
                
                # Obtém os cabeçalhos da resposta
                response_headers = dict(response.getheaders())
                
                # Retorna o resultado formatado
                return f"Status: {response.status}\nHeaders: {response_headers}\n\nBody: {response_body}"
                
        except HTTPError as e:
            # Captura erros HTTP como 404, 500, etc.
            error_body = e.read().decode('utf-8')
            return f"Erro HTTP {e.code}: {e.reason}\n\nBody: {error_body}"
        except URLError as e:
            # Captura erros de conexão
            return f"Erro de conexão: {str(e.reason)}"
        except Exception as e:
            # Captura outros erros
            return f"Erro na requisição HTTP: {str(e)}"
            
    return mcp

# Inicializa todas as ferramentas
async def initialize_server():
    """
    Inicializa o servidor MCP com todas as ferramentas
    """
    print("Inicializando servidor MCP customizado...")
    
    # Criar instância do MCP
    mcp = FastMCP("custom_mcp_server")
    
    # Configurar chave API do Brave Search
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
    if BRAVE_API_KEY:
        os.environ["BRAVE_API_KEY"] = BRAVE_API_KEY
        print(f"Chave API Brave Search configurada: {'***' + BRAVE_API_KEY[-4:] if BRAVE_API_KEY else 'Não configurada'}")
    else:
        print("Aviso: BRAVE_API_KEY não configurada. Pesquisas Brave não funcionarão corretamente.")
    
    # Configurar credenciais do Git na inicialização
    setup_result = setup_git_credentials()
    print(setup_result)
    
    # Registrar ferramentas essenciais
    mcp = register_system_tools(mcp)
    mcp = register_git_tools(mcp)
    mcp = register_file_tools(mcp)
    mcp = register_api_tools(mcp)
    
    # Registrar ferramentas do Brave Search
    mcp = register_brave_search_tools(mcp)
    
    print("Todas as ferramentas foram registradas com sucesso!")
    
    # Exibir contagem de ferramentas registradas
    tools = await mcp.get_tools()
    print(f"Total de ferramentas MCP registradas: {len(tools)}")
    
    return mcp

# Inicia o servidor MCP
async def main():
    print("Iniciando servidor MCP personalizado...")
    print(f"Token GitHub configurado: {'***' + GITHUB_TOKEN[-4:] if GITHUB_TOKEN else 'Não configurado'}")
    
    # Inicializar o servidor principal
    mcp = await initialize_server()
    
    # Em vez de chamar mcp.run(), vamos chamar diretamente o método run_stdio_async
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
