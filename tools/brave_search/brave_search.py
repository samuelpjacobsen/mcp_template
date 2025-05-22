"""
Módulo para integração com a API Brave Search
"""
import os
import json
import urllib.parse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def register_brave_search_tools(mcp):
    @mcp.tool()
    def brave_web_search(query: str, count: int = 10, offset: int = 0) -> str:
        """
        Realiza uma pesquisa web usando a API Brave Search.
        
        Args:
            query: Consulta de pesquisa
            count: Número de resultados (1-20, padrão 10)
            offset: Deslocamento para paginação (máximo 9, padrão 0)
        """
        BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
        if not BRAVE_API_KEY:
            return "Erro: BRAVE_API_KEY não configurada. Configure-a no arquivo .env"
            
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY
        }
        
        # Limitar count e offset a valores válidos
        count = min(max(1, count), 20)
        offset = min(max(0, offset), 9)
        
        params = {
            "q": query,
            "count": str(count),
            "offset": str(offset)
        }
        
        # Construir URL com parâmetros
        query_string = "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"
        
        try:
            req = Request(full_url, headers=headers)
            with urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                # Formatar resultados
                results = []
                for web in data.get("web", {}).get("results", []):
                    title = web.get("title", "")
                    url = web.get("url", "")
                    description = web.get("description", "")
                    results.append(f"## {title}\n{url}\n{description}\n")
                
                if results:
                    return f"# Resultados da pesquisa para '{query}':\n\n" + "\n".join(results)
                else:
                    return f"Nenhum resultado encontrado para '{query}'."
                    
        except HTTPError as e:
            return f"Erro HTTP {e.code}: {e.reason}"
        except URLError as e:
            return f"Erro de conexão: {str(e.reason)}"
        except Exception as e:
            return f"Erro na pesquisa: {str(e)}"
    
    @mcp.tool()
    def brave_local_search(query: str, count: int = 5) -> str:
        """
        Pesquisa por negócios e lugares locais usando a API Brave Search.
        
        Args:
            query: Consulta de pesquisa local
            count: Número de resultados (1-20, padrão 5)
        """
        BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
        if not BRAVE_API_KEY:
            return "Erro: BRAVE_API_KEY não configurada. Configure-a no arquivo .env"
            
        url = "https://api.search.brave.com/res/v1/spotter/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY
        }
        
        # Limitar count a valores válidos
        count = min(max(1, count), 20)
        
        params = {
            "q": query,
            "count": str(count),
            "spotter_src": "local"
        }
        
        # Construir URL com parâmetros
        query_string = "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"
        
        try:
            req = Request(full_url, headers=headers)
            with urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                # Formatar resultados
                results = []
                for place in data.get("results", []):
                    name = place.get("name", "")
                    address = place.get("location", {}).get("display_address", "")
                    phone = place.get("phone", "")
                    rating = place.get("rating", "")
                    
                    result = f"## {name}\n"
                    if address:
                        result += f"Endereço: {address}\n"
                    if phone:
                        result += f"Telefone: {phone}\n"
                    if rating:
                        result += f"Avaliação: {rating}/5\n"
                    
                    results.append(result)
                
                if results:
                    return f"# Locais encontrados para '{query}':\n\n" + "\n".join(results)
                else:
                    return f"Nenhum local encontrado para '{query}'."
                    
        except HTTPError as e:
            return f"Erro HTTP {e.code}: {e.reason}"
        except URLError as e:
            return f"Erro de conexão: {str(e.reason)}"
        except Exception as e:
            return f"Erro na pesquisa: {str(e)}"
            
    return mcp
