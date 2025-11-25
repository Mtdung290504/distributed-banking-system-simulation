# client.py
from typing import TypeVar as _TypeVar, Type as _Type, cast as _cast, Tuple as _Tuple
import inspect as _inspect

from xmlrpc.client import ServerProxy as _ServerProxy
from . import utils as _utils, constants as _constants


_T = _TypeVar("_T")


class _RPCStub:
    """Stub object gọi RPC với validation."""

    def __init__(
        self,
        proxy: _ServerProxy,
        interface_class: _Type,
        class_hash: str,
        service_name: str,
    ):
        self._proxy = proxy
        self._interface_class = interface_class
        self._class_hash = class_hash
        self._service_name = service_name

    def __getattr__(self, name: str):
        """Intercept method calls và forward tới RPC server."""
        if not hasattr(self._interface_class, name):
            raise AttributeError(
                f"Method [{name}] không tồn tại trong interface "
                f"{self._interface_class.__name__}"
            )

        method = getattr(self._interface_class, name)

        # Skip nếu không phải method
        if not callable(method):
            raise AttributeError(f"[{name}] không phải method")

        sig = _inspect.signature(method)

        def rpc_call(*args, **kwargs):
            # Validate parameters
            try:
                bound = sig.bind(None, *args, **kwargs)
                bound.apply_defaults()
            except TypeError as e:
                raise TypeError(f"Lỗi tham số khi gọi [{name}]: {e}")

            # Gọi với format: serviceNameSPLITORmethodName
            rpc_method_name = f"{self._service_name}{_constants.SPLITOR}{name}"
            rpc_method = getattr(self._proxy, rpc_method_name)
            return rpc_method(self._class_hash, *args, **kwargs)

        return rpc_call


def lookup(proxy: _ServerProxy, binding: _Tuple[str, _Type[_T]]) -> _T:
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
    service_name, interface_class = binding

    # Tính hash của interface class
    class_hash = _utils.get_interface_hash(interface_class)
    print(f"Lookup interface [{interface_class.__name__}] hash:", class_hash)

    # Tạo stub
    stub_obj = _RPCStub(proxy, interface_class, class_hash, service_name)

    # Cast về type interface
    return _cast(_T, stub_obj)
