"""
Servidor MCP para dados do CEMADEN
Acessa dados de pluviômetros e informações de alertas

Autor: Assistente Claude
Data: Janeiro 2026
"""

import asyncio
import json
import os
from typing import Any, Optional, Dict, List
import requests
from datetime import datetime, timedelta
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# ====================
# CONFIGURAÇÕES
# ====================

CEMADEN_PAINEL_BASE = "https://painelalertas.cemaden.gov.br"
CEMADEN_MAPA_BASE = "https://mapainterativo.cemaden.gov.br"
TIMEOUT_SEGUNDOS = 15

# Cache de municípios carregado na inicialização
MUNICIPIOS_CACHE: Optional[Dict[str, List[str]]] = None

# ====================
# SERVIDOR MCP
# ====================

server = Server("cemaden-monitor-server")

# ====================
# FUNÇÕES UTILITÁRIAS
# ====================

def carregar_municipios() -> Dict[str, List[str]]:
    """
    Carrega dados de municípios do arquivo JSON.
    
    Returns:
        Dicionário com estados como chaves e lista de municípios como valores
    """
    global MUNICIPIOS_CACHE
    
    if MUNICIPIOS_CACHE is not None:
        return MUNICIPIOS_CACHE
    
    try:
        arquivo = os.path.join(os.path.dirname(__file__), "municipios.json")
        with open(arquivo, "r", encoding="utf-8") as f:
            MUNICIPIOS_CACHE = json.load(f)
            return MUNICIPIOS_CACHE
    except FileNotFoundError:
        print("⚠️  Arquivo municipios.json não encontrado")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar municipios.json: {e}")
        return {}
    except Exception as e:
        print(f"❌ Erro ao carregar municipios.json: {e}")
        return {}


# ====================
# FUNÇÕES DE API
# ====================

def buscar_info_painel_alertas() -> Dict[str, Any]:
    """
    Busca informações da página de alertas do CEMADEN.
    Valida conexão com o painel interativo.
    
    Returns:
        Dicionário com informações dos alertas
    """
    try:
        url = f"{CEMADEN_PAINEL_BASE}/"
        
        print(f"🔍 Acessando painel de alertas: {url}")
        response = requests.get(url, timeout=TIMEOUT_SEGUNDOS)
        response.raise_for_status()
        
        # Retorna informações do painel
        return {
            "sucesso": True,
            "url_painel": url,
            "mensagem": "O CEMADEN disponibiliza alertas através do painel interativo. "
                       "Acesse https://painelalertas.cemaden.gov.br/ para visualizar "
                       "alertas ativos de movimento de massa e riscos hidrológicos.",
            "info": {
                "descricao": "Painel mostra alertas por UF e município",
                "niveis": ["Moderado", "Alto", "Muito Alto"],
                "tipos": ["Movimento de Massa", "Risco Hidrológico"],
                "total_municipios_monitorados": 959
            },
            "acesso_direto": url
        }
    
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout ao acessar painel de alertas")
        return {
            "sucesso": False,
            "erro": "Timeout ao acessar painel de alertas",
            "url_alternativa": "https://painelalertas.cemaden.gov.br/",
            "nota": "Acesse o link diretamente no navegador para visualizar alertas ativos"
        }
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar painel: {str(e)}")
        return {
            "sucesso": False,
            "erro": f"Erro ao acessar painel de alertas: {str(e)}",
            "url_alternativa": "https://painelalertas.cemaden.gov.br/",
            "nota": "Acesse o link diretamente no navegador para visualizar alertas ativos"
        }


def buscar_municipios_monitorados(estado: Optional[str] = None) -> Dict[str, Any]:
    """
    Lista municípios monitorados pelo CEMADEN.
    
    Args:
        estado: Sigla do estado (opcional). Ex: SP, RJ, MG
    
    Returns:
        Dicionário com municípios ou mensagem de erro
    """
    try:
        municipios_data = carregar_municipios()
        
        if not municipios_data:
            return {
                "sucesso": False,
                "erro": "Não foi possível carregar dados de municípios",
                "nota": "O CEMADEN monitora 959 municípios em todo o Brasil. "
                       "Para lista completa, acesse: http://www2.cemaden.gov.br/"
            }
        
        # Se especificou estado, valida e retorna
        if estado:
            estado_upper = estado.upper().strip()
            
            if estado_upper not in municipios_data:
                estados_disponiveis = sorted(municipios_data.keys())
                return {
                    "sucesso": False,
                    "erro": f"Estado '{estado}' não encontrado",
                    "estados_disponiveis": estados_disponiveis,
                    "total_estados": len(estados_disponiveis),
                    "nota": "Use a sigla do estado (ex: SP, RJ, MG)"
                }
            
            municipios = municipios_data[estado_upper]
            return {
                "sucesso": True,
                "estado": estado_upper,
                "total": len(municipios),
                "municipios": municipios,
                "fonte": "CEMADEN - Centro Nacional de Monitoramento e Alertas de Desastres Naturais"
            }
        
        # Se não especificou estado, retorna todas as informações
        total_municipios = sum(len(m) for m in municipios_data.values())
        return {
            "sucesso": True,
            "total_municipal": total_municipios,
            "total_estados": len(municipios_data),
            "estados_disponiveis": sorted(municipios_data.keys()),
            "municipios_por_estado": municipios_data,
            "fonte": "CEMADEN",
            "nota": "Para filtrar por estado, use o parâmetro 'estado' com a sigla (SP, RJ, MG, etc)"
        }
    
    except Exception as e:
        return {
            "sucesso": False,
            "erro": f"Erro ao processar municipios: {str(e)}"
        }


