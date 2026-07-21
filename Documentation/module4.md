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


# Return to Readme.md
[**Readme.md**](../README.md)