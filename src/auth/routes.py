from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from src.auth.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
)
from src.auth.schemas import UserBooksOut, UserLogin, UserOut, UserCreate
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.auth.utils import create_access_token, verify_password
from src.config import Config
from src.db.main import get_session
from src.db.models import User
from src.db.redish import add_jti_to_blocklist
from src.errors import InvalidCredentials, InvalidToken, UserAlreadyExists


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserOut
)
async def create_user_account(
    user_data: UserCreate, session: AsyncSession = Depends(get_session)
) -> User:
    email = user_data.email

    user_exists = await user_service.user_exists(email=email, session=session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data=user_data, session=session)

    return new_user


@auth_router.post("/login")
async def login_users(
    login_data: UserLogin, session: AsyncSession = Depends(get_session)
) -> JSONResponse:
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email=email, session=session)

    if user is not None:
        password_valid = verify_password(
            password=password, stored_hashed=user.password_hash
        )

        if password_valid:
            access_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)}
            )

            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=Config.REFRESH_TOKEN_EXPIRY_DAYS),
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"user": user.email, "uid": str(user.uid)},
                }
            )
        raise InvalidCredentials()
    raise InvalidCredentials()


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken()


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out successfully"}, status_code=status.HTTP_200_OK
    )


"""
----------------------------------------------------------------------------------------------------------------------------------
|Pattern                 | Where                 | How                                                                           |
----------------------------------------------------------------------------------------------------------------------------------
|Module-level instance   | books/routes.py:12    | access_token_bearer = AccessTokenBearer() then Depends(access_token_bearer)   |
|Inline instance         | auth/routes.py:82     | Depends(RefreshTokenBearer())                                                 |
|Inline instance         | auth/routes.py:96     | Depends(AccessTokenBearer())                                                  |
----------------------------------------------------------------------------------------------------------------------------------
Both work identically. Depends() just needs a callable object — it doesn't care whether you created it once at module load or create it fresh inline. The inline version is shorter but creates a new instance each time the module is imported (not per-request — Python evaluates the default argument once at definition time).
The two files are just inconsistent with each other. Books uses a named module-level variable, auth uses an inline anonymous instance. Same end result.
"""


@auth_router.get("/me", response_model=UserBooksOut)
# @auth_router.get("/me", response_model=UserOut)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user
