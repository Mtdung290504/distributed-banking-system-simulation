from typing import List

from rmi_framework.v2 import RemoteObject

from shared.interfaces.server import PeerService
from shared.models.server import ATMCommand

from ..coordinator import Coordinator


class PeerServiceImpl(RemoteObject, PeerService):
    def __init__(self, coordinator: Coordinator):
        super().__init__()
        self.coordinator = coordinator

    def request_token(self) -> bool:
        self.coordinator.set_peer_demanding(True)
        print(">> [PeerService] Peer requested Token.")
        return True

    def receive_sync(self, logs: List[ATMCommand], pass_token: bool):
        print("\n>> [PeerService] Received sync request from Peer")

        if logs:
            print(f"\tReceived {len(logs)} commands.")
            self.coordinator.handle_incoming_sync(logs)

        if pass_token:
            print("\tToken received")
            self.coordinator.accept_token()

        print("\n")
        return True

    def get_token_status(self):
        peer_hold_token = self.coordinator.is_holding_token()
        self.coordinator.on_peer_alive()
        return peer_hold_token
