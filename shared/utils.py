import time


def current_ms_timestamp() -> int:
    """
    Trả về timestamp hiện tại theo ms
    """
    return int(time.time() * 1000)
