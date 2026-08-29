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


# CREATE: Adicionar uma nova tarefa
@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")  #

    # Insere a tarefa no banco usando placeholder (?) para segurança
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, 0))  #
    conn.commit()

    # Recupera o ID que o próprio banco de dados gerou automaticamente[cite: 1]
    new_id = cursor.lastrowid

    return {"id": new_id, "title": task.title, "done": False}


# UPDATE: Atualizar uma tarefa existente
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    # 1. Verifica se a tarefa existe
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")  #

    current_title = row[1]
    current_done = bool(row[2])

    # 2. Prepara os novos valores
    new_title = task.title if task.title is not None else current_title
    new_done = task.done if task.done is not None else current_done

    if task.title is not None and not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")  #

    # 3. Executa o UPDATE no banco de dados
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, int(new_done), task_id)
    )
    conn.commit()

    return {"id": task_id, "title": new_title, "done": new_done}


# DELETE: Remover uma tarefa
@app.delete("/tasks/{task_id}", status_code=204)  # [cite: 1]
def delete_task(task_id: int):
    # 1. Verifica se a tarefa existe
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Task not found")  # [cite: 1]

    # 2. Executa o DELETE no banco de dados[cite: 1]
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))  # [cite: 1]
    conn.commit()

    return None