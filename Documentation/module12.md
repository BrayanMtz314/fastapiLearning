# Module 12: File Uploads - Image Processing, Validation, and Storage

In this module, we add the ability for users to upload and manage their own profile pictures. This introduces handling non-text data (files) in our API.

## 1. Installing Pillow (Image Processing)
To handle image manipulation safely, we use the standard Python imaging library, **Pillow**. It allows us to open, resize, compress, and change the format of uploaded images before saving them to the server.
```bash
uv add pillow
```

## 2. Configuration & Utilities
Before touching the API endpoints, we set up the rules and logic for how images should be handled.

* **Configuration (`config.py`):** We added a new setting to define the maximum allowed file size (in MB). This prevents users from uploading massive files that could crash the server or fill up storage.

* **Utility Functions (`image_utils.py`):** We created a dedicated file to hold our image logic. This file contains helper functions like `process_profile_image()` (for resizing and saving) and `delete_profile_image()` (to clean up old files from the server).

## 3. Router Updates (`routers/users.py`)
Handling file uploads requires specific FastAPI tools, as files are sent using `multipart/form-data` rather than standard JSON.

* **Required Imports:**
```python
from fastapi import UploadFile
from PIL import UnidentifiedImageError
from starlette.concurrency import run_in_threadpool
from image_utils import delete_profile_image, process_profile_image
```

* **Dedicated Upload Endpoint:** We created a brand new endpoint exclusively for handling image uploads.

    * Best Practice: It is always better to separate file uploads from standard text data updates. Mixing JSON bodies and file uploads in a single request can be unnecessarily complex to manage.

* **Delete Image Endpoint:** We also added a `delete_user_picture()` endpoint that uses our utility function to remove the file from the server and reset the user's database record to the default profile picture.

## 4. Frontend Integration (account.html)
While our API endpoints can now be tested via Swagger UI (`/docs`), our application users need a graphical interface to manage their pictures.

* We updated the `account.html` template.

* We added the necessary HTML form elements (like `<input type="file">`) and JavaScript logic to capture the selected image, send it to our new upload endpoint, and dynamically update the profile picture on the page without requiring a hard refresh.


# Return to Readme.md
[**Readme.md**](../README.md)