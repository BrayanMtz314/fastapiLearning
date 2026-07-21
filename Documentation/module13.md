# Module 13: Pagination - Loading More Data with Query Parameters

When an application scales, returning all records from a database in a single request becomes a major bottleneck. If an endpoint tries to pull thousands of rows at once, it can consume massive server memory, slow down network transit, and potentially crash the user's browser. To solve this, we implement **Pagination**.

Pagination divides our dataset into small, manageable chunks, returning only a specific subset of records per request and letting the client request more as needed.

## 1. Populating the Database
To test pagination effectively, you need a substantial amount of data. We initialized this process by running a mock data generator script called `populate_db.py` to seed our SQLite database with dozens of sample posts.

## 2. Defining the Pagination Structure (Schemas)
When returning paginated data, the API needs to provide metadata alongside the actual records so the frontend knows how to build navigation or "Load More" controls.

```python
from pydantic import BaseModel
from schemas import PostResponse

class PaginatedPostsResponse(BaseModel):
    # The slice of data for the current page
    posts: list[PostResponse] 
    # Total number of records matching the query in the DB 
    total: int      
    # How many records were skipped (offset)           
    skip: int         
    # Max number of records requested per page         
    limit: int          
    # Flag telling the frontend if there are more pages left       
    has_more: bool             
```

## 3. Implementing the Paginated Endpoint (`routers/posts.py`)
To handle pagination dynamically, we use FastAPI's `Query` parameters. We calculate the total count first, and then use SQLAlchemy's `.offset()` and `.limit()` modifiers to slice our database query.

* **Required Imports:** `from fastapi import Query` and `from sqlalchemy import func`
```python
@router.get("", response_model=PaginatedPostsResponse)
async def get_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    # Best practice: Pull the default page size limit from our global settings
    limit: Annotated[int, Query(ge=1, le=100)] = settings.posts_per_page
):
    # 1. Get total number of posts in the database
    count_result = await db.execute(select(func.count()).select_from(models.Post))
    total = count_result.scalar() or 0

    # 2. Fetch the specific slice of posts using offset (skip) and limit
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
        .offset(skip)
        .limit(limit)
    ) 
    posts = result.scalars().all()

    # 3. Determine if there are more records beyond this current page
    has_more = skip + len(posts) < total
    
    return PaginatedPostsResponse(
        posts=[PostResponse.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )
```

## 4. Frontend Integration: Dynamic Loading
To support asynchronous data injection on the frontend, we need to adapt our templates and JavaScript to read from our new paginated endpoint.

### A. New Utilities (`static/js/utils.js`)
Because our JavaScript will now render raw text received from the API directly into the DOM, we must protect against Cross-Site Scripting (XSS) vulnerabilities. We also need a helper to format date strings cleanly.
```js
// XSS prevention: Converts user input strings safely so they don't execute as HTML
export function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Date formatting utility to mirror the server's backend strftime structure
export function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "2-digit",
  });
}
```

### B. "Load More" Interface (`home.html` & `user_posts.html`)
Instead of classic page numbers (1, 2, 3), we implement an infinite scroll or "Load More" interaction pattern. We add a button conditional on the `has_more` property provided by the backend:
```html
{% if has_more %}
    <div class="text-center mb-4">
      <button type="button" class="btn btn-outline-primary" id="loadMoreBtn">Load More Posts</button>
    </div>
{% endif %}
```

### C. JavaScript Event Handling
We write a `<script>` module block in `home.html` that listens for clicks on `#loadMoreBtn`. Every time the button is clicked, the script increments the `skip` pointer by the `limit` size, fetches the next chunk of JSON data from our API, formats it via `utils.js`, and dynamically appends the new posts to the bottom of the page container.

## 5. Summary & Production Note
Offset-based pagination follows a simple mathematical footprint:

* `limit` defines how many rows to fetch.

* `skip` defines where to begin fetching.

>**Production Tip:** Building pagination manually is a fantastic exercise to understand how databases evaluate query slicing under the hood. However, in enterprise environments, it is generally better practice to leverage specialized open-source libraries (like `fastapi-pagination`). These pre-packaged tools save time and offer out-of-the-box support for advanced pagination patterns, such as cursor-based pagination.


# Return to Readme.md
[**Readme.md**](../README.md)