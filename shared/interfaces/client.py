from abc import abstractmethod

from rmi_framework.v2 import Remote


# Define interface
class PingCallback(Remote):
    @abstractmethod
    def ping(self, timestamp: int) -> int:
        pass


class SuccessCallback(Remote):
    @abstractmethod
    def notify(self, message: str):
        pass
