from typing import Optional
from fastapi import FastAPI, Header
from src.books.schemas import User
from src.books.routes import book_router
from contextlib import asynccontextmanager

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
    description="A REST API for a book review web service",
    version= version,
    lifespan=lifespan
)


app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])