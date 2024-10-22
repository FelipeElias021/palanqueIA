from pydantic import BaseModel

# Definindo o modelo de mensagem
class Message(BaseModel):
    message: str
    style: str = "conservador"
    # criativo
    # conservador

def process_message(msg: Message):
    return msg.message
