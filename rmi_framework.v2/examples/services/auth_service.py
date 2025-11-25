from abc import abstractmethod
from core.remote import RemoteObject, Remote
from examples.services.user_callback import UserCallback


# Define interface
class AuthService(Remote):
    @abstractmethod
    def login(self, username: str, password: str, callback: UserCallback) -> bool:
        pass


# Implementation
class AuthServiceImpl(RemoteObject, AuthService):
    def __init__(self, db: dict[str, str]):
        super().__init__()
        self.db = db

    def login(self, username: str, password: str, callback: UserCallback) -> bool:
        print(f"User [{username}] is trying to log in...")

        if username not in self.db or self.db[username] != password:
            print(f"Login failed for user [{username}].")
            return False

        # Giả sử đăng nhập luôn thành công
        session_id = "SESSION12345"
        print(
            f"User [{username}] logged in successfully. Setting session ID via callback..."
        )
        callback.set_session_id(session_id)
        return True
