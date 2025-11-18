import xmlrpc.client
import framework.client

from interfaces.calculator_service import CalculatorInterface

proxy = xmlrpc.client.ServerProxy("http://127.0.0.1:8000/")
calc = framework.client.stub(proxy, CalculatorInterface)

result = calc.add(5.0, 3.0)
result2 = calc.multiply(2.5, 4.0)
# calc.nonexistent()  # Runtime AttributeError

print(result, result2)
