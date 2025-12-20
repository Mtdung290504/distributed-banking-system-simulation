# Server side

from rmi_framework.v2 import LocateRegistry

from .database.main import Database
from .command_queue import CommandQueue
from .command_executor import CommandExecutor
from .event_emitter import EventEmitter

from .services.auth_service import AuthServiceImpl
from .config import get_current_config, PEER_ID
from .services.peer_service import PeerServiceImpl
from .coordinator import Coordinator

# Lấy config động
current_conf = get_current_config()
MY_PORT = current_conf["port"]

database = Database("127.0.0.1", "root", "123456", f"atm_db_s{PEER_ID}")
command_queue = CommandQueue()
event_emitter = EventEmitter()
command_executor = CommandExecutor(command_queue, database.writer())

# Coordinator
coordinator = Coordinator(command_queue, command_executor, event_emitter)

local_registry = LocateRegistry.local_registry(MY_PORT)

auth_service = AuthServiceImpl(local_registry, database, command_queue)
peer_service = PeerServiceImpl(coordinator)

local_registry.bind("auth", auth_service)
local_registry.bind("peer", peer_service)

print(f"Server {PEER_ID} running on port {MY_PORT}...")
local_registry.listen(background=True)

while command := input("\nEnter command or press Enter to exit...: "):
    if "list" in command:
        print(command_queue.get_all())
    elif "exec" in command:
        print(command_executor.exec())
