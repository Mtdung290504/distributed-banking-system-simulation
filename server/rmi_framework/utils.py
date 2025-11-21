# utils.py
from typing import Type as _Type
import inspect as _inspect
import hashlib as _hashlib


def get_class_hash(interface_class: _Type) -> str:
    """
    Tính hash của class interface dựa trên SOURCE CODE thực tế.
    Đảm bảo client và server có CHÍNH XÁC cùng interface.
    """
    hasher = _hashlib.sha256()

    # Hash tên class
    hasher.update(interface_class.__name__.encode())

    # Lấy tất cả methods
    methods = []
    for name in dir(interface_class):
        attr = getattr(interface_class, name)
        if callable(attr):
            methods.append(name)

    # Sort để đảm bảo thứ tự nhất quán
    methods.sort()

    # Hash từng method SOURCE CODE
    for method_name in methods:
        method = getattr(interface_class, method_name)

        # Hash method name
        hasher.update(method_name.encode())

        # Hash SOURCE CODE của method
        try:
            source = _inspect.getsource(method)
            # Bỏ hết khoảng trắng, newline, tab. Chỉ giữ lại logic thực sự
            normalized = "".join(source.split())
            hasher.update(normalized.encode())
        except (OSError, TypeError):
            # Không lấy được source (builtin, C extension, etc.)
            # Fallback về signature
            try:
                sig = _inspect.signature(method)
                hasher.update(str(sig).encode())
            except (ValueError, TypeError):
                pass

    return hasher.hexdigest()
