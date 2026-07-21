# Module 11: Authorization - Protecting Routes and Verifying the Current User

In the previous module, we gave users the ability to log in and get a token. In this module, we actually enforce security by protecting our routes and ensuring users can only modify their own data.

## 1. The `get_current_user` Dependency (`auth.py`)
To protect a route, FastAPI needs a way to look at the incoming request, extract the token, and figure out who is making the request. 

* **Required Imports:**
  ```python
  from typing import Annotated
  from fastapi import Depends, HTTPException, status
  from sqlalchemy import select
  from sqlalchemy.ext.asyncio import AsyncSession
  import models
  from database import get_db
  ```

* **The Dependency Function:** We build `get_current_user()`. This function intercepts the token from the browser's request, decodes it, looks up the user in the database, and returns the full `models.User` object. If the token is invalid or missing, it blocks the request.

```python
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> models.User:
    # Logic to decode token and fetch user from DB...
    pass
```

## 2. Securing Schemas (Never Trust the Client)
Previously, the frontend had to tell the API which user was creating a post. This is a massive security risk (a malicious user could send `user_id: 2` and write a post as someone else).

* **The Fix:** We remove `user_id` entirely from the `PostCreate` schema. The API will no longer accept this information from the client.

```python
class PostCreate(PostBase):
    pass # We only expect title and content now
```

## 3. Protecting Endpoints (`routers/posts.py` & `routers/users.py`)
Now we inject our new `get_current_user` dependency into our endpoints.

* **Creating Posts:** We extract the `user_id` directly from the `current_user` object. This guarantees the post is authored by the person who is actually logged in.

```python
# Notice the new 'current_user' parameter
async def create_post(post: PostCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id # Securely assigned by the backend!
    )
    # ... save to database ...
```

* **Updating & Deleting (Ownership Checks):** For the `update_full`, `update_partial`, and `delete_post` functions, checking if a user is logged in isn't enough. We must add logic to verify that the `current_user.id` matches the `post.user_id`. If someone tries to edit a post they don't own, we raise an HTTP 403 Forbidden error.

* **User Routes:** We apply this same logic to `users.py` so users can only update or delete their own accounts.

## 4. Frontend Integration: Removing Hardcoded Users
Our API is now secure, but the frontend templates (`layout.html` and `post.html`) were still using our temporary, hardcoded `user_id = 1` to show the Create/Edit/Delete buttons.

* **The Fix:** We update the JavaScript in our frontend to rely on the `get_token()` function. The UI will now dynamically check if a valid token exists in local storage and update the interface accordingly (e.g., showing the "New Post" button only for logged-in users, and showing "Edit/Delete" only if the logged-in user owns that specific post).


## 5. Account Management Interface
Now that users have secure, isolated data, they need a place to manage their profiles.

* We added an `account.html` template.

* We added a new route in `main.py` that serves this page, allowing users to view and update their specific account details securely.

## 6. Summary
By completing this module, the application now has a fully functioning, secure loop:

1. Unauthenticated users can read posts.

2. Authenticated users can create posts.

3. Authorized users (the specific owners) can edit or delete their own posts and manage their accounts.


# Return to Readme.md
[**Readme.md**](../README.md)