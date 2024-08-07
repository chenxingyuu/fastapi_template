from datetime import timedelta, datetime
from typing import Optional

from fastapi import HTTPException
from jose import jwt, JWTError
from pydantic import BaseModel
from starlette import status

from cores.config import settings


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = timedelta(days=settings.security.token_expire_days)
):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, settings.security.secret_key, algorithm=settings.security.algorithm)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.security.secret_key, algorithms=[settings.security.algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
