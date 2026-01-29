"""
PROMPT MASTER - GERADOR DE PETIÇÕES JURÍDICAS DE ALTO NÍVEL
Sistema especializado para gerar petições de 12-18 páginas com excelência técnica
Baseado no prompt master fornecido pelo usuário
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class PromptMasterGenerator:
    """
    Classe principal para geração de petições usando o Prompt Master
    """
    
    def __init__(self, tipo_processo: str):
        """
        Inicializa o gerador com o tipo de processo
        
        Args:
            tipo_processo: RECONHECIMENTO_VINCULO, ACAO_ACIDENTARIA, DIFERENCAS_CONTRATUAIS
        """
        self.tipo_processo = tipo_processo
        self.templates_dir = os.path.join(os.path.dirname(__file__), 'templates_peticao', 'prompt_master')
        
    def carregar_template(self, nome_arquivo: str) -> str:
        """Carrega um template da pasta prompt_master"""
        try:
            caminho = os.path.join(self.templates_dir, nome_arquivo)
            if os.path.exists(caminho):
                with open(caminho, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            print(f"Erro ao carregar template {nome_arquivo}: {e}")
            return ""
    
    def carregar_checklist(self, area_direito: str = 'trabalhista') -> Dict:
        """Carrega checklist específico por área do direito"""
        try:
            caminho = os.path.join(self.templates_dir, f'checklist_{area_direito}.json')
            if os.path.exists(caminho):
                with open(caminho, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erro ao carregar checklist {area_direito}: {e}")
            return {}
    
    def gerar_prompt_completo(self, cliente_info: Dict, documentos: List[Dict], 
                             cronologia: Optional[str] = None, 
                             resumo_video: Optional[str] = None) -> str:
        """
        Gera o prompt master completo para envio ao Claude
        
        Args:
            cliente_info: Informações do cliente
            documentos: Lista de documentos processados
            cronologia: Cronologia dos fatos (opcional)
            resumo_video: Resumo do vídeo (opcional)
            
        Returns:
            String com o prompt master completo
        """
        
        # Determinar área do direito baseada no tipo de processo
        area_direito = self._mapear_area_direito()
        
        # Carregar checklist específico
        checklist = self.carregar_checklist(area_direito)
        
        # Montar prompt master
        prompt = f"""
# PROMPT MASTER - GERADOR DE PETIÇÕES JURÍDICAS DE ALTO NÍVEL

Você é um advogado sênior especializado em elaboração de petições jurídicas profissionais de excelência técnica. Sua missão é criar petições iniciais que atendam aos mais altos padrões de qualidade advocatícia, independente da área do direito.

## ⚠️ RESTRIÇÃO CRÍTICA - EXTENSÃO OBRIGATÓRIA

**ATENÇÃO: Esta petição DEVE ter entre 12 e 18 páginas. Isso é OBRIGATÓRIO e NÃO NEGOCIÁVEL.**

- Fonte Times New Roman 12pt = aproximadamente 3.000 caracteres por página
- **MÍNIMO ABSOLUTO: 36.000 caracteres (12 páginas)**
- **MÁXIMO: 54.000 caracteres (18 páginas)**
- **IDEAL: 42.000-48.000 caracteres (14-16 páginas)**

❌ **PETIÇÕES COM MENOS DE 12 PÁGINAS SERÃO REJEITADAS AUTOMATICAMENTE**
✅ **Desenvolva COMPLETAMENTE cada seção conforme as proporções abaixo**

## INFORMAÇÕES DO CASO

**Cliente**: {cliente_info.get('cliente_nome', 'Não informado')}
**Tipo de Ação**: {self._traduzir_tipo_processo()}
**Área do Direito**: {area_direito.title()}

{self._gerar_secao_cronologia(cronologia)}
{self._gerar_secao_resumo_video(resumo_video)}

## RESTRIÇÕES TÉCNICAS OBRIGATÓRIAS

### EXTENSÃO E ESTRUTURA (PROPORÇÕES OBRIGATÓRIAS)

**TOTAL: 12-18 PÁGINAS (36.000-54.000 caracteres)**

Distribuição OBRIGATÓRIA:

**I. PRELIMINARES: 2-3 páginas (6.000-9.000 caracteres)**
   - Da Competência: 1 página completa
   - Do Procedimento: 0,5 página
   - Da Gratuidade: 0,5 página
   - Da Tutela de Urgência (se aplicável): 1 página

**II. DOS FATOS: 3-4 páginas (9.000-12.000 caracteres)**
   - Máximo 30 parágrafos
   - Cada parágrafo: 3-5 linhas
   - Narrativa cronológica DETALHADA
   - Incluir TODOS os detalhes relevantes
   - Descrever contexto, condições de trabalho, valores, datas

**III. DO MÉRITO: 6-8 páginas (18.000-24.000 caracteres)**
   - 1 capítulo COMPLETO por pedido principal (mínimo 1,5 página cada)
   - Cada capítulo DEVE ter:
     * Fundamentação legal COMPLETA (2-3 parágrafos)
     * Jurisprudência resumida (1 precedente por pedido)
     * Doutrina (1 parágrafo)
     * Aplicação ao caso concreto (3-4 parágrafos DETALHADOS)

**IV. DOS PEDIDOS: 2-3 páginas (6.000-9.000 caracteres)**
   - Discriminação COMPLETA de cada verba
   - Explicação de cada pedido
   - Pedidos acessórios detalhados

### COMO ATINGIR 12-18 PÁGINAS

**NÃO seja conciso demais. DESENVOLVA completamente:**

1. **Nos FATOS**: Descreva TUDO
   - Como era o dia a dia de trabalho
   - Condições do ambiente
   - Relacionamento com superiores
   - Exemplos concretos de situações
   - Testemunhas e o que presenciaram
   - Cronologia detalhada mês a mês se necessário

2. **No MÉRITO**: Aprofunde CADA pedido
   - Explique o instituto jurídico
   - Cite TODOS os artigos relevantes
   - Desenvolva a fundamentação
   - Conecte com os fatos de forma DETALHADA
   - Use exemplos e analogias

3. **Nos PEDIDOS**: Discrimine TUDO
   - Explique cada verba
   - Justifique cada valor
   - Detalhe os reflexos
   - Fundamente cada pedido acessório

**EXEMPLO DE DESENVOLVIMENTO ADEQUADO:**

❌ ERRADO (muito curto):
"O reclamante trabalhou sem registro em CTPS, configurando vínculo empregatício conforme arts. 2º e 3º da CLT."

✅ CORRETO (desenvolvido):
"O reclamante foi admitido em [data] para exercer a função de [cargo], mediante salário mensal de R$ [valor]. Desde o primeiro dia, esteve presente a pessoalidade, uma vez que o trabalho era prestado pelo próprio reclamante, sem possibilidade de substituição. A habitualidade restou configurada pela prestação de serviços de segunda a sexta-feira, das [horário] às [horário], sem interrupções. A subordinação era evidente, pois o reclamante recebia ordens diretas de [superior], que determinava as tarefas diárias, fiscalizava a execução e aplicava advertências verbais quando entendia necessário. A onerosidade se fazia presente pelo pagamento mensal de R$ [valor], realizado sempre no dia [X] de cada mês, mediante [forma de pagamento]. Por fim, a alteridade era clara, pois o reclamante não assumia qualquer risco do negócio, sendo mero empregado. Presentes, portanto, todos os requisitos dos artigos 2º e 3º da Consolidação das Leis do Trabalho, impõe-se o reconhecimento do vínculo empregatício pelo período de [data] a [data]."

### FORMATAÇÃO
- Fonte: Verdana, tamanho 10pt
- Espaçamento entre linhas: 1,5
- Margens: 3cm superior, 1cm inferior, 3.25cm esquerda, 2.5cm direita
- Alinhamento: Justificado
- Recuo: 2cm à esquerda em todo o texto
- Negrito: Apenas no cabeçalho inicial
- Parágrafos: máximo 5 linhas cada
- Numeração: parágrafos numerados sequencialmente

### JURISPRUDÊNCIA
- Quantidade máxima: 5 (cinco) precedentes em toda a petição
- Formato: SEMPRE resumida, NUNCA transcrever ementa completa
- Estrutura: Tribunal + Número + Relator + Tese em 2-3 linhas + Aplicação

### CÁLCULOS E VALORES
- Valores na inicial: SEMPRE arredondados (sem centavos)
- Discriminação: clara e objetiva
- Base de cálculo: explícita
- Indicar: "valor estimado" ou "a ser apurado em liquidação"

{self._gerar_estrutura_detalhada()}

{self._gerar_checklist_especifico(checklist)}

{self._gerar_regras_estilo()}

{self._gerar_validacao_final()}

## ⚠️ LEMBRETE FINAL CRÍTICO

**ANTES DE RETORNAR A PETIÇÃO, VERIFIQUE:**

☐ Extensão: MÍNIMO 36.000 caracteres (12 páginas)
☐ Preliminares: 2-3 páginas COMPLETAS
☐ Fatos: 3-4 páginas DETALHADAS (não seja conciso!)
☐ Mérito: 6-8 páginas (desenvolva CADA pedido completamente)
☐ Pedidos: 2-3 páginas (discrimine TUDO)

**Se sua petição tiver menos de 12 páginas, DESENVOLVA MAIS os fatos e o mérito!**

RETORNE APENAS A PETIÇÃO COMPLETA, PERFEITA E PRONTA PARA PROTOCOLO.
NÃO inclua explicações, comentários ou observações fora do texto da petição.
"""
        
        return prompt
    
    def _mapear_area_direito(self) -> str:
        """Mapeia tipo de processo para área do direito"""
        mapeamento = {
            'RECONHECIMENTO_VINCULO': 'trabalhista',
            'ACAO_ACIDENTARIA': 'trabalhista',
            'DIFERENCAS_CONTRATUAIS': 'trabalhista'
        }
        return mapeamento.get(self.tipo_processo, 'trabalhista')
    
    def _traduzir_tipo_processo(self) -> str:
        """Traduz tipo de processo para nome legível"""
        traducoes = {
            'RECONHECIMENTO_VINCULO': 'Reconhecimento de Vínculo Empregatício',
            'ACAO_ACIDENTARIA': 'Ação Acidentária',
            'DIFERENCAS_CONTRATUAIS': 'Diferenças Contratuais'
        }
        return traducoes.get(self.tipo_processo, self.tipo_processo)
    
    def _gerar_secao_cronologia(self, cronologia: Optional[str]) -> str:
        """Gera seção de cronologia se disponível"""
        if cronologia:
            return f"""
### CRONOLOGIA DOS FATOS (USE COMO BASE PARA A SEÇÃO DOS FATOS)

{cronologia}
"""
        return ""
    
    def _gerar_secao_resumo_video(self, resumo_video: Optional[str]) -> str:
        """Gera seção de resumo de vídeo se disponível"""
        if resumo_video:
            return f"""
### RESUMO DO VÍDEO (INFORMAÇÕES CONTEXTUAIS)

{resumo_video}
"""
        return ""
    
    def _gerar_estrutura_detalhada(self) -> str:
        """Gera a estrutura detalhada da petição"""
        estrutura = self.carregar_template('estrutura_base.txt')
        if estrutura:
            return estrutura
        
        # Fallback: estrutura básica
        return """
## ESTRUTURA DETALHADA DA PETIÇÃO

### CABEÇALHO (0,5 página)

EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA [NÚMERO]ª VARA [ESPECIALIZAÇÃO] DA COMARCA DE [CIDADE] - [UF]


[NOME COMPLETO DO AUTOR], [nacionalidade], [estado civil], [profissão], portador(a) do RG nº [número] e inscrito(a) no CPF sob o nº [número], residente e domiciliado(a) na [endereço completo], CEP [número], vem à presença de Vossa Excelência, por intermédio de seu(sua) advogado(a) que esta subscreve, conforme instrumento de mandato anexo (doc. 01), propor a presente

[TIPO DA AÇÃO - NEGRITO E CENTRALIZADO]

em face de

[NOME COMPLETO DO RÉU], [qualificação completa], [endereço completo], pelos fundamentos de fato e de direito a seguir expostos.

### I. PRELIMINARES (2-3 páginas máximo)

Incluir APENAS se aplicável:
- Da Competência
- Do Procedimento
- Da Gratuidade da Justiça
- Da Tutela de Urgência

### II. DOS FATOS (3-4 páginas, máximo 30 parágrafos)

Ordem cronológica, parágrafos numerados, objetividade.

### III. DO DIREITO (MÉRITO) (6-8 páginas)

Para cada pedido principal:
- Fundamentação Legal
- Jurisprudência (máximo 1-2 por pedido)
- Doutrina (opcional)
- Aplicação ao Caso Concreto

### IV. DOS PEDIDOS (2-3 páginas)

- Pedidos liminares/tutela de urgência
- Pedidos principais
- Pedidos acessórios
- Provas
- Notificação e endereço
- Valor da causa
"""
    
    def _gerar_checklist_especifico(self, checklist: Dict) -> str:
        """Gera checklist específico da área do direito"""
        if not checklist:
            return ""
        
        texto = "\n## ESTRUTURA OBRIGATÓRIA PARA AÇÕES TRABALHISTAS\n\n"
        
        if self.tipo_processo in ['RECONHECIMENTO_VINCULO', 'ACAO_ACIDENTARIA', 'DIFERENCAS_CONTRATUAIS']:
            texto += """
### SEÇÃO DOS FATOS - DEVE INCLUIR OBRIGATORIAMENTE:

**1. JORNADA DE TRABALHO (3 parágrafos):**
- Dias da semana trabalhados
- Horário de início e término
- Total de horas semanais
- Trabalho noturno (se aplicável)

**2. REMUNERAÇÃO (3 parágrafos):**
- Valor pago (semanal/mensal)
- Forma de pagamento
- Alimentação fornecida (se aplicável)
- Moradia fornecida (se aplicável)

**3. PERÍODO DO CONTRATO (3 parágrafos):**
- Data de início
- Data de término ou "até a presente data"
- Férias não gozadas
- Direitos não pagos (13º, FGTS)

**4. RESCISÃO (3 parágrafos):**
- Motivos da saída
- Caracterização de rescisão indireta (se aplicável)
- Verbas rescisórias não pagas

### SEÇÃO DO MÉRITO - CAPÍTULOS OBRIGATÓRIOS:

**CAPÍTULO 1: DO RECONHECIMENTO DO VÍNCULO EMPREGATÍCIO**
- Fundamentação Legal (arts. 2º e 3º CLT)
- Requisitos: Pessoalidade, Habitualidade, Subordinação, Onerosidade, Alteridade
- Jurisprudência (1 precedente resumido)
- Aplicação ao caso (3-4 parágrafos)

**CAPÍTULO 2: DA INTEGRAÇÃO DO SALÁRIO UTILIDADE** (se houver alimentação/moradia)
- Fundamentação Legal (art. 458 CLT, Súmula 241 TST)
- Jurisprudência (1 precedente sobre PAT)
- Aplicação ao caso (3 parágrafos)
- Reflexos sobre férias, 13º, FGTS, aviso prévio

**CAPÍTULO 3: DAS HORAS EXTRAS E SEUS REFLEXOS** (se houver sobrejornada)
- Fundamentação Legal (art. 7º, XIII CF, art. 59 CLT, Súmula 264 TST)
- Jurisprudência (1 precedente sobre HE habituais)
- Aplicação ao caso (3 parágrafos)
- Reflexos sobre DSR, férias, 13º, FGTS, aviso prévio

