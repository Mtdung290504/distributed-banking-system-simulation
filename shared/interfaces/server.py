from abc import abstractmethod
from typing import List

from rmi_framework.v2 import Remote

from .client import SuccessCallback

from ..models.server import LoginResult, TransactionData, UserData


class AuthService(Remote):
    @abstractmethod
    def login(
        self, card_number: str, pin: str, callback: SuccessCallback
    ) -> LoginResult:
        pass


class UserService(Remote):
    @abstractmethod
    def get_balance(self) -> int:
        pass

    @abstractmethod
    def get_transaction_history(self) -> List[TransactionData]:
        pass

    @abstractmethod
    def get_info(self) -> UserData:
        pass

    @abstractmethod
    def change_pin(self, new_pin: str, callback: SuccessCallback):
        pass

    @abstractmethod
    def deposit(self, amount: int, callback: SuccessCallback):
        pass

    @abstractmethod
    def withdraw(self, amount: int, callback: SuccessCallback):
        pass

    @abstractmethod
    def transfer(self, to_card: str, amount: int, callback: SuccessCallback):
        pass

    @abstractmethod
    def logout(self, callback: SuccessCallback):
        pass
