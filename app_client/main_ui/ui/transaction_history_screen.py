"""
Màn hình lịch sử giao dịch
"""
from PyQt5.QtWidgets import (
    QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .base_screen import BaseScreen


class TransactionHistoryScreen(BaseScreen):
    """Màn hình lịch sử giao dịch"""
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Tiêu đề
        title = QLabel("LỊCH SỬ GIAO DỊCH")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Bảng lịch sử giao dịch
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Ngày/Giờ", "Loại giao dịch", "STK gửi", "STK nhận", "Số tiền"
        ])
        
        # Style cho bảng
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        
        # Cấu hình bảng
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Dữ liệu mẫu
        sample_data = [
            ["13/12/2025 10:30", "Nạp tiền", "-", "1234567890", "1,000,000 VNĐ"],
            ["12/12/2025 15:20", "Rút tiền", "1234567890", "-", "500,000 VNĐ"],
            ["11/12/2025 09:15", "Chuyển khoản", "1234567890", "9876543210", "2,000,000 VNĐ"],
        ]
        
        self.table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                self.table.setItem(row, col, QTableWidgetItem(value))
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        # TODO: Backend - Gọi hàm lấy lịch sử giao dịch từ database
        # self.load_transaction_history()
    
    def load_transaction_history(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Lấy lịch sử giao dịch từ database và hiển thị lên bảng
        - Query database để lấy lịch sử giao dịch
        - Format dữ liệu
        - Hiển thị lên QTableWidget
        """
        pass
