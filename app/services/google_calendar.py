from __future__ import annotations

from app.config.settings import load_settings

from app.services.auth.google_oauth import load_google_credentials
from googleapiclient.discovery import build

class GoogleCalendarClient:
    def __init__(self):
        self._settings = load_settings()
        self._service = self._build_service()
        
    def _build_service(self):
        creds = load_google_credentials(
            credentials_file=self._settings.google_credentials_file,
            token_file=self._settings.google_token_file,
        )
        
        return build("calendar", "v3", credentials=creds)
    
    def create_event(self, summary, start_time, end_time):
        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time,
                'timeZone': self._settings.timezone,
            },
            "end": {
                "dateTime": end_time,
                'timeZone': self._settings.timezone,
            },
        }
        
        return self._service.events().insert(
            calendarId=self._settings.default_calendar_id,
            body=event
        ).execute()