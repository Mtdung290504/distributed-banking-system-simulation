from rmi_framework.v2 import RemoteObject, LocalRegistry

from shared.interfaces.server import AuthService
from shared.interfaces.client import SuccessCallback
from shared.models.server import LoginResult

from ..database.main import Database

from .user_service import UserServiceImpl

import uuid
from typing import Optional


class AuthServiceImpl(RemoteObject, AuthService):
    def __init__(self, registry: LocalRegistry, database: Database):
        super().__init__()
        self.database = database
        self.registry = registry
        self.user_id: Optional[int] = None

    def login(self, card_number: str, pin: str, callback: SuccessCallback):
        success_message = "Đăng nhập thành công!"
        fail_message = "Đăng nhập thất bại!"

        try:
            user_data = self.database.reader().login(card_number, pin)
            session_id = str(uuid.uuid4())

            user_service = UserServiceImpl(self.registry, session_id, user_data)
            self.registry.bind(session_id, user_service)

            callback.notify(success_message)
            return LoginResult(
                {
                    "success": True,
                    "message": success_message,
                    "session_id": session_id,
                }
            )

        except Exception as e:
            print(e)
            callback.notify(fail_message)
            return LoginResult(
                {
                    "success": False,
                    "message": fail_message,
                    "session_id": None,
                }
            )
