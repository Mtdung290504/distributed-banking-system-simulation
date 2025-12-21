"""
Module chứa lớp cơ sở cho tất cả các màn hình
"""
from PyQt5.QtWidgets import QWidget


class BaseScreen(QWidget):
    """Lớp cơ sở cho tất cả các màn hình"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Khởi tạo giao diện - sẽ được override bởi các lớp con"""
        pass
