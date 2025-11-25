# Client Code
from core.registry import LocateRegistry
from examples.services.auth_service import AuthService
from examples.services.calc_service import CalcService
from examples.services.user_callback import UserCallbackImpl

from xmlrpc.client import Fault

# Không cần tạo registry thủ công nữa nếu muốn auto
# Hoặc nếu tạo thủ công thì không cần gọi listen() nếu lười

registry = LocateRegistry.getRegistry(address=None, port=29054)
auth_service = registry.lookup("auth", AuthService)
calc_service = registry.lookup("calc", CalcService)

user_callback = UserCallbackImpl()

# Lúc này _serialize_arguments sẽ tự động dựng local server lên ở background
while not auth_service.login(input("username:"), input("password:"), user_callback):
    print("Login failed!")
    continue

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
