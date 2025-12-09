from abc import abstractmethod

from rmi_framework.v2 import Remote

from .client import UserCallback

from ..models.server import LoginResult


class AuthService(Remote):
    @abstractmethod
    def login(
        self, username: str, password: str, callback: UserCallback
    ) -> LoginResult:
        pass
