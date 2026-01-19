from app.services.google_calendar import GoogleCalendarClient

def create_event_tool(title: str, start: str, end: str) -> str:
    service = GoogleCalendarClient()
    event = service.create_event(
        summary=title,
        start_time=start,
        end_time=end
    )
    return f"Event created: {event['summary']} ({start} → {end})"
