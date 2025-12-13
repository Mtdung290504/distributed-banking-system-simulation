import mysql.connector
from mysql.connector.connection import MySQLConnection

from threading import Lock

from typing import List, Any, Optional, cast

from shared.models.server import CardData, TransactionData, UserData


class Database:
    """Quản lý kết nối database"""

    def __init__(self, db_url: str, db_user: str, db_password: str, db_name: str):
        self.host = db_url
        self.user = db_user
        self.password = db_password
        self.db_name = db_name
        self._lock = Lock()

        self._writer: Optional["DatabaseWriter"] = None
        self._reader: Optional["DatabaseReader"] = None
        self.connection: Optional[MySQLConnection] = None
        self._connect()

    def _connect(self) -> None:
        """Lấy kết nối tới database"""
        if self.connection is None or not self.connection.is_connected():
            self.connection = cast(
                MySQLConnection,
                mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.db_name,
                    use_pure=True,
                ),
            )
            print("Kết nối database thành công!")

    def get_connection(self):
        """Lấy connection, tự động reconnect nếu cần"""
        if self.connection is None or not self.connection.is_connected():
            self._connect()

        # Nếu _connect thất bại thì sẽ raise error ở đó,
        # nên ở đây an toàn để assert connection không None
        assert self.connection is not None

        return self.connection

    def writer(self):
        if self._writer is None:
            with self._lock:
                if self._writer is None:
                    self._writer = DatabaseWriter(self)

        return self._writer

    def reader(self):
        if self._reader is None:
            with self._lock:
                if self._reader is None:
                    self._reader = DatabaseReader(self)

        return self._reader

    def close(self) -> None:
        if self.connection and self.connection.is_connected():
            self.connection.close()


class DatabaseReader:
    """Xử lý các thao tác READ từ database"""

    def __init__(self, database: Database):
        self.database: Database = database

    def get_all_users(self):
        """Lấy danh sách tất cả users"""
        users = []
        cursor = None

        try:
            cursor = self.database.get_connection().cursor(dictionary=True)
            cursor.callproc("get_all_users")

            for result in cursor.stored_results():
                rows = result.fetchall()
                users = [cast(UserData, row) for row in rows]

            return users
        finally:
            if cursor:
                cursor.close()

    def get_cards_by_user_id(self, user_id: int):
        """Lấy danh sách thẻ của một user"""
        cards = []
        cursor = None

        try:
            cursor = self.database.get_connection().cursor(dictionary=True)
            cursor.callproc("get_cards_by_user_id", [user_id])

            for result in cursor.stored_results():
                rows = result.fetchall()
                cards = [cast(CardData, row) for row in rows]

            return cards
        finally:
            if cursor:
                cursor.close()

    def login(self, card_number: str, card_pin: str):
        """Đăng nhập và lấy thông tin user"""
        cursor = None

        try:
            cursor = self.database.get_connection().cursor()

            # Tham số OUT cần khởi tạo giá trị ban đầu
            # args bao gồm: [IN_card, IN_pin, OUT_id, OUT_name, OUT_dob, OUT_phone, OUT_citizen]
            args = [card_number, card_pin, 0, "", None, "", ""]

            # callproc trả về một list các tham số đã được cập nhật giá trị
            # Ta dùng cast(List[Any], ...) để IDE không báo lỗi khi truy cập index
            result_args = cast(List[Any], cursor.callproc("login", args))

            user_info: UserData = {
                "id": result_args[2],
                "name": result_args[3],
                "dob": result_args[4],  # mysql-connector tự chuyển về datetime.date
                "phone": result_args[5],
                "citizen_id": result_args[6],
            }

            return user_info

        finally:
            if cursor:
                cursor.close()

    def check_balance(self, card_number: str) -> int:
        """Kiểm tra số dư"""
        cursor = None

        try:
            cursor = self.database.get_connection().cursor(dictionary=True)
            cursor.callproc("check_balance", [card_number])

            for result in cursor.stored_results():
                # fetchone có thể trả về None
                row = cast(Optional[CardData], result.fetchone())
                if row:
                    return int(row["balance"])

            raise Exception("Không tìm thấy số dư cho thẻ này.")
        finally:
            if cursor:
                cursor.close()

    def get_transaction_history(self, card_number: str) -> List[TransactionData]:
        """Lấy lịch sử giao dịch"""
        transactions = []
        cursor = None

        try:
            cursor = self.database.get_connection().cursor(dictionary=True)
            cursor.callproc("get_transaction_history", [card_number])

            for result in cursor.stored_results():
                rows = cast(List[Any], result.fetchall())
                transactions = [cast(TransactionData, row) for row in rows]

            return transactions
        finally:
            if cursor:
                cursor.close()


class DatabaseWriter:
    """Xử lý các thao tác WRITE vào database"""

    def __init__(self, database: Database):
        self.database = database
        self._lock = Lock()

    def register_user(self, name: str, dob: str, phone: str, citizen_id: str):
        with self._lock:
            cursor = self.database.get_connection().cursor()
            try:
                cursor.callproc("register_user", [name, dob, phone, citizen_id])
                self.database.get_connection().commit()
            finally:
                cursor.close()

    def register_card(self, card_number: str, pin: str, balance: int, user_id: int):
        with self._lock:
            cursor = self.database.get_connection().cursor()
            try:
                cursor.callproc("register_card", [card_number, pin, balance, user_id])
                self.database.get_connection().commit()
            finally:
                cursor.close()

    def withdraw_money(self, card_number: str, amount: int, transaction_time: int):
        with self._lock:
            cursor = self.database.get_connection().cursor()
            try:
                cursor.callproc(
                    "withdraw_money", [card_number, amount, transaction_time]
                )
                self.database.get_connection().commit()
            finally:
                cursor.close()

    def transfer_money(
        self,
        from_card_number: str,
        to_card_number: str,
        amount: int,
        transaction_time: int,
    ):
        with self._lock:
            cursor = self.database.get_connection().cursor()
            try:
                cursor.callproc(
                    "transfer_money",
                    [from_card_number, to_card_number, amount, transaction_time],
                )
                self.database.get_connection().commit()
            finally:
                cursor.close()

    def deposit_money(self, card_number: str, amount: int, transaction_time: int):
        with self._lock:
            cursor = self.database.get_connection().cursor()
            try:
                cursor.callproc(
                    "deposit_money", [card_number, amount, transaction_time]
                )
                self.database.get_connection().commit()
            finally:
                cursor.close()

    def change_pin(self, card_number: str, new_pin: str):
        with self._lock:
            cursor = self.database.get_connection().cursor()
            try:
                cursor.callproc("change_pin", [card_number, new_pin])
                self.database.get_connection().commit()
            finally:
                cursor.close()
