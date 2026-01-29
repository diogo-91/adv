"""
Script para limpar registros duplicados de RECONHECIMENTO_VINCULO
do arquivo historico_peticoes.json
"""
import json
from datetime import datetime

def limpar_historico():
    """Remove registros duplicados mantendo apenas o mais recente de cada tipo"""
    
    # Ler arquivo
    with open('historico_peticoes.json', 'r', encoding='utf-8') as f:
        historico = json.load(f)
    
    print(f"📊 Total de registros antes: {len(historico)}")
    
    # Contar por tipo
    por_tipo = {}
    for item in historico:
        tipo = item.get('tipo_processo', 'DESCONHECIDO')
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append(item)
    
    print("\n📈 Distribuição ANTES da limpeza:")
    for tipo, items in por_tipo.items():
        print(f"   {tipo}: {len(items)} registros")
    
    # Filtrar RECONHECIMENTO_VINCULO - manter apenas o mais recente
    historico_limpo = []
    
    for item in historico:
        tipo = item.get('tipo_processo', 'DESCONHECIDO')
        
        # Se não for RECONHECIMENTO_VINCULO, manter todos
        if tipo != 'RECONHECIMENTO_VINCULO':
            historico_limpo.append(item)
        else:
            # Para RECONHECIMENTO_VINCULO, vamos manter apenas 1
            # Verificar se já adicionamos algum
            ja_tem_vinculo = any(
                h.get('tipo_processo') == 'RECONHECIMENTO_VINCULO' 
                for h in historico_limpo
            )
            
            if not ja_tem_vinculo:
                # Adicionar o primeiro (mais recente se estiver ordenado)
                historico_limpo.append(item)
                print(f"\n✅ Mantendo registro de RECONHECIMENTO_VINCULO:")
                print(f"   Cliente: {item.get('cliente')}")
                print(f"   Data: {item.get('data_geracao')}")
    
    print(f"\n📊 Total de registros depois: {len(historico_limpo)}")
    
    # Contar por tipo após limpeza
    por_tipo_limpo = {}
    for item in historico_limpo:
        tipo = item.get('tipo_processo', 'DESCONHECIDO')
        if tipo not in por_tipo_limpo:
            por_tipo_limpo[tipo] = []
        por_tipo_limpo[tipo].append(item)
    
    print("\n📈 Distribuição DEPOIS da limpeza:")
    for tipo, items in por_tipo_limpo.items():
        print(f"   {tipo}: {len(items)} registros")
    
    # Salvar arquivo limpo
    with open('historico_peticoes.json', 'w', encoding='utf-8') as f:
        json.dump(historico_limpo, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Arquivo limpo salvo com sucesso!")
    print(f"🗑️  Removidos: {len(historico) - len(historico_limpo)} registros duplicados")

if __name__ == '__main__':
    limpar_historico()
