#!/usr/bin/env python3
"""
Script de teste para funções do CEMADEN
Não requer servidor MCP, testa diretamente as funções
"""

import json
import sys
sys.path.insert(0, '.')

from cemaden_server import (
    buscar_info_painel_alertas,
    buscar_municipios_monitorados,
    buscar_info_monitoramento,
    buscar_links_uteis
)

def teste_com_separador(nome_teste):
    """Imprime separador para cada teste"""
    print(f"\n{'='*60}")
    print(f"🧪 {nome_teste}")
    print(f"{'='*60}\n")

# Teste 1: Painel de alertas
teste_com_separador("TESTE 1: Painel de Alertas")
resultado = buscar_info_painel_alertas()
print(json.dumps(resultado, indent=2, ensure_ascii=False))

# Teste 2: Listar todos os municípios
teste_com_separador("TESTE 2: Listar TODOS os municípios")
resultado = buscar_municipios_monitorados()
print(f"Total de estados: {resultado.get('total_estados')}")
print(f"Total de municípios: {resultado.get('total_municipal')}")
print(f"Estados disponíveis: {resultado.get('estados_disponiveis')}\n")

# Teste 3: Listar municípios de SP
teste_com_separador("TESTE 3: Listar municípios de SP")
resultado = buscar_municipios_monitorados("SP")
print(json.dumps(resultado, indent=2, ensure_ascii=False))

# Teste 4: Listar municípios de RJ
teste_com_separador("TESTE 4: Listar municípios de RJ")
resultado = buscar_municipios_monitorados("RJ")
print(json.dumps(resultado, indent=2, ensure_ascii=False))

# Teste 5: Estado inválido (deve retornar erro com lista de válidos)
teste_com_separador("TESTE 5: Estado INVÁLIDO (XX)")
resultado = buscar_municipios_monitorados("XX")
print(json.dumps(resultado, indent=2, ensure_ascii=False))

# Teste 6: Info do sistema
teste_com_separador("TESTE 6: Informações do Sistema")
resultado = buscar_info_monitoramento()
print(json.dumps(resultado, indent=2, ensure_ascii=False))

# Teste 7: Links úteis
teste_com_separador("TESTE 7: Links por categoria")
resultado = buscar_links_uteis("alertas")
print(json.dumps(resultado, indent=2, ensure_ascii=False))

teste_com_separador("TESTE 8: Todos os links")
resultado = buscar_links_uteis()
print(json.dumps(resultado, indent=2, ensure_ascii=False))

print(f"\n{'='*60}")
print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
print(f"{'='*60}\n")
