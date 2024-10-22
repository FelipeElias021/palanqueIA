from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models.message import Message
from app.api.prompt_optimization import extend_query
from app.api.token_classifier import entity_identifier
from app.api.sumarization_response import summarized_proposals
from database.db_conection import get_documents
import uvicorn

app = FastAPI()

# Diretório de templates HTML
templates = Jinja2Templates(directory="frontend")

# Servindo arquivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/")
async def get_chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_response(msg: Message):
    style = msg.style
    if style not in ['criativo', 'conservador']:
        style = 'conservador'
        
    entities, prompt = entity_identifier(msg)
    
    extended = extend_query(prompt)

    # Define o número de chunks que vai procurar
    n_results = 15 if style == 'criativo' else 5
    
    db_reply = get_documents(extended, n_results)

    final_text = summarized_proposals(db_reply, prompt, style)
    
    if not final_text:
        response = {"reply": ["Esse assunto não parece com uma proposta, tente novamente."]}
    else:
        response = {"reply": final_text}
    
    return response

if __name__ == '__main__':
    # uvicorn.run(app, host='0.0.0.0', port=8000)
    uvicorn.run('main:app', host="0.0.0.0", port=8001, reload=True)