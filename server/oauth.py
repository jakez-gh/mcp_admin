from typing import Dict
from urllib.parse import urlencode

import httpx

from server import config

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def build_auth_url(state: str) -> str:
    query = urlencode(
        {
            "client_id": config.GMAIL_CLIENT_ID,
            "redirect_uri": config.GMAIL_REDIRECT_URI,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "scope": " ".join(config.GMAIL_OAUTH_SCOPES),
            "state": state,
        }
    )
    return f"{GOOGLE_AUTH_URL}?{query}"


def exchange_code_for_tokens(code: str) -> Dict[str, str]:
    payload = {
        "client_id": config.GMAIL_CLIENT_ID,
        "client_secret": config.GMAIL_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.GMAIL_REDIRECT_URI,
    }
    response = httpx.post(GOOGLE_TOKEN_URL, data=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    payload = {
        "client_id": config.GMAIL_CLIENT_ID,
        "client_secret": config.GMAIL_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = httpx.post(GOOGLE_TOKEN_URL, data=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_user_email(access_token: str) -> str:
    response = httpx.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["email"]
