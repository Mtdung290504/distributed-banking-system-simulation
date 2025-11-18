from typing import Type, TypeVar
from functools import wraps
from framework.client import calculate_class_hash

T = TypeVar("T")


class RPCSkeleton:
    """Wrapper tự động thêm hash validation cho service implementation."""

    def __init__(self, service_instance, interface_class: Type, expected_hash: str):
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

        @wraps(original_method)
        def wrapped(client_hash: str, *args, **kwargs):
            # Validate hash trước
            self._validate_hash(client_hash, method_name)

            # Gọi method gốc (business logic thuần túy)
            return original_method(*args, **kwargs)

        return wrapped


def skeleton(service_class: Type[T], interface_class: Type[T]) -> RPCSkeleton:
    """
    Tạo RPC skeleton từ service implementation class.

    Args:
        service_class: Class implement interface (PHẢI extends interface_class)
        interface_class: Interface class để validate

    Returns:
        RPCSkeleton đã wrap sẵn hash validation để register vào XML-RPC server
    """
    # Import ở đây để tránh circular dependency
    # from framework.client import calculate_class_hash

    # Validate service_class có extends interface_class không
    if not issubclass(service_class, interface_class):
        raise TypeError(
            f"{service_class.__name__} phải extends {interface_class.__name__}!"
        )

    # Tính hash của interface
    expected_hash = calculate_class_hash(interface_class)
    print(
        f"Server skeleton interface [{interface_class.__name__}] hash: {expected_hash}"
    )

    # Tạo service instance
    service_instance = service_class()

    # Tạo skeleton với validation
    skeleton_obj = RPCSkeleton(service_instance, interface_class, expected_hash)

    return skeleton_obj
