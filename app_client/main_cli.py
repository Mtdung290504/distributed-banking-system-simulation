# Client side

from xmlrpc.client import Fault
from rmi_framework.v2 import LocateRegistry

from shared.interfaces.server import AuthService, UserService
from .callbacks import SuccessCallbackImpl


local_registry = LocateRegistry.local_registry()
local_registry.listen(background=True)

registry = LocateRegistry.get_registry(address=None, port=29054)
auth_service = registry.lookup("auth", AuthService)

# ping_callback = PingCallbackImpl()
success_callback = SuccessCallbackImpl()

login_success = False
session_id: str | None = None
try:
    while not login_success:
        try:
            username, password = input("username:"), input("password:")
        # Bắt Ctrl+C + Enter để ngắt
        except:
            exit()

        try:
            login_result = auth_service.login(username, password, success_callback)
            login_success = login_result["success"]
            session_id = login_result["session_id"]

            if not login_success:
                # print("Login failed:", login_result["message"])
                continue

        except Exception as e:
            # Bắt Remote Error
            print("\n*Remote error:", e, "\n")
            login_success = False


except KeyboardInterrupt:
    pass

# Get user service
assert session_id is not None
user_service = registry.lookup(session_id, UserService)

# Lưu ý: Vì client chạy background thread, nếu main thread kết thúc, client sẽ tắt.
# Cần block main thread lại nếu muốn giữ connection (ví dụ chờ input)
while command := input("\nEnter command or press Enter to exit...: "):
    if "logout" in command:
        try:
            user_service.logout(success_callback)
        except Fault as f:
            print(f)
    else:
        try:
            print(user_service.get_balance())
            print(user_service.get_info())

            history = user_service.get_transaction_history()
            for record in history:
                print(record["timestamp"], record)

            user_service.change_pin("haha", success_callback)
            user_service.deposit(1000, success_callback)
            user_service.withdraw(2000, success_callback)
            user_service.transfer("222222", 1000, success_callback)
        except Fault as f:
            print(f)
