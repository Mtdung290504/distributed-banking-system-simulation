"""
Module chứa cửa sổ chính (Main Window) của ứng dụng ATM Client
"""

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from . import (
    ProfileScreen,
    DepositScreen,
    WithdrawScreen,
    TransferScreen,
    TransactionHistoryScreen,
    ChangePinScreen,
)
from .notification import NotificationManager


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng ATM"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Khởi tạo giao diện chính"""
        self.setWindowTitle("ATM System - Trang chủ")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #ecf0f1;")

        # Widget trung tâm
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout chính (ngang)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Tạo Navbar (thanh điều hướng bên trái)
        self.create_navbar()
        main_layout.addWidget(self.navbar)

        # Container cho nội dung chính
        content_container = QFrame()
        content_container.setStyleSheet(
            """
            QFrame {
                background-color: #ecf0f1;
                border-left: 3px solid #bdc3c7;
            }
        """
        )
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Stacked Widget để chứa các màn hình
        self.stacked_widget = QStackedWidget()

        # Thêm các màn hình vào stacked widget
        self.profile_screen = ProfileScreen()
        self.deposit_screen = DepositScreen()
        self.withdraw_screen = WithdrawScreen()
        self.transfer_screen = TransferScreen()
        self.history_screen = TransactionHistoryScreen()
        self.change_pin_screen = ChangePinScreen()

        self.stacked_widget.addWidget(self.profile_screen)  # Index 0
        self.stacked_widget.addWidget(self.deposit_screen)  # Index 1
        self.stacked_widget.addWidget(self.withdraw_screen)  # Index 2
        self.stacked_widget.addWidget(self.transfer_screen)  # Index 3
        self.stacked_widget.addWidget(self.history_screen)  # Index 4
        self.stacked_widget.addWidget(self.change_pin_screen)  # Index 5

        content_layout.addWidget(self.stacked_widget)
        content_container.setLayout(content_layout)

        main_layout.addWidget(content_container, stretch=1)

        central_widget.setLayout(main_layout)

        # Hiển thị màn hình profile mặc định
        self.show_screen(0)

    def create_navbar(self):
        """Tạo thanh điều hướng (Navbar)"""
        self.navbar = QFrame()
        self.navbar.setFixedWidth(250)
        self.navbar.setStyleSheet(
            """
            QFrame {
                background-color: #2c3e50;
                border-right: 3px solid #34495e;
            }
        """
        )

        navbar_layout = QVBoxLayout()
        navbar_layout.setContentsMargins(0, 0, 0, 0)
        navbar_layout.setSpacing(0)

        # Header của navbar
        header = QLabel("ATM SYSTEM")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
            """
            QLabel {
                background-color: #34495e;
                color: white;
                padding: 25px;
                border-bottom: 3px solid #3498db;
            }
        """
        )
        navbar_layout.addWidget(header)

        # Danh sách các nút trong navbar
        nav_buttons = [
            ("👤 Thông tin cá nhân", 0),
            ("💰 Nạp tiền", 1),
            ("💳 Rút tiền", 2),
            ("💸 Chuyển khoản", 3),
            ("📜 Lịch sử giao dịch", 4),
            ("🔒 Đổi mã PIN", 5),
        ]

        self.nav_btn_list = []

        for btn_text, screen_index in nav_buttons:
            btn = QPushButton(btn_text)
            btn.setFont(QFont("Arial", 11))
            btn.setStyleSheet(self.get_nav_button_style(False))
            btn.setFixedHeight(60)
            btn.clicked.connect(lambda checked, idx=screen_index: self.show_screen(idx))
            navbar_layout.addWidget(btn)
            self.nav_btn_list.append(btn)

        # Nút đăng xuất
        navbar_layout.addStretch()
        logout_btn = QPushButton("🚪 Đăng xuất")
        logout_btn.setFont(QFont("Arial", 11, QFont.Bold))
        logout_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        logout_btn.clicked.connect(self.handle_logout)
        navbar_layout.addWidget(logout_btn)

        self.navbar.setLayout(navbar_layout)

    def get_nav_button_style(self, is_active):
        """Lấy style cho nút navbar"""
        if is_active:
            return """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-left: 5px solid #2980b9;
                    padding: 15px;
                    text-align: left;
                    padding-left: 20px;
                    font-weight: bold;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    border: none;
                    padding: 15px;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    border-left: 5px solid #3498db;
                }
            """

    def show_screen(self, index):
        """
        Hiển thị màn hình tương ứng với index

        Args:
            index: Index của màn hình trong stacked widget
                0: Profile
                1: Deposit
                2: Withdraw
                3: Transfer
                4: Transaction History
                5: Change PIN
        """
        # Cập nhật style cho các nút navbar
        for i, btn in enumerate(self.nav_btn_list):
            btn.setStyleSheet(self.get_nav_button_style(i == index))

        # Chuyển đổi màn hình
        self.stacked_widget.setCurrentIndex(index)

        # TODO: Backend - Load dữ liệu cho màn hình mới
        # self.load_screen_data(index)

    def load_screen_data(self, screen_index):
        """
        FAKE FUNCTION - Backend sẽ implement
        Load dữ liệu cho màn hình được chọn
        - Gọi các hàm backend tương ứng để lấy dữ liệu
        - Cập nhật UI với dữ liệu mới
        """
        pass

    def handle_logout(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Xử lý đăng xuất
        - Xóa session/token hiện tại
        - Đóng cửa sổ chính
        - Mở lại cửa sổ đăng nhập
        """
        # TODO: Backend - Implement logic đăng xuất
        # backend.logout()

        self.close()
        # Sẽ mở lại cửa sổ đăng nhập trong file client.py
