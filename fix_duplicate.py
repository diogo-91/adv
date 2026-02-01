#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para remover função duplicada showCustomModal"""

import re

# Ler o arquivo
with open(r'c:\Users\Tutta\Documents\PROJETOS\peticoes-automatizadas\telas\dashboard_v2.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar e comentar a segunda ocorrência da função showCustomModal
found_first = False
in_duplicate = False
start_line = None
end_line = None

for i, line in enumerate(lines):
    if 'function showCustomModal(type, title, message)' in line:
        if not found_first:
            found_first = True
            print(f"Primeira função encontrada na linha {i+1}")
        else:
            start_line = i - 1  # Incluir o comentário anterior
            print(f"Segunda função (duplicada) encontrada na linha {i+1}")
            in_duplicate = True
    
    if in_duplicate and line.strip() == '}' and 'setTimeout' in lines[i-2]:
        end_line = i
        print(f"Fim da função duplicada na linha {i+1}")
        break

if start_line is not None and end_line is not None:
    # Comentar as linhas
    print(f"\nComentando linhas {start_line+1} a {end_line+1}")
    lines[start_line] = "        // DUPLICATA REMOVIDA - função já definida acima\n"
    lines[start_line+1] = "        /* " + lines[start_line+1]
    lines[end_line] = lines[end_line].rstrip() + " */\n"
    
    # Salvar
    with open(r'c:\Users\Tutta\Documents\PROJETOS\peticoes-automatizadas\telas\dashboard_v2.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Arquivo atualizado com sucesso!")
else:
    print("\n❌ Não foi possível encontrar a função duplicada")
