import pytest
from src.auth.service import UserService
from src.auth.schemas import UserCreate
from src.auth.utils import verify_password


class TestAuthService:
    @pytest.mark.asyncio
    async def test_create_user(self, session):
        service = UserService()
        user_data = UserCreate(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            email="john@example.com",
            password="secret123",
        )
        user = await service.create_user(user_data=user_data, session=session)
        assert user.email == "john@example.com"
        assert user.first_name == "John"
        assert verify_password("secret123", user.password_hash)

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, session, test_user):
        service = UserService()
        user = await service.get_user_by_email(
            email=test_user.email, session=session
        )
        assert user is not None
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, session):
        service = UserService()
        user = await service.get_user_by_email(
            email="nonexistent@example.com", session=session
        )
        assert user is None

    @pytest.mark.asyncio
    async def test_user_exists_true(self, session, test_user):
        service = UserService()
        exists = await service.user_exists(
            email=test_user.email, session=session
        )
        assert exists is True

    @pytest.mark.asyncio
    async def test_user_exists_false(self, session):
        service = UserService()
        exists = await service.user_exists(
            email="nonexistent@example.com", session=session
        )
        assert exists is False

    @pytest.mark.asyncio
    async def test_update_user(self, session, test_user):
        service = UserService()
        updated = await service.update_user(
            test_user, {"first_name": "Updated"}, session
        )
        assert updated.first_name == "Updated"
        fetched = await service.get_user_by_email(
            email=test_user.email, session=session
        )
        assert fetched.first_name == "Updated"
