# Client side

from xmlrpc.client import Fault
from rmi_framework.v2 import LocateRegistry

from shared.interfaces.server import AuthService, UserService
from shared.utils import dmy_hms_from_timestamp
from .callbacks import SuccessCallbackImpl


def run_client():
    # 1. Setup Registry
    local_registry = LocateRegistry.local_registry(29056)
    local_registry.listen(background=True)

    # Thay đổi port nếu cần (kết nối tới Server 1 hoặc 2)
    registry = LocateRegistry.get_registry(address=None, port=29055)
    auth_service = registry.lookup("auth", AuthService)
    success_callback = SuccessCallbackImpl()

    # 2. Login Process
    login_success = False
    session_id: str | None = None

    print("--- ATM CLIENT SYSTEM ---")
    try:
        while not login_success:
            try:
                card = input("Card Number: ").strip()
                if not card:
                    continue  # Bỏ qua nếu enter rỗng
                pin = input("PIN: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                exit()

            try:
                print("Logging in...")
                login_result = auth_service.login(card, pin, success_callback)
                login_success = login_result["success"]
                session_id = login_result["session_id"]

                if not login_success:
                    print(f">> Login Failed: {login_result['message']}")
                    continue

            except Exception as e:
                print(f"\n* Remote error: {e}\n")
                login_success = False

    except KeyboardInterrupt:
        return

    # 3. User Session Loop
    assert session_id is not None
    user_service = registry.lookup(session_id, UserService)

    print("\n--- LOGIN SUCCESSFUL ---")
    print("Syntax: <command>, <arg1>, <arg2>...")
    print("Commands: balance, info, history, deposit, withdraw, transfer, pin, logout")
    print("Example: 'deposit, 50000' or 'transfer, 999999, 10000'")

    while True:
        try:
            raw_input = input("\nAWS:ATM> ").strip()
            if not raw_input:
                continue

            # Tách chuỗi bằng dấu phẩy
            parts = [p.strip() for p in raw_input.split(",")]
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ["exit", "quit"]:
                break

            # --- Dispatcher Logic ---
            if cmd == "logout":
                user_service.logout(success_callback)
                break

            elif cmd == "balance":
                bal = user_service.get_balance()
                print(f">> Balance: {bal:,} VND")

            elif cmd == "info":
                info = user_service.get_info()
                print(f">> Info: {info}")

            elif cmd == "history":
                history = user_service.get_transaction_history()
                print(f"{'TIME':<15} | {'TYPE':<10} | {'AMOUNT'}")
                print("-" * 40)
                for rec in history:
                    # Xử lý hiển thị history đẹp hơn chút
                    amt = rec.get("amount", 0)
                    print(
                        f"{dmy_hms_from_timestamp(rec['timestamp'])} | {rec['transaction_type']:<10} | {amt:,}"
                    )

            elif cmd == "deposit":
                # Syntax: deposit, amount
                if len(args) < 1:
                    print("Usage: deposit, <amount>")
                    continue
                amount = int(args[0])
                user_service.deposit(amount, success_callback)

            elif cmd == "withdraw":
                # Syntax: withdraw, amount
                if len(args) < 1:
                    print("Usage: withdraw, <amount>")
                    continue
                amount = int(args[0])
                user_service.withdraw(amount, success_callback)

            elif cmd == "transfer":
                # Syntax: transfer, to_card, amount
                if len(args) < 2:
                    print("Usage: transfer, <to_card>, <amount>")
                    continue
                to_card = args[0]
                amount = int(args[1])
                user_service.transfer(to_card, amount, success_callback)

            elif cmd in ["pin", "change_pin"]:
                # Syntax: pin, new_pin
                if len(args) < 1:
                    print("Usage: pin, <new_pin>")
                    continue
                new_pin = args[0]
                user_service.change_pin(new_pin, success_callback)

            else:
                print(f"Unknown command: '{cmd}'. Try again.")

        except ValueError:
            print("Error: Invalid number format. Please check your arguments.")
        except Fault as f:
            print(f"Remote Error: {f.faultString}")
        except KeyboardInterrupt:
            print("\nForce Exit.")
            break
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    run_client()
