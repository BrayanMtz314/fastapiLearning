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


# Return to Readme.md
[**Readme.md**](../README.md)