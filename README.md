# 🏛️ Sistema de Automação de Petições Jurídicas

Sistema inteligente para automação de geração de petições trabalhistas utilizando IA (Claude/Anthropic e Gemini), integrado com Google Drive para gestão de documentos.

## 📋 Funcionalidades

- **Geração Automática de Petições**: Utiliza IA para criar petições jurídicas baseadas em templates e documentos fornecidos
- **Processamento de Vídeos**: Transcrição e análise de vídeos de depoimentos de clientes
- **Cronologia Automática**: Geração de cronologia dos fatos a partir de documentos e transcrições
- **Cálculos Trabalhistas**: Sistema de cálculo de verbas trabalhistas (horas extras, adicional noturno, etc.)
- **Integração Google Drive**: Sincronização automática com pastas do Google Drive
- **Dashboard Web**: Interface visual para gerenciamento de casos e petições
- **Sistema de Qualidade**: Validação e verificação de petições geradas com Prompt Master
- **Jurisprudência**: Busca e inclusão de jurisprudências relevantes

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **Anthropic Claude API** - IA principal para geração de petições
- **Google Gemini API** - IA auxiliar para análise de documentos
- **Google Drive API** - Gestão de documentos
- **Flask** - Dashboard web
- **python-docx** - Manipulação de documentos Word
- **PyMuPDF** - Processamento de PDFs
- **Schedule** - Automação de tarefas

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/diogo-91/adv.git
cd adv
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

Ou use o script de instalação automática:
```bash
python instalar_dependencias_windows.py
```

### 5. Configure as variáveis de ambiente

1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edite o arquivo `.env` e preencha com suas credenciais:
   - **ANTHROPIC_API_KEY**: Sua chave da API Anthropic (obtenha em https://console.anthropic.com/)
   - **GEMINI_API_KEY**: Sua chave da API Google Gemini (obtenha em https://makersuite.google.com/app/apikey)
   - **IDs das pastas do Google Drive**: IDs das pastas onde os documentos serão armazenados
   - **IDs dos modelos**: IDs dos documentos modelo no Google Drive

### 6. Configure o Google Drive API

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a Google Drive API
4. Crie credenciais OAuth 2.0
5. Baixe o arquivo `credentials.json` e coloque na raiz do projeto

## 🚀 Uso

### Iniciar o sistema principal

```bash
python main_v10_fase3.py
```

Este script monitora as pastas do Google Drive e processa automaticamente novos casos.

### Iniciar o Dashboard Web

```bash
python dashboard_server.py
```

Acesse o dashboard em: `http://localhost:5000`

### Verificar o sistema

```bash
python verificar_sistema.py
```

### Testar o Prompt Master

```bash
python testar_prompt_master.py
```

## 📁 Estrutura do Projeto

```
peticoes-automatizadas/
├── main_v10_fase3.py              # Script principal
├── dashboard_server.py            # Servidor do dashboard web
├── prompt_master.py               # Sistema de prompts avançado
├── validacao_prompt_master.py    # Validação de petições
├── calculos_trabalhistas.py      # Cálculos de verbas trabalhistas
├── verificacao_qualidade.py      # Sistema de qualidade
├── templates_peticao/            # Templates de petições
│   ├── merito_*.txt
│   ├── preliminar_*.txt
│   └── prompt_master/
├── telas/                        # Arquivos HTML do dashboard
│   └── dashboard_v2.html
├── .env                          # Variáveis de ambiente (NÃO COMMITAR)
├── credentials.json              # Credenciais Google (NÃO COMMITAR)
└── requirements.txt              # Dependências Python
```

## 🔒 Segurança

⚠️ **IMPORTANTE**: Nunca faça commit dos seguintes arquivos:
- `.env` - Contém suas API keys
- `credentials.json` - Credenciais do Google
- `token.json` - Token de autenticação do Google
- Arquivos de clientes ou dados sensíveis

Estes arquivos já estão incluídos no `.gitignore`.

## 📖 Documentação Adicional

- [Como usar o Prompt Master](COMO_USAR_PROMPT_MASTER.md)
- [Instruções de Instalação](INSTALACAO.md)

## 🤝 Contribuindo

Este é um projeto privado para uso interno do escritório. Para sugestões ou melhorias, entre em contato com o desenvolvedor.

## 📝 Licença

Uso privado - Todos os direitos reservados.

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs em `logs_auditoria/` e `logs_prints/`
2. Execute `python verificar_sistema.py` para diagnóstico
3. Consulte a documentação dos arquivos `.md`

---

**Desenvolvido para automação jurídica trabalhista** 🏛️⚖️
