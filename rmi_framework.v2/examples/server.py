# Server side
from core.registry import LocateRegistry
from examples.services.auth_service import AuthServiceImpl

auth_service_db = {
    "alice": "password123",
    "bob": "securepass",
}

registry = LocateRegistry.createRegistry(29054)
auth_service = AuthServiceImpl(auth_service_db)

# Bind services
registry.bind("auth", auth_service)

# Start blocking server
registry.listen()
