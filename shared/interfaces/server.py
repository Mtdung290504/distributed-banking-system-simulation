from abc import abstractmethod

from rmi_framework.v2 import Remote

from .client import SuccessCallback

from ..models.server import LoginResult


class AuthService(Remote):
    @abstractmethod
    def login(
        self, card_number: str, pin: str, callback: SuccessCallback
    ) -> LoginResult:
        pass


class UserService(Remote):
    @abstractmethod
    def message(self, message: str):
        pass

    @abstractmethod
    def logout(self, callback: SuccessCallback):
        pass
