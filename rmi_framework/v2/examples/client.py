# Client side
from core.registry import LocateRegistry
from .services.auth_service import AuthService
from .services.calc_service import CalcService
from .services.user_callback import UserCallbackImpl

from xmlrpc.client import Fault

local_registry = LocateRegistry.createRegistry()
local_registry.listen(background=True)

registry = LocateRegistry.getRegistry(address=None, port=29054)
auth_service = registry.lookup("auth", AuthService)
calc_service = registry.lookup("calc", CalcService)

user_callback = UserCallbackImpl()

logged_in = False
try:
    while not logged_in:
        try:
            username, password = input("username:"), input("password:")
        # Bắt Ctrl+C + Enter để ngắt
        except:
            exit()

        try:
            logged_in = auth_service.login(username, password, user_callback)

        except Exception as e:
            # Bắt Remote Error
            print("\n*Remote error:", e, "\n")
            logged_in = False

        # Chỉ chạy nếu logged_in == False và không có ngoại lệ
        if not logged_in:
            print("Login failed!")
            continue

except KeyboardInterrupt:
    pass

print(user_callback.session_id)
assert (
    user_callback.session_id != None
), "Login thành công, session ID không tồn tại là do lỗi server"

# Lưu ý: Vì client chạy background thread, nếu main thread kết thúc, client sẽ tắt.
# Cần block main thread lại nếu muốn giữ connection (ví dụ chờ input)

while command := input("\nEnter command or press Enter to exit...: "):
    if "+" in command:
        param = command.split("+")
        try:
            print(
                command,
                "=",
                calc_service.add(
                    user_callback.session_id,
                    float(param[0].strip()),
                    float(param[1].strip()),
                ),
            )
        except Fault as f:
            print(f)
