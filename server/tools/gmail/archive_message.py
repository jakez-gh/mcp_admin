import httpx

from server import storage
from server.oauth import refresh_access_token

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"


def archive_message(email: str, message_id: str) -> dict:
    refresh_token = storage.get_refresh_token(email)
    if not refresh_token:
        raise RuntimeError("No refresh token stored for this account")

    token_response = refresh_access_token(refresh_token)
    access_token = token_response["access_token"]

    url = f"{GMAIL_API_BASE}/users/me/messages/{message_id}/modify"
    payload = {"removeLabelIds": ["INBOX"]}
    response = httpx.post(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def metadata() -> dict:
    return {
        "name": "archive_message",
        "description": "Archive a Gmail message by removing the INBOX label.",
        "inputs": {
            "email": "Gmail account email address.",
            "message_id": "ID of the Gmail message to archive.",
        },
        "token_status": storage.token_status(),
        "scopes": ["https://www.googleapis.com/auth/gmail.modify"],
    }
