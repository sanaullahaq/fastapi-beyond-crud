from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from starlette.requests import Request

from src.auth.utils import decode_token
from src.db.redish import token_in_blocklist




class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)
    
    """
    __call__() is to turn your instances into callable objects,

    """
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        if creds is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authenticated"
            )

        token_data = decode_token(creds.credentials)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired",
                    "resolution": "Please get new token",
                },
            )

        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or has been revoked",
                    "resolution": "Please get new token",
                },
            )

        self.verify_token_data(token_data)

        return token_data # pyright: ignore[reportReturnType]

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token",
            )
