# Server side
from core.registry import LocateRegistry
from examples.services.auth_service import AuthServiceImpl
from examples.services.calc_service import CalcServiceImpl

# Create service instances
auth_service = AuthServiceImpl(
    {"alice": "password123", "bob": "securepass", "dung": "123456"}
)
calc_service = CalcServiceImpl(auth_service)

local_registry = LocateRegistry.createRegistry(29054)

# Bind services
local_registry.bind("auth", auth_service)
local_registry.bind("calc", calc_service)

local_registry.listen(background=True)
input("Press Enter to stop the server...")
