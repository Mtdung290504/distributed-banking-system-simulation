from queue import Queue
from threading import Lock, Event
from shared.models.server import ATMCommand


class CommandQueue:
    def __init__(self):
        self._queue: Queue[ATMCommand] = Queue()
        self._lock = Lock()
        self.has_data_event = Event()

    def add(self, command: ATMCommand):
        """Thêm command vào queue"""
        with self._lock:
            self._queue.put(command)
            self.has_data_event.set()

    def get_all(self) -> list[ATMCommand]:
        """Lấy tất cả commands (để xử lý batch)"""
        commands = []

        with self._lock:
            while not self._queue.empty():
                commands.append(self._queue.get())

            self.has_data_event.clear()

        return commands

    def size(self) -> int:
        return self._queue.qsize()

    def is_empty(self) -> bool:
        return self._queue.empty()

    def wait_for_data(self, timeout: float | None = None) -> bool:
        """
        Trả về True nếu có data.
        Trả về False nếu hết timeout mà vẫn chưa có data.
        """
        return self.has_data_event.wait(timeout=timeout)
