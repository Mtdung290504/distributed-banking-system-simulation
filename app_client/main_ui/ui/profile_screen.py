"""
Màn hình thông tin người dùng
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .base_screen import BaseScreen


class ProfileScreen(BaseScreen):
    """Màn hình thông tin người dùng"""
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Tiêu đề
        title = QLabel("THÔNG TIN NGƯỜI DÙNG")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Container cho thông tin
        info_container = QFrame()
        info_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 30px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)
        
        # Các trường thông tin
        info_fields = [
            ("Họ và tên", "Nguyễn Văn A"),
            ("Ngày sinh", "01/01/1990"),
            ("Số CCCD", "001234567890"),
            ("Số điện thoại", "0901234567"),
            ("Số tài khoản", "1234567890"),
            ("Số dư hiện tại", "10,000,000 VNĐ")
        ]
        
        for label_text, value_text in info_fields:
            # Container cho mỗi hàng
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(20)
            
            # Label - căn trái, độ dài cố định
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 12, QFont.Bold))
            label.setStyleSheet("color: #34495e;")
            label.setMinimumWidth(200)
            label.setMaximumWidth(200)
            label.setAlignment(Qt.AlignLeft)
            row_layout.addWidget(label)
            
            # Value - căn trái
            value = QLabel(value_text)
            value.setFont(QFont("Arial", 12))
            value.setStyleSheet("""
                color: #2c3e50;
                background-color: #ecf0f1;
                padding: 10px 15px;
                border-radius: 5px;
            """)
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            row_layout.addWidget(value, 1)
            
            row_widget.setLayout(row_layout)
            info_layout.addWidget(row_widget)
        
        info_container.setLayout(info_layout)
        layout.addWidget(info_container)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # TODO: Backend - Gọi hàm lấy thông tin người dùng từ database
        # self.load_user_info()
    
    def load_user_info(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Lấy thông tin người dùng từ database và hiển thị lên UI
        """
        pass
