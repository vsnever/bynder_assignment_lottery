import pytest
import random
from datetime import date, timedelta
from uuid import uuid4
from sqlmodel import SQLModel, create_engine, Session

from app.domain.models import User, Lottery, Ballot
from app.schemas.lottery import LotteryCreate
from app.core.config import settings
from app.domain.services import LotteryService
from app.domain.exceptions import (
    LotteryAlreadyExists,
    LotteryNotFound,
    LotteryAlreadyClosed,
    LotteryNotClosed,
    LotteryInvalidClosureDate,
    LotteryNoWinnerDrawn
)

engine = create_engine(settings.DATABASE_URL)

@pytest.fixture(scope="function")
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def service(session):
    return LotteryService(session)


@pytest.fixture
def user(session):
    user = User(username="testuser", email="testuser@example.com", hashed_password="hashed")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_create_lottery_success(service):
    tomorrow = date.today() + timedelta(days=1)
    data = LotteryCreate(name="Test Lottery", closure_date=tomorrow)

    lottery = service.create_lottery(data)

    assert lottery.name == "Test Lottery"
    assert lottery.closure_date == tomorrow
    assert not lottery.is_closed


def test_create_lottery_in_the_past(service):
    yesterday = date.today() - timedelta(days=1)
    data = LotteryCreate(name="Past Lottery", closure_date=yesterday)

    with pytest.raises(LotteryInvalidClosureDate):
        service.create_lottery(data)


def test_create_lottery_already_exists(service):
    tomorrow = date.today() + timedelta(days=1)
    data = LotteryCreate(name="First Lottery", closure_date=tomorrow)
    service.create_lottery(data)

    with pytest.raises(LotteryAlreadyExists):
        service.create_lottery(data)


def test_get_lottery_success(service):
    tomorrow = date.today() + timedelta(days=1)
    data = LotteryCreate(name="Get Lottery", closure_date=tomorrow)
    created = service.create_lottery(data)

    fetched = service.get_lottery(created.id)

    assert fetched.id == created.id


def test_get_lottery_not_found(service):
    with pytest.raises(LotteryNotFound):
        service.get_lottery(uuid4())


def test_get_lottery_by_date_success(service):
    tomorrow = date.today() + timedelta(days=1)
    data = LotteryCreate(name="Date Lottery", closure_date=tomorrow)
    created = service.create_lottery(data)

    fetched = service.get_lottery_by_date(tomorrow)

    assert fetched.id == created.id


def test_get_lottery_by_date_not_found(service):
    future_date = date.today() + timedelta(days=10)

    with pytest.raises(LotteryNotFound):
        service.get_lottery_by_date(future_date)


def test_get_open_lotteries(service):
    tomorrow = date.today() + timedelta(days=1)
    day_after = tomorrow + timedelta(days=1)
    data1 = LotteryCreate(name="Lottery 1", closure_date=tomorrow)
    data2 = LotteryCreate(name="Lottery 2", closure_date=day_after)

    service.create_lottery(data1)
    service.create_lottery(data2)

    open_lotteries = service.get_open_lotteries()
    assert len(open_lotteries) == 2


def test_close_and_draw_winner(service, user):
    tomorrow = date.today() + timedelta(days=1)
    lottery = service.create_lottery(LotteryCreate(name="Winner Draw Lottery", closure_date=tomorrow))

    # Add ballots manually
    ballot1 = Ballot(lottery_id=lottery.id, user_id=user.id)
    ballot2 = Ballot(lottery_id=lottery.id, user_id=user.id)
    service.session.add_all([ballot1, ballot2])
    service.session.commit()
    service.session.refresh(lottery)

    closed_lottery = service.close_and_draw_winner(lottery)

    assert closed_lottery.is_closed
    assert closed_lottery.winning_ballot_id in [ballot1.id, ballot2.id]


def test_close_already_closed_lottery(service):
    tomorrow = date.today() + timedelta(days=1)
    lottery = service.create_lottery(LotteryCreate(name="Already Closed Lottery", closure_date=tomorrow))
    lottery.is_closed = True
    service.session.commit()

    with pytest.raises(LotteryAlreadyClosed):
        service.close_and_draw_winner(lottery)


def test_get_winning_ballot_success(service, user):
    tomorrow = date.today() + timedelta(days=1)
    lottery = service.create_lottery(LotteryCreate(name="Winning Ballot Lottery", closure_date=tomorrow))

    ballot = Ballot(lottery_id=lottery.id, user_id=user.id)
    service.session.add(ballot)
    service.session.commit()

    # Close lottery and set the winning ballot manually
    lottery.is_closed = True
    lottery.winning_ballot_id = ballot.id
    service.session.commit()

    winning = service.get_winning_ballot(lottery)

    assert winning.id == ballot.id


def test_get_winning_ballot_not_closed(service):
    tomorrow = date.today() + timedelta(days=1)
    lottery = service.create_lottery(LotteryCreate(name="Not Closed Lottery", closure_date=tomorrow))

    with pytest.raises(LotteryNotClosed):
        service.get_winning_ballot(lottery)


def test_get_winning_ballot_no_winner(service):
    tomorrow = date.today() + timedelta(days=1)
    lottery = service.create_lottery(LotteryCreate(name="No Winner", closure_date=tomorrow))

    lottery.is_closed = True
    service.session.commit()

    with pytest.raises(LotteryNoWinnerDrawn):
        service.get_winning_ballot(lottery)