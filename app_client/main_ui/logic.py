# Client side

from xmlrpc.client import Fault
from rmi_framework.v2 import LocateRegistry

from shared.interfaces.server import AuthService, UserService
from shared.utils import dmy_hms_from_timestamp
from app_client.callbacks import SuccessCallbackImpl


# 1. Setup Registry
local_registry = LocateRegistry.local_registry()
local_registry.listen(background=True)

# Thay đổi port nếu cần (kết nối tới Server 1 hoặc 2)
registry = LocateRegistry.get_registry(address="10.31.176.169", port=29055)
auth_service = registry.lookup("auth", AuthService)
success_callback = SuccessCallbackImpl()

# 2. Login Process
login_success = False
session_id: str | None = None

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
    pass

# 3. User Session Loop
assert session_id is not None
user_service = registry.lookup(session_id, UserService)
