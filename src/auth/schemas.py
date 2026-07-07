from typing import List
import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from src.books.schemas import BookOut
from src.reviews.schemas import ReviewOut


class UserOut(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Sana",
                "last_name": "U",
                "username": "sanau",
                "email": "sanau@xyz.com",
                "password": "123456",
            }
        }
    }


class UserLogin(BaseModel):
    email: str
    password: str

    model_config = {
    "json_schema_extra": {
        "example": {
            "email": "sanau@xyz.com",
            "password": "123456",
        }
    }
}


class UserBooksOut(UserOut):
    books: List[BookOut]
    reviews: List[ReviewOut]
