from net.registry import LocateRegistry, local_registry
from examples.services.auth_service import AuthService
from examples.services.user_callback import UserCallbackImpl


registry = LocateRegistry.createRegistry(("192.168.1.48", 29054))
auth_service = registry.lookup("auth", AuthService)

user_callback = UserCallbackImpl()
auth_service.login("alice", "password123", user_callback)

local_registry.listen()
