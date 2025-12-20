from rmi_framework.v2 import RemoteObject, LocalRegistry

from shared.interfaces.server import UserService
from shared.interfaces.client import SuccessCallback
from shared.models.server import (
    UserData,
    ChangePinCommand,
    WithdrawCommand,
    DepositCommand,
    TransferCommand,
)
from shared.utils import now

from ..database.main import DatabaseReader
from ..command_queue import CommandQueue
from ..config import PEER_ID


class UserServiceImpl(RemoteObject, UserService):
    def __init__(
        self,
        session_id: str,
        user: UserData,
        registry: LocalRegistry,
        command_queue: CommandQueue,
        database_reader: DatabaseReader,
    ):
        super().__init__()
        self.session_id = session_id
        self.user = user
        self.registry = registry
        self.command_queue = command_queue
        self.database_reader = database_reader

    def get_balance(self):
        return self.database_reader.check_balance(self.user["card_number"])

    def get_transaction_history(self):
        return self.database_reader.get_transaction_history(self.user["card_number"])

    def get_info(self):
        return self.user

    def change_pin(self, new_pin: str, callback: SuccessCallback):
        self.command_queue.add(
            ChangePinCommand(
                command_type="change-pin",
                card_number=self.user["card_number"],
                peer_id=PEER_ID,
                new_pin=new_pin,
                timestamp=now(),
                success_callback=callback,
            )
        )

    def deposit(self, amount: int, callback: SuccessCallback):
        self.command_queue.add(
            DepositCommand(
                peer_id=PEER_ID,
                command_type="deposit",
                card_number=self.user["card_number"],
                amount=amount,
                timestamp=now(),
                success_callback=callback,
            )
        )

    def withdraw(self, amount: int, callback: SuccessCallback):
        self.command_queue.add(
            WithdrawCommand(
                peer_id=PEER_ID,
                command_type="withdraw",
                card_number=self.user["card_number"],
                amount=amount,
                timestamp=now(),
                success_callback=callback,
            )
        )

    def transfer(self, to_card: str, amount: int, callback: SuccessCallback):
        self.command_queue.add(
            TransferCommand(
                peer_id=PEER_ID,
                command_type="transfer",
                card_number=self.user["card_number"],
                to_card=to_card,
                amount=amount,
                timestamp=now(),
                success_callback=callback,
            )
        )

    def logout(self, callback: SuccessCallback):
        print(f"User [{self.user['name']}] log out")
        self.registry.unbind(self.session_id)
        callback.notify("Đã logout!")
