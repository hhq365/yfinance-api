from typing import Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    code: int
    message: str
    data: Any


def success(data: Any = None):
    return {
        "code": 0,
        "message": "success",
        "data": data
    }


def error(message: str = "error", code: int = -1):
    return {
        "code": code,
        "message": message,
        "data": None
    }
