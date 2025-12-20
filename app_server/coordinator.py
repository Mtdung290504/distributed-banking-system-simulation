import time
import threading
from typing import List

from rmi_framework.v2 import LocateRegistry

# Import lỗi connection
from xmlrpc.client import Fault
import socket

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
        self.peer_registry = LocateRegistry.get_registry(
            address=peer_conf["host"], port=peer_conf["port"]
        )

        # Note: Lúc init có thể peer chưa bật, nên lookup ở đây ok
        # nhưng lúc gọi hàm mới biết sống hay chết
        self.peer_service_proxy = self.peer_registry.lookup("peer", PeerService)

        # State cần bảo vệ bởi Lock
        self.has_token = False
        self.peer_demanding = False
        self.pending_sync_logs: List[ATMCommand] = []

        self.lock = threading.Lock()

        # Event để đánh thức worker khi nhận được Token từ Peer
        self.token_event = threading.Event()

        self._initial_token_check()
        threading.Thread(target=self._worker_loop, daemon=True).start()

    def _initial_token_check(self):
        # Server 1 cầm cái ban đầu
        if PEER_ID == 1:
            with self.lock:
                self.has_token = True
            self.token_event.set()  # Đánh dấu là đã có token
            print(">> [STARTUP] I am Server 1. Holding Token.")
        else:
            with self.lock:
                self.has_token = False
            print(f">> [STARTUP] I am Server {PEER_ID}. Waiting.")

    # --- CÁC HÀM RMI GỌI VÀO (Thread khác) ---
    def set_peer_demanding(self, status: bool):
        with self.lock:
            self.peer_demanding = status
        # Không cần làm gì thêm, Worker sẽ tự check biến này khi tỉnh dậy

    def accept_token(self):
        with self.lock:
            self.has_token = True
            self.peer_demanding = False  # Đã nhận được rồi thì reset đòi
            self.token_event.set()  # Đánh thức worker đang đợi token
        print(">> [TOKEN] Received Token from Peer.")

    def handle_incoming_sync(self, logs: List[ATMCommand]):
        # Chạy trực tiếp update DB
        self.emitter.emit(self.executor.exec_direct, [logs])

    # --- WORKER LOOP (Thread chính xử lý) ---
    def _worker_loop(self):
        print(">> [COORDINATOR] Worker started.")
        while True:
            # 1. NGỦ CÓ THỜI HẠN (Giải quyết vấn đề 'Ngủ quên')
            # Cứ 1 giây tỉnh dậy 1 lần dù không có data, để check xem Peer có đòi Token không
            self.queue.wait_for_data(timeout=1.0)

            # 2. KIỂM TRA TRẠNG THÁI (Snapshot với Lock)
            with self.lock:
                am_holding_token = self.has_token
                is_peer_demanding = self.peer_demanding
                is_queue_empty = self.queue.is_empty()

            # 3. KỊCH BẢN: NHƯỜNG TOKEN (Khi rảnh + Bị đòi)
            if am_holding_token and is_peer_demanding and is_queue_empty:
                self._sync_and_pass_token()
                continue

            # 4. KỊCH BẢN: CÓ VIỆC CẦN LÀM (Queue có lệnh)
            if not is_queue_empty:

                # Chưa có Token -> Phải đi xin
                if not am_holding_token:
                    print(">> [WORKER] Data waiting. Requesting Token...")

                    # Gọi hàm xin (Logic Failover nằm trong này)
                    success = self._request_token_logic()

                    if success:
                        # Nếu xin được (hoặc tự chiếm được), cập nhật lại biến cục bộ
                        am_holding_token = True
                    else:
                        # Nếu vẫn không có token (ví dụ: đang đợi peer trả lời),
                        # Quay lại đầu vòng lặp đợi tiếp
                        continue

                # Đã có Token -> Xử lý lệnh
                if am_holding_token:
                    commands = self.queue.get_all()
                    if commands:
                        executed_cmds = self.executor.exec_direct(commands)
                        with self.lock:
                            self.pending_sync_logs.extend(executed_cmds)

                        # Làm xong việc, check lại xem Peer có đòi không để trả luôn
                        with self.lock:
                            still_demanding = self.peer_demanding

                        if still_demanding:
                            self._sync_and_pass_token()

    # --- LOGIC XIN TOKEN & FAILOVER ---
    def _request_token_logic(self) -> bool:
        """
        Gửi yêu cầu xin token.
        - Nếu Peer sống: Đợi Peer trả lời.
        - Nếu Peer chết (Refused): Tự chiếm Token ngay.
        Returns: True nếu đã có Token, False nếu chưa.
        """
        try:
            # 1. Gửi tín hiệu đòi
            self.peer_service_proxy.request_token()

            # 2. Đợi Peer phản hồi (Gọi accept_token)
            # Wait 5s. Nếu Peer sống, nó sẽ trả lời nhanh.
            # Nếu Peer treo (không refused nhưng không trả lời), ta đợi 5s.
            got_token = self.token_event.wait(timeout=5.0)

            if got_token:
                return True
            else:
                print(">> [TIMEOUT] Peer did not reply in 5s.")
                return False

        except (ConnectionRefusedError, OSError, socket.error):
            # --- FAILOVER: PEER CHẾT ---
            print(">> [FAILOVER] Connection Refused! Peer is DOWN.")
            print(">> [FAILOVER] Seizing Token immediately.")

            with self.lock:
                self.has_token = True
                self.token_event.set()
                # Quan trọng: Peer chết rồi thì không coi là nó đang đòi nữa
                self.peer_demanding = False

            return True  # Đã có token

        except Exception as e:
            print(f">> [ERROR] Request error: {e}")
            return False

    # --- LOGIC TRẢ TOKEN ---
    def _sync_and_pass_token(self):
        with self.lock:
            logs = self.pending_sync_logs[:]

        print(f">> [PASS] Syncing {len(logs)} logs & Passing Token...")

        try:
            # Gọi Peer nhận hàng
            self.peer_service_proxy.receive_sync(logs, True)

            # Peer nhận OK -> Mình bỏ Token
            with self.lock:
                self.has_token = False
                self.peer_demanding = False
                self.pending_sync_logs = []
                self.token_event.clear()  # Reset sự kiện token

            print(">> [INFO] Token passed.")

        except (ConnectionRefusedError, OSError):
            print(">> [ERROR] Peer died during sync. Keeping Token.")
            with self.lock:
                # Peer chết thì hủy yêu cầu đòi, giữ token dùng tiếp
                self.peer_demanding = False

        except Exception as e:
            print(f">> [ERROR] Sync failed: {e}")
            with self.lock:
                self.peer_demanding = False
