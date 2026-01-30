from langchain.tools import tool
from app.services.google_calendar import GoogleCalendarClient, GoogleCalendarError
from app.config.settings import load_settings
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def _ensure_tz(dt: datetime, tz: ZoneInfo) -> datetime:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)

@tool
def create_event_tool(title: str, start: datetime, end: datetime) -> dict:
    """
    Use this tool to create a calendar event when a user asks to schedule,
    book, add, or create an event or meeting at a specific date and time.

    The tool requires a clear event title, a start datetime, and an end datetime.
    Datetimes must be concrete (not relative) and will be converted to ISO-8601
    format with second-level precision before being sent to Google Calendar.

    Do NOT use this tool if:
    - The user is only asking questions about availability
    - The user provides incomplete or ambiguous time information
    - The user is asking to edit or delete an existing event

    Args:
        title (str): A concise event title (e.g., "Team Sync", "Doctor Appointment").
        start (datetime): The exact start datetime of the event.
        end (datetime): The exact end datetime of the event.

    Returns:
        dict: A structured response with summary, start date and end date of the
        newly created event.
        
    Example usage:
        User: "Schedule a team meeting tomorrow from 10am to 11am"
        Tool call:
            create_event_tool(
                title="Team Meeting",
                start=datetime(2026, 1, 20, 10, 0),
                end=datetime(2026, 1, 20, 11, 0)
            )
    """
    service = GoogleCalendarClient()
    try:
        event = service.create_event(
            summary=title,
            start_time=start.isoformat(timespec="seconds"),
            end_time=end.isoformat(timespec="seconds"),
        )
    except GoogleCalendarError as exc:
        return {
            "error": exc.message,
            "status": exc.status,
            "reason": exc.reason,
        }

    return {
        "summary": event['summary'],
        "start": start,
        "end": end
    }

@tool
def check_conflicts_tool(start: datetime, end: datetime, buffer_minutes: int = 0) -> dict:
    """
    Use this tool to check for existing calendar events that conflict with a
    proposed time window before creating or rescheduling an event.

    The tool expands the requested window by `buffer_minutes` on both sides
    to capture near-miss conflicts, then lists any events found in that range.
    If no events are found, it returns a safe-to-proceed message.

    Do NOT use this tool if:
    - The user is explicitly asking to create, edit, or delete an event
    - The user has not provided a concrete start and end datetime

    Args:
        start (datetime): The proposed start datetime to check.
        end (datetime): The proposed end datetime to check.
        buffer_minutes (int, optional): Minutes to pad before and after the
            window when searching for conflicts. Defaults to 0.
        
    Returns:
        dict: A structured response with conflict_count and conflicts[].

    Example usage:
        User: "Am I free on Jan 20, 2026 from 2pm to 3pm?"
        Tool call:
            check_conflicts_tool(
                start=datetime(2026, 1, 20, 14, 0),
                end=datetime(2026, 1, 20, 15, 0),
                buffer_minutes=15
            )
    """
    settings = load_settings()
    tz = ZoneInfo(settings.timezone)
    start_tz = _ensure_tz(start, tz)
    end_tz = _ensure_tz(end, tz)

    time_min = start_tz - timedelta(minutes=buffer_minutes)
    time_end = end_tz + timedelta(minutes=buffer_minutes)
    
    service = GoogleCalendarClient()
    try:
        events = service.list_from_to(
            time_min=time_min.isoformat(timespec="seconds"),
            time_max=time_end.isoformat(timespec="seconds"),
        )
    except GoogleCalendarError as exc:
        return {
            "error": exc.message,
            "status": exc.status,
            "reason": exc.reason,
        }
    
    if not events:
        return {
            "conflict_count": 0,
            "conflicts": []
        }
    
    conflicts = []
    for event in events:
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")
        summary = event.get("summary", "Untitled event")
        conflicts.append({
            "summary": summary,
            "start": start,
            "end": end
        })

    return {
        "conflict_count": len(conflicts),
        "conflicts": conflicts
    }
