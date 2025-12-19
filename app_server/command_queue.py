from queue import Queue
from threading import Lock
from shared.models.server import ATMCommand


class CommandQueue:
    def __init__(self):
        self._queue: Queue[ATMCommand] = Queue()
        self._lock = Lock()

    def add(self, command: ATMCommand):
        """Thêm command vào queue"""
        with self._lock:
            self._queue.put(command)

    def get_all(self) -> list[ATMCommand]:
        """Lấy tất cả commands (để xử lý batch)"""
        commands = []

        with self._lock:
            while not self._queue.empty():
                commands.append(self._queue.get())

        return commands

    def size(self) -> int:
        return self._queue.qsize()

    def is_empty(self) -> bool:
        return self._queue.empty()
