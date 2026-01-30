from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from langchain.tools import tool

from app.config.settings import load_settings
from app.services.google_calendar import GoogleCalendarClient, GoogleCalendarError


@tool
def list_next_events_tool(n: int = 5) -> dict:
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
        dict: A structured response with events[] containing summary, start,
            end, and eventId fields.

    Example usage:
        User: "What are my next 3 events?"
        Tool call:
            list_next_events_tool(n=3)
    """
    if n <= 0:
        return "Please request a positive number of events."

    settings = load_settings()
    now = datetime.now(tz=ZoneInfo(settings.timezone)).isoformat(timespec="seconds")

    service = GoogleCalendarClient()
    try:
        events = service.list_events(time_min=now, max_results=n)
    except GoogleCalendarError as exc:
        return {
            "error": exc.message,
            "status": exc.status,
            "reason": exc.reason,
        }

    if not events:
        return {
            "events": []
        }
        
    events_list = []
    for event in events:
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")
        summary = event.get("summary", "Untitled event")
        event_id = event["id"]
        events_list.append({
            "summary": summary,
            "start": start,
            "end": end,
            "eventId": event_id
        })
        
    return {
        "events": events_list
    }

@tool
def list_today_events_tool() -> dict:
    """
    Use this tool to list the events of today when a user asks
    to see their schedule or requests for the day.
    
    The tool returns all the events of today starting from 00:00 to 00:00
    of the next day, ordered by start time.
    
    Returns:
        dict: A structured response with events[] containing summary, start,
            end, and eventId fields.

    Example usage:
        User: "Show me today's events"
        Tool call:
            list_today_events_tool()
    """
    settings = load_settings()
    now = datetime.now(tz=ZoneInfo(settings.timezone))
    start_day = now.replace().replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = start_day + timedelta(days=1)
    
    service = GoogleCalendarClient()
    try:
        events = service.list_from_to(
            time_min=start_day.isoformat(timespec="seconds"),
            time_max=end_day.isoformat(timespec="seconds"),
        )
    except GoogleCalendarError as exc:
        return {
            "error": exc.message,
            "status": exc.status,
            "reason": exc.reason,
        }
    
    if not events:
        return {
            "events": []
        }
        
    events_list = []
    for event in events:
        start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")
        summary = event.get("summary", "Untitled event")
        event_id = event["id"]
        events_list.append({
            "summary": summary,
            "start": start,
            "end": end,
            "eventId": event_id
        })
        
    return {
        "events": events_list
    }
