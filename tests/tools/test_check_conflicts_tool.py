from datetime import datetime

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
        "conflict_count": 1,
        "conflicts": [
            {
                "summary": "Existing Meeting",
                "start": "2026-01-30T10:15:00+00:00",
                "end": "2026-01-30T10:45:00+00:00",
            }
        ],
    }
