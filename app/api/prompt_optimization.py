import random
from openai import OpenAI
import os
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


def get_text_after_newline(text):
    # Encontra o índice do primeiro '\n'
    newline_index = text.find('\n')
    
    # Se encontrar um '\n', retorna o texto após ele
    if newline_index != -1:
        return text[newline_index+1:]
    
    # Se não encontrar '\n', retorna a string original ou uma mensagem
    return text


def clean_text(old_text):
    # Remove asteriscos, quebras de linha (\n), números e outros caracteres indesejados
    cleaned_text = re.sub(r'[*\n\d]', '', old_text)
    
    # Opcional: Remove espaços extras antes de retornar
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text


def extend_query(prompt):
    # Escolher uma chave aleatoriamente
    api_key = random.choice(api_keys)

    # Hugging Face API setup
    client = OpenAI(
        base_url="https://api.sambanova.ai/v1/",
        api_key=api_key,  
    )

    completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "Você é um candidato político."},
        {"role": "user", "content": f"Retorne em poucas palavras 3 propostas diferentes de acordo com o seguinte pedido: \n\n {prompt}",}
    ],
    stream=True,
    )
    
    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""

    simple_response = get_text_after_newline(response)
    result = clean_text(simple_response)
    
    client.close()

    return result