from abc import ABC
from inspect import isabstract

from net import address
from helpers import constants, utils


class Remote(ABC):
    """Shared interface định nghĩa hành vi cho các remote object cần kế thừa class này"""


class RemoteObject:
    __object_id = 0

    @staticmethod
    def __next_object_ID():
        RemoteObject.__object_id += 1
        return RemoteObject.__object_id

    def __init__(self):
        self.object_id = RemoteObject.__next_object_ID()
        self.host = address.get_local_inet_address()
        self.port = constants.LOCAL_PORT
        self.signature_hash = str("")  # Khởi tạo mặc định

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

    def export(self, port=constants.LOCAL_PORT):
        try:
            self.__initialized
        except:
            raise RuntimeError(
                f"Class {self.__class__.__name__} cần gọi super().__init__() để khởi động RemoteObject"
            )

        self.port = port


if __name__ == "__main__":
    import random
    from abc import abstractmethod

    class RandomService(Remote):
        @abstractmethod
        def random(self) -> float:
            pass

    class RandomServiceImpl(RandomService, RemoteObject):
        def __init__(self, seed: int):
            super().__init__()  # Tự động tính hash của RandomService và lưu vào signature_hash
            random.seed(seed)

        def random(self) -> float:
            return random.random()

    ex = RandomServiceImpl(295)
    print(f"Object ID: {ex.object_id}")
    print(f"Host: {ex.host}")
    print(f"Port: {ex.port}")
    print(f"Interface Hash: {ex.signature_hash}")  # Hash của RandomService
    print(f"Interface Hash': {utils.get_interface_hash(RandomService)}")
    ex.export()

    print([ex.random() for _ in range(3)])
    print("Is Remote instance:", isinstance(ex, Remote))
    print("Is RemoteObject instance:", isinstance(ex, RemoteObject))
