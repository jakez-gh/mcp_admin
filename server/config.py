import os

GMAIL_CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET", "")
GMAIL_REDIRECT_URI = os.environ.get("GMAIL_REDIRECT_URI", "http://localhost:8000/admin/gmail/callback")
GMAIL_TOKEN_ENCRYPTION_KEY = os.environ.get("GMAIL_TOKEN_ENCRYPTION_KEY", "")

GMAIL_OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/userinfo.email",
]

DB_PATH = os.environ.get("MCP_ADMIN_DB_PATH", "/workspace/mcp_admin/server/mcp_admin.sqlite")
