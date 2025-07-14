import re
import os


def parse_fasta_headers(fasta_file):
    """
    Extrai informações dos cabeçalhos no formato:
    >drugbank_target|UNIPROT_ID Description (DBXXXXX; DBXXXXX)
    """
    pattern = r'^>drugbank_target\|([^\s]+)\s+(.*?)\s*\(([^)]+)\)$'
    results = []

    with open(fasta_file, 'r') as f:
        for line in f:
            if line.startswith('>'):
                line = line.strip()
                match = re.match(pattern, line)
                if match:
                    uniprot_id = match.group(1)
                    description = match.group(2).strip()
                    drug_ids = [db.strip() for db in match.group(3).split(';')]

                    # Limpeza adicional da descrição
                    description = re.sub(r'\s+', ' ', description)  # Remove múltiplos espaços
                    description = description.strip()

                    results.append((uniprot_id, description, drug_ids))
                else:
                    print(f"Padrão não encontrado em: {line}")

    return results


def write_tsv_output(data, output_file):
    """Escreve os dados em formato TSV"""
    with open(output_file, 'w') as f:
        # Cabeçalho
        f.write("Protein_ID\tDescription\tDrugBank_IDs\n")

        # Dados
        for uniprot_id, description, drug_ids in data:
            drug_ids_str = "; ".join(drug_ids)
            f.write(f"{uniprot_id}\t{description}\t{drug_ids_str}\n")


def main():
    input_file = input("Digite o caminho do arquivo FASTA: ").strip()

    if not os.path.isfile(input_file):
        print("Erro: Arquivo não encontrado!")
        return

    output_file = os.path.splitext(input_file)[0] + "_mapping.tsv"

    print("Processando arquivo FASTA...")
    parsed_data = parse_fasta_headers(input_file)

    if not parsed_data:
        print("Nenhum dado válido encontrado nos cabeçalhos.")
        return

    write_tsv_output(parsed_data, output_file)
    print(f"Arquivo TSV gerado com sucesso: {output_file}")
    print(f"Total de entradas processadas: {len(parsed_data)}")


if __name__ == "__main__":
    main()