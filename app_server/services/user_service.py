from rmi_framework.v2 import RemoteObject, LocalRegistry

from shared.interfaces.server import UserService
from shared.interfaces.client import SuccessCallback
from shared.models.server import UserData

from ..database.main import DatabaseReader


class UserServiceImpl(RemoteObject, UserService):
    def __init__(
        self,
        session_id: str,
        user: UserData,
        database_reader: DatabaseReader,
        registry: LocalRegistry,
    ):
        super().__init__()
        self.session_id = session_id
        self.user = user
        self.database_reader = database_reader
        self.registry = registry

    def get_balance(self):
        return self.database_reader.check_balance(self.user["card_number"])

    def get_transaction_history(self):
        return self.database_reader.get_transaction_history(self.user["card_number"])

    def get_info(self):
        return self.user

    def change_pin(self, new_pin: str, callback: SuccessCallback):
        pass

    def deposit(self, amount: int, callback: SuccessCallback):
        pass

    def withdraw(self, amount: int, callback: SuccessCallback):
        pass

    def transfer(self, to_card: str, amount: int, callback: SuccessCallback):
        pass

    def logout(self, callback: SuccessCallback):
        print(f"User [{self.user['name']}] log out")
        self.registry.unbind(self.session_id)
        callback.notify("Đã logout!")
