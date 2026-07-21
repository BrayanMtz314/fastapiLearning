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


# Return to Readme.md
[**Readme.md**](../README.md)