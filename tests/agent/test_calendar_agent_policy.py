from app.agent.calendar_agent import CalendarAgent
from app.agent.prompts import SYSTEM_PROMPT
from app.tools.create_event import check_conflicts_tool


def test_system_prompt_requires_conflict_checks():
    assert "Always run conflict check before creating or rescheduling events." in SYSTEM_PROMPT


def test_calendar_agent_registers_conflict_check_tool(monkeypatch):
    captured = {}

    class MockSettings:
        openai_api = "test"
        openai_model = "test-model"

    class MockLLM:
        def __init__(self, **kwargs):
            captured["llm_kwargs"] = kwargs

    def mock_create_agent(*, model, tools, system_prompt):
        captured["tools"] = tools
        captured["system_prompt"] = system_prompt
        return object()

    monkeypatch.setattr("app.agent.calendar_agent.load_settings", lambda: MockSettings())
    monkeypatch.setattr("app.agent.calendar_agent.ChatOpenAI", MockLLM)
    monkeypatch.setattr("app.agent.calendar_agent.create_agent", mock_create_agent)

    agent = CalendarAgent()

    assert check_conflicts_tool in agent.tools
    assert "Always run conflict check before creating or rescheduling events." in captured["system_prompt"]
