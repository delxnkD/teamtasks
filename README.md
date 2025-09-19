# TeamTasks

A minimal, collaborative task-list web application built with Flask.

This repository contains a lightweight application for creating, sharing, and managing task lists. It includes a small reusable Python client library (`lib/tasklib`), unit tests, and a short demo script. It was designed to satisfy the B144 Software Design & Modelling assignment requirements, including runnable code, UML/architecture documentation, test evidence, and a short demo.

## Features

-   **User Management:** Registration and login with session-based authentication via Flask-Login.
-   **Role-Based Access:** Two user roles (`user`, `admin`), with the admin account created by an initialization script.
-   **Task Management:** Create, edit, and delete task lists and individual tasks.
-   **Collaboration:** Share lists with other users, granting either view or edit permissions.
-   **REST API:** A clean API for interacting with lists and tasks, used by both the frontend and the client library.
-   **Minimalist Frontend:** A responsive UI built with Bootstrap, custom CSS, and vanilla JavaScript.
-   **Reusable Client:** A small Python client library (`lib/tasklib`) for scripting and automation.
-   **Testing:** Unit tests written with `pytest` using an in-memory SQLite database for isolated test runs.

## Tech Stack

-   **Backend:** Python 3.10+, Flask, Flask-Login, Flask-SQLAlchemy
-   **Database:** SQLite (default)
-   **Frontend:** Jinja2 Templates, Bootstrap 5, Custom CSS & JS
-   **Testing:** `pytest`
-   **Client Library:** `requests`


## Quick Start (Development)

Follow these steps to get the development server running.

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/](https://github.com/)<your-org>/teamtasks.git
    cd teamtasks
    ```

2.  **Create & Activate Virtual Environment**
    ```bash
    python -m venv venv
    ```
    * On Windows (PowerShell):
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    * On macOS / Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize Database & Create Admin User**
    ```bash
    python run.py init-db
    ```
    The output will include the default admin credentials (e.g., username `admin` and password `adminpass`).

5.  **Run the Development Server**
    ```bash
    python run.py
    ```
    The server will be available at `http://127.0.0.1:5000`.

6.  **Open the App**
    Visit `http://127.0.0.1:5000` in your browser and log in with the admin credentials or register a new user.

## Run Server (Detailed Notes)

-   For production environments, you must change the `SECRET_KEY` and use a production-grade WSGI server (like Gunicorn or uWSGI) and a robust database (like PostgreSQL).
-   If you modify the SQLAlchemy models, you will need to implement a database migration strategy using a tool like Flask-Migrate (not included by default).

## API Endpoints

The API is mounted under `/api`. Only authenticated users (via their session cookie) can access these endpoints.

### `GET /api/lists`

Returns lists owned by and shared with the current user.
-   **Response:** ` { "owned": [list], "shared": [list] } `

### `POST /api/lists/<list_id>/tasks`

Creates a new task in the specified list. Requires ownership or edit permissions.
-   **JSON Body:** ` { "title": "Task title", "description": "optional" } `
-   **Response (201):** The created task object.

### `POST /api/tasks/<task_id>/toggle`

Toggles the `done` state of a task. Requires ownership or edit permissions.
-   **JSON Body:** ` { "done": true } ` (or `false`)
-   **Response:** The updated task object.

### `DELETE /api/tasks/<task_id>`

Deletes a task. Requires ownership or edit permissions.
-   **Response:** ` { "deleted": true } `

## Reusable Client Library (lib/tasklib)

The `lib/tasklib` directory contains a small, dependency-light Python client for interacting with the TeamTasks server programmatically.

### Example Usage

```python
from lib.tasklib.api import TaskAPI

# Initialize the client
api = TaskAPI("http://127.0.0.1:5000")

# Authenticate
api.login("admin", "adminpass")

# Get all lists
lists = api.get_lists()
print(lists)

# Create a new task in the first owned list
if lists and hasattr(lists[0], "id"):
    api.create_task(lists[0].id, "New task from script", "This is an optional description.")
```


## API Details

-   `TaskAPI(base_url)`: Constructs the client.
-   `login(username, password)`: Performs a form POST to authenticate and stores the session cookie for subsequent requests.
-   `get_lists()`: Returns a list of `ListData` objects.
-   `create_task(list_id, title, description="")`: Creates a new task and returns a `TaskData` object.

---

## Testing

Unit tests use `pytest` and run against a temporary in-memory SQLite database to ensure they are isolated and fast.

**To run tests:**

```bash
pytest -q    

