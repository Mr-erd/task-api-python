# Task API: In-Memory CRUD with FastAPI

A RESTful API built with Python and FastAPI to manage a to-do list. This project was developed to demonstrate the implementation of core CRUD operations (Create, Read, Update, Delete), proper HTTP status codes management, and strict data validation.

## 🚀 Quick Start (How to run this project)

This API runs locally and uses in-memory storage (no external database required).

### Prerequisites
- Python 3.10+
- Git

### Installation & Execution
1. Clone the repository and navigate to the project folder.
2. Install the required dependencies:
   ```bash
   pip install fastapi uvicorn
   ```
3. Start the local server:
   ```bash
   python -m uvicorn main:app --reload
   ```
The server will start at `http://localhost:8000`.

## 🗂️ Endpoints Reference

The API provides the following endpoints to manage tasks.

| Operation | HTTP Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Read (List)** | `GET` | `/tasks` | Returns a list of all tasks |
| **Read (Single)** | `GET` | `/tasks/{task_id}` | Returns a specific task by its ID |
| **Create** | `POST` | `/tasks` | Creates a new task (requires JSON body) |
| **Update** | `PUT` | `/tasks/{task_id}` | Updates a task's title and/or done status |
| **Delete** | `DELETE` | `/tasks/{task_id}` | Deletes a task by its ID |
| **Info** | `GET` | `/` | Returns general API information |
| **Health** | `GET` | `/health` | Returns the server's health status |

## 💻 cURL Example

Here is a complete example of a `POST` request creating a new task, demonstrating the JSON input and the exact HTTP response (including the `201 Created` status code).

**Request:**
```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy coffee"}'
```

**Response:**
```http
HTTP/1.1 201 Created
date: Tue, 25 Aug 2026 01:25:46 GMT
server: uvicorn
content-length: 42
content-type: application/json

{"id":4,"title":"Buy coffee","done":false}
```

## 📖 Interactive Documentation (Swagger UI)

FastAPI automatically generates a live, interactive OpenAPI documentation. Once the server is running, you can access the Swagger UI to explore and test all endpoints directly from your browser without needing tools like Postman or cURL.

**Access the docs at:** `http://localhost:8000/docs`

![Swagger UI Screenshot](./swagger.png)

## 🏗️ Technical Details & Business Rules
- **Pagination:** The `GET /tasks` endpoint supports pagination via `limit` and `offset` query parameters. Real-world APIs never return "everything" at once because retrieving millions of records simultaneously would consume excessive server memory, overload the database, and result in massive network delays for the client.
- **In-Memory Storage:** Data is stored in a Python list. Restarting the server resets the data to its initial state.
- **Validation:** Creating or updating a task with an empty string as a title returns a `400 Bad Request`.
- **Error Handling:** Requesting, updating, or deleting a non-existent task ID returns a `404 Not Found` with a clear JSON error message.
## 🤖 AI vs Me (Stage 7 - The Rematch)

**Prompt used:**
"Atue como um desenvolvedor backend sênior. Construa uma API RESTful em Python utilizando o framework FastAPI. A API deve gerenciar uma lista de tarefas (To-Do list) executando as quatro operações principais do CRUD. Utilize uma lista em memória para guardar os dados. Rotas: GET /, GET /health, GET /tasks, GET /tasks/{id}, POST /tasks (201), PUT /tasks/{id}, DELETE /tasks/{id} (204). Validação: Título vazio no POST/PUT retorna 400. ID não encontrado retorna 404."

**1. What did the AI do better?**
The AI included a very helpful top-level docstring to explain the module. It also utilized more advanced Pydantic features like `Field` for data validation, the `typing.Optional` module for clearer type hinting, and the `fastapi.status` module instead of hardcoding HTTP status integers.

**2. What did it get wrong or quietly ignore?**
Because the prompt was somewhat brief, the AI assumed its own structure for the data model initialization, which might differ from a strictly simple dictionary list if not tightly constrained. 

**3. What did your prompt forget to specify?**
I completely forgot to specify the "Stretch Goal" in the prompt! I didn't ask the AI to implement **Pagination** (`limit` and `offset`) for the `GET /tasks` route, so it built a standard route that returns all items at once.

## 💾 Database Integration (Week 3)

- **Why SQLite:** It was chosen because it requires zero configuration, operates from a single file, and ensures data survives server restarts perfectly.
- **Where the data lives:** The data lives in a file named `tasks.db`. This file is automatically created and seeded with initial tasks the first time the server runs.
- **How to run:** Start the API using `python -m uvicorn main:app --reload`[cite: 1].
- **SQL Exploration:** I used DB Browser to run raw queries like `SELECT COUNT(*) FROM tasks;` to verify data independently of the API[cite: 1].

### DB Browser Snapshot
![DB Browser View](./db_screenshot.png)

