# Module 10: Authentication - Registration and Login with JWT

Adding security to an application is critical. In this module, we implement a complete JSON Web Token (JWT) authentication system, allowing users to securely register, log in, and maintain an authenticated session.

## 1. Required Packages
To handle password hashing, token generation, and environment variables, we install three new libraries:
```bash
uv add "pwdlib[argon2]" pyjwt pydantic-settings
```

* `pwdlib[argon2]`: Used to securely hash passwords using the Argon2 algorithm (the current industry standard for password hashing).

* `pyjwt`: Used to encode and decode JSON Web Tokens (JWTs).

* `pydantic-settings`: Manages application settings and reads sensitive environment variables securely from a .env file.


## 2. Updating Database Models & Schemas
Because our user security requirements have changed, we must update our data models. (Note: When SQLite tables change significantly during development, we often delete the old database file so SQLAlchemy can recreate tables with the new schema).

* **Database Model (`models.py`):** We add a column to store the hashed password—never the plain-text password!

```python
password_hash: Mapped[str] = mapped_column(String(200), nullable=False) 
```

* **Pydantic Schemas (`schemas.py`):** We enforce an 8-character minimum for passwords during registration, and we split our user response models into Public and Private states to prevent leaking sensitive information (like email addresses) to other users.

```python
class UserCreate(UserBase):
    password: str = Field(min_length=8)

# Used when viewing other users' profiles (e.g., author of a post)
class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str

# Used when a user is viewing their own profile (includes sensitive email data)
class UserPrivate(UserPublic):
    email: EmailStr

# Schema for the OAuth2 login response
class Token(BaseModel):
    access_token: str
    token_type: str
```

## 3. Environment Variables & Security Configuration (`config.py`)

To prevent hardcoding secret keys into our source code, we use `pydantic-settings` to load sensitive configuration from a local `.env` file.

* **Configuration File (`config.py`):**

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

settings = Settings()
```

* **Security Best Practice:** We create a `.env` file in our root folder containing our project's secret key. We immediately add `.env` to our `.gitignore` file so sensitive secrets are never committed to version control (GitHub).

## 4. Core Authentication Logic (`auth.py`)
We create a dedicated `auth.py` file to handle all cryptography, password verification, and token management.

```python
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from datetime import timedelta

# Initialize recommended Argon2 password hasher
password_hash = PasswordHash.recommended()

# Points to the API endpoint where frontend clients will request tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

def hash_password(password: str) -> str:
    """Return a securely hashed version of a plain-text password."""
    pass

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the provided plain-text password matches the stored hash."""
    pass

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generate a signed JWT containing user claims and an expiration time."""
    pass

def verify_access_token(token: str) -> str | None:
    """Decode and validate a JWT using our secret key."""
    pass
```

## 5. Router Updates (`routers/users.py`)
We update our user endpoints to integrate the authentication logic:

* **Registration:** When a user creates an account, we intercept the raw password, pass it through `hash_password()`, and store only the resulting hash in the database.


* **Token Endpoint (`/api/users/token`):** We add a standard OAuth2 login endpoint. This route checks a user's credentials using `verify_password()`; if valid, it generates and returns a JWT access token using `create_access_token()`.

* **Schema Filtering:** Endpoints returning user data now dynamically use `UserPublic` or `UserPrivate` depending on who is making the request.

## 6. Frontend Integration (HTML & JS)
To connect the user interface to our new authentication API, we add registration templates and browser-side token management.

* **Registration Template (`register.html`):** Displays the registration form and includes client-side JavaScript validation to ensure the "Password" and "Confirm Password" fields match before submitting.

* **Auth Scripts (`static/js/auth.js`):** Handles the frontend authentication workflow:

    * Sending user login credentials to the `/token` endpoint.

    * Saving the returned JWT securely in the browser's `localStorage` (or `sessionStorage`).

    * Automatically attaching the token as a `Bearer` header in future fetch requests to authenticate the user.

    * Managing UI state (e.g., showing/hiding the "New Post" or "Logout" buttons based on whether a valid token exists).


## 7. Module Summary: How JWT Authentication Works
This module establishes a standard stateless authentication workflow:

1. **Registration:** A user submits their credentials. The backend hashes the password using Argon2 and stores the user in the database.

2. **Login:** The user submits their username and password to /api/users/token. The backend verifies the password against the stored hash.

3. **Token Issuance:** Upon successful verification, the server signs a JSON Web Token (JWT) using its secret key and sends it back to the client.

4. **Client Storage:** The browser script (auth.js) stores this token locally.

5. **Authenticated Requests:** For any protected action (like creating or editing a post), the frontend sends the token in the HTTP Authorization header (Bearer <token>).

6. **Verification:** FastAPI decodes the token using OAuth2 dependencies (oauth2_scheme), verifies the signature, and identifies the user without needing to repeatedly query the database for login credentials.



# Return to Readme.md
[**Readme.md**](../README.md)