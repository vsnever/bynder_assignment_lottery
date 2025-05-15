import pytest
from uuid import uuid4
from sqlmodel import create_engine, SQLModel, Session
from jose import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token
from app.domain.models import User
from app.domain.services import UserService
from app.api.dependencies import get_current_user, require_admin


# Create real engine
engine = create_engine(settings.DATABASE_URL)

@pytest.fixture(scope="function")
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    u = User(username="testuser", email="testuser@example.com", hashed_password="hashed")
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


@pytest.fixture
def admin(session):
    u = User(username="testadmin", email="testadmin@example.com", hashed_password="hashed")
    u.is_admin = True
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def test_get_current_user_valid(session, user):

    token = create_access_token(str(user.id))
    service = UserService(session)

    result = get_current_user(token=token, service=service)
    assert result.id == user.id
    assert result.email == user.email


def test_get_current_user_invalid_token(session):
    invalid_token = "invalid.token.here"
    service = UserService(session)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=invalid_token, service=service)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_missing_sub(session):
    bad_token = jwt.encode({}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    service = UserService(session)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=bad_token, service=service)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_user_not_found(session):
    token = create_access_token(str(uuid4()))
    service = UserService(session)

    with pytest.raises(HTTPException) as exc:
        get_current_user(token=token, service=service)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_require_admin_valid_admin(session, admin):

    result = require_admin(current_user=admin)
    assert result.is_admin


def test_require_admin_forbidden(session, user):

    with pytest.raises(HTTPException) as exc:
        require_admin(current_user=user)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Admin access required" in str(exc.value.detail)
