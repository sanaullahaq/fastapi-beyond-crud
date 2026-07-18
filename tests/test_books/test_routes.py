import uuid
import pytest

from src.books.schemas import BookCreate
from src.books.service import BookService


class TestBookRoutes:
    book_create_payload = {
        "title": "Integration Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "page_count": 300,
        "language": "English",
        "published_date": "2024-03-15",
    }

    @pytest.mark.asyncio
    async def test_create_book_unauthenticated(self, client):
        resp = await client.post("/api/v1/books/", json=self.book_create_payload)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_create_book_success(self, client, session, auth_headers):
        resp = await client.post(
            "/api/v1/books/",
            json=self.book_create_payload,
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Integration Test Book"
        assert data["author"] == "Test Author"
        assert "uid" in data
        assert "tags" in data

    @pytest.mark.asyncio
    async def test_get_all_books(self, client, session, auth_headers, test_user):
        service = BookService()
        for i in range(2):
            await service.create_book(
                book_data=BookCreate(
                    title=f"List Book {i}",
                    author="Author",
                    publisher="Publisher",
                    page_count=100,
                    language="English",
                    published_date="2024-01-01",
                ),
                user_uid=test_user.uid,
                session=session,
            )
        resp = await client.get("/api/v1/books/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_book_by_uid(self, client, session, auth_headers, test_user):
        service = BookService()
        book = await service.create_book(
            book_data=BookCreate(
                title="Specific Book",
                author="Author",
                publisher="Publisher",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=test_user.uid,
            session=session,
        )
        resp = await client.get(
            f"/api/v1/books/{book.uid}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Specific Book"
        assert "reviews" in data

    @pytest.mark.asyncio
    async def test_get_book_not_found(self, client, auth_headers):
        resp = await client.get(
            f"/api/v1/books/{uuid.uuid4()}",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_book(self, client, session, auth_headers, test_user):
        service = BookService()
        book = await service.create_book(
            book_data=BookCreate(
                title="Before Update",
                author="Author",
                publisher="Publisher",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=test_user.uid,
            session=session,
        )
        resp = await client.patch(
            f"/api/v1/books/{book.uid}",
            json={"title": "After Update", "page_count": 999},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "After Update"
        assert data["page_count"] == 999

    @pytest.mark.asyncio
    async def test_update_book_not_found(self, client, auth_headers):
        resp = await client.patch(
            f"/api/v1/books/{uuid.uuid4()}",
            json={"title": "Nope"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_book(self, client, session, auth_headers, test_user):
        service = BookService()
        book = await service.create_book(
            book_data=BookCreate(
                title="To Be Deleted",
                author="Author",
                publisher="Publisher",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=test_user.uid,
            session=session,
        )
        resp = await client.delete(
            f"/api/v1/books/{book.uid}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

        gone = await service.get_book(
            book_uid=str(book.uid),
            session=session,
        )
        assert gone is None

    @pytest.mark.asyncio
    async def test_delete_book_not_found(self, client, auth_headers):
        resp = await client.delete(
            f"/api/v1/books/{uuid.uuid4()}",
            headers=auth_headers,
        )
        assert resp.status_code == 404
