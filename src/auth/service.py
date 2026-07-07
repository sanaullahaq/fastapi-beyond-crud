from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.schemas import UserCreate
from sqlmodel import select
from src.db.models import User

from src.auth.utils import hash_password


class UserService:
    """
    This class provides methods to create, read, update, and delete books
    """

    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        user = result.first()

        return user

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email=email, session=session)

        return True if user is not None else False

    async def create_user(
        self, user_data: UserCreate, session: AsyncSession
    ) -> User:
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)
        new_user.password_hash = hash_password(user_data_dict["password"])

        session.add(new_user)

        await session.commit()

        return new_user
