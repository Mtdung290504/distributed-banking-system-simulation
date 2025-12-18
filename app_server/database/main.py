import mysql.connector
from mysql.connector.connection import MySQLConnection

from threading import Lock

from typing import List, Any, Optional, cast

from shared.models.server import CardData, TransactionData, UserData
from .exceptions import SQLException


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
        rows = self._query_procedure("get_all_users")
        return [cast(UserData, row) for row in rows]

    def get_cards_by_user_id(self, user_id: int):
        """Lấy danh sách thẻ của một user"""
        rows = self._query_procedure("get_cards_by_user_id", [user_id])
        return [cast(CardData, row) for row in rows]

    def login(self, card_number: str, card_pin: str):
        """Đăng nhập và lấy thông tin user"""
        cursor = None
        try:
            cursor = self.database.get_connection().cursor()
            args = [card_number, card_pin, 0, "", None, "", ""]

            # callproc trả về một list các tham số đã được cập nhật giá trị
            result_args = cast(List[Any], cursor.callproc("login", args))

            user_info: UserData = {
                "id": result_args[2],
                "name": result_args[3],
                "dob": result_args[4],
                "phone": result_args[5],
                "citizen_id": result_args[6],
                "card_number": card_number,
            }
            return user_info
        except mysql.connector.Error as e:
            raise SQLException(str(e.msg), e.sqlstate)
        finally:
            if cursor:
                cursor.close()

    def check_balance(self, card_number: str):
        """Kiểm tra số dư"""
        rows = self._query_procedure("check_balance", [card_number])
        if rows:
            row = cast(CardData, rows[0])  # lấy row đầu tiên từ results
            return int(row["balance"])

        raise Exception(f"Không tìm thấy số dư cho thẻ {card_number}")

    def get_transaction_history(self, card_number: str) -> List[TransactionData]:
        """Lấy lịch sử giao dịch"""
        rows = self._query_procedure("get_transaction_history", [card_number])
        return [cast(TransactionData, row) for row in rows]

    def _query_procedure(
        self, proc_name: str, params: list | None = None, dictionary: bool = True
    ) -> List[Any]:
        """Hàm helper để thực thi proc lấy dữ liệu và bắt lỗi tập trung"""
        cursor = None
        results = []
        try:
            cursor = self.database.get_connection().cursor(dictionary=dictionary)
            cursor.callproc(proc_name, params or [])

            # gom tất cả rows từ stored_results
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            return results
        except mysql.connector.Error as e:
            raise SQLException(str(e.msg), e.sqlstate)
        finally:
            if cursor:
                cursor.close()


class DatabaseWriter:
    """Xử lý các thao tác WRITE vào database thông qua Stored Procedures"""

    def __init__(self, database: Database):
        self.database = database
        self._lock = Lock()

    # Note: k dùng trong app chính
    def register_user(self, name: str, dob: str, phone: str, citizen_id: str):
        """
        Đăng ký người dùng mới.
            *dob: Ngày sinh định dạng 'YYYY-MM-DD'.

        Raises:
            SQLException: Nếu số điện thoại hoặc CCCD đã tồn tại trong hệ thống.
        """
        self._exec_procedure("register_user", [name, dob, phone, citizen_id])

    # Note: k dùng trong app chính
    def register_card(self, card_number: str, pin: str, balance: int, user_id: int):
        """
        Raises:
            SQLException: Nếu số thẻ đã tồn tại hoặc User ID không hợp lệ.
        """
        self._exec_procedure("register_card", [card_number, pin, balance, user_id])

    def withdraw_money(self, card_number: str, amount: int, transaction_time: int):
        """
        Raises:
            SQLException: Nếu số dư không đủ để thực hiện giao dịch.
        """
        self._exec_procedure("withdraw_money", [card_number, amount, transaction_time])

    def transfer_money(
        self, from_card: str, to_card: str, amount: int, transaction_time: int
    ):
        """
        Raises:
            SQLException: Nếu số dư tài khoản gửi không đủ, tài khoản nhận không tồn tại, hoặc chuyển cho chính mình.
        """
        self._exec_procedure(
            "transfer_money", [from_card, to_card, amount, transaction_time]
        )

    def deposit_money(self, card_number: str, amount: int, transaction_time: int):
        """
        Raises:
            SQLException: Nếu số thẻ không tồn tại.
        """
        self._exec_procedure("deposit_money", [card_number, amount, transaction_time])

    def change_pin(self, card_number: str, new_pin: str):
        """
        Raises:
            SQLException: Nếu mã PIN mới trùng với mã PIN hiện tại.
        """
        self._exec_procedure("change_pin", [card_number, new_pin])

    def _exec_procedure(self, proc_name: str, params: list):
        """
        Thực thi Stored Procedure và xử lý lỗi.

        Raises:
            SQLException: Nếu có lỗi nghiệp vụ từ SQL (45000) hoặc lỗi kết nối.
        """
        with self._lock:
            conn = self.database.get_connection()
            cursor = conn.cursor()
            try:
                cursor.callproc(proc_name, params)
                conn.commit()
            except mysql.connector.Error as e:
                raise SQLException(str(e.msg), e.sqlstate)
            finally:
                cursor.close()
