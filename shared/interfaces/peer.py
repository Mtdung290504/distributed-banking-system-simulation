from abc import ABC, abstractmethod
from typing import List
from shared.models.server import ATMCommand


class PeerService(ABC):
    @abstractmethod
    def request_token(self) -> bool:
        pass

    @abstractmethod
    def receive_sync(self, logs: List[ATMCommand], pass_token: bool) -> bool:
        pass