def buscar_info_monitoramento() -> Dict[str, Any]:
    """
    Retorna informações sobre o sistema de monitoramento do CEMADEN.
    
    Returns:
        Dicionário com informações completas do sistema
    """
    return {
        "sucesso": True,
        "cemaden": {
            "nome_completo": "Centro Nacional de Monitoramento e Alertas de Desastres Naturais",
            "website": "http://www.cemaden.gov.br",
            "painel_alertas": "https://painelalertas.cemaden.gov.br/",
            "mapa_interativo": "https://mapainterativo.cemaden.gov.br/"
        },
        "monitoramento": {
            "total_municipios": 959,
            "tipos_alerta": [
                {
                    "tipo": "Movimento de Massa",
                    "descricao": "Deslizamentos de terra, corridas de massa e outros movimentos geológicos"
                },
                {
                    "tipo": "Risco Hidrológico",
                    "descricao": "Enchentes, enxurradas, inundações e alagamentos"
                }
            ],
            "niveis_alerta": [
                {
                    "nivel": "Moderado",
                    "cor": "Amarelo",
                    "descricao": "Potencial de ocorrência de desastres"
                },
                {
                    "nivel": "Alto",
                    "cor": "Laranja",
                    "descricao": "Risco elevado de ocorrência de desastres"
                },
                {
                    "nivel": "Muito Alto",
                    "cor": "Vermelho",
                    "descricao": "Risco muito elevado de ocorrência de desastres"
                }
            ]
        },
        "rede_observacional": {
            "pluviometros_automaticos": "Medem chuva a cada 10 minutos",
            "pluviometros_comunitarios": "~1150 distribuídos em +300 municípios",
            "radares_meteorologicos": "9 radares de dupla polarização",
            "estacoes_hidrologicas": "Monitoram nível de rios"
        },
        "como_usar": {
            "alertas": "Acesse https://painelalertas.cemaden.gov.br/ para ver alertas ativos",
            "dados_chuva": "Acesse https://mapainterativo.cemaden.gov.br/ para dados de pluviômetros",
            "download_dados": "Disponível no Mapa Interativo por UF e município"
        }
    }


def buscar_links_uteis(tipo: Optional[str] = None) -> Dict[str, Any]:
    """
    Retorna links úteis do CEMADEN.
    
    Args:
        tipo: Tipo de recurso (alertas, dados, educacao)
    
    Returns:
        Dicionário com links organizados por categoria
    """
    links = {
        "alertas": {
            "titulo": "Sistema de Alertas",
            "links": [
                {
                    "nome": "Painel de Alertas",
                    "url": "https://painelalertas.cemaden.gov.br/",
                    "descricao": "Visualização de alertas ativos por estado e município"
                }
            ]
        },
        "dados": {
            "titulo": "Dados e Monitoramento",
            "links": [
                {
                    "nome": "Mapa Interativo",
                    "url": "https://mapainterativo.cemaden.gov.br/",
                    "descricao": "Dados de pluviômetros em tempo real e download de histórico"
                },
                {
                    "nome": "Site Oficial",
                    "url": "http://www.cemaden.gov.br",
                    "descricao": "Portal principal do CEMADEN"
                }
            ]
        },
        "educacao": {
            "titulo": "CEMADEN Educação",
            "links": [
                {
                    "nome": "Portal Educação",
                    "url": "https://educacao.cemaden.gov.br/",
                    "descricao": "Projeto educacional sobre percepção de riscos"
                }
            ]
        }
    }
    
    if tipo and tipo.lower() in links:
        return {
            "sucesso": True,
            "categoria": tipo.lower(),
            **links[tipo.lower()]
        }
    else:
        return {
            "sucesso": True,
            "todas_categorias": links
        }


