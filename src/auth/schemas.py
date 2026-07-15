from typing import Annotated, List
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, model_validator

from src.books.schemas import BookOut
from src.reviews.schemas import ReviewOut


PasswordStr = Annotated[str, Field(min_length=6)]


class UserOut(BaseModel):
    model_config = {"from_attributes": True}
    """
    This will help us to build schema from from a SQLAlchemy/ORM instance.
    Though FastAPI does this by default (when we returns only a SQLAlchemy/ORM instance),
    But we need to explicitly declare this here as our "/signup" end points which returns `UserCreateResponse` schema and there is nested `UserOut` schema


    By default, Pydantic v2 models expect to be built from a dict — e.g. UserOut(**some_dict). But new_user in your endpoint is a SQLAlchemy ORM object (an instance of your User model), not a dict. Its data lives in attributes (new_user.uid, new_user.email, etc.), not dict keys.
    from_attributes = True tells Pydantic: "when validating input, also try reading it off object attributes, not just dict keys." This is the direct v2 replacement for the old v1 class Config: orm_mode = True.
    """

    uid: uuid.UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserCreateResponse(BaseModel):
    message: str
    user: UserOut


class UserCreate(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: EmailStr = Field(max_length=40)
    password: PasswordStr

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Sanaulla",
                "last_name": "Haq",
                "username": "sanau",
                "email": "sanaullahaq1997@gmail.com",
                "password": "123456",
            }
        }
    }


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "sanaullahaq1997@gmail.com",
                "password": "123456",
            }
        }
    }


class UserBooksOut(UserOut):
    books: List[BookOut]
    reviews: List[ReviewOut]


class EmailAddresses(BaseModel):
    addresses: List[EmailStr]


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    new_password: PasswordStr
    confirm_new_password: PasswordStr

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
