from typing import List, Optional

from app.system.serializers.auth import GithubEmail, GithubToken
from cores.async_http import async_http_request
from cores.config import settings

oauth_api = "https://github.com/login/oauth/access_token"
emails_api = "https://api.github.com/user/emails"


async def get_access_token(code: str) -> GithubToken:
    response = await async_http_request(
        url=oauth_api,
        headers={"Accept": "application/json"},
        json={
            "client_id": settings.github.client,
            "client_secret": settings.github.secret,
            "code": code,
        },
    )
    json_data = response.json()
    return GithubToken(**json_data)


async def get_emails_by_access_token(token: GithubToken) -> List[GithubEmail]:
    response = await async_http_request(
        url=emails_api,
        headers={
            "Accept": "application/json",
            "Authorization": f"{token.token_type} {token.access_token}",
        },
    )
    json_data = response.json()
    return [GithubEmail(**email_data) for email_data in json_data]


async def get_primary_email_by_access_token(token: GithubToken) -> Optional[GithubEmail]:
    emails = await get_emails_by_access_token(token)
    return next((email for email in emails if email.primary), None)
