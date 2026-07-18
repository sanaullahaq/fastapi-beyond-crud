import uuid
import pytest
from src.books.schemas import BookCreate
from src.books.service import BookService
from src.reviews.service import ReviewService
from src.reviews.schemas import ReviewCreate


class TestReviewRoutes:
    @pytest.mark.asyncio
    async def test_get_all_reviews_as_admin(self, client, session, admin_headers, test_user):
        service = ReviewService()
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Admin Review Book",
                author="Author",
                publisher="Pub",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=test_user.uid,
            session=session,
        )
        await service.add_review_to_book(
            user_email=test_user.email,
            book_uid=str(book.uid),
            review_data=ReviewCreate(rating=4, review_text="Good book"),
            session=session,
        )
        resp = await client.get("/api/v1/reviews/", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_all_reviews_as_user(self, client, auth_headers):
        resp = await client.get("/api/v1/reviews/", headers=auth_headers)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_review_found(self, client, session, auth_headers, test_user):
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Review Book",
                author="Author",
                publisher="Pub",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=test_user.uid,
            session=session,
        )
        service = ReviewService()
        review = await service.add_review_to_book(
            user_email=test_user.email,
            book_uid=str(book.uid),
            review_data=ReviewCreate(rating=5, review_text="Excellent"),
            session=session,
        )
        resp = await client.get(f"/api/v1/reviews/{review.uid}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["review_text"] == "Excellent"
        assert data["rating"] == 5

    @pytest.mark.asyncio
    async def test_get_review_not_found(self, client, auth_headers):
        resp = await client.get(f"/api/v1/reviews/{uuid.uuid4()}", headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_add_review_to_book(self, client, session, auth_headers, test_user):
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Add Review Book",
                author="Author",
                publisher="Pub",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=test_user.uid,
            session=session,
        )
        resp = await client.post(
            f"/api/v1/reviews/book/{book.uid}",
            json={"rating": 3, "review_text": "Decent"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["rating"] == 3
        assert data["review_text"] == "Decent"

    @pytest.mark.asyncio
    async def test_delete_own_review(self, client, session, auth_headers, verified_user):
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Delete Review Book",
                author="Author",
                publisher="Pub",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=verified_user.uid,
            session=session,
        )
        service = ReviewService()
        review = await service.add_review_to_book(
            user_email=verified_user.email,
            book_uid=str(book.uid),
            review_data=ReviewCreate(rating=2, review_text="Meh"),
            session=session,
        )
        resp = await client.delete(
            f"/api/v1/reviews/{review.uid}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_other_users_review(self, client, session, auth_headers, test_user):
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Other Review Book",
                author="Author",
                publisher="Pub",
                page_count=100,
                language="English",
                published_date="2024-01-01",
            ),
            user_uid=test_user.uid,
            session=session,
        )
        service = ReviewService()
        review = await service.add_review_to_book(
            user_email=test_user.email,
            book_uid=str(book.uid),
            review_data=ReviewCreate(rating=1, review_text="Bad"),
            session=session,
        )
        resp = await client.delete(
            f"/api/v1/reviews/{review.uid}",
            headers=auth_headers,
        )
        assert resp.status_code == 401
