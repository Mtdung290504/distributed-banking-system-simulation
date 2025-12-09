from typing import TypedDict


class LoginResult(TypedDict):
    success: bool
    message: str
    session_id: str | None
