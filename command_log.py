from enum import Enum, auto
from typing import Any, Callable



class CommandType(Enum):
    SET_POWER = auto()
    SLEEP = auto()



class CommandLog:
    def __init__(self):
        self.log: list[tuple[CommandType, tuple[Any, ...]]] = []
    def log_command(self, command_type: CommandType, *command_arguments: Any):
        self.log.append((command_type, command_arguments))
    def exists_log(self, command_type: CommandType, *command_arguments: Any):
        for type, args in self.log:
            if type == command_type and args == command_arguments:
                return True
        return False
    def exists_log_predicate(self, predicate: Callable[[tuple[CommandType, tuple[Any, ...]]], bool]):
        for log in self.log:
            if predicate(log):
                return True