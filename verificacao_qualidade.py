"""
Sistema de Verificação de Qualidade de Petições
Valida se a petição atende aos padrões profissionais
"""

import re

def verificar_qualidade_peticao(peticao_texto, tipo_processo):
    """
    Verifica se a petição atende aos padrões de qualidade
    
    Args:
        peticao_texto: Texto completo da petição
        tipo_processo: RECONHECIMENTO_VINCULO, ACAO_ACIDENTARIA, DIFERENCAS_CONTRATUAIS
    
    Returns:
        dict com resultado da verificação
    """
    resultado = {
        'aprovada': True,
        'score': 100,
        'problemas': [],
        'avisos': [],
        'pontos_fortes': [],
        'detalhes': {}
    }
    
    # 1. Verificar numeração de parágrafos
    tem_numeracao = verificar_numeracao_paragrafos(peticao_texto)
    resultado['detalhes']['numeracao'] = tem_numeracao
    
    if tem_numeracao['presente']:
        resultado['pontos_fortes'].append(f"Numeração sequencial presente ({tem_numeracao['quantidade']} parágrafos)")
    else:
        resultado['problemas'].append("Falta numeração sequencial de parágrafos")
        resultado['score'] -= 10
    
    # 2. Verificar preliminares
    tem_preliminares = verificar_preliminares(peticao_texto)
    resultado['detalhes']['preliminares'] = tem_preliminares
    
    if tem_preliminares['competencia']:
        resultado['pontos_fortes'].append("Preliminar de competência territorial presente")
    else:
        resultado['avisos'].append("Recomenda-se incluir preliminar de competência territorial")
        resultado['score'] -= 3
    
    # 3. Verificar jurisprudências
    juris = verificar_jurisprudencias(peticao_texto)
    resultado['detalhes']['jurisprudencias'] = juris
    
    if juris['quantidade'] >= 2:
        resultado['pontos_fortes'].append(f"Fundamentação jurisprudencial robusta ({juris['quantidade']} citações)")
    elif juris['quantidade'] == 1:
        resultado['avisos'].append("Apenas 1 jurisprudência encontrada, recomenda-se incluir mais")
        resultado['score'] -= 5
    else:
        resultado['problemas'].append("Falta fundamentação jurisprudencial")
        resultado['score'] -= 15
    
    # 4. Verificar estrutura de seções
    secoes = verificar_secoes(peticao_texto)
    resultado['detalhes']['secoes'] = secoes
    
    secoes_obrigatorias = ['DOS FATOS', 'DO MÉRITO', 'DOS PEDIDOS']
    for secao in secoes_obrigatorias:
        if secao in secoes['presentes']:
            resultado['pontos_fortes'].append(f"Seção '{secao}' presente")
        else:
            resultado['problemas'].append(f"Falta seção obrigatória: {secao}")
            resultado['score'] -= 10
    
    # 5. Verificar capítulos do mérito
    capitulos = verificar_capitulos_merito(peticao_texto, tipo_processo)
    resultado['detalhes']['capitulos_merito'] = capitulos
    
    if tipo_processo == 'RECONHECIMENTO_VINCULO':
        if 'RECONHECIMENTO' in capitulos['presentes']:
            resultado['pontos_fortes'].append("Capítulo de reconhecimento de vínculo presente")
        else:
            resultado['problemas'].append("Falta capítulo de reconhecimento de vínculo")
            resultado['score'] -= 15
    
    # 6. Verificar reflexos de horas extras (se aplicável)
    if 'HORAS EXTRAS' in peticao_texto.upper() or 'HE' in peticao_texto:
        reflexos = verificar_reflexos_he(peticao_texto)
        resultado['detalhes']['reflexos_he'] = reflexos
        
        if reflexos['completo']:
            resultado['pontos_fortes'].append(f"Todos os {reflexos['presentes']}/7 reflexos de HE presentes")
        else:
            faltantes = 7 - reflexos['presentes']
            resultado['avisos'].append(f"Faltam {faltantes} reflexos de horas extras")
            resultado['score'] -= (faltantes * 2)
    
    # 7. Verificar valores monetários
    valores = verificar_valores_monetarios(peticao_texto)
    resultado['detalhes']['valores'] = valores
    
    if valores['quantidade'] > 0:
        resultado['pontos_fortes'].append(f"{valores['quantidade']} valores monetários discriminados")
    else:
        resultado['avisos'].append("Nenhum valor monetário discriminado na petição")
        resultado['score'] -= 5
    
    # 8. Verificar fórmula de encerramento
    tem_encerramento = verificar_encerramento(peticao_texto)
    resultado['detalhes']['encerramento'] = tem_encerramento
    
    if tem_encerramento:
        resultado['pontos_fortes'].append("Fórmula de encerramento presente")
    else:
        resultado['problemas'].append("Falta fórmula de encerramento")
        resultado['score'] -= 10
    
    # Determinar aprovação
    resultado['aprovada'] = resultado['score'] >= 70
    
    return resultado

def verificar_numeracao_paragrafos(texto):
    """Verifica se há numeração sequencial de parágrafos"""
    # Procurar padrão "1. ", "2. ", etc.
    padrao = r'^\d+\.\s'
    linhas = texto.split('\n')
    
    paragrafos_numerados = []
    for linha in linhas:
        if re.match(padrao, linha.strip()):
            numero = int(linha.strip().split('.')[0])
            paragrafos_numerados.append(numero)
    
    # Verificar se é sequencial
    sequencial = False
    if len(paragrafos_numerados) >= 3:
        sequencial = all(paragrafos_numerados[i] == paragrafos_numerados[i-1] + 1 
                        for i in range(1, min(5, len(paragrafos_numerados))))
    
    return {
        'presente': len(paragrafos_numerados) >= 3,
        'quantidade': len(paragrafos_numerados),
        'sequencial': sequencial
    }

