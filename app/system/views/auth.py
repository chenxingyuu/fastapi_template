from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.system.models import User
from app.system.serializers import UserDetail
from cores.jwt import Token, create_access_token
from cores.pwd import verify_password

auth_router = APIRouter()


async def authenticate_user(username: str, password: str) -> bool | UserDetail:
    user = await User.get_queryset().get_or_none(username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return UserDetail.from_orm(user)


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user: UserDetail = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}
