from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None
    total: Optional[int] = None


def ok(data: Any = None, total: Optional[int] = None, message: str = "success") -> ApiResponse:
    return ApiResponse(code=200, message=message, data=data, total=total)
