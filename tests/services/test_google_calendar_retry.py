from googleapiclient.errors import HttpError

from app.services.google_calendar import GoogleCalendarClient


class _Resp:
    def __init__(self, status: int, reason: str = "service unavailable"):
        self.status = status
        self.reason = reason


def test_execute_retries_transient_http_errors(monkeypatch):
    # Avoid building a real Google service client.
    monkeypatch.setattr(GoogleCalendarClient, "_build_service", lambda self: None)

    client = GoogleCalendarClient()
    client._MAX_RETRIES = 2
    client._BASE_BACKOFF_SECONDS = 0.0

    sleeps = []
    monkeypatch.setattr("app.services.google_calendar.time.sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr("app.services.google_calendar.random.uniform", lambda a, b: 0.0)

    calls = {"count": 0}

    class DummyRequest:
        def execute(self):
            calls["count"] += 1
            if calls["count"] <= 2:
                raise HttpError(_Resp(503), b"service unavailable")
            return {"ok": True}

    result = client._execute("test_op", DummyRequest())

    assert result == {"ok": True}
    assert calls["count"] == 3
    assert len(sleeps) == 2
