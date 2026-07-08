from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import desc, select
from src.books.service import BookService
from src.db.models import Tag
from src.errors import BookNotFound, TagAlreadyExists, TagNotFound
from src.tags.schemas import TagAdd, TagCreate


book_service = BookService()


class TagService:
    async def get_tags(self, session: AsyncSession):
        statement = select(Tag).order_by(desc(Tag.created_at))

        result = await session.exec(statement)

        return result.all()

    async def add_tags_to_book(
        self, book_uid: str, tag_data: TagAdd, session: AsyncSession
    ):
        # ------------------------------------------------------------
        # 1. Validate that the book exists in the database.
        #    get_book() internally tries uuid.UUID(str(book_uid)) and
        #    returns None if parsing fails or no row is found.
        # ------------------------------------------------------------
        book = await book_service.get_book(book_uid=book_uid, session=session)

        if not book:
            raise BookNotFound()

        # ------------------------------------------------------------
        # 2. Process each tag from the request payload.
        #    tag_data.tags is a List[TagCreate] — each item has a .name.
        #    We use a "find-or-create" pattern so the same tag name
        #    can be shared across multiple books (many-to-many).
        # ------------------------------------------------------------
        for tag_item in tag_data.tags:
            # ------------------------------------------------------------
            # 2a. Look up an existing Tag by name.
            #     one_or_none() returns the Tag or None if not found.
            # ------------------------------------------------------------
            # result = await session.exec(select(Tag).where(Tag.name == tag_item.name))
            # tag = result.one_or_none()
            tag = await self.get_tag_by_name(tag_name=tag_item.name, session=session)

            # ------------------------------------------------------------
            # 2b. Create a new Tag if it doesn't already exist.
            #     This object is NOT yet tracked by the session — it will
            #     become tracked when it's appended to a tracked parent's
            #     relationship (cascade behavior), or when session.add()
            #     is called explicitly (line 53).
            # ------------------------------------------------------------
            if not tag:
                tag = Tag(name=tag_item.name)

            # ------------------------------------------------------------
            # 2c. Append the Tag to the book's relationship list.
            #     Book.tags is a many-to-many relationship with
            #     link_model=BookTag (the association table).
            #     SQLAlchemy tracks this append operation and will
            #     INSERT a row into the BookTag table on next flush.
            #
            #     Even if this tag was already linked to this book,
            #     appending it again would create a duplicate BookTag
            #     row. In practice this method is called once per set
            #     of tags, so duplicates don't occur here.
            # ------------------------------------------------------------
            book.tags.append(tag)

        # ------------------------------------------------------------
        # 3. Explicitly add the book to the session's identity map.
        #    book is already tracked (fetched via session on line 28),
        #    so this call is technically a no-op for book itself.
        #
        #    However, if any tag was newly created (line 42-43) and
        #    was NOT automatically cascaded, this ensures it's tracked.
        #    In SQLModel, cascade="save-update" is the default on
        #    many-to-many relationships, so even this is redundant.
        #    Keeping it here is defensive documentation.
        # ------------------------------------------------------------
        session.add(book)

        # ------------------------------------------------------------
        # 4. Flush all pending changes to the database and commit.
        #    - Any newly created Tag rows are INSERTed.
        #    - BookTag link rows are INSERTed for each (book_uid, tag_uid).
        #    - After commit, the session clears its "expire all" flag,
        #      meaning all loaded objects are marked as expired/stale.
        # ------------------------------------------------------------
        await session.commit()

        # ------------------------------------------------------------
        # 5. Refresh the book object from the database.
        #
        #    Why this is necessary:
        #      After commit(), SQLAlchemy expires all attributes of
        #      every object in the session. If anything downstream
        #      (e.g., FastAPI response serialization) accesses
        #      book.tags, it would trigger a lazy load. In an async
        #      session, lazy loads raise MissingGreenlet because
        #      there's no greenlet context to run the query in.
        #
        #    What refresh() does:
        #      It re-queries the DB for the book's current row AND
        #      eagerly re-populates all relationship collections
        #      (including book.tags) using the configured loader
        #      strategy (lazy="selectin"). The returned book now
        #      has fully loaded, non-expired data.
        #
        #    Without refresh():
        #      Accessing book.tags in the route handler or during
        #      response serialization would raise MissingGreenlet.
        # ------------------------------------------------------------
        await session.refresh(book)

        # ------------------------------------------------------------
        # 6. Return the book with its tags eagerly loaded.
        #    FastAPI serializes this into the response_model schema.
        #    Since book.tags is already loaded, no lazy load occurs
        #    during serialization.
        # ------------------------------------------------------------
        return book

    async def get_tag_by_name(self, tag_name: str, session: AsyncSession):
        result = await session.exec(select(Tag).where(Tag.name == tag_name))
        tag = result.one_or_none()
        return tag

    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession):
        statement = select(Tag).where(Tag.uid == tag_uid)
        result = await session.exec(statement)
        return result.first()

    async def add_tag(self, tag_data: TagCreate, session: AsyncSession):
        tag = await self.get_tag_by_name(tag_name=tag_data.name, session=session)
        if tag is not None:
            raise TagAlreadyExists()

        new_tag = Tag(name=tag_data.name)

        session.add(new_tag)

        await session.commit()

        return new_tag

    async def update_tag(
        self, tag_uid: str, tag_update_data: TagCreate, session: AsyncSession
    ):
        tag = await self.get_tag_by_uid(tag_uid=tag_uid, session=session)

        if tag is not None:
            tag_update_data_dict = tag_update_data.model_dump()
            for k, v in tag_update_data_dict.items():
                setattr(tag, k, v)

            await session.commit()

            await session.refresh(tag)

            return tag
        else:
            raise TagNotFound()

    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid, session)

        if not tag:
            raise TagNotFound()

        await session.delete(tag)

        await session.commit()
