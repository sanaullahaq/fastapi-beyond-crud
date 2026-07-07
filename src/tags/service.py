from fastapi import status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import desc, select
from src.books.service import BookService
from src.db.models import Tag
from src.tags.schemas import TagAdd


book_service = BookService()

server_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong"
)


class TagService:
    async def get_tags(self, session: AsyncSession):
        statement = select(Tag).order_by(desc(Tag.created_at))

        result = await session.exec(statement)

        return result.all()

    async def add_tags_to_book(
        self, book_uid: str, tag_data: TagAdd, session: AsyncSession
    ):
        book = await book_service.get_book(book_uid=book_uid, session=session)

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        for tag_item in tag_data.tags:
            result = await session.exec(select(Tag).where(Tag.name == tag_item.name))
            tag = result.one_or_none()

            if not tag:
                tag = Tag(name=tag_item.name)

            book.tags.append(tag)

        session.add(book)

        await session.commit()

        await session.refresh(book)

        return book
