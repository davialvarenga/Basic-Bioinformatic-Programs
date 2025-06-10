import gzip

# Configurações
obo_file = "/home/dalvarenga/Documentos/4_leishmania_targets/2_go_analysis/go-basic.obo"  # Ou "go-basic.obo.gz" se for compactado
output_file = "/home/dalvarenga/Documentos/4_leishmania_targets/2_go_analysis/go_terms_vocabulary.tsv"

# Verifica se o arquivo está compactado
is_compressed = obo_file.endswith('.gz')

# Abre o arquivo OBO
open_func = gzip.open if is_compressed else open

with open_func(obo_file, 'rt') as obo, open(output_file, 'w') as out:
    out.write("GO_ID\tCategory\tName\tNamespace\n")  # Cabeçalho

    current_term = None
    for line in obo:
        line = line.strip()

        # Início de um novo termo GO
        if line == "[Term]":
            current_term = {}

        # Fim do termo atual - escrever no arquivo de saída
        elif line == "" and current_term:
            if 'id' in current_term and 'name' in current_term and 'namespace' in current_term:
                # Determinar a categoria baseada no namespace
                namespace = current_term['namespace']
                if namespace == 'molecular_function':
                    category = 'MF'
                elif namespace == 'biological_process':
                    category = 'BP'
                elif namespace == 'cellular_component':
                    category = 'CC'
                else:
                    category = 'UNKNOWN'

                # Escrever no arquivo de saída
                out.write(f"{current_term['id']}\t{category}\t{current_term['name']}\t{namespace}\n")
            current_term = None

        # Processar campos do termo atual
        elif current_term is not None:
            if ': ' in line:
                field, value = line.split(': ', 1)
                current_term[field.lower()] = value

print(f"Arquivo base criado com sucesso: {output_file}")
