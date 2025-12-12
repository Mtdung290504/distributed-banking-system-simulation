"""
RMI Registry Implementation

Module này cung cấp registry để bind/lookup remote services:
- LocalRegistry: Server-side registry quản lý services
- RemoteRegistry: Client-side proxy để lookup services
- LocateRegistry: Factory để tạo/lấy registry
- RPCStub: Client-side stub để gọi remote methods
"""

import inspect
import threading
import socket
from typing import TypeVar, Type, cast, get_type_hints, Optional

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy

from ..helpers.constants import METHOD_SPLITOR, SERVICE_NAME_SPLITOR, DEFAULT_RMI_PORT
from ..helpers.types import valid_inet4_address, RemoteReference
from ..helpers.utils import get_interface_hash

from .remote import RemoteObject, Remote

T = TypeVar("T")


def get_local_inet_address() -> str:
    """
    Lấy địa chỉ IP local của máy (LAN IP).

    Sử dụng trick: tạo UDP socket connect tới 8.8.8.8
    để OS tự chọn interface và lấy IP tương ứng.

    Returns:
        str: Local IP address (fallback về 127.0.0.1 nếu lỗi)
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Không thực sự connect, chỉ để OS chọn interface
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        print(f"[Warning] Không lấy được IP LAN, fallback về 127.0.0.1: {e}")
        return "127.0.0.1"
    finally:
        s.close()


class ServiceWrapper:
    """
    Wrapper để validate interface hash trước khi gọi method.

    Class này wrap remote service và đảm bảo:
    - Client và server có cùng interface (qua hash)
    - Arguments được deserialize đúng (remote refs -> stubs)
    """

    def __init__(self, service: RemoteObject):
        """
        Args:
            service: Remote object cần wrap
        """
        self.service = service
        self._expected_hash = service.signature_hash

    def __getattr__(self, name: str):
        """
        Intercept method calls để validate hash và deserialize arguments.

        Args:
            name: Tên method cần gọi

        Returns:
            Callable: Wrapped method với validation

        Raises:
            AttributeError: Nếu method không tồn tại hoặc không callable
        """
        # Check method có tồn tại không
        if not hasattr(self.service, name):
            raise AttributeError(
                f"Method [{name}] không tồn tại trong service "
                f"[{self.service.__class__.__name__}]"
            )

        method = getattr(self.service, name)

        # Check method có callable không
        if not callable(method):
            raise AttributeError(
                f"Attribute [{name}] trong service "
                f"[{self.service.__class__.__name__}] không phải method"
            )

        def validated_call(client_hash: str, *args, **kwargs):
            """
            Wrapper thực tế gọi method với validation.

            Args:
                client_hash: Interface hash từ client
                *args: Method arguments
                **kwargs: Method keyword arguments

            Returns:
                Method result (có thể là RemoteObject)

            Raises:
                ValueError: Nếu interface hash không khớp
            """
            # Validate interface hash
            if client_hash != self._expected_hash:
                raise ValueError(
                    f"Interface mismatch giữa client và server!\n"
                    f"Server interface hash: {self._expected_hash}\n"
                    f"Client interface hash: {client_hash}\n"
                    f"Cần đảm bảo cả 2 peer dùng cùng phiên bản interface."
                )

            # Deserialize arguments (remote refs -> stubs)
            deserialized_args = self._deserialize_arguments(method, args)

            # Gọi method gốc
            result = method(*deserialized_args, **kwargs)

            # Note: Nếu result là RemoteObject, LocalRegistry.__getattr__
            # sẽ tự động serialize thành remote_ref trước khi trả về client
            return result

        return validated_call

    def _deserialize_arguments(self, method, args):
        """
        Deserialize arguments, chuyển remote references thành RPCStub.

        Remote reference (dict) -> RPCStub để gọi callback từ server về client.

        Args:
            method: Method sẽ được gọi (để lấy type hints)
            args: Tuple arguments từ client

        Returns:
            list: Deserialized arguments

        Raises:
            TypeError: Nếu remote ref không match với type hint
        """
        sig = inspect.signature(method)
        type_hints = get_type_hints(method)

        deserialized = []
        param_names = list(sig.parameters.keys())

        for i, arg_value in enumerate(args):
            # Nếu vượt quá số params (trường hợp *args), giữ nguyên
            if i >= len(param_names):
                deserialized.append(arg_value)
                continue

            param_name = param_names[i]
            expected_type = type_hints.get(param_name)

            # Check nếu arg là remote reference
            if isinstance(arg_value, dict) and arg_value.get("__remote_ref__"):
                arg_value = cast(RemoteReference, arg_value)

                # Validate type hint phải là Remote subclass
                if (
                    expected_type
                    and inspect.isclass(expected_type)
                    and issubclass(expected_type, Remote)
                ):
                    # Tạo stub để gọi về client
                    stub = RPCStub(
                        proxy=ServerProxy(
                            f"http://{arg_value['host']}:{arg_value['port']}/",
                            allow_none=True,
                        ),
                        interface=expected_type,
                        interface_hash=arg_value["signature_hash"],
                        service_name=arg_value["service_name"],
                    )
                    deserialized.append(stub)
                else:
                    raise TypeError(
                        f"Parameter [{param_name}] nhận được Remote Reference "
                        f"nhưng type hint [{expected_type}] không phải Remote subclass."
                    )
            else:
                deserialized.append(arg_value)

        return deserialized


class LocalRegistry:
    """
    Registry quản lý các remote services trên local machine.

    Registry này:
    - Bind/unbind remote services
    - Start XML-RPC server để client connect
    - Route RPC calls đến đúng service
    """

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Tạo local registry (chưa start server).

        Args:
            host: IP address (None = auto-detect local IP)
            port: Port number (None = DEFAULT_RMI_PORT)
        """
        self.host = host or get_local_inet_address()
        self.port = port or DEFAULT_RMI_PORT

        self._services: dict[str, ServiceWrapper] = {}
        self._lock = threading.RLock()

        self._server: Optional[SimpleXMLRPCServer] = None
        self._is_running = False

    @staticmethod
    def _assert_valid_remote_object(remote_object: RemoteObject):
        """
        Validate remote object phải implement Remote interface.

        Args:
            remote_object: Object cần validate

        Raises:
            AssertionError: Nếu object không hợp lệ
            ValueError: Nếu object không có signature hash
        """
        # Check phải kế thừa cả RemoteObject và Remote
        if not (
            isinstance(remote_object, RemoteObject)
            and isinstance(remote_object, Remote)
        ):
            raise AssertionError(
                f"Remote object không hợp lệ!\n"
                f"Class [{remote_object.__class__.__name__}] phải kế thừa "
                f"RemoteObject và gián tiếp kế thừa Remote interface."
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
            name: Service name (phải unique)
            remote_object: Remote object cần bind

        Raises:
            ValueError: Nếu service name đã tồn tại
            AssertionError: Nếu remote object không hợp lệ
        """
        self._assert_valid_remote_object(remote_object)

        with self._lock:
            if name in self._services:
                raise ValueError(
                    f"Service [{name}] đã được bind trong registry. "
                    f"Dùng rebind() để thay thế hoặc unbind() trước."
                )

            # Wrap service với validation layer
            self._services[name] = ServiceWrapper(remote_object)
            remote_object.exported_name = name
            print(f"[Registry-{self.host}:{self.port}] Bound service: [{name}]")

    def rebind(self, name: str, remote_object: RemoteObject):
        """
        Rebind (overwrite) một remote object.

        Args:
            name: Service name
            remote_object: Remote object mới

        Raises:
            RuntimeError: Nếu server đang chạy
            AssertionError: Nếu remote object không hợp lệ
        """
        if self._is_running:
            raise RuntimeError(
                "Không thể rebind service khi server đang chạy. "
                "Dừng server trước hoặc dùng bind() trước khi start."
            )

        self._assert_valid_remote_object(remote_object)

        with self._lock:
            if name in self._services:
                print(f"[Registry-{self.host}:{self.port}] Rebinding service: [{name}]")
            else:
                print(
                    f"[Registry-{self.host}:{self.port}] Binding new service: [{name}]"
                )

            self._services[name] = ServiceWrapper(remote_object)
            remote_object.exported_name = name

    def unbind(self, name: str):
        """
        Unbind một service khỏi registry.

        Args:
            name: Service name cần unbind

        Raises:
            RuntimeError: Nếu server đang chạy
            ValueError: Nếu service không tồn tại
        """
        # if self._is_running:
        #     raise RuntimeError(
        #         "Không thể unbind service khi server đang chạy. " "Dừng server trước."
        #     )

        with self._lock:
            if name not in self._services:
                raise ValueError(f"Service [{name}] không tồn tại trong registry!")

            self._services[name].service.exported_name = None
            del self._services[name]

            print(f"[Registry-{self.host}:{self.port}] Unbound service: [{name}]")

    def list(self):
        """
        List tất cả service names trong registry.

        Returns:
            list: Danh sách service names
        """
        with self._lock:
            return list(self._services.keys())

    def listen(self, background: bool = False):
        """
        Start RPC server.

        Args:
            background: Nếu True, chạy trong daemon thread (non-blocking).
                       Nếu False, chạy blocking ở main thread.

        Raises:
            RuntimeError: Nếu server đã đang chạy
        """
        if self._is_running:
            raise RuntimeError(
                f"Registry server đã đang chạy tại {self.host}:{self.port}"
            )

        # Tạo XML-RPC server
        if self._server is None:
            self._server = SimpleXMLRPCServer(
                addr=(str(self.host), self.port),
                allow_none=True,
                logRequests=False,
                bind_and_activate=True,
            )
            self._server.register_instance(self)

        self._is_running = True
        print(f"[RPC Server] Listening on {self.host}:{self.port}")

        if background:
            # Chạy trong daemon thread
            t = threading.Thread(target=self._server.serve_forever, daemon=True)
            t.start()
            print("[RPC Server] Started in background thread.")
        else:
            # Chạy blocking (main server)
            try:
                self._server.serve_forever()
            except KeyboardInterrupt:
                print("\n[RPC Server] Shutting down...")
            finally:
                self._server.server_close()
                self._is_running = False

    def __getattr__(self, name: str):
        """
        Route XML-RPC calls đến đúng service.

        Format: serviceName@methodName

        Args:
            name: RPC method name (serviceName@methodName)

        Returns:
            Callable: Method wrapper để XML-RPC gọi

        Raises:
            AttributeError: Nếu format sai hoặc service/method không tồn tại
        """
        # Validate format
        if METHOD_SPLITOR not in name:
            raise AttributeError(
                f"Invalid RPC method format: [{name}]\n"
                f"Expected format: serviceName{METHOD_SPLITOR}methodName"
            )

        parts = name.split(METHOD_SPLITOR, 1)
        service_name = parts[0]
        method_name = parts[1]

        # Lookup service
        with self._lock:
            if service_name not in self._services:
                raise AttributeError(
                    f"Service [{service_name}] không tồn tại trong registry"
                )
            service_wrapper = self._services[service_name]

        # Check method tồn tại
        if not hasattr(service_wrapper, method_name):
            raise AttributeError(
                f"Method [{method_name}] không tồn tại trong service [{service_name}]"
            )

        # Lấy validated method
        method = getattr(service_wrapper, method_name)

        def rpc_method(client_hash: str, *args, **kwargs):
            """
            Wrapper cuối cùng cho XML-RPC call.

            Gọi method và serialize result nếu là RemoteObject.
            """
            result = method(client_hash, *args, **kwargs)

            # Nếu result là RemoteObject -> convert thành remote_ref
            if isinstance(result, RemoteObject):
                service_instance = result

                # Format: ClassName#ObjectID
                service_name_ref = (
                    f"{service_instance.__class__.__name__}"
                    f"{SERVICE_NAME_SPLITOR}"
                    f"{service_instance.object_id}"
                )

                return service_instance.serialize(
                    service_name_ref, self.host, self.port
                )

            return result

        return rpc_method


class LocateRegistry:
    """
    Factory để tạo/lấy registry (tương tự java.rmi.registry.LocateRegistry).
    """

    # Giữ reference tới local registry hiện tại
    _current_local_registry: Optional[LocalRegistry] = None

    @staticmethod
    def createRegistry(port: Optional[int] = None) -> LocalRegistry:
        """
        Tạo local registry mới.

        Args:
            port: Port number (None = DEFAULT_RMI_PORT)

        Returns:
            LocalRegistry: Registry mới tạo (chưa start)
        """
        reg = LocalRegistry(port=port)
        LocateRegistry._current_local_registry = reg
        return reg

    @staticmethod
    def getRegistry(address: Optional[str] = None, port: Optional[int] = None):
        """
        Lấy remote registry (client-side proxy).

        Args:
            address: Server IP (None = local IP)
            port: Server port (None = DEFAULT_RMI_PORT)

        Returns:
            RemoteRegistry: Client-side registry proxy

        Raises:
            AssertionError: Nếu address không hợp lệ
        """
        host = address or get_local_inet_address()
        port = port or DEFAULT_RMI_PORT

        assert valid_inet4_address(host), f"Invalid IPv4 address: {host}"

        proxy = ServerProxy(f"http://{host}:{port}/", allow_none=True)
        return RemoteRegistry(proxy)

    @staticmethod
    def getLocalRegistry() -> Optional[LocalRegistry]:
        """
        Lấy local registry hiện tại (nếu có).

        Returns:
            Optional[LocalRegistry]: Registry hiện tại hoặc None
        """
        return LocateRegistry._current_local_registry


class RemoteRegistry:
    """
    Client-side registry để lookup remote services.
    """

    def __init__(self, proxy: ServerProxy):
        """
        Args:
            proxy: XML-RPC ServerProxy tới remote registry
        """
        self.__proxy = proxy

    def lookup(self, service_name: str, interface: Type[T]) -> T:
        """
        Lookup remote service và tạo stub.

        Args:
            service_name: Tên service trong registry
            interface: Interface class (Remote subclass)

        Returns:
            T: Stub object (type cast về interface type)
        """
        interface_hash = get_interface_hash(interface)
        stub_obj = RPCStub(self.__proxy, interface, interface_hash, service_name)

        return cast(T, stub_obj)


class RPCStub:
    """
    Client-side stub để gọi remote methods với validation.
    """

    def __init__(
        self,
        proxy: ServerProxy,
        interface: Type,
        interface_hash: str,
        service_name: str,
    ):
        """
        Args:
            proxy: XML-RPC ServerProxy
            interface: Interface class
            interface_hash: Interface signature hash
            service_name: Service name trong registry
        """
        self.__proxy = proxy
        self.__interface = interface
        self.__interface_hash = interface_hash
        self.__service_name = service_name

    def __getattr__(self, name: str):
        """
        Intercept method calls và forward tới remote server.

        Args:
            name: Method name

        Returns:
            Callable: Wrapper để gọi remote method

        Raises:
            AttributeError: Nếu method không tồn tại trong interface
        """
        # Check method có trong interface không
        if not hasattr(self.__interface, name):
            raise AttributeError(
                f"Method [{name}] không tồn tại trong interface "
                f"[{self.__interface.__name__}]"
            )

        method = getattr(self.__interface, name)

        if not callable(method):
            raise AttributeError(
                f"Attribute [{name}] trong interface "
                f"[{self.__interface.__name__}] không phải method"
            )

        sig = inspect.signature(method)

        def remote_call(*args, **kwargs):
            """
            Thực tế gọi remote method.

            Args:
                *args: Method arguments
                **kwargs: Method keyword arguments

            Returns:
                Method result (có thể là stub nếu server trả callback)

            Raises:
                TypeError: Nếu arguments không match signature
            """
            # Validate arguments với signature
            try:
                bound = sig.bind(None, *args, **kwargs)
                bound.apply_defaults()
            except TypeError as e:
                raise TypeError(f"Lỗi tham số khi gọi method [{name}]: {e}")

            # Serialize arguments (RemoteObject -> remote ref)
            # AUTO-EXPORT nếu chưa bind
            serialized_args = self._serialize_arguments(args)

            # Gọi XML-RPC với format: serviceName@methodName
            rpc_method_name = f"{self.__service_name}{METHOD_SPLITOR}{name}"
            rpc_method = getattr(self.__proxy, rpc_method_name)

            # RPC call với interface hash
            result = rpc_method(self.__interface_hash, *serialized_args)

            # Deserialize result nếu là remote reference (callback)
            if isinstance(result, dict) and result.get("__remote_ref__"):
                result = cast(RemoteReference, result)

                # Server trả callback -> tạo stub ngược lại
                remote_host = result["host"]
                remote_port = result["port"]

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

    def _serialize_arguments(self, args: tuple):
        """
        Serialize arguments, chuyển RemoteObject thành remote reference.

        AUTO-EXPORT: Tự động bind RemoteObject vào local registry nếu chưa bind.
        Developer có thể dùng obj.exported_name để tự unbind sau này.

        Args:
            args: Tuple arguments

        Returns:
            list: Serialized arguments

        Raises:
            RuntimeError: Nếu có RemoteObject nhưng registry chưa start
        """
        serialized = []

        for arg in args:
            if isinstance(arg, RemoteObject):
                # Lấy local registry
                reg = LocateRegistry.getLocalRegistry()

                # Check registry đã start chưa
                if reg is None or not reg._is_running:
                    raise RuntimeError(
                        f"Không thể pass RemoteObject [{arg.__class__.__name__}] "
                        f"làm argument vì Local Registry chưa được start!\n\n"
                        f"Giải pháp:\n"
                        f"#1. Tạo registry:\n"
                        f"local_registry = LocateRegistry.createRegistry()\n"
                        f"#2. Start registry:\n"
                        f"local_registry.listen(background=True)\n\n"
                        f"Sau đó mới gọi được remote method với RemoteObject\n"
                        f"\tLưu ý: Có thể dùng obj.exported_name để dùng trong unbind."
                    )

                # Format: ClassName#ObjectID
                service_name = (
                    f"{arg.__class__.__name__}"
                    f"{SERVICE_NAME_SPLITOR}"
                    f"{arg.object_id}"
                )

                # AUTO-EXPORT: Tự động bind nếu chưa có
                if service_name not in reg.list():
                    reg.bind(service_name, arg)
                    # Lưu exported_name để dev có thể tự unbind
                    arg.exported_name = service_name
                    print(f"[Auto-Export] Bound [{service_name}] to registry")

                # Serialize thành remote reference
                serialized.append(arg.serialize(service_name, reg.host, reg.port))
            else:
                serialized.append(arg)

        return serialized
