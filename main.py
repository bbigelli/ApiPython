# Api de livros

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

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

# Definindo o modelo de dados para um livro
class Livro(BaseModel):
    titulo: str
    autor: str
    ano: int

@app.get("/livros")
def listar_livros():
    if not livros_db:
        return {"mensagem": "Nenhum livro encontrado."}
    else:
        return {"Livros": livros_db}

#id nome autor ano    
@app.post("/addlivros")
def post_livros(id: int, livro: Livro):
    if id in livros_db:
        raise HTTPException(status_code=400, detail="Livro já cadastrado.")
    else:
        livros_db[id] = livro.dict()
        return {"mensagem": "Livro cadastrado com sucesso."}
    
@app.put("/atualizarlivros/{id}")
def put_livros(id: int, livro: Livro):
    livros = livros_db.get(id)
    if not livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    else:
        livros_db[id] = livro.dict()
        
        return {"mensagem": "Livro atualizado com sucesso."}

@app.delete("/deletarlivros/{id}")
def deletar_livros(id: int):
    if id not in livros_db:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    else:
        del livros_db[id]

        return {"mensagem": "Livro deletado com sucesso."}
