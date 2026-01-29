import os
from dotenv import load_dotenv
from anthropic import Anthropic
import sys

# Carregar variáveis de ambiente (remover .env explícito se estiver na raiz)
# Mas vou carregar explicitamente para garantir
load_dotenv(r'c:\Users\Admin\Desktop\peticoes-automatizadas\.env')

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("❌ ERRO: ANTHROPIC_API_KEY não encontrada no .env")
    sys.exit(1)

print(f"🔑 API Key encontrada: {api_key[:15]}...")

try:
    client = Anthropic(api_key=api_key)

    texto_teste = "Esta é uma entrevista de teste. O cliente João da Silva trabalhou na empresa X de 2020 a 2024."

    print("⏳ Testando Agente Cronologia...")
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": f"Crie uma cronologia para: {texto_teste}"}
        ]
    )
    print("✅ Sucesso!")
    print(message.content[0].text)
except Exception as e:
    print(f"❌ ERRO API: {e}")
