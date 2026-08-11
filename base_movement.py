from dataclasses import dataclass
from typing import Callable, Literal

import sbot
from FunctionBasedContextManager import FunctionBasedContextManager
from sbot import * #type: ignore
from my_motor import *

DEFAULT_POWER = 1
DEFAULT_END = BRAKE
DEFAULT_OFFSET = 0


class BaseMovement:
    def __init__(self, sleeper: Callable[[float], None], *motors: MyMotor):
        self.motors = list(motors)
        self._sleeper = sleeper

    @property
    def left_motor(self) -> MyMotor:
        #TODO: Generalize
        return self.motors[0]

    @property
    def right_motor(self) -> MyMotor:
        #TODO: Generalize
        return self.motors[1]

    def stop(self, *, end: int = DEFAULT_END):
        for motor in self.motors:
            motor.set_power(end)

    def turn_left(self, power: int = DEFAULT_POWER, offset: int = DEFAULT_OFFSET, *, end: int = DEFAULT_END):
        self.left_motor.set_power(power + offset)
        self.right_motor.set_power(offset - power)
        return FunctionBasedContextManager(lambda: self.stop(end=end))

    
    def forwards(self, power: int = DEFAULT_POWER, *, end: int = DEFAULT_END):
        for motor in self.motors:
            motor.set_power(power)

        return FunctionBasedContextManager(lambda: self.stop(end=end))

    def wait(self, time: float | int):
        self._sleeper(time)


    def forwards_time(self, time: float = 0, power: int = DEFAULT_POWER, *, end: int = DEFAULT_END):
        with self.forwards(power, end=end):
            self.wait(time)

    def backwards(self, power: int = DEFAULT_POWER, *, end: int = DEFAULT_END):
        return self.forwards(-1 * power, end=end)

    def backwards_time(self, time: float = 0, power: int = DEFAULT_POWER, *, end: int = DEFAULT_END):
        self.forwards_time(time, power * -1, end=end)

    def move_until_blocking(self, predicate: Callable[[], bool], movement: Callable[[], FunctionBasedContextManager]):
        with movement():
            while not predicate():
                pass
        

    def move_time_blocking(self, time: float, movement: Callable[[], FunctionBasedContextManager]):
        with movement():
            self.wait(time)
        


    @staticmethod
    def get_sleep_prod() -> Callable[[float], None]:
        return utils.sleep