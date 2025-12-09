from abc import abstractmethod
from core.remote import RemoteObject, Remote

from examples.services.auth_service import AuthServiceImpl


# Define interface
class CalcService(Remote):
    @abstractmethod
    def add(self, session_id: str, a: float, b: float) -> float:
        pass

    @abstractmethod
    def sub(self, a: float, b: float) -> float:
        pass

    @abstractmethod
    def mul(self, a: float, b: float) -> float:
        pass

    @abstractmethod
    def div(self, a: float, b: float) -> float:
        pass


# Implementation
class CalcServiceImpl(RemoteObject, CalcService):
    def __init__(self, req: AuthServiceImpl):
        super().__init__()
        self.req = req

    def add(self, session_id: str, a: float, b: float) -> float:
        history = self.req.sessions[session_id]["history"]
        history.append({"method": "add", "params": (a, b)})

        if len(history) % 3 == 0:
            print(history)

        return a + b

    def sub(self, a: float, b: float) -> float:
        return a - b

    def mul(self, a: float, b: float) -> float:
        return a * b

    def div(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b
