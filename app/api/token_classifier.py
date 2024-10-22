import requests
import os
from app.models.message import Message

API_TOKEN = os.getenv('API_KEY')
MODEL = "dbmdz/bert-large-cased-finetuned-conll03-english"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# As entidade permanecem a cada consulta, mas vou manter a fim de deixar um hisórico acerca de quem está sendo falado
# Caso queira resetar a cada consulta, essa lista vazia deve ser inicializada dentro da função entity_identifier()
remove_words = []

def prompt_format(old_prompt, words):

    for word in words:
        old_prompt = old_prompt.replace(word, "")
    
    new_prompt = ' '.join(old_prompt.split())

    return new_prompt

def entity_identifier(msg: Message):
    prompt = msg.message

    payload = {
        "inputs": prompt,
        "options": {
            "wait_for_model": True, # Espera o modelo carregar se estiver inativo
            "use_cache": False
        }
    }
    
    # Faz uma requisição POST para a API
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        text = response.json()

        for item in text:
            if item['entity_group'] == "PER":
                name = item['word']
                remove_words.append(name)

            elif item['entity_group'] == "LOC":
                local = item['word']
                remove_words.append(local)

        result = f"Keyworks: {remove_words}"

    else:
        result = f"Erro com a conexão da Api: {response.status_code}"

    next_prompt = prompt_format(prompt, remove_words)
        
    return result, next_prompt
