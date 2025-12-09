from abc import abstractmethod
from rmi_framework.v2 import Remote


# Define interface
class UserCallback(Remote):
    @abstractmethod
    def set_session_id(self, session_id: str) -> bool:
        pass
