import pytest
from pydantic import ValidationError
from src.auth.schemas import UserCreate, UserLogin, PasswordResetConfirm, PasswordResetRequest, EmailAddresses


class TestUserCreate:
    def test_valid_input(self):
        data = UserCreate(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            email="john@example.com",
            password="secret123",
        )
        assert data.email == "john@example.com"

    def test_short_password(self):
        with pytest.raises(ValidationError):
            UserCreate(
                first_name="John",
                last_name="Doe",
                username="johndoe",
                email="john@example.com",
                password="12345",
            )

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(
                first_name="John",
                last_name="Doe",
                username="johndoe",
                email="not-an-email",
                password="secret123",
            )


class TestUserLogin:
    def test_valid_input(self):
        data = UserLogin(email="john@example.com", password="secret123")
        assert data.email == "john@example.com"


class TestPasswordResetConfirm:
    def test_matching_passwords(self):
        data = PasswordResetConfirm(
            new_password="newpass123",
            confirm_new_password="newpass123",
        )
        assert data.new_password == "newpass123"

    def test_non_matching_passwords(self):
        with pytest.raises(ValidationError):
            PasswordResetConfirm(
                new_password="newpass123",
                confirm_new_password="different",
            )


class TestEmailAddresses:
    def test_valid_input(self):
        data = EmailAddresses(addresses=["a@b.com", "c@d.com"])
        assert len(data.addresses) == 2

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            EmailAddresses(addresses=["not-an-email"])


class TestPasswordResetRequest:
    def test_valid_email(self):
        data = PasswordResetRequest(email="john@example.com")
        assert data.email == "john@example.com"
