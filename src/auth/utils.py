from datetime import datetime, timedelta
import logging
import uuid

import bcrypt
import jwt

from src.config import Config


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
    user_data: dict, expiry: timedelta = None, refresh: bool = False # pyright: ignore[reportArgumentType]
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
