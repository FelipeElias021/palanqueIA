import requests
import os
import json
from openai import OpenAI
import random
import re

api_keys = [
    os.getenv("SAMBANOVA_API_KEY"),
    os.getenv("SAMBANOVA_API_KEY_2"),
    os.getenv("SAMBANOVA_API_KEY_3"),
    os.getenv("SAMBANOVA_API_KEY_4"),
    os.getenv("SAMBANOVA_API_KEY_5"),
    os.getenv("SAMBANOVA_API_KEY_6"),
    os.getenv("SAMBANOVA_API_KEY_7"),
]

model = "Meta-Llama-3.1-405B-Instruct"


with open('frontend/static/output_sq_ue.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# Convertendo o conteúdo do arquivo para uma lista de dicionários
data = json.loads(content)


def get_link(resp):
    municipio = resp['municipio']
    sq_candidato = resp['sq_candidato']
    estado = resp['estado']
    
    regiao = ''
    if estado in ['AC', 'AM', 'AP', 'PA', 'RO', 'RR', 'TO']:
        regiao = 'NORTE'
    if estado in ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE']:
        regiao = 'NORDESTE'
    if estado in ['DF', 'GO', 'MS', 'MT']:
        regiao = 'CENTROOESTE'
    if estado in ['ES', 'MG', 'RJ', 'SP']:
        regiao = 'SUDESTE'
    if estado in ['PR', 'RS', 'SC']:
        regiao = 'SUL'

    
    cod = next((item[municipio] for item in data if municipio in item), None)
    cod_text = str(cod)    
    while cod_text is not None and len(cod_text) < 5:
        cod_text = '0' + cod_text
    
    link = 'https://divulgacandcontas.tse.jus.br/divulga/#/candidato/' + regiao + '/' + estado + "/2045202024/" + sq_candidato + '/2024/' + cod_text
    
    return link


def format_text(lista_dict):
    resultado = []
    info_resut = []
    for item in lista_dict:
        nome = item.get('nome', 'Nome não informado')
        municipio = item.get('municipio', 'Município não informado')
        estado = item.get('estado', 'Estado não informado')
        documento = item.get('documento', 'Documento não informado')
        
        # Concatenação do nome, município e documento em uma string
        info_concatenada = f"{nome}, de {municipio}-{estado}\n Proposta:{documento}"
        resultado.append(info_concatenada)

        nome_loc = f"{nome}, de {municipio}-{estado}"
        info_resut.append(nome_loc)

    return resultado, info_resut


# Função para sumarizar textos usando a API do SambaNova
def summarize_texts(text_list, context, param):
    # Escolher uma chave aleatoriamente
    api_key = random.choice(api_keys)

    # Hugging Face API setup
    client = OpenAI(
        base_url="https://api.sambanova.ai/v1/",
        api_key=api_key,  
    )

    summarized_texts = []
    
    for text in text_list:
        # Dados da requisição (payload)
        
        completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"{param['system_base']}{context}"},
            {"role": "user", "content":  text}
        ],
        stream=True,
        temperature=param['temperature'],
        top_p=param['top_p']
        )
        
        response = ""

        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        
        summarized_texts.append(response)

    client.close()
        
    return summarized_texts


def summarized_proposals(chroma_response, prompt, style):
    # Você é um assistente que resume em poucas palavras com foco em
    if style == 'conservador':
        param = {'temperature': 0.2,
            'top_p': 0.90,
            'system_base': f"Você é um assistente que resume em poucas palavras de maneira factual, com foco em: "
        }
    elif style == 'criativo':
        param = {'temperature': 1.5,
            'top_p': 0.75,
            'system_base': f"Você é um candidato político e deve criar 5 propostas de governo, seja criativo e realista, com foco apenas em: "
        }
        # Você é um candidato político que cria planos de governo criativos com base nesses outros planos e com foco em: 
    
    # Chamar a função para sumarizar os textos
    form_text, info_text = format_text(chroma_response)

    # Quando for criativo juntar os textos para ele enviar apenas um texto e assim criar uma proposta
    final_text_comp = ''
    if style == 'criativo':
        for text in form_text:
            text_split = text.split('\n')
            final_text = ' '.join(text_split[1:]).lstrip()
            final_text_comp += final_text + ' \n'
            
        final_text_comp = final_text_comp.strip()
        
        form_text = [final_text_comp]
        info_text = []
    
    summs = summarize_texts(form_text, prompt, param)

    responses = []  # Lista para armazenar as respostas

    # Exibir os resumos
    for i, resume in enumerate(summs):
        res_str = str(resume)
        #final_response = str(resume) + "\n\nLink de candidatura: " + links
        # Padronização de tópicos
        res_str = res_str.replace('*', '-')
        res_str = res_str.replace('\n', '<br>')
        res_str = re.sub(r'--(.*?)--', r'<I>\1</I>', res_str)
        
        if info_text:
            links = get_link(chroma_response[i])
            final_response = f"<p>Candidato: <strong>{info_text[i]}</strong> <br><br>{res_str} <br><br><a href='{links}' target='_blank'>Saiba mais</a></p>"
        else:
            final_response = f"{res_str}"
        
        # Apesar de cortar pela distância, alguns textos passam e esse trecho se padroniza
        if 'texto que não está relacionado ao tema' not in final_response and 'Não há informações sobre' not in final_response:
            responses.append(final_response)

    return responses