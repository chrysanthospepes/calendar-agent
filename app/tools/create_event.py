from langchain.tools import tool
from app.services.google_calendar import GoogleCalendarClient
from datetime import datetime

@tool
def create_event_tool(title: str, start: datetime, end: datetime) -> str:
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
        str: A confirmation message describing the newly created calendar event.
        
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
    event = service.create_event(
        summary=title,
        start_time=start.isoformat(timespec="seconds"),
        end_time=end.isoformat(timespec="seconds")
    )
    print(f"Event created: {event['summary']} ({start} → {end})")
    return f"Event created: {event['summary']} ({start} → {end})"
