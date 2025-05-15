from fastapi import APIRouter, Query, Depends, HTTPException, status
from datetime import date
from typing import Annotated

from app.api.dependencies import get_ballot_service, get_lottery_service, get_current_user, require_admin
from app.domain.models import User
from app.schemas.ballot import BallotRead
from app.domain.services import BallotService, LotteryService
from app.domain.exceptions import LotteryNotFound, LotteryAlreadyClosed

router = APIRouter(prefix="/ballots", tags=["Ballots"])


@router.post("/", response_model=BallotRead, status_code=status.HTTP_201_CREATED)
def submit_ballot(
    lottery_date: Annotated[date, Query(title='Lottery closure date.')],
    current_user: User = Depends(get_current_user),
    ballot_service: BallotService = Depends(get_ballot_service),
    lottery_service: LotteryService = Depends(get_lottery_service),
):
    """
    Submit a ballot for the specified lottery date.
    Only registered users can submit ballots.
    Admins are not allowed to submit a ballot.
    """
    if current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot submit ballots.")
    
    try:
        lottery = lottery_service.get_lottery_by_date(lottery_date)
    except LotteryNotFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exception))

    try:
        return ballot_service.submit_ballot(current_user, lottery)
    except LotteryAlreadyClosed as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception))


@router.get("/mine", response_model=list[BallotRead])
def view_my_ballots(
    current_user: User = Depends(get_current_user),
    ballot_service: BallotService = Depends(get_ballot_service),
):
    """
    View all ballots submitted by the current user.
    """
    return ballot_service.get_ballots_by_user(current_user)


@router.get("/lottery/{lottery_date}", response_model=list[BallotRead])
def list_ballots_by_lottery(
    lottery_date: date,
    admin_user: User = Depends(require_admin),
    ballot_service: BallotService = Depends(get_ballot_service),
    lottery_service: LotteryService = Depends(get_lottery_service),
):
    """
    List all ballots for a specific lottery. Admin privileges are required.
    """
    try:
        lottery = lottery_service.get_lottery_by_date(lottery_date)
    except LotteryNotFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exception))

    return ballot_service.get_ballots_by_lottery(lottery)
