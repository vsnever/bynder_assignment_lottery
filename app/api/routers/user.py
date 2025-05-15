from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserRead
from app.domain.services import UserService
from app.api.dependencies import get_user_service
from app.core.security import create_access_token
from app.domain.exceptions import UserAlreadyExists, UserInvalidCredentials, UserNotFound


router = APIRouter(tags=["User"])


@router.post("/user/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, service: UserService = Depends(get_user_service)):
    """
    Register a new user.
    """
    try:
        return service.register_user(user_in)

    except UserAlreadyExists as exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception))


@router.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), service: UserService = Depends(get_user_service)):
    """
    Authenticate a user and return an access token.
    """
    try:
        user = service.authenticate_user(form_data.username, form_data.password)
    except UserNotFound as exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exception))

    except UserInvalidCredentials as exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exception))
    
    token = create_access_token(sub=str(user.id))
    return {"access_token": token, "token_type": "bearer"}
