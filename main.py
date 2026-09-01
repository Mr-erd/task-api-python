import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from supabase import create_client, Client

load_dotenv()

# Recupere a URL do banco de dados JUNTO com as chaves do Supabase
DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Servidor executando e conectado ao Supabase")

# Modelos de Dados
class UserCredentials(BaseModel):
    email: str
    password: str

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# Inicialização do Banco
def init_db():
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            seed_data = [
                ("Aprender Docker", False),
                ("Configurar variáveis de ambiente", True),
                ("Conectar API no Postgres", False)
            ]
            conn.cursor().executemany("INSERT INTO tasks (title, done) VALUES (%s, %s)", seed_data)
        conn.commit()


app = FastAPI()


@app.get("/public/info", status_code=200)
def public_info():
    # Retorna uma mensagem pública sem exigir nenhuma autenticação
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile")
def protected_profile(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")

    token = auth_header.split(" ")[1]

    try:
        # Pergunta ao Supabase se o token é válido
        user_response = supabase.auth.get_user(token)

        # Se for validado com sucesso, retorna os dados seguros do usuário
        return {
            "message": "Acesso autorizado!",
            "user_id": user_response.user.id,
            "email": user_response.user.email
        }
    except Exception:
        # Se o token estiver expirado, adulterado ou inválido, barra a entrada
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.post("/auth/signup", status_code=201)
def signup(credentials: UserCredentials):
    try:
        # Repassa o email e senha para o Supabase registrar
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        return response
    except Exception as e:
        # Se faltar dados ou der erro no Supabase, retorna 400 Bad Request
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", status_code=200)
def login(credentials: UserCredentials):
    try:
        # Tenta autenticar o usuário no Supabase
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        return response
    except Exception:
        # Se a senha estiver errada, retorna 401 Unauthorized
        raise HTTPException(status_code=401, detail="Invalid login credentials")


@app.on_event("startup")
def on_startup():
    init_db()


# Rotas
@app.get("/", tags=["Sistema"])
def read_root():
    return {"name": "Task API", "version": "2.0 (Postgres)"}


@app.get("/tasks", tags=["Tarefas"])
def get_tasks():
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            cursor = conn.execute("SELECT id, title, done FROM tasks ORDER BY id")
            rows = cursor.fetchall()
            return [{"id": row[0], "title": row[1], "done": row[2]} for row in rows]
    except Exception as e:
        # Isso vai jogar o erro exato na tela do curl em vez de dar Erro 500
        return {"erro_fatal": str(e)}


@app.get("/tasks/{task_id}", tags=["Tarefas"])
def get_task(task_id: int):
    with psycopg.connect(DATABASE_URL) as conn:
        cursor = conn.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"id": row[0], "title": row[1], "done": row[2]}


@app.post("/tasks", status_code=201, tags=["Tarefas"])
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    with psycopg.connect(DATABASE_URL) as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
            (task.title, False)
        )
        new_id = cursor.fetchone()[0]
    return {"id": new_id, "title": task.title, "done": False}


@app.put("/tasks/{task_id}", tags=["Tarefas"])
def update_task(task_id: int, task: TaskUpdate):
    with psycopg.connect(DATABASE_URL) as conn:
        cursor = conn.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")

        current_title = row[1]
        current_done = bool(row[2])

        new_title = task.title if task.title is not None else current_title
        new_done = task.done if task.done is not None else current_done

        if task.title is not None and not task.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")

        conn.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
            (new_title, new_done, task_id)
        )
    return {"id": task_id, "title": new_title, "done": new_done}


@app.delete("/tasks/{task_id}", status_code=204, tags=["Tarefas"])
def delete_task(task_id: int):
    with psycopg.connect(DATABASE_URL) as conn:
        cursor = conn.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Task not found")
        conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))