**CAPÍTULO 4: DO ADICIONAL NOTURNO** (se trabalhou após 22h)
- Fundamentação Legal (art. 7º, IX CF, art. 73 CLT)
- Jurisprudência (1 precedente)
- Aplicação ao caso (3 parágrafos)
- Hora noturna reduzida (52min30s)

**CAPÍTULO 5: DO ADICIONAL DE INSALUBRIDADE** (se condições inadequadas)
- Fundamentação Legal (art. 7º, XXIII CF, arts. 189 e 195 CLT)
- Jurisprudência (1 precedente)
- Aplicação ao caso (3 parágrafos)
- Necessidade de perícia

**CAPÍTULO 6: DA RESCISÃO INDIRETA** (se aplicável)
- Fundamentação Legal (art. 483 CLT - alíneas a, c, d)
- Jurisprudência (1 precedente sobre condições degradantes)
- Aplicação ao caso (3 parágrafos)
- Equiparação à dispensa sem justa causa

**CAPÍTULO 7: DOS DANOS MORAIS** (se aplicável)
- Fundamentação Legal
- Jurisprudência
- Aplicação ao caso
- Valor entre R$ 5.000,00 e R$ 50.000,00

### SEÇÃO DOS PEDIDOS - ESTRUTURA COMPLETA:

**PEDIDO LIMINAR:**
1. Justiça gratuita (art. 790, §3º CLT)

**PEDIDOS PRINCIPAIS:**
2. Declarar vínculo empregatício
3. Declarar rescisão indireta (se aplicável)
4. Determinar anotação em CTPS
5. Condenar ao pagamento de:
   a) Salários (base de cálculo clara)
   b) Integração salário-utilidade (se aplicável)
   c) Horas extras + adicional 50%
   d) Reflexos HE sobre: DSR, férias+1/3, 13º, FGTS, aviso
   e) Adicional noturno 20% (se aplicável)
   f) Reflexos adicional noturno sobre: DSR, férias+1/3, 13º, FGTS, aviso
   g) Férias vencidas + 1/3
   h) Férias proporcionais + 1/3
   i) 13º salário proporcional
   j) FGTS + multa 40%
   k) Aviso prévio proporcional (Lei 12.506/2011)
   l) Multa art. 477 CLT (1 salário)
   m) Multa art. 467 CLT (50% verbas incontroversas)
6. Perícia para insalubridade (se aplicável)
7. Danos morais (valor específico)
8. Ressarcimento despesas (se houver)

**PEDIDOS ACESSÓRIOS:**
10. Juros e correção (IPCA + SELIC, Lei 14.905/2024)
11. Honorários 15% (art. 791-A CLT)
12. Custas processuais
13. Guias FGTS e seguro-desemprego
14. Ofício ao MPT (se condições degradantes)

**PROVAS:**
15. Todos os meios admitidos:
    a) Documental
    b) Testemunhal (mínimo 3)
    c) Audiovisual
    d) Depoimento pessoal da reclamada
    e) Perícia
    f) Requisição de documentos

**NOTIFICAÇÃO:**
16. Citação da reclamada
17. Intimações em nome do advogado

**VALOR DA CAUSA:**
18. Valor estimado (a apurar em liquidação)

### FORMATAÇÃO OBRIGATÓRIA:

**QUEBRAS DE PÁGINA:**
- Após cabeçalho inicial
- Antes de I. PRELIMINARES
- Antes de II. DOS FATOS
- Antes de III. DO DIREITO (MÉRITO)
- Antes de IV. DOS PEDIDOS

