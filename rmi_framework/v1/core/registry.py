import inspect
import threading
import socket

from typing import TypeVar, Type, cast, get_type_hints, Optional
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy

from helpers.constants import METHOD_SPLITOR, SERVICE_NAME_SPLITOR, DEFAULT_RMI_PORT
from helpers.types import valid_inet4_address, RemoteReference
from helpers.utils import get_interface_hash

from core.remote import RemoteObject, Remote

T = TypeVar("T")


def get_local_inet_address() -> str:
    """Fallback local IP getter (simple, uses UDP trick)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception as e:
        print("Lấy IP LAN thất bại, fallback về 127.0.0.1", e)
        return "127.0.0.1"
    finally:
        s.close()


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
                    f"Mâu thuẫn Interface giữa 2 peer"
                    f"Local interface hash: {self._expected_hash}, Remote interface hash: {client_hash}"
                )

            # Deserialize arguments (xử lý remote references/callbacks)
            deserialized_args = self._deserialize_arguments(method, args)

            # Gọi method gốc
            result = method(*deserialized_args, **kwargs)

            # Serialize result nếu là RemoteObject (cho return callback)
            if isinstance(result, RemoteObject):
                # Lưu ý: Caller của ServiceWrapper (LocalRegistry) biết host/port của registry
                # nên sẽ convert result thành remote_ref trước khi trả về. Đây là handled
                # ở LocalRegistry.__getattr__ wrapper.
                return result

            return result

        return validated_call

    def _deserialize_arguments(self, method, args):
        """
        Deserialize arguments, chuyển remote references thành RPCStub.
        """
        sig = inspect.signature(method)
        type_hints = get_type_hints(method)

        deserialized = []

        # Lấy tên param (bound method có 'self' ẩn, nhưng signature chứa 'self' vì method ở class)
        param_names = list(sig.parameters.keys())

        for i, arg_value in enumerate(args):
            # Nếu vượt quá số params định nghĩa (trường hợp *args), giữ nguyên
            if i >= len(param_names):
                deserialized.append(arg_value)
                continue

            param_name = param_names[i]
            expected_type = type_hints.get(param_name)

            # Check nếu arg là remote reference (dict chứa cờ hiệu)
            if isinstance(arg_value, dict) and arg_value.get("__remote_ref__"):
                arg_value = cast(RemoteReference, arg_value)

                if (
                    expected_type
                    and inspect.isclass(expected_type)
                    and issubclass(expected_type, Remote)
                ):
                    deserialized.append(
                        RPCStub(
                            proxy=ServerProxy(
                                f"http://{arg_value['host']}:{arg_value['port']}/",
                                allow_none=True,
                            ),
                            interface=expected_type,
                            interface_hash=arg_value["signature_hash"],
                            service_name=arg_value["service_name"],
                        )
                    )
                else:
                    raise TypeError(
                        f"Parameter [{param_name}] nhận được Remote Reference nhưng Type Hint [{expected_type}] không phải là subclass của Remote."
                    )
            else:
                deserialized.append(arg_value)

        return deserialized


class LocalRegistry:
    """Registry quản lý các remote services trên local machine"""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self.host = host or get_local_inet_address()
        self.port = port or DEFAULT_RMI_PORT

        self._services = {}
        self._lock = threading.RLock()

        self._server: Optional[SimpleXMLRPCServer] = None
        self._is_running = False

    @staticmethod
    def _assert_valid_remote_object(remote_object: RemoteObject):
        """Validate remote object phải kế thừa cả RemoteObject và Remote"""
        assert isinstance(remote_object, RemoteObject) and isinstance(
            remote_object, Remote
        ), f"Remote object không hợp lệ, class [{remote_object.__class__.__name__}] phải là class con của cả RemoteObject và Remote"

        # Validate có signature hash
        if not remote_object.signature_hash:
            raise ValueError(
                f"Remote object [{remote_object.__class__.__name__}] không có interface hash (không implement Remote interface?)"
            )

    def bind(self, name: str, remote_object: RemoteObject):
        """
        Bind một remote object vào registry.
        """
        self._assert_valid_remote_object(remote_object)

        with self._lock:
            if name in self._services:
                raise ValueError(f"Service [{name}] đã được bind")

            # Wrap service với validation layer
            self._services[name] = ServiceWrapper(remote_object)
            print(f"[Registry:{self.host}:{self.port}] Bound service: [{name}]")

    def rebind(self, name: str, remote_object: RemoteObject):
        if self._is_running:
            raise RuntimeError("Không thể rebind service khi server đang chạy")

        self._assert_valid_remote_object(remote_object)

        with self._lock:
            if name in self._services:
                print(f"[Registry:{self.host}:{self.port}] Rebinding service: [{name}]")
            else:
                print(f"[Registry:{self.host}:{self.port}] Bound service: [{name}]")

            self._services[name] = ServiceWrapper(remote_object)

    def unbind(self, name: str):
        if self._is_running:
            raise RuntimeError("Không thể unbind service khi server đang chạy")

        with self._lock:
            if name not in self._services:
                raise ValueError(f"Service [{name}] không tồn tại!")

            del self._services[name]
            print(f"[Registry:{self.host}:{self.port}] Unbound service: [{name}]")

    def list(self):
        with self._lock:
            return list(self._services.keys())

    def listen(self, background: bool = False):
        """
        Start RPC server.
        Args:
            background: Nếu True, chạy server trong thread riêng (Non-blocking).
                        Nếu False, chạy blocking (như cũ).
        """
        if self._is_running:
            # Nếu đã chạy rồi thì bỏ qua, tránh lỗi runtime khi auto-start gọi lại
            return

        # Tạo server (Bind port)
        # Lưu ý: SimpleXMLRPCServer bind port ngay tại __init__, nên
        # connection refused sẽ không xảy ra miễn là object này được tạo.
        if self._server is None:
            self._server = SimpleXMLRPCServer(
                addr=(str(self.host), self.port),
                allow_none=True,
                logRequests=False,
                bind_and_activate=True,  # Mặc định là True, port mở ngay lập tức
            )
            self._server.register_instance(self)

        self._is_running = True
        print(f"[RPC Server] Listening on {self.host}:{self.port}")

        if background:
            # Chạy trong thread riêng (Daemon để tự tắt khi main thread tắt)
            t = threading.Thread(target=self._server.serve_forever, daemon=True)
            t.start()
            print("[RPC Server] Started in background thread.")
        else:
            # Chạy blocking (dành cho Server chính)
            try:
                self._server.serve_forever()
            except KeyboardInterrupt:
                print("\n[RPC Server] Shutting down...")
            finally:
                self._server.server_close()
                self._is_running = False

    def __getattr__(self, name: str):
        """
        Điều hướng method calls từ XML-RPC đến đúng service.
        Format: serviceName[SPLITOR]methodName
        """

        # Validate format
        if METHOD_SPLITOR not in name:
            raise AttributeError(
                f"Invalid method format: [{name}]. Expected: serviceName{METHOD_SPLITOR}methodName"
            )

        parts = name.split(METHOD_SPLITOR, 1)
        service_name = parts[0]
        method_name = parts[1]

        with self._lock:
            if service_name not in self._services:
                raise AttributeError(f"Service [{service_name}] không tồn tại")
            service_wrapper = self._services[service_name]

        if not hasattr(service_wrapper, method_name):
            raise AttributeError(
                f"Method [{method_name}] không tồn tại trong service [{service_name}]"
            )

        # Gọi validated_call -> có thể trả về RemoteObject instance
        method = getattr(service_wrapper, method_name)

        def rpc_method(client_hash: str, *args, **kwargs):
            result = method(client_hash, *args, **kwargs)

            # Nếu result là RemoteObject -> convert thành remote_ref với registry host/port
            if isinstance(result, RemoteObject):
                # Server trả về remote_ref để client tạo stub cho callback
                service_instance = result
                # Format: ClassName[SPLITOR]ObjectID
                service_name_ref = f"{service_instance.__class__.__name__}{SERVICE_NAME_SPLITOR}{service_instance.object_id}"

                return service_instance.serialize(
                    service_name_ref, self.host, self.port
                )

            return result

        return rpc_method


class LocateRegistry:
    """Factory để tạo registry (local hoặc remote)"""

    # giữ registry hiện tại để auto-export callback
    _current_local_registry: Optional[LocalRegistry] = None

    @staticmethod
    def createRegistry(port: Optional[int] = None) -> LocalRegistry:
        """
        Tạo local registry mới
        """
        reg = LocalRegistry(port=port)
        LocateRegistry._current_local_registry = reg
        return reg

    @staticmethod
    def getRegistry(address: Optional[str] = None, port: Optional[int] = None):
        """
        Trả về RemoteRegistry (client side) kết nối tới address:port.
        Nếu address là None -> mặc định dùng local IP
        Nếu port là None -> dùng port 1099
        """

        host = address or get_local_inet_address()
        port = port or DEFAULT_RMI_PORT
        assert valid_inet4_address(host), "Invalid IPv4 address"

        proxy = ServerProxy(f"http://{host}:{port}/", allow_none=True)
        return RemoteRegistry(proxy)

    @staticmethod
    def getLocalRegistry() -> Optional[LocalRegistry]:
        return LocateRegistry._current_local_registry


class RemoteRegistry:
    """Client-side registry để lookup remote services"""

    def __init__(self, proxy: ServerProxy):
        self.__proxy = proxy

    def lookup(self, service_name: str, interface: Type[T]) -> T:
        interface_hash = get_interface_hash(interface)
        stub_obj = RPCStub(self.__proxy, interface, interface_hash, service_name)

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
        if not hasattr(self.__interface, name):
            raise AttributeError(
                f"Method [{name}] không tồn tại trong interface [{self.__interface.__name__}]"
            )

        method = getattr(self.__interface, name)

        if not callable(method):
            raise AttributeError(f"Attribute [{name}] không phải method")

        sig = inspect.signature(method)

        def remote_call(*args, **kwargs):
            # Validate parameters với signature
            try:
                bound = sig.bind(None, *args, **kwargs)
                bound.apply_defaults()
            except TypeError as e:
                raise TypeError(f"Lỗi tham số khi gọi method [{name}]: {e}")

            # Serialize arguments (xử lý RemoteObject thành remote reference)
            serialized_args = self._serialize_arguments(args)

            # Gọi proxy với format: serviceName[SPLITOR]methodName
            rpc_method_name = f"{self.__service_name}{METHOD_SPLITOR}{name}"
            rpc_method = getattr(self.__proxy, rpc_method_name)

            # RPC call với hash validation
            result = rpc_method(self.__interface_hash, *serialized_args)

            # Deserialize result nếu là remote reference
            if isinstance(result, dict) and result.get("__remote_ref__"):
                result = cast(RemoteReference, result)

                # Server trả về remote_ref - tạo stub (reverse proxy)
                remote_host = result["host"]
                remote_port = result["port"]
                print("Debug:", remote_host, remote_port)
                return RPCStub(
                    proxy=ServerProxy(
                        uri=f"http://{remote_host}:{remote_port}/", allow_none=True
                    ),
                    interface=self.__interface,
                    interface_hash=result["signature_hash"],
                    service_name=result["service_name"],
                )

            return result

        return remote_call

    def _serialize_arguments(self, args):
        """
        Serialize arguments, chuyển RemoteObject thành remote reference.
        Nếu thấy RemoteObject, auto-export vào current local registry (nếu có) và bind service.
        """
        serialized = []

        for arg in args:
            if isinstance(arg, RemoteObject):
                # lấy registry hiện tại để auto-export
                reg = LocateRegistry.getLocalRegistry()
                if reg is None:
                    # Nếu không có registry, tạo 1 registry mặc định (auto) và tự khởi động
                    reg = LocateRegistry.createRegistry()
                    if not reg._is_running:
                        reg.listen(background=True)

                # Format: ClassName[SPLITOR]ObjectID
                service_name = (
                    f"{arg.__class__.__name__}{SERVICE_NAME_SPLITOR}{arg.object_id}"
                )

                # Tự export remote object
                if service_name not in reg.list():
                    reg.bind(service_name, arg)

                # Serialize thành remote reference, dùng host/port của registry
                serialized.append(arg.serialize(service_name, reg.host, reg.port))
            else:
                serialized.append(arg)

        return serialized
