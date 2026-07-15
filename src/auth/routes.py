from src.middleware import limiter
from fastapi import BackgroundTasks, Request
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from src.celery_tasks import send_email
from src.auth.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
)
from src.auth.schemas import (
    EmailAddresses,
    PasswordResetConfirm,
    PasswordResetRequest,
    UserBooksOut,
    UserCreateResponse,
    UserLogin,
    UserCreate,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.auth.utils import (
    create_access_token,
    create_url_safe_token,
    decode_url_safe_token,
    hash_password,
    verify_password,
)
from src.config import Config
from src.db.main import get_session
from src.db.redish import add_jti_to_blocklist
from src.errors import InvalidCredentials, InvalidToken, UserAlreadyExists, UserNotFound


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserCreateResponse
)
@limiter.limit("5/hour")  # 5 request per hour per IP, Prevent account creation spam
async def create_user_account(
    user_data: UserCreate,
    bg_tasks: BackgroundTasks,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> UserCreateResponse:
    email = user_data.email

    user_exists = await user_service.user_exists(email=email, session=session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data=user_data, session=session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    emails = [email]
    subject = "Verify your email"
    html = f"""
                    <h1>Verify your Email</h1>
                    <p>Please click this <a href="{link}">link</a> to verify your email</p>
                """
    # message = create_mail_message(
    #     recipients=emails, subject=subject, body=html
    # )

    # await mail.send_message(message=message)
    # bg_tasks.add_task(mail.send_message, message)       # Now mail will be sent in the background
    send_email.delay(emails, subject, html)  # celery in action

    return UserCreateResponse(
        message="Account Created!, Check email to verify your account",
        user=new_user,
    )


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token=token)
    if token_data:
        email = token_data.get("email")

        if email:
            user = await user_service.get_user_by_email(email=email, session=session)

            if not user:
                raise UserNotFound()

            await user_service.update_user(user, {"is_verified": True}, session)

            return JSONResponse(
                content={"message": "Account verified successfully"},
                status_code=status.HTTP_200_OK,
            )
    return JSONResponse(
        content={"message": "Error occurred during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.post("/login")
@limiter.limit("10/minute")  # 10 request per minute per IP, Brute-force protection
async def login_users(
    login_data: UserLogin,
    request: Request,
    session: AsyncSession = Depends(get_session),
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


@auth_router.post("/send_mail")
@limiter.limit("5/hour")  # 5 request per hour per IP, Email abuse prevention
async def send_mail(emails: EmailAddresses, request: Request):
    emails = emails.addresses

    subject = "Welcome to our app"
    html = "<h1>Welcome to the app</h1>"

    # message = create_mail_message(recipients=emails, subject=subject, body=html)
    # await mail.send_message(message)
    send_email.delay(emails, subject, html)  # celery in action

    return {"message": "Email sent successfully"}


@auth_router.post(
    "/password-reset-request",
)
@limiter.limit("3/hour")  # 3 requests per hour per IP, Prevent email flooding
async def password_reset_request(
    email_data: PasswordResetRequest,
    request: Request,  # The request: Request parameter is required by slowapi to extract the client IP — it doesn't affect existing logic.
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    email = email_data.email

    user_exists = await user_service.user_exists(email=email, session=session)

    if user_exists:
        # raise UserAlreadyExists()

        token = create_url_safe_token({"email": email})

        link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

        emails = [email]
        subject = "Reset Your Password"
        html = f"""
                        <h1>Reset Your Password</h1>
                        <p>Please click this <a href="{link}">link</a> to reset your password</p>
                    """
        # message = create_mail_message(
        #     recipients=[email], subject=subject, body=html
        # )

        # await mail.send_message(message=message)

        send_email.delay(emails, subject, html)  # celery in action

    return JSONResponse(
        content={
            "message": "If an account with that email exists, a password reset link has been sent.",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirm,
    session: AsyncSession = Depends(get_session),
):
    # new_password = passwords.new_password
    # confirm_password = passwords.confirm_new_password

    # if new_password != confirm_password:
    #     raise HTTPException(
    #         detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
    #     )

    token_data = decode_url_safe_token(token=token)
    if token_data:
        email = token_data.get("email")

        if email:
            user = await user_service.get_user_by_email(email=email, session=session)

            if not user:
                raise UserNotFound()

            password_hash = hash_password(passwords.new_password)

            await user_service.update_user(
                user, {"password_hash": password_hash}, session
            )

            return JSONResponse(
                content={"message": "Password reset successfully"},
                status_code=status.HTTP_200_OK,
            )
    return JSONResponse(
        content={"message": "Error occurred during password reset"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
