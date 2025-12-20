from rmi_framework.v2 import RemoteObject
from shared.interfaces.peer import PeerService
from shared.models.server import ATMCommand
from typing import List

from ..coordinator import Coordinator


class PeerServiceImpl(RemoteObject, PeerService):
    def __init__(self, coordinator: Coordinator):
        super().__init__()
        self.coordinator = coordinator

    def request_token(self) -> bool:
        # Peer gọi hàm này để báo: 'Ê, tao cần ghi'
        self.coordinator.set_peer_demanding(True)
        print(">> [INFO] Peer requested Token.")
        return True

    def receive_sync(self, logs: List[ATMCommand], pass_token: bool) -> bool:
        # Peer gọi hàm này để đẩy dữ liệu + Trao Token
        if logs:
            print(f">> [SYNC] Received {len(logs)} commands from Peer.")
            self.coordinator.handle_incoming_sync(logs)

        if pass_token:
            print(">> [TOKEN] Token received from Peer!")
            self.coordinator.accept_token()

        return True
