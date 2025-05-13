# Api de livros

from fastapi import FastAPI, HTTPException

app = FastAPI()

# Simulando um banco de dados com um dicionário
livros_db = {}

@app.get("/livros")
def listar_livros():
    if not livros_db:
        return {"mensagem": "Nenhum livro encontrado."}
    else:
        return {"Livros": livros_db}

#id nome autor ano    
@app.post("/addlivros")
def post_livros(id: int, titulo: str, autor: str, ano: int):
    if id in livros_db:
        raise HTTPException(status_code=400, detail="Livro já cadastrado.")
    else:
        livros_db[id] = {"titulo": titulo, "autor": autor, "ano": ano}
        return {"mensagem": "Livro cadastrado com sucesso."}
    
@app.put("/atualizarlivros/{id}")
def put_livros(id: int, titulo: str, autor: str, ano: int):
    livros = livros_db.get(id)
    if not livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    else:
        if titulo:
            livros["titulo"] = titulo
        if autor:
            livros["autor"] = autor
        if ano:
            livros["ano"] = ano

        return {"mensagem": "Livro atualizado com sucesso."}

@app.delete("/deletarlivros/{id}")
def deletar_livros(id: int):
    if id not in livros_db:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    else:
        del livros_db[id]

        return {"mensagem": "Livro deletado com sucesso."}
