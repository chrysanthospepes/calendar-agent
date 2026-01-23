Calendar Agent
==============

A small CLI that uses an LLM to interpret natural-language scheduling requests
and create or list Google Calendar events via the Google Calendar API.

Features
--------
- Create events from natural-language prompts.
- List upcoming events.
- Uses OAuth for Google Calendar access.

Project Layout
--------------
- `app/main.py`: CLI entry point.
- `app/agent/calendar_agent.py`: LLM + tool wiring.
- `app/tools/create_event.py`: Create-event tool.
- `app/tools/list_events.py`: List-events tool.
- `app/services/google_calendar.py`: Google Calendar API client.
- `app/services/auth/google_oauth.py`: OAuth flow and token handling.

Requirements
------------
- Python 3.10+ recommended.
- A Google Cloud project with Calendar API enabled.
- OAuth desktop app credentials (`credentials.json`).
- OpenAI API key.

Setup
-----
1) Create and activate a virtual environment.
2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Copy `.env.example` to `.env` and update values.

Environment Variables
---------------------
From `.env.example`:

- `OPENAI_API_KEY`: OpenAI API key.
- `OPENAI_MODEL`: Model name (default: `gpt-5-mini`).
- `GOOGLE_CREDENTIALS_FILE`: Path to OAuth client secrets (default: `secrets/credentials.json`).
- `GOOGLE_TOKEN_FILE`: Path to stored OAuth token (default: `secrets/token.json`).
- `GOOGLE_CALENDAR_ID`: Calendar ID (default: `primary`).
- `CALENDAR_TIMEZONE`: Time zone ID (default: `Europe/Athens`).

Google OAuth Notes
------------------
- Place your OAuth client secrets JSON at `secrets/credentials.json` (or update the env var).
- On first run, the app will open a local browser flow and store a token at
  `secrets/token.json`.

Run
---
```bash
python -m app.main
```

Example usage:
```
> Schedule a team meeting on Jan 30 at 10am for 1 hour
> Show my next 3 events
> exit
```

Notes
-----
- The CLI exits when you type `exit`.
- Event times are created using the configured `CALENDAR_TIMEZONE`.
