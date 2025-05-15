import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import SQLModel, create_engine, Session

from app.core.config import settings
from app.api.main import app
from app.domain.models import User, Lottery, Ballot
from app.api.dependencies import require_admin, get_current_user

client = TestClient(app)

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


@pytest.fixture
def open_lottery(session):
    l = Lottery(name="Test Lottery", closure_date=date.today() + timedelta(days=1), is_closed=False)
    session.add(l)
    session.commit()
    session.refresh(l)
    return l


@pytest.fixture
def closed_lottery(session):
    l = Lottery(name="Closed Lottery", closure_date=date.today() - timedelta(days=1), is_closed=True)
    session.add(l)
    session.commit()
    session.refresh(l)
    return l


@pytest.fixture
def ballot(session, user, open_lottery):
    b = Ballot(user_id=user.id, lottery_id=open_lottery.id)
    session.add(b)
    session.commit()
    session.refresh(b)
    return b


@pytest.fixture
def require_admin_override(admin):
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[require_admin] = lambda: admin


@pytest.fixture
def get_current_user_override(user):
    app.dependency_overrides[get_current_user] = lambda: user


def test_submit_ballot_success(get_current_user_override, user, open_lottery):

    response = client.post(f"/ballots/?lottery_date={open_lottery.closure_date.isoformat()}")
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user_id"] ==str(user.id)
    assert data["lottery_id"] == str(open_lottery.id)


def test_submit_ballot_to_closed_lottery(get_current_user_override, closed_lottery):

    response = client.post(f"/ballots/?lottery_date={closed_lottery.closure_date.isoformat()}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "closed lottery" in response.text


def test_submit_ballot_as_admin_forbidden(require_admin_override, open_lottery):

    response = client.post(f"/ballots/?lottery_date={open_lottery.closure_date.isoformat()}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Admins cannot submit ballots" in response.text


def test_submit_ballot_lottery_not_found(get_current_user_override):

    invalid_date = "2099-01-01"
    response = client.post(f"/ballots/?lottery_date={invalid_date}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()


def test_view_my_ballots(get_current_user_override, ballot):

    response = client.get("/ballots/mine")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(ballot.id)
    assert data[0]["user_id"] == str(ballot.user_id)
    assert data[0]["lottery_id"] == str(ballot.lottery_id)


def test_view_my_ballots_empty(get_current_user_override):
    response = client.get("/ballots/mine")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def list_ballots_by_lottery_success(require_admin_override, open_lottery, ballot):

    response = client.get(f"/ballots/lottery/{open_lottery.closure_date.isoformat()}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(ballot.id)
    assert data[0]["user_id"] == str(ballot.user_id)
    assert data[0]["lottery_id"] == str(open_lottery.id)


def list_ballots_by_lottery_empty(require_admin_override, open_lottery):

    response = client.get(f"/ballots/lottery/{open_lottery.closure_date.isoformat()}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == []


def list_ballots_by_lottery_not_found(require_admin_override):

    invalid_date = "2099-01-01"
    response = client.get(f"/ballots/lottery/{invalid_date}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()
