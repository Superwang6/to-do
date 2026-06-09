from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PageRequest(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=200)


class TimeRangeRequest(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
