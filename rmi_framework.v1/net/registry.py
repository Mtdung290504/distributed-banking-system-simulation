import inspect
from typing import TypeVar, Type, cast, get_type_hints
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy

from helpers.constants import LOCAL_ADDRESS, LOCAL_PORT, SPLITOR
from helpers.types import valid_inet4_address
from helpers.utils import get_interface_hash
from net.remote import RemoteObject, Remote

T = TypeVar("T")


class ServiceWrapper:
    """Wrapper để validate interface hash trước khi gọi method"""

    def __init__(self, service: RemoteObject):
        self._service = service
        self._expected_hash = service.signature_hash

    def __getattr__(self, name: str):
        """Chặn method calls và validate hash"""

        # Lấy method gốc từ service
        if not hasattr(self._service, name):
            raise AttributeError(f"Method [{name}] không tồn tại trong service")

        method = getattr(self._service, name)

        if not callable(method):
            raise AttributeError(f"Attribute [{name}] không phải method")

        def validated_call(client_hash: str, *args, **kwargs):
            # Validate interface hash
            if client_hash != self._expected_hash:
                raise ValueError(
                    f"Interface mismatch! "
                    f"Expected: {self._expected_hash}, Got: {client_hash}"
                )
            print("Debug", args)

            # Deserialize arguments (xử lý remote references/callbacks)
            deserialized_args = self._deserialize_arguments(method, args)
            print(
                f"[ServiceWrapper] Deserialized args for method {name}: {deserialized_args}"
            )

            # Gọi method gốc
            result = method(*deserialized_args, **kwargs)

            # Serialize result nếu là RemoteObject (cho return callback)
            if isinstance(result, RemoteObject):
                return result.__to_remote_ref__()

            return result

        return validated_call

    def _deserialize_arguments(self, method, args):
        """
        Deserialize arguments, chuyển remote references thành RPCStub.
        """
        sig = inspect.signature(method)
        type_hints = get_type_hints(method)

        deserialized = []

        # SỬA LỖI: Không dùng [1:] vì bound method signature không chứa 'self'
        param_names = list(sig.parameters.keys())

        for i, arg_value in enumerate(args):
            # Nếu vượt quá số params định nghĩa (trường hợp *args), giữ nguyên
            if i >= len(param_names):
                deserialized.append(arg_value)
                continue

            param_name = param_names[i]
            expected_type = type_hints.get(param_name)

            # Check nếu arg là remote reference (dict chứa cờ hiệu)
            # Giả định dict có key "__remote_ref__" hoặc format tương tự
            if isinstance(arg_value, dict) and arg_value.get("__remote_ref__"):

                # Cần kiểm tra inspect.isclass trước khi gọi issubclass
                # để tránh lỗi nếu expected_type là Generic (ví dụ List[int])
                if (
                    expected_type
                    and inspect.isclass(expected_type)
                    and issubclass(expected_type, Remote)
                ):

                    print(
                        f"  [Deserialize] Found RemoteRef for param '{param_name}', transforming to Stub..."
                    )

                    # Tạo reverse proxy về client
                    proxy = ServerProxy(
                        f"http://{arg_value['host']}:{arg_value['port']}/",
                        allow_none=True,
                    )

                    stub = RPCStub(
                        proxy=proxy,
                        interface=expected_type,
                        interface_hash=arg_value.get("signature_hash", ""),
                        service_name=arg_value.get("service_name", ""),
                    )
                    deserialized.append(stub)
                else:
                    # Nếu là dict remote ref nhưng param không có type hint là Remote subclass
                    # Bạn có thể chọn raise lỗi hoặc để nguyên dict.
                    # Raise lỗi sẽ an toàn hơn về mặt logic RMI.
                    raise TypeError(
                        f"Parameter [{param_name}] nhận được Remote Reference nhưng "
                        f"Type Hint [{expected_type}] không phải là subclass của Remote."
                    )
            else:
                deserialized.append(arg_value)

        return deserialized


