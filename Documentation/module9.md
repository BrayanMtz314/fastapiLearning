# Module 9: Frontend Forms & JavaScript Integration

Until now, our website was read-only. In this module, we use HTML and JavaScript to build a dynamic web interface that allows users to Create, Update, and Delete posts directly from the browser.

## 1. Updating the Layout (Adding Buttons & Modals)
We begin by modifying `layout.html` to include a "New Post" button and Bootstrap Modals (pop-up windows) for the forms.

* **The Button:** Triggers the Create Post modal.
  ```html
  <button class="btn btn-outline-light mb-2 mb-md-0 me-md-2"
          type="button"
          data-bs-toggle="modal"
          data-bs-target="#createPostModal">New Post</button>
    ```

* The Modals: We added HTML blocks for three different modals in layout.html:

1. `#createPostModal` (The form to write a post)

2. `#successModal` (To show a success message)

3. `#errorModal` (To display API errors)

## 2. Intercepting Form Submissions (The JavaScript Approach)
If you look at the Create Post form HTML, you will notice it lacks standard `action` or `method`     attributes.

Why? We are intercepting the form submission using JavaScript. Instead of the browser reloading the page to submit the form, our JavaScript catches the submit event, packages the data into JSON, and sends it to our FastAPI endpoints via an asynchronous fetch request.

Note on Auth: Because we haven't built an authentication system yet, we temporarily hardcode the `user_id = 1` directly in the JavaScript to make the API accept the request.


## 3. JavaScript Utilities (`utils.js`)
To keep our code clean and avoid repeating ourselves, we created a utility file at `./static/js/utils.js` with three reusable functions:
```js
// Extracts readable error messages from FastAPI's Pydantic validation errors
export function getErrorMessage(error) {
  if (typeof error.detail === "string") {
    return error.detail;
  } else if (Array.isArray(error.detail)) {
    return error.detail.map((err) => err.msg).join(". ");
  }
  return "An error occurred. Please try again.";
}

// Uses Bootstrap's JS API to show a modal by its ID
export function showModal(modalId) {
  const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById(modalId));
  modal.show();
  return modal;
}

// Uses Bootstrap's JS API to hide a modal by its ID
export function hideModal(modalId) {
  const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
  if (modal) modal.hide();
}
```

We import these functions into `layout.html` inside a `<script type="module">` tag to handle the Create Post form logic.

## 4. Backend Update: Sorting Posts
Now that we can add posts, we notice they appear from oldest to newest at the bottom of the page. We want the newest posts at the top.

* **The Fix:** We update our SQLAlchemy queries in the router endpoints by adding `.order_by()`.

```python
# Notice the .order_by(models.Post.date_posted.desc()) at the end
result = await db.execute(
    select(models.Post)
    .options(selectinload(models.Post.author))
    .order_by(models.Post.date_posted.desc())
)
```

## 5. Editing and Deleting Posts (`post.html`)
To allow users to manage their existing content, we added Edit and Delete functionality to the individual post pages.

* **Temporary Authentication Check:** We only render the Edit/Delete buttons if the post belongs to our hardcoded user (user_id == 1).

```html
{% if post.user_id == 1 %}
    <div class="post-actions mt-3 pt-3 border-top">
        <button type="button" class="btn btn-outline-secondary me-1" data-bs-toggle="modal" data-bs-target="#editModal">Edit Post</button>
        <button type="button" class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteModal">Delete Post</button>
    </div>
{% endif %}
```

* **Modals & Scripts:** Just like in `layout.html`, we added the HTML for `#editModal` and `#deleteModal`, and included a `{% block scripts %}` section at the bottom to import our `utils.js` functions and handle the `PATCH` and `DELETE` requests to our API.


# Return to Readme.md
[**Readme.md**](../README.md)