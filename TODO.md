
  Tool boundaries (what exists vs what you add)

  - Keep: create_event_tool(title, start, end)
  - Add: check_conflicts_tool(start, end, buffer_minutes=0, include_all_day=true)
      - Uses GoogleCalendarClient.list_from_to(time_min, time_max) and filters overlaps.
      - Returns a structured summary: conflict_count, conflicts[] (id, summary, start, end,
        is_all_day, status/transparent), and window info.
  - Optional add: suggest_slots_tool(duration_minutes, window_start, window_end, limit=3,
    buffer_minutes=0)
      - Uses the same list_from_to and computes gaps; returns 2–3 candidate start/end pairs.

  Agent policy (what the agent must do)

  - Before calling create_event_tool, the agent must call check_conflicts_tool with the
    proposed start/end.
  - If conflict_count == 0: proceed to create_event_tool.
  - If conflict_count > 0:
      - Ask a follow‑up question unless the user explicitly said “book anyway / override
        conflicts.”
      - Offer up to 3 alternative slots (either using suggest_slots_tool or a simple follow‑up
        that asks for a new time).
  - For ambiguous time or timezone: ask clarifying question before conflict check.

  Prompt changes (app/agent/prompts.py)
  Add a short “policy” block to the system prompt:

  - “Always run conflict check before creating or rescheduling events.”
  - “If conflicts exist, summarize the conflicts and ask to reschedule or confirm override.”
  - “If user says ‘book anyway’, proceed and mention the conflict count.”
  - “If time is ambiguous, ask a question instead of guessing.”

  Example wording (conceptual):

  - “Preflight: use check_conflicts_tool before create_event_tool or any update tool.”
  - “If conflicts > 0: ask user to pick a new time or confirm override.”
  - “Only create after confirmation when conflicts exist.”

  Agent wiring (app/agent/calendar_agent.py)

  - Add the new tool(s) to self.tools, but leave the create/delete/list logic intact.
  - The core behavior change comes from the system prompt + tool availability.

  Behavior examples (how it would feel)

  - User: “Schedule a team sync tomorrow 10–11.”
      - Agent: checks conflicts → “You have 2 conflicts at 10:30–11:00 and 11:45–12:15. Want
        me to suggest new times or book anyway?”
  - User: “Book anyway.”
      - Agent: proceeds to create, with a warning.