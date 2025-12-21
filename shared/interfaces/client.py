from abc import abstractmethod

from rmi_framework.v2 import Remote
from typing import Literal


# Define interface
class PingCallback(Remote):
    @abstractmethod
    def ping(self, timestamp: int) -> int:
        pass


class SuccessCallback(Remote):
    @abstractmethod
    def notify(self, message: str, type: Literal["success", "error", "info"] = "info"):
        pass
