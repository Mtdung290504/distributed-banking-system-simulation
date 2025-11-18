from typing import TypeVar, Type, cast
from xmlrpc.client import ServerProxy
import inspect
import hashlib


T = TypeVar("T")


class RPCStub:
    """Stub object gọi RPC với validation."""

    def __init__(self, proxy: ServerProxy, interface_class: Type, class_hash: str):
        self._proxy = proxy
        self._interface_class = interface_class
        self._class_hash = class_hash

    def __getattr__(self, name: str):
        """Intercept method calls và forward tới RPC server."""
        if not hasattr(self._interface_class, name):
            raise AttributeError(
                f"Method '{name}' không tồn tại trong interface "
                f"{self._interface_class.__name__}"
            )

        method = getattr(self._interface_class, name)

        # Skip nếu không phải method
        if not callable(method):
            raise AttributeError(f"{name} không phải method")

        sig = inspect.signature(method)

        def rpc_call(*args, **kwargs):
            # Validate parameters
            try:
                bound = sig.bind(None, *args, **kwargs)
                bound.apply_defaults()
            except TypeError as e:
                raise TypeError(f"Lỗi tham số khi gọi {name}: {e}")

            # Gọi RPC với hash kèm theo
            rpc_method = getattr(self._proxy, name)
            return rpc_method(self._class_hash, *args, **kwargs)

        return rpc_call


def calculate_class_hash(interface_class: Type) -> str:
    """
    Tính hash của class interface dựa trên SOURCE CODE thực tế.
    Đảm bảo client và server có CHÍNH XÁC cùng interface.
    """
    hasher = hashlib.sha256()

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
            source = inspect.getsource(method)
            # Bỏ hết khoảng trắng, newline, tab. Chỉ giữ lại logic thực sự
            normalized = "".join(source.split())
            hasher.update(normalized.encode())
        except (OSError, TypeError):
            # Không lấy được source (builtin, C extension, etc.)
            # Fallback về signature
            try:
                sig = inspect.signature(method)
                hasher.update(str(sig).encode())
            except (ValueError, TypeError):
                pass

    return hasher.hexdigest()


def stub(proxy: ServerProxy, interface_class: Type[T]) -> T:
    """
    Tạo type-safe stub từ interface class.
    Trả về stub object có type hints từ interface class
    """

    # Tính hash của interface class
    class_hash = calculate_class_hash(interface_class)
    print(f"Interface [{interface_class.__name__}] hash:", class_hash)

    # Tạo stub
    stub_obj = RPCStub(proxy, interface_class, class_hash)

    # Cast về type interface
    return cast(T, stub_obj)
