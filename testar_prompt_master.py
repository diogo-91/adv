"""
TESTE DO PROMPT MASTER
Script para testar a geração de petições com o Prompt Master ativado
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(__file__))

from main_v10_fase3 import (
    autenticar_google_drive,
    gerar_peticao_com_claude,
    salvar_peticao_docx
)

def testar_prompt_master():
    """
    Testa a geração de uma petição usando o Prompt Master
    """
    print("="*80)
    print("TESTE DO PROMPT MASTER")
    print("="*80)
    print()
    
    # Autenticar Google Drive
    print("1. Autenticando Google Drive...")
    service = autenticar_google_drive()
    print("   ✅ Autenticado")
    print()
    
    # Informações do cliente (exemplo)
    cliente_info = {
        'cliente_nome': 'João da Silva',
        'tipo_processo': 'RECONHECIMENTO_VINCULO',
        'pasta_id': 'ID_DA_PASTA_DO_CLIENTE'  # Substituir pelo ID real
    }
    
    # Documentos (exemplo simplificado)
    documentos_completos = [
        {
            'tipo': 'DOCUMENTO_PESSOAL',
            'nome': 'RG.pdf',
            'conteudo': b'',
            'texto': 'RG: 12.345.678-9\nCPF: 123.456.789-00'
        },
        {
            'tipo': 'TRANSCRICAO',
            'nome': 'Entrevista.docx',
            'conteudo': b'',
            'texto': 'Cliente trabalhou de 2020 a 2023 sem registro em CTPS...'
        }
    ]
    
    print("2. Informações do teste:")
    print(f"   Cliente: {cliente_info['cliente_nome']}")
    print(f"   Tipo: {cliente_info['tipo_processo']}")
    print(f"   Documentos: {len(documentos_completos)}")
    print()
    
    # Opção de escolha
    print("3. Escolha o modo de geração:")
    print("   [1] Modo Padrão (rápido, 5-10 páginas)")
    print("   [2] Modo Prompt Master (alto nível, 12-18 páginas)")
    print()
    
    escolha = input("   Digite 1 ou 2: ").strip()
    usar_prompt_master = (escolha == '2')
    
    print()
    if usar_prompt_master:
        print("   ✨ MODO PROMPT MASTER ATIVADO")
        print("   - Petição de 12-18 páginas")
        print("   - Padrão de advogado sênior")
        print("   - Times New Roman 12pt")
        print("   - Validação rigorosa")
    else:
        print("   📝 Modo Padrão ativado")
    print()
    
    # Gerar petição
    print("4. Gerando petição...")
    print("   (Isso pode levar 2-3 minutos no modo Prompt Master)")
    print()
    
    try:
        peticao_texto = gerar_peticao_com_claude(
            service=service,
            cliente_info=cliente_info,
            documentos_completos=documentos_completos,
            tipo_processo=cliente_info['tipo_processo'],
            cronologia_fatos=None,
            resumo_video=None,
            procuracao=None,
            usar_prompt_master=usar_prompt_master  # ← PARÂMETRO CHAVE
        )
        
        if peticao_texto:
            print("   ✅ Petição gerada com sucesso!")
            print(f"   Tamanho: {len(peticao_texto)} caracteres")
            print(f"   Páginas estimadas: {len(peticao_texto) / 3000:.1f}")
            print()
            
            # Salvar localmente para visualização
            with open('peticao_teste.txt', 'w', encoding='utf-8') as f:
                f.write(peticao_texto)
            
            print("   💾 Salvo em: peticao_teste.txt")
            print()
            
            if usar_prompt_master:
                print("   📊 Validação Prompt Master executada")
                print("   Verifique os logs acima para o score e status")
            
        else:
            print("   ❌ Erro ao gerar petição")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("="*80)
    print("FIM DO TESTE")
    print("="*80)

if __name__ == '__main__':
    testar_prompt_master()
