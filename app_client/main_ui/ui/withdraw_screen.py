"""
Màn hình rút tiền
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .base_screen import BaseScreen
from .notification import NotificationManager


class WithdrawScreen(BaseScreen):
    """Màn hình rút tiền"""
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Tiêu đề
        title = QLabel("RÚT TIỀN")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Hiển thị số dư
        balance_label = QLabel("Số dư hiện tại:")
        balance_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(balance_label)
        
        self.balance_value = QLabel("10,000,000 VNĐ")
        self.balance_value.setFont(QFont("Arial", 16, QFont.Bold))
        self.balance_value.setStyleSheet("color: #27ae60; padding: 10px;")
        layout.addWidget(self.balance_value)
        
        # Nhập số tiền
        amount_label = QLabel("Nhập số tiền muốn rút:")
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
        
        # Nút rút tiền
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        withdraw_btn = QPushButton("RÚT TIỀN")
        withdraw_btn.setFont(QFont("Arial", 12, QFont.Bold))
        withdraw_btn.setFixedWidth(250)
        withdraw_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        withdraw_btn.clicked.connect(self.handle_withdraw)
        btn_layout.addWidget(withdraw_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # TODO: Backend - Gọi hàm lấy số dư từ database
        # self.load_balance()
    
    def handle_withdraw(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Xử lý rút tiền từ tài khoản
        - Validate số tiền nhập vào
        - Kiểm tra số dư có đủ không
        - Gọi API/Function backend để rút tiền
        - Cập nhật số dư mới
        - Hiển thị thông báo kết quả
        """
        amount_text = self.amount_input.text().strip()
        
        # Kiểm tra nếu rỗng
        if not amount_text:
            NotificationManager.show_error(self, "Vui lòng nhập số tiền!")
            return
        
        # Kiểm tra chỉ chứa số
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
        
        # TODO: Backend - Xử lý rút tiền
        pass
    
    def load_balance(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Lấy số dư hiện tại từ database
        """
        pass
