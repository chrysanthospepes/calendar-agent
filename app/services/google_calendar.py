from __future__ import annotations

from app.config.settings import load_settings

from app.services.auth.google_oauth import load_google_credentials
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None, reason: str | None = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.reason = reason

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
                "timeZone": self._settings.timezone,
            },
            "end": {
                "dateTime": end_time,
                "timeZone": self._settings.timezone,
            },
        }

        return self._execute(
            "create_event",
            self._service.events().insert(
                calendarId=self._settings.default_calendar_id,
                body=event,
            ),
        )

    def list_events(self, time_min, max_results=5):
        response = self._execute(
            "list_events",
            self._service.events().list(
                calendarId=self._settings.default_calendar_id,
                timeMin=time_min,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ),
        )
        return response.get("items", [])
        
    def list_from_to(self, time_min, time_max):
        response = self._execute(
            "list_from_to",
            self._service.events().list(
                calendarId=self._settings.default_calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            ),
        )
        return response.get("items", [])
        
    def delete_event(self, event_id: str):
        return self._execute(
            "delete_event",
            self._service.events().delete(
                calendarId=self._settings.default_calendar_id,
                eventId=event_id,
            ),
        )
        
    def get_event(self, event_id: str):
        return self._execute(
            "get_event",
            self._service.events().get(
                calendarId=self._settings.default_calendar_id,
                eventId=event_id,
            ),
        )

    @staticmethod
    def _http_error_details(error: HttpError) -> tuple[int | None, str | None]:
        status = getattr(error.resp, "status", None)
        reason = None
        if hasattr(error, "error_details") and error.error_details:
            reason = "; ".join(str(detail) for detail in error.error_details)
        elif hasattr(error, "content") and error.content:
            reason = str(error.content)
        return status, reason

    def _execute(self, operation: str, request):
        try:
            return request.execute()
        except HttpError as exc:
            status, reason = self._http_error_details(exc)
            raise GoogleCalendarError(
                f"Google Calendar API error during {operation}.",
                status=status,
                reason=reason,
            ) from exc
        except RefreshError as exc:
            raise GoogleCalendarError(
                "Google Calendar credentials expired or invalid.",
                reason=str(exc),
            ) from exc
