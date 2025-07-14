import pandas as pd


def process_files(blast_file, drugbank_file, output_file):
    # Carrega os arquivos com tratamento especial
    try:
        # Lê o arquivo BLAST sem cabeçalho e atribui nomes às colunas
        blast_df = pd.read_csv(blast_file, sep='\t', header=None,
                               names=['Query ID', 'Subject ID', 'Identity (%)',
                                      'Query coverage (%)', 'Target Description',
                                      'Drugs associated'])

        # Lê o arquivo DrugBank
        drugbank_df = pd.read_csv(drugbank_file)
    except Exception as e:
        print(f"Erro ao ler arquivos: {e}")
        return

    # Cria dicionários de mapeamento
    drug_map = {}
    drug_descriptions = {}

    for _, row in drugbank_df.iterrows():
        drug_id = row['DrugBank ID']

        # Mapeamento de nomes
        name = row['Common name'] if pd.notna(row['Common name']) else (
            row['Synonyms'].split('|')[0].strip() if pd.notna(row['Synonyms']) else drug_id
        )
        drug_map[drug_id] = name

        # Armazena todas as descrições/sinônimos sem repetição
        descriptions = set()
        if pd.notna(row['Common name']):
            descriptions.add(row['Common name'])
        if pd.notna(row['Synonyms']):
            for syn in row['Synonyms'].split('|'):
                descriptions.add(syn.strip())
        drug_descriptions[drug_id] = ' | '.join(sorted(descriptions))

    # Processa os nomes dos fármacos
    def map_drug_names(drug_str):
        if pd.isna(drug_str):
            return ''
        return '; '.join(
            f"{drug_map.get(did.strip(), did.strip())} ({did.strip()})"
            for did in drug_str.split(';')
        )

    # Processa as descrições completas sem repetição
    def get_unique_descriptions(drug_str):
        if pd.isna(drug_str):
            return ''
        unique_descs = set()
        for did in drug_str.split(';'):
            did = did.strip()
            if did in drug_descriptions:
                unique_descs.add(drug_descriptions[did])
            else:
                unique_descs.add(did)
        return '; '.join(sorted(unique_descs))

    # Adiciona as novas colunas
    blast_df['Drug Names'] = blast_df['Drugs associated'].apply(map_drug_names)
    blast_df['Drug Descriptions'] = blast_df['Drugs associated'].apply(get_unique_descriptions)

    # Reorganiza as colunas para melhor visualização
    column_order = [
        'Query ID',
        'Subject ID',
        'Identity (%)',
        'Query coverage (%)',
        'Target Description',
        'Drugs associated',
        'Drug Names',
        'Drug Descriptions'
    ]
    blast_df = blast_df[column_order]

    # Salva o resultado
    blast_df.to_csv(output_file, sep='\t', index=False)
    print(f"Processamento concluído! Arquivo salvo em: {output_file}")


if __name__ == "__main__":
    # Configuração dos caminhos dos arquivos
    blast_file = "/home/dalvarenga/Documentos/1_Doutorado/12_Artigo_GAT3_Tcruzi/1_align_GATs_Dm28_TCC/4_drugbank_analysis/blast_TcDm28GATs_wTargets_DBs.tsv"
    drugbank_file = "/home/dalvarenga/Documentos/5_drugbank_v5.1.13/1_drugbank_vocabulary_v5_1_13.csv"
    output_file = "/home/dalvarenga/Documentos/1_Doutorado/12_Artigo_GAT3_Tcruzi/1_align_GATs_Dm28_TCC/4_drugbank_analysis/drugbank_analysis_results_with_drug_names.tsv"

    process_files(blast_file, drugbank_file, output_file)