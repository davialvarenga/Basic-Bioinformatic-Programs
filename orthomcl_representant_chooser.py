import pandas as pd

transcripts = pd.read_csv("transcripts_full.csv")
orthogroups = pd.read_csv("ortho_groups_full.csv", header = None, low_memory = False)

representantes = {}
for linha in orthogroups.iterrows():
    grupo = None
    fold_change = None
    for indice_linha, gene_id in enumerate(linha[1]):
        if indice_linha == 0:
            grupo = gene_id.rstrip(":")
        else:
            if isinstance(gene_id,str):
                gene_id = gene_id.split("=")[1]
                temp_fold = transcripts.loc[transcripts["Transcripts"] == gene_id, "Fold"]
                if len(temp_fold) > 0:
                    temp_fold = temp_fold.item()
                    if fold_change is None:
                        fold_change = temp_fold
                        representantes[grupo] = {"Gene ID": gene_id, "Fold Change": fold_change}
                    elif temp_fold > fold_change:
                        fold_change = temp_fold
                        representantes[grupo] = {"Gene ID": gene_id, "Fold Change": fold_change}
print(representantes)

representantes = pd.DataFrame(representantes)
representantes.transpose().to_excel("out_bestprot_orthomcl.xlsx")