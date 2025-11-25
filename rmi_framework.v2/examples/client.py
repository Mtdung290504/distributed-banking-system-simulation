# Client Code
from core.registry import LocateRegistry
from examples.services.auth_service import AuthService
from examples.services.user_callback import UserCallbackImpl

# Không cần tạo registry thủ công nữa nếu muốn auto
# Hoặc nếu tạo thủ công thì không cần gọi listen() nếu lười

registry = LocateRegistry.getRegistry(address=None, port=29054)
auth_service = registry.lookup("auth", AuthService)

user_callback = UserCallbackImpl()

# Lúc này _serialize_arguments sẽ tự động dựng local server lên ở background
auth_service.login("alice", "password123", user_callback)

# Lưu ý: Vì client chạy background thread, nếu main thread kết thúc, client sẽ tắt.
# Cần block main thread lại nếu muốn giữ connection (ví dụ chờ input)
input("Press Enter to exit...")
