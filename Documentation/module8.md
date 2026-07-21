# Module 8: Routers - Code Organization

## 1. The Problem: Code Bloat
As our application grows, `main.py` becomes overloaded. Keeping all our API URLs, page routes, database connections, and error handlers in a single file becomes a nightmare to maintain. 

* **The Solution:** We use **Routers** (specifically `APIRouter`). This allows us to split our endpoints into separate files based on their functionality (e.g., separating users from posts), optimizing our code organization.

## 2. Directory Structure
To implement this, we create a new folder to house our routing logic.

* **`/routers` directory:**
  * `__init__.py`: An empty file that tells Python to treat this directory as a proper module (a standard Python best practice).
  * `users.py`: Contains all the endpoints related to users.
  * `posts.py`: Contains all the endpoints related to posts.

## 3. Setting Up a Router File (e.g., `users.py`)
Inside your new router files, you no longer use the `app` object to create endpoints. Instead, you use an `APIRouter` instance.

* **Required Imports & Initialization:**
```python
  from fastapi import APIRouter
  
  # Create a router instance for this specific file
  router = APIRouter()
  
  # Use @router.get instead of @app.get
  @router.get("/")
  def get_users():
      pass
```

## 4. Relative Paths
Because we are handling routes dynamically, the paths declared in our endpoint decorators must change.

* Instead of hardcoding the full path in every single function, we declare the "root" path in `main.py` and use relative paths inside our router files.

* Example:

* Old way (in `main.py`): `@app.get("/api/users/{user_id}")`

* New way (in `users.py`): `@router.get("/{user_id}")`

## 5. Connecting Routers to `main.py`
After moving all the route functions out of `main.py` and into their specific router files, we need to wire everything back together.

** Clean Up: First, remove all the Pydantic schema imports from `main.py` that are no longer needed there.

* Import the Routers: `from routers import posts, users`

* Include the Routers: We attach them to our main app instance using `app.include_router()`.
```python
# prefix: Automatically adds this string to the beginning of every route in the file.
# tags: Groups these endpoints together under a specific heading in the /docs UI.

app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
```

## 6. Summary
By doing this, a request to `GET /api/users/5` hits `main.py`, sees the `/api/users` prefix, forwards the request to the `users.router`, and matches the `/{user_id}` endpoint. The application functions exactly the same, but the codebase is now modular and easy to read.


# Return to Readme.md
[**Readme.md**](../README.md)