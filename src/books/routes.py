from typing import List
from fastapi import APIRouter, Depends, status
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.books.schemas import BookDetailOut, BookOut, BookCreate, BookUpdate
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session
from src.db.models import Book
from src.errors import BookNotFound


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
role_checker = Depends(RoleChecker(["admin", "user"]))


@book_router.get("/", response_model=List[BookOut], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session=session)
    return books


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BookOut,
    dependencies=[role_checker],
)
async def create_a_book(
    book_data: BookCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> Book:
    user_uid = token_details["user"]["user_uid"]
    new_book = await book_service.create_book(
        book_data=book_data, user_uid=user_uid, session=session
    )
    return new_book


@book_router.get(
    "/{book_uid}", response_model=BookDetailOut, dependencies=[role_checker]
)
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> Book:
    book = await book_service.get_book(book_uid=book_uid, session=session)

    if book:
        return book
    else:
        raise BookNotFound()


@book_router.patch("/{book_uid}", response_model=BookOut, dependencies=[role_checker])
async def update_book(
    book_uid: str,
    book_update_data: BookUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> Book:
    updated_book = await book_service.update_book(
        book_uid=book_uid, update_data=book_update_data, session=session
    )

    if updated_book:
        return updated_book
    else:
        raise BookNotFound()


@book_router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    book_to_delete = await book_service.delete_book(book_uid=book_uid, session=session)

    if book_to_delete == {}:
        return {}
    else:
        raise BookNotFound()
