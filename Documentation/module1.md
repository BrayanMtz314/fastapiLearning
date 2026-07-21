# Module 1: Getting Started with FastAPI – Web App & REST API

## 1. Project Setup & Environment
Managing dependencies and the virtual environment using `uv` on Linux.

* **Initialize Project:** Run `uv init <project_name>` to create the base structure.
* **Install Dependencies:** Run `uv add fastapi`. 
  * *Note:* This automatically installs FastAPI along with essential packages like `uvicorn` (the ASGI web server used to run the application).
* **Activate Virtual Environment:** `source .venv/bin/activate`
* **Deactivate Virtual Environment:** `deactivate`

## 2. Running the Application
* **Development Mode:** Run the server using the environment created by uv with `uv run fastapi dev main.py`.
  * The `dev` flag enables auto-reloading, meaning the server updates instantly whenever you save a change to the code.
* **Production Mode:** The `dev` flag should always be removed when deploying to a production environment.

## 3. Core Features & Routing
* **Auto-Serialization:** FastAPI automatically serializes Python objects (like dictionaries or database models) into JSON format. You do not need to manually serialize the data.
* **Custom Response Formats:** You can override the default JSON response. For example, to return an HTML page, use:
  ```python
  from fastapi.responses import HTMLResponse
  ```
## API Documentation
FastAPI automatically generates interactive API documentation based on your code.
* **Swagger UI:** Accessible at the `/docs` path from the root URL.

* **ReDoc:** An alternative documentation viewer accessible at the `/redoc` path.

* **Hiding Endpoints:** If you have internal routes that shouldn't appear in the public documentation, you can disable them by adding `include_in_schema=False` to the route decorator.


# Return to Readme.md
[**Readme.md**](../README.md)