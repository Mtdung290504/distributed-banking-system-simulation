from rmi_framework.v2 import RemoteObject, LocalRegistry

from shared.interfaces.server import AuthService
from shared.interfaces.client import SuccessCallback
from shared.models.server import LoginResult

from ..database.main import Database
from ..command_queue import CommandQueue

from .user_service import UserServiceImpl

import uuid
from typing import Optional


class AuthServiceImpl(RemoteObject, AuthService):
    def __init__(
        self, registry: LocalRegistry, database: Database, command_queue: CommandQueue
    ):
        super().__init__()

        self.registry = registry
        self.database = database
        self.command_queue = command_queue

        self.user_id: Optional[int] = None

    def login(self, card_number: str, pin: str, callback: SuccessCallback):
        success_message = "Đăng nhập thành công!"
        fail_message = "Đăng nhập thất bại!"

        try:
            user_data = self.database.reader().login(card_number, pin)

            while True:
                session_id = str(uuid.uuid4())
                user_service = UserServiceImpl(
                    session_id=session_id,
                    user=user_data,
                    registry=self.registry,
                    database_reader=self.database.reader(),
                    command_queue=self.command_queue,
                )

                # Đảm bảo session_id là duy nhất, chạy đến khi nào uuid không trùng thì thôi
                # Nhưng xác suất trùng thấp hơn trúng số nữa
                try:
                    self.registry.bind(session_id, user_service)
                    break
                except ValueError:
                    print("Bingo!!! May mắn không ai bằng!!!")
                    continue

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
