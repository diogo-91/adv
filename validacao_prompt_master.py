"""
VALIDAÇÃO PROMPT MASTER
Sistema de validação especializado para petições geradas com o prompt master
Verifica conformidade com os padrões de excelência técnica
"""

import re
from typing import Dict, List, Tuple
from docx import Document
import io


def validar_extensao(texto: str) -> Tuple[bool, str, int]:
    """
    Valida se o texto está entre 12-18 páginas
    
    Args:
        texto: Texto da petição
        
    Returns:
        (válido, mensagem, páginas_estimadas)
    """
    # Estimativa: ~3000 caracteres por página (Times New Roman 12, espaçamento 1.5)
    caracteres = len(texto)
    paginas_estimadas = caracteres / 3000
    
    if 12 <= paginas_estimadas <= 18:
        return True, f"✓ Extensão adequada: ~{paginas_estimadas:.1f} páginas", int(paginas_estimadas)
    elif paginas_estimadas < 12:
        return False, f"✗ Petição muito curta: ~{paginas_estimadas:.1f} páginas (mínimo 12)", int(paginas_estimadas)
    else:
        return False, f"✗ Petição muito longa: ~{paginas_estimadas:.1f} páginas (máximo 18)", int(paginas_estimadas)


def validar_estrutura_completa(texto: str) -> Tuple[bool, List[str], List[str]]:
    """
    Valida se todas as seções obrigatórias estão presentes
    
    Returns:
        (válido, seções_presentes, seções_faltantes)
    """
    secoes_obrigatorias = {
        'VOCATIVO': r'EXCELENT[IÍ]SSIM[OA]',
        'PRELIMINARES': r'(I\.|1\.)\s*(PRELIMINAR|DA COMPET[EÊ]NCIA)',
        'DOS_FATOS': r'(II\.|DOS FATOS)',
        'DO_MERITO': r'(III\.|DO M[ÉE]RITO|DO DIREITO)',
        'DOS_PEDIDOS': r'(IV\.|DOS PEDIDOS)',
        'ENCERRAMENTO': r'Termos em que',
        'DATA': r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}',
        'ASSINATURA': r'OAB'
    }
    
    presentes = []
    faltantes = []
    
    for secao, padrao in secoes_obrigatorias.items():
        if re.search(padrao, texto, re.IGNORECASE):
            presentes.append(secao)
        else:
            faltantes.append(secao)
    
    valido = len(faltantes) == 0
    return valido, presentes, faltantes


def validar_jurisprudencia(texto: str) -> Tuple[bool, str, int]:
    """
    Valida jurisprudências: máximo 5, formato resumido
    
    Returns:
        (válido, mensagem, quantidade)
    """
    # Padrões para identificar jurisprudências
    padroes = [
        r'\(TST\s*-',
        r'\(TRT\s*-',
        r'\(STF\s*-',
        r'\(STJ\s*-',
        r'Relator:',
        r'EMENTA:'
    ]
    
    count = 0
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.IGNORECASE)
        count = max(count, len(matches))
    
    # Verificar se há ementas completas (muito longas)
    ementas_completas = re.findall(r'EMENTA:.*?(?=\n\n|\Z)', texto, re.DOTALL | re.IGNORECASE)
    tem_ementas_longas = any(len(ementa) > 500 for ementa in ementas_completas)
    
    if count == 0:
        return False, "✗ Nenhuma jurisprudência encontrada", 0
    elif count > 5:
        return False, f"✗ Excesso de jurisprudências: {count} (máximo 5)", count
    elif tem_ementas_longas:
        return False, f"⚠ Jurisprudências muito longas (devem ser resumidas)", count
    else:
        return True, f"✓ Jurisprudências adequadas: {count}", count


def validar_calculos(texto: str) -> Tuple[bool, List[str]]:
    """
    Valida se valores estão arredondados (sem centavos)
    
    Returns:
        (válido, lista_de_problemas)
    """
    # Procurar valores monetários
    valores = re.findall(r'R\$\s*[\d.]+,\d{2}', texto)
    
    problemas = []
    for valor in valores:
        # Extrair centavos
        centavos = valor.split(',')[1]
        if centavos != '00':
            problemas.append(f"Valor não arredondado: {valor}")
    
    if len(problemas) > 5:
        # Mostrar apenas os primeiros 5
        problemas = problemas[:5] + [f"... e mais {len(problemas) - 5} valores"]
    
    valido = len(problemas) == 0
    return valido, problemas