# ====================
# HANDLERS MCP
# ====================

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    Lista todas as ferramentas disponíveis no servidor MCP
    """
    return [
        Tool(
            name="consultar_painel_alertas",
            description="""
            Acessa o painel de alertas do CEMADEN para obter informações sobre alertas ativos
            de desastres naturais no Brasil.
            
            O CEMADEN emite alertas de:
            - Movimento de Massa (deslizamentos)
            - Risco Hidrológico (enchentes, enxurradas)
            
            Com níveis: Moderado, Alto, Muito Alto
            
            Retorna link direto para o painel interativo onde podem ser consultados
            alertas por estado e município.
            """,
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        
        Tool(
            name="listar_municipios_monitorados",
            description="""
            Lista municípios brasileiros monitorados pelo CEMADEN.
            
            O CEMADEN monitora 959 municípios vulneráveis a desastres naturais.
            Pode filtrar por estado específico (use sigla: SP, RJ, MG, etc.).
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "estado": {
                        "type": "string",
                        "description": "Sigla do estado (SP, RJ, MG, RS, PR, SC, BA, PE, CE, ES, etc.). Opcional.",
                    },
                },
                "required": [],
            },
        ),
        
        Tool(
            name="info_sistema_monitoramento",
            description="""
            Retorna informações completas sobre o sistema de monitoramento do CEMADEN,
            incluindo tipos de alerta, níveis, rede observacional e como acessar os dados.
            
            Útil para entender como funciona o sistema de alertas e monitoramento.
            """,
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        
        Tool(
            name="links_cemaden",
            description="""
            Retorna links úteis do CEMADEN organizados por categoria.
            
            Categorias disponíveis:
            - alertas: Painel de alertas ativos
            - dados: Mapa interativo e dados de pluviômetros
            - educacao: Portal educacional sobre percepção de riscos
            
            Se não especificar categoria, retorna todos os links.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "tipo": {
                        "type": "string",
                        "description": "Categoria de links: 'alertas', 'dados' ou 'educacao'. Opcional.",
                    },
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    Executa a ferramenta solicitada pelo Claude Desktop
    """
    
    import sys
    
    # Log em arquivo
    try:
        with open("cemaden_mcp_debug.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"\n{'='*50}\n")
            log_file.write(f"🔧 Ferramenta: {name}\n")
            log_file.write(f"📥 Argumentos: {arguments}\n")
            log_file.write(f"⏰ {datetime.now()}\n")
            log_file.write(f"{'='*50}\n")
    except:
        pass
    
    print(f"\n{'='*50}", file=sys.stderr)
    print(f"🔧 Executando: {name}", file=sys.stderr)
    print(f"📥 Argumentos: {arguments}", file=sys.stderr)
    print(f"{'='*50}\n", file=sys.stderr)
    
    # ===== PAINEL DE ALERTAS =====
    if name == "consultar_painel_alertas":
        resultado = buscar_info_painel_alertas()
        return [TextContent(type="text", text=json.dumps(resultado, indent=2, ensure_ascii=False))]
    
    # ===== MUNICÍPIOS =====
    elif name == "listar_municipios_monitorados":
        estado = arguments.get("estado") if arguments else None
        resultado = buscar_municipios_monitorados(estado)
        return [TextContent(type="text", text=json.dumps(resultado, indent=2, ensure_ascii=False))]
    
    # ===== INFO SISTEMA =====
    elif name == "info_sistema_monitoramento":
        resultado = buscar_info_monitoramento()
        return [TextContent(type="text", text=json.dumps(resultado, indent=2, ensure_ascii=False))]
    
    # ===== LINKS ÚTEIS =====
    elif name == "links_cemaden":
        tipo = arguments.get("tipo") if arguments else None
        resultado = buscar_links_uteis(tipo)
        return [TextContent(type="text", text=json.dumps(resultado, indent=2, ensure_ascii=False))]
    
    # ===== FERRAMENTA DESCONHECIDA =====
    else:
        raise ValueError(f"Ferramenta desconhecida: {name}")


# ====================
# INICIALIZAÇÃO
# ====================

async def main():
    """
    Função principal que inicializa e executa o servidor MCP
    """
    import sys
    
    # Pré-carrega dados de municípios
    carregar_municipios()
    
    # Log de inicialização
    try:
        with open("cemaden_mcp_debug.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"\n{'='*60}\n")
            log_file.write(f"🚀 Servidor iniciado: {datetime.now()}\n")
            log_file.write(f"📡 Painel: {CEMADEN_PAINEL_BASE}\n")
            log_file.write(f"🗺️  Mapa: {CEMADEN_MAPA_BASE}\n")
            log_file.write(f"{'='*60}\n")
    except:
        pass
    
    print("🚀 Servidor MCP CEMADEN iniciado", file=sys.stderr)
    print(f"📡 Painel: {CEMADEN_PAINEL_BASE}", file=sys.stderr)
    print(f"🗺️  Mapa: {CEMADEN_MAPA_BASE}", file=sys.stderr)
    print(f"📝 Log: cemaden_mcp_debug.log", file=sys.stderr)
    print("="*50, file=sys.stderr)
    
    # Rodar servidor
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="cemaden-monitor-server",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


# ====================
# EXECUÇÃO
# ====================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Servidor encerrado")
    except Exception as e:
        print(f"\n\n❌ Erro: {str(e)}")
        raise