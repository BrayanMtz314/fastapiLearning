# LEARNING FASTAPI
These are my notes from when I took the FastAPI Course by Corey Schafer [link to video](https://www.youtube.com/watch?v=iukOehU5aF4&t=10369s)

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


# Module 6: Completing CRUD - Update and Delete (PUT, PATCH, DELETE)

With the addition of Update and Delete functionality, our API now has complete CRUD (Create, Read, Update, Delete) capabilities.

## 1. Updating Schemas for Partial Modifications
To allow users to update only specific fields of a post, we need a new Pydantic schema where all fields are optional.

* **Implementation:** By setting the type to `str | None` and the default to `None`, we tell Pydantic that the user doesn't have to provide these fields.
```python
from pydantic import BaseModel, Field

class PostUpdate(BaseModel):
    # The user can change the title and/or content, or neither.
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)
```

## 2. Full Updates (PUT Method)
The PUT method is used when you want to completely replace an existing resource.

* Because it requires a full replacement, we reuse the `PostCreate` schema, which forces the user to provide all required fields (title, content, author).
```python
@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post_full(post_id: int, post_data: PostCreate, db: Annotated[Session, Depends(get_db)]):
    # Logic to find the post and replace all its data...
```

## 3. Partial Updates (PATCH Method)
The `PATCH` method is used to apply partial modifications. The user only sends the fields they want to change.

* `exclude_unset=True`: This is the most important part of the logic. It ensures that Pydantic only extracts the fields the user actually sent in the request, preventing us from accidentally overwriting existing database values with `None`.
```python
@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(post_id: int, post_data: PostUpdate, db: Annotated[Session, Depends(get_db)]):
    # 1. Fetch the existing post
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    
    if not post:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # 2. Extract ONLY the fields the user provided in the request
    update_data = post_data.model_dump(exclude_unset=True)
    
    # 3. Update the database object dynamically
    for field, value in update_data.items():
        setattr(post, field, value)

    # 4. Save changes
    db.commit()
    db.refresh(post)
    return post
```

## 4. Deleting Resources (DELETE Method)
When a resource is successfully deleted, the standard practice is to return no data.

* **Status Code**: We use `status.HTTP_204_NO_CONTENT`. The endpoint will successfully execute the delete query and return an empty response body.

## 5. HTTP Status Code Cheat Sheet
A summary of the standard REST API status codes used in this project:

* **200 OK:** Successful GET, PUT, or PATCH.

* **201 Created:** Successful POST (e.g., creating a new user or post).

* **204 No Content:** Successful DELETE (resource removed, nothing to return).

* **400 Bad Request:** Client error (e.g., duplicate username/email when creating a user).

* **404 Not Found:** The requested resource (user or post) does not exist.

* **422 Unprocessable Entity:** Validation error caught automatically by Pydantic (e.g., sending a string instead of an integer).

## 6. Relationships & Cascade Deletions
We repeated the same CRUD logic for the `User` endpoints. However, deleting a user introduces a database problem: what happens to the posts they wrote?

* **Cascade Deletion:** We can tell SQLAlchemy to automatically delete all child objects (Posts) when the parent object (User) is deleted.

* **Implementation in models.py:** We update the relationship definition in the User model by adding `cascade="all, delete-orphan"`.

```python
# Inside the User model in models.py
posts: Mapped[list["Post"]] = relationship(
    back_populates="author", 
    cascade="all, delete-orphan" # Automatically deletes the user's posts if the user is deleted
)
```

# Module 7: Synchronous vs. Asynchronous Programming

## 1. Sync vs. Async Concepts
* **Synchronous (Sync):** Each step must fully complete before the next one starts. If the app asks the database for information, the entire server pauses and waits until the database replies.
* **Asynchronous (Async):** Steps can begin without waiting for the previous one to finish. If the app asks the database for info, it yields control, allowing the server to handle *other* users' requests while waiting for the database to reply.

**When to use which?**
* **Use Async:** For I/O-bound operations (managing multiple independent tasks, calling external APIs, making database queries, reading files). This provides massive performance benefits for web servers.
* **Use Sync:** For CPU-bound operations (heavy mathematical calculations, image processing, complex data transformations).

## 2. Installing Async Drivers
To make SQLAlchemy asynchronous, we need an async driver for SQLite and a library to help SQLAlchemy manage async execution contexts.
```bash
uv add aiosqlite
uv add greenlet
```

## 3. Updating the Database Setup (`database.py`)

The connection setup must be completely rewritten to use async classes and functions.

* `create_engine` becomes `create_async_engine`

* `sessionmaker` becomes `async_sessionmaker`

* `Session` becomes `AsyncSession`

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## 4. Database Initialization (Lifespan Events)

Previously, we used `Base.metadata.create_all(bind=engine)` directly in `main.py`. Because table creation is an I/O operation, it must now be awaited. We handle this using FastAPI's "lifespan" context manager to safely run code when the server starts up and shuts down.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup: Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    # Shutdown: Cleanly close the database connection
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

## 5. Lazy Loading vs. Eager Loading
This is the biggest change when moving to Async SQLAlchemy.

* **The Problem:** In Sync mode, if you try to access a post's author (e.g., `post.author`), SQLAlchemy automatically runs a secret background query to fetch it ("Lazy Loading"). In Async mode, lazy loading is not supported because every database query requires an await keyword.

* **The Solution:** We must use Eager Loading (`selectinload`). We have to explicitly tell SQLAlchemy to fetch the relationships at the exact same time it fetches the initial object.

```python
# Example: Loading posts and eagerly loading their authors
from sqlalchemy.orm import selectinload
from sqlalchemy import select

@app.get("/", name="home", include_in_schema=False)
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    # Notice the .options(selectinload(...))
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)))
    posts = result.scalars().all()
    # ... return template ...
```

## 6. Updating Endpoints with `await`
Every endpoint interacting with the database must be converted to an `async def` function, and any operation that touches the database must use `await`.

* **Memory vs. I/O:**
```python
db.add(new_user)       # NO AWAIT: This only stages the object in local RAM.
await db.commit()      # AWAIT: This actually writes the data to the database over the network.
await db.refresh(new_user) # AWAIT: This reads the new data (like the generated ID) back from the database.
```

* **Refreshing Relationships:** When creating or updating a post, if you need the response to include the author data, you must explicitly tell db.refresh to fetch the relationship attribute asynchronously:
```python
await db.refresh(new_post, attribute_names=["author"])
```

## 7. Updating Exception Handlers
Our custom exception handlers must also become async. We can delegate the JSON formatting back to FastAPI's default async handlers for API routes.

```python
from fastapi.exception_handlers import http_exception_handler

@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    # API endpoints use the default async JSON handler
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)
    
    # Frontend routes return the custom HTML template
    message = exception.detail if exception.detail else "An error occurred. Please check your request and try again"
    # ... return TemplateResponse ...
```







