import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import SQLModel, create_engine, Session

from app.core.config import settings
from app.api.main import app


client = TestClient(app)

engine = create_engine(settings.DATABASE_URL)

@pytest.fixture(scope="function")
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


def test_register_user_success(session):
    payload = {"username": "testuser", "email": "test@example.com", "password": "strongpassword"}

    response = client.post("/user/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_register_user_already_exists(session):
    payload = {"username": "existing", "email": "existing@example.com", "password": "strongpassword"}

    # Register once
    client.post("/user/register", json=payload)
    # Try registering again
    response = client.post("/user/register", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.text


def test_login_success(session):
    payload = {"username": "loginuser", "email": "login@example.com", "password": "strongpassword"}

    # Register first
    client.post("/user/register", json=payload)

    # Login with correct credentials
    response = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "strongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(session):
    payload = {"username": "wrongpassuser", "email": "wrongpass@example.com", "password": "strongpassword"}

    # Register first
    client.post("/user/register", json=payload)

    # Attempt login with wrong password
    response = client.post(
        "/auth/login",
        data={"username": "wrongpass@example.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid" in response.text


def test_login_user_not_found(session):
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "nopassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text
