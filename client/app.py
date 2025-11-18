import xmlrpc.client
import rmi_framework.client as RMIClient

from interfaces.calculator_service import CalculatorInterface
from interfaces.user_service import UserInterface

proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:8000/")

# Tạo stub cho từng service với tên tương ứng
calc = RMIClient.lookup(proxy, ("calculator", CalculatorInterface))
user_service = RMIClient.lookup(proxy, ("user", UserInterface))

# Sử dụng:

result = calc.add(5.0, 3.0)
print("Service calculator result:", result)

try:
    user = user_service.get_user(123)
    print("Service user result:", user)
except xmlrpc.client.Fault as error:
    print(error.faultString)
