"""
Module chứa màn hình đăng nhập (Login) cho ứng dụng ATM Client
- Đã sửa lỗi hụt chữ (clipping) bằng cách cho phép container tự co giãn.
- Tăng kích thước cửa sổ để hiển thị đầy đủ thông tin.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QGraphicsDropShadowEffect,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from typing import Callable

# Bảng màu hiện đại
COLOR_PRIMARY = "#007BFF"
COLOR_PRIMARY_HOVER = "#0056B3"
COLOR_BACKGROUND = "#f4f7fa"
COLOR_CARD_BACKGROUND = "white"
COLOR_TEXT_DARK = "#333333"
COLOR_TEXT_MUTED = "#6c757d"
COLOR_INPUT_BORDER = "#ced4da"
COLOR_INPUT_FOCUS = "#007BFF"


class LoginWindow(QWidget):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ATM System - Đăng nhập")

        # Tăng kích thước cửa sổ chính để không bị chật chội
        self.setMinimumSize(500, 650)
        self.setStyleSheet(f"background-color: {COLOR_BACKGROUND};")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            50, 50, 50, 50
        )  # Tạo khoảng cách với viền cửa sổ

        # Container chính (Card)
        login_container = QFrame()
        # Quan trọng: Bỏ setFixedSize ở đây để Card tự nở theo chữ
        login_container.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLOR_CARD_BACKGROUND};
                border-radius: 20px;
            }}
        """
        )

        # Hiệu ứng bóng đổ
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        login_container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(login_container)
        container_layout.setContentsMargins(40, 45, 40, 45)
        container_layout.setSpacing(10)

        # 1. Tiêu đề
        title = QLabel("🏦 ATM SYSTEM")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        container_layout.addWidget(title)

        subtitle = QLabel("Chào mừng trở lại, đăng nhập để tiếp tục")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)  # Cho phép xuống dòng nếu cửa sổ quá nhỏ
        subtitle.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; margin-bottom: 20px;")
        container_layout.addWidget(subtitle)

        # 2. Số tài khoản
        account_label = QLabel("Số tài khoản")
        account_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        account_label.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        container_layout.addWidget(account_label)

        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("Nhập số tài khoản")
        self.account_input.setMinimumHeight(50)  # Đảm bảo ô nhập liệu đủ lớn
        self.account_input.setStyleSheet(
            f"""
            QLineEdit {{
                padding-left: 15px;
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }}
            QLineEdit:focus {{ border: 2px solid {COLOR_INPUT_FOCUS}; }}
        """
        )
        container_layout.addWidget(self.account_input)

        container_layout.addSpacing(10)  # Khoảng cách giữa các field

        # 3. Mã PIN
        pin_label = QLabel("Mã PIN")
        pin_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        pin_label.setStyleSheet(f"color: {COLOR_TEXT_DARK};")
        container_layout.addWidget(pin_label)

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Nhập mã PIN")
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setMinimumHeight(50)
        self.pin_input.setStyleSheet(
            f"""
            QLineEdit {{
                padding-left: 15px;
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
            }}
            QLineEdit:focus {{ border: 2px solid {COLOR_INPUT_FOCUS}; }}
        """
        )
        container_layout.addWidget(self.pin_input)

        # 4. Nút đăng nhập
        login_btn = QPushButton("ĐĂNG NHẬP")
        login_btn.setMinimumHeight(55)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        login_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                padding: 18px;
                color: white;
                border-radius: 8px;
                margin-top: 20px;
            }}
            QPushButton:hover {{ background-color: {COLOR_PRIMARY_HOVER}; }}
        """
        )
        login_btn.clicked.connect(self.handle_login)
        container_layout.addWidget(login_btn)

        # 5. Footer
        container_layout.addStretch()  # Đẩy footer xuống dưới cùng của Card
        support_label = QLabel("Cần hỗ trợ? Liên hệ: 1900-xxxx")
        support_label.setAlignment(Qt.AlignCenter)
        support_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10pt;")
        container_layout.addWidget(support_label)

        main_layout.addWidget(login_container)

        # Event Enter
        self.pin_input.returnPressed.connect(self.handle_login)
        self.account_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        # Chức năng giữ nguyên như cũ
        stk, pin = self.account_input.text(), self.pin_input.text()

        self.login_successful.emit()
