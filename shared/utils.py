import time
from datetime import date, datetime


def now() -> int:
    """
    Trả về timestamp hiện tại theo ms
    """
    return int(time.time() * 1000)


def dmy_from_date(date_obj: date) -> str:
    """
    Chuyển đổi đối tượng datetime.date thành chuỗi định dạng dd-mm-yyyy
    """
    return date_obj.strftime("%d-%m-%Y")


def dmy_hms_from_timestamp(timestamp_seconds: int):
    """
    Chuyển đổi Unix Timestamp (số giây) thành chuỗi định dạng dd-mm-yyyy hh:mm:ss.
    """
    return datetime.fromtimestamp(timestamp_seconds).strftime("%d-%m-%Y %H:%M:%S")
