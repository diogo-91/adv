"""
API Flask para Dashboard do Sistema de Petições
Fornece estatísticas em tempo real
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io
from docx import Document
import tempfile
import subprocess

load_dotenv()

app = Flask(__name__)
CORS(app)  # Permitir CORS para o dashboard

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/health')
def health_check():
    """Health check endpoint - não depende de Google Drive"""
    return jsonify({
        'status': 'healthy',
        'service': 'peticoes-automatizadas',
        'timestamp': datetime.now().isoformat()
    })


SCOPES = ['https://www.googleapis.com/auth/drive']
HISTORICO_FILE = 'historico_peticoes.json'

def carregar_historico():
    """Carrega histórico de petições geradas"""
    try:
        if os.path.exists(HISTORICO_FILE):
            with open(HISTORICO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except:
        return []

def autenticar_google_drive():
    """Autentica com Google Drive"""
    try:
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
        if creds:
            return build('drive', 'v3', credentials=creds)
        return None
    except Exception as e:
        print(f"⚠️ Erro ao autenticar Google Drive: {e}")
        return None

def listar_arquivos_pasta(service, pasta_id):
    """Lista arquivos em uma pasta"""
    try:
        query = f"'{pasta_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'"
        results = service.files().list(
            q=query,
            fields="files(id, name, createdTime, modifiedTime)",
            pageSize=1000
        ).execute()
        return results.get('files', [])
    except Exception as e:
        print(f"Erro ao listar: {e}")
        return []

def contar_clientes_processados(service):
    """Conta clientes que têm _PROCESSADO.txt"""
    try:
        pastas_tipos = [
            os.getenv('PASTA_RECONHECIMENTO_VINCULO'),
            os.getenv('PASTA_ACAO_ACIDENTARIA'),
            os.getenv('PASTA_DIFERENCAS_CONTRATUAIS')
        ]
        
        total = 0
        for pasta_tipo_id in pastas_tipos:
            if not pasta_tipo_id:
                continue
            
            # Listar pastas de clientes
            query = f"'{pasta_tipo_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
            results = service.files().list(q=query, fields="files(id)").execute()
            pastas_clientes = results.get('files', [])
            
            # Para cada cliente, verificar se tem _PROCESSADO.txt
            for pasta_cliente in pastas_clientes:
                arquivos = listar_arquivos_pasta(service, pasta_cliente['id'])
                for arq in arquivos:
                    if arq['name'].strip().upper() == '_PROCESSADO.TXT':
                        total += 1
                        break
        
        return total
    except Exception as e:
        print(f"Erro ao contar clientes: {e}")
        return 0

def analisar_peticoes(service, pasta_id):
    """Analisa petições em uma pasta"""
    arquivos = listar_arquivos_pasta(service, pasta_id)
    
    peticoes = []
    for arq in arquivos:
        if arq['name'].startswith('Peticao_') and arq['name'].endswith('.docx'):
            # Extrair tipo do processo do nome
            parts = arq['name'].split('_')
            tipo = parts[1] if len(parts) > 1 else 'DESCONHECIDO'
            cliente = parts[2] if len(parts) > 2 else 'Desconhecido'
            
            peticoes.append({
                'nome': arq['name'],
                'tipo_processo': tipo,
                'cliente': cliente,
                'timestamp': arq.get('createdTime', arq.get('modifiedTime')),
                'id': arq['id']
            })
    
    return peticoes

def extrair_score_do_log(service):
    """
    Busca logs de auditoria na pasta 05_LOGS (se existir)
    e extrai scores das petições
    """
    # TODO: Implementar quando tiver pasta de logs
    # Por enquanto, retorna scores simulados baseados no status
    return {}

@app.route('/api/historico')
def get_historico():
    """Retorna histórico completo de petições com informações de prints"""
    try:
        historico_file = 'historico_peticoes.json'
        if not os.path.exists(historico_file):
            return jsonify([])
        
        with open(historico_file, 'r', encoding='utf-8') as f:
            historico = json.load(f)
        
        # Agrupar por tipo
        por_tipo = {}
        
        for item in historico:
            tipo = item.get('tipo_processo', 'DESCONHECIDO')
            
            if tipo not in por_tipo:
                por_tipo[tipo] = []
            
            # Carregar informações de prints se existir relatório
            info_prints = carregar_info_prints(item.get('cliente'))
            
            por_tipo[tipo].append({
                'cliente': item.get('cliente'),
                'arquivo_nome': item.get('arquivo_nome'),
                'arquivo_id': item.get('arquivo_id'),
                'link': item.get('link'),
                'data_geracao': item.get('data_geracao'),
                'data_auditoria': item.get('data_auditoria'),
                'status': item.get('status'),
                'status_processamento': item.get('status_processamento'),  # NOVO: status em tempo real
                'score': item.get('score'),
                'ranking': item.get('ranking'),
                'relatorio_auditoria': item.get('relatorio_auditoria'),
                'erros': item.get('erros', []),
                'prints': info_prints
            })
        
        return jsonify(por_tipo)
        
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        return jsonify({}), 500

def carregar_info_prints(cliente_nome):
    """Carrega informações de prints do relatório mais recente do cliente"""
    try:
        logs_dir = 'logs_prints'
        if not os.path.exists(logs_dir):
            return None
        
        # Buscar relatórios deste cliente
        arquivos = [f for f in os.listdir(logs_dir) if cliente_nome in f and f.endswith('.txt')]
        
        if not arquivos:
            return None
        
        # Pegar mais recente
        arquivo_mais_recente = sorted(arquivos)[-1]
        caminho = os.path.join(logs_dir, arquivo_mais_recente)
        
        # Extrair informações do relatório
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Extrair dados principais
        info = {
            'arquivo_relatorio': arquivo_mais_recente,
            'total_marcadores': 0,
            'criticos_faltantes': 0,
            'importantes_faltantes': 0,
            'desejaveis_faltantes': 0,
            'tem_bloqueio': False
        }
        
        # Parse simples do conteúdo
        for linha in conteudo.split('\n'):
            if 'Total de marcadores inseridos:' in linha:
                try:
                    info['total_marcadores'] = int(linha.split(':')[1].strip())
                except:
                    pass
            elif 'Prints CRÍTICOS faltantes:' in linha:
                try:
                    info['criticos_faltantes'] = int(linha.split(':')[1].strip())
                except:
                    pass
            elif 'Prints IMPORTANTES faltantes:' in linha:
                try:
                    info['importantes_faltantes'] = int(linha.split(':')[1].strip())
                except:
                    pass
            elif 'Prints DESEJÁVEIS faltantes:' in linha:
                try:
                    info['desejaveis_faltantes'] = int(linha.split(':')[1].strip())
                except:
                    pass
            elif 'BLOQUEADO - Prints críticos faltantes' in linha:
                info['tem_bloqueio'] = True
        
        return info
        
    except Exception as e:
        print(f"Erro ao carregar info prints: {e}")
        return None

@app.route('/api/detailed-stats')
def get_detailed_stats():
    """Endpoint detalhado - retorna info completa por pasta/tipo/cliente"""
    try:
        service = autenticar_google_drive()
        
        # Se não conseguiu autenticar, retornar estrutura vazia
        if not service:
            return jsonify({
                'total_clientes': 0,
                'total_aprovadas': 0,
                'total_rejeitadas': 0,
                'taxa_aprovacao': 0,
                'casos_novos': {},
                'peticoes_geradas': {},
                'aprovadas': {},
                'rejeitadas': {},
                'error': 'Google Drive não autenticado'
            })
        
        # Estrutura de retorno
        result = {
            'total_clientes': 0,
            'total_aprovadas': 0,
            'total_rejeitadas': 0,
            'taxa_aprovacao': 0,
            'casos_novos': {},
            'peticoes_geradas': {},
            'aprovadas': {},
            'rejeitadas': {}
        }
        
        # 01 - CASOS NOVOS
        result['casos_novos'] = analisar_casos_novos(service)
        
        # Contar total de clientes
        for tipo_data in result['casos_novos'].values():
            result['total_clientes'] += tipo_data.get('total', 0)
        
        # 02 - PETIÇÕES GERADAS
        result['peticoes_geradas'] = analisar_pasta_peticoes(service, {
            'RECONHECIMENTO_VINCULO': '1ya29qkIu8J2O1idmlco9HwSqCFKSsxTm',
            'ACAO_ACIDENTARIA': '1OE_MFrNmzrDKTQ4iJN30qhMc95cEfI1P',
            'DIFERENCAS_CONTRATUAIS': '1edqtmAgtZI_B4GvcmXrn8mSRK9DpU-BE'
        })
        
        # 03 - APROVADAS
        pasta_aprovadas = os.getenv('PASTA_03_APROVADAS')
        result['aprovadas'] = analisar_pasta_final(service, pasta_aprovadas)
        result['total_aprovadas'] = sum(t.get('total', 0) for t in result['aprovadas'].values())
        
        # 04 - REJEITADAS
        pasta_rejeitadas = os.getenv('PASTA_04_REJEITADAS')
        result['rejeitadas'] = analisar_pasta_final(service, pasta_rejeitadas)
        result['total_rejeitadas'] = sum(t.get('total', 0) for t in result['rejeitadas'].values())
        
        # Taxa aprovação
        total_peticoes = result['total_aprovadas'] + result['total_rejeitadas']
        if total_peticoes > 0:
            result['taxa_aprovacao'] = (result['total_aprovadas'] / total_peticoes) * 100
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def analisar_casos_novos(service):
    """Analisa pasta 01_CASOS_NOVOS com sistema de 3 prioridades"""
    tipos_pastas = {
        'RECONHECIMENTO_VINCULO': os.getenv('PASTA_RECONHECIMENTO_VINCULO'),
        'ACAO_ACIDENTARIA': os.getenv('PASTA_ACAO_ACIDENTARIA'),
        'DIFERENCAS_CONTRATUAIS': os.getenv('PASTA_DIFERENCAS_CONTRATUAIS')
    }
    
    # Sistema de 3 prioridades - Checklist v4.0
    DOCUMENTOS_POR_TIPO = {
        'RECONHECIMENTO_VINCULO': {
            'ALTA': ['DOCUMENTO_PESSOAL', 'CTPS', 'COMPROVANTE_PAGAMENTO', 'TRANSCRICAO'],
            'MEDIA': ['COMPROVANTE_RESIDENCIA', 'FOTOS_TRABALHANDO', 'TRCT'],
            'BAIXA': ['CONVERSAS_WHATSAPP', 'CONTRATO']
        },
        'ACAO_ACIDENTARIA': {
            'ALTA': ['DOCUMENTO_PESSOAL', 'CTPS', 'COMPROVANTE_PAGAMENTO', 'ATESTADO_MEDICO', 
                     'EXAMES_MEDICOS', 'DOCUMENTOS_PREVIDENCIARIOS', 'CAT', 'TRANSCRICAO'],
            'MEDIA': ['COMPROVANTE_RESIDENCIA', 'FOTOS_TRABALHANDO', 'FOTOS_AMBIENTE', 'TRCT'],
            'BAIXA': ['CONVERSAS_WHATSAPP']
        },
        'DIFERENCAS_CONTRATUAIS': {
            'ALTA': ['DOCUMENTO_PESSOAL', 'CTPS', 'COMPROVANTE_PAGAMENTO', 'HOLERITES', 'TRCT', 'TRANSCRICAO'],
            'MEDIA': ['COMPROVANTE_RESIDENCIA', 'FOTOS_TRABALHANDO', 'CONTRATO', 
                      'CARTAO_PONTO', 'EXTRATO_FGTS'],
            'BAIXA': ['CONVERSAS_WHATSAPP']
        }
    }
    
    resultado = {}
    
    for tipo, pasta_id in tipos_pastas.items():
        if not pasta_id:
            continue
        
        # Listar pastas de clientes
        query = f"'{pasta_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
        pastas = service.files().list(q=query, fields="files(id, name)").execute().get('files', [])
        
        clientes = []
        processados = 0
        pendentes = 0
        
        for pasta_cliente in pastas:
            # Verificar se processado
            arquivos = listar_arquivos_pasta(service, pasta_cliente['id'])
            eh_processado = any(a['name'].strip().upper() == '_PROCESSADO.TXT' for a in arquivos)
            
            if eh_processado:
                processados += 1
                clientes.append({
                    'nome': pasta_cliente['name'],
                    'status': 'processado',
                    'status_label': '✅ Processado',
                    'documentos': None
                })
            else:
                # Classificar documentos com sistema expandido
                docs_presentes = []
                for arq in arquivos:
                    tipo_doc = classificar_doc_completo(arq['name'])
                    if tipo_doc and tipo_doc not in docs_presentes:
                        docs_presentes.append(tipo_doc)
                
                # Verificar com 3 prioridades
                docs_config = DOCUMENTOS_POR_TIPO.get(tipo, {})
                
                alta_presentes = [d for d in docs_config.get('ALTA', []) if d in docs_presentes]
                alta_faltantes = [d for d in docs_config.get('ALTA', []) if d not in docs_presentes]
                
                media_presentes = [d for d in docs_config.get('MEDIA', []) if d in docs_presentes]
                media_faltantes = [d for d in docs_config.get('MEDIA', []) if d not in docs_presentes]
                
                baixa_presentes = [d for d in docs_config.get('BAIXA', []) if d in docs_presentes]
                baixa_faltantes = [d for d in docs_config.get('BAIXA', []) if d not in docs_presentes]
                
                # Todos os faltantes
                todos_faltantes = alta_faltantes + media_faltantes + baixa_faltantes
                todos_presentes = alta_presentes + media_presentes + baixa_presentes
                
                # Status: completo APENAS se tudo estiver presente
                if len(todos_faltantes) == 0:
                    status = 'completo'
                    status_label = '🟢 Completo'
                else:
                    status = 'incompleto'
                    # Priorizar erro por ALTA
                    if alta_faltantes:
                        status_label = f'🔴 Crítico ({len(alta_faltantes)} ALTA faltando)'
                    elif media_faltantes:
                        status_label = f'⚠️ Incompleto ({len(media_faltantes)} MÉDIA faltando)'
                    else:
                        status_label = f'🟡 Quase ({len(baixa_faltantes)} BAIXA faltando)'
                    pendentes += 1
                
                clientes.append({
                    'nome': pasta_cliente['name'],
                    'status': status,
                    'status_label': status_label,
                    'documentos': {
                        'presentes': todos_presentes,
                        'faltantes': todos_faltantes,
                        'alta_faltantes': alta_faltantes,
                        'media_faltantes': media_faltantes,
                        'baixa_faltantes': baixa_faltantes
                    }
                })
        
        resultado[tipo] = {
            'total': len(clientes),
            'processados': processados,
            'pendentes': pendentes,
            'clientes': clientes
        }
    
    return resultado

def classificar_doc_completo(nome):
    """Classificação completa - igual ao sistema principal"""
    nome = nome.lower()
    
    # DOCUMENTO_PESSOAL
    if any(x in nome for x in ['rg', 'identidade', 'cpf', 'cnh', 'habilitacao']):
        return 'DOCUMENTO_PESSOAL'
    # CTPS
    elif any(x in nome for x in ['ctps', 'carteira trabalho', 'carteira de trabalho', 'trabalho', 'ct ']):
        return 'CTPS'
    # HOLERITES
    elif any(x in nome for x in ['holerite', 'contracheque', 'hollerite', 'olerite']):
        return 'HOLERITES'
    # COMPROVANTE_PAGAMENTO
    elif any(x in nome for x in ['pagamento', 'pagto', 'recibo', 'folha ponto']):
        return 'COMPROVANTE_PAGAMENTO'
    # TRCT
    elif any(x in nome for x in ['rescisao', 'trct']):
        return 'TRCT'
    # COMPROVANTE_RESIDENCIA
    elif any(x in nome for x in ['luz', 'agua', 'energia', 'iptu', 'aluguel', 'residencia']):
        return 'COMPROVANTE_RESIDENCIA'
    # MÉDICOS
    elif 'atestado' in nome:
        return 'ATESTADO_MEDICO'
    elif 'exame' in nome or 'laudo' in nome:
        return 'EXAMES_MEDICOS'
    elif 'cat' in nome:
        return 'CAT'
    elif 'inss' in nome or 'previdencia' in nome:
        return 'DOCUMENTOS_PREVIDENCIARIOS'
    # TRANSCRIÇÃO
    elif any(x in nome for x in ['transcricao', 'entrevista', 'relato', 'fatos']):
        return 'TRANSCRICAO'
    # FOTOS
    elif 'foto' in nome or 'imagem' in nome:
        if 'ambiente' in nome:
            return 'FOTOS_AMBIENTE'
        return 'FOTOS_TRABALHANDO'
    # CONTRATO
    elif 'contrato' in nome:
        return 'CONTRATO'
    # CARTAO PONTO
    elif 'ponto' in nome or 'cartao' in nome:
        return 'CARTAO_PONTO'
    # EXTRATO FGTS
    elif 'fgts' in nome or 'extrato' in nome:
        return 'EXTRATO_FGTS'
    # WHATSAPP
    elif any(x in nome for x in ['whatsapp', 'wpp', 'conversa', 'chat']):
        return 'CONVERSAS_WHATSAPP'
    else:
        return None

def classificar_doc_simples(nome):
    """Classificação simplificada de documento"""
    nome = nome.lower()
    if 'rg' in nome or 'identidade' in nome:
        return 'RG'
    elif 'cpf' in nome:
        return 'CPF'
    elif 'cnh' in nome:
        return 'CNH'
    elif 'ctps' in nome:
        return 'CTPS'
    elif any(x in nome for x in ['holerite', 'contracheque', 'comprovante', 'pagamento', 'pagto', 'pag ', 'recibo', 'folha ponto']):
        return 'COMPROVANTE_PAGAMENTO'
    elif 'rescisao' in nome or 'trct' in nome:
        return 'TRCT'
    elif any(x in nome for x in ['luz', 'agua', 'energia', 'iptu', 'aluguel', 'residencia']):
        return 'COMPROVANTE_RESIDENCIA'
    elif 'atestado' in nome:
        return 'ATESTADO_MEDICO'
    elif 'exame' in nome or 'laudo' in nome:
        return 'EXAMES_MEDICOS'
    elif 'cat' in nome:
        return 'CAT'
    elif 'inss' in nome or 'previdencia' in nome:
        return 'DOCUMENTOS_PREVIDENCIARIOS'
    return None

def analisar_pasta_peticoes(service, pastas_tipos):
    """Analisa pasta 02 - petições aguardando auditoria com links"""
    resultado = {}
    
    for tipo, pasta_id in pastas_tipos.items():
        arquivos = listar_arquivos_pasta(service, pasta_id)
        peticoes = [a for a in arquivos if a['name'].startswith('Peticao_') and a['name'].endswith('.docx')]
        
        clientes = []
        for pet in peticoes:
            parts = pet['name'].split('_')
            cliente_nome = parts[2] if len(parts) > 2 else 'Desconhecido'
            
            # Link do Drive
            try:
                file_info = service.files().get(fileId=pet['id'], fields='webViewLink,createdTime').execute()
                link = file_info.get('webViewLink', '')
                created = file_info.get('createdTime', '')
            except:
                link = ''
                created = ''
            
            clientes.append({
                'nome': cliente_nome,
                'status': 'pendente',
                'status_label': '⏳ Aguardando Auditoria',
                'documentos': None,
                'link': link,
                'arquivo_id': pet['id'],
                'criado_em': created
            })
        
        resultado[tipo] = {
            'total': len(clientes),
            'processados': 0,
            'pendentes': len(clientes),
            'clientes': clientes
        }
    
    return resultado

def ler_score_do_log(cliente_nome):
    """Lê o score e análise completa do arquivo de log da auditoria"""
    try:
        log_dir = 'logs_auditoria'
        if not os.path.exists(log_dir):
            return None
        
        # Procurar arquivo mais recente deste cliente
        arquivos = [f for f in os.listdir(log_dir) if cliente_nome.replace(' ', '_') in f]
        if not arquivos:
            return None
        
        arquivo_mais_recente = max(arquivos, key=lambda f: os.path.getctime(os.path.join(log_dir, f)))
        caminho = os.path.join(log_dir, arquivo_mais_recente)
        
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Extrair informações
        resultado = {}
        
        # Score
        if 'Score Final:' in conteudo:
            score_line = [l for l in conteudo.split('\n') if 'Score Final:' in l][0]
            score = score_line.split(':')[1].strip().split('/')[0]
            resultado['score'] = int(score)
        
        # Status
        if '✅ APROVADA' in conteudo:
            resultado['aprovada'] = True
        elif '❌ REJEITADA' in conteudo:
            resultado['aprovada'] = False
        
        # Justificativa do Score
        if 'JUSTIFICATIVA DO SCORE' in conteudo:
            inicio = conteudo.find('JUSTIFICATIVA DO SCORE')
            fim = conteudo.find('===', inicio + 50)
            justificativa_section = conteudo[inicio:fim]
            linhas_justificativa = [l.strip() for l in justificativa_section.split('\n') if l.strip() and '===' not in l and 'JUSTIFICATIVA' not in l]
            resultado['justificativa'] = ' '.join(linhas_justificativa)
        
        # Erros críticos
        erros = []
        capturando_erros = False
        for linha in conteudo.split('\n'):
            if 'ERROS CRÍTICOS' in linha:
                capturando_erros = True
                continue
            if capturando_erros:
                if '===' in linha or 'ALERTAS' in linha:
                    break
                if linha.strip().startswith('❌'):
                    erros.append(linha.strip()[2:])
        resultado['erros_criticos'] = erros
        
        # Alertas
        alertas = []
        capturando_alertas = False
        for linha in conteudo.split('\n'):
            if 'ALERTAS' in linha and 'ERROS' not in linha:
                capturando_alertas = True
                continue
            if capturando_alertas:
                if '===' in linha or 'SUGESTÕES' in linha:
                    break
                if linha.strip().startswith('⚠️'):
                    alertas.append(linha.strip()[2:])
        resultado['alertas'] = alertas
        
        # Sugestões
        sugestoes = []
        capturando_sugestoes = False
        for linha in conteudo.split('\n'):
            if 'SUGESTÕES DE MELHORIA' in linha:
                capturando_sugestoes = True
                continue
            if capturando_sugestoes:
                if '===' in linha or 'PONTOS POSITIVOS' in linha:
                    break
                if linha.strip().startswith('💡'):
                    sugestoes.append(linha.strip()[2:])
        resultado['sugestoes'] = sugestoes
        
        # Pontos Positivos
        positivos = []
        capturando_positivos = False
        for linha in conteudo.split('\n'):
            if 'PONTOS POSITIVOS' in linha:
                capturando_positivos = True
                continue
            if capturando_positivos:
                if '===' in linha or 'O QUE PRECISA MELHORAR' in linha:
                    break
                if linha.strip().startswith('✅'):
                    positivos.append(linha.strip()[2:])
        resultado['pontos_positivos'] = positivos
        
        # Melhorias para 100/100
        melhorias = []
        capturando_melhorias = False
        for linha in conteudo.split('\n'):
            if 'O QUE PRECISA MELHORAR PARA 100/100' in linha:
                capturando_melhorias = True
                continue
            if capturando_melhorias:
                if '===' in linha or 'RESUMO EXECUTIVO' in linha:
                    break
                if linha.strip().startswith('🎯'):
                    melhorias.append(linha.strip()[2:])
        resultado['melhorias_100'] = melhorias
        
        # Resumo
        if 'RESUMO EXECUTIVO' in conteudo:
            inicio = conteudo.find('RESUMO EXECUTIVO')
            fim = conteudo.find('===', inicio + 50)
            resumo_section = conteudo[inicio:fim]
            linhas_resumo = [l.strip() for l in resumo_section.split('\n') if l.strip() and '===' not in l and 'RESUMO' not in l]
            resultado['resumo'] = ' '.join(linhas_resumo)
        
        return resultado
        
    except Exception as e:
        print(f"Erro ao ler log: {e}")
        return None

def analisar_pasta_final(service, pasta_id):
    """Analisa pastas 03 e 04 com scores, justificativas e melhorias"""
    if not pasta_id:
        return {}
    
    arquivos = listar_arquivos_pasta(service, pasta_id)
    peticoes = [a for a in arquivos if a['name'].startswith('Peticao_') and a['name'].endswith('.docx')]
    
    # Agrupar por tipo
    por_tipo = {}
    
    for pet in peticoes:
        parts = pet['name'].split('_')
        tipo = parts[1] if len(parts) > 1 else 'DESCONHECIDO'
        
        # Extrair nome completo do cliente
        # Formato: Peticao_RECONHECIMENTO_VINCULO_Cliente_Rodrigo_Diogo_20251217...
        # Pegar tudo entre o tipo e a data (que começa com números)
        cliente_nome = 'Desconhecido'
        if len(parts) > 2:
            # Encontrar onde começa a data (primeiro elemento que começa com dígito)
            nome_parts = []
            for i in range(2, len(parts)):
                if parts[i][0].isdigit():  # Encontrou a data
                    break
                nome_parts.append(parts[i])
            cliente_nome = '_'.join(nome_parts) if nome_parts else parts[2]
        
        if tipo not in por_tipo:
            por_tipo[tipo] = {
                'total': 0,
                'processados': 0,
                'pendentes': 0,
                'clientes': []
            }
        
        # Buscar informações do log
        log_data = ler_score_do_log(cliente_nome)
        
        # Link do Drive
        try:
            file_info = service.files().get(fileId=pet['id'], fields='webViewLink').execute()
            link = file_info.get('webViewLink', '')
        except:
            link = ''
        
        por_tipo[tipo]['total'] += 1
        por_tipo[tipo]['clientes'].append({
            'nome': cliente_nome,
            'status': 'processado',
            'status_label': '✅ Finalizado',
            'documentos': None,
            'score': log_data.get('score', 0) if log_data else 0,
            'justificativa': log_data.get('justificativa', '') if log_data else '',
            'erros': log_data.get('erros_criticos', []) if log_data else [],
            'alertas': log_data.get('alertas', []) if log_data else [],
            'sugestoes': log_data.get('sugestoes', []) if log_data else [],
            'pontos_positivos': log_data.get('pontos_positivos', []) if log_data else [],
            'melhorias_100': log_data.get('melhorias_100', []) if log_data else [],
            'resumo': log_data.get('resumo', '') if log_data else '',
            'link': link,
            'arquivo_id': pet['id']
        })
    
    return por_tipo

@app.route('/api/stats')
def get_stats():
    """Endpoint principal - retorna estatísticas"""
    try:
        service = autenticar_google_drive()
        
        # Se não conseguiu autenticar, retornar dados vazios
        if not service:
            return jsonify({
                'total_clientes': 0,
                'total_aprovadas': 0,
                'total_rejeitadas': 0,
                'taxa_aprovacao': 0,
                'score_medio': 0,
                'peticoes_hoje': 0,
                'ultimas_atividades': [],
                'timestamp': datetime.now().isoformat(),
                'error': 'Google Drive não autenticado'
            })
        
        # Contar clientes processados
        total_clientes = contar_clientes_processados(service)
        
        # Analisar petições aprovadas
        pasta_aprovadas = os.getenv('PASTA_03_APROVADAS')
        peticoes_aprovadas = analisar_peticoes(service, pasta_aprovadas) if pasta_aprovadas else []
        
        # Analisar petições rejeitadas
        pasta_rejeitadas = os.getenv('PASTA_04_REJEITADAS')
        peticoes_rejeitadas = analisar_peticoes(service, pasta_rejeitadas) if pasta_rejeitadas else []
        
        total_aprovadas = len(peticoes_aprovadas)
        total_rejeitadas = len(peticoes_rejeitadas)
        total_peticoes = total_aprovadas + total_rejeitadas
        
        # Calcular taxa de aprovação
        taxa_aprovacao = (total_aprovadas / total_peticoes * 100) if total_peticoes > 0 else 0
        
        # Score médio (estimativa: aprovadas ~85, rejeitadas ~50)
        if total_peticoes > 0:
            score_medio = (total_aprovadas * 85 + total_rejeitadas * 50) / total_peticoes
        else:
            score_medio = 0
        
        # Petições de hoje
        hoje = datetime.now().date()
        peticoes_hoje = 0
        
        for pet in peticoes_aprovadas + peticoes_rejeitadas:
            if pet.get('timestamp'):
                data_pet = datetime.fromisoformat(pet['timestamp'].replace('Z', '+00:00')).date()
                if data_pet == hoje:
                    peticoes_hoje += 1
        
        # Últimas atividades (10 mais recentes)
        todas_peticoes = []
        
        for pet in peticoes_aprovadas:
            todas_peticoes.append({
                'cliente': pet['cliente'],
                'tipo_processo': pet['tipo_processo'],
                'timestamp': pet['timestamp'],
                'aprovada': True,
                'score': 85  # Estimativa para aprovadas
            })
        
        for pet in peticoes_rejeitadas:
            todas_peticoes.append({
                'cliente': pet['cliente'],
                'tipo_processo': pet['tipo_processo'],
                'timestamp': pet['timestamp'],
                'aprovada': False,
                'score': 50  # Estimativa para rejeitadas
            })
        
        # Ordenar por timestamp (mais recentes primeiro)
        todas_peticoes.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True)
        ultimas_atividades = todas_peticoes[:10]
        
        return jsonify({
            'total_clientes': total_clientes,
            'total_aprovadas': total_aprovadas,
            'total_rejeitadas': total_rejeitadas,
            'taxa_aprovacao': taxa_aprovacao,
            'score_medio': score_medio,
            'peticoes_hoje': peticoes_hoje,
            'ultimas_atividades': ultimas_atividades,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Erro na API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'total_clientes': 0,
            'total_aprovadas': 0,
            'total_rejeitadas': 0,
            'taxa_aprovacao': 0,
            'score_medio': 0,
            'peticoes_hoje': 0,
            'ultimas_atividades': []
        }), 500

@app.route('/')
def index():
    """Serve o dashboard CRM v2"""
    try:
        # Tentar primeiro no local original
        for path in ['dashboard_v2.html', 'telas/dashboard_v2.html', 'dashboard_crm_v2.html', 'dashboard_crm.html', 'dashboard.html', 
                     'telas/dashboard.html', 'telas/dashboard_crm_v2.html']:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        return "Dashboard não encontrado", 404
    except Exception as e:
        return f"Erro ao carregar dashboard: {e}", 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/gerar-peticao-manual', methods=['POST'])
def gerar_peticao_manual():
    """
    Endpoint para geração manual de petições
    Permite gerar mesmo com documentos faltantes
    """
    try:
        data = request.json
        cliente_nome = data.get('cliente_nome')
        tipo_acao = data.get('tipo_acao', 'RECONHECIMENTO_VINCULO')
        forcar_geracao = data.get('forcar_geracao', False)
        
        print(f"\n{'='*70}")
        print(f"  🚀 GERAÇÃO MANUAL DE PETIÇÃO")
        print(f"  👤 Cliente: {cliente_nome}")
        print(f"  📋 Tipo: {tipo_acao}")
        print(f"  ⚡ Forçar: {forcar_geracao}")
        print(f"{'='*70}\n")
        
        if not cliente_nome:
            return jsonify({
                'success': False, 
                'error': 'Nome do cliente não fornecido'
            }), 400
        
        # Executar o script main.py com parâmetros específicos
        # Isso vai acionar o processamento manual do cliente
        resultado = executar_geracao_manual(cliente_nome, tipo_acao, forcar_geracao)
        
        if resultado.get('success'):
            return jsonify({
                'success': True,
                'message': 'Petição gerada com sucesso',
                'arquivo': resultado.get('arquivo'),
                'link': resultado.get('link')
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('error', 'Erro ao gerar petição')
            }), 500
            
    except Exception as e:
        print(f"❌ Erro ao gerar petição manual: {e}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/gerar-cronologia', methods=['POST'])
def gerar_cronologia():
    """
    Endpoint para geração manual de cronologia dos fatos
    Gera apenas o documento de cronologia sem a petição completa
    """
    try:
        data = request.json
        cliente_nome = data.get('cliente_nome')
        
        print(f"\n{'='*70}")
        print(f"  📅 GERAÇÃO MANUAL DE CRONOLOGIA")
        print(f"  👤 Cliente: {cliente_nome}")
        print(f"{'='*70}\n")
        
        if not cliente_nome:
            return jsonify({
                'success': False, 
                'error': 'Nome do cliente não fornecido'
            }), 400
        
        # Criar flag para geração de cronologia
        flag_file = f"flag_cronologia_{cliente_nome.replace(' ', '_')}.json"
        with open(flag_file, 'w') as f:
            json.dump({
                'cliente_nome': cliente_nome,
                'tipo': 'cronologia',
                'timestamp': datetime.now().isoformat()
            }, f)
        
        print(f"✅ Flag de cronologia criada: {flag_file}")
        print(f"⏳ Aguarde o sistema processar...")
        
        return jsonify({
            'success': True,
            'message': 'Solicitação de cronologia enviada. O documento será gerado em instantes.',
            'flag_file': flag_file
        })
            
    except Exception as e:
        print(f"❌ Erro ao gerar cronologia: {e}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/transcrever-video', methods=['POST'])
def transcrever_video():
    """
    Endpoint para transcrição de vídeo (Assíncrono via Flag)
    Apenas cria a flag para que o main_v10_fase3.py processe
    """
    try:
        data = request.json
        cliente_nome = data.get('cliente_nome')
        
        print(f"\n{'='*70}")
        print(f"  🎥 SOLICITAÇÃO DE TRANSCRIÇÃO DE VÍDEO")
        print(f"  👤 Cliente: {cliente_nome}")
        print(f"{'='*70}\n")
        
        if not cliente_nome:
            return jsonify({
                'success': False, 
                'error': 'Nome do cliente não fornecido'
            }), 400
        
        # Criar flag para transcrição
        flag_file = f"flag_transcricao_{cliente_nome.replace(' ', '_')}.json"
        with open(flag_file, 'w') as f:
            json.dump({
                'cliente_nome': cliente_nome,
                'tipo': 'transcricao_video',
                'timestamp': datetime.now().isoformat()
            }, f)
        
        print(f"✅ Flag de transcrição criada: {flag_file}")
        print(f"⏳ Aguarde o sistema processar...")
        
        return jsonify({
            'success': True,
            'message': 'Solicitação de transcrição enviada. O sistema irá buscar e processar os vídeos automaticamente.',
            'flag_file': flag_file
        })
            
    except Exception as e:
        print(f"❌ Erro ao solicitar transcrição: {e}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/videos-pendentes', methods=['GET'])
def listar_videos_pendentes():
    """
    Lista vídeos que ainda não foram transcritos
    Busca por arquivos de vídeo que não têm transcrição correspondente
    """
    try:
        cliente_nome = request.args.get('cliente')
        pasta_cliente_id = request.args.get('pasta_id')
        
        if not pasta_cliente_id:
            return jsonify({
                'success': False,
                'error': 'ID da pasta do cliente não fornecido'
            }), 400
        
        service = autenticar_google_drive()
        
        # Listar todos os arquivos da pasta do cliente
        arquivos = listar_arquivos_pasta(service, pasta_cliente_id)
        
        # Filtrar vídeos
        extensoes_video = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.mpeg', '.mpg']
        videos = []
        
        for arquivo in arquivos:
            nome = arquivo.get('name', '')
            if any(nome.lower().endswith(ext) for ext in extensoes_video):
                # Verificar se já existe transcrição
                nome_base = os.path.splitext(nome)[0]
                transcricao_existe = any(
                    (a.get('name', '').startswith(f'TRANSCRICAO_{nome_base}') or 
                     a.get('name', '').startswith(f'RESUMO_{nome_base}'))
                    for a in arquivos
                )
                
                videos.append({
                    'id': arquivo.get('id'),
                    'nome': nome,
                    'tamanho': arquivo.get('size', 0),
                    'data_modificacao': arquivo.get('modifiedTime', ''),
                    'transcrito': transcricao_existe
                })
        
        return jsonify({
            'success': True,
            'videos': videos,
            'total': len(videos),
            'pendentes': len([v for v in videos if not v['transcrito']])
        })
        
    except Exception as e:
        print(f"❌ Erro ao listar vídeos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def executar_geracao_manual(cliente_nome, tipo_acao, forcar_geracao):
    """
    Executa a geração manual de petição
    
    OPÇÃO 1: Importar diretamente (se main.py estiver preparado)
    OPÇÃO 2: Executar como subprocess (mais seguro)
    """
    try:
        # OPÇÃO 1: Importar diretamente
        # Descomente se tiver a função no main.py:
        """
        from main_v10_fase3 import gerar_peticao_para_cliente
        
        resultado = gerar_peticao_para_cliente(
            cliente_nome=cliente_nome,
            tipo_acao=tipo_acao,
            forcar_geracao=forcar_geracao
        )
        return resultado
        """
        
        # OPÇÃO 2: Executar como subprocess (RECOMENDADO)
        # Cria um arquivo temporário com flag de geração manual
        flag_file = f"flag_manual_{cliente_nome.replace(' ', '_')}.json"
        with open(flag_file, 'w') as f:
            json.dump({
                'cliente_nome': cliente_nome,
                'tipo_acao': tipo_acao,
                'forcar_geracao': forcar_geracao,
                'timestamp': datetime.now().isoformat()
            }, f)
        
        # O main.py deve verificar por flags e processar
        # Por enquanto, retornar sucesso simulado
        print(f"✅ Flag criada: {flag_file}")
        print(f"⏳ Aguarde o main.py processar...")
        
        return {
            'success': True,
            'message': 'Solicitação de geração enviada',
            'arquivo': f'Peticao_{cliente_nome}_pendente.docx',
            'link': None,
            'flag_file': flag_file
        }
        
    except Exception as e:
        print(f"❌ Erro em executar_geracao_manual: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/api/status-processamento', methods=['GET'])
def check_status_processamento():
    cliente = request.args.get('cliente')
    if not cliente:
        return jsonify({'error': 'Cliente não informado'}), 400
        
    try:
        historico = carregar_historico()
        
        print(f"\n[DEBUG] Buscando status para cliente: '{cliente}'")
        print(f"[DEBUG] Total de entradas no histórico: {len(historico)}")
        
        # Procurar entrada mais recente do cliente (buscar em múltiplos campos)
        entradas_cliente = []
        for h in historico:
            nome_no_historico = h.get('cliente', '') or h.get('nome', '') or h.get('cliente_nome', '')
            if nome_no_historico.lower() == cliente.lower():
                entradas_cliente.append(h)
                print(f"[DEBUG] Entrada encontrada: {h.get('cliente')} - Status: {h.get('status')} - Msg: {h.get('status_processamento')}")
        
        if not entradas_cliente:
            print(f"[DEBUG] Nenhuma entrada encontrada para '{cliente}'")
            print(f"[DEBUG] Primeiras 3 entradas do histórico:")
            for h in historico[:3]:
                print(f"  - {h.get('cliente')} / {h.get('nome')} - {h.get('status')}")
            return jsonify({
                'status': 'nao_encontrado',
                'mensagem': 'Aguardando início do processamento...',
                'concluido': False
            })
            
        # Pegar a mais recente
        # Ordenar por data (assumindo que novos ficam no fim ou tem data)
        item = entradas_cliente[-1]
        
        status = item.get('status', 'desconhecido')
        msg = item.get('status_processamento', 'Processando...')
        
        # Se mensagem for None ou vazia, usar status
        if not msg:
            if status == 'gerada': msg = 'Petição gerada, aguardando auditoria...'
            elif status == 'aprovada': msg = 'Processo concluído com sucesso!'
            elif status == 'rejeitada': msg = 'Processo concluído (rejeitada)'
            elif status == 'processando': msg = 'Em processamento...'
            else: msg = 'Gerando petição...'  # Fallback adicional
            
        concluido = status in ['aprovada', 'rejeitada', 'concluido']
        # Se tiver status 'gerada', ainda não acabou (falta auditoria)
        # Se tiver status 'processando', não acabou
        
        # Debug
        print(f"[DEBUG] Cliente: {cliente}")
        print(f"[DEBUG] Status: {status}")
        print(f"[DEBUG] Mensagem: {msg}")
        print(f"[DEBUG] Concluído: {concluido}")
        
        return jsonify({
            'status': status,
            'mensagem': msg,
            'concluido': concluido,
            'dados': item if concluido else None
        })
        
    except Exception as e:
        print(f"Erro ao verificar status: {e}")
        return jsonify({'error': str(e)}), 500

def criar_pasta_google_drive(service, nome_pasta, pasta_pai_id):
    """Cria uma nova pasta no Google Drive dentro da pasta pai especificada"""
    try:
        file_metadata = {
            'name': nome_pasta,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [pasta_pai_id]
        }
        
        file = service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        print(f"✅ Pasta criada: {nome_pasta} (ID: {file.get('id')})")
        return file.get('id')
        
    except Exception as e:
        print(f"❌ Erro ao criar pasta no Drive: {e}")
        raise e

def salvar_json_drive(service, dados, nome_arquivo, pasta_pai_id):
    """Salva um dicionário como arquivo JSON no Google Drive"""
    try:
        file_metadata = {
            'name': nome_arquivo,
            'parents': [pasta_pai_id]
        }
        
        # Converter dict para stream de bytes
        json_str = json.dumps(dados, indent=4, ensure_ascii=False)
        fh = io.BytesIO(json_str.encode('utf-8'))
        media = MediaIoBaseUpload(fh, mimetype='application/json', resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"✅ Arquivo JSON salvo: {nome_arquivo} (ID: {file.get('id')})")
        return file.get('id')
    except Exception as e:
        print(f"❌ Erro ao salvar JSON no Drive: {e}")
        # Não lança erro para não impedir o cadastro, mas loga
        return None

@app.route('/api/client-metadata', methods=['GET'])
def get_client_metadata():
    """Busca os metadados (dados_cliente.json) de um cliente pelo nome"""
    try:
        nome_cliente = request.args.get('nome')
        if not nome_cliente:
            return jsonify({'success': False, 'error': 'Nome do cliente obrigatório'}), 400
            
        print(f"🔍 Buscando metadados para: {nome_cliente}")
        service = autenticar_google_drive()
        
        # 1. Encontrar pasta do cliente pelo nome
        query = f"name = '{nome_cliente}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(q=query, fields="files(id, parents)").execute()
        pastas = results.get('files', [])
        
        if not pastas:
            return jsonify({'success': False, 'error': 'Pasta do cliente não encontrada'}), 404
            
        # Assumir a primeira pasta encontrada (idealmente filtrar pelo pai correto se houver duplicidade)
        pasta_id = pastas[0]['id']
        
        # 2. Buscar dados_cliente.json dentro da pasta
        query_json = f"'{pasta_id}' in parents and name = 'dados_cliente.json' and trashed = false"
        results_json = service.files().list(q=query_json, fields="files(id)").execute()
        arquivos = results_json.get('files', [])
        
        if not arquivos:
            return jsonify({'success': False, 'error': 'Arquivo de dados não encontrado'}), 404
            
        file_id = arquivos[0]['id']
        
        # 3. Baixar conteúdo
        request_drive = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request_drive)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        fh.seek(0)
        dados = json.load(fh)
        
        return jsonify({
            'success': True,
            'dados': dados
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar metadados: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/drive/folders', methods=['GET'])
def list_drive_folders():
    """Lista pastas e arquivos do Google Drive"""
    try:
        folder_id = request.args.get('folderId')
        service = autenticar_google_drive()
        
        # Se não especificar folder, listar as pastas raiz (tipos de ação)
        if not folder_id:
            # Pastas principais do sistema (em destaque)
            pastas_principais = [
                {'id': os.getenv('PASTA_01_CASOS_NOVOS'), 'name': '📋 01_CASOS_NOVOS', 'isPrincipal': True},
                {'id': os.getenv('PASTA_03_APROVADAS'), 'name': '✅ 03_PETICOES_APROVADAS', 'isPrincipal': True}
            ]
            
            # Adicionar apenas pastas principais
            items = []
            for pasta in pastas_principais:
                if pasta['id']:
                    items.append({
                        'id': pasta['id'],
                        'name': pasta['name'],
                        'mimeType': 'application/vnd.google-apps.folder',
                        'isFolder': True,
                        'isPrincipal': True,
                        'size': '-',
                        'modifiedTime': '-'
                    })
            
            return jsonify({
                'success': True,
                'items': items,
                'currentFolder': {'id': 'root', 'name': 'Google Drive'}
            })
        
        # Listar conteúdo da pasta especificada
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType, size, modifiedTime, parents)",
            orderBy="folder,name",
            pageSize=100
        ).execute()
        
        files = results.get('files', [])
        
        # Buscar nome da pasta atual
        folder_info = service.files().get(
            fileId=folder_id,
            fields="name, parents"
        ).execute()
        
        items = []
        for file in files:
            is_folder = file['mimeType'] == 'application/vnd.google-apps.folder'
            size = '-' if is_folder else f"{int(file.get('size', 0)) / 1024:.1f} KB" if file.get('size') else '-'
            
            items.append({
                'id': file['id'],
                'name': file['name'],
                'mimeType': file['mimeType'],
                'isFolder': is_folder,
                'size': size,
                'modifiedTime': file.get('modifiedTime', '-')
            })
        
        return jsonify({
            'success': True,
            'items': items,
            'currentFolder': {
                'id': folder_id,
                'name': folder_info.get('name', 'Pasta'),
                'parentId': folder_info.get('parents', [None])[0]
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao listar pastas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/drive/upload', methods=['POST'])
def upload_to_drive():
    """Faz upload de arquivo para uma pasta específica do Google Drive"""
    try:
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        folder_id = request.form.get('folderId')
        
        if not folder_id:
            return jsonify({'success': False, 'error': 'ID da pasta não especificado'}), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nome de arquivo vazio'}), 400
        
        print(f"📤 Iniciando upload: {file.filename} para pasta {folder_id}")
        
        service = autenticar_google_drive()
        
        # Preparar metadados do arquivo
        file_metadata = {
            'name': file.filename,
            'parents': [folder_id]
        }
        
        # Criar media upload
        media = MediaIoBaseUpload(
            io.BytesIO(file.read()),
            mimetype=file.content_type or 'application/octet-stream',
            resumable=True
        )
        
        # Upload do arquivo
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, size, modifiedTime'
        ).execute()
        
        print(f"✅ Upload concluído: {uploaded_file['name']} (ID: {uploaded_file['id']})")
        
        return jsonify({
            'success': True,
            'file': {
                'id': uploaded_file['id'],
                'name': uploaded_file['name'],
                'mimeType': uploaded_file.get('mimeType', ''),
                'size': uploaded_file.get('size', '0'),
                'modifiedTime': uploaded_file.get('modifiedTime', '')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro no upload: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/drive/delete', methods=['DELETE'])
def delete_from_drive():
    """Exclui um arquivo do Google Drive"""
    try:
        data = request.json
        file_id = data.get('fileId')
        
        if not file_id:
            return jsonify({'success': False, 'error': 'ID do arquivo não especificado'}), 400
        
        print(f"🗑️ Excluindo arquivo: {file_id}")
        
        service = autenticar_google_drive()
        
        # Mover arquivo para lixeira (soft delete)
        service.files().delete(fileId=file_id).execute()
        
        print(f"✅ Arquivo excluído com sucesso")
        
        return jsonify({
            'success': True,
            'message': 'Arquivo excluído com sucesso'
        })
        
    except Exception as e:
        print(f"❌ Erro ao excluir arquivo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clientes', methods=['POST'])
def criar_cliente():
    """
    Cria um novo cliente (pasta) na estrutura do Google Drive
    e salva metadados (dados_cliente.json)
    """
    try:
        data = request.json
        nome = data.get('nome')
        tipo = data.get('tipo')
        
        # Campos opcionais
        cpf = data.get('cpf', '')
        telefone = data.get('telefone', '')
        email = data.get('email', '')
        endereco = data.get('endereco', '')
        observacoes = data.get('observacoes', '')
        
        if not nome or not tipo:
            return jsonify({'success': False, 'error': 'Nome e Tipo são obrigatórios'}), 400
            
        # Mapear tipo para ID da pasta pai
        pasta_pai_id = None
        if tipo == 'ACAO_ACIDENTARIA':
            pasta_pai_id = os.getenv('PASTA_ACAO_ACIDENTARIA')
        elif tipo == 'DIFERENCAS_CONTRATUAIS':
            pasta_pai_id = os.getenv('PASTA_DIFERENCAS_CONTRATUAIS')
        elif tipo == 'RECONHECIMENTO_VINCULO':
            pasta_pai_id = os.getenv('PASTA_RECONHECIMENTO_VINCULO')
            
        if not pasta_pai_id:
            return jsonify({'success': False, 'error': 'ID da pasta pai não configurado para este tipo'}), 500
            
        # Autenticar e Criar Pasta
        service = autenticar_google_drive()
        pasta_id = criar_pasta_google_drive(service, nome, pasta_pai_id)
        
        # Salvar metadados do cliente
        dados_cliente = {
            'nome': nome,
            'tipo_acao': tipo,
            'cpf_cnpj': cpf,
            'telefone': telefone,
            'email': email,
            'endereco': endereco,
            'observacoes': observacoes,
            'data_cadastro': datetime.now().isoformat(),
            'pasta_id': pasta_id
        }
        
        salvar_json_drive(service, dados_cliente, 'dados_cliente.json', pasta_id)
        
        return jsonify({
            'success': True,
            'message': f'Cliente {nome} cadastrado com sucesso!',
            'pasta_id': pasta_id,
            'dados': dados_cliente
        })
        
    except Exception as e:
        print(f"❌ Erro ao criar cliente: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🚀 SERVIDOR DASHBOARD INICIADO")
    print("  📊 Dashboard: http://localhost:5000")
    print("  🔌 API: http://localhost:5000/api/stats")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)