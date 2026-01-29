import requests
import json

def test_api():
    try:
        print("Chamando API...")
        response = requests.get('http://localhost:5000/api/detailed-stats')
        data = response.json()
        
        # Procurar cliente Rodrigo na resposta
        found = False
        
        # Verificar em Casos Novos (onde ele aparece como Pendente na tela)
        casos_novos = data.get('casos_novos', {})
        for tipo, info in casos_novos.items():
            for cliente in info.get('clientes', []):
                if 'Rodrigo' in cliente['nome']:
                    print(f"\n[CASOS NOVOS] Cliente: {cliente['nome']}")
                    print(f"Status: {cliente['status']}")
                    print(f"Label: {cliente['status_label']}")
                    found = True
        
        # Verificar em Petições Geradas
        peticoes = data.get('peticoes_geradas', {})
        for tipo, info in peticoes.items():
            for cliente in info.get('clientes', []):
                if 'Rodrigo' in cliente['nome']:
                    print(f"\n[PETIÇÕES GERADAS] Cliente: {cliente['nome']}")
                    print(f"Status: {cliente['status']}")
                    print(f"Label: {cliente['status_label']}")
                    found = True
                    
        if not found:
            print("❌ Cliente não encontrado na resposta da API.")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_api()
