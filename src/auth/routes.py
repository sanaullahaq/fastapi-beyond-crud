from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.books.schemas import Book, BookCreateModel, BookUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import AuthService
from src.db.main import get_session


auth_router = APIRouter()
auth_service = AuthService()