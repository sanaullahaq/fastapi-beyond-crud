from datetime import date, datetime
import uuid

from pydantic import BaseModel


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
    created_at: datetime
    updated_at: datetime
