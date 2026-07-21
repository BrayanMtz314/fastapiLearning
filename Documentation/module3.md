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



# Return to Readme.md
[**Readme.md**](../README.md)