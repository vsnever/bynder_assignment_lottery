import pytest
import uuid
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from app.domain.services import UserService
from app.domain.models import User
from app.schemas.user import UserCreate
from app.domain.exceptions import (
    UserAlreadyExists,
    UserInvalidCredentials,
    UserNotFound,
)

engine = create_engine(settings.DATABASE_URL)

@pytest.fixture(scope="function")
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def user_service(session):
    return UserService(session)


def test_register_user_success(user_service):
    user_data = UserCreate(username="user", email="user@example.com", password="Password123^")
    user = user_service.register_user(user_data)

    assert user.email == user_data.email
    assert user.username == user_data.username
    assert user.hashed_password != user_data.password


def test_register_user_already_exists(user_service):
    user_data = UserCreate(username="user", email="user@example.com", password="Password123^")
    user_service.register_user(user_data)

    with pytest.raises(UserAlreadyExists):
        user_service.register_user(user_data)


def test_authenticate_user_success(user_service):
    user_data = UserCreate(username="user", email="user@example.com", password="Password123^")
    user_service.register_user(user_data)

    user = user_service.authenticate_user(user_data.email, user_data.password)
    assert user.email == user_data.email


def test_authenticate_user_invalid_password(user_service):
    user_data = UserCreate(username="user", email="user@example.com", password="Password123^")
    user_service.register_user(user_data)

    with pytest.raises(UserInvalidCredentials):
        user_service.authenticate_user(user_data.email, "wrongpass")


def test_authenticate_user_not_found(user_service):
    with pytest.raises(UserNotFound):
        user_service.authenticate_user("nonexistent@example.com", "password")


def test_get_user_success(user_service):
    user_data = UserCreate(username="user", email="user@example.com", password="Password123^")
    created_user = user_service.register_user(user_data)

    retrieved_user = user_service.get_user(created_user.id)
    assert retrieved_user.id == created_user.id


def test_get_user_not_found(user_service):
    with pytest.raises(UserNotFound):
        user_service.get_user(uuid.uuid4())


def test_get_user_by_email_success(user_service):
    user_data = UserCreate(username="user", email="user@example.com", password="Password123^")
    created_user = user_service.register_user(user_data)

    retrieved_user = user_service.get_user_by_email(user_data.email)
    assert retrieved_user.id == created_user.id


def test_get_user_by_email_not_found(user_service):
    with pytest.raises(UserNotFound):
        user_service.get_user_by_email("nonexistent@example.com")
