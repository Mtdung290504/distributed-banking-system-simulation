import xmlrpc.server
import rmi_framework.server as RMIServer

from interfaces.calculator_service import CalculatorInterface
from interfaces.user_service import UserInterface


class CalculatorImpl(CalculatorInterface):
    def add(self, a: float, b: float) -> float:
        return a + b

    def multiply(self, a: float, b: float) -> float:
        return a * b


class UserServiceImpl(UserInterface):
    def get_user(self, user_id: int) -> str:
        return f"User {user_id}"


if __name__ == "__main__":
    # Tạo registry
    registry = RMIServer.Registry()

    # Đăng ký services
    registry.rebind(
        "calculator", RMIServer.skeleton(CalculatorImpl, CalculatorInterface)()
    )
    registry.rebind("user", RMIServer.skeleton(UserServiceImpl, UserInterface)())

    # Serve
    RMIServer.listen(
        xmlrpc.server.SimpleXMLRPCServer(("127.0.0.1", 8000)),
        registry,
        lambda: print("Server chạy tại http://127.0.0.1:8000"),
    )
