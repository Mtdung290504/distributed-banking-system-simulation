from abc import abstractmethod

from rmi_framework.v2 import Remote

from .client import PingCallback

from ..models.server import LoginResult


class AuthService(Remote):
    @abstractmethod
    def login(
        self, username: str, password: str, callback: PingCallback
    ) -> LoginResult:
        pass

    @abstractmethod
    def logout(self, session_id: str):
        pass
