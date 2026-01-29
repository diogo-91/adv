import os

env_path = r'c:\Users\Admin\Desktop\peticoes-automatizadas\.env'

print(f"📂 Checando arquivo: {env_path}")

try:
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    found = False
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("ANTHROPIC_API_KEY="):
            found = True
            key_val = line.split("=", 1)[1]
            print(f"✅ Linha {i+1}: Chave encontrada.")
            print(f"   - Tamanho: {len(key_val)} caracteres")
            print(f"   - Início: {key_val[:12]}...")
            print(f"   - Fim: ...{key_val[-4:]}")
            
            if " " in key_val:
                print("   ❌ ALERTA: Espaços em branco detectados no meio da chave!")
            if key_val.startswith('"') or key_val.startswith("'"):
                print("   ⚠️ ALERTA: Chave está entre aspas. Pode ser problema se não removidas corretamente.")
            if not key_val.startswith("sk-ant-"):
                print("   ❌ ALERTA: Chave não começa com 'sk-ant-'. Formato suspeito.")
            
    if not found:
        print("❌ Chave ANTHROPIC_API_KEY não encontrada no arquivo!")

except Exception as e:
    print(f"❌ Erro ao ler arquivo: {e}")
