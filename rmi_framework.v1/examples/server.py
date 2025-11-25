# Server side
from net.registry import local_registry
from examples.services.auth_service import AuthServiceImpl

auth_service_db = {
    "alice": "password123",
    "bob": "securepass",
}

auth_service = AuthServiceImpl(auth_service_db)

# Bind services
local_registry.bind("auth", auth_service)

# Start blocking server
local_registry.listen()
