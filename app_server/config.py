from typing import Dict, TypedDict


class ServerInfo(TypedDict):
    host: str
    port: int


# Cấu hình cứng
SERVER_CONFIG: Dict[int, ServerInfo] = {
    1: {"host": "127.0.0.1", "port": 29054},
    2: {"host": "127.0.0.1", "port": 29055},
}

# ID của server hiện tại (Sửa thành "2" khi chạy code server 2)
PEER_ID = 1


def get_current_config() -> ServerInfo:
    return SERVER_CONFIG[PEER_ID]


def get_peer_config() -> ServerInfo:
    # Tìm ID không phải là mình
    for server_id, conf in SERVER_CONFIG.items():
        if server_id != PEER_ID:
            return conf

    raise ValueError("Config error: No peer found")
