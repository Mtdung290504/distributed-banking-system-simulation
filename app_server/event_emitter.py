from queue import Queue
from threading import Thread
from typing import Callable, List, Any


class EventEmitter:
    def __init__(self):
        self.events = Queue()
        self._start()

    def _start(self):
        def worker():
            while True:
                # Mỗi item trong queue: (callback, args)
                callback, args = self.events.get()

                try:
                    # Dùng * để giải nén list thành các tham số rời rạc cho hàm
                    callback(*args)
                except Exception as e:
                    print(f"Lỗi khi chạy callback: {e}")
                finally:
                    self.events.task_done()

        Thread(target=worker, daemon=True).start()

    def emit(self, callback: Callable, args: List[Any]):
        self.events.put((callback, args))
