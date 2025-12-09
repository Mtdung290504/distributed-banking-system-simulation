import socket

cache_private_IP: None | str = None


def get_local_inet_address(refresh: bool = False):
    """
    Tạo một kết nối socket tạm thời tới một địa chỉ ngoài (ví dụ: Google DNS 8.8.8.8)
    để tìm ra IP local của thiết bị đang dùng để thực hiện kết nối.
    """
    global cache_private_IP

    if not refresh and cache_private_IP:
        return cache_private_IP

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        cache_private_IP = s.getsockname()[0]
        s.close()

        assert cache_private_IP is not None, "IP nhận được không thể là None tại đây"
        return cache_private_IP
    except Exception as e:
        return f"Lỗi khi lấy IP Private: {e}"


if __name__ == "__main__":
    print(get_local_inet_address(refresh=True))
