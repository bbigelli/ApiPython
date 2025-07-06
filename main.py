from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from enum import Enum

app = FastAPI(
    title="API de Livros",
    description="Uma API simples para gerenciar livros com autenticação, paginação e ordenação.",
    version="1.1.0",
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

# Configuração de usuários (em produção, usar banco de dados com senhas hasheadas)
USERS = {
    "admin": {
        "password": "123456",
        "scopes": ["admin", "user"]
    },
    "user": {
        "password": "abc123",
        "scopes": ["user"]
    }
}

security = HTTPBasic()

# Enum para ordenação
class OrdenacaoCampos(str, Enum):
    titulo = "titulo"
    autor = "autor"
    ano = "ano"

# Definindo o modelo de dados para um livro
class Livro(BaseModel):
    titulo: str
    autor: str
    ano: int

# Modelo de resposta para lista paginada
class LivrosPaginados(BaseModel):
    page: int
    limit: int
    total: int
    livros: List[dict]

def autenticar(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    
    if username not in USERS:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    if not secrets.compare_digest(password, USERS[username]["password"]):
        raise HTTPException(
            status_code=401,
            detail="Senha incorreta",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return username

@app.get("/livros", response_model=LivrosPaginados, tags=["livros"])
def listar_livros(
    page: int = Query(1, gt=0, description="Número da página"),
    limit: int = Query(10, gt=0, le=100, description="Quantidade de itens por página"),
    sort_by: Optional[OrdenacaoCampos] = Query(None, description="Campo para ordenação"),
    sort_desc: bool = Query(False, description="Ordenar em ordem decrescente"),
    credentials: HTTPBasicCredentials = Depends(autenticar)
):
    """
    Lista todos os livros com paginação e ordenação opcional.
    """
    if not livros_db:
        raise HTTPException(status_code=404, detail="Nenhum livro cadastrado.")
    
    # Converter dicionário para lista de tuplas (id, livro)
    livros_list = list(livros_db.items())
    
    # Aplicar ordenação se solicitado
    if sort_by:
        livros_list.sort(
            key=lambda item: item[1][sort_by.value],
            reverse=sort_desc
        )
    
    # Aplicar paginação
    start = (page - 1) * limit
    end = start + limit
    livros_paginados = livros_list[start:end]
    
    # Formatar resposta
    livros_formatados = [
        {"id": id, **livro} for id, livro in livros_paginados
    ]
    
    return {
        "page": page,
        "limit": limit,
        "total": len(livros_db),
        "livros": livros_formatados
    }

@app.post("/addlivros", tags=["livros"])
def post_livros(
    id: int, 
    livro: Livro,
    credentials: HTTPBasicCredentials = Depends(autenticar)
):
    """
    Adiciona um novo livro ao sistema.
    """
    if id in livros_db:
        raise HTTPException(status_code=400, detail="Livro já cadastrado.")
    
    livros_db[id] = livro.dict()
    return {"mensagem": "Livro cadastrado com sucesso."}

@app.put("/atualizarlivros/{id}", tags=["livros"])
def put_livros(
    id: int, 
    livro: Livro,
    credentials: HTTPBasicCredentials = Depends(autenticar)
):
    """
    Atualiza um livro existente.
    """
    if id not in livros_db:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    
    livros_db[id] = livro.dict()
    return {"mensagem": "Livro atualizado com sucesso."}

@app.delete("/deletarlivros/{id}", tags=["livros"])
def deletar_livros(
    id: int,
    credentials: HTTPBasicCredentials = Depends(autenticar)
):
    """
    Remove um livro do sistema.
    """
    if id not in livros_db:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    
    del livros_db[id]
    return {"mensagem": "Livro deletado com sucesso."}