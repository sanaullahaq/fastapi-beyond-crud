import uuid
import pytest
from src.reviews.service import ReviewService
from src.reviews.schemas import ReviewCreate
from src.books.service import BookService
from src.books.schemas import BookCreate


class TestReviewService:
    @pytest.mark.asyncio
    async def test_add_review_to_book(self, session, test_user):
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Review Target",
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
            review_data=ReviewCreate(rating=4, review_text="Good"),
            session=session,
        )
        assert review.rating == 4
        assert review.review_text == "Good"
        assert review.user_uid == test_user.uid
        assert review.book_uid == book.uid

    @pytest.mark.asyncio
    async def test_get_review_found(self, session, test_user):
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Find Review Book",
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
        created = await service.add_review_to_book(
            user_email=test_user.email,
            book_uid=str(book.uid),
            review_data=ReviewCreate(rating=3, review_text="Okay"),
            session=session,
        )
        found = await service.get_review(
            review_uid=str(created.uid), session=session
        )
        assert found is not None
        assert found.review_text == "Okay"

    @pytest.mark.asyncio
    async def test_get_review_not_found(self, session):
        service = ReviewService()
        result = await service.get_review(
            review_uid=str(uuid.uuid4()), session=session
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_get_review_invalid_uuid(self, session):
        service = ReviewService()
        result = await service.get_review(
            review_uid="not-a-uuid", session=session
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_reviews(self, session, test_user):
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Reviews Galore",
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
        await service.add_review_to_book(
            user_email=test_user.email,
            book_uid=str(book.uid),
            review_data=ReviewCreate(rating=5, review_text="Amazing"),
            session=session,
        )
        await service.add_review_to_book(
            user_email=test_user.email,
            book_uid=str(book.uid),
            review_data=ReviewCreate(rating=2, review_text="Not great"),
            session=session,
        )
        all_reviews = await service.get_all_reviews(session=session)
        assert len(all_reviews) >= 2

    @pytest.mark.asyncio
    async def test_delete_own_review(self, session, test_user):
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Delete Review",
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
        created = await service.add_review_to_book(
            user_email=test_user.email,
            book_uid=str(book.uid),
            review_data=ReviewCreate(rating=1, review_text="Terrible"),
            session=session,
        )
        result = await service.delete_review_to_from_book(
            review_uid=str(created.uid),
            user_email=test_user.email,
            session=session,
        )
        assert result == {}
        gone = await service.get_review(
            review_uid=str(created.uid), session=session
        )
        assert gone is None

    @pytest.mark.asyncio
    async def test_delete_other_users_review(self, session, test_user, verified_user):
        book_service = BookService()
        book = await book_service.create_book(
            book_data=BookCreate(
                title="Others Review",
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
        created = await service.add_review_to_book(
            user_email=test_user.email,
            book_uid=str(book.uid),
            review_data=ReviewCreate(rating=3, review_text="Decent"),
            session=session,
        )
        result = await service.delete_review_to_from_book(
            review_uid=str(created.uid),
            user_email=verified_user.email,
            session=session,
        )
        assert result is None
