import re
from datetime import date, datetime, timedelta
from typing import Optional

WEEKDAY_MAP = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "日": 7,
    "天": 7,
}


class ParserService:
    """Parse transcribed text into structured todo with rule-based + LLM fallback."""

    def parse(self, text: str) -> Optional[dict]:
        todo = self._rule_parse(text)
        if todo is not None and self._is_complete(todo):
            return todo
        return self._llm_fallback(text)

    def _rule_parse(self, text: str) -> Optional[dict]:
        due_date = self._extract_date(text)
        time_of_day = self._extract_time(text)

        # Merge time into due_date
        if due_date and time_of_day:
            dt = datetime.fromisoformat(due_date)
            h, m = map(int, time_of_day.split(":"))
            due_date = dt.replace(hour=h, minute=m).isoformat()

        priority = self._extract_priority(text)
        title = self._clean_title(text)
        if not title:
            return None
        recurrence = self._extract_recurrence(text)
        if recurrence and time_of_day:
            recurrence["time_of_day"] = time_of_day
        result = {
            "title": title,
            "description": None,
            "due_date": due_date,
            "priority": priority,
        }
        if recurrence:
            result["type"] = "recurring"
            result["recurrence_rule"] = recurrence
        return result

    def _extract_time(self, text: str) -> Optional[str]:
        """Extract time of day, return 'HH:MM' or None."""
        # Direct 24h: 14:00, 14：00
        m = re.search(r"(\d{1,2})[：:](\d{2})", text)
        if m:
            h, minute = int(m.group(1)), int(m.group(2))
            if 0 <= h <= 23 and 0 <= minute <= 59:
                return f"{h:02d}:{minute:02d}"

        # Chinese: 下午2点, 上午10点半, 晚上8点, 3点
        m = re.search(
            r"(凌晨|早上|早晨|上午|中午|下午|晚上)?\s*(\d{1,2})\s*点\s*(半|(\d{1,2})分)?",
            text,
        )
        if m:
            period = m.group(1) or ""
            hour = int(m.group(2))
            half = m.group(3) == "半"
            minute_str = m.group(4)
            minute = 30 if half else (int(minute_str) if minute_str else 0)

            if "下午" in period or "晚上" in period:
                if hour != 12:
                    hour += 12
            elif "上午" in period or "早上" in period or "早晨" in period:
                if hour == 12:
                    hour = 0
            elif "中午" in period:
                if hour != 12:
                    hour += 12
            elif "凌晨" in period:
                pass
            else:
                # Bare number: 3点 → ambiguous, assume 15:00 if <= 6
                if hour <= 6:
                    hour += 12

            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"

        return None

    def _extract_recurrence(self, text: str) -> Optional[dict]:
        """Detect recurring patterns like 每天/每周五/每月15号."""
        # 每天 / 每N天
        m = re.search(r"每(\d*)\s*天", text)
        if m:
            interval = int(m.group(1)) if m.group(1) else 1
            return {"frequency": "daily", "interval": interval}

        # 每周X, X, X
        m = re.search(r"每周\s*([一二三四五六日天])", text)
        if m:
            weekday = WEEKDAY_MAP.get(m.group(1), 1)
            return {"frequency": "weekly", "interval": 1, "days_of_week": [weekday]}

        # 每N周
        m = re.search(r"每(\d+)\s*周", text)
        if m:
            interval = int(m.group(1))
            days_match = re.findall(r"[一二三四五六日天]", text)
            days_of_week = [WEEKDAY_MAP[d] for d in days_match if d in WEEKDAY_MAP]
            if not days_of_week:
                days_of_week = [1]
            return {"frequency": "weekly", "interval": interval, "days_of_week": sorted(days_of_week)}

        # 每月N号 / 每N月N号
        m = re.search(r"每月\s*(\d{1,2})\s*[号日]", text)
        if m:
            day = min(int(m.group(1)), 28)
            return {"frequency": "monthly", "interval": 1, "day_of_month": day}

        # 每年N月N日
        m = re.search(r"每年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]", text)
        if m:
            month = int(m.group(1))
            day = min(int(m.group(2)), 28)
            return {"frequency": "yearly", "interval": 1, "month_of_year": month, "day_of_month": day}

        return None

    def _is_complete(self, todo: dict) -> bool:
        return bool(todo.get("title"))

    def _llm_fallback(self, text: str) -> Optional[dict]:
        return {"title": text, "description": None, "due_date": None, "priority": "medium"}

    def _extract_date(self, text: str) -> Optional[str]:
        today = date.today()
        patterns = [
            (r"后天", lambda _: today + timedelta(days=2)),
            (r"明天|明日", lambda _: today + timedelta(days=1)),
            (r"今天|今日", lambda _: today),
            (r"大后天", lambda _: today + timedelta(days=3)),
            (r"下个月(\d{1,2})[号日]", lambda m: self._next_month_day(today, int(m.group(1)))),
            (r"下周([一二三四五六日天])", lambda m: self._next_weekday(WEEKDAY_MAP.get(m.group(1), 1))),
            (r"下个月", lambda _: self._next_month(today)),
            (r"(\d{1,2})月(\d{1,2})[日号]?", lambda m: self._month_day(today, int(m.group(1)), int(m.group(2)))),
        ]
        for pattern, fn in patterns:
            match = re.search(pattern, text)
            if match:
                dt = fn(match)
                return datetime.combine(dt, datetime.min.time()).isoformat()
        return None

    def _extract_priority(self, text: str) -> str:
        if re.search(r"重要|紧急|加急|high|urgent", text, re.IGNORECASE):
            return "high"
        if re.search(r"低优先级|一般|随便|low|minor", text, re.IGNORECASE):
            return "low"
        return "medium"

    def _clean_title(self, text: str) -> str:
        text = re.sub(
            r"(今天|明天|后天|大后天|下个月\d{1,2}[号日]|下周[一二三四五六日天]|下个月|"
            r"\d{1,2}月\d{1,2}[日号]?|"
            r"早上|上午|中午|下午|晚上|凌晨|早晨|"
            r"\d{1,2}[：:]\d{2}|\d{1,2}点[半]?|\d{1,2}点\d{1,2}分|"
            r"重要|紧急|加急|低优先级|一般|随便)",
            "",
            text,
        )
        text = re.sub(r"[，。！？\s,\.!?\s]+", " ", text).strip()
        return text if text else None

    @staticmethod
    def _next_weekday(weekday: int) -> date:
        today = date.today()
        days_ahead = weekday - today.isoweekday()
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days=days_ahead)

    @staticmethod
    def _next_month(today: date) -> date:
        month = today.month + 1
        year = today.year
        if month > 12:
            month = 1
            year += 1
        return date(year, month, min(today.day, 28))

    @staticmethod
    def _next_month_day(today: date, day: int) -> date:
        month = today.month + 1
        year = today.year
        if month > 12:
            month = 1
            year += 1
        return date(year, month, min(day, 28))

    @staticmethod
    def _month_day(today: date, month: int, day: int) -> date:
        year = today.year
        try:
            target = date(year, month, day)
        except ValueError:
            target = date(year, month, 28)
        if target < today:
            try:
                target = date(year + 1, month, day)
            except ValueError:
                target = date(year + 1, month, 28)
        return target
