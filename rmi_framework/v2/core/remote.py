"""
Remote Object Base Classes

Module này cung cấp các class cơ bản cho RMI framework:
- Remote: Marker interface cho các remote objects
- RemoteObject: Base class với auto ID generation và interface hashing
"""

import threading
from abc import ABC
from inspect import isabstract
from typing import TYPE_CHECKING, Optional

from ..helpers.utils import get_interface_hash

if TYPE_CHECKING:
    from helpers.types import RemoteReference


class Remote(ABC):
    """
    Marker Interface.

    Tất cả remote object interfaces phải kế thừa class này.
    Đây là abstract class để đánh dấu một object có thể được gọi từ xa.
    """

    pass


class RemoteObject:
    """
    Base class cho tất cả remote objects.

    Class này cung cấp:
    - Auto-generated unique object ID (thread-safe)
    - Interface signature hashing để validate compatibility
    - Serialization thành remote reference
    - Tracking exported_name để dev có thể tự unbind

    Usage:
        class MyInterface(Remote):
            @abstractmethod
            def do_something(self): pass

        class MyService(RemoteObject, MyInterface):
            def __init__(self):
                super().__init__()  # Bắt buộc phải gọi!

            def do_something(self):
                return "Hello"

        # Sau khi pass vào remote method, object tự động export
        # và có thể unbind sau:
        if my_service.exported_name:
            registry.unbind(my_service.exported_name)
    """

    # Class-level state cho ID generation
    __object_id = 0
    __id_lock = threading.Lock()

    @staticmethod
    def __next_object_ID() -> int:
        """
        Generate unique object ID (thread-safe).

        Sử dụng lock để đảm bảo không có race condition khi
        nhiều threads cùng tạo RemoteObject.

        Returns:
            int: Unique object ID
        """
        with RemoteObject.__id_lock:
            RemoteObject.__object_id += 1
            return RemoteObject.__object_id

    def __init__(self):
        """
        Khởi tạo RemoteObject.

        - Generate unique object ID
        - Tìm và hash abstract interface (kế thừa Remote)
        - Khởi tạo exported_name = None (sẽ được set khi auto-export)

        Raises:
            ValueError: Nếu class không implement interface Remote hợp lệ
        """
        # Generate unique ID
        self.object_id = RemoteObject.__next_object_ID()

        # Tìm abstract interface và tính hash
        self.signature_hash = self._find_and_hash_interface()

        # Validate signature hash
        if not self.signature_hash:
            raise ValueError(
                f"Class [{self.__class__.__name__}] không implement Remote interface hợp lệ. "
                f"Cần có ít nhất một abstract class kế thừa Remote trong hierarchy."
            )

        # Track exported name (sẽ được set khi auto-export vào registry)
        self.exported_name: Optional[str] = None

        # Đánh dấu đã khởi tạo thành công
        self.__initialized = True

    def _find_and_hash_interface(self) -> str:
        """
        Tìm abstract interface class và tính signature hash.

        Duyệt qua method resolution order (MRO) để tìm abstract class
        đầu tiên kế thừa Remote (không phải chính Remote).

        Returns:
            str: Interface hash hoặc empty string nếu không tìm thấy
        """
        for cls in self.__class__.__mro__:
            # Bỏ qua RemoteObject và object
            if cls is RemoteObject or cls is object:
                continue

            # Bỏ qua chính Remote marker interface
            if cls is Remote:
                continue

            # Tìm abstract class kế thừa Remote
            if isabstract(cls) and issubclass(cls, Remote):
                return get_interface_hash(cls)

        # Không tìm thấy interface hợp lệ
        return ""

    def _commit(self):
        """
        Validate rằng __init__ của RemoteObject đã được gọi.

        Method này được gọi trước khi serialize để đảm bảo
        object đã được khởi tạo đúng cách.

        Raises:
            RuntimeError: Nếu __init__ chưa được gọi
        """
        # Check xem attribute __initialized có tồn tại không
        # Dùng getattr với default False để tránh AttributeError
        if not getattr(self, "_RemoteObject__initialized", False):
            raise RuntimeError(
                f"Class [{self.__class__.__name__}] phải gọi `super().__init__()` "
                f"trong hàm __init__ để khởi tạo RemoteObject"
            )

    def serialize(self, service_name: str, host: str, port: int) -> "RemoteReference":
        """
        Serialize RemoteObject thành remote reference.

        Remote reference là một dictionary chứa thông tin để
        client có thể tạo stub và gọi object từ xa.

        Args:
            service_name: Tên service trong registry (phải unique)
            host: Địa chỉ IP của registry
            port: Port của registry

        Returns:
            RemoteReference: Dictionary chứa thông tin remote reference

        Raises:
            RuntimeError: Nếu RemoteObject chưa được khởi tạo đúng
            AssertionError: Nếu service_name chứa ký tự không hợp lệ
        """
        # Validate object đã được khởi tạo
        self._commit()

        # Validate service_name không chứa ký tự đặc biệt
        # (Defensive programming - tránh conflict với SPLITOR)
        assert (
            "@" not in service_name
        ), f"Service name [{service_name}] không được chứa ký tự '@'"

        # Tạo remote reference
        return {
            "__remote_ref__": True,
            "service_name": service_name,
            "host": host,
            "port": port,
            "signature_hash": self.signature_hash,
        }
