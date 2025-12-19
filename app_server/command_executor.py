from shared.models.server import ATMCommand

from .database.main import DatabaseWriter, SQLException
from .command_queue import CommandQueue


class CommandExecutor:
    def __init__(self, command_queue: CommandQueue, database_writer: DatabaseWriter):
        self.command_queue = command_queue
        self.database_writer = database_writer

    def exec(self) -> list[ATMCommand]:
        success: list[ATMCommand] = []
        current = self.command_queue.get_all()

        for cmd in current:
            try:
                # Note: python version > 3.10
                match cmd["command_type"]:
                    case "change-pin":
                        self.database_writer.change_pin(
                            cmd["card_number"], cmd["new_pin"]
                        )

                    case "deposit":
                        self.database_writer.deposit_money(
                            cmd["card_number"], cmd["amount"], cmd["timestamp"]
                        )

                    case "withdraw":
                        self.database_writer.withdraw_money(
                            cmd["card_number"], cmd["amount"], cmd["timestamp"]
                        )

                    case "transfer":
                        self.database_writer.transfer_money(
                            cmd["card_number"],
                            cmd["to_card"],
                            cmd["amount"],
                            cmd["timestamp"],
                        )

                success.append(cmd)

                cmd["success_callback"].notify('\nGiao dịch thành công!')
            except SQLException as e:
                cmd["success_callback"].notify(e.get_notify_message())
            except Exception as e:
                print(f"Unexpected error: {e}")

        return success
