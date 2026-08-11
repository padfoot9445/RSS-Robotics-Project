from typing import Callable

from command_log import CommandLog, CommandType
from my_motor import MyMotor
from type_aliases import *
from dataclasses import field

class MyMotorMock(MyMotor):
    def __init__(self, reversed: bool, identifier: int, logger: CommandLog):
        self.power_history: list[power_type] = []
        self.set_power_callback: Callable[[power_type], None] | None = None
        self.logger = logger
        super().__init__(reversed, identifier)
    def set_power(self, power: power_type):
        self.logger.log_command(CommandType.SET_POWER, power)
        self.power_history.append(power)