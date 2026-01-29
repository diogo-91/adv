"""
Script de Teste - Verificar Sistema V9
"""

import os
import json

print("\n" + "="*70)
print("  VERIFICAÇÃO DO SISTEMA V9.0")
print("="*70 + "\n")

# 1. Verificar histórico
print("1. Verificando historico_peticoes.json...")
if os.path.exists('historico_peticoes.json'):
    with open('historico_peticoes.json', 'r', encoding='utf-8') as f:
        historico = json.load(f)
    print(f"   ✅ Arquivo existe!")
    print(f"   📊 Total de petições: {len(historico)}")
    
    if historico:
        print(f"\n   Última petição:")
        ultima = historico[-1]
        print(f"   - Cliente: {ultima.get('cliente')}")
        print(f"   - Tipo: {ultima.get('tipo_processo')}")
        print(f"   - Status: {ultima.get('status')}")
        print(f"   - Score: {ultima.get('score', 'N/A')}")
else:
    print("   ❌ Arquivo NÃO existe!")
    print("   → Rode o sistema (python main.py) para gerar")

# 2. Verificar logs de auditoria
print("\n2. Verificando logs_auditoria/...")
if os.path.exists('logs_auditoria'):
    logs = [f for f in os.listdir('logs_auditoria') if f.endswith('.txt')]
    print(f"   ✅ Pasta existe!")
    print(f"   📄 Total de logs: {len(logs)}")
    
    if logs:
        print(f"\n   Último log:")
        ultimo_log = max(logs, key=lambda f: os.path.getctime(os.path.join('logs_auditoria', f)))
        print(f"   - Arquivo: {ultimo_log}")
        
        # Ler log
        with open(os.path.join('logs_auditoria', ultimo_log), 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar campos
        campos = {
            'Score Final': '✅' if 'Score Final:' in conteudo else '❌',
            'JUSTIFICATIVA DO SCORE': '✅' if 'JUSTIFICATIVA DO SCORE' in conteudo else '❌',
            'PONTOS POSITIVOS': '✅' if 'PONTOS POSITIVOS' in conteudo else '❌',
            'O QUE PRECISA MELHORAR': '✅' if 'O QUE PRECISA MELHORAR' in conteudo else '❌'
        }
        
        print(f"\n   Campos no log:")
        for campo, status in campos.items():
            print(f"   {status} {campo}")
        
        # Extrair score
        if 'Score Final:' in conteudo:
            for linha in conteudo.split('\n'):
                if 'Score Final:' in linha:
                    print(f"\n   {linha.strip()}")
                    break
else:
    print("   ❌ Pasta NÃO existe!")
    print("   → Rode o sistema e aguarde auditoria")

# 3. Verificar arquivos do sistema
print("\n3. Verificando arquivos do sistema...")
arquivos = {
    'main.py': os.path.exists('main.py') or os.path.exists('main_v9_corrigido.py'),
    'dashboard_server.py': os.path.exists('dashboard_server.py'),
    'dashboard_crm_v2.html': os.path.exists('dashboard_crm_v2.html'),
    '.env': os.path.exists('.env'),
    'token.json': os.path.exists('token.json')
}

for arquivo, existe in arquivos.items():
    status = '✅' if existe else '❌'
    print(f"   {status} {arquivo}")

# 4. Instruções
print("\n" + "="*70)
print("  PRÓXIMOS PASSOS:")
print("="*70)

if not os.path.exists('historico_peticoes.json'):
    print("\n❌ HISTÓRICO VAZIO - Você precisa:")
    print("   1. Parar o sistema (Ctrl+C)")
    print("   2. Baixar main_v9_corrigido.py")
    print("   3. Substituir o main.py")
    print("   4. Delete _PROCESSADO.txt de um cliente")
    print("   5. Rodar: python main.py")
    print("   6. Aguardar gerar e auditar")
else:
    print("\n✅ Sistema funcionando!")

if not os.path.exists('logs_auditoria') or not os.listdir('logs_auditoria'):
    print("\n❌ SEM LOGS - Aguarde o auditor processar")
else:
    # Verificar se tem justificativa
    logs = [f for f in os.listdir('logs_auditoria') if f.endswith('.txt')]
    ultimo_log = max(logs, key=lambda f: os.path.getctime(os.path.join('logs_auditoria', f)))
    with open(os.path.join('logs_auditoria', ultimo_log), 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    if 'JUSTIFICATIVA DO SCORE' not in conteudo:
        print("\n⚠️ LOGS ANTIGOS - Você precisa:")
        print("   1. Delete pasta logs_auditoria/")
        print("   2. Delete petições de 03_APROVADAS/")
        print("   3. Delete petições de 04_REJEITADAS/")
        print("   4. Delete _PROCESSADO.txt do cliente")
        print("   5. Reprocessar com sistema novo")
    else:
        print("\n✅ Logs com justificativa!")

print("\n" + "="*70 + "\n")