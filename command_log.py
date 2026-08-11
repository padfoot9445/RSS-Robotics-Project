from enum import Enum, auto
from typing import Any



class CommandType(Enum):
    SET_POWER = auto()
    SLEEP = auto()



class CommandLog:
    def __init__(self):
        self.log: list[tuple[CommandType, tuple[Any, ...]]] = []
    def log_command(self, command_type: CommandType, *command_arguments: Any):
        self.log.append((command_type, command_arguments))