class LocalRegistry:
    """Registry quản lý các remote services trên local machine"""

    def __init__(self):
        self._services = {}
        self._server = None
        self._is_running = False

    @staticmethod
    def __assert_valid_remote_object(remote_object: RemoteObject):
        """Validate remote object phải kế thừa cả RemoteObject và Remote"""
        assert isinstance(remote_object, RemoteObject) and isinstance(
            remote_object, Remote
        ), (
            f"Remote object không hợp lệ, class [{remote_object.__class__.__name__}] "
            f"phải là class con của cả RemoteObject và Remote"
        )

        # Validate có signature hash
        if not remote_object.signature_hash:
            raise ValueError(
                f"Remote object [{remote_object.__class__.__name__}] "
                f"không có interface hash (không implement Remote interface?)"
            )

    def bind(self, name: str, remote_object: RemoteObject):
        """
        Bind một remote object vào registry.

        Args:
            name: Tên để client lookup
            remote_object: Instance của class extends RemoteObject và implement Remote interface

        Raises:
            ValueError: Nếu name đã tồn tại hoặc object không hợp lệ
            RuntimeError: Nếu bind khi server đang chạy
        """
        if self._is_running:
            raise RuntimeError("Không thể bind service khi server đang chạy")

        self.__assert_valid_remote_object(remote_object)

        if name in self._services:
            raise ValueError(f"Service [{name}] đã được bind")

        # Wrap service với validation layer
        self._services[name] = ServiceWrapper(remote_object)
        print(f"[Registry] Bound service: [{name}]")

    def rebind(self, name: str, remote_object: RemoteObject):
        """Bind hoặc thay thế một remote object"""
        if self._is_running:
            raise RuntimeError("Không thể rebind service khi server đang chạy")

        self.__assert_valid_remote_object(remote_object)

        if name in self._services:
            print(f"[Registry] Rebinding service: [{name}]")
        else:
            print(f"[Registry] Bound service: [{name}]")

        self._services[name] = ServiceWrapper(remote_object)

    def unbind(self, name: str):
        """Gỡ bỏ remote object khỏi registry"""
        if self._is_running:
            raise RuntimeError("Không thể unbind service khi server đang chạy")

        if name not in self._services:
            raise ValueError(f"Service [{name}] không tồn tại!")

        del self._services[name]
        print(f"[Registry] Unbound service: [{name}]")

    def list(self):
        """List tất cả tên services đã bind"""
        return list(self._services.keys())

    def listen(self):
        """
        Start RPC server (BLOCKING).
        Server sẽ listen trên LOCAL_ADDRESS:LOCAL_PORT từ constants.

        Hàm này block cho đến khi server shutdown (Ctrl+C).

        Raises:
            RuntimeError: Nếu server đã đang chạy
        """
        if self._is_running:
            raise RuntimeError("Server đã đang chạy")

        # Tạo XML-RPC server
        self._server = SimpleXMLRPCServer(
            addr=(str(LOCAL_ADDRESS), LOCAL_PORT),
            allow_none=True,
            logRequests=False,  # Tắt log mặc định, dùng custom log
        )

        # Register registry instance để handle method calls
        self._server.register_instance(self)

        self._is_running = True
        print(f"[RPC Server] Listening on {LOCAL_ADDRESS}:{LOCAL_PORT}")
        print(f"[RPC Server] Registered services: {self.list()}")
        print("[RPC Server] Press Ctrl+C to stop")

        try:
            self._server.serve_forever()
        except KeyboardInterrupt:
            print("\n[RPC Server] Shutting down...")
        finally:
            self._server.server_close()
            self._is_running = False
            print("[RPC Server] Stopped")

    def __getattr__(self, name: str):
        """
        Điều hướng method calls từ XML-RPC đến đúng service.
        Format: serviceName[SPLITOR]methodName
        """

        # Log lời gọi remote (không log internal calls của XML-RPC)
        if not name.startswith("_") and SPLITOR in name:
            print(f"[RPC Call] {name}")

        # Validate format
        if SPLITOR not in name:
            raise AttributeError(
                f"Invalid method format: [{name}]. "
                f"Expected: serviceName{SPLITOR}methodName"
            )

        # Tách service name và method name
        parts = name.split(SPLITOR, 1)
        service_name = parts[0]
        method_name = parts[1]

        # Tìm service
        if service_name not in self._services:
            raise AttributeError(f"Service [{service_name}] không tồn tại")

        service_wrapper = self._services[service_name]

        # Lấy method từ service wrapper (đã có validation)
        if not hasattr(service_wrapper, method_name):
            raise AttributeError(
                f"Method [{method_name}] không tồn tại trong service [{service_name}]"
            )

        return getattr(service_wrapper, method_name)


