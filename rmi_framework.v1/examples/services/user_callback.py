from abc import abstractmethod
from net.remote import RemoteObject, Remote


# Define interface
class UserCallback(Remote):
    @abstractmethod
    def set_session_id(self, session_id: str) -> bool:
        pass


# Implementation
class UserCallbackImpl(RemoteObject, UserCallback):
    def __init__(self):
        super().__init__()

    def set_session_id(self, session_id: str) -> bool:
        print(f"Session ID set to: {session_id}")
        return True
