from __future__ import annotations

from pathlib import Path
from typing import Sequence

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

DEFAULT_SCOPES: Sequence[str] = ("https://www.googleapis.com/auth/calendar",)

def load_google_credentials(
    *,
    credentials_file: Path,
    token_file: Path,
    scopes: Sequence[str] = DEFAULT_SCOPES,
) -> Credentials:
    """
    Load stored user credentials (token), refresh if needed, or run local OAuth flow.
    Single user.
    """
    creds: Credentials | None = None

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), scopes=scopes)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(creds.to_json(), encoding="utf-8")
        return creds

    # First-time auth (Desktop app flow). This matches Google’s Python quickstart pattern.
    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), scopes=scopes)
    creds = flow.run_local_server(port=0)

    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds
