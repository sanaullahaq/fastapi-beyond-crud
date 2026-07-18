import uuid
from datetime import datetime
import pytest
from pydantic import ValidationError
from src.reviews.schemas import ReviewBase, ReviewCreate, ReviewOut


class TestReviewBase:
    def test_valid_input(self):
        data = ReviewBase(rating=5, review_text="Great!")
        assert data.rating == 5
        assert data.review_text == "Great!"

    def test_rating_above_max(self):
        with pytest.raises(ValidationError):
            ReviewBase(rating=6, review_text="Too high")

    def test_rating_at_min(self):
        data = ReviewBase(rating=0, review_text="Bad")
        assert data.rating == 0

    def test_missing_rating(self):
        with pytest.raises(ValidationError):
            ReviewBase(review_text="No rating")


class TestReviewCreate:
    def test_valid_input(self):
        data = ReviewCreate(rating=3, review_text="Okay")
        assert data.rating == 3


class TestReviewOut:
    def test_valid_input(self):
        data = ReviewOut(
            uid=uuid.uuid4(),
            rating=4,
            review_text="Nice",
            user_uid=uuid.uuid4(),
            book_uid=uuid.uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert data.rating == 4
        assert isinstance(data.uid, uuid.UUID)
