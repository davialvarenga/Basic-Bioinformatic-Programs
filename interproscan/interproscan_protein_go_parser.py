#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: processa_GO_terms.py
Descrição:
  Lê um arquivo com proteínas e anotações de GO (ex: gerado pelo InterProScan),
  separa cada GO term, classifica em BP/MF/CC e salva um novo arquivo formatado.
  Agora, o script pede ao usuário os caminhos de entrada e saída na execução.
"""

# === Importante: não precisa de bibliotecas externas ===

# Solicita os caminhos interativamente
arquivo_entrada = input("📂 Digite o caminho do arquivo de entrada (.tab): ").strip()
arquivo_saida = input("💾 Digite o caminho do arquivo de saída (.tsv): ").strip()

# Exemplo de arquivo de entrada:
# LINF_200007600-T1       GO:0000027(InterPro)|GO:0005634(InterPro)|GO:0016887(InterPro)
# LINF_200007600-T1       GO:0000027(InterPro)|GO:0005634(InterPro)|GO:0016887(InterPro)
# LINF_200007600-T1       GO:0000027(InterPro)|GO:0005634(InterPro)|GO:0016887(InterPro)
# LINF_200007600-T1       GO:0000027(PANTHER)|GO:0000055(PANTHER)|GO:0005634(PANTHER)|GO:0030687(PANTHER)


# Abrir arquivos
with open(arquivo_entrada, 'r') as entrada, open(arquivo_saida, 'w') as saida:
    # Escrever cabeçalho
    saida.write("Protein_ID\tGO_Term\tCategory\tSource\n")

    # Processar cada linha do arquivo
    for linha in entrada:
        linha = linha.strip()
        if not linha:
            continue

        # Dividir a linha em protein_id e lista de GO terms
        partes = linha.split('\t')
        if len(partes) != 2:
            continue

        protein_id, go_entries = partes

        # Processar cada termo GO
        for entry in go_entries.split('|'):
            if not entry:
                continue

            # Extrair GO term e fonte
            try:
                go_part = entry.split('(')
                go_term = go_part[0]  # Pega GO:XXXXXXX
                source = go_part[1][:-1]  # Remove o parêntese final

                # Determinar a categoria
                go_num = go_term.split(':')[1]
                primeiro_digito = go_num[0]

                # Verificar termos pais principais primeiro
                if go_num == '0003674':
                    categoria = 'MF'
                elif go_num == '0008150':
                    categoria = 'BP'
                elif go_num == '0005575':
                    categoria = 'CC'
                # Determinar por intervalo numérico aproximado
                elif primeiro_digito == '0':
                    categoria = 'BP'
                elif primeiro_digito == '1':
                    categoria = 'MF'
                elif primeiro_digito == '2':
                    categoria = 'CC'
                else:
                    categoria = 'UNKNOWN'

                # Escrever no arquivo de saída
                saida.write(f"{protein_id}\t{go_term}\t{categoria}\t{source}\n")

            except (IndexError, AttributeError):
                continue

print("\n✅ Processamento concluído com sucesso!")
print(f"📄 Resultados salvos em: {arquivo_saida}")
