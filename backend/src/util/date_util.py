import calendar
from datetime import datetime, timedelta


def _apply_time(dt: datetime, time_of_day: str | None) -> datetime:
    """Apply HH:MM time to a datetime. Returns dt with time set."""
    if not time_of_day:
        return dt
    h, m = map(int, time_of_day.split(":"))
    return dt.replace(hour=h, minute=m, second=0, microsecond=0)


def calculate_first_due_date(rule: dict, time_of_day: str | None = None) -> datetime:
    """Calculate the first due date from now based on recurrence rule.

    If time_of_day is set: if today's occurrence time hasn't passed,
    return today at that time; otherwise return the next occurrence.
    """
    now = datetime.now()
    frequency = rule["frequency"]
    interval = rule.get("interval", 1)

    if frequency == "daily":
        candidate = _apply_time(now, time_of_day) if time_of_day else now + timedelta(days=interval)
        if time_of_day and candidate <= now:
            candidate += timedelta(days=interval)
        elif not time_of_day:
            candidate = now + timedelta(days=interval)
        return candidate

    if frequency == "weekly":
        days_of_week = rule.get("days_of_week", [])
        if not days_of_week:
            candidate = now + timedelta(weeks=interval)
            return _apply_time(candidate, time_of_day) if time_of_day else candidate

        current_dow = now.isoweekday()
        sorted_days = sorted(days_of_week)
        next_day = None
        for d in sorted_days:
            if d >= current_dow:
                next_day = d
                break
        if next_day is not None:
            offset = next_day - current_dow
            if offset == 0 and time_of_day:
                candidate = _apply_time(now, time_of_day)
                if candidate > now:
                    return candidate
                # Time already passed today, find next matching day
                next_day = None
                for d in sorted_days:
                    if d > current_dow:
                        next_day = d
                        break
                if next_day is not None:
                    offset = next_day - current_dow
                else:
                    offset = 7 - current_dow + sorted_days[0] + (interval - 1) * 7
            elif offset == 0:
                offset = 7
            offset += (interval - 1) * 7
        else:
            offset = 7 - current_dow + sorted_days[0] + (interval - 1) * 7

        candidate = now + timedelta(days=offset)
        return _apply_time(candidate, time_of_day) if time_of_day else candidate

    if frequency == "monthly":
        day_of_month = rule.get("day_of_month", now.day)
        target_year = now.year
        target_month = now.month
        last_day = calendar.monthrange(target_year, target_month)[1]
        actual_day = min(day_of_month, last_day)

        if actual_day == now.day and time_of_day:
            candidate = _apply_time(now, time_of_day)
            if candidate > now:
                return candidate

        if actual_day <= now.day:
            target_month += interval
            while target_month > 12:
                target_year += 1
                target_month -= 12
            last_day = calendar.monthrange(target_year, target_month)[1]
            actual_day = min(day_of_month, last_day)

        candidate = now.replace(year=target_year, month=target_month, day=actual_day)
        return _apply_time(candidate, time_of_day) if time_of_day else candidate

    if frequency == "yearly":
        month_of_year = rule.get("month_of_year", now.month)
        day_of_month = rule.get("day_of_month", now.day)
        target_year = now.year
        last_day = calendar.monthrange(target_year, month_of_year)[1]
        actual_day = min(day_of_month, last_day)

        if month_of_year == now.month and actual_day == now.day and time_of_day:
            candidate = _apply_time(now, time_of_day)
            if candidate > now:
                return candidate

        candidate = now.replace(year=target_year, month=month_of_year, day=actual_day)
        if candidate <= now:
            target_year += interval
            last_day = calendar.monthrange(target_year, month_of_year)[1]
            actual_day = min(day_of_month, last_day)
            candidate = now.replace(year=target_year, month=month_of_year, day=actual_day)

        return _apply_time(candidate, time_of_day) if time_of_day else candidate

    return _apply_time(now, time_of_day) if time_of_day else now


def calculate_next_due_date(current_due: datetime, rule: dict) -> datetime:
    """Calculate the next due date based on recurrence rule. Preserves time_of_day."""
    frequency = rule["frequency"]
    interval = rule.get("interval", 1)
    time_of_day = rule.get("time_of_day")

    if frequency == "daily":
        candidate = current_due + timedelta(days=interval)
        return _apply_time(candidate, time_of_day) if time_of_day else candidate

    if frequency == "weekly":
        days_of_week = rule.get("days_of_week", [])
        if not days_of_week:
            candidate = current_due + timedelta(weeks=interval)
            return _apply_time(candidate, time_of_day) if time_of_day else candidate

        current_dow = current_due.isoweekday()
        sorted_days = sorted(days_of_week)
        next_day = None
        for d in sorted_days:
            if d > current_dow:
                next_day = d
                break
        if next_day is not None:
            offset = next_day - current_dow
        else:
            offset = 7 - current_dow + sorted_days[0]
        offset += (interval - 1) * 7
        candidate = current_due + timedelta(days=offset)
        return _apply_time(candidate, time_of_day) if time_of_day else candidate

    if frequency == "monthly":
        day_of_month = rule.get("day_of_month", current_due.day)
        year = current_due.year
        month = current_due.month + interval
        while month > 12:
            year += 1
            month -= 12
        last_day = calendar.monthrange(year, month)[1]
        actual_day = min(day_of_month, last_day)
        candidate = current_due.replace(year=year, month=month, day=actual_day)
        return _apply_time(candidate, time_of_day) if time_of_day else candidate

    if frequency == "yearly":
        month_of_year = rule.get("month_of_year", current_due.month)
        day_of_month = rule.get("day_of_month", current_due.day)
        year = current_due.year + interval
        last_day = calendar.monthrange(year, month_of_year)[1]
        actual_day = min(day_of_month, last_day)
        candidate = current_due.replace(year=year, month=month_of_year, day=actual_day)
        return _apply_time(candidate, time_of_day) if time_of_day else candidate

    return _apply_time(current_due, time_of_day) if time_of_day else current_due
