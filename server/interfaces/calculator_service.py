from abc import ABC, abstractmethod


class CalculatorInterface(ABC):
    """Interface chung cho RPC service calculator."""

    @abstractmethod
    def add(self, a: float, b: float) -> float:
        """Cộng hai số."""
        pass

    @abstractmethod
    def multiply(self, a: float, b: float) -> float:
        """Nhân hai số."""
        pass
