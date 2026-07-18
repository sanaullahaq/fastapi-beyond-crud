import uuid
from datetime import datetime
import pytest
from pydantic import ValidationError
from src.tags.schemas import TagOut, TagCreate, TagAdd


class TestTagOut:
    def test_valid_input(self):
        data = TagOut(
            uid=uuid.uuid4(),
            name="fiction",
            created_at=datetime.now(),
        )
        assert data.name == "fiction"
        assert isinstance(data.uid, uuid.UUID)

    def test_invalid_uid(self):
        with pytest.raises(ValidationError):
            TagOut(
                uid="not-a-uuid",
                name="fiction",
                created_at=datetime.now(),
            )


class TestTagCreate:
    def test_valid_input(self):
        data = TagCreate(name="fiction")
        assert data.name == "fiction"

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            TagCreate()


class TestTagAdd:
    def test_valid_input(self):
        data = TagAdd(tags=[TagCreate(name="fiction"), TagCreate(name="non-fiction")])
        assert len(data.tags) == 2
        assert data.tags[0].name == "fiction"
