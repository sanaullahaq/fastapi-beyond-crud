from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router

from src.db.main import initdb


#the lifespan event
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

version_prefix =f"/api/{version}"


app = FastAPI(
    title="Bookly",
    description=description,
    version= version,
    # lifespan=lifespan     # Commented this, because we shall be using Alembic to make changes to our database,
)


app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])
app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"{version_prefix}/review", tags=["review"])