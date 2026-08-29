"""
API RESTful de To-Do List usando FastAPI + SQLite (biblioteca padrão sqlite3).

Armazenamento persistente em arquivo tasks.db.
Executar com: uvicorn main:app --reload
Documentação Swagger automática em: http://127.0.0.1:8000/docs
"""

import sqlite3
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

DB_PATH = "tasks.db"

app = FastAPI(
    title="To-Do List API",
    description="API RESTful para gerenciamento de tarefas (CRUD) com persistência em SQLite.",
    version="2.0.0",
)


# ---------------------------------------------------------------------------
# Conexão com o banco de dados
# ---------------------------------------------------------------------------
@contextmanager
def get_connection():
    """Abre uma conexão SQLite por requisição e garante o fechamento correto."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Cria o arquivo do banco (se necessário), a tabela e insere o seed inicial."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT    NOT NULL,
                done  INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        # Seed apenas se a tabela estiver completamente vazia
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            seed_data = [
                ("Estudar FastAPI", 0),
                ("Configurar CNC router", 0),
                ("Migrar API para SQLite", 1),
            ]
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                seed_data,
            )


@app.on_event("startup")
def on_startup():
    init_db()


# ---------------------------------------------------------------------------
# Schemas (Pydantic)
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    title: str = Field(..., description="Título da tarefa")
    done: bool = Field(False, description="Status de conclusão da tarefa")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Novo título da tarefa")
    done: Optional[bool] = Field(None, description="Novo status de conclusão")


class Task(BaseModel):
    id: int
    title: str
    done: bool


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------
def row_to_task(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def find_task(conn: sqlite3.Connection, task_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()


# ---------------------------------------------------------------------------
# Rotas de sistema
# ---------------------------------------------------------------------------
@app.get("/", tags=["Sistema"])
def root():
    """Retorna informações básicas da API."""
    return {
        "name": "To-Do List API",
        "version": app.version,
        "description": "API RESTful para gerenciamento de tarefas (SQLite).",
        "docs": "/docs",
    }


@app.get("/health", tags=["Sistema"])
def health():
    """Retorna o status de integridade do servidor."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Rotas CRUD
# ---------------------------------------------------------------------------
@app.get("/tasks", response_model=list[Task], tags=["Tarefas"])
def list_tasks():
    """Retorna a lista completa de tarefas."""
    with get_connection() as conn:
        rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
    return [row_to_task(r) for r in rows]


@app.get("/tasks/{task_id}", response_model=Task, tags=["Tarefas"])
def get_task(task_id: int):
    """Retorna uma única tarefa pelo ID."""
    with get_connection() as conn:
        row = find_task(conn, task_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarefa com id {task_id} não encontrada.",
            )
        return row_to_task(row)


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tarefas"])
def create_task(task_in: TaskCreate):
    """Cria uma nova tarefa."""
    if not task_in.title or not task_in.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O título da tarefa não pode ser vazio.",
        )

    title = task_in.title.strip()
    done = int(task_in.done)

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, done),
        )
        new_id = cursor.lastrowid
        row = find_task(conn, new_id)

    return row_to_task(row)


@app.put("/tasks/{task_id}", response_model=Task, tags=["Tarefas"])
def update_task(task_id: int, task_in: TaskUpdate):
    """Atualiza o título e/ou o status 'done' de uma tarefa existente."""
    with get_connection() as conn:
        row = find_task(conn, task_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarefa com id {task_id} não encontrada.",
            )

        new_title = row["title"]
        new_done = row["done"]

        if task_in.title is not None:
            if not task_in.title.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O título da tarefa não pode ser vazio.",
                )
            new_title = task_in.title.strip()

        if task_in.done is not None:
            new_done = int(task_in.done)

        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, new_done, task_id),
        )
        updated_row = find_task(conn, task_id)

    return row_to_task(updated_row)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tarefas"])
def delete_task(task_id: int):
    """Remove uma tarefa pelo ID. Retorna 204 No Content."""
    with get_connection() as conn:
        row = find_task(conn, task_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarefa com id {task_id} não encontrada.",
            )
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    return None