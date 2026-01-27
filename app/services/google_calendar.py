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

    def list_events(self, time_min, max_results=5):
        return self._service.events().list(
            calendarId=self._settings.default_calendar_id,
            timeMin=time_min,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute().get("items", [])
        
    def list_from_to(self, time_min, time_max):
        return self._service.events().list(
            calendarId=self._settings.default_calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        ).execute().get("items", [])
        
    def delete_event(self, event_id: str):
        return self._service.events().delete(
            calendarId=self._settings.default_calendar_id,
            eventId=event_id,
        ).execute()
        
    def get_event(self, event_id: str):
        return self._service.events().get(
            calendarId=self._settings.default_calendar_id,
            eventId=event_id
        ).execute()