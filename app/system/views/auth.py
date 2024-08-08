from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from passlib.exc import InvalidTokenError
from pydantic import BaseModel, ValidationError
from starlette import status

from app.system.models import Permission, User
from cores.jwt import Token, create_access_token, verify_token
from cores.pwd import verify_password
from cores.scope import filter_scopes, scopes

auth_router = APIRouter(dependency_overrides_provider=None)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token", scopes=scopes
)


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []


async def authenticate_user(username: str, password: str) -> bool | User:
    user = await User.get_queryset().get_or_none(username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = verify_token(token)

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    user = await User.get_queryset().get_or_none(username=username)
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        for user_scope in token_data.scopes:
            if scope.startswith(user_scope):
                break
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_user(
    current_user: User = Security(get_current_user),
) -> User:
    if current_user.is_active:
        return current_user
    raise HTTPException(status_code=400, detail="Inactive user")


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )

    # 查询权限
    permissions = (
        await Permission.get_queryset()
        .filter(users=user)
        .all()
        .values_list("name", flat=True)
    )

    access_token = create_access_token(
        data={"sub": user.username, "scopes": filter_scopes(permissions)}
    )
    return Token(access_token=access_token, token_type="bearer")
