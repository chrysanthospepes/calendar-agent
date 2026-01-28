from langchain.tools import tool

from app.services.google_calendar import GoogleCalendarClient

@tool
def delete_event_tool(event_id: str) -> dict:
    """
    Use this tool to delete a calendar event when a user explicitly asks to
    cancel, remove, or delete a specific event.

    The tool requires a concrete event id. If the user provides an event title,
    time range, or other details instead of an id, first use a listing tool to
    identify the event id, then call this tool.

    Do NOT use this tool if:
    - The user is only asking to view events or availability
    - The user is asking to edit, reschedule, or update an event
    - The event id is missing or ambiguous

    Args:
        event_id (str): The unique Google Calendar event id to delete.

    Returns:
        dict: A structured response with the summary and event id of
        the deleted event.

    Example usage:
        User: "Delete the event with id abc123"
        Tool call:
            delete_event_tool(event_id="abc123")
    """
    service = GoogleCalendarClient()
    
    event = service.get_event(event_id=event_id)
    summary = event.get("summary", "Untitled Event")
    
    service.delete_event(event_id=event_id)
    
    return {
        "summary": summary,
        "eventId": event_id
    }
