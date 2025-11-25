from abc import abstractmethod

from core.remote import RemoteObject, Remote
from examples.services.user_callback import UserCallback

import uuid


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
        self.sessions = dict()

    def login(self, username: str, password: str, callback: UserCallback) -> bool:
        print(f"User [{username}] is trying to log in...")

        if username not in self.db or self.db[username] != password:
            print(f"Login failed for user [{username}].")
            return False

        # Giả sử đăng nhập luôn thành công
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = dict()
        self.sessions[session_id]["history"] = list()
        callback.set_session_id(session_id)

        return True
