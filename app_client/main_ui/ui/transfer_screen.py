"""
Màn hình chuyển khoản
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .base_screen import BaseScreen
from .notification import NotificationManager


class TransferScreen(BaseScreen):
    """Màn hình chuyển khoản"""
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Tiêu đề
        title = QLabel("CHUYỂN KHOẢN")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Thông tin người gửi
        sender_label = QLabel("Số tài khoản người gửi:")
        sender_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(sender_label)
        
        self.sender_account = QLabel("1234567890")
        self.sender_account.setFont(QFont("Arial", 13))
        self.sender_account.setStyleSheet("color: #2c3e50; padding: 5px;")
        layout.addWidget(self.sender_account)
        
        # Số dư người gửi
        balance_label = QLabel("Số dư hiện tại:")
        balance_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(balance_label)
        
        self.balance_value = QLabel("10,000,000 VNĐ")
        self.balance_value.setFont(QFont("Arial", 14, QFont.Bold))
        self.balance_value.setStyleSheet("color: #27ae60; padding: 5px;")
        layout.addWidget(self.balance_value)
        
        # STK người nhận
        receiver_label = QLabel("Số tài khoản người nhận:")
        receiver_label.setFont(QFont("Arial", 12))
        layout.addWidget(receiver_label)
        
        self.receiver_input = QLineEdit()
        self.receiver_input.setPlaceholderText("Nhập số tài khoản người nhận")
        self.receiver_input.setFont(QFont("Arial", 12))
        self.receiver_input.setStyleSheet("""
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
        layout.addWidget(self.receiver_input)
        
        # Số tiền chuyển
        amount_label = QLabel("Số tiền chuyển:")
        amount_label.setFont(QFont("Arial", 12))
        layout.addWidget(amount_label)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Nhập số tiền (VNĐ)")
        self.amount_input.setFont(QFont("Arial", 12))
        self.amount_input.setStyleSheet("""
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
        layout.addWidget(self.amount_input)
        
        # Nút chuyển khoản
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        transfer_btn = QPushButton("CHUYỂN KHOẢN")
        transfer_btn.setFont(QFont("Arial", 12, QFont.Bold))
        transfer_btn.setFixedWidth(250)
        transfer_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        transfer_btn.clicked.connect(self.handle_transfer)
        btn_layout.addWidget(transfer_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # TODO: Backend - Gọi hàm lấy thông tin tài khoản và số dư
        # self.load_account_info()
    
    def handle_transfer(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Xử lý chuyển khoản
        - Validate số tài khoản người nhận
        - Validate số tiền
        - Kiểm tra số dư có đủ không
        - Gọi API/Function backend để thực hiện chuyển khoản
        - Cập nhật số dư
        - Hiển thị thông báo kết quả
        """
        receiver_text = self.receiver_input.text().strip()
        amount_text = self.amount_input.text().strip()
        
        # Kiểm tra số tài khoản người nhận
        if not receiver_text:
            NotificationManager.show_error(self, "Vui lòng nhập số tài khoản người nhận!")
            return
        
        if not receiver_text.isdigit():
            NotificationManager.show_error(self, "Số tài khoản không hợp lệ!")
            self.receiver_input.clear()
            return
        
        # Kiểm tra số tiền
        if not amount_text:
            NotificationManager.show_error(self, "Vui lòng nhập số tiền!")
            return
        
        if not amount_text.isdigit():
            NotificationManager.show_error(self, "Số tiền không hợp lệ!")
            self.amount_input.clear()
            return
        
        # Kiểm tra giới hạn 10 triệu
        amount = int(amount_text)
        if amount > 10000000:
            NotificationManager.show_error(self, "Số tiền giao dịch phải dưới 10 triệu")
            self.amount_input.clear()
            return
        
        # TODO: Backend - Xử lý chuyển khoản
        pass
    
    def load_account_info(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Lấy thông tin tài khoản và số dư từ database
        """
        pass
