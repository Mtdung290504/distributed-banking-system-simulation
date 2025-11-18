import xmlrpc.server
from framework.server import skeleton
from interfaces.calculator_service import CalculatorInterface


class CalculatorService(CalculatorInterface):
    """Implementation thuần túy - CHỈ business logic!"""

    def add(self, a: float, b: float) -> float:
        return a + b

    def multiply(self, a: float, b: float) -> float:
        return a * b


if __name__ == "__main__":
    # Truyền class vào skeleton - framework tự tạo instance và wrap
    calc_service = skeleton(CalculatorService, CalculatorInterface)

    # Register vào XML-RPC server
    server = xmlrpc.server.SimpleXMLRPCServer(("127.0.0.1", 8000))
    server.register_instance(calc_service)

    print("Server đang chạy tại http://127.0.0.1:8000")
    server.serve_forever()
