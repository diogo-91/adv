# Guia Rápido: Como Usar o Prompt Master

## Opção 1: Via Script de Teste (Mais Fácil)

1. **Execute o script de teste:**
   ```bash
   cd c:\Users\Tutta\Documents\PROJETOS\peticoes-automatizadas
   python testar_prompt_master.py
   ```

2. **Escolha o modo:**
   - Digite `1` para modo padrão
   - Digite `2` para **Prompt Master**

3. **Aguarde a geração** (2-3 minutos no modo Prompt Master)

4. **Veja o resultado** em `peticao_teste.txt`

---

## Opção 2: Modificar o Sistema Principal

### No arquivo `main_v10_fase3.py`, localize onde `gerar_peticao_com_claude` é chamado e adicione:

```python
# Exemplo de chamada com Prompt Master ATIVADO
peticao = gerar_peticao_com_claude(
    service=service,
    cliente_info=cliente_info,
    documentos_completos=documentos,
    tipo_processo='RECONHECIMENTO_VINCULO',
    cronologia_fatos=cronologia,
    resumo_video=resumo,
    procuracao=procuracao,
    usar_prompt_master=True  # ← ADICIONE ESTA LINHA
)
```

---

## Opção 3: Integração no Dashboard (Futuro)

Para integrar completamente no dashboard, será necessário:

### 1. Modificar `dashboard_v2.html`

Adicionar checkbox no modal de geração:

```html
<div class="form-check mb-3">
    <input type="checkbox" class="form-check-input" id="usarPromptMaster">
    <label class="form-check-label" for="usarPromptMaster">
        ✨ <strong>Usar Prompt Master</strong> 
        <small class="text-muted">(Petição de Alto Nível - 12-18 páginas)</small>
    </label>
</div>
```

### 2. Modificar JavaScript para capturar o valor

```javascript
const usarPromptMaster = document.getElementById('usarPromptMaster').checked;

// Enviar na requisição
fetch('/api/gerar-peticao', {
    method: 'POST',
    body: JSON.stringify({
        cliente_id: clienteId,
        usar_prompt_master: usarPromptMaster  // ← Novo parâmetro
    })
})
```

### 3. Modificar `dashboard_server.py`

```python
@app.route('/api/gerar-peticao', methods=['POST'])
def gerar_peticao_api():
    data = request.json
    usar_prompt_master = data.get('usar_prompt_master', False)
    
    # Passar para a função de geração
    peticao = gerar_peticao_com_claude(
        # ... outros parâmetros ...
        usar_prompt_master=usar_prompt_master
    )
```

---

## O Que Esperar

### Modo Padrão
- ⏱️ Tempo: 1-2 minutos
- 📄 Extensão: 5-10 páginas
- 💰 Custo: Normal
- ✅ Qualidade: Boa

### Modo Prompt Master
- ⏱️ Tempo: 2-3 minutos
- 📄 Extensão: 12-18 páginas (obrigatório)
- 💰 Custo: 2-3x maior
- 🏆 Qualidade: Excelência técnica

### Validação Automática (Prompt Master)
Após gerar, você verá no console:
```
✅ Formatação Prompt Master aplicada (Times New Roman 12, margens 3-2-3-2)
- Score Prompt Master: 85/100 (MUITO BOM)
- ✓ Extensão adequada: ~14.2 páginas
- ✓ DOS FATOS adequada: ~3.5 páginas, 28 parágrafos
- ✓ DO MÉRITO adequado: ~7.1 páginas
```

---

## Dicas

1. **Use Prompt Master para casos importantes** - A qualidade é significativamente superior
2. **Tenha documentos completos** - Quanto mais informação, melhor a petição
3. **Revise o relatório de validação** - Ele indica pontos de melhoria
4. **Compare os modos** - Gere a mesma petição nos dois modos para ver a diferença

---

## Próximos Passos

✅ **Implementação Core**: Completa
✅ **Script de Teste**: Criado
⏳ **Dashboard HTML**: Pendente (manual)

Para completar a integração no dashboard, siga as instruções da "Opção 3" acima.
