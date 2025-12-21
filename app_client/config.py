from typing import Dict, TypedDict


class ServerInfo(TypedDict):
    host: str
    port: int


# Cấu hình IP/Port của 2 server (Phải khớp với server side)
SERVER_CONFIG: Dict[str, ServerInfo] = {
    "1": {"host": "192.168.1.48", "port": 29054},
    "2": {"host": "192.168.1.48", "port": 29055},
}

# ID của server ưu tiên kết nối trước
PRIMARY_PEER_ID = "1"
