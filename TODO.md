Improve:
- Align conflict-check policy with tool docs; prefer a wrapper tool to enforce check-then-create flow.
- Normalize datetimes to configured timezone before creating events; avoid naive ISO strings.
- Standardize tool return shapes (always dicts with errors structured).
- Expand tests for timezone handling, error paths, and conflict-check enforcement.