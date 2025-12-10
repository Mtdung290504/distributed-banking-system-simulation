from typing import TypedDict
from datetime import date


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
