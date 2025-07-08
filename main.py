from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from enum import Enum

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

DATABASE_URL = "sqlite:///./livros.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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

# Simulando um banco de dados com um dicionário
livros_db = {}

security = HTTPBasic()

# Definindo o modelo de dados para um livro
class LivroDB(Base):
    __tablename__ = "Livros"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    autor = Column(String, index=True)
    ano = Column(Integer)

class Livro(BaseModel):
    titulo: str
    autor: str
    ano: int

Base.metadata.create_all(bind=engine)

def session_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

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

@app.get("/livros", tags=["livros"])
def listar_livros(
    page: int = Query(1, gt=0, description="Número da página"),
    limit: int = Query(10, gt=0, le=100, description="Quantidade de itens por página"),
    db: Session = Depends(session_db)
):

    livros = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()

    if not livros:
        raise HTTPException(status_code=404, detail="Nenhum livro cadastrado.")
    
    total_livros = db.query(LivroDB).count()
               
    return {
        "page": page,
        "limit": limit,
        "total": total_livros,
        "livros": [{"id": livro.id, "titulo": livro.titulo, "autor": livro.autor, "ano": livro.ano} for livro in livros]
    }

@app.post("/addlivros", tags=["livros"])
def post_livros(db: Session = Depends(session_db), credentials: HTTPBasicCredentials = Depends(autenticar)):
    
    db_livro = db.query(LivroDB).filter(LivroDB.titulo == livro.titulo, LivroDB.autor == livro.autor).first()
    if db_livro:
        raise HTTPException(status_code=400, detail="Livro já cadastrado.")


    novo_livro = LivroDB(titulo=livro.titulo, autor=livro.autor, ano=livro.ano)
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    return {"mensagem": "Livro adicionado com sucesso."}

@app.put("/atualizarlivros/{id}", tags=["livros"])
def put_livros(id: int, livro: Livro, db: Session = Depends(session_db), credentials: HTTPBasicCredentials = Depends(autenticar)):
   
    db_livro = db.query(LivroDB).filter(LivroDB.id == id).first()
    
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    
    db_livro.titulo = livro.titulo
    db_livro.autor = livro.autor
    db_livro.ano = livro.ano
    
    db.commit()
    db.refresh(db_livro)

    return {"mensagem": "Livro atualizado com sucesso."}


@app.delete("/deletarlivros/{id}", tags=["livros"])
def deletar_livros(id: int, db: Session = Depends(session_db), credentials: HTTPBasicCredentials = Depends(autenticar)):
    
    db_livro = db.query(LivroDB).filter(LivroDB.id == id).first()
        
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
        
    db.delete(db_livro)
    db.commit()

    return {"mensagem": "Livro deletado com sucesso."}