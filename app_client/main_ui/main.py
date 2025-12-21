"""
Ứng dụng ATM Client
Chạy bằng lệnh: python -m app.client
"""

import sys
from PyQt5.QtWidgets import QApplication
from .ui.login import LoginWindow
from .ui.main_window import MainWindow


class ATMClientApp:
    """Ứng dụng ATM Client chính"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.main_window = None

    def run(self):
        """Khởi chạy ứng dụng"""
        self.show_login()
        sys.exit(self.app.exec_())

    def show_login(self):
        """Hiển thị màn hình đăng nhập"""
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

    def on_login_success(self):
        """
        Xử lý khi đăng nhập thành công
        - Đóng màn hình đăng nhập
        - Mở màn hình chính
        """
        # TODO: Backend - Lưu thông tin session/user sau khi đăng nhập thành công
        # backend.store_session(user_data)

        if self.login_window:
            self.login_window.hide()
        self.show_main_window()

    def show_main_window(self):
        """Hiển thị màn hình chính"""
        self.main_window = MainWindow()
        self.main_window.show()

        # TODO: Backend - Load dữ liệu người dùng khi vào màn hình chính
        # self.load_user_data()

    def load_user_data(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Load dữ liệu người dùng sau khi đăng nhập
        - Lấy thông tin tài khoản
        - Lấy số dư
        - Lấy lịch sử giao dịch gần đây
        """
        pass


def main():
    """Hàm main để chạy ứng dụng"""
    app = ATMClientApp()
    app.run()


if __name__ == "__main__":
    main()
