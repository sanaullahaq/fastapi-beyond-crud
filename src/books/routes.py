from typing import List
from fastapi import APIRouter, HTTPException, status

from src.books.book_data import books
from src.books.schemas import Book, BookUpdate


version='v1'

book_router = APIRouter(
    prefix='/api/{version}',
    tags=['books']
)


@book_router.get('/books', response_model=List[Book])
async def get_all_books():
    return books


@book_router.post('/books', status_code=status.HTTP_201_CREATED)
async def create_a_book(book_data: Book)->dict:
    books.append(book_data.model_dump())
    return books[-1]


@book_router.get('/books/{book_id}')
async def get_book(book_id: int)->dict:
    for book in books:
        if book['id'] == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.patch('/books/{book_id}')
async def update_book(book_id: int, book_update_data: BookUpdate)->dict:
    for book in books:
        if book['id'] == book_id:
            # book['title'] = book_update_data.title
            # book['author'] = book_update_data.author
            # book['publisher'] = book_update_data.publisher
            # book['page_count'] = book_update_data.page_count
            # book['language'] = book_update_data.language
            for k, v in book_update_data.model_dump().items():
                book[k] = v
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.delete('/books/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book['id'] == book_id:
            books.remove(book)
            return {}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")