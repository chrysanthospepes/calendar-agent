from app.tools.delete_event import delete_event_tool


def test_delete_event_tool_fetches_summary_and_deletes(monkeypatch):
    calls = {"deleted": False}

    class MockService:
        def get_event(self, event_id):
            calls["event_id"] = event_id
            return {"summary": "Test Meet"}

        def delete_event(self, event_id):
            calls["deleted"] = True
            calls["deleted_id"] = event_id

    monkeypatch.setattr("app.tools.delete_event.GoogleCalendarClient", lambda: MockService())

    result = delete_event_tool.func(event_id="event_1")

    assert calls["event_id"] == "event_1"
    assert calls["deleted"] is True
    assert calls["deleted_id"] == "event_1"
    assert result == {
        "ok": True,
        "data": {"summary": "Test Meet", "eventId": "event_1"},
        "error": None,
    }


def test_delete_event_tool_returns_error_shape(monkeypatch):
    from app.services.google_calendar import GoogleCalendarError

    class MockService:
        def get_event(self, event_id):
            raise GoogleCalendarError(
                "Nope",
                status=404,
                reason="Not found",
            )

    monkeypatch.setattr("app.tools.delete_event.GoogleCalendarClient", lambda: MockService())

    result = delete_event_tool.func(event_id="event_1")

    assert result["ok"] is False
    assert result["data"] is None
    assert result["error"]["message"] == "Nope"
    assert result["error"]["status"] == 404
    assert result["error"]["reason"] == "Not found"
    assert result["error"]["code"] == "google_calendar_error"
