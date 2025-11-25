import inspect
import hashlib
from typing import Type


def get_interface_hash(interface_class: Type) -> str:
    """
    Tính hash của class interface chỉ dựa trên chữ ký của các phương thức.
    Trả về chuỗi hash dưới dạng hex.
    """
    hasher = hashlib.sha256()

    # Hash tên class
    hasher.update(interface_class.__name__.encode())

    # Lấy và sắp xếp tất cả các phương thức callable
    methods = [
        name
        for name in dir(interface_class)
        if callable(getattr(interface_class, name)) and not name.startswith("__")
    ]
    methods.sort()

    # Cập nhật từng tên và chữ ký hàm vào hash
    for method_name in methods:
        method = getattr(interface_class, method_name)
        hasher.update(method_name.encode())

        try:
            sig = inspect.signature(method)
            hasher.update(str(sig).encode())
        except (ValueError, TypeError):
            # Xử lý các đối tượng không phải là hàm/callable thông thường
            pass

    return hasher.hexdigest()
