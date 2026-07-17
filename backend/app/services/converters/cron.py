from __future__ import annotations

from datetime import datetime, timezone

from croniter import CroniterBadCronError, croniter

from app.core.errors import AppError

_FIELD_NAMES = ["minute", "hour", "day of month", "month", "day of week"]


def parse_cron(expression: str, count: int = 5) -> dict:
    expression = expression.strip()
    if not croniter.is_valid(expression):
        raise AppError("Invalid cron expression")

    try:
        base = datetime.now(timezone.utc)
        it = croniter(expression, base)
        next_runs = [it.get_next(datetime).isoformat() for _ in range(count)]
    except CroniterBadCronError as exc:
        raise AppError(f"Invalid cron expression: {exc}") from exc

    fields = expression.split()
    description = ", ".join(f"{name}={value}" for name, value in zip(_FIELD_NAMES, fields))

    return {"description": description, "next_runs": next_runs}
