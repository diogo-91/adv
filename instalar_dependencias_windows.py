"""
Script de Instalação para Windows
Sistema de Petições Automatizadas

Versão otimizada para Windows com tratamento de erros de compilação.
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
        return False
    
    return True

def upgrade_pip():
    """Atualiza pip para última versão"""
    print_header("🔧 Atualizando pip")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ pip atualizado com sucesso!")
        return True
    except:
        print("⚠️ Não foi possível atualizar pip, continuando...")
        return True

def install_package(package_name, version=None):
    """Instala um pacote específico"""
    try:
        if version:
            package = f"{package_name}=={version}"
        else:
            package = package_name
        
        print(f"  Instalando {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
        print(f"  ✅ {package_name} instalado")
        return True
    except:
        print(f"  ❌ Erro ao instalar {package_name}")
        return False

def install_dependencies():
    """Instala dependências uma por uma"""
    print_header("📦 Instalando Dependências")
    
    # Lista de pacotes em ordem de instalação
    packages = [
        ("google-auth", "2.34.0"),
        ("google-auth-oauthlib", "1.2.1"),
        ("google-auth-httplib2", "0.2.0"),
        ("google-api-python-client", "2.147.0"),
        ("anthropic", "0.39.0"),
        ("python-docx", "1.1.2"),
        ("schedule", "1.2.2"),
        ("python-dotenv", "1.0.1"),
        ("pymupdf", None),
        ("Pillow", "10.4.0"),
        ("PyPDF2", "3.0.1"),
        ("flask", None),
        ("flask-cors", None)
    ]
    
    success_count = 0
    failed = []
    
    for package_name, version in packages:
        if install_package(package_name, version):
            success_count += 1
        else:
            failed.append(package_name)
    
    print(f"\n📊 Resumo: {success_count}/{len(packages)} pacotes instalados")
    
    if failed:
        print(f"\n⚠️ Pacotes com problemas: {', '.join(failed)}")
        
        # Tentar instalar Pillow sem versão específica se falhou
        if "Pillow" in failed:
            print("\n🔄 Tentando instalar Pillow de forma alternativa...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--only-binary", ":all:", "Pillow"])
                print("✅ Pillow instalado com sucesso!")
                failed.remove("Pillow")
            except:
                print("⚠️ Pillow ainda com problemas - funcionalidades de imagem podem ser limitadas")
    
    return len(failed) == 0

def verify_critical_packages():
    """Verifica pacotes críticos para o sistema"""
    print_header("✅ Verificando Pacotes Críticos")
    
    critical = {
        'google.auth': 'Google Drive (CRÍTICO)',
        'googleapiclient': 'Google Drive API (CRÍTICO)',
        'anthropic': 'IA Claude (CRÍTICO)',
        'docx': 'Manipulação Word (CRÍTICO)',
        'schedule': 'Agendamento',
        'dotenv': 'Configurações',
        'flask': 'Dashboard Web'
    }
    
    optional = {
        'PIL': 'Processamento de Imagens (OPCIONAL)',
        'PyPDF2': 'Leitura de PDFs (OPCIONAL)'
    }
    
    all_critical_ok = True
    
    print("Pacotes Críticos:")
    for package, desc in critical.items():
        try:
            __import__(package)
            print(f"  ✅ {desc}")
        except ImportError:
            print(f"  ❌ {desc} - FALTANDO!")
            all_critical_ok = False
    
    print("\nPacotes Opcionais:")
    for package, desc in optional.items():
        try:
            __import__(package)
            print(f"  ✅ {desc}")
        except ImportError:
            print(f"  ⚠️ {desc} - Não instalado (sistema funcionará sem)")
    
    return all_critical_ok

def check_config_files():
    """Verifica arquivos de configuração"""
    print_header("⚙️ Verificando Configurações")
    
    files = {
        '.env': 'Variáveis de ambiente',
        'credentials.json': 'Credenciais Google',
        'token.json': 'Token de autenticação'
    }
    
    for file, desc in files.items():
        if os.path.exists(file):
            print(f"✅ {desc} ({file})")
        else:
            print(f"⚠️ {desc} ({file}) - NÃO ENCONTRADO")

def show_next_steps():
    """Mostra próximos passos"""
    print_header("🎯 Próximos Passos")
    
    print("""
✅ SISTEMA PRONTO PARA USO!

1. Para executar o sistema principal:
   python main_v10_fase3.py

2. Para executar o dashboard web:
   python dashboard_server.py
   Depois acesse: http://localhost:5000

3. Para verificar o sistema:
   python verificar_sistema.py

📚 Consulte INSTALACAO.md para mais informações
    """)

def main():
    """Função principal"""
    print_header("🚀 Instalador Windows - Petições Automatizadas")
    
    # Verificar Python
    if not check_python():
        input("\nPressione Enter para sair...")
        sys.exit(1)
    
    # Atualizar pip
    upgrade_pip()
    
    # Instalar dependências
    print("\nEste processo pode levar alguns minutos...")
    install_dependencies()
    
    # Verificar pacotes críticos
    critical_ok = verify_critical_packages()
    
    # Verificar configurações
    check_config_files()
    
    # Próximos passos
    if critical_ok:
        show_next_steps()
        print_header("✅ Instalação Concluída com Sucesso!")
        print("🎉 Todos os pacotes críticos foram instalados!")
    else:
        print_header("⚠️ Instalação Concluída com Avisos")
        print("Alguns pacotes críticos não foram instalados.")
        print("O sistema pode não funcionar corretamente.")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
