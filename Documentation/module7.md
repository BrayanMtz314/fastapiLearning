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


# Return to Readme.md
[**Readme.md**](../README.md)