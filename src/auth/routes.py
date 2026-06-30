from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.schemas import UserModel, UserCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.db.main import get_session


auth_router = APIRouter()
user_service = UserService()


@auth_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserModel
)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
) -> dict:
    email = user_data.email

    user_exists = await user_service.user_exists(email=email, session=session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with email already exists",
        )

    new_user = await user_service.create_user(user_data=user_data, session=session)

    return new_user
