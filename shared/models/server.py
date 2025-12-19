from typing import TypedDict, Literal, List, Union
from datetime import date

from shared.interfaces.client import SuccessCallback


class LoginResult(TypedDict):
    success: bool
    message: str
    session_id: str | None


class UserData(TypedDict):
    id: int
    name: str
    dob: date
    phone: str
    citizen_id: str
    card_number: str


class CardData(TypedDict):
    owner_id: int
    number: str
    pin: str
    balance: int


class TransactionData(TypedDict):
    amount: int
    transaction_type: str
    from_card_number: str
    to_card_number: str
    timestamp: int


# Các command


class BaseCommand(TypedDict):
    peer_id: int
    card_number: str
    timestamp: int
    success_callback: SuccessCallback


class TransactionCommand(BaseCommand):
    """Base cho các lệnh liên quan đến tiền (Rút/Nạp/Chuyển)"""

    amount: int


# Các command cụ thể


class ChangePinCommand(BaseCommand):
    command_type: Literal["change-pin"]
    new_pin: str


class WithdrawCommand(TransactionCommand):
    command_type: Literal["withdraw"]


class DepositCommand(TransactionCommand):
    command_type: Literal["deposit"]


class TransferCommand(TransactionCommand):
    command_type: Literal["transfer"]
    to_card: str


# 3. Tạo Alias để code gọn hơn
ATMCommand = Union[ChangePinCommand, WithdrawCommand, DepositCommand, TransferCommand]


class Token(TypedDict):
    results: List[ATMCommand]
