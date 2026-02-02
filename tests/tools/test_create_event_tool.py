from datetime import datetime
from app.tools.create_event import create_event_tool

def test_create_event_tool_calls_service_and_returns_data(monkeypatch):
    calls = {}

    class MockSettings:
        timezone = "UTC"
    
    class MockService:
        def create_event(self, summary, start_time, end_time):
            calls["summary"] = summary
            calls["start"] = start_time
            calls["end"] = end_time
            return {"summary": summary}
        
    monkeypatch.setattr(
        "app.tools.create_event.GoogleCalendarClient",
        lambda: MockService()
    )
    monkeypatch.setattr("app.tools.create_event.load_settings", lambda: MockSettings())
    
    start = datetime(2026, 1, 30, 10, 0, 0)
    end = datetime(2026, 1, 30, 11, 0 ,0)
    
    result = create_event_tool.func(title="Test", start=start, end=end)
    
    assert calls["summary"] == "Test"
    assert calls["start"] == "2026-01-30T10:00:00+00:00"
    assert calls["end"] == "2026-01-30T11:00:00+00:00"
    
    assert result == {
        "ok": True,
        "data": {
            "summary": "Test",
            "start": start,
            "end": end,
        },
        "error": None,
    }


def test_create_event_tool_returns_error_shape(monkeypatch):
    from app.services.google_calendar import GoogleCalendarError

    class MockSettings:
        timezone = "UTC"

    class MockService:
        def create_event(self, summary, start_time, end_time):
            raise GoogleCalendarError(
                "Boom",
                status=503,
                reason="Service unavailable",
            )

    monkeypatch.setattr(
        "app.tools.create_event.GoogleCalendarClient",
        lambda: MockService(),
    )
    monkeypatch.setattr("app.tools.create_event.load_settings", lambda: MockSettings())

    start = datetime(2026, 1, 30, 10, 0, 0)
    end = datetime(2026, 1, 30, 11, 0, 0)

    result = create_event_tool.func(title="Test", start=start, end=end)

    assert result["ok"] is False
    assert result["data"] is None
    assert result["error"]["message"] == "Boom"
    assert result["error"]["status"] == 503
    assert result["error"]["reason"] == "Service unavailable"
    assert result["error"]["code"] == "google_calendar_error"
