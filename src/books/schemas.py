from datetime import date, datetime
from typing import List
import uuid

from pydantic import BaseModel

from src.db.models import Review, Tag


class BookBase(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str


class BookCreate(BookBase):
    """
    This class is used to validate the request when creating a book
    """

    published_date: str


class BookUpdate(BookBase):
    """
    This class is used to validate the request when updating a book
    """

    pass


class BookOut(BookBase):
    uid: uuid.UUID
    published_date: date
    tags: List[Tag]
    created_at: datetime
    updated_at: datetime


class BookDetailOut(BookOut):
    reviews: List[Review]
    tags: List[Tag]