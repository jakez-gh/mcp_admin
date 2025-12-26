from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from server import config, storage
from server.oauth import (
    build_auth_url,
    exchange_code_for_tokens,
    fetch_user_email,
    generate_state,
    verify_state,
)
from server.tools import all_tool_metadata

app = FastAPI(title="MCP Admin")


@app.on_event("startup")
async def startup() -> None:
    storage.init_db()


@app.get("/admin/gmail", response_class=HTMLResponse)
async def gmail_admin() -> str:
    status = storage.token_status()
    accounts = storage.list_accounts()
    accounts_html = (
        "".join(f"<li>{account.email} (token stored)</li>" for account in accounts)
        or "<li>No accounts connected</li>"
    )
    return f"""
    <html>
      <head><title>Gmail اتصال</title></head>
      <body>
        <h1>Gmail Connection</h1>
        <p>Status: <strong>{status}</strong></p>
        <a href=\"/admin/gmail/connect\">Connect Gmail</a>
        <h2>Connected Accounts</h2>
        <ul>{accounts_html}</ul>
      </body>
    </html>
    """


@app.get("/admin/gmail/connect")
async def gmail_connect() -> RedirectResponse:
    if not config.GMAIL_CLIENT_ID or not config.GMAIL_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Gmail OAuth is not configured")
    if not config.GMAIL_TOKEN_ENCRYPTION_KEY:
        raise HTTPException(status_code=500, detail="Token encryption is not configured")

    state = generate_state()
    url = build_auth_url(state)
    return RedirectResponse(url)


@app.get("/admin/gmail/callback", response_class=HTMLResponse)
async def gmail_callback(code: str | None = None, state: str | None = None) -> str:
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth code or state")
    if not verify_state(state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    token_payload = exchange_code_for_tokens(code)
    refresh_token = token_payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="No refresh token returned")

    access_token = token_payload["access_token"]
    email = fetch_user_email(access_token)
    storage.store_refresh_token(email, refresh_token)

    return f"""
    <html>
      <body>
        <h1>Gmail Connected</h1>
        <p>Stored refresh token for {email}.</p>
        <a href=\"/admin/gmail\">Back</a>
      </body>
    </html>
    """


@app.get("/admin/gmail/status")
async def gmail_status() -> JSONResponse:
    return JSONResponse(
        {
            "status": storage.token_status(),
            "accounts": [account.to_dict() for account in storage.list_accounts()],
        }
    )


@app.get("/tools/metadata")
async def tools_metadata() -> JSONResponse:
    return JSONResponse({"tools": all_tool_metadata()})
