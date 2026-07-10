from datetime import datetime, timedelta
import logging
import uuid

import bcrypt
from fastapi import HTTPException, status
import jwt

from src.config import Config
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

"""
    Did not follow the same approach as in the tutorial as passlib library is not under active maintenance
"""


def hash_password(password: str) -> str:
    # Convert string to bytes
    password_bytes = password.encode("utf-8")

    # Generate a salt and hash the password
    salt = bcrypt.gensalt()

    # Decode back to a UTF-8 string to safely save in our database
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, stored_hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), stored_hashed.encode("utf-8"))


def create_access_token(
    user_data: dict,
    expiry: timedelta = None,
    refresh: bool = False,  # pyright: ignore[reportArgumentType]
) -> str:
    payload = {
        "user": user_data,
        "exp": datetime.now()
        + (
            expiry
            if expiry is not None
            else timedelta(seconds=Config.ACCESS_TOKEN_EXPIRY_SECONDS)
        ),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict | None:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )

        return token_data
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None
    except Exception as e:
        logging.exception(e)
        return None


"""
    Note - Using PyJWTError is a very effective way of catching all exceptions that arise from PyJWT,
    since it is the base class from which they are built.
"""


serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-configuration"
)


def create_url_safe_token(data: dict):
    """Serialize a dict into a URLSafe Token"""
    token = serializer.dumps(data)

    return token


def decode_url_safe_token(token: str, max_age=300) -> dict | None:
    """Deserialize a URLSafe token to get data"""

    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except SignatureExpired:
        raise HTTPException(
            detail="Token has expired", status_code=status.HTTP_400_BAD_REQUEST
        )
        # If the token is expired, it raises a SignatureExpired exception
    except BadSignature:
        raise HTTPException(detail="Invalid Token", status_code=status.HTTP_400_BAD_REQUEST)
        # If the token is invalid for any other reason, it raises a BadSignature exception
