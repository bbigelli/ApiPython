from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

app = FastAPI(
    title="API de Livros",
    description="Uma API simples para gerenciar livros.",
    version="1.0.0",
    contact={
        "name": "Bruno Bigelli",
        "email": "bbigelli@hotmail.com",
        "url": "https://github.com/bbigelli"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "livros",
            "description": "Operações relacionadas a livros."
        }
    ]

)

# Simulando um banco de dados com um dicionário
livros_db = {}

login = "admin"
senha = "123456"

security = HTTPBasic()

# Definindo o modelo de dados para um livro
class Livro(BaseModel):
    titulo: str
    autor: str
    ano: int

def autenticar(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, login)
    is_password_correct = secrets.compare_digest(credentials.password, senha)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.get("/livros")
def listar_livros(page int = 1, limit int = 10, credentials: HTTPBasicCredentials = Depends(autenticar)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Parâmetros inválidos. 'page' e 'limit' devem ser maiores que 0.")
    
    if not livros_db:
        raise HTTPException(status_code=404, detail="Nenhum livro cadastrado.")
    
    start = (page - 1) * limit
    end = start + limit
    livros_paginados = [
        {"id": id, titulo: livro["titulo"], autor: livro["autor"], ano: livro["ano"]}
        for id, livro in list(livros_db.items())[start:end]
        
    ]

#id nome autor ano    
@app.post("/addlivros")
def post_livros(id: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar)):
    if id in livros_db:
        raise HTTPException(status_code=400, detail="Livro já cadastrado.")
    else:
        livros_db[id] = livro.dict()
        return {"mensagem": "Livro cadastrado com sucesso."}
    
@app.put("/atualizarlivros/{id}")
def put_livros(id: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar)):
    livros = livros_db.get(id)
    if not livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    else:
        livros_db[id] = livro.dict()
        
        return {"mensagem": "Livro atualizado com sucesso."}

@app.delete("/deletarlivros/{id}")
def deletar_livros(id: int, credentials: HTTPBasicCredentials = Depends(autenticar)):
    if id not in livros_db:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    else:
        del livros_db[id]

        return {"mensagem": "Livro deletado com sucesso."}
