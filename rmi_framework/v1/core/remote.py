from abc import ABC
from inspect import isabstract
import threading

from helpers.utils import get_interface_hash
from helpers.types import RemoteReference


class Remote(ABC):
    """
    Marker Interface.
    Shared interface định nghĩa hành vi cho các remote object cần kế thừa class này
    """


class RemoteObject:
    """
    Base class cho tất cả remote objects
    """

    __object_id = 0
    __id_lock = threading.Lock()

    @staticmethod
    def __next_object_ID():
        with RemoteObject.__id_lock:
            RemoteObject.__object_id += 1
            return RemoteObject.__object_id

    def __init__(self):
        self.object_id = RemoteObject.__next_object_ID()
        self.signature_hash = ""  # Hash của interface

        # Tìm abstract interface class kế thừa Remote
        for cls in self.__class__.__mro__:
            # Bỏ qua RemoteObject và object
            if cls is RemoteObject or cls is object:
                continue

            # Chỉ lấy abstract class và là subclass của Remote (không phải chính Remote)
            if isabstract(cls) and issubclass(cls, Remote) and cls is not Remote:
                # Tính hash cho interface class
                self.signature_hash = get_interface_hash(cls)
                break

        self.__initialized = True

    def _commit(self):
        """Đảm bảo class con đã gọi hàm `__init__` của class này"""

        try:
            self.__initialized
        except Exception:
            raise RuntimeError(
                f"Class {self.__class__.__name__} cần gọi `super().__init__()` để khởi động RemoteObject"
            )

    def serialize(self, service_name: str, host: str, port: int) -> RemoteReference:
        """
        Serialize RemoteObject thành remote reference để truyền qua mạng.

        Args:
            service_name: Tên của dịch vụ remote.
            host: Địa chỉ IP host.
            port: Cổng mạng.

        Raises:
            RuntimeError: Khi class của object chưa gọi hàm `__init__` của class `RemoteObject`
        """

        self._commit()

        return {
            "__remote_ref__": True,
            "service_name": service_name,
            "host": host,
            "port": port,
            "signature_hash": self.signature_hash,
        }
