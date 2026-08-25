from fastapi import FastAPI, HTTPException

app = FastAPI()

# 1. Nosso "banco de dados" em memória (uma lista de dicionários)
tasks_db = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Learn FastAPI", "done": True},
    {"id": 3, "title": "Build a CRUD API", "done": False}
]


@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# 2. Rota para ler todas as tarefas (List)
@app.get("/tasks")
def get_tasks():
    return tasks_db


# 3. Rota para ler uma tarefa específica (Single task) usando Path Parameter
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    # Procura a tarefa pelo ID
    for task in tasks_db:
        if task["id"] == task_id:
            return task

    # Se o loop terminar e não achar nada, retorna o erro 404
    raise HTTPException(status_code=404, detail="Task not found")