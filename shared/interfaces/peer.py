from abc import abstractmethod
from typing import List
from shared.models.server import ATMCommand

from rmi_framework.v2 import Remote


class PeerService(Remote):
    @abstractmethod
    def request_token(self) -> bool:
        pass

    @abstractmethod
    def receive_sync(self, logs: List[ATMCommand], pass_token: bool) -> bool:
        pass