def verificar_preliminares(texto):
    """Verifica presença de seções preliminares"""
    texto_upper = texto.upper()
    
    return {
        'competencia': 'COMPETÊNCIA' in texto_upper or 'COMPETENCIA' in texto_upper,
        'juizo_digital': 'JUÍZO' in texto_upper and 'DIGITAL' in texto_upper,
        'documentos': 'JUNTADA' in texto_upper and 'DOCUMENTOS' in texto_upper
    }

def verificar_jurisprudencias(texto):
    """Verifica presença e quantidade de jurisprudências"""
    # Procurar padrões de citação jurisprudencial
    padroes = [
        r'\(TST\s*-',
        r'\(TRT-\d+',
        r'Relator:',
        r'Data:\s*\d{2}/\d{2}/\d{4}'
    ]
    
    citacoes = 0
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.IGNORECASE)
        citacoes = max(citacoes, len(matches))
    
    return {
        'quantidade': citacoes,
        'presente': citacoes > 0
    }

def verificar_secoes(texto):
    """Verifica presença de seções principais"""
    texto_upper = texto.upper()
    
    secoes_possiveis = [
        'PRELIMINAR',
        'DOS FATOS',
        'DO MÉRITO',
        'DOS PEDIDOS'
    ]
    
    presentes = [s for s in secoes_possiveis if s in texto_upper]
    
    return {
        'presentes': presentes,
        'total': len(presentes)
    }

def verificar_capitulos_merito(texto, tipo_processo):
    """Verifica capítulos específicos do mérito"""
    texto_upper = texto.upper()
    
    capitulos_possiveis = [
        'RECONHECIMENTO',
        'HORAS EXTRAS',
        'ADICIONAL NOTURNO',
        'INSALUBRIDADE',
        'DANOS MORAIS',
        'RESCISÃO INDIRETA',
        'MULTAS'
    ]
    
    presentes = [c for c in capitulos_possiveis if c in texto_upper]
    
    return {
        'presentes': presentes,
        'total': len(presentes)
    }

def verificar_reflexos_he(texto):
    """Verifica se todos os 7 reflexos de HE estão presentes"""
    texto_upper = texto.upper()
    
    reflexos = {
        'DSR': 'DSR' in texto_upper or 'DESCANSO SEMANAL' in texto_upper,
        '13º': '13' in texto_upper or 'DÉCIMO TERCEIRO' in texto_upper,
        'Férias': 'FÉRIAS' in texto_upper or 'FERIAS' in texto_upper,
        'FGTS': 'FGTS' in texto_upper,
        'Aviso': 'AVISO' in texto_upper and 'PRÉVIO' in texto_upper,
        'Noturno': 'NOTURNO' in texto_upper,
        'Adicional HE': 'ADICIONAL' in texto_upper and ('HORA' in texto_upper or 'HE' in texto_upper)
    }
    
    presentes = sum(1 for v in reflexos.values() if v)
    
    return {
        'presentes': presentes,
        'completo': presentes >= 6,  # Pelo menos 6 dos 7
        'detalhes': reflexos
    }

def verificar_valores_monetarios(texto):
    """Verifica presença de valores monetários discriminados"""
    # Procurar padrão R$ X.XXX,XX
    padrao = r'R\$\s*[\d.]+,\d{2}'
    valores = re.findall(padrao, texto)
    
    return {
        'quantidade': len(valores),
        'presente': len(valores) > 0
    }

def verificar_encerramento(texto):
    """Verifica fórmula de encerramento"""
    texto_upper = texto.upper()
    
    formulas = [
        'TERMOS EM QUE' in texto_upper and 'PEDE DEFERIMENTO' in texto_upper,
        'NESTES TERMOS' in texto_upper and 'PEDE DEFERIMENTO' in texto_upper
    ]
    
    return any(formulas)

def gerar_relatorio_verificacao(resultado):
    """
    Gera relatório formatado da verificação
    
    Args:
        resultado: Dict retornado por verificar_qualidade_peticao
    
    Returns:
        String formatada com relatório
    """
    relatorio = "\n" + "="*70 + "\n"
    relatorio += "RELATÓRIO DE VERIFICAÇÃO DE QUALIDADE\n"
    relatorio += "="*70 + "\n\n"
    
    # Status geral
    status = "✅ APROVADA" if resultado['aprovada'] else "❌ REPROVADA"
    relatorio += f"Status: {status}\n"
    relatorio += f"Score: {resultado['score']}/100\n\n"
    
    # Pontos fortes
    if resultado['pontos_fortes']:
        relatorio += "PONTOS FORTES:\n"
        for ponto in resultado['pontos_fortes']:
            relatorio += f"  ✅ {ponto}\n"
        relatorio += "\n"
    
    # Avisos
    if resultado['avisos']:
        relatorio += "AVISOS:\n"
        for aviso in resultado['avisos']:
            relatorio += f"  ⚠️  {aviso}\n"
        relatorio += "\n"
    
    # Problemas
    if resultado['problemas']:
        relatorio += "PROBLEMAS:\n"
        for problema in resultado['problemas']:
            relatorio += f"  ❌ {problema}\n"
        relatorio += "\n"
    
    relatorio += "="*70 + "\n"
    
    return relatorio
