from rmi_framework.v2 import RemoteObject
from shared.interfaces.client import PingCallback
from shared.utils import current_ms_timestamp


# Implementation
class PingCallbackImpl(RemoteObject, PingCallback):
    def __init__(self):
        super().__init__()

    def ping(self, timestamp: int) -> int:
        return current_ms_timestamp() - timestamp
