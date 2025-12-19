# Server side

from rmi_framework.v2 import LocateRegistry

from .database.main import Database
from .command_queue import CommandQueue
from .command_executor import CommandExecutor
from .event_emitter import EventEmitter

from .services.auth_service import AuthServiceImpl

database = Database("127.0.0.1", "root", "123456", "atm_db_s1")
command_queue = CommandQueue()
command_executor = CommandExecutor(command_queue, database.writer())
event_emitter = EventEmitter()

local_registry = LocateRegistry.local_registry(29054)

# Create service instances
auth_service = AuthServiceImpl(local_registry, database, command_queue)
# calc_service = CalcServiceImpl(auth_service)

# Bind services
local_registry.bind("auth", auth_service)
# local_registry.bind("calc", calc_service)

local_registry.listen(background=True)
while command := input("\nEnter command or press Enter to exit...: "):
    if "list" in command:
        print(command_queue.get_all())
    elif "exec" in command:
        print(command_executor.exec())
