import pytest
from uuid import uuid4
from datetime import date, timedelta
from sqlmodel import SQLModel, create_engine, Session

from app.domain.models import User, Lottery, Ballot
from app.core.config import settings
from app.domain.services import BallotService
from app.domain.exceptions import BallotNotFound, LotteryAlreadyClosed

engine = create_engine(settings.DATABASE_URL)

@pytest.fixture(scope="function")
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def ballot_service(session):
    return BallotService(session)


@pytest.fixture
def user(session):
    u = User(username="testuser", email="testuser@example.com", hashed_password="hashed")
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
    l = Lottery(name="Closed Lottery", closure_date=date.today(), is_closed=True)
    session.add(l)
    session.commit()
    session.refresh(l)
    return l


def test_submit_ballot_success(ballot_service, user, open_lottery):
    ballot = ballot_service.submit_ballot(user, open_lottery)
    assert ballot.user_id == user.id
    assert ballot.lottery_id == open_lottery.id


def test_submit_ballot_to_closed_lottery(ballot_service, user, closed_lottery):
    with pytest.raises(LotteryAlreadyClosed):
        ballot_service.submit_ballot(user, closed_lottery)


def test_get_ballot_success(ballot_service, user, open_lottery):
    ballot = ballot_service.submit_ballot(user, open_lottery)
    retrieved = ballot_service.get_ballot(ballot.id)
    assert retrieved.id == ballot.id


def test_get_ballot_not_found(ballot_service):
    with pytest.raises(BallotNotFound):
        ballot_service.get_ballot(uuid4())


def test_get_ballots_by_user(ballot_service, user, open_lottery):
    ballot1 = ballot_service.submit_ballot(user, open_lottery)
    ballot2 = ballot_service.submit_ballot(user, open_lottery)

    ballots = ballot_service.get_ballots_by_user(user)
    assert len(ballots) == 2
    assert {b.id for b in ballots} == {ballot1.id, ballot2.id}


def test_get_ballots_by_lottery(ballot_service, user, open_lottery):
    ballot1 = ballot_service.submit_ballot(user, open_lottery)
    ballot2 = ballot_service.submit_ballot(user, open_lottery)

    ballots = ballot_service.get_ballots_by_lottery(open_lottery)
    assert len(ballots) == 2
    assert {b.id for b in ballots} == {ballot1.id, ballot2.id}
