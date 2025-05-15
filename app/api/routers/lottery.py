from fastapi import APIRouter, Query, Depends, HTTPException, status
from datetime import date
from typing import Annotated

from app.api.dependencies import require_admin, get_lottery_service
from app.domain.services import LotteryService
from app.domain.models import User
from app.schemas.lottery import LotteryCreate, LotteryRead
from app.schemas.ballot import WinnerBallotRead
from app.domain.exceptions import (
    LotteryNotFound,
    LotteryAlreadyExists,
    LotteryAlreadyClosed,
    LotteryNoWinnerDrawn,
    LotteryNotClosed,
    LotteryInvalidClosureDate
)

router = APIRouter(prefix="/lotteries", tags=["Lotteries"])


@router.get("/", response_model=list[LotteryRead])
def list_open_lotteries(service: LotteryService = Depends(get_lottery_service)):
    """
    List all open lotteries. No registration required.
    """
    return service.get_open_lotteries()


@router.get("/{closure_date}", response_model=LotteryRead)
def get_lottery_by_date(closure_date: date, service: LotteryService = Depends(get_lottery_service)):
    """
    Get a lottery by its closure date. No registration required.
    """
    try:
        return service.get_lottery_by_date(closure_date)
    except LotteryNotFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exception))


@router.get("/{closure_date}/winner", response_model=WinnerBallotRead)
def get_winning_ballot(closure_date: date, service: LotteryService = Depends(get_lottery_service)):
    """
    Get the winning ballot for a lottery by its closure date.
    No registration required.
    """
    try:
        lottery = service.get_lottery_by_date(closure_date)
    except LotteryNotFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exception))

    try:
        return service.get_winning_ballot(lottery)
    except (LotteryNotClosed, LotteryNoWinnerDrawn) as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception))


@router.post("/", response_model=LotteryRead, status_code=status.HTTP_201_CREATED)
def create_lottery(
    request: LotteryCreate,
    service: LotteryService = Depends(get_lottery_service),
    admin_user: User = Depends(require_admin),
):
    """
    Create a new lottery. If no name is provided, a random name will be generated.
    Admin privileges are required to create a lottery.
    """
    try:
        return service.create_lottery(request)
    except (LotteryAlreadyExists, LotteryInvalidClosureDate) as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception))


@router.post("/close_and_draw", response_model=LotteryRead)
def close_and_draw_winner(
    lottery_date: Annotated[date, Query(title='Lottery closure date.')],
    service: LotteryService = Depends(get_lottery_service),
    admin_user: User = Depends(require_admin),
):
    """
    Draw a winner for the lottery with the given closure date.
    Admin privileges are required to draw a winner.
    """
    try:
        lottery = service.get_lottery_by_date(lottery_date)
    except LotteryNotFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exception))

    try:
        return service.close_and_draw_winner(lottery)
    except LotteryAlreadyClosed as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception))
