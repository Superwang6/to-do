from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, field_validator, model_validator

from src.schema.common import PageRequest, TimeRangeRequest


class Frequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class RecurrenceRule(BaseModel):
    frequency: Frequency
    interval: int = 1
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    month_of_year: Optional[int] = None
    time_of_day: Optional[str] = None  # "HH:MM" 24h format, e.g. "14:00"

    @field_validator("interval")
    @classmethod
    def interval_ge_1(cls, v):
        if v < 1:
            raise ValueError("interval must be >= 1")
        return v

    @field_validator("days_of_week")
    @classmethod
    def days_of_week_range(cls, v):
        if v is not None:
            for d in v:
                if d < 1 or d > 7:
                    raise ValueError("days_of_week values must be 1-7")
        return v

    @field_validator("day_of_month")
    @classmethod
    def day_of_month_range(cls, v):
        if v is not None and (v < 1 or v > 28):
            raise ValueError("day_of_month must be 1-28")
        return v

    @field_validator("month_of_year")
    @classmethod
    def month_of_year_range(cls, v):
        if v is not None and (v < 1 or v > 12):
            raise ValueError("month_of_year must be 1-12")
        return v

    @model_validator(mode="after")
    def check_frequency_fields(self):
        if self.frequency == Frequency.weekly and not self.days_of_week:
            raise ValueError("days_of_week is required for weekly frequency")
        return self


class TodoListRequest(BaseModel):
    """POST /api/todos/list request body."""
    page: PageRequest = PageRequest()
    time_range: Optional[TimeRangeRequest] = None
    type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    keyword: Optional[str] = None


class GroupedTodoResponse(BaseModel):
    """Grouped active todos: today / recurring / once."""
    today: list[TodoResponse] = []
    recurring: list[TodoResponse] = []
    once: list[TodoResponse] = []
    completed_count: int = 0


class CompletedListResponse(BaseModel):
    """Completed todos list."""
    completed: list[TodoResponse] = []
    total: int = 0


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"
    type: str = "once"
    recurrence_rule: Optional[RecurrenceRule] = None

    @model_validator(mode="after")
    def check_type_rule_consistency(self):
        if self.type == "recurring" and self.recurrence_rule is None:
            raise ValueError("recurrence_rule is required when type is recurring")
        if self.type == "once" and self.recurrence_rule is not None:
            raise ValueError("recurrence_rule must be empty when type is once")
        return self


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    recurrence_rule: Optional[RecurrenceRule] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str
    status: str
    type: str = "once"
    recurrence_rule: Optional[dict] = None
    recurring_template_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VoiceUploadResponse(BaseModel):
    text: str
    todo: Optional["TodoResponse"] = None
