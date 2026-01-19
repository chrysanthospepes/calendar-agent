from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import os
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Settings:
    # OpenAI
    openai_api: str = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    
    # Google auth files
    google_credentials_file: Path = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", "secrets/credentials.json"))
    google_token_file: Path = Path(os.getenv("GOOGLE_TOKEN_FILE", "secrets/token.json"))
    
    # Calendar defaults
    default_calendar_id: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    timezone: str = os.getenv("CALENDAR_TIMEZONE", "Europe/Athens")
    
def load_settings() -> Settings:
    return Settings()