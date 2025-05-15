from jose import jwt
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from datetime import datetime, timezone, timedelta


def test_hash_verify_password():
    password = "test_password"
    hashed_password = hash_password(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password) is True
    assert verify_password("wrong_password", hashed_password) is False


def test_create_access_token_validity():
    sub = "test-user-id"
    token = create_access_token(sub)

    # Decode the token
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    # Check payload contents
    assert payload.get("sub") == sub
    assert "exp" in payload

    # Check expiration is in the future
    exp_timestamp = payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    exp_datetime_expected = datetime.now(timezone.utc) + expires_delta

    threshold_seconds = timedelta(seconds=1).total_seconds()
    
    assert abs((exp_datetime - exp_datetime_expected).total_seconds()) < threshold_seconds