from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

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

# 1. Conecta ao banco (isso cria o arquivo tasks.db automaticamente)
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

# 2. Cria a tabela 'tasks' se ela ainda não existir
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0
    )
""")
conn.commit()

# 3. Conta quantas tarefas existem e insere exemplos apenas se a tabela estiver vazia
cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]

if count == 0:
    cursor.executemany(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        [("Buy milk", 0), ("Learn FastAPI", 1), ("Build a CRUD API", 0)]
    )
    conn.commit()


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

# READ: Listar todas as tarefas
@app.get("/tasks")
def get_tasks():
    cursor.execute("SELECT * FROM tasks")  #

    tasks = []
    for row in cursor.fetchall():
        # row[0] é id, row[1] é title, row[2] é done
        tasks.append({"id": row[0], "title": row[1], "done": bool(row[2])})

    return tasks


# READ: Listar uma tarefa específica
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    # O sinal de interrogação (?) protege o banco contra ataques (Parameterized query)
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))  #
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")  # [cite: 1]

    return {"id": row[0], "title": row[1], "done": bool(row[2])}


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