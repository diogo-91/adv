import os

html_path = r"c:\Users\Admin\Desktop\peticoes-automatizadas\telas\dashboard_v2.html"
css_path = r"c:\Users\Admin\Desktop\peticoes-automatizadas\new_style.css"

try:
    with open(html_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(css_path, 'r', encoding='utf-8') as f:
        new_css = f.read()

    start_idx = -1
    end_idx = -1

    for i, line in enumerate(lines):
        if "<style>" in line:
            start_idx = i
            break # Pega o primeiro style

    # Busca </style> APÓS o start
    for i in range(start_idx + 1, len(lines)):
         if "</style>" in lines[i]:
            end_idx = i
            break

    if start_idx != -1 and end_idx != -1:
        print(f"Substituindo CSS entre linha {start_idx+1} e {end_idx+1}")
        
        # Mantém até a linha do <style> (que deve ser limpa de conteúdo anterior se houver)
        # Se a linha do <style> tiver algo depois, quebra. Mas meu replace deixou <style> limpo no fim.
        
        new_lines = lines[:start_idx+1]
        new_lines.append(new_css + "\n")
        new_lines.extend(lines[end_idx:]) # Mantém do </style> pra frente
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("CSS atualizado com sucesso.")
    else:
        print(f"Indices não encontrados: Start {start_idx}, End {end_idx}")

except Exception as e:
    print(f"Erro: {e}")
