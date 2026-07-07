from datetime import date, datetime
from typing import List, Optional
from sqlmodel import Relationship, SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid


class User(SQLModel, table=True):
    __tablename__: str = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            nullable=False,
            default=uuid.uuid4,
            info={"description": "Unique identifier for the user account"},
        )
    )

    username: str
    first_name: str = Field(nullable=True)
    last_name: str = Field(nullable=True)
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    """
    `default` : `Python-side default`
    `server_default`: `Database Server Side default`

    `default` evaluates dynamic values via Python code on the application side before sending the query.
    `server_default` hardcodes values directly into the database schema definition (DDL) via an SQL DEFAULT constraint.
    """
    is_verified: bool = False
    email: str
    password_hash: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    # "user" = Book's attribute name
    """
    The change defines a relationship attribute `books` for a `User` model, which is a list of `Book` objects.
    The Relationship function establishes a two-way connection between the `User` and `Book` models, with `back_populates="user"` 
    indicating that each `Book` instance is linked back to the `User` instance that added it.

    The `sa_relationship_kwargs={"lazy": "selectin"}` parameter optimizes the query performance by loading related Book objects in a single 
    query when the `User` object is accessed, reducing the number of database queries and improving efficiency.
    """

    """
    This tells SQLAlchemy/SQLModel: "When I access book.user, give me the User this book belongs to. And when I access user.books, give me all Book instances that point back to this user."

    Without back_populates, the two relationships would be independent and unaware of each other, potentially creating sync issues.

    sa_relationship_kwargs={}
    Passes extra keyword arguments directly to SQLAlchemy's underlying relationship() function. Common settings:

    Kwarg	                            Meaning
    {"lazy": "selectin"}	            Load related objects in a single extra SELECT query (usually best for performance)
    {"lazy": "joined"}	                Load via JOIN in the same query (can be heavy)
    {"lazy": "subquery"}	            Load via a subquery
    {"cascade": "all, delete-orphan"}	Delete children when parent is deleted
    {"order_by": Review.created_at}	    Control ordering of the related list
    
    So sa_relationship_kwargs={"lazy": "selectin"} means: "When I access user.books, issue one SELECT ... WHERE user_uid = ? query for all books at once" — avoiding N+1 queries.
    """

    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    # "user" = Reviews's attribute name

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class BookTag(SQLModel, table=True):
    book_uid: uuid.UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_uid: uuid.UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__: str = "tags"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        link_model=BookTag,
        back_populates="tags",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    """
    It specifies `link_model=BookTag`, indicating that the association between Tag and Book instances is managed through the BookTag class.
    """

    def __repr__(self):
        return f"Tag <{self.name}>"


class Book(SQLModel, table=True):
    """All SQLModel models are pydantic tables and therefore can be used for data validation."""

    __tablename__: str = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    )

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str

    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional[User] = Relationship(back_populates="books")
    # "books" = User's attribute name
    """
    In the Book model, we have defined a relationship attribute `user`, which optionally refers to a User object. The `Relationship` 
    function establishes a connection where each `Book` instance can be associated with a single `User` instance, specified by `back_populates="books"`.
    This bidirectional relationship means that for every Book, there is a corresponding User who owns or is associated with that book.
    """

    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )
    # "book" = Review's attribute name

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    tags: List[Tag] = Relationship(
        link_model=BookTag,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"<Book {self.title}>"


class Review(SQLModel, table=True):
    __tablename__: str = "reviews"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    )
    rating: int = Field(le=5)
    review_text: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional[User] = Relationship(
        back_populates="reviews", sa_relationship_kwargs={"lazy": "selectin"}
    )
    # "reviews" = User's attribute name
    book: Optional[Book] = Relationship(
        back_populates="reviews", sa_relationship_kwargs={"lazy": "selectin"}
    )
    # "reviews" = Book's attribute name

    def __repr__(self) -> str:
        return f"Review for book {self.book_uid} by user {self.user_uid}"