class LocateRegistry:
    """Factory để tạo registry (local hoặc remote)"""

    @staticmethod
    def createRegistry(address: tuple[str, int] | None = None):
        """
        Tạo registry instance.

        Args:
            address: Tuple (host, port). Nếu None, trả về local registry.

        Returns:
            LocalRegistry nếu address=None, RemoteRegistry nếu có address.
        """
        if address is None:
            return local_registry

        inet4_address, port = address
        assert valid_inet4_address(inet4_address), "Invalid IPv4 address"

        return RemoteRegistry(
            proxy=ServerProxy(f"http://{inet4_address}:{port}/", allow_none=True)
        )


class RemoteRegistry:
    """Client-side registry để lookup remote services"""

    def __init__(self, proxy: ServerProxy):
        self.__proxy = proxy

    def lookup(self, service_name: str, interface: Type[T]) -> T:
        """
        Lookup remote object từ registry theo tên.

        Args:
            service_name: Tên service đã bind trên server
            interface: Interface class để type checking và stub creation

        Returns:
            Stub object có type hints từ interface class

        Example:
            registry = LocateRegistry.createRegistry(("192.168.1.100", 8000))
            calc = registry.lookup("calculator", CalculatorInterface)
            result = calc.add(5, 3)  # RPC call
        """

        # Tính hash của interface class
        interface_hash = get_interface_hash(interface)
        print(f"[Lookup] Interface [{interface.__name__}] hash: {interface_hash}")

        # Tạo stub
        stub_obj = RPCStub(self.__proxy, interface, interface_hash, service_name)

        # Cast về type interface để có type hints
        return cast(T, stub_obj)


class RPCStub:
    """Client-side stub gọi RPC với validation"""

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
        """Chặn lời gọi method và gọi server qua proxy"""

        # Validate method tồn tại trong interface
        if not hasattr(self.__interface, name):
            raise AttributeError(
                f"Method [{name}] không tồn tại trong interface [{self.__interface.__name__}]"
            )

        method = getattr(self.__interface, name)

        # Skip nếu không phải method
        if not callable(method):
            raise AttributeError(f"Attribute [{name}] không phải method")

        sig = inspect.signature(method)

        def remote_call(*args, **kwargs):
            # Validate parameters với signature
            try:
                bound = sig.bind(None, *args, **kwargs)  # None cho 'self'
                bound.apply_defaults()
            except TypeError as e:
                raise TypeError(f"Lỗi tham số khi gọi [{name}]: {e}")

            # Serialize arguments (xử lý RemoteObject thành remote reference)
            serialized_args = self._serialize_arguments(args)

            # Gọi proxy với format: serviceName[SPLITOR]methodName
            rpc_method_name = f"{self.__service_name}{SPLITOR}{name}"
            rpc_method = getattr(self.__proxy, rpc_method_name)

            # RPC call với hash validation
            print(f"[RPC Stub] Calling {rpc_method_name} with args: {serialized_args}")
            result = rpc_method(self.__interface_hash, *serialized_args, **kwargs)

            # Deserialize result nếu là remote reference
            if isinstance(result, dict) and result.get("__remote_ref__"):
                # Server trả về callback - tạo stub
                # TODO: Cần type hint của return type để biết interface
                pass

            return result

        return remote_call

    def _serialize_arguments(self, args):
        """Serialize arguments, chuyển RemoteObject thành remote reference"""
        serialized = []

        for arg in args:
            if isinstance(arg, RemoteObject):
                # Auto-bind callback vào local registry
                service_name = f"{arg.__class__.__name__}_{arg.object_id}"

                if service_name not in local_registry.list():
                    # Bind callback vào registry để server có thể gọi lại
                    local_registry.bind(service_name, arg)
                    print(f"[Auto-bind] Callback service: [{service_name}]")

                # Serialize thành remote reference
                serialized.append(arg.__to_remote_ref__())
            else:
                serialized.append(arg)

        return serialized


# Global singleton instance
local_registry = LocalRegistry()
