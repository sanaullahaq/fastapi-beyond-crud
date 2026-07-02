from datetime import date, datetime
from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid


class User(SQLModel, table=True):
    __tablename__: str = "user_accounts"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
            info={"description": "Unique identifier for the user account"},
        )
    )

    username: str
    first_name: str = Field(nullable=True)
    last_name: str = Field(nullable=True)
    is_verified: bool = False
    email: str
    password_hash: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Book(SQLModel, table=True):
    """All SQLModel models are pydantic tables and therefore can be used for data validation."""
    
    __tablename__ = "books"
    
    uid: uuid.UUID = Field(
        sa_column = Column(
            pg.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4
        )
    )

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f"<Book {self.title}>"