from server import storage


def list_authenticated_accounts() -> list[dict]:
    return [account.to_dict() for account in storage.list_accounts()]


def metadata() -> dict:
    return {
        "name": "list_authenticated_accounts",
        "description": "List Gmail accounts connected to the admin UI.",
        "outputs": {
            "email": "Gmail account email address.",
            "has_token": "Whether a refresh token is stored for the account.",
        },
        "token_status": storage.token_status(),
    }
