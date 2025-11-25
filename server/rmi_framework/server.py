# server.py
from typing import (
    Type as _Type,
    TypeVar as _TypeVar,
    Optional as _Optional,
    Callable as _Callable,
)
from functools import wraps as _wraps
from xmlrpc.server import SimpleXMLRPCServer as _SimpleXMLRPCServer

from . import utils as _utils, constants as _constants

_T = _TypeVar("_T")


class _RPCSkeleton:
    """Wrapper tự động thêm hash validation cho service implementation."""

    def __init__(self, service_instance, interface_class: _Type, expected_hash: str):
        self._service = service_instance
        self._interface_class = interface_class
        self._expected_hash = expected_hash

        # Tự động wrap tất cả methods
        self._wrap_methods()

    def _validate_hash(self, client_hash: str, method_name: str):
        """Validate client interface khớp với server."""
        if client_hash != self._expected_hash:
            raise ValueError(
                f"Interface mismatch khi gọi proxy method:[{method_name}] - Client hash:[{client_hash}] - Server hash: [{self._expected_hash}]"
            )

    def _wrap_methods(self):
        """Tự động wrap tất cả public methods của service."""
        # Lấy tất cả abstract methods từ interface
        for name in dir(self._interface_class):
            if name.startswith("_"):
                continue

            interface_attr = getattr(self._interface_class, name)
            if not callable(interface_attr):
                continue

            # Lấy method từ service instance
            service_method = getattr(self._service, name)

            # Wrap method với hash validation
            wrapped = self._create_wrapped_method(name, service_method)

            # Gắn wrapped method vào skeleton
            setattr(self, name, wrapped)

    def _create_wrapped_method(self, method_name: str, original_method):
        """Tạo wrapped method có hash validation."""

        @_wraps(original_method)
        def wrapped(client_hash: str, *args, **kwargs):
            # Validate hash trước
            self._validate_hash(client_hash, method_name)

            # Gọi method gốc (business logic thuần túy)
            return original_method(*args, **kwargs)

        return wrapped


class Registry:
    """Registry quản lý nhiều RPC services."""

    def __init__(self):
        self._services = {}

    def bind(self, name: str, skeleton: _RPCSkeleton):
        """
        Bind một remote object vào registry với tên cho trước.

        Args:
            name: Tên để client lookup
            skeleton: Skeleton object đã wrap

        Raises:
            ValueError: Nếu name đã tồn tại
        """
        if name in self._services:
            raise ValueError(f"Service [{name}] đã được bind")
        self._services[name] = skeleton
        print(f"Bound service: [{name}]")

    def rebind(self, name: str, skeleton: _RPCSkeleton):
        """
        Bind hoặc replace một remote object.
        """
        if name in self._services:
            print(f"Rebinding service: [{name}]")
        else:
            print(f"Bound service: [{name}]")
        self._services[name] = skeleton

    def unbind(self, name: str):
        """
        Gỡ bỏ binding.
        """
        if name not in self._services:
            raise ValueError(f"Service [{name}] không tồn tại!")
        del self._services[name]
        print(f"Unbound service: [{name}]")

    def list(self):
        """
        List tất cả tên services đã bind.
        """
        return list(self._services.keys())

    def __getattr__(self, name: str):
        """Route method calls đến đúng service.

        Format: serviceName_methodName
        VD: calculator_add, user_getById
        """
        if not name.startswith("_") and _constants.SPLITOR in name:
            print("[REMOTE]", name)

        # Tách service name và method name
        if _constants.SPLITOR not in name:
            raise AttributeError(
                f"Invalid method format: [{name}]. Expected: serviceName{_constants.SPLITOR}methodName"
            )

        parts = name.split(_constants.SPLITOR, 1)
        service_name = parts[0]
        method_name = parts[1]

        # Tìm service
        if service_name not in self._services:
            raise AttributeError(f"Service [{service_name}] không tồn tại!")

        service = self._services[service_name]

        # Lấy method từ service
        if not hasattr(service, method_name):
            raise AttributeError(
                f"Method [{method_name}] không tồn tại trong service [{service_name}]"
            )

        return getattr(service, method_name)


def skeleton(
    service_class: _Type[_T], interface_class: _Type[_T]
) -> _Callable[..., _RPCSkeleton]:
    """
    Tạo skeleton factory từ service implementation class.

    Args:
        service_class: Class implement interface (PHẢI extends interface_class)
        interface_class: Interface class để validate

    Returns:
        Factory function nhận các params của constructor và trả về RPCSkeleton

    Example:
        # Interface
        class ICalculator(ABC):
            @abstractmethod
            def add(self, a: int, b: int) -> int: pass

        # Implementation với constructor có params
        class CalculatorImpl(ICalculator):
            def __init__(self, precision: int, debug: bool):
                self.precision = precision
                self.debug = debug

            def add(self, a: int, b: int) -> int:
                return a + b

        # Tạo skeleton factory
        calc_skeleton_factory = skeleton(CalculatorImpl, ICalculator)

        # Tạo skeleton instance với params
        calc_skeleton = calc_skeleton_factory(precision=2, debug=True)

        # Bind vào registry
        registry.bind("calculator", calc_skeleton)
    """
    # Validate service_class có extends interface_class không
    if not issubclass(service_class, interface_class):
        raise TypeError(
            f"{service_class.__name__} phải extends {interface_class.__name__}!"
        )

    # Tính hash của interface
    expected_hash = _utils.get_class_hash(interface_class)
    print(
        f"Server skeleton interface [{interface_class.__name__}] hash: {expected_hash}"
    )

    # Trả về factory function
    def _create_skeleton(*args, **kwargs) -> _RPCSkeleton:
        """
        Factory function tạo skeleton instance.

        Args:
            *args, **kwargs: Các params truyền vào constructor của service class

        Returns:
            RPCSkeleton đã wrap sẵn hash validation
        """
        # Tạo service instance với params
        service_instance = service_class(*args, **kwargs)

        # Tạo skeleton với validation
        skeleton_obj = _RPCSkeleton(service_instance, interface_class, expected_hash)

        return skeleton_obj

    return _create_skeleton


def listen(
    rpc_server: _SimpleXMLRPCServer,
    registry: Registry,
    before_serve: _Optional[_Callable[[], None]] = None,
):
    """
    Đăng ký registry vào XML-RPC server và bắt đầu lắng nghe.

    Args:
        rpc_server: SimpleXMLRPCServer instance
        registry: Registry chứa các services đã bind
        before_serve: Optional callback trước khi serve
    """
    rpc_server.register_instance(registry)
    if before_serve:
        before_serve()

    rpc_server.serve_forever()
