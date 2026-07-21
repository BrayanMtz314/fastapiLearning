# Module 14: Password Reset - Email, Tokens, and Background Tasks

In this module, we create a complete, secure workflow for password recovery. This involves generating secure one-time tokens, sending asynchronous emails, and updating database records securely.

## 1. Asynchronous Email Dependency
To send emails without freezing our server, we need an asynchronous SMTP library.
```bash
uv add aiosmtplib
```

## 2. Configuration & Mailtrap Sandbox
During development, sending real emails is risky and can lead to spamming actual addresses. Instead, we use Mailtrap.io, a sandbox service that captures all outgoing test emails.

* **Updating `config.py`:** We add variables to handle email server settings and our frontend URL.
```python
reset_token_expire_minutes: int = 60

## Email Configuration Settings
mail_server: str = "localhost"
mail_port: int = 587
mail_username: str = ""
mail_password: SecretStr = SecretStr("")
mail_from: str = "noreply@example.com"
mail_use_tls: bool = True

frontend_url: str = "http://localhost:8000"
```
* **Updating `.env`:** We add our Mailtrap credentials (found in the Mailtrap integration tab) to our `.env` file so they remain secure.
```code
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=<your_username>
MAIL_PASSWORD=<your_password>
MAIL_FROM=noreply@fastapiblog.com
MAIL_USE_TLS=true
FRONTEND_URL=http://localhost:8000
```

## 3. Email Utilities (`email_utils.py`)
We create a dedicated file to handle email logic and define templates for the email bodies.
```python
async def send_email(to_email: str, subject: str, plain_text: str, html_content: str | None = None) -> None:
    # Logic to connect to the SMTP server and send the email
    pass

async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    # Uses a template located in `templates/email/password_reset.html`
    pass
```

## 4. Secure Token Storage (`models.py` & `auth.py`)
When a user requests a password reset, we must generate a secure, temporary token and store it in the database to verify their request later.

* **Database Model (`models.py`):** We create a `PasswordResetToken` table that links to the `User` table.
```python
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # We store the HASH of the token, not the raw token, for security
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship(back_populates="reset_tokens")
```

* **Token Generation (`auth.py`):** We use Python's built-in `secrets` and `hashlib` libraries to generate URL-safe tokens and hash them.
```python
import secrets
import hashlib

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
```

## 5. Pydantic Schemas
We add three specific schemas to handle the different password workflows:
```python
class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
```

## 6. Endpoints & Background Tasks (`routers/users.py`)
We build three new endpoints: `forgot_password`, `reset_password`, and `change_password`.

* **Background Tasks:** Notice the use of FastAPI's `BackgroundTasks`. Sending an email takes time. By using a background task, the API instantly returns a `202 Accepted` response to the user, while the email sends silently in the background. This keeps the frontend feeling fast and responsive.
```python
from fastapi import BackgroundTasks

@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks, # Injected dependency
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # 1. Delete old tokens, generate a new one, save hash to DB.
    # 2. Add the email sending function to the background task queue.
    pass
```

## 7. Frontend Integration & Security Headers (`main.py`)
We update `main.py` to serve the HTML pages for `forgot_password.html` and `reset_password.html.`

* **The `Referrer-Policy` Header:** When serving the `reset_password` page, we explicitly set the `Referrer-Policy` header. The URL for this page contains the highly sensitive reset token (e.g., `?token=abc123xyz`). If a user clicks an external link from this page, their browser might send the token to that external website. Setting this header prevents the browser from leaking the token.
```python
@app.get("/reset-password", include_in_schema=False)
async def reset_password_page(request: Request):
    response = templates.TemplateResponse(
        request,
        "reset_password.html",
        {"title": "Reset Password"},
    )
    # Security: Prevents token leakage to external sites
    response.headers["Referrer-Policy"] = "no-referrer" 
    return response
```

## 8. Summary
Users can now click "Forgot your password?" on the login page. This triggers an API request that generates a secure token and emails them a link via Mailtrap. The user clicks the link, enters their new password, and the backend verifies the token before securely hashing and updating their database record!

(Remember: For a production environment, you will swap out Mailtrap for a real email provider like AWS SES, SendGrid, or Resend).