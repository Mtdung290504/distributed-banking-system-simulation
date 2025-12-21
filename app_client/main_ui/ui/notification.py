"""
Module xử lý thông báo (Notification) cho ứng dụng ATM
"""
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import os


class NotificationManager:
    """
    Quản lý hiển thị thông báo cho người dùng
    Hỗ trợ 3 loại thông báo: success, error, info
    """
    
    @staticmethod
    def show_notification(parent, title, message, notification_type="info"):
        """
        Hiển thị thông báo cho người dùng
        
        Args:
            parent: Widget cha
            title: Tiêu đề thông báo
            message: Nội dung thông báo
            notification_type: Loại thông báo ('success', 'error', 'info')
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # Căn giữa text
        msg_box.setTextFormat(Qt.RichText)
        
        if notification_type == "success":
            # Thông báo thành công - màu xanh
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #d4edda;
                }
                QMessageBox QLabel {
                    color: #155724;
                    font-size: 14px;
                    font-weight: bold;
                }
                QMessageBox QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    font-size: 13px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #218838;
                }
            """)
            
        elif notification_type == "error":
            # Thông báo lỗi - màu đỏ
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #f8d7da;
                }
                QMessageBox QLabel {
                    color: #721c24;
                    font-size: 14px;
                    font-weight: bold;
                }
                QMessageBox QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    font-size: 13px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            
        else:  # info
            # Thông báo thông tin - không màu nền, icon đen
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #000000;
                    font-size: 14px;
                }
                QMessageBox QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    font-size: 13px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
        
        # Hiển thị thông báo
        msg_box.exec_()
    
    @staticmethod
    def show_success(parent, message, title="Thành công"):
        """Hiển thị thông báo thành công"""
        NotificationManager.show_notification(parent, title, message, "success")
    
    @staticmethod
    def show_error(parent, message, title="Lỗi"):
        """Hiển thị thông báo lỗi"""
        NotificationManager.show_notification(parent, title, message, "error")
    
    @staticmethod
    def show_info(parent, message, title="Thông báo"):
        """Hiển thị thông báo thông tin"""
        NotificationManager.show_notification(parent, title, message, "info")
