from typing import Annotated, List
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

from src.books.schemas import BookOut
from src.reviews.schemas import ReviewOut


PasswordStr = Annotated[str, Field(min_length=6)]


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
    password : PasswordStr

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


class EmailAddresses(BaseModel):
    addresses: List[str]


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    new_password : PasswordStr
    confirm_new_password : PasswordStr

    @model_validator(mode="after")
    def password_match(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("Passwords do not match!")
        return self
    """
    mode="after": Runs after all individual fields have already been validated and the model instance is built.

    The method receives self (the model instance), not raw data.
    You access fields normally via self.field_name.
    You must return self at the end.
    Good for: cross-field checks (like password matching), since you need both fields already validated and coerced to their final types.


    mode="before"
    Runs before field validation — you get the raw, unvalidated input (usually a dict).
    python@model_validator(mode="before")
    @classmethod
    def check_raw_data(cls, data):
        # data is raw input, e.g. {"new_password": "abc", "confirm_new_password": "abc"}
        if isinstance(data, dict) and data.get("new_password") != data.get("confirm_new_password"):
            raise ValueError("Passwords do not match")
        return data
    """
