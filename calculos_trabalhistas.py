"""
Sistema de Cálculos Trabalhistas
Funções para calcular verbas trabalhistas com precisão
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import locale

# Configurar locale para formatação de valores
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

def formatar_valor_extenso(valor):
    """
    Formata valor numérico para extenso em português
    Simplificado para valores até 999.999,99
    """
    if valor == 0:
        return "zero reais"
    
    # Separar parte inteira e decimal
    inteiro = int(valor)
    decimal = int(round((valor - inteiro) * 100))
    
    # Unidades, dezenas e centenas
    unidades = ['', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove']
    dezenas = ['', '', 'vinte', 'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta', 'oitenta', 'noventa']
    especiais = ['dez', 'onze', 'doze', 'treze', 'quatorze', 'quinze', 'dezesseis', 'dezessete', 'dezoito', 'dezenove']
    centenas = ['', 'cento', 'duzentos', 'trezentos', 'quatrocentos', 'quinhentos', 'seiscentos', 'setecentos', 'oitocentos', 'novecentos']
    
    def numero_por_extenso(n):
        if n == 0:
            return ''
        elif n == 100:
            return 'cem'
        elif n < 10:
            return unidades[n]
        elif n < 20:
            return especiais[n - 10]
        elif n < 100:
            d = n // 10
            u = n % 10
            return dezenas[d] + (' e ' + unidades[u] if u > 0 else '')
        else:
            c = n // 100
            resto = n % 100
            return centenas[c] + (' e ' + numero_por_extenso(resto) if resto > 0 else '')
    
    # Processar milhares
    if inteiro >= 1000:
        milhares = inteiro // 1000
        centenas_resto = inteiro % 1000
        
        if milhares == 1:
            texto_inteiro = 'mil'
        else:
            texto_inteiro = numero_por_extenso(milhares) + ' mil'
        
        if centenas_resto > 0:
            texto_inteiro += ' e ' + numero_por_extenso(centenas_resto)
    else:
        texto_inteiro = numero_por_extenso(inteiro)
    
    # Adicionar "reais"
    if inteiro == 1:
        texto_inteiro += ' real'
    else:
        texto_inteiro += ' reais'
    
    # Processar centavos
    if decimal > 0:
        texto_decimal = numero_por_extenso(decimal)
        if decimal == 1:
            texto_decimal += ' centavo'
        else:
            texto_decimal += ' centavos'
        return texto_inteiro + ' e ' + texto_decimal
    
    return texto_inteiro

def formatar_valor(valor, incluir_extenso=True):
    """
    Formata valor monetário com extenso
    Exemplo: R$ 1.500,00 (um mil e quinhentos reais)
    """
    valor_formatado = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    if incluir_extenso:
        extenso = formatar_valor_extenso(valor)
        return f"{valor_formatado} ({extenso})"
    
    return valor_formatado

def calcular_13_salario(salario_mensal, meses_trabalhados, proporcional=True):
    """
    Calcula 13º salário
    
    Args:
        salario_mensal: Salário mensal do trabalhador
        meses_trabalhados: Número de meses trabalhados no ano
        proporcional: Se True, calcula proporcional aos meses
    
    Returns:
        dict com valor e detalhamento
    """
    if proporcional:
        valor = (salario_mensal / 12) * meses_trabalhados
        formula = f"R$ {salario_mensal:,.2f} ÷ 12 × {meses_trabalhados} meses"
    else:
        valor = salario_mensal
        formula = f"R$ {salario_mensal:,.2f} (integral)"
    
    return {
        'valor': valor,
        'formula': formula,
        'formatado': formatar_valor(valor),
        'descricao': '13º salário proporcional' if proporcional else '13º salário integral'
    }

def calcular_ferias(salario_mensal, periodo_aquisitivo_meses, vencidas=0, proporcionais_meses=0):
    """
    Calcula férias vencidas e proporcionais com 1/3 constitucional
    
    Args:
        salario_mensal: Salário mensal
        periodo_aquisitivo_meses: Meses do período aquisitivo (12 para completo)
        vencidas: Número de períodos de férias vencidas
        proporcionais_meses: Meses para cálculo de férias proporcionais
    
    Returns:
        dict com valores discriminados
    """
    resultado = {
        'ferias_vencidas': 0,
        'terco_vencidas': 0,
        'ferias_proporcionais': 0,
        'terco_proporcionais': 0,
        'total': 0,
        'detalhamento': []
    }
    
    # Férias vencidas
    if vencidas > 0:
        valor_ferias_vencidas = salario_mensal * vencidas
        valor_terco_vencidas = (salario_mensal / 3) * vencidas
        
        resultado['ferias_vencidas'] = valor_ferias_vencidas
        resultado['terco_vencidas'] = valor_terco_vencidas
        
        resultado['detalhamento'].append({
            'item': f'Férias vencidas ({vencidas} período(s))',
            'formula': f'R$ {salario_mensal:,.2f} × {vencidas}',
            'valor': valor_ferias_vencidas,
            'formatado': formatar_valor(valor_ferias_vencidas)
        })
        
        resultado['detalhamento'].append({
            'item': f'1/3 constitucional sobre férias vencidas',
            'formula': f'R$ {salario_mensal:,.2f} ÷ 3 × {vencidas}',
            'valor': valor_terco_vencidas,
            'formatado': formatar_valor(valor_terco_vencidas)
        })
    
    # Férias proporcionais
    if proporcionais_meses > 0:
        valor_ferias_prop = (salario_mensal / 12) * proporcionais_meses
        valor_terco_prop = valor_ferias_prop / 3
        
        resultado['ferias_proporcionais'] = valor_ferias_prop
        resultado['terco_proporcionais'] = valor_terco_prop
        
        resultado['detalhamento'].append({
            'item': f'Férias proporcionais ({proporcionais_meses} meses)',
            'formula': f'R$ {salario_mensal:,.2f} ÷ 12 × {proporcionais_meses}',
            'valor': valor_ferias_prop,
            'formatado': formatar_valor(valor_ferias_prop)
        })
        
        resultado['detalhamento'].append({
            'item': '1/3 constitucional sobre férias proporcionais',
            'formula': f'{formatar_valor(valor_ferias_prop, False)} ÷ 3',
            'valor': valor_terco_prop,
            'formatado': formatar_valor(valor_terco_prop)
        })
    
    resultado['total'] = (resultado['ferias_vencidas'] + resultado['terco_vencidas'] + 
                          resultado['ferias_proporcionais'] + resultado['terco_proporcionais'])
    
    return resultado

def calcular_fgts(salario_mensal, meses_trabalhados, incluir_multa_40=True):
    """
    Calcula FGTS com multa de 40%
    
    Args:
        salario_mensal: Salário mensal
        meses_trabalhados: Número de meses trabalhados
        incluir_multa_40: Se True, inclui multa de 40%
    
    Returns:
        dict com valores discriminados
    """
    # FGTS = 8% do salário por mês
    valor_fgts = salario_mensal * 0.08 * meses_trabalhados
    
    resultado = {
        'fgts': valor_fgts,
        'multa_40': 0,
        'total': valor_fgts,
        'detalhamento': []
    }
    
    resultado['detalhamento'].append({
        'item': 'FGTS (8% sobre salário)',
        'formula': f'R$ {salario_mensal:,.2f} × 8% × {meses_trabalhados} meses',
        'valor': valor_fgts,
        'formatado': formatar_valor(valor_fgts)
    })
    
    if incluir_multa_40:
        multa = valor_fgts * 0.40
        resultado['multa_40'] = multa
        resultado['total'] = valor_fgts + multa
        
        resultado['detalhamento'].append({
            'item': 'Multa de 40% sobre FGTS',
            'formula': f'{formatar_valor(valor_fgts, False)} × 40%',
            'valor': multa,
            'formatado': formatar_valor(multa)
        })
    
    return resultado

def calcular_horas_extras_reflexos(salario_mensal, horas_mes, percentual_adicional=50, meses_trabalhados=12):
    """
    Calcula horas extras com TODOS os 7 reflexos obrigatórios
    
    Args:
        salario_mensal: Salário mensal
        horas_mes: Horas extras por mês
        percentual_adicional: Percentual do adicional (50% ou 100%)
        meses_trabalhados: Número de meses com horas extras
    
    Returns:
        dict com todos os reflexos discriminados
    """
    # Valor da hora normal (220 horas/mês)
    valor_hora_normal = salario_mensal / 220
    
    # Valor da hora extra
    valor_hora_extra = valor_hora_normal * (1 + percentual_adicional/100)
    
    # Total de horas extras
    total_horas = horas_mes * meses_trabalhados
    
    # 1. Horas extras
    valor_he = valor_hora_extra * total_horas
    
    # 2. DSR sobre horas extras (aproximadamente 1/6)
    valor_dsr = valor_he / 6
    
    # 3. Reflexos em 13º salário
    media_he_mensal = valor_he / meses_trabalhados
    reflexo_13 = media_he_mensal
    
    # 4. Reflexos em férias + 1/3
    reflexo_ferias = media_he_mensal
    reflexo_terco_ferias = reflexo_ferias / 3
    
    # 5. Reflexos em FGTS + 40%
    reflexo_fgts = (valor_he + valor_dsr) * 0.08
    reflexo_multa_fgts = reflexo_fgts * 0.40
    
    # 6. Reflexos em aviso prévio
    reflexo_aviso = media_he_mensal
    
    resultado = {
        'total': 0,
        'reflexos': [
            {
                'numero': 1,
                'nome': f'Horas Extras ({percentual_adicional}%)',
                'formula': f'{total_horas}h × R$ {valor_hora_extra:.2f}',
                'valor': valor_he,
                'formatado': formatar_valor(valor_he)
            },
            {
                'numero': 2,
                'nome': 'DSR sobre Horas Extras',
                'formula': f'{formatar_valor(valor_he, False)} ÷ 6',
                'valor': valor_dsr,
                'formatado': formatar_valor(valor_dsr)
            },
            {
                'numero': 3,
                'nome': 'Reflexos em 13º Salário',
                'formula': f'Média mensal de HE',
                'valor': reflexo_13,
                'formatado': formatar_valor(reflexo_13)
            },
            {
                'numero': 4,
                'nome': 'Reflexos em Férias',
                'formula': f'Média mensal de HE',
                'valor': reflexo_ferias,
                'formatado': formatar_valor(reflexo_ferias)
            },
            {
                'numero': 4,
                'nome': 'Reflexos em 1/3 de Férias',
                'formula': f'{formatar_valor(reflexo_ferias, False)} ÷ 3',
                'valor': reflexo_terco_ferias,
                'formatado': formatar_valor(reflexo_terco_ferias)
            },
            {
                'numero': 5,
                'nome': 'Reflexos em FGTS',
                'formula': f'(HE + DSR) × 8%',
                'valor': reflexo_fgts,
                'formatado': formatar_valor(reflexo_fgts)
            },
            {
                'numero': 5,
                'nome': 'Reflexos em Multa 40% FGTS',
                'formula': f'{formatar_valor(reflexo_fgts, False)} × 40%',
                'valor': reflexo_multa_fgts,
                'formatado': formatar_valor(reflexo_multa_fgts)
            },
            {
                'numero': 6,
                'nome': 'Reflexos em Aviso Prévio',
                'formula': f'Média mensal de HE',
                'valor': reflexo_aviso,
                'formatado': formatar_valor(reflexo_aviso)
            }
        ]
    }
    
    # Calcular total
    resultado['total'] = sum(r['valor'] for r in resultado['reflexos'])
    resultado['total_formatado'] = formatar_valor(resultado['total'])
    
    return resultado

def calcular_multa_477(salario_mensal):
    """
    Calcula multa do art. 477, §8º da CLT (1 salário)
    """
    return {
        'valor': salario_mensal,
        'formatado': formatar_valor(salario_mensal),
        'descricao': 'Multa do art. 477, §8º da CLT',
        'fundamento': 'Atraso no pagamento das verbas rescisórias'
    }

def calcular_multa_467(valor_verbas_incontroversas):
    """
    Calcula multa do art. 467 da CLT (50% sobre verbas incontroversas)
    """
    multa = valor_verbas_incontroversas * 0.50
    
    return {
        'valor': multa,
        'formatado': formatar_valor(multa),
        'formula': f'{formatar_valor(valor_verbas_incontroversas, False)} × 50%',
        'descricao': 'Multa do art. 467 da CLT',
        'fundamento': 'Não pagamento de verbas rescisórias incontroversas'
    }

def gerar_tabela_calculos(calculos_dict):
    """
    Gera uma tabela formatada com os cálculos para inserção na petição
    
    Args:
        calculos_dict: Dicionário com os cálculos realizados
    
    Returns:
        String formatada para inserção na petição
    """
    texto = "\n\nDISCRIMINAÇÃO DOS VALORES:\n\n"
    
    total_geral = 0
    
    for categoria, dados in calculos_dict.items():
        if isinstance(dados, dict) and 'detalhamento' in dados:
            texto += f"\n{categoria.upper()}:\n"
            for item in dados['detalhamento']:
                texto += f"  • {item['item']}: {item['formatado']}\n"
                if 'formula' in item:
                    texto += f"    Cálculo: {item['formula']}\n"
                total_geral += item['valor']
        elif isinstance(dados, dict) and 'reflexos' in dados:
            texto += f"\n{categoria.upper()}:\n"
            for reflexo in dados['reflexos']:
                texto += f"  {reflexo['numero']}. {reflexo['nome']}: {reflexo['formatado']}\n"
                texto += f"     Cálculo: {reflexo['formula']}\n"
            total_geral += dados['total']
    
    texto += f"\n{'='*60}\n"
    texto += f"TOTAL GERAL: {formatar_valor(total_geral)}\n"
    texto += f"{'='*60}\n"
    
    return texto
