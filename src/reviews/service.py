import uuid

from sqlalchemy.exc import IntegrityError
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review
from src.errors import BookNotFound, ReviewAlreadyExists, UserNotFound
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
        user = await user_service.get_user_by_email(email=user_email, session=session)
        if not user:
            raise UserNotFound()

        book = await books_service.get_book(book_uid=book_uid, session=session)
        if not book:
            raise BookNotFound()

        """
        If I can check is there any duplicate review by that user for that same book with logic:
            ```
            for review in book.reviews:
                if review.user_uid == user.uid:
                    raise ReviewAlreadyExists()
            ```
            Then why should I execute a db query?
            
        ***Answer:***
             — Fair pushback — 
                for the sequential single-user case, your loop does the job, and in this codebase it's even "free": book.reviews is already loaded into memory by lazy="selectin" (set on Review.book),
                so the loop costs no extra DB round-trip. The query is not required for correctness here. 

            Where the two actually differ:
                1. Neither one is race-proof. Two simultaneous requests can both pass either check and both insert, because there's no unique constraint in the DB. The loop has exactly the same race as the query.
                If you want a real guarantee, the only thing that provides it is a DB unique constraint on (user_uid, book_uid) — everything else is a fast-path UX check.

                2. Efficiency at scale. The loop scans all of a book's reviews in Python to find the one matching row; a targeted select returns 0-or-1 row using an index.
                Trivial at 10 reviews, meaningful at 1,000. The query also isn't tied to the relationship's lazy strategy — if someone later changes lazy to "lazy" (or "raise"),
                the loop silently breaks (MissingGreenlet / N+1) while the query keeps working.

                3. Intent. select(...).where(book_uid=…, user_uid=…) reads as "is there a review belonging to this user for this book" without needing to know the book's review-loading strategy.
            
            So the honest breakdown:
            - Loop: fine today, slightly fragile (depends on lazy="selectin"), O(all reviews of the book).
            - Query: independent of load strategy, O(1) row, works the same either way.
            - Both same race; only a DB unique constraint fixes that.
        """
        existing = await session.exec(
            select(Review).where(
                Review.book_uid == book.uid, Review.user_uid == user.uid
            )
        )
        if existing.first():
            raise ReviewAlreadyExists()

        review_data_dict = review_data.model_dump()
        new_review = Review(**review_data_dict)
        new_review.user = user  # SQLAlchemy sees the relationship assignment, extracts user.uid, and sets user_uid behind the scenes during commit()
        new_review.book = book

        session.add(new_review)


        """
        As we know, two simultaneous requests can both pass either if-statement check and both insert. But the unique constraints will be able to catch this and will throw `IntegrityError`
        """
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ReviewAlreadyExists()

        await session.refresh(new_review)
        return new_review

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
