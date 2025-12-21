import socket
import time
from typing import Optional, Tuple
from xmlrpc.client import Fault
from rmi_framework.v2 import LocateRegistry

from shared.interfaces.server import AuthService, UserService
from shared.utils import dmy_hms_from_timestamp
from .callbacks import SuccessCallbackImpl
from .config import SERVER_CONFIG, PRIMARY_PEER_ID


def get_failover_order():
    """Trả về peer server ID theo thứ tự ưu tiên theo cấu hình client: [Primary, Secondary]"""
    secondary = 2 if PRIMARY_PEER_ID == 1 else 1
    return [PRIMARY_PEER_ID, secondary]


def try_login(
    card: str, pin: str, callback_obj
) -> Tuple[Optional[UserService], Optional[int]]:
    """
    Hàm đóng gói logic Login + Failover.
    - Thử Server 1 -> Chết -> Thử Server 2.
    - Trả về (UserService, server_id) nếu thành công.
    - Trả về (None, None) nếu thất bại (sai pass hoặc cả 2 server sập).
    """
    for peer_id in get_failover_order():
        conf = SERVER_CONFIG[peer_id]
        print(
            f">> Connecting to Server {peer_id} ({conf['host']})...",
            end=" ",
        )

        try:
            # 1. Lấy Registry (Chưa kết nối mạng)
            registry = LocateRegistry.get_registry(
                address=conf["host"], port=conf["port"]
            )
            auth_service = registry.lookup("auth", AuthService)

            # 2. Gọi Login (Lúc này mới thực sự kết nối mạng)
            # Nếu Server chết, dòng này sẽ bắn OSError/ConnectionRefusedError
            login_result = auth_service.login(card, pin, callback_obj)
            print(f"\tServer:[{conf['host']}:{conf['port']}] OK")

            if login_result["success"] and login_result["session_id"]:
                # Login thành công -> Lấy UserService
                session_id = login_result["session_id"]
                user_service = registry.lookup(session_id, UserService)
                return user_service, peer_id
            else:
                # Kết nối được nhưng sai Pass -> Không thử server kia nữa
                print(f"\tLogin fail: {login_result['message']}")
                return None, None

        except (ConnectionRefusedError, OSError, socket.error):
            # Server này chết -> In lỗi và tiếp tục vòng lặp sang server kế tiếp
            print("\tLogin failed (Server unreachable).")
            continue

        except Fault as f:
            # Lỗi Logic từ Server (VD: DB lỗi) -> Coi như connect được
            print(f"\n>> [REMOTE ERROR] {f.faultString}")
            return None, None
        except Exception as e:
            print(f"\n>> [ERROR] {e}")
            return None, None

    # Hết vòng lặp mà không return -> Cả 2 server đều tạch
    print("\n>> [FATAL] All servers are currently down.")
    return None, None


def run_client():
    # Setup Callback cục bộ
    local_registry = LocateRegistry.local_registry()
    local_registry.listen(background=True)
    success_callback = SuccessCallbackImpl()

    print("\nATM CLIENT SYSTEM")

    while True:  # Vòng lặp chính: Quay lại đây nếu logout hoặc mất kết nối
        try:
            # --- PHA 1: NHẬP LIỆU & LOGIN ---
            user_service = None
            connected_server_id = None

            while user_service is None:
                try:
                    card = input("\nCard Number: ").strip()
                    if not card:
                        continue
                    pin = input("PIN: ").strip()

                    # Gọi hàm login thông minh đã đóng gói
                    user_service, connected_server_id = try_login(
                        card, pin, success_callback
                    )
                except KeyboardInterrupt:
                    print("\nExiting...")
                    return

            # --- PHA 2: SESSION LOOP ---
            print(f"\n--- LOGIN SUCCESSFUL (Server {connected_server_id}) ---")
            print(
                "Commands: balance, info, history, deposit, withdraw, transfer, pin, logout"
            )

            while True:
                try:
                    raw_input = input(f"\nATM({connected_server_id})> ").strip()
                    if not raw_input:
                        continue

                    parts = [p.strip() for p in raw_input.split(",")]
                    cmd = parts[0].lower()
                    args = parts[1:]

                    if cmd in ["exit", "quit"]:
                        return

                    # --- Xử lý lệnh ---
                    if cmd == "logout":
                        try:
                            user_service.logout(success_callback)
                        except:
                            pass  # Kệ lỗi mạng lúc logout
                        break  # Break ra vòng lặp ngoài để login lại

                    elif cmd == "balance":
                        print(f">> Balance: {user_service.get_balance():,} VND")

                    elif cmd == "info":
                        print(f">> Info: {user_service.get_info()}")

                    elif cmd == "history":
                        history = user_service.get_transaction_history()
                        print(f"{'TIME':<20} | {'TYPE':<10} | {'AMOUNT'}")
                        print("-" * 45)
                        for rec in history:
                            ts = dmy_hms_from_timestamp(rec["timestamp"])
                            amt = rec.get("amount", 0)
                            print(f"{ts:<20} | {rec['transaction_type']:<10} | {amt:,}")

                    elif cmd == "deposit":
                        if len(args) < 1:
                            print("Usage: deposit, <amount>")
                            continue
                        user_service.deposit(int(args[0]), success_callback)

                    elif cmd == "withdraw":
                        if len(args) < 1:
                            print("Usage: withdraw, <amount>")
                            continue
                        user_service.withdraw(int(args[0]), success_callback)

                    elif cmd == "transfer":
                        if len(args) < 2:
                            print("Usage: transfer, <card>, <amount>")
                            continue
                        user_service.transfer(args[0], int(args[1]), success_callback)

                    elif cmd in ["pin", "change_pin"]:
                        if len(args) < 1:
                            print("Usage: pin, <new_pin>")
                            continue
                        user_service.change_pin(args[0], success_callback)

                    else:
                        print(f"Unknown command: '{cmd}'")

                # --- BẮT LỖI MẠNG KHI ĐANG DÙNG ---
                except (ConnectionRefusedError, OSError, socket.error):
                    print(
                        f"\n>> [DISCONNECTED] Lost connection to Server {connected_server_id}!"
                    )
                    print(">> Please login again to find an active server.")
                    break  # Break ra để login lại (Failover sẽ tự tìm server sống)

                except Fault as f:
                    print(f">> [REMOTE ERROR] {f.faultString}")
                except ValueError:
                    print(">> Error: Invalid number format.")
                except Exception as e:
                    print(f">> Error: {e}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    run_client()
