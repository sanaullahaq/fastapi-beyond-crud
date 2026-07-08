from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker, get_current_user
from src.db.main import get_session
from src.db.models import User
from src.errors import InsufficientPermission, ReviewNotFound
from src.reviews.schemas import ReviewCreate
from src.reviews.service import ReviewService

review_router = APIRouter()

review_service = ReviewService()

admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@review_router.get("/", dependencies=[admin_role_checker])
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    reviews = await review_service.get_all_reviews(session=session)
    return reviews


@review_router.get("/{review_uid}", dependencies=[user_role_checker])
async def get_review(review_uid: str, session: AsyncSession = Depends(get_session)):
    review = await review_service.get_review(review_uid=review_uid, session=session)
    
    if review:
        return review
    else:
        raise ReviewNotFound()


@review_router.post("/book/{book_uid}", dependencies=[user_role_checker])
async def add_review_to_books(
    book_uid: str,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    email = current_user.email
    new_review = await review_service.add_review_to_book(
        book_uid=book_uid, review_data=review_data, session=session, user_email=email
    )
    return new_review


@review_router.delete(
    "/{review_uid}",
    dependencies=[user_role_checker],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_uid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    email = current_user.email
    review_to_delete = await review_service.delete_review_to_from_book(
        review_uid=review_uid, user_email=email, session=session
    )

    if review_to_delete == {}:
        return {}
    else:
        raise InsufficientPermission()
