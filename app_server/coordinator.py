import time
import threading
from typing import List

from rmi_framework.v2 import LocateRegistry

from .command_queue import CommandQueue
from .command_executor import CommandExecutor
from .event_emitter import EventEmitter
from shared.models.server import ATMCommand
from shared.interfaces.peer import PeerService
from .config import PEER_ID, get_peer_config


class Coordinator:
    def __init__(
        self,
        command_queue: CommandQueue,
        command_executor: CommandExecutor,
        event_emitter: EventEmitter,
    ):
        self.queue = command_queue
        self.executor = command_executor
        self.emitter = event_emitter

        peer_conf = get_peer_config()

        # Lấy Registry của thằng kia
        self.peer_registry = LocateRegistry.get_registry(
            address=peer_conf["host"], port=peer_conf["port"]
        )
        self.peer_service_proxy = self.peer_registry.lookup("peer", PeerService)

        # State
        self.has_token = False
        self.peer_demanding = False
        self.pending_sync_logs: List[ATMCommand] = []

        self.token_event = threading.Event()
        self.lock = threading.Lock()

        self._initial_token_check()
        threading.Thread(target=self._worker_loop, daemon=True).start()

    def _initial_token_check(self):
        # Quy ước: Server ID "1" cầm token trước
        if PEER_ID == "1":
            self.has_token = True
            self.token_event.set()
            print(">> [STARTUP] I am Server 1. Holding Token.")
        else:
            self.has_token = False
            print(f">> [STARTUP] I am Server {PEER_ID}. Waiting.")

    def set_peer_demanding(self, status: bool):
        self.peer_demanding = status

    def accept_token(self):
        with self.lock:
            self.has_token = True
            self.token_event.set()

    def handle_incoming_sync(self, logs: List[ATMCommand]):
        self.emitter.emit(self.executor.exec_direct, [logs])

    def _worker_loop(self):
        while True:
            if not self.has_token:
                if not self.queue.is_empty():
                    self._request_token_from_peer()
                self.token_event.wait()

            if self.has_token:
                # 1. Yield nếu rỗng và bị đòi
                if self.queue.is_empty() and self.peer_demanding:
                    self._sync_and_pass_token()
                    continue

                # 2. Process Queue
                if not self.queue.is_empty():
                    commands = self.queue.get_all()
                    executed_cmds = self.executor.exec_direct(commands)
                    self.pending_sync_logs.extend(executed_cmds)

                    if self.peer_demanding:
                        self._sync_and_pass_token()
                else:
                    time.sleep(0.1)

    def _request_token_from_peer(self):
        try:
            # Gọi phương thức interface chuẩn
            self.peer_service_proxy.request_token()
        except Exception as e:
            print(f"Error requesting token (Peer might be down): {e}")
            time.sleep(1)

    def _sync_and_pass_token(self):
        print(f">> [PASS] Syncing {len(self.pending_sync_logs)} logs...")
        try:
            logs_to_send = self.pending_sync_logs[:]

            # Gọi phương thức interface chuẩn
            self.peer_service_proxy.receive_sync(logs_to_send, True)

            with self.lock:
                self.has_token = False
                self.peer_demanding = False
                self.pending_sync_logs = []
                self.token_event.clear()

            print(">> [INFO] Token passed successfully.")

        except Exception as e:
            print(f"Error passing token: {e}")
            self.peer_demanding = False
