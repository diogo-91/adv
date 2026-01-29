"""
Script de Instalação Automática
Sistema de Petições Automatizadas

Instala todas as dependências necessárias automaticamente.
"""

import subprocess
import sys
import os

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def check_python():
    """Verifica versão do Python"""
    print_header("🐍 Verificando Python")
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERRO: Python 3.8 ou superior é necessário!")
        print("   Baixe em: https://www.python.org/downloads/")
        return False
    
    return True

def install_requirements():
    """Instala dependências do requirements.txt"""
    print_header("📦 Instalando Dependências do Projeto")
    
    if not os.path.exists('requirements.txt'):
        print("❌ ERRO: Arquivo requirements.txt não encontrado!")
        return False
    
    try:
        print("Instalando pacotes de requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências do projeto instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRO ao instalar dependências: {e}")
        return False

def install_dashboard_deps():
    """Instala dependências do dashboard"""
    print_header("🌐 Instalando Dependências do Dashboard")
    
    try:
        print("Instalando Flask e Flask-CORS...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
        print("✅ Dependências do dashboard instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERRO ao instalar Flask: {e}")
        return False

def verify_installation():
    """Verifica se todas as bibliotecas foram instaladas"""
    print_header("✅ Verificando Instalação")
    
    required_packages = [
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient',
        'anthropic',
        'docx',
        'schedule',
        'dotenv',
        'PIL',
        'PyPDF2',
        'flask',
        'flask_cors'
    ]
    
    missing = []
    installed = []
    
    for package in required_packages:
        try:
            __import__(package)
            installed.append(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - FALTANDO")
    
    print(f"\n📊 Resumo: {len(installed)}/{len(required_packages)} pacotes instalados")
    
    if missing:
        print(f"\n⚠️ Pacotes faltando: {', '.join(missing)}")
        return False
    
    return True

def check_config_files():
    """Verifica arquivos de configuração"""
    print_header("⚙️ Verificando Configurações")
    
    files_to_check = {
        '.env': 'Variáveis de ambiente',
        'credentials.json': 'Credenciais Google Drive',
        'token.json': 'Token de autenticação'
    }
    
    all_ok = True
    for file, desc in files_to_check.items():
        if os.path.exists(file):
            print(f"✅ {desc} ({file})")
        else:
            print(f"⚠️ {desc} ({file}) - NÃO ENCONTRADO")
            all_ok = False
    
    return all_ok

def show_next_steps():
    """Mostra próximos passos"""
    print_header("🎯 Próximos Passos")
    
    print("""
1. Para executar o sistema principal:
   python main_v10_fase3.py

2. Para executar o dashboard web:
   python dashboard_server.py
   Depois acesse: http://localhost:5000

3. Para verificar o sistema:
   python verificar_sistema.py

4. Consulte INSTALACAO.md para mais informações
    """)

def main():
    """Função principal"""
    print_header("🚀 Instalador - Sistema de Petições Automatizadas")
    
    # Verificar Python
    if not check_python():
        sys.exit(1)
    
    # Instalar dependências
    if not install_requirements():
        print("\n❌ Falha ao instalar dependências do projeto")
        sys.exit(1)
    
    # Instalar Flask
    if not install_dashboard_deps():
        print("\n⚠️ Aviso: Dashboard pode não funcionar corretamente")
    
    # Verificar instalação
    if not verify_installation():
        print("\n⚠️ Algumas dependências podem estar faltando")
    
    # Verificar configurações
    config_ok = check_config_files()
    
    # Próximos passos
    show_next_steps()
    
    # Resumo final
    print_header("✅ Instalação Concluída!")
    
    if config_ok:
        print("🎉 Tudo pronto! O sistema está configurado e pronto para uso.")
    else:
        print("⚠️ Instalação concluída, mas alguns arquivos de configuração estão faltando.")
        print("   Verifique o guia de instalação para mais detalhes.")

if __name__ == "__main__":
    main()
