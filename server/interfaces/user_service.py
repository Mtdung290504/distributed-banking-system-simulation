from abc import ABC, abstractmethod


class UserInterface(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> str:
        pass
