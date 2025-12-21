"""
Module chứa các màn hình (screens) của ứng dụng ATM Client
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class BaseScreen(QWidget):
    """Lớp cơ sở cho tất cả các màn hình"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Khởi tạo giao diện - sẽ được override bởi các lớp con"""
        pass


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


class DepositScreen(BaseScreen):
    """Màn hình nạp tiền"""
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Tiêu đề
        title = QLabel("NẠP TIỀN")
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
        amount_label = QLabel("Nhập số tiền muốn nạp:")
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
        
        # Nút nạp tiền
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        deposit_btn = QPushButton("NẠP TIỀN")
        deposit_btn.setFont(QFont("Arial", 12, QFont.Bold))
        deposit_btn.setFixedWidth(250)
        deposit_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        deposit_btn.clicked.connect(self.handle_deposit)
        btn_layout.addWidget(deposit_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # TODO: Backend - Gọi hàm lấy số dư từ database
        # self.load_balance()
    
    def handle_deposit(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Xử lý nạp tiền vào tài khoản
        - Validate số tiền nhập vào
        - Gọi API/Function backend để nạp tiền
        - Cập nhật số dư mới
        - Hiển thị thông báo kết quả
        """
        pass
    
    def load_balance(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Lấy số dư hiện tại từ database
        """
        pass


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
        pass
    
    def load_balance(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Lấy số dư hiện tại từ database
        """
        pass


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
        pass
    
    def load_account_info(self):
        """
        FAKE FUNCTION - Backend sẽ implement
        Lấy thông tin tài khoản và số dư từ database
        """
        pass


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
        pass
