from app.tools.create_event import create_event_tool

class CalendarAgent:
    def __init__(self):
        self.tools = {
            "create_event": create_event_tool
        }

    def run(self, user_prompt: str) -> str:
        """
        1. Parse intent (via LLM)
        2. Call create_event tool
        3. Return confirmation
        """
        # Later: replace with real LLM call
        event_data = {
            "title": "Meeting",
            "start": "2026-01-20T10:00:00",
            "end": "2026-01-20T11:00:00"
        }

        return self.tools["create_event"](**event_data)