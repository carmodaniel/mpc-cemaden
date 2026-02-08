# 🌧️ CEMADEN MCP Server

Servidor MCP para acessar dados do CEMADEN (Centro Nacional de Monitoramento e Alertas de Desastres Naturais) diretamente no Claude Desktop.

## O que é isso?

Este projeto permite que você consulte informações sobre alertas de desastres naturais do Brasil conversando com o Claude Desktop. Você pode perguntar sobre alertas ativos, municípios monitorados e dados de monitoramento de forma natural.

**Exemplo:**
- "Quais são os alertas ativos de desastres no Brasil?"
- "Que cidades de São Paulo são monitoradas pelo CEMADEN?"
- "Como funciona o sistema de alertas?"

## Funcionalidades

- **Consultar alertas ativos** de movimentos de massa e riscos hidrológicos
- **Listar municípios monitorados** (959 cidades em todo o Brasil)
- **Informações do sistema** de monitoramento
- **Links úteis** para painéis e mapas interativos

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/carmodaniel/cemaden-mcp-server.git
cd cemaden-mcp-server
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure no Claude Desktop

Edite o arquivo de configuração do Claude Desktop:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Adicione esta configuração:

```json
{
  "mcpServers": {
    "cemaden": {
      "command": "python",
      "args": [
        "/caminho/completo/para/cemaden_server.py"
      ]
    }
  }
}
```

**Importante:** Substitua `/caminho/completo/para/` pelo caminho real onde você salvou o projeto.

**Exemplo (Windows):**
```json
"args": ["C:\\Users\\João\\projetos\\cemaden-mcp-server\\cemaden_server.py"]
```

**Exemplo (Mac/Linux):**
```json
"args": ["/home/joao/projetos/cemaden-mcp-server/cemaden_server.py"]
```

### 4. Reinicie o Claude Desktop

Feche e abra novamente o Claude Desktop. Pronto! 🎉

## Como usar

Converse naturalmente com o Claude sobre dados do CEMADEN:

```
Você: Há alertas de deslizamento ativos no Brasil?

Claude: Vou consultar o painel de alertas do CEMADEN...
[Retorna informações sobre alertas ativos]
```

```
Você: Quais cidades do Rio de Janeiro são monitoradas?

Claude: Consultando municípios do RJ...
[Lista: Rio de Janeiro, Niterói, Petrópolis, etc.]
```

## Ferramentas disponíveis

O servidor oferece 4 ferramentas que o Claude pode usar automaticamente:

1. **consultar_painel_alertas** - Acessa alertas ativos
2. **listar_municipios_monitorados** - Lista cidades por estado
3. **info_sistema_monitoramento** - Detalhes do sistema
4. **links_cemaden** - Links úteis organizados

## Melhorias técnicas (v2.0)

### Dados estruturados
- **municipios.json**: Arquivo de dados separado com informações de 15 estados e ~99 municípios monitorados
- Fácil expansão: Basta adicionar novos estados ao JSON

### Otimizações
- **Caching de dados**: Municípios carregados uma única vez na inicialização
- **Type hints robustos**: Tipagem completa com `Dict`, `List`, `Optional`, `Any`
- **Validação melhorada**: Verifica se estado existe, retorna lista de disponíveis em caso de erro
- **Tratamento de erros específico**: Diferencia Timeout de outras falhas de rede

### Exemplo de uso da ferramenta com parâmetros

```python
# Listar todos os municípios
listar_municipios_monitorados()

# Listar apenas municípios de um estado
listar_municipios_monitorados(estado="SP")
```

Resposta com estado inválido:
```json
{
  "sucesso": false,
  "erro": "Estado 'XX' não encontrado",
  "estados_disponiveis": ["SP", "RJ", "MG", ...],
  "nota": "Use a sigla do estado (ex: SP, RJ, MG)"
}
```

## Requisitos

- Python 3.10 ou superior
- Claude Desktop instalado
- Conexão com a internet

## Estrutura do projeto

```
cemaden-mcp-server/
├── cemaden_server.py       # Servidor principal MCP
├── municipios.json        # Dados de municípios por estado
├── requirements.txt        # Dependências Python
├── README.md              # Esta documentação
└── LICENSE.txt            # Licença do projeto
```

## Solução de problemas

**O servidor não aparece no Claude Desktop?**
- Verifique se o caminho em `claude_desktop_config.json` está correto
- Teste rodar manualmente: `python cemaden_server.py`
- Reinicie completamente o Claude Desktop

**Erro "Module not found"?**
- Instale as dependências: `pip install -r requirements.txt`

**No Windows, "python não é reconhecido"?**
- Use o caminho completo do Python no config:
  ```json
  "command": "C:\\Python311\\python.exe"
  ```

**Quer ver o log de execução?**
- O servidor cria arquivo `cemaden_mcp_debug.log` com todas as operações
- Útil para debugging de questões com a integração

## Sobre o CEMADEN

O CEMADEN é o Centro Nacional de Monitoramento e Alertas de Desastres Naturais, vinculado ao Ministério da Ciência, Tecnologia e Inovação. Monitora 959 municípios brasileiros vulneráveis a desastres naturais.

**Links oficiais:**
- Site: http://www.cemaden.gov.br
- Painel de Alertas: https://painelalertas.cemaden.gov.br/
- Mapa Interativo: https://mapainterativo.cemaden.gov.br/

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Melhorar a documentação
- Enviar pull requests

### Expandir dados de municípios

Para adicionar mais estados ou municípios:

1. Edite `municipios.json` e adicione a sigla do estado com sua lista de cidades:
```json
{
  "DF": ["Brasília"],
  "GO": ["Goiânia", "Anápolis"],
  "MG": ["Belo Horizonte", ...],
  "XX": ["Cidade1", "Cidade2"]  // Novo estado
}
```

2. O servidor recarrega automaticamente após reiniciar

Os dados seguem fonte oficial do CEMADEN (959 municípios monitorados em todo Brasil)

## Licença

MIT License - use livremente!

