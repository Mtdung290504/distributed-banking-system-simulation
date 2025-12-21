"""
Màn hình đổi mã PIN
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .base_screen import BaseScreen
from .notification import NotificationManager


class ChangePinScreen(BaseScreen):
    """Màn hình đổi mã PIN"""
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Tiêu đề
        title = QLabel("ĐỔI MÃ PIN")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Mã PIN cũ
        old_pin_label = QLabel("Mã PIN cũ:")
        old_pin_label.setFont(QFont("Arial", 12))
        layout.addWidget(old_pin_label)
        
        self.old_pin_input = QLineEdit()
        self.old_pin_input.setPlaceholderText("Nhập mã PIN cũ")
        self.old_pin_input.setEchoMode(QLineEdit.Password)
        self.old_pin_input.setFont(QFont("Arial", 12))
        self.old_pin_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.old_pin_input)
        
        # Mã PIN mới
        new_pin_label = QLabel("Mã PIN mới:")
        new_pin_label.setFont(QFont("Arial", 12))
        layout.addWidget(new_pin_label)
        
        self.new_pin_input = QLineEdit()
        self.new_pin_input.setPlaceholderText("Nhập mã PIN mới")
        self.new_pin_input.setEchoMode(QLineEdit.Password)
        self.new_pin_input.setFont(QFont("Arial", 12))
        self.new_pin_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.new_pin_input)
        
        # Xác nhận mã PIN mới
        confirm_pin_label = QLabel("Xác nhận mã PIN mới:")
        confirm_pin_label.setFont(QFont("Arial", 12))
        layout.addWidget(confirm_pin_label)
        
        self.confirm_pin_input = QLineEdit()
        self.confirm_pin_input.setPlaceholderText("Nhập lại mã PIN mới")
        self.confirm_pin_input.setEchoMode(QLineEdit.Password)
        self.confirm_pin_input.setFont(QFont("Arial", 12))
        self.confirm_pin_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.confirm_pin_input)
        
        # Nút đổi PIN
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        change_pin_btn = QPushButton("ĐỔI MÃ PIN")
        change_pin_btn.setFont(QFont("Arial", 12, QFont.Bold))
        change_pin_btn.setFixedWidth(250)
        change_pin_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        change_pin_btn.clicked.connect(self.handle_change_pin)
        btn_layout.addWidget(change_pin_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def handle_change_pin(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Xử lý đổi mã PIN
        - Validate mã PIN cũ
        - Validate mã PIN mới
        - Kiểm tra mã PIN mới và xác nhận có khớp không
        - Gọi API/Function backend để đổi PIN
        - Hiển thị thông báo kết quả
        """
        old_pin = self.old_pin_input.text().strip()
        new_pin = self.new_pin_input.text().strip()
        confirm_pin = self.confirm_pin_input.text().strip()
        
        # Kiểm tra mã PIN cũ
        if not old_pin:
            NotificationManager.show_error(self, "Vui lòng nhập mã PIN cũ!")
            return
        
        if not old_pin.isdigit():
            NotificationManager.show_error(self, "Mã PIN không hợp lệ!")
            self.old_pin_input.clear()
            return
        
        # Kiểm tra mã PIN mới
        if not new_pin:
            NotificationManager.show_error(self, "Vui lòng nhập mã PIN mới!")
            return
        
        if not new_pin.isdigit():
            NotificationManager.show_error(self, "Mã PIN không hợp lệ!")
            self.new_pin_input.clear()
            return
        
        # Kiểm tra xác nhận mã PIN
        if not confirm_pin:
            NotificationManager.show_error(self, "Vui lòng xác nhận mã PIN mới!")
            return
        
        if not confirm_pin.isdigit():
            NotificationManager.show_error(self, "Mã PIN không hợp lệ!")
            self.confirm_pin_input.clear()
            return
        
        # Kiểm tra mã PIN mới và xác nhận có khớp không
        if new_pin != confirm_pin:
            NotificationManager.show_error(self, "Mã PIN mới và xác nhận không khớp!")
            self.new_pin_input.clear()
            self.confirm_pin_input.clear()
            return
        
        # TODO: Backend - Xử lý đổi PIN
        pass
