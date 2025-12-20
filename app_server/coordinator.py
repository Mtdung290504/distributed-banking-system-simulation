import threading
import socket
from typing import List

from rmi_framework.v2 import LocateRegistry

from .command_queue import CommandQueue
from .command_executor import CommandExecutor
from .event_emitter import EventEmitter
from .config import PEER_ID, get_peer_config

from shared.models.server import ATMCommand
from shared.interfaces.server import PeerService


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

        # Lookup peer service
        self.peer_registry = LocateRegistry.get_registry(
            address=peer_conf["host"], port=peer_conf["port"]
        )
        self.peer_service_proxy = self.peer_registry.lookup("peer", PeerService)

        # State
        self.has_token = False
        self.peer_demanding = False
        self.pending_sync_logs: List[ATMCommand] = []

        self.lock = threading.Lock()
        self.token_event = threading.Event()

        self._initial_token_check()
        threading.Thread(target=self._worker_loop, daemon=True).start()

    def _initial_token_check(self):
        if PEER_ID == 1:
            with self.lock:
                self.has_token = True
            self.token_event.set()
            print(">> [STARTUP] I am Server 1. Holding Token.")
        else:
            with self.lock:
                self.has_token = False
            print(f">> [STARTUP] I am Server {PEER_ID}. Waiting.")

    def _sanitize_logs(self, logs: List[ATMCommand]):
        """
        Làm sạch các command trước khi gửi đi (tránh bị Fault do callback là object)
        Loại bỏ 'success_callback' vì nó là Remote Object không thể serialize qua XML-RPC.
        Tạo bản copy để không ảnh hưởng dữ liệu gốc.
        """
        clean_logs = []

        for cmd in logs:
            # Copy dict để không xóa mất dữ liệu gốc trong RAM
            clean_cmd = cmd.copy()
            if "success_callback" in clean_cmd:
                del clean_cmd["success_callback"]
            clean_logs.append(clean_cmd)

        return clean_logs

    def is_holding_token(self):
        with self.lock:
            return self.has_token

    def set_peer_demanding(self, status: bool):
        """Đánh dấu rằng peer kia đang cần token"""
        with self.lock:
            self.peer_demanding = status

    def accept_token(self):
        """Đánh dấu mình cầm token"""
        with self.lock:
            self.has_token = True
            self.peer_demanding = False
            self.token_event.set()
        print(">> [TOKEN] Received Token from Peer.")

    def handle_incoming_sync(self, logs: List[ATMCommand]):
        self.emitter.emit(self.executor.exec_direct, [logs])

    def _worker_loop(self):
        print(">> [COORDINATOR] Worker started.")
        while True:
            # Ngủ 0.25s để check state liên tục
            self.queue.wait_for_data(timeout=0.25)

            with self.lock:
                am_holding_token = self.has_token
                is_peer_demanding = self.peer_demanding
                is_queue_empty = self.queue.is_empty()

            # 1. KỊCH BẢN: NHƯỜNG TOKEN (Khi rảnh + Bị đòi)
            if am_holding_token and is_peer_demanding and is_queue_empty:
                self._sync_and_pass_token()
                continue

            # 2. KỊCH BẢN: CÓ VIỆC CẦN LÀM
            if not is_queue_empty:
                # Chưa có Token -> Xin
                if not am_holding_token:
                    print(">> [WORKER] Data waiting. Requesting Token...")
                    success = self._request_token_logic()
                    if success:
                        am_holding_token = True
                    else:
                        continue

                # Đã có Token -> Xử lý
                if am_holding_token:
                    commands = self.queue.get_all()
                    # print("Execute:", commands) # Debug

                    if commands:
                        success_cmds = self.executor.exec_direct(commands)
                        with self.lock:
                            self.pending_sync_logs.extend(success_cmds)

                        # Sync thay đổi, và pass token hay không tùy trường hợp bên kia cần không
                        with self.lock:
                            still_demanding = self.peer_demanding
                            has_pending_logs = len(self.pending_sync_logs) > 0

                        if still_demanding:
                            # Nếu Peer đòi -> Sync + Pass Token luôn
                            self._sync_and_pass_token()
                        elif has_pending_logs:
                            # Nếu Peer KHÔNG đòi nhưng có dữ liệu mới -> Sync nhưng không pass token
                            self._sync_data_only()

    def _request_token_logic(self) -> bool:
        try:
            self.peer_service_proxy.request_token()
            got_token = self.token_event.wait(timeout=5.0)

            if got_token:
                return True
            else:
                print(">> [TIMEOUT] Peer did not reply in 5s.")
                return False

        except (ConnectionRefusedError, OSError, socket.error):
            print(">> [FAILOVER] Peer DOWN. Seizing Token.")
            with self.lock:
                self.has_token = True
                self.token_event.set()
                self.peer_demanding = False
            return True
        except Exception as e:
            print(f">> [ERROR] Request error: {e}")
            return False

    def _sync_and_pass_token(self):
        """Sync dữ liệu và CHUYỂN giao Token"""
        with self.lock:
            # Lấy và sanitize logs
            logs = self._sanitize_logs(self.pending_sync_logs)
            log_size = len(logs)

        # Nếu không có log nào thì vẫn phải gọi để pass token
        print(f">> [PASS] Syncing {log_size} logs & Passing Token...")

        try:
            # pass_token = True
            # Nếu bên kia bị mất kết nối => sync thất bại, xử lý trong except
            self.peer_service_proxy.receive_sync(logs, True)

            with self.lock:
                # Set trạng thái và giải phóng log khi gửi thành công
                self.has_token = False
                self.peer_demanding = False
                self.pending_sync_logs = self.pending_sync_logs[log_size:]
                self.token_event.clear()

            print(">> [INFO] Token passed.")

        except (ConnectionRefusedError, OSError):
            print(">> [ERROR] Peer died during pass. Keeping Token.")
            with self.lock:
                self.peer_demanding = False
        except Exception as e:
            print(f">> [ERROR] Pass failed: {e}")
            with self.lock:
                self.peer_demanding = False

    def _sync_data_only(self):
        """Sync dữ liệu nhưng giữ lại Token (Background Sync)"""
        with self.lock:
            logs = self._sanitize_logs(self.pending_sync_logs)
            log_size = len(logs)

        print(f">> [SYNC-ONLY] Pushing {log_size} logs to Peer (Keep Token)...")

        try:
            # pass_token = False
            self.peer_service_proxy.receive_sync(logs, False)

            with self.lock:
                # Xóa logs đã gửi để tránh gửi trùng lần sau
                self.pending_sync_logs = self.pending_sync_logs[log_size:]

            print(">> [INFO] Background sync success.")

        except (ConnectionRefusedError, OSError):
            # Không làm gì cả, giữ logs lại trong pending_sync_logs để lần sau gửi tiếp
            print(">> [WARN] Peer unreachable for background sync. Retrying later.")
        except Exception as e:
            print(f">> [ERROR] Background sync failed: {e}")
