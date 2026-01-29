import os
from dotenv import load_dotenv
from anthropic import Anthropic
import sys

load_dotenv(r'c:\Users\Admin\Desktop\peticoes-automatizadas\.env')
api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

modelos_para_testar = [
    "claude-sonnet-4-20250514",
    "claude-4-sonnet-20250514",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-latest"
]

print("🔍 Testando quais modelos sua chave tem acesso...")

for modelo in modelos_para_testar:
    print(f"\n👉 Testando: {modelo}")
    try:
        message = client.messages.create(
            model=modelo,
            max_tokens=10,
            messages=[{"role": "user", "content": "Oi"}]
        )
        print(f"✅ SUCESSO! Esse modelo está liberado.")
        # Se funcionar, vamos sugerir usar este
    except Exception as e:
        if "not_found_error" in str(e) or "404" in str(e):
             print(f"❌ INDISPONÍVEL (404 Not Found)")
        elif "authentication_error" in str(e):
             print(f"❌ ERRO DE CHAVE (Autenticação falhou)")
             break
        else:
             print(f"❌ ERRO: {e}")
