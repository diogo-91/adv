"""
Script para listar pastas de Reconhecimento de Vínculo no Google Drive
e identificar quais devem ser removidas
"""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive']

def autenticar_google_drive():
    """Autentica no Google Drive"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def listar_pastas_vinculo():
    """Lista todas as pastas dentro da pasta de Reconhecimento de Vínculo"""
    service = autenticar_google_drive()
    
    # ID da pasta de Reconhecimento de Vínculo
    pasta_vinculo_id = os.getenv('PASTA_RECONHECIMENTO_VINCULO', '1ya29qkIu8J2O1idmlco9HwSqCFKSsxTm')
    
    print(f"\n🔍 Listando pastas em Reconhecimento de Vínculo...")
    print(f"📁 ID da pasta: {pasta_vinculo_id}\n")
    
    # Listar todas as pastas
    query = f"'{pasta_vinculo_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(
        q=query,
        fields="files(id, name, createdTime, modifiedTime)",
        orderBy="createdTime desc"
    ).execute()
    
    pastas = results.get('files', [])
    
    print(f"📊 Total de pastas encontradas: {len(pastas)}\n")
    print("=" * 80)
    
    for i, pasta in enumerate(pastas, 1):
        print(f"\n{i}. 📂 {pasta['name']}")
        print(f"   ID: {pasta['id']}")
        print(f"   Criada: {pasta['createdTime']}")
        print(f"   Modificada: {pasta['modifiedTime']}")
        
        # Listar arquivos dentro da pasta
        query_arquivos = f"'{pasta['id']}' in parents and trashed=false"
        arquivos_result = service.files().list(
            q=query_arquivos,
            fields="files(name, mimeType)"
        ).execute()
        
        arquivos = arquivos_result.get('files', [])
        print(f"   📄 Arquivos: {len(arquivos)}")
        
        if arquivos:
            for arq in arquivos[:5]:  # Mostrar apenas os 5 primeiros
                print(f"      - {arq['name']}")
            if len(arquivos) > 5:
                print(f"      ... e mais {len(arquivos) - 5} arquivos")
        else:
            print(f"      ⚠️  PASTA VAZIA")
    
    print("\n" + "=" * 80)
    print(f"\n✅ Listagem concluída!")
    print(f"📊 Total: {len(pastas)} pastas")
    
    # Contar pastas vazias
    pastas_vazias = 0
    for pasta in pastas:
        query_arquivos = f"'{pasta['id']}' in parents and trashed=false"
        arquivos_result = service.files().list(q=query_arquivos, fields="files(id)").execute()
        if not arquivos_result.get('files', []):
            pastas_vazias += 1
    
    print(f"⚠️  Pastas vazias: {pastas_vazias}")
    print(f"✅ Pastas com conteúdo: {len(pastas) - pastas_vazias}")

if __name__ == '__main__':
    listar_pastas_vinculo()
