from abc import abstractmethod
from core.remote import RemoteObject, Remote


# Define interface
class CalcService(Remote):
    @abstractmethod
    def add(self, a: float, b: float) -> float:
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
    def __init__(self):
        super().__init__()

    def add(self, a: float, b: float) -> float:
        return a + b

    def sub(self, a: float, b: float) -> float:
        return a - b

    def mul(self, a: float, b: float) -> float:
        return a * b

    def div(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b
