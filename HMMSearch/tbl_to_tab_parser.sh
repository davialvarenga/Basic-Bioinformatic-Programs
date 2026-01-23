#!/bin/bash
# Script: process_hmmsearch_results.sh
# Descrição: Processa resultados do hmmsearch e organiza em formato tabular simplificado

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo "Uso: $0 arquivo_resultados.tbl [saida.tab]"
    echo "Exemplo: $0 resultados_gsk3.tbl hits_gsk3.tab"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-$(basename "$INPUT_FILE" .tbl).tab}"

echo "Processando: $INPUT_FILE"
echo "Saída: $OUTPUT_FILE"

# Criar arquivo de saída com cabeçalho
cat > "$OUTPUT_FILE" << 'HEADER'
#target_name	tlen	query_name	qlen	full_evalue	full_score	full_bias	domain_num	total_domains	domain_c_evalue	domain_i_evalue	domain_score	domain_bias	hmm_from	hmm_to	ali_from	ali_to	env_from	env_to	accuracy	gene_id	gene_name	organism	gene_product	transcript_product	location	protein_length	sequence_SO	SO	is_pseudo
HEADER

# Processar linhas de dados
awk '
BEGIN {
    FS = "\\s+";
    OFS = "\t";
}

# Pular linhas de comentário
/^#/ { next; }

# Processar linhas de dados
{
    # Extrair os primeiros 19 campos (dados do HMMER)
    target_name = $1;
    accession = $2;
    tlen = $3;
    query_name = $4;
    query_accession = $5;
    qlen = $6;
    full_evalue = $7;
    full_score = $8;
    full_bias = $9;
    domain_num = $10;
    total_domains = $11;
    domain_c_evalue = $12;
    domain_i_evalue = $13;
    domain_score = $14;
    domain_bias = $15;
    hmm_from = $16;
    hmm_to = $17;
    ali_from = $18;
    ali_to = $19;
    env_from = $20;
    env_to = $21;
    accuracy = $22;
    
    # Extrair descrição (a partir do campo 23)
    desc = "";
    for (i=23; i<=NF; i++) {
        desc = desc (i==23 ? "" : " ") $i;
    }
    
    # Parsear campos da descrição
    transcript = "";
    gene = "";
    organism = "";
    gene_product = "";
    transcript_product = "";
    location = "";
    protein_length = "";
    sequence_SO = "";
    SO = "";
    is_pseudo = "";
    
    # Dividir a descrição por pipes
    split(desc, parts, "\\|");
    for (i in parts) {
        if (parts[i] ~ /^ transcript=/) {
            gsub(/^ transcript=/, "", parts[i]);
            transcript = parts[i];
        }
        else if (parts[i] ~ /^ gene=/) {
            gsub(/^ gene=/, "", parts[i]);
            gene = parts[i];
        }
        else if (parts[i] ~ /^ organism=/) {
            gsub(/^ organism=/, "", parts[i]);
            organism = parts[i];
        }
        else if (parts[i] ~ /^ gene_product=/) {
            gsub(/^ gene_product=/, "", parts[i]);
            gene_product = parts[i];
        }
        else if (parts[i] ~ /^ transcript_product=/) {
            gsub(/^ transcript_product=/, "", parts[i]);
            transcript_product = parts[i];
        }
        else if (parts[i] ~ /^ location=/) {
            gsub(/^ location=/, "", parts[i]);
            location = parts[i];
        }
        else if (parts[i] ~ /^ protein_length=/) {
            gsub(/^ protein_length=/, "", parts[i]);
            protein_length = parts[i];
        }
        else if (parts[i] ~ /^ sequence_SO=/) {
            gsub(/^ sequence_SO=/, "", parts[i]);
            sequence_SO = parts[i];
        }
        else if (parts[i] ~ /^ SO=/) {
            gsub(/^ SO=/, "", parts[i]);
            SO = parts[i];
        }
        else if (parts[i] ~ /^ is_pseudo=/) {
            gsub(/^ is_pseudo=/, "", parts[i]);
            is_pseudo = parts[i];
        }
    }
    
    # Imprimir linha formatada
    print target_name, tlen, query_name, qlen, full_evalue, full_score, full_bias, 
          domain_num, total_domains, domain_c_evalue, domain_i_evalue, domain_score, 
          domain_bias, hmm_from, hmm_to, ali_from, ali_to, env_from, env_to, 
          accuracy, gene, transcript, organism, gene_product, transcript_product, 
          location, protein_length, sequence_SO, SO, is_pseudo;
}
' "$INPUT_FILE" >> "$OUTPUT_FILE"

echo "Arquivo processado: $OUTPUT_FILE"

# Gerar resumo estatístico
echo -e "\n=== RESUMO ESTATÍSTICO ==="
echo "Total de hits: $(tail -n +2 "$OUTPUT_FILE" | wc -l)"
echo "Proteínas únicas: $(tail -n +2 "$OUTPUT_FILE" | cut -f1 | sort -u | wc -l)"

# Gerar arquivo com top hits organizados
TOP_HITS_FILE="top_hits_$(date +%Y%m%d_%H%M%S).tab"
echo -e "# Top Hits Organizados por Score\n" > "$TOP_HITS_FILE"

# Extrair melhores hits por proteína (maior score)
awk -F'\t' '
NR == 1 { next; }  # Pular cabeçalho
{
    protein = $1;
    score = $6;
    
    if (!best_score[protein] || score > best_score[protein]) {
        best_score[protein] = score;
        best_line[protein] = $0;
    }
}
END {
    # Ordenar por score decrescente
    for (protein in best_score) {
        printf "%s\t%s\n", best_score[protein], best_line[protein];
    }
}
' "$OUTPUT_FILE" | sort -rn -k1 | cut -f2- >> "$TOP_HITS_FILE"

echo "Top hits por proteína salvo em: $TOP_HITS_FILE"

# Gerar estatísticas por tipo de quinase
echo -e "\n=== DISTRIBUIÇÃO POR TIPO DE QUINASE ==="
tail -n +2 "$OUTPUT_FILE" | awk -F'\t' '
{
    # Extrair tipo da descrição do produto
    product = $24;  # gene_product
    if (product ~ /glycogen synthase kinase/) type = "GSK3";
    else if (product ~ /mitogen.*activated protein kinase/) type = "MAPK";
    else if (product ~ /cdc2.*related kinase/) type = "CDK";
    else if (product ~ /serine.*threonine.*kinase/) type = "Ser/Thr kinase";
    else if (product ~ /casein kinase/) type = "Casein kinase";
    else if (product ~ /protein kinase.*putative/) type = "Protein kinase putative";
    else type = "Outros";
    
    count[type]++;
}
END {
    for (type in count) {
        printf "%s: %d hits\n", type, count[type];
    }
}' | sort -rn -k2

echo -e "\n=== PRIMEIROS 10 HITS (maior score) ==="
head -n 11 "$OUTPUT_FILE" | column -t -s $'\t'
