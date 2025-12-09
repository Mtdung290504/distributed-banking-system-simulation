import ipaddress


def valid_inet4_address(value: str):
    try:
        ipaddress.IPv4Address(value)
        return True
    except:
        return False


from typing import TypedDict


class RemoteReference(TypedDict):
    """Cấu trúc của remote reference để truyền qua mạng."""

    __remote_ref__: bool
    service_name: str
    host: str
    port: int
    signature_hash: str
