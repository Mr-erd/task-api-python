from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # <-- NOVO IMPORTE

app = FastAPI()


# Modelo de dados que o cliente deve enviar
class TaskCreate(BaseModel):
    title: str


tasks_db = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Learn FastAPI", "done": True},
    {"id": 3, "title": "Build a CRUD API", "done": False}
]


# ... (Mantenha as rotas /, /health, /tasks e /tasks/{task_id} aqui) ...

# 4. Rota para criar uma nova tarefa (Create)
@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    # Regra de Negócio: se o título for vazio, retorne 400 Bad Request
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    # Descobre qual será o próximo ID
    next_id = max(t["id"] for t in tasks_db) + 1 if tasks_db else 1

    # Cria o novo dicionário da tarefa
    new_task = {
        "id": next_id,
        "title": task.title,
        "done": False  # Começa como falso
    }

    # Adiciona à nossa lista em memória
    tasks_db.append(new_task)

    return new_task