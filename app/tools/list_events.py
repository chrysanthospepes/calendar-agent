from datetime import datetime
from zoneinfo import ZoneInfo

from langchain.tools import tool

from app.config.settings import load_settings
from app.services.google_calendar import GoogleCalendarClient


@tool
def list_next_events_tool(n: int = 5) -> str:
    """
    Use this tool to list the next upcoming calendar events when a user asks
    to see their schedule or requests the next N events.

    The tool returns the next N upcoming events starting from now, ordered by
    start time. If the user does not specify N, default to 5.

    Do NOT use this tool if:
    - The user asks to create, edit, or delete an event
    - The user asks for availability without requesting event details

    Args:
        n (int): Number of upcoming events to list.

    Returns:
        str: A list of upcoming events with start and end times.
    """
    if n <= 0:
        return "Please request a positive number of events."

    settings = load_settings()
    now = datetime.now(tz=ZoneInfo(settings.timezone)).isoformat(timespec="seconds")

    service = GoogleCalendarClient()
    events = service.list_events(time_min=now, max_results=n)

    if not events:
        return "No upcoming events found."

    lines = []
    for idx, event in enumerate(events, start=1):
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")
        summary = event.get("summary", "Untitled event")
        event_id = event["id"]
        lines.append(f"{idx}. {summary} ({start} - {end}), eventID: {event_id} ")
        
    return "\n".join(lines)