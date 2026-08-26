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
- **In-Memory Storage:** Data is stored in a Python list. Restarting the server resets the data to its initial state.
- **Validation:** Creating or updating a task with an empty string as a title returns a `400 Bad Request`.
- **Error Handling:** Requesting, updating, or deleting a non-existent task ID returns a `404 Not Found` with a clear JSON error message.