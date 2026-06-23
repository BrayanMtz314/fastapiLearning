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



# Module 2: HTML Frontend for Your API - Jinja2 Templates

## 1. What is Jinja2?
Jinja2 is a templating engine for Python. It allows you to write standard HTML but inject Python variables, loops, and logic directly into the page before it gets sent to the user's browser.

* **Installation:** If you initialized your project with `uv add "fastapi[standard]"`, Jinja2 is already included. If not, you need to install it manually (e.g., `uv add jinja2`).

## 2. Setting Up Templates
To use HTML files, you need to tell FastAPI where they are located.

* **Configuration:** You instantiate a `Jinja2Templates` object, pointing it to your designated folder (usually named `templates`).
  ```python
  from fastapi.templating import Jinja2Templates
  templates = Jinja2Templates(directory="templates")
  ```
## 3. Returning Template Responses
Instead of returning JSON (like a standard REST API), you return a rendered HTML page using the TemplateResponse method.

* Example:

```python
return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "HOME"})
```

* How it works:

  * request: FastAPI requires the current request object to be passed to the template.

  * "home.html": The specific HTML file you want to render.

  * {"posts": posts, ...}: The "context" dictionary. This is how you pass data from your Python backend into the Jinja2 variables inside your HTML.

## 4. Serving Static Files
Static files are assets that don't change dynamically, such as CSS styles, JavaScript files, and images (like logos or icons).

* Mounting the Directory: You must explicitly tell FastAPI to serve these files using app.mount().

```python
from fastapi.staticfiles import StaticFiles
# This makes any file inside the "static" folder accessible via the "/static" URL path
app.mount('/static', StaticFiles(directory="static"), name="static")
```

## 5. Best Practices: Dynamic URLs (url_for)
When linking to CSS, images, or other pages inside your HTML templates, never hardcode the URLs (e.g., href="static/icons/favicon.ico"). If your folder structure or routing ever changes, hardcoded links will break.

* The Solution: Use Jinja's url_for() function. It dynamically generates the correct URL based on the route name.

* Example in HTML (e.g., layout.html or home.html):

```html
<link rel="icon" href="{{ url_for('static', path='icons/favicon.ico') }}">
```

# Module 3: Path Parameters, Validation, and Error Handling

## 1. Path Parameters
Path parameters allow you to create dynamic URLs to load specific resources, like a single blog post. FastAPI automatically captures the variable from the URL path.

* **Type Validation:** By declaring the type (e.g., `post_id: int`), FastAPI automatically validates that the parameter is an integer and adds this requirement to the auto-generated documentation.

```python
@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    # Notice this is outside the loop! It only runs if no post is found.
    return {"error": "Post not found"}
```

## 2. Using HTTP Exceptions (API Best Practices)

Returning a simple dictionary like `{"error": "Not found"}` is not a best practice. A proper REST API should use standard HTTP Status Codes (like `404 Not Found` or `400 Bad Request`).

* Implementation: Use HTTPException and status from fastapi.

* Example
```python
from fastapi import HTTPException, status

# Instead of returning an error dictionary, we raise an exception:
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
```

## 3. Path Parameters with HTML Templates

You can also use path parameters to serve dynamic HTML pages instead of API JSON data.

* **Hiding Web Routes:** We use `include_in_schema=False` so these frontend pages don't clutter up the API docume**ntation (`/docs`).

```python
from fastapi import Request

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            # Truncate the title for the HTML tab
            title = post['title'][:50] 
            return templates.TemplateResponse(
                request,
                "post.html",
                {"post": post, "title": title}
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
```

## 4. Dynamic Links in Jinja Templates

When building the frontend (like a home page listing all posts), you can dynamically generate links to individual post pages using `url_for`.

* **Example (in your home page HTML):**
```html
<a class="article-title" href="{{ url_for('post_page', post_id=post.id) }}">{{ post.title }}</a>
```

## 5. Global Error Handling (API vs. Web)

When an error occurs, you usually want to return a JSON response if the user is calling an `/api` endpoint, but show a nice HTML error page if they are browsing the website.

* **Required Imports**
```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
```

* **Custom Exception Handlers:** You can override FastAPI's default error handling using the `@app.exception_handler()` decorator.

```python
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    # Set a default message if none is provided
    message = exception.detail if exception.detail else "An error occurred. Please try again."

    # If the request was for the API, return JSON
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    # If the request was for the web interface, return an HTML template
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": f"Error {exception.status_code}",
            "message": message,
        },
        status_code=exception.status_code,
    )
```

* **Validation Errors:** You can create a second handler using `@app.exception_handler(RequestValidationError)`. This catches "Type" errors (e.g., a user typing `/posts/abc` instead of `/posts/1`). It functions the exact same way, returning JSON for API routes and an HTML template for frontend users.


# Module 4: Pydantic Schemas - Request and Response Validation

## 1. What is Pydantic?
Pydantic is a Python library designed for data validation and settings management. FastAPI explicitly uses Pydantic as its core foundation for handling data. It acts as a strict "data contract" between the client and your backend.

* **Native Data Validation:** Provides automatic parsing, instant validation, clear error messages, and type coercion (e.g., converting a string `"123"` to an integer `123` if required).
* **Standardized Documentation:** Integrates seamlessly with OpenAPI, meaning your data models automatically generate the interactive UI (`/docs`) with zero duplication of effort.

## 2. Setting Up `schemas.py`
Best practices dictate keeping your data models in a dedicated file, typically named `schemas.py`.

* **Required Imports:**
  ```python
  from pydantic import BaseModel, ConfigDict, Field
  
  # BaseModel: The core class that all our Pydantic models inherit from.
  # Field: Allows us to add constraints to attributes (like minimum/maximum lengths).
  # ConfigDict: The modern way to configure model behavior in Pydantic v2.
  ```

## 3. Defining Schema Models

A standard practice in FastAPI is to use inheritance to avoid repeating code. We define a "Base" model with shared attributes, and then create specific variations for creating data versus returning data.

```python
class PostBase(BaseModel):
    # Field enforces validation rules automatically
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50) 

# Used for reading incoming POST requests
class PostCreate(PostBase):
    pass # Inherits exactly what is in PostBase

# Used for formatting the outgoing response
class PostResponse(PostBase):
    # This allows Pydantic to read data from ORM objects (like database models), 
    # not just standard Python dictionaries.
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: str
```

## 4. Applying Schemas in Endpoints
Once your models are defined, you use them directly in your route decorators and function parameters.

* **Response Validation** (`response_model`): By defining `response_model=PostResponse` in the `@app.get()` decorator, FastAPI guarantees that the outgoing data will be filtered and formatted to match that specific model. It also updates the automatic documentation to show exactly what a user can expect to receive.

```python
@app.get("/posts/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int):
    # Code to retrieve post...
```

* **Request Validation** (Creating Data): Pydantic excels when receiving data (like a new post). If you set a parameter as `post: PostCreate`, FastAPI will intercept the incoming JSON, check that all fields exist and meet the `Field` constraints, and automatically return a detailed HTTP 422 (Unprocessable Entity) status code if there is a validation error.

## 5. Summary

Pydantic schemas define the strict API contracts of your application. They give you absolute control and certainty over exactly what data is allowed to come in, and exactly what data is allowed to go out.


# Module 5: Adding a Database - SQLAlchemy Models and Relationships

## 1. Object-Relational Mapping (ORM)
To interact with a database easily, we use an ORM. It translates (maps) Python classes into relational database tables, allowing you to query and manipulate data using standard Python code instead of writing raw SQL strings.

* **Library:** FastAPI commonly pairs with `sqlalchemy`.
* **Installation:** Run `uv add sqlalchemy` to add it to your project.
* **Database Engine:** For this module, we are using **SQLite**. It is a lightweight database that stores everything in a local file, making it perfect for development.

## 2. Separation of Concerns (Project Structure)
Best practices dictate splitting the database logic into specific files:

* **`database.py`:** Handles the core setup and connection. This is where you configure the database URL, create the connection `engine`, set up the `SessionLocal`, and define the `Base` class.
* **`models.py`:** Contains the actual data structures. Each object class (like a Post or User) inherits from `Base` and defines how its attributes map directly to the database columns.

## 3. Initializing the Database in `main.py`
To connect your FastAPI app to the database, you need to import your database configuration and models into `main.py`.

* **Required Imports:**
  ```python
  from typing import Annotated
  from sqlalchemy import select
  from sqlalchemy.orm import Session
  from fastapi import FastAPI, Request, HTTPException, status, Depends
  
  import models
  from database import Base, engine, get_db
  from schemas import PostCreate, PostResponse, UserCreate, UserResponse
  ```

  * **Creating Tables**
  ```python
  models.Base.metadata.create_all(bind=engine)
  ```
*How it works:* When the app starts, this line checks all models that inherit from `Base` and creates their corresponding tables in the database. It is perfectly safe to leave this in your code because it only creates tables if they do not already exist.

## 4. Dependency Injection (Depends)

FastAPI uses "Dependency Injection" to manage database connections. Instead of keeping a global database connection open, FastAPI provides a fresh database session for each individual request and closes it when the request is done.

* **Example Endpoint:** We use `Depends(get_db)` to inject the database session into the function.

```python
@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    # You can now use the 'db' variable to add the user to the database
    pass
```

* **Next Steps:** Every endpoint that needs to read from or write to the database must be updated to include this `db` parameter.

## 5. Updating Jinja Templates 

Now that your API endpoints are fetching data from a real database, they are passing SQLAlchemy ORM objects to your frontend templates instead of simple Python dictionaries.

* **HTML Updates:** You must update files like `post.html` and `home.html`. While dictionaries use bracket notation (e.g., `post["title"]`), ORM objects use dot notation (e.g., `post.title`). Jinja is flexible, but it's important to ensure your templates correctly reference the new object structures.






