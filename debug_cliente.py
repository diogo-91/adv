from dashboard_server import autenticar_google_drive, listar_arquivos_pasta
import os

def debug_cliente():
    print("Iniciando debug...")
    service = autenticar_google_drive()
    
    # ID da pasta vinculo (onde o cliente está)
    pasta_pai_id = os.getenv('PASTA_RECONHECIMENTO_VINCULO')
    print(f"Buscando na pasta pai: {pasta_pai_id}")
    
    # Listar pastas de clientes
    query = f"'{pasta_pai_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    pastas = results.get('files', [])
    
    found = False
    for pasta in pastas:
        if 'Rodrigo Diogo' in pasta['name']:
            found = True
            print(f"\n📁 PASTA ENCONTRADA: {pasta['name']} (ID: {pasta['id']})")
            
            arquivos = listar_arquivos_pasta(service, pasta['id'])
            print(f"   📄 Arquivos encontrados: {len(arquivos)}")
            
            print(f"   📄 Arquivos encontrados: {len(arquivos)}")
            tem_processado = False
            for arq in arquivos:
                if '_PROCESSADO' in arq['name'].upper():
                     print(f"        🎉 ARQUIVO PROCESSADO DETECTADO! Nome: '{arq['name']}' ID: {arq['id']}")
                     tem_processado = True
            
            if not tem_processado:
                print("        ⚠️ Nenhum arquivo _PROCESSADO encontrado nesta pasta.")
            
    if not found:
        print("❌ Cliente Rodrigo Diogo não encontrado na pasta pai.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    debug_cliente()
