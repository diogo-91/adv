#!/bin/bash

# Script de instalação automática na VPS Ubuntu 24.04
# Uso: bash setup_vps.sh

set -e  # Parar em caso de erro

echo "🚀 Iniciando instalação do Sistema de Petições na VPS..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Atualizar sistema
echo -e "${YELLOW}📦 Atualizando sistema...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# 2. Instalar Docker (se não estiver instalado)
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}🐳 Instalando Docker...${NC}"
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo systemctl enable docker
    sudo systemctl start docker
    echo -e "${GREEN}✅ Docker instalado com sucesso!${NC}"
else
    echo -e "${GREEN}✅ Docker já está instalado${NC}"
fi

# 3. Instalar Docker Compose (standalone)
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}🔧 Instalando Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose instalado!${NC}"
else
    echo -e "${GREEN}✅ Docker Compose já está instalado${NC}"
fi

# 4. Instalar Git (se não estiver instalado)
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}📥 Instalando Git...${NC}"
    sudo apt-get install -y git
    echo -e "${GREEN}✅ Git instalado!${NC}"
else
    echo -e "${GREEN}✅ Git já está instalado${NC}"
fi

# 5. Criar diretório para a aplicação
APP_DIR="/opt/peticoes-automatizadas"
echo -e "${YELLOW}📁 Criando diretório da aplicação em ${APP_DIR}...${NC}"
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# 6. Clonar repositório
echo -e "${YELLOW}📥 Clonando repositório do GitHub...${NC}"
cd $APP_DIR
if [ -d ".git" ]; then
    echo -e "${YELLOW}Repositório já existe, fazendo pull...${NC}"
    git pull
else
    git clone https://github.com/diogo-91/adv.git .
fi

# 7. Criar diretório de dados
echo -e "${YELLOW}📂 Criando diretórios de dados...${NC}"
mkdir -p data/logs_auditoria
mkdir -p data/logs_prints
touch data/historico_peticoes.json
touch data/estatisticas_escritorio.json
touch data/jurisprudencias.json

# 8. Configurar arquivo .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚙️  Criando arquivo .env...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais!${NC}"
    echo -e "${YELLOW}Execute: nano $APP_DIR/.env${NC}"
else
    echo -e "${GREEN}✅ Arquivo .env já existe${NC}"
fi

# 9. Informações finais
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Instalação concluída com sucesso!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📝 Próximos passos:${NC}"
echo ""
echo "1. Configure suas credenciais:"
echo "   nano $APP_DIR/.env"
echo ""
echo "2. (Opcional) Adicione credentials.json do Google:"
echo "   scp credentials.json root@31.97.175.252:$APP_DIR/"
echo ""
echo "3. Inicie a aplicação:"
echo "   cd $APP_DIR"
echo "   docker-compose up -d"
echo ""
echo "4. Verifique os logs:"
echo "   docker-compose logs -f"
echo ""
echo "5. Acesse o dashboard:"
echo "   http://31.97.175.252:5000"
echo ""
echo -e "${YELLOW}📚 Comandos úteis:${NC}"
echo "   docker-compose ps              # Ver status dos containers"
echo "   docker-compose logs -f         # Ver logs em tempo real"
echo "   docker-compose restart         # Reiniciar serviços"
echo "   docker-compose down            # Parar tudo"
echo "   docker-compose up -d           # Iniciar em background"
echo ""
