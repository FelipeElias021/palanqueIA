import sqlite3
import pandas as pd
import json

# CSV BASE
cand_path = 'database/documents/consulta_cand_2024_BRASIL.csv'

conn = sqlite3.connect('database/db/candidatos.db') 
cursor = conn.cursor()

# CRIA A TABELA
cursor.execute(''' CREATE TABLE IF NOT EXISTS eleicoes ( ano_eleicao INTEGER, nm_tipo_eleicao TEXT, ds_eleicao TEXT, sg_uf TEXT, sg_ue TEXT, nm_ue TEXT, sq_candidato INTEGER PRIMARY KEY, nm_candidato TEXT, nm_urna_candidato TEXT, tp_agremiacao TEXT, nr_partido TEXT, sq_coligacao TEXT, nm_coligacao TEXT, ds_composicao_coligacao TEXT, sg_uf_nascimento TEXT, dt_nascimento TEXT, ds_genero TEXT, ds_grau_instrucao TEXT, ds_estado_civil TEXT, ds_cor_raca TEXT, ds_ocupacao TEXT, ds_cargo TEXT ) ''')

# TRANSFORMA O CSV EM DATAFRAME, FILTRA PARA PEGAR APENAS OS PREFEITOS E DIMINUI O NÚMERO DE COLUNAS
df_candidatos = pd.read_csv(cand_path, encoding='ISO-8859-1', sep=';')
df_candidatos = df_candidatos[df_candidatos['DS_CARGO'] == 'PREFEITO']
df_candidatos = df_candidatos[['ANO_ELEICAO', 'NM_TIPO_ELEICAO', 'DS_ELEICAO', 'SG_UF', 'SG_UE', 'NM_UE', 'SQ_CANDIDATO', 'NM_CANDIDATO', 'NM_URNA_CANDIDATO', 'TP_AGREMIACAO', 'NR_PARTIDO', 'SG_PARTIDO', 'NM_PARTIDO', 'NR_FEDERACAO', 'NM_FEDERACAO', 'SG_FEDERACAO', 'SQ_COLIGACAO', 'NM_COLIGACAO', 'DS_COMPOSICAO_COLIGACAO', 'SG_UF_NASCIMENTO', 'DT_NASCIMENTO', 'DS_GENERO', 'DS_GRAU_INSTRUCAO', 'DS_ESTADO_CIVIL', 'DS_COR_RACA', 'DS_OCUPACAO', 'DS_CARGO']]

cursor.execute(''' SELECT DISTINCT e.sg_ue, e.NM_UE FROM eleicoes e  ''')

# Fetching all the results
results = cursor.fetchall()

# Transforming the results into a list of dictionaries
data = [{row[1]: row[0]} for row in results]

# Writing the list to a .txt file with UTF-8 encoding
with open('database/db/output.txt', 'w', encoding='utf-8') as file:
    file.write(json.dumps(data, ensure_ascii=False, indent=4))

# SALVA EM BANCO
df_candidatos.to_sql('eleicoes', conn, if_exists='replace', index=False)