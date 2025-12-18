# Server side

from rmi_framework.v2 import LocateRegistry
from .database.main import Database
from .services.auth_service import AuthServiceImpl

database = Database("127.0.0.1", "root", "123456", "atm_db_s1")
local_registry = LocateRegistry.local_registry(29054)

# Create service instances
auth_service = AuthServiceImpl(local_registry, database)
# calc_service = CalcServiceImpl(auth_service)

# Bind services
local_registry.bind("auth", auth_service)
# local_registry.bind("calc", calc_service)

local_registry.listen(background=True)
input("Press Enter to stop the server...")
