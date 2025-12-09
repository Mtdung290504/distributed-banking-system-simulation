# Server side
from core.registry import LocateRegistry
from examples.services.auth_service import AuthServiceImpl
from examples.services.calc_service import CalcServiceImpl

auth_service_db = {"alice": "password123", "bob": "securepass", "dung": "123456"}

registry = LocateRegistry.createRegistry(29054)
registry.listen(background=True)

auth_service = AuthServiceImpl(auth_service_db)
calc_service = CalcServiceImpl(auth_service)

# Bind services
registry.bind("auth", auth_service)
registry.bind("calc", calc_service)
print("Server is running and services are bound.")
input("Press Enter to stop the server...")
