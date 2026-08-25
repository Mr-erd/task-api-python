from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# -----------------
# MODELOS DE DADOS
# -----------------
class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


# -----------------
# BANCO DE DADOS (MEMÓRIA)
# -----------------
tasks_db = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Learn FastAPI", "done": True},
    {"id": 3, "title": "Build a CRUD API", "done": False}
]


# -----------------
# ROTAS DE SISTEMA (Stage 1)
# -----------------
@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# -----------------
# ROTAS CRUD
# -----------------

# READ: Listar todas as tarefas (Stage 2)
@app.get("/tasks")
def get_tasks():
    return tasks_db


# READ: Listar uma tarefa específica (Stage 2)
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


# CREATE: Criar uma nova tarefa (Stage 3)
@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    next_id = max(t["id"] for t in tasks_db) + 1 if tasks_db else 1
    new_task = {"id": next_id, "title": task.title, "done": False}
    tasks_db.append(new_task)

    return new_task


# UPDATE: Atualizar uma tarefa (Stage 4)
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    for task in tasks_db:
        if task["id"] == task_id:
            if task_update.title is not None and not task_update.title.strip():
                raise HTTPException(status_code=400, detail="Title cannot be empty")

            if task_update.title is not None:
                task["title"] = task_update.title
            if task_update.done is not None:
                task["done"] = task_update.done
            return task

    raise HTTPException(status_code=404, detail="Task not found")


# DELETE: Deletar uma tarefa (Stage 4)
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            del tasks_db[i]
            return

    raise HTTPException(status_code=404, detail="Task not found")