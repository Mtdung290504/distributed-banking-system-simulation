# Client side

from xmlrpc.client import Fault
from rmi_framework.v2 import LocateRegistry

from shared.interfaces import server
from .callbacks.ping_callback import PingCallbackImpl


local_registry = LocateRegistry.createRegistry()
local_registry.listen(background=True)

registry = LocateRegistry.getRegistry(address=None, port=29054)
auth_service = registry.lookup("auth", server.AuthService)

ping_callback = PingCallbackImpl()

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
            login_result = auth_service.login(username, password, ping_callback)
            login_success = login_result["success"]
            session_id = login_result["session_id"]

            if not login_success:
                print("Login failed:", login_result["message"])
                continue

        except Exception as e:
            # Bắt Remote Error
            print("\n*Remote error:", e, "\n")
            login_success = False


except KeyboardInterrupt:
    pass


# Lưu ý: Vì client chạy background thread, nếu main thread kết thúc, client sẽ tắt.
# Cần block main thread lại nếu muốn giữ connection (ví dụ chờ input)
assert session_id is not None
while command := input("\nEnter command or press Enter to exit...: "):
    if "logout" in command:
        try:
            auth_service.logout(session_id)
        except Fault as f:
            print(f)
