import inspect
from typing import TypeVar, Type, cast

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy

from helpers.constants import LOCAL_ADDRESS, LOCAL_PORT, SPLITOR
from helpers.types import valid_inet4_address
from helpers.utils import get_interface_hash
from net.remote import RemoteObject, Remote

T = TypeVar("T")


class LocalRegistry:
    def __init__(self):
        self._services = {}

    @staticmethod
    def __assert_valid_remote_object(remote_object: RemoteObject):
        assert isinstance(remote_object, RemoteObject) and isinstance(
            remote_object, Remote
        ), f"Remote object không hợp lệ, class[{remote_object.__class__}] phải là class con của cả RemoteObject và Remote"

    def bind(self, name: str, remote_object: RemoteObject):
        """
        Bind một remote object vào registry.

        Args:
            name: Tên để client lookup
            skeleton: Instance của class extends RemoteObject đã implement (remote object)

        Raises:
            ValueError: Nếu name đã tồn tại
        """
        self.__assert_valid_remote_object(remote_object)

        if name in self._services:
            raise ValueError(f"Service [{name}] đã được bind")

        self._services[name] = remote_object
        print(f"Bound service: [{name}]")

    def rebind(self, name: str, remote_object: RemoteObject):
        """Bind hoặc thay thế một remote object."""

        self.__assert_valid_remote_object(remote_object)

        if name in self._services:
            print(f"Rebinding service: [{name}]")
        else:
            print(f"Bound service: [{name}]")

        self._services[name] = remote_object

    def unbind(self, name: str):
        """Gỡ bỏ remote object khỏi registry bằng tên đã đăng ký từ trước."""

        if name not in self._services:
            raise ValueError(f"Service [{name}] không tồn tại!")

        del self._services[name]
        print(f"Unbound service: [{name}]")

    def list(self):
        """List tất cả tên services đã bind."""
        return list(self._services.keys())

    def __getattr__(self, name: str):
        """Điều hướng method calls đến đúng service"""

        # Không log lời gọi hàm nội bộ của rpcxml
        if not name.startswith("_") and SPLITOR in name:
            print("[REMOTE]", name)

        # Tách service name và method name
        if SPLITOR not in name:
            raise AttributeError(
                f"Invalid method format: [{name}]"
                f"Expected: [serviceName{SPLITOR}methodName]"
            )

        parts = name.split(SPLITOR, 1)
        service_name = parts[0]
        method_name = parts[1]

        # Tìm service
        if service_name not in self._services:
            raise AttributeError(f"Service [{service_name}] không tồn tại")

        service = self._services[service_name]

        # Lấy method từ service
        if not hasattr(service, method_name):
            raise AttributeError(
                f"Method [{method_name}] không tồn tại trong service [{service_name}]"
            )

        return getattr(service, method_name)


# Local server and registry
local_registry = LocalRegistry()
local_rpc_server = SimpleXMLRPCServer(addr=(str(LOCAL_ADDRESS), LOCAL_PORT))
local_rpc_server.register_instance(local_registry)
local_rpc_server.serve_forever()


class LocateRegistry:
    @staticmethod
    def createRegistry(address: tuple[str, int] | None):
        if address is None:
            return local_registry

        inet4_address, port = address
        assert valid_inet4_address(inet4_address), "Invalid IPv4 address"
        return RemoteRegistry(proxy=ServerProxy(f"http://{inet4_address}:{port}/"))


class RemoteRegistry:
    def __init__(self, proxy: ServerProxy):
        self.__proxy = proxy

    def lookup(self, service_name: str, interface: Type[T]):
        """
        Lookup remote object từ registry theo tên.

        Args:
            proxy: XML-RPC ServerProxy đã kết nối
            binding: Tuple (service_name, interface_class)
                    VD: ('calculator', CalculatorInterface)

        Returns:
            Stub object có type hints từ interface class

        Example:
            proxy = ServerProxy("http://localhost:8000/")
            calc = lookup(proxy, ('calculator', CalculatorInterface))
            result = calc.add(5, 3)
        """

        # Tính hash của interface class
        interface_hash = get_interface_hash(interface)
        print(f"Lookup interface [{interface.__name__}] hash:", interface_hash)

        # Tạo stub
        stub_obj = RPCStub(self.__proxy, interface, interface_hash, service_name)

        # Cast về type interface
        return cast(T, stub_obj)


class RPCStub:
    """Stub object gọi RPC với validation."""

    def __init__(
        self,
        proxy: ServerProxy,
        interface: Type,
        interface_hash: str,
        service_name: str,
    ):
        self.__proxy = proxy
        self.__interface = interface
        self.__interface_hash = interface_hash
        self.__service_name = service_name

    def __getattr__(self, name: str):
        """Chặn lời gọi method và gọi server proxy."""

        if not hasattr(self.__interface, name):
            raise AttributeError(
                f"Method [{name}] không tồn tại trong interface: [{self.__interface.__name__}]"
            )

        method = getattr(self.__interface, name)

        # Skip nếu không phải method
        if not callable(method):
            raise AttributeError(f"Attribute [{name}] không phải method")
        sig = inspect.signature(method)

        def remote_call(*args, **kwargs):
            # Validate parameters
            try:
                bound = sig.bind(None, *args, **kwargs)
                bound.apply_defaults()
            except TypeError as e:
                raise TypeError(f"Lỗi tham số khi gọi [{name}]: {e}")

            # Gọi proxy với format: serviceName[SPLITOR]methodName
            rpc_method_name = f"{self.__service_name}{SPLITOR}{name}"
            rpc_method = getattr(self.__proxy, rpc_method_name)
            return rpc_method(self.__interface_hash, *args, **kwargs)

        return remote_call
