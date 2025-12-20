from rmi_framework.v2 import RemoteObject
from shared.interfaces.client import PingCallback, SuccessCallback

from shared.utils import now


class PingCallbackImpl(RemoteObject, PingCallback):
    def __init__(self):
        super().__init__()

    def ping(self, timestamp: int) -> int:
        return now() - timestamp


class SuccessCallbackImpl(RemoteObject, SuccessCallback):
    def __init__(self):
        super().__init__()

    def notify(self, message: str):
        return print("Server success message:", message)
