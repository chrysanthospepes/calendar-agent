from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from app.tools.create_event import create_event_tool
from app.tools.list_events import list_next_events_tool, list_today_events_tool

from app.config.settings import load_settings

from app.agent.prompts import SYSTEM_PROMPT

class CalendarAgent:
    def __init__(self):
        self._settings = load_settings()
        self.llm = ChatOpenAI(model=self._settings.openai_model, temperature=0, api_key=self._settings.openai_api)
        self.tools = [create_event_tool, list_next_events_tool, list_today_events_tool]
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT
            )
        
    def run(self, user_prompt: str) -> str:
        result = self.agent.invoke({"messages": [("user", user_prompt)]})
        return result["messages"][-1].content