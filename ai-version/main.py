"""
API RESTful de To-Do List usando FastAPI.

Armazenamento em memória (lista de dicionários).
Executar com: uvicorn main:app --reload
Documentação Swagger automática em: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="To-Do List API",
    description="API RESTful para gerenciamento de tarefas (CRUD) com armazenamento em memória.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# "Banco de dados" em memória
# ---------------------------------------------------------------------------
tasks: list[dict] = [
    {"id": 1, "title": "Estudar FastAPI", "done": False},
    {"id": 2, "title": "Configurar CNC router", "done": False},
]
next_id: int = 3


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
def find_task(task_id: int) -> Optional[dict]:
    return next((t for t in tasks if t["id"] == task_id), None)


def error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": message})


# ---------------------------------------------------------------------------
# Rotas de sistema
# ---------------------------------------------------------------------------
@app.get("/", tags=["Sistema"])
def root():
    """Retorna informações básicas da API."""
    return {
        "name": "To-Do List API",
        "version": app.version,
        "description": "API RESTful para gerenciamento de tarefas.",
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
    return tasks


@app.get("/tasks/{task_id}", response_model=Task, tags=["Tarefas"])
def get_task(task_id: int):
    """Retorna uma única tarefa pelo ID."""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tarefa com id {task_id} não encontrada.")
    return task


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tarefas"])
def create_task(task_in: TaskCreate):
    """Cria uma nova tarefa."""
    global next_id

    if not task_in.title or not task_in.title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O título da tarefa não pode ser vazio.")

    new_task = {"id": next_id, "title": task_in.title.strip(), "done": task_in.done}
    tasks.append(new_task)
    next_id += 1
    return new_task


@app.put("/tasks/{task_id}", response_model=Task, tags=["Tarefas"])
def update_task(task_id: int, task_in: TaskUpdate):
    """Atualiza o título e/ou o status 'done' de uma tarefa existente."""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tarefa com id {task_id} não encontrada.")

    if task_in.title is not None:
        if not task_in.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O título da tarefa não pode ser vazio.",
            )
        task["title"] = task_in.title.strip()

    if task_in.done is not None:
        task["done"] = task_in.done

    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tarefas"])
def delete_task(task_id: int):
    """Remove uma tarefa pelo ID. Retorna 204 No Content."""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tarefa com id {task_id} não encontrada.")

    tasks.remove(task)
    return None