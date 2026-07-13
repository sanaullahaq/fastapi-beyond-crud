import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.schemas import BookCreate, BookUpdate
from sqlmodel import select, desc
from src.db.models import Book
from datetime import datetime


class BookService:
    """
    This class provides methods to create, read, update, and delete books
    """

    async def get_all_books(self, session: AsyncSession):
        """
        Get a list of all books

        Returns:
            list: list of books
        """

        statement = select(Book).order_by(desc(Book.created_at))

        result = await session.exec(statement)

        return result.all()

    async def get_users_books(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)

        return result.all()

    async def create_book(
        self, book_data: BookCreate, user_uid: uuid.UUID, session: AsyncSession
    ):
        """
        Create a new book

        Args:
            book_data (BookCreateModel): data to create a new

        Returns:
            Book: the new book
        """

        book_data_dict = book_data.model_dump()

        new_book = Book(**book_data_dict)

        new_book.published_date = datetime.strptime(
            book_data_dict["published_date"], "%Y-%m-%d"
        )
        new_book.user_uid = user_uid

        session.add(new_book)

        await session.commit()

        return new_book

    async def get_book(self, book_uid: str, session: AsyncSession):
        """
        Get a book by its UUID.

        Args:
            book_uid(str): the UUID of the book

        Returns:
            Book: the book object
        """

        try:
            book_uid_obj = uuid.UUID(str(book_uid))
        except ValueError:
            return None

        statement = select(Book).where(Book.uid == book_uid_obj)

        result = await session.exec(statement)

        book = result.first()

        return book if book is not None else None

    async def update_book(
        self, book_uid: str, update_data: BookUpdate, session: AsyncSession
    ):
        """
        Update a book

        Args:
            book_uid (str): the UUID of the book
            update_data (BookCreateModel): the data to update the book

        Returns:
            Book: the updated book
        """

        book_to_update = await self.get_book(book_uid=book_uid, session=session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump(exclude_none=True)        # as there are optional fields with None as default

            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()

            return book_to_update
        else:
            return None

    async def delete_book(self, book_uid: str, session: AsyncSession):
        """Delete a book

        Args:
            book_uid (str): the UUID of the book
        """
        book_to_delete = await self.get_book(book_uid=book_uid, session=session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)

            await session.commit()

            return {}
        else:
            return None
