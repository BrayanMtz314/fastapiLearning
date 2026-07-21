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


# Return to Readme.md
[**Readme.md**](../README.md)