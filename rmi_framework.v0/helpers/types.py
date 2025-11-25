import ipaddress


def valid_inet4_address(value: str):
    try:
        ipaddress.IPv4Address(value)
        return True
    except:
        return False
