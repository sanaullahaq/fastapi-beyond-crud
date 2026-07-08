from typing import Any, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from starlette.requests import Request

from src.auth.utils import decode_token
from src.db.main import get_session
from src.db.models import User
from src.db.redish import token_in_blocklist

from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.errors import (
    AccessTokenRequired,
    InsufficientPermission,
    InvalidToken,
    NotAuthenticated,
    RefreshTokenRequired,
)

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=False):
        super().__init__(auto_error=auto_error)

    """
    __call__() is to turn your instances into callable objects,

    """

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        if creds is None:
            raise NotAuthenticated()

        token_data = decode_token(creds.credentials)

        if not token_data:
            raise InvalidToken()

        if await token_in_blocklist(token_data["jti"]):
            raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data  # pyright: ignore[reportReturnType]

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
) -> User | None:
    user_email = token_details["user"]["email"]

    user = await user_service.get_user_by_email(email=user_email, session=session)

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True
        else:
            raise InsufficientPermission()
