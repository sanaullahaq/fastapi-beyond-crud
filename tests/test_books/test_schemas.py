import uuid
from datetime import date, datetime
import pytest
from pydantic import ValidationError

from src.books.schemas import BookBase, BookCreate, BookUpdate, BookOut, BookDetailOut
from src.db.models import Review


class TestBookBase:
    def test_valid_input(self):
        data = BookBase(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            page_count=200,
            language="English",
        )
        assert data.title == "Test Book"
        assert data.author == "Test Author"

    def test_missing_title(self):
        with pytest.raises(ValidationError):
            BookBase(
                author="Test Author",
                publisher="Test Publisher",
                page_count=200,
                language="English",
            )

    def test_missing_author(self):
        with pytest.raises(ValidationError):
            BookBase(
                title="Test Book",
                publisher="Test Publisher",
                page_count=200,
                language="English",
            )


class TestBookCreate:
    def test_valid_input(self):
        data = BookCreate(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            page_count=200,
            language="English",
            published_date="2024-01-15",
        )
        assert data.published_date == "2024-01-15"

    def test_default_published_date(self):
        data = BookCreate(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            page_count=200,
            language="English",
        )
        assert data.published_date == "YYYY-MM-DD"

    def test_missing_title_raises_error(self):
        with pytest.raises(ValidationError):
            BookCreate(
                author="Test Author",
                publisher="Test Publisher",
                page_count=200,
                language="English",
            )


class TestBookUpdate:
    def test_all_fields_optional(self):
        data = BookUpdate()
        assert data.model_dump(exclude_none=True) == {}

    def test_partial_update(self):
        data = BookUpdate(title="Updated Title")
        assert data.title == "Updated Title"
        assert data.author is None
        assert data.publisher is None

    def test_update_multiple_fields(self):
        data = BookUpdate(title="New Title", page_count=300)
        assert data.title == "New Title"
        assert data.page_count == 300
        assert data.author is None


class TestBookOut:
    def test_valid_input(self):
        data = BookOut(
            uid=uuid.uuid4(),
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            page_count=200,
            language="English",
            published_date=date(2024, 1, 15),
            tags=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert isinstance(data.uid, uuid.UUID)
        assert data.published_date == date(2024, 1, 15)

    def test_rejects_invalid_uid(self):
        with pytest.raises(ValidationError):
            BookOut(
                uid="not-a-uuid",
                title="Test Book",
                author="Test Author",
                publisher="Test Publisher",
                page_count=200,
                language="English",
                published_date=date(2024, 1, 15),
                tags=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )


class TestBookDetailOut:
    def test_valid_input(self):
        data = BookDetailOut(
            uid=uuid.uuid4(),
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            page_count=200,
            language="English",
            published_date=date(2024, 1, 15),
            tags=[],
            reviews=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert data.reviews == []

    def test_with_reviews(self):
        mock_review = Review(
            uid=uuid.uuid4(),
            rating=4,
            review_text="Great book",
        )
        data = BookDetailOut(
            uid=uuid.uuid4(),
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            page_count=200,
            language="English",
            published_date=date(2024, 1, 15),
            tags=[],
            reviews=[mock_review],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert len(data.reviews) == 1
        assert data.reviews[0].rating == 4