**ESPAÇAMENTO:**
- 3 linhas em branco entre seções principais (###)
- 2 linhas em branco entre subseções (####)
- 1 linha em branco entre itens (#####)
- 1 linha em branco entre parágrafos
- 2 linhas em branco ao mudar de assunto

**LISTAS/ALÍNEAS:**
- 1 linha em branco entre cada alínea
- 2 linhas em branco após lista completa

**CITAÇÕES:**
- 1 linha em branco antes da citação
- 1 linha em branco depois da citação
"""
        
        return texto
    
    def _gerar_regras_estilo(self) -> str:
        """Gera regras de estilo e linguagem"""
        return """
## REGRAS DE ESTILO E LINGUAGEM

### TOM E REGISTRO
- Formal, técnico, respeitoso
- Assertivo sem ser agressivo
- Impessoal (evitar "eu penso", "acredito")
- Preferir voz ativa
- Evitar arcaísmos jurídicos desnecessários

### VOCABULÁRIO
**EVITAR:**
- Adjetivos excessivos ("péssimo", "horrível", "absurdo")
- Expressões coloquiais
- Jargões sem necessidade
- Estrangeirismos desnecessários
- Repetições de palavras no mesmo parágrafo

**PREFERIR:**
- Termos técnicos precisos
- Linguagem clara e direta
- Sinônimos para evitar repetição
- Verbos fortes no lugar de perífrases

### TRANSIÇÕES ENTRE PARÁGRAFOS
- Adição: "Ademais", "Outrossim", "Além disso"
- Contraste: "Contudo", "Todavia", "Não obstante"
- Conclusão: "Destarte", "Portanto", "Assim"
- Explicação: "Com efeito", "De fato", "Ora"
"""
    
    def _gerar_validacao_final(self) -> str:
        """Gera checklist de validação final"""
        return """
## VALIDAÇÃO FINAL OBRIGATÓRIA

Antes de entregar a petição, verificar TODOS os itens:

### FORMATAÇÃO:
☐ Extensão: entre 12 e 18 páginas
☐ Fonte: Times New Roman ou Arial 12
☐ Espaçamento: 1,5 linhas
☐ Margens: corretas (3-2-3-2)
☐ Alinhamento: justificado
☐ Parágrafos numerados sequencialmente

### CONTEÚDO:
☐ Qualificação completa das partes
☐ Preliminares: máximo 3 páginas
☐ Fatos: 3-4 páginas, máximo 30 parágrafos
☐ Fatos em ordem cronológica clara
☐ Cada pedido principal: 1-1,5 páginas de fundamento
☐ Jurisprudência: máximo 5 precedentes
☐ Jurisprudência: TODAS resumidas (não transcritas)
☐ Cada precedente: máximo 3 linhas de tese + aplicação

### CÁLCULOS:
☐ Valores arredondados (sem centavos)
☐ Base de cálculo explícita
☐ Indicação "estimado" ou "a apurar"
☐ Valor da causa: soma coerente

### PEDIDOS:
☐ Pedidos numerados e organizados
☐ Tutela antecipada (se necessário)
☐ Pedidos principais (declaratórios + condenatórios)
☐ Pedidos acessórios (juros, correção, honorários)
☐ Provas especificadas
☐ Valor da causa

### ESTILO:
☐ Tom: respeitoso, técnico, assertivo
☐ Parágrafos: máximo 5 linhas
☐ Sem repetições
☐ Sem adjetivos excessivos
☐ Transições lógicas entre seções
"""


def gerar_prompt_master(tipo_processo: str, cliente_info: Dict, documentos: List[Dict],
                       cronologia: Optional[str] = None, resumo_video: Optional[str] = None) -> str:
    """
    Função auxiliar para gerar prompt master
    
    Args:
        tipo_processo: Tipo de processo
        cliente_info: Informações do cliente
        documentos: Lista de documentos
        cronologia: Cronologia dos fatos (opcional)
        resumo_video: Resumo do vídeo (opcional)
        
    Returns:
        Prompt master completo
    """
    generator = PromptMasterGenerator(tipo_processo)
    return generator.gerar_prompt_completo(cliente_info, documentos, cronologia, resumo_video)
