import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import SQLModel, create_engine, Session

from app.core.config import settings
from app.api.main import app
from app.domain.models import User, Lottery, Ballot
from app.api.dependencies import require_admin


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
    # override the require_admin dependency to allow all requests
    app.dependency_overrides[require_admin] = lambda: admin


def test_list_open_lotteries(open_lottery):
    response = client.get("/lotteries/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Lottery"
    assert data[0]["closure_date"] == open_lottery.closure_date.isoformat()


def test_create_lottery_success(require_admin_override):
    tomorrow_str = (date.today() + timedelta(days=1)).isoformat()
    response = client.post("/lotteries/", json={"closure_date": tomorrow_str, "name": "Test Lottery"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Lottery"
    assert data["closure_date"] == tomorrow_str


def test_create_lottery_duplicate(require_admin_override, open_lottery):
    payload = {"closure_date": open_lottery.closure_date.isoformat(), "name": "Duplicate Lottery"}
    response = client.post("/lotteries/", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.text


def test_get_lottery_by_date_found(open_lottery):
    response = client.get(f"/lotteries/{open_lottery.closure_date.isoformat()}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(open_lottery.id)


def test_get_lottery_by_date_not_found(session):
    response = client.get(f"/lotteries/2099-01-01")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text


def test_close_and_draw_winner_success(require_admin_override, open_lottery, ballot):

    response = client.post(f"/lotteries/close_and_draw/?lottery_date={open_lottery.closure_date.isoformat()}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(open_lottery.id)
    assert data["is_closed"] == True
    assert data["winning_ballot_id"] == str(ballot.id)


def test_close_and_draw_winner_no_ballots(require_admin_override, open_lottery):

    response = client.post(f"/lotteries/close_and_draw/?lottery_date={open_lottery.closure_date.isoformat()}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(open_lottery.id)
    assert data["is_closed"] == True
    assert data["winning_ballot_id"] == None


def test_close_and_draw_winner_already_closed(require_admin_override, closed_lottery):

    response = client.post(f"/lotteries/close_and_draw/?lottery_date={closed_lottery.closure_date.isoformat()}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already closed" in response.text


def test_get_winning_ballot_success(open_lottery, user, ballot):

    client.post(f"/lotteries/close_and_draw/?lottery_date={open_lottery.closure_date.isoformat()}")
    response = client.get(f"/lotteries/{open_lottery.closure_date.isoformat()}/winner")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(ballot.id)
    assert data["user"]["id"] == str(user.id)
    assert data["lottery"]["id"] == str(open_lottery.id)


def test_get_winning_ballot_no_winner(closed_lottery):

    response = client.get(f"/lotteries/{closed_lottery.closure_date.isoformat()}/winner")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "no winner" in response.text


def test_get_winning_ballot_lottery_not_closed(open_lottery):

    response = client.get(f"/lotteries/{open_lottery.closure_date.isoformat()}/winner")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not closed" in response.text.lower()
