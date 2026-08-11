from typing import Callable


class FunctionBasedContextManager:
    def __init__(self, f: Callable[[], None]):
        self.after_function = f

    def __enter__(self):
        pass
    def __exit__(self):
        self.after_function()