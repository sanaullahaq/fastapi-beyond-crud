from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.dependencies import AccessTokenBearer
from src.books.schemas import BookOut, BookCreate, BookUpdate
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session
from src.db.models import Book


book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
"""
FastAPI resolves the dependency at request time:
FastAPI sees that access_token_bearer is a callable instance (it has __call__ inherited from TokenBearer/HTTPBearer). So FastAPI calls:
access_token_bearer.__call__(request)
...behind the scenes, passing the incoming Request object. This is FastAPI's DI framework doing the work.
In short: Depends(access_token_bearer) tells FastAPI "use this callable object as the dependency", and FastAPI invokes __call__ on it automatically when a request hits the route.
"""


@book_router.get("/", response_model=List[BookOut])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: str = Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session=session)
    return books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookOut)
async def create_a_book(
    book_data: BookCreate,
    session: AsyncSession = Depends(get_session),
    token_details: str = Depends(access_token_bearer),
) -> Book:
    new_book = await book_service.create_book(book_data=book_data, session=session)
    return new_book


@book_router.get("/{book_uid}", response_model=BookOut)
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: str = Depends(access_token_bearer),
) -> Book:
    book = await book_service.get_book(book_uid=book_uid, session=session)

    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


@book_router.patch("/{book_uid}", response_model=BookOut)
async def update_book(
    book_uid: str,
    book_update_data: BookUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: str = Depends(access_token_bearer),
) -> Book:
    updated_book = await book_service.update_book(
        book_uid=book_uid, update_data=book_update_data, session=session
    )

    if updated_book:
        return updated_book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: str = Depends(access_token_bearer),
):
    book_to_delete = await book_service.delete_book(book_uid=book_uid, session=session)

    if book_to_delete == {}:
        return {}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
