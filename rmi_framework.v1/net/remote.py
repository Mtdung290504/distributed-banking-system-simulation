from abc import ABC
from inspect import isabstract

from net import address
from helpers import constants, utils


class Remote(ABC):
    """Shared interface định nghĩa hành vi cho các remote object cần kế thừa class này"""


class RemoteObject:
    """Base class cho tất cả remote objects"""

    __object_id = 0

    @staticmethod
    def __next_object_ID():
        RemoteObject.__object_id += 1
        return RemoteObject.__object_id

    def __init__(self):
        self.object_id = RemoteObject.__next_object_ID()
        self.host = address.get_local_inet_address()
        self.port = constants.LOCAL_PORT
        self.signature_hash = None  # Hash của interface

        # Tìm abstract interface class kế thừa Remote
        for cls in self.__class__.__mro__:
            # Bỏ qua RemoteObject và object
            if cls is RemoteObject or cls is object:
                continue

            # Chỉ lấy abstract class và là subclass của Remote (không phải chính Remote)
            if isabstract(cls) and issubclass(cls, Remote) and cls is not Remote:
                # Tính hash cho interface class
                self.signature_hash = utils.get_interface_hash(cls)
                break

        self.__initialized = True

    def __to_remote_ref__(self):
        """
        Serialize RemoteObject thành remote reference để truyền qua network.
        Dùng cho callback mechanism.
        """

        try:
            self.__initialized
        except:
            raise RuntimeError(
                f"Class {self.__class__.__name__} cần gọi super().__init__() để khởi động RemoteObject"
            )

        service_name = f"{self.__class__.__name__}_{self.object_id}"

        return {
            "__remote_ref__": True,
            "service_name": service_name,
            "host": self.host,
            "port": self.port,
            "signature_hash": self.signature_hash,
        }
