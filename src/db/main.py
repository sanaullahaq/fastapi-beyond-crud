# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator
from sqlmodel import SQLModel

from src.config import Config


async_engine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=True,
    # connect_args={"ssl": "require"}
)


# Note - conn.run_sync() is an asynchronous function that we utilize to run synchronous functions such as SQLModel.metadata.create_all().
async def initdb():
    """create a connection to our db"""
    """create our database models in the database"""

    async with async_engine.begin() as conn:
        # statement = text("SELECT 'Hello World'")
        # result = await conn.execute(statement)
        # print(result.all())
        await conn.run_sync(SQLModel.metadata.create_all)


async_session = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
