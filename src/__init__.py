from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.books.routes import book_router
from src.auth.routes import auth_router
from src.middleware import register_cors_middleware, register_custom_logging_middleware
from src.reviews.routes import review_router
from src.tags.routes import tags_router

from src.db.main import initdb
from src.errors import register_all_errors
from fastapi.openapi.docs import get_redoc_html


# the lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting...")
    await initdb()
    yield
    print("Server is stopping...")


version = "v1"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
    """

version_prefix = f"/api/{version}"


app = FastAPI(
    title="Bookly",
    description=description,
    version=version,
    # lifespan=lifespan     # Commented this, because we shall be using Alembic to make changes to our database,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Sanaulla Haq",
        "url": "https://github.com/sanaullahaq",
        "email": "sanaullahaq01@gmail.com",
    },
    terms_of_service="https://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",  # 127.0.0.1:8000/api/v1/docs
    # redoc_url=f"{version_prefix}/redoc",
    redoc_url=None,
)
"""
    If you want to disable the openapi_url, docs_url, or redoc_url, simply set their values to None.
"""

"""
There is an issue with default /redoc_url, so we set it to `None` and followed the below approach
"""

@app.get(f"{version_prefix}/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.2.0/bundles/redoc.standalone.js",
    )


register_all_errors(app)
register_custom_logging_middleware(app)  # Custom Logging through middleware
register_cors_middleware(app)


app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])
app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"{version_prefix}/reviews", tags=["reviews"])
app.include_router(tags_router, prefix=f"{version_prefix}/tags", tags=["tags"])
