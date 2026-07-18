import uuid
import pytest
from sqlmodel import select

from src.books.service import BookService
from src.books.schemas import BookCreate, BookUpdate
from src.db.models import Book, User
from src.auth.utils import hash_password


class TestBookService:
    @pytest.mark.asyncio
    async def test_create_book(self, session, test_user):
        service = BookService()
        book_data = BookCreate(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            page_count=200,
            language="English",
            published_date="2024-01-15",
        )
        book = await service.create_book(
            book_data=book_data,
            user_uid=test_user.uid,
            session=session,
        )
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.user_uid == test_user.uid
        assert isinstance(book.uid, uuid.UUID)

    @pytest.mark.asyncio
    async def test_get_book_by_uid(self, session, test_user):
        service = BookService()
        book_data = BookCreate(
            title="Findable Book",
            author="Author",
            publisher="Publisher",
            page_count=100,
            language="English",
            published_date="2024-06-01",
        )
        created = await service.create_book(
            book_data=book_data,
            user_uid=test_user.uid,
            session=session,
        )
        found = await service.get_book(
            book_uid=str(created.uid),
            session=session,
        )
        assert found is not None
        assert found.title == "Findable Book"

    @pytest.mark.asyncio
    async def test_get_book_not_found(self, session):
        service = BookService()
        result = await service.get_book(
            book_uid=str(uuid.uuid4()),
            session=session,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_get_book_invalid_uuid(self, session):
        service = BookService()
        result = await service.get_book(
            book_uid="not-a-uuid",
            session=session,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_books(self, session, test_user):
        service = BookService()
        for i in range(3):
            await service.create_book(
                book_data=BookCreate(
                    title=f"Book {i}",
                    author="Author",
                    publisher="Publisher",
                    page_count=100,
                    language="English",
                    published_date="2024-01-01",
                ),
                user_uid=test_user.uid,
                session=session,
            )
        books = await service.get_all_books(session=session)
        assert len(books) == 3

    @pytest.mark.asyncio
    async def test_get_users_books(self, session, test_user):
        service = BookService()
        other_user = User(
            username="other",
            email="other@example.com",
            first_name="Other",
            last_name="User",
            role="user",
            is_verified=False,
            password_hash=hash_password("testpass123"),
        )
        session.add(other_user)
        await session.flush()
        for i in range(2):
            await service.create_book(
                book_data=BookCreate(
                    title=f"My Book {i}",
                    author="Author",
                    publisher="Publisher",
                    page_count=100,
                    language="English",
                    published_date="2024-01-01",
                ),
                user_uid=test_user.uid,
                session=session,
            )
        await service.create_book(
            book_data=BookCreate(
                title="Other Users Book",
                author="Author",
                publisher="Publisher",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=other_user.uid,
            session=session,
        )
        user_books = await service.get_users_books(
            user_uid=str(test_user.uid),
            session=session,
        )
        assert len(user_books) == 2

    @pytest.mark.asyncio
    async def test_update_book(self, session, test_user):
        service = BookService()
        book = await service.create_book(
            book_data=BookCreate(
                title="Original Title",
                author="Author",
                publisher="Publisher",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=test_user.uid,
            session=session,
        )
        updated = await service.update_book(
            book_uid=str(book.uid),
            update_data=BookUpdate(title="Updated Title", page_count=250),
            session=session,
        )
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.page_count == 250
        assert updated.author == "Author"

    @pytest.mark.asyncio
    async def test_update_book_not_found(self, session):
        service = BookService()
        result = await service.update_book(
            book_uid=str(uuid.uuid4()),
            update_data=BookUpdate(title="Nope"),
            session=session,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_book(self, session, test_user):
        service = BookService()
        book = await service.create_book(
            book_data=BookCreate(
                title="Delete Me",
                author="Author",
                publisher="Publisher",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=test_user.uid,
            session=session,
        )
        result = await service.delete_book(
            book_uid=str(book.uid),
            session=session,
        )
        assert result == {}
        gone = await service.get_book(
            book_uid=str(book.uid),
            session=session,
        )
        assert gone is None

    @pytest.mark.asyncio
    async def test_delete_book_not_found(self, session):
        service = BookService()
        result = await service.delete_book(
            book_uid=str(uuid.uuid4()),
            session=session,
        )
        assert result is None
