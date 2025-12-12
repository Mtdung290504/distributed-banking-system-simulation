from rmi_framework.v2 import RemoteObject, LocalRegistry

from shared.interfaces.server import UserService
from shared.interfaces.client import SuccessCallback

from shared.models.server import UserData


class UserServiceImpl(RemoteObject, UserService):
    def __init__(self, registry: LocalRegistry, session_id: str, user: UserData):
        super().__init__()
        self.registry = registry
        self.session_id = session_id
        self.user = user

    def message(self, message: str):
        return print(f"User [{self.user['name']}] message:", message)

    def logout(self, callback: SuccessCallback):
        print(f"User [{self.user['name']}] log out")
        self.registry.unbind(self.session_id)
        callback.notify("Đã logout!")