def validar_preliminares(texto: str) -> Tuple[bool, str]:
    """
    Valida se preliminares não excedem 2-3 páginas
    
    Returns:
        (válido, mensagem)
    """
    # Extrair seção de preliminares
    match = re.search(r'(I\.|PRELIMINAR).*?(?=II\.|DOS FATOS)', texto, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return True, "Seção de preliminares não encontrada (pode ser opcional)"
    
    preliminares = match.group(0)
    caracteres = len(preliminares)
    paginas = caracteres / 3000
    
    if paginas <= 3:
        return True, f"✓ Preliminares adequadas: ~{paginas:.1f} páginas"
    else:
        return False, f"✗ Preliminares muito longas: ~{paginas:.1f} páginas (máximo 3)"


def validar_fatos(texto: str) -> Tuple[bool, str, int]:
    """
    Valida seção DOS FATOS: 3-4 páginas, máximo 30 parágrafos
    
    Returns:
        (válido, mensagem, num_paragrafos)
    """
    # Extrair seção DOS FATOS
    match = re.search(r'(II\.|DOS FATOS).*?(?=III\.|DO M[ÉE]RITO|DO DIREITO)', texto, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return False, "✗ Seção DOS FATOS não encontrada", 0
    
    fatos = match.group(0)
    caracteres = len(fatos)
    paginas = caracteres / 3000
    
    # Contar parágrafos numerados
    paragrafos = re.findall(r'^\d+\.\s', fatos, re.MULTILINE)
    num_paragrafos = len(paragrafos)
    
    problemas = []
    if paginas < 3:
        problemas.append(f"muito curta (~{paginas:.1f} páginas, mínimo 3)")
    elif paginas > 4:
        problemas.append(f"muito longa (~{paginas:.1f} páginas, máximo 4)")
    
    if num_paragrafos > 30:
        problemas.append(f"muitos parágrafos ({num_paragrafos}, máximo 30)")
    
    if problemas:
        return False, f"✗ DOS FATOS: {', '.join(problemas)}", num_paragrafos
    else:
        return True, f"✓ DOS FATOS adequada: ~{paginas:.1f} páginas, {num_paragrafos} parágrafos", num_paragrafos


def validar_merito(texto: str) -> Tuple[bool, str]:
    """
    Valida seção DO MÉRITO: 6-8 páginas
    
    Returns:
        (válido, mensagem)
    """
    # Extrair seção DO MÉRITO
    match = re.search(r'(III\.|DO M[ÉE]RITO|DO DIREITO).*?(?=IV\.|DOS PEDIDOS)', texto, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return False, "✗ Seção DO MÉRITO não encontrada"
    
    merito = match.group(0)
    caracteres = len(merito)
    paginas = caracteres / 3000
    
    if 6 <= paginas <= 8:
        return True, f"✓ DO MÉRITO adequado: ~{paginas:.1f} páginas"
    elif paginas < 6:
        return False, f"✗ DO MÉRITO muito curto: ~{paginas:.1f} páginas (mínimo 6)"
    else:
        return False, f"✗ DO MÉRITO muito longo: ~{paginas:.1f} páginas (máximo 8)"


def validar_pedidos(texto: str) -> Tuple[bool, str]:
    """
    Valida seção DOS PEDIDOS: 2-3 páginas
    
    Returns:
        (válido, mensagem)
    """
    # Extrair seção DOS PEDIDOS
    match = re.search(r'(IV\.|DOS PEDIDOS).*?(?=Termos em que|$)', texto, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return False, "✗ Seção DOS PEDIDOS não encontrada"
    
    pedidos = match.group(0)
    caracteres = len(pedidos)
    paginas = caracteres / 3000
    
    if 2 <= paginas <= 3:
        return True, f"✓ DOS PEDIDOS adequados: ~{paginas:.1f} páginas"
    elif paginas < 2:
        return False, f"✗ DOS PEDIDOS muito curtos: ~{paginas:.1f} páginas (mínimo 2)"
    else:
        return False, f"✗ DOS PEDIDOS muito longos: ~{paginas:.1f} páginas (máximo 3)"


def gerar_relatorio_validacao_master(texto: str) -> Dict:
    """
    Gera relatório completo de validação do prompt master
    
    Args:
        texto: Texto da petição
        
    Returns:
        Dicionário com resultados da validação
    """
    relatorio = {
        'aprovado': True,
        'score': 100,
        'validacoes': {},
        'problemas': [],
        'avisos': []
    }
    
    # 1. Validar extensão
    valido, msg, paginas = validar_extensao(texto)
    relatorio['validacoes']['extensao'] = {'valido': valido, 'mensagem': msg, 'paginas': paginas}
    if not valido:
        relatorio['aprovado'] = False
        relatorio['score'] -= 15
        relatorio['problemas'].append(msg)
    
    # 2. Validar estrutura
    valido, presentes, faltantes = validar_estrutura_completa(texto)
    relatorio['validacoes']['estrutura'] = {
        'valido': valido,
        'presentes': presentes,
        'faltantes': faltantes
    }
    if not valido:
        relatorio['aprovado'] = False
        relatorio['score'] -= len(faltantes) * 5
        relatorio['problemas'].append(f"Seções faltantes: {', '.join(faltantes)}")
    
    # 3. Validar jurisprudência
    valido, msg, count = validar_jurisprudencia(texto)
    relatorio['validacoes']['jurisprudencia'] = {'valido': valido, 'mensagem': msg, 'quantidade': count}
    if not valido:
        if count == 0:
            relatorio['score'] -= 10
            relatorio['avisos'].append(msg)
        else:
            relatorio['score'] -= 5
            relatorio['avisos'].append(msg)
    
    # 4. Validar cálculos
    valido, problemas = validar_calculos(texto)
    relatorio['validacoes']['calculos'] = {'valido': valido, 'problemas': problemas}
    if not valido:
        relatorio['score'] -= min(len(problemas), 10)
        relatorio['avisos'].append(f"Valores não arredondados encontrados ({len(problemas)})")
    
    # 5. Validar preliminares
    valido, msg = validar_preliminares(texto)
    relatorio['validacoes']['preliminares'] = {'valido': valido, 'mensagem': msg}
    if not valido:
        relatorio['score'] -= 5
        relatorio['avisos'].append(msg)
    
    # 6. Validar DOS FATOS
    valido, msg, paragrafos = validar_fatos(texto)
    relatorio['validacoes']['fatos'] = {'valido': valido, 'mensagem': msg, 'paragrafos': paragrafos}
    if not valido:
        relatorio['aprovado'] = False
        relatorio['score'] -= 10
        relatorio['problemas'].append(msg)
    
    # 7. Validar DO MÉRITO
    valido, msg = validar_merito(texto)
    relatorio['validacoes']['merito'] = {'valido': valido, 'mensagem': msg}
    if not valido:
        relatorio['aprovado'] = False
        relatorio['score'] -= 10
        relatorio['problemas'].append(msg)
    
    # 8. Validar DOS PEDIDOS
    valido, msg = validar_pedidos(texto)
    relatorio['validacoes']['pedidos'] = {'valido': valido, 'mensagem': msg}
    if not valido:
        relatorio['aprovado'] = False
        relatorio['score'] -= 10
        relatorio['problemas'].append(msg)
    
    # Score mínimo 0
    relatorio['score'] = max(0, relatorio['score'])
    
    # Determinar status final
    if relatorio['score'] >= 90:
        relatorio['status'] = 'EXCELENTE'
        relatorio['emoji'] = '🏆'
    elif relatorio['score'] >= 80:
        relatorio['status'] = 'MUITO BOM'
        relatorio['emoji'] = '⭐'
    elif relatorio['score'] >= 70:
        relatorio['status'] = 'BOM'
        relatorio['emoji'] = '✅'
    else:
        relatorio['status'] = 'PRECISA MELHORAR'
        relatorio['emoji'] = '📝'
        relatorio['aprovado'] = False
    
    return relatorio


def imprimir_relatorio_validacao(relatorio: Dict):
    """Imprime relatório de validação formatado"""
    print("\n" + "="*80)
    print(f"RELATÓRIO DE VALIDAÇÃO - PROMPT MASTER")
    print("="*80)
    print(f"\nStatus: {relatorio['emoji']} {relatorio['status']}")
    print(f"Score: {relatorio['score']}/100")
    print(f"Aprovado: {'✓ SIM' if relatorio['aprovado'] else '✗ NÃO'}")
    
    if relatorio.get('validacoes', {}).get('extensao'):
        ext = relatorio['validacoes']['extensao']
        print(f"\nExtensão: ~{ext.get('paginas', 0)} páginas")
    
    if relatorio['problemas']:
        print("\n🔴 PROBLEMAS CRÍTICOS:")
        for problema in relatorio['problemas']:
            print(f"  - {problema}")
    
    if relatorio['avisos']:
        print("\n⚠️  AVISOS:")
        for aviso in relatorio['avisos']:
            print(f"  - {aviso}")
    
    print("\n" + "="*80)
