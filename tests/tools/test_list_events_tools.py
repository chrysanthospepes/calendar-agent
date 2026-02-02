from datetime import datetime

from app.tools.list_events import list_next_events_tool, list_today_events_tool


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime(2026, 1, 30, 9, 0, 0, tzinfo=tz)


def test_list_next_events_tool_calls_service_and_formats_events(monkeypatch):
    calls = {}

    class MockSettings:
        timezone = "UTC"

    class MockService:
        def list_events(self, time_min, max_results=5):
            calls["time_min"] = time_min
            calls["max_results"] = max_results
            return [
                {
                    "id": "evt_1",
                    "summary": "Standup",
                    "start": {"dateTime": "2026-01-30T10:00:00+00:00"},
                    "end": {"dateTime": "2026-01-30T10:15:00+00:00"},
                }
            ]

    monkeypatch.setattr("app.tools.list_events.load_settings", lambda: MockSettings())
    monkeypatch.setattr("app.tools.list_events.GoogleCalendarClient", lambda: MockService())
    monkeypatch.setattr("app.tools.list_events.datetime", FixedDateTime)

    result = list_next_events_tool.func(n=1)

    assert calls["time_min"] == "2026-01-30T09:00:00+00:00"
    assert calls["max_results"] == 1
    assert result == {
        "ok": True,
        "data": {
            "events": [
                {
                    "summary": "Standup",
                    "start": "2026-01-30T10:00:00+00:00",
                    "end": "2026-01-30T10:15:00+00:00",
                    "eventId": "evt_1",
                }
            ]
        },
        "error": None,
    }


def test_list_next_events_tool_rejects_non_positive_n():
    result = list_next_events_tool.func(n=0)

    assert result["ok"] is False
    assert result["data"] is None
    assert result["error"]["message"] == "Please request a positive number of events."
    assert result["error"]["code"] == "invalid_argument"


def test_list_today_events_tool_calls_service_for_day_window(monkeypatch):
    calls = {}

    class MockSettings:
        timezone = "UTC"

    class MockService:
        def list_from_to(self, time_min, time_max):
            calls["time_min"] = time_min
            calls["time_max"] = time_max
            return []

    monkeypatch.setattr("app.tools.list_events.load_settings", lambda: MockSettings())
    monkeypatch.setattr("app.tools.list_events.GoogleCalendarClient", lambda: MockService())
    monkeypatch.setattr("app.tools.list_events.datetime", FixedDateTime)

    result = list_today_events_tool.func()

    assert calls["time_min"] == "2026-01-30T00:00:00+00:00"
    assert calls["time_max"] == "2026-01-31T00:00:00+00:00"
    assert result == {"ok": True, "data": {"events": []}, "error": None}


def test_list_today_events_tool_returns_error_shape(monkeypatch):
    from app.services.google_calendar import GoogleCalendarError

    class MockSettings:
        timezone = "UTC"

    class MockService:
        def list_from_to(self, time_min, time_max):
            raise GoogleCalendarError(
                "Fail",
                status=502,
                reason="Bad gateway",
            )

    monkeypatch.setattr("app.tools.list_events.load_settings", lambda: MockSettings())
    monkeypatch.setattr("app.tools.list_events.GoogleCalendarClient", lambda: MockService())
    monkeypatch.setattr("app.tools.list_events.datetime", FixedDateTime)

    result = list_today_events_tool.func()

    assert result["ok"] is False
    assert result["data"] is None
    assert result["error"]["message"] == "Fail"
    assert result["error"]["status"] == 502
    assert result["error"]["reason"] == "Bad gateway"
    assert result["error"]["code"] == "google_calendar_error"
