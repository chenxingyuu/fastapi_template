from typing import Optional

from pydantic import BaseModel


class GithubToken(BaseModel):
    access_token: str
    token_type: str
    scope: str


class GithubEmail(BaseModel):
    email: str
    primary: bool
    verified: bool
    visibility: Optional[str]


class OAuth2GithubRequestForm(BaseModel):
    code: str
