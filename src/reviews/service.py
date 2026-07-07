import logging
import uuid
from fastapi import HTTPException, status
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review
from src.reviews.schemas import ReviewCreate


books_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreate,
        session: AsyncSession,
    ):
        try:
            user = await user_service.get_user_by_email(
                email=user_email, session=session
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict)

            book = await books_service.get_book(book_uid=book_uid, session=session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
                )

            new_review.user = user
            """
            SQLAlchemy sees the relationship assignment, extracts user.uid, and sets user_uid behind the scenes during commit()
            """

            new_review.book = book

            session.add(new_review)

            await session.commit()

            return new_review

        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                detail="Oops...something went wrong!",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def get_review(self, review_uid: str, session: AsyncSession):
        try:
            review_uid_obj = uuid.UUID(str(review_uid))
        except ValueError:
            return None
        
        statement = select(Review).where(Review.uid == review_uid_obj)
        
        result = await session.exec(statement)
        
        review = result.first()

        return review if review is not None else None

    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))
        result = await session.exec(statement)
        return result.all()

    async def delete_review_to_from_book(
        self, review_uid: str, user_email: str, session: AsyncSession
    ):
        user = await user_service.get_user_by_email(email=user_email, session=session)

        review = await self.get_review(review_uid, session)

        if not review or review.user != user:
            return None

        await session.delete(review)

        await session.commit()

        return {}
