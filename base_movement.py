from dataclasses import dataclass
from typing import Callable, Literal
from type_aliases import *

from .FunctionBasedContextManager import FunctionBasedContextManager
from sbot import utils, BRAKE
from .my_motor import *

DEFAULT_POWER = 1
DEFAULT_TURN_POWER = .2
DEFAULT_END = BRAKE
DEFAULT_OFFSET = 0

class BaseMovement:
    def __init__(self, sleeper: Callable[[float], None], left_motor: MyMotor, right_motor: MyMotor):
        self.motors = [left_motor, right_motor]
        self._sleeper = sleeper
        self.left_motor = left_motor
        self.right_motor = right_motor

    def stop(self, *, end: power_type = DEFAULT_END):
        for motor in self.motors:
            motor.set_power(end)

    def turn_left(self, power: power_type = DEFAULT_TURN_POWER, offset: int = DEFAULT_OFFSET, *, end: power_type = DEFAULT_END):
        self.left_motor.set_power(power + offset)
        self.right_motor.set_power(offset - power)
        return FunctionBasedContextManager(lambda: self.stop(end=end))

    def turn_right(self, power: power_type = DEFAULT_TURN_POWER, offset: int = DEFAULT_OFFSET, *, end: power_type = DEFAULT_END):
        self.right_motor.set_power(power + offset)
        self.left_motor.set_power(offset - power)
        return FunctionBasedContextManager(lambda: self.stop(end=end))

    
    def forwards(self, power: power_type = DEFAULT_POWER, *, end: power_type = DEFAULT_END):
        for motor in self.motors:
            motor.set_power(power)

        return FunctionBasedContextManager(lambda: self.stop(end=end))

    def wait(self, time: float | int):
        self._sleeper(time)


    def forwards_time(self, time: float = 0, power: power_type = DEFAULT_POWER, *, end: power_type = DEFAULT_END):
        with self.forwards(power, end=end):
            self.wait(time)

    def backwards(self, power: power_type = DEFAULT_POWER, *, end: power_type = DEFAULT_END):
        return self.forwards(-1 * power, end=end)

    def backwards_time(self, time: float = 0, power: power_type = DEFAULT_POWER, *, end: power_type = DEFAULT_END):
        self.forwards_time(time, power * -1, end=end)

    def move_until_blocking(self, predicate: Callable[[], bool], movement: Callable[[], FunctionBasedContextManager], ivl: float = 0.1):
        with movement():
            while not predicate():
                self.wait(ivl)
        

    def move_time_blocking(self, time: float, movement: Callable[[], FunctionBasedContextManager]):
        with movement():
            self.wait(time)
        


    @staticmethod
    def get_sleep_prod() -> Callable[[float], None]:
        return utils.sleep