from langchain.document_loaders import PyPDFLoader
import pandas as pd
import os
import re
import sqlite3
import chromadb
# from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

# Caminhos dos PDFs com as proposta e o banco dos candidatos
# Alterar o caminho do PDF para cada estado que for carregar
pdf_directory = "database/documents/MG"
db_path = "database/db/candidatos.db"

def preprocess_text(text):
    # Converter para minúsculas
    text = text.lower()

    # # Remover caracteres indesejados, exceto acentos e caracteres como "ç"
    text = re.sub(r'[^\w\s\.,;:!?()@#$%&*"\']', '', text)

    # Personalizado
    text = text.replace("ü", "-")
    text = text.replace("ø", "-")
    text = text.replace("_", "")
    text = text.replace("..", "")

    # Remover espaços antes e depois do texto e entre caracteres chaves
    text = text.strip()
    text = text.replace("  ", " ")
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    text = text.replace("( ", "(")
    text = text.replace(" )", ")")
    text = text.replace(" ;", ";")
    text = text.replace(" :", ":")

    return text

def preprocess_text_pos(text):
    # Remover quebras de linha e caracteres indesejados
    text = text.replace('\n', ' ').replace('\x00', '')

    # Remover múltiplos espaços
    text = re.sub(r'\s+', ' ', text)

    return text

def get_dados_cand(filename):
    uf = re.search(r"\d{4}([A-Z]{2})\d+", filename).group(1)
    cod_cand = re.search(r"\d{4}[A-Z]{2}(\d+)_", filename).group(1)
    seq = re.search(r"_(\d{2})\.pdf", filename).group(1)
    
    # Conecta ao banco de dados, realiza a query e armazena os resultados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT e.NM_CANDIDATO, e.NM_UE FROM eleicoes e WHERE e.SQ_CANDIDATO = ?", (cod_cand,))
    resultados = cursor.fetchall()

    # Fecha a conexão com o banco de dados
    conn.close()

    if resultados:
        dados = [{'Seq': seq, 'Cod_cand': cod_cand, 'Nome': linha[0], 'UF': uf, 'UE': linha[1]} for linha in resultados]
        return dados[0]
    else:
        return {'Seq': '01', 'Cod_cand': cod_cand, 'Nome': 'Não Encontrado', 'UF': uf, 'UE': 'Não Encontrado'}
    
    # Armazenar os documentos processados
def batch_iterable(iterable: List, batch_size: int):
    """
    Divide um iterável em lotes de tamanho fixo.

    :param iterable: O iterável a ser dividido em lotes.
    :param batch_size: O tamanho de cada lote.
    :return: Um gerador que produz lotes do tamanho especificado.
    """
    length = len(iterable)
    for start in range(0, length, batch_size):
        yield iterable[start:start + batch_size]
        
documents = []
i = 0

# Passar por todos os documentos
for filename in os.listdir(pdf_directory):
    # Verificar se é um pdf e se a primeira proposta
    if filename.endswith(".pdf") and filename != 'leiame.pdf': # and filename[18:20] == '01':
        # Cria o caminho completo para o arquivo, carrega o arquivo PDF e carrega todas as páginas
        file_path = os.path.join(pdf_directory, filename)
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        full_text = ''.join([pag.page_content for pag in pages])

        if full_text != '':
            #Preprocessamento
            full_text = preprocess_text(full_text)

            # Pega o código do candidato e procura na base para inserir nome e UE
            dados_cand = get_dados_cand(filename)

            documents.append({'value': full_text, 'cod_cand': dados_cand['Cod_cand'], 'nome': dados_cand['Nome'], 'uf': dados_cand['UF'], 'ue': dados_cand['UE']})

            if i == 10:
                break

            i += 1

client = chromadb.PersistentClient(path="database/chromadb")

# Carregar o modelo de embeddings personalizado
# sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = client.get_or_create_collection(
    name="propostas",
    metadata={"hnsw:space": "cosine"}
    )

# Configurações
chunk_size = 256
batch_size = 100  # Ajuste o tamanho do lote conforme necessário
indice = 1

# Listas para acumular os dados antes de inserir
batch_texts = []
batch_metas = []
batch_ids = []

# Processamento dos documentos
for i in range(len(documents)):
    meta = {
        "candidato": documents[i]['cod_cand'],
        "nome": documents[i]['nome'],
        "uf": documents[i]['uf'],
        "ue": documents[i]['ue']
    }
    texto = documents[i]['value']

    # Quebra do texto em chunks
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        separators=["\n\n", "\n", ";", "."]
    )
    texto_split = r_splitter.split_text(texto)

    for j in range(len(texto_split)):
        texto_split_tratado = preprocess_text_pos(texto_split[j])
        
        # Adiciona o chunk ao lote
        batch_texts.append(texto_split_tratado)
        batch_metas.append(meta)
        batch_ids.append(str(indice))
        indice += 1

        # Se o lote estiver cheio, insere os dados no banco e limpa as listas
        if len(batch_texts) >= batch_size:
            collection.add(
                documents=batch_texts,
                metadatas=batch_metas,
                ids=batch_ids
                # embeddings=[val]  # Se necessário
            )
            # Limpa as listas para o próximo lote
            batch_texts = []
            batch_metas = []
            batch_ids = []

# Insere o restante dos dados que podem não ter preenchido um lote completo
if batch_texts:
    collection.add(
        documents=batch_texts,
        metadatas=batch_metas,
        ids=batch_ids
        # embeddings=[val]  # Se necessário
    )

print("Inserção completa!")
