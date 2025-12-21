from rmi_framework.v2 import RemoteObject
from shared.interfaces.client import PingCallback, SuccessCallback

from shared.utils import now

from typing import Literal, Callable


class PingCallbackImpl(RemoteObject, PingCallback):
    def __init__(self):
        super().__init__()

    def ping(self, timestamp: int) -> int:
        return now() - timestamp


TypeLiteral = Literal["success", "error", "info"]


class SuccessCallbackImpl(RemoteObject, SuccessCallback):
    def __init__(
        self,
        notify_handler: Callable[[str, TypeLiteral], None] | None = None,
    ):
        super().__init__()
        self.notify_handler = notify_handler

    def notify(self, message: str, type: TypeLiteral = "info"):
        if self.notify_handler:
            return self.notify_handler(message, type)

        return print(f"[{type}] Server message:", message)
