from __future__ import annotations


def ok(data: dict | None = None) -> dict:
    return {
        "ok": True,
        "data": data or {},
        "error": None,
    }


def err(
    message: str,
    *,
    status: int | str | None = None,
    reason: str | None = None,
    code: str | None = None,
) -> dict:
    return {
        "ok": False,
        "data": None,
        "error": {
            "message": message,
            "status": status,
            "reason": reason,
            "code": code,
        },
    }
