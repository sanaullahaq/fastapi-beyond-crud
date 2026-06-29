from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from src.auth.models import User
from datetime import datetime


class AuthService:
    """
    This class provides methods to create, read, update, and delete books
    """
    pass