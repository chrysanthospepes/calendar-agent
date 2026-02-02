from datetime import datetime
from zoneinfo import ZoneInfo

from app.tools.create_event import check_conflicts_tool


def test_check_conflicts_tool_expands_window_and_returns_conflicts(monkeypatch):
    calls = {}

    class MockSettings:
        timezone = "UTC"

    class MockService:
        def list_from_to(self, time_min, time_max):
            calls["time_min"] = time_min
            calls["time_max"] = time_max
            return [
                {
                    "summary": "Existing Meeting",
                    "start": {"dateTime": "2026-01-30T10:15:00+00:00"},
                    "end": {"dateTime": "2026-01-30T10:45:00+00:00"},
                }
            ]

    monkeypatch.setattr("app.tools.create_event.load_settings", lambda: MockSettings())
    monkeypatch.setattr("app.tools.create_event.GoogleCalendarClient", lambda: MockService())

    start = datetime(2026, 1, 30, 10, 0, 0)
    end = datetime(2026, 1, 30, 11, 0, 0)

    result = check_conflicts_tool.func(start=start, end=end, buffer_minutes=15)

    assert calls["time_min"] == "2026-01-30T09:45:00+00:00"
    assert calls["time_max"] == "2026-01-30T11:15:00+00:00"
    assert result == {
        "ok": True,
        "data": {
            "conflict_count": 1,
            "conflicts": [
                {
                    "summary": "Existing Meeting",
                    "start": "2026-01-30T10:15:00+00:00",
                    "end": "2026-01-30T10:45:00+00:00",
                }
            ],
        },
        "error": None,
    }


def test_check_conflicts_tool_returns_error_shape(monkeypatch):
    from app.services.google_calendar import GoogleCalendarError

    class MockSettings:
        timezone = "UTC"

    class MockService:
        def list_from_to(self, time_min, time_max):
            raise GoogleCalendarError(
                "Down",
                status=500,
                reason="Internal error",
            )

    monkeypatch.setattr("app.tools.create_event.load_settings", lambda: MockSettings())
    monkeypatch.setattr("app.tools.create_event.GoogleCalendarClient", lambda: MockService())

    start = datetime(2026, 1, 30, 10, 0, 0)
    end = datetime(2026, 1, 30, 11, 0, 0)

    result = check_conflicts_tool.func(start=start, end=end, buffer_minutes=0)

    assert result["ok"] is False
    assert result["data"] is None
    assert result["error"]["message"] == "Down"
    assert result["error"]["status"] == 500
    assert result["error"]["reason"] == "Internal error"
    assert result["error"]["code"] == "google_calendar_error"


def test_check_conflicts_tool_converts_timezone_and_respects_buffer(monkeypatch):
    calls = {}

    class MockSettings:
        timezone = "America/Los_Angeles"

    class MockService:
        def list_from_to(self, time_min, time_max):
            calls["time_min"] = time_min
            calls["time_max"] = time_max
            return []

    monkeypatch.setattr("app.tools.create_event.load_settings", lambda: MockSettings())
    monkeypatch.setattr("app.tools.create_event.GoogleCalendarClient", lambda: MockService())

    start = datetime(2026, 1, 30, 10, 0, 0, tzinfo=ZoneInfo("UTC"))
    end = datetime(2026, 1, 30, 11, 0, 0, tzinfo=ZoneInfo("UTC"))

    result = check_conflicts_tool.func(start=start, end=end, buffer_minutes=15)

    assert calls["time_min"] == "2026-01-30T01:45:00-08:00"
    assert calls["time_max"] == "2026-01-30T03:15:00-08:00"
    assert result == {
        "ok": True,
        "data": {"conflict_count": 0, "conflicts": []},
        "error": None,
    }
