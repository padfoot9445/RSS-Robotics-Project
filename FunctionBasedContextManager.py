from typing import Callable


class FunctionBasedContextManager:
    def __init__(self, f: Callable[[], None]):
        self.stop = f
        self._stopped = False

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        if not self._stopped:
            self.stop()
        self._stopped = True