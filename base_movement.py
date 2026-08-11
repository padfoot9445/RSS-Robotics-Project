from dataclasses import dataclass
from typing import Callable, Literal
from FunctionBasedContextManager import FunctionBasedContextManager
from sbot import * #type: ignore
from my_motor import *

DEFAULT_POWER = 1



class BaseMovement:
    def __init__(self, sleeper: Callable[[int | float], None], *motors: MyMotor):
        self.motors = list(motors)
        self._sleeper = sleeper
    
    def forwards(self, power: int = DEFAULT_POWER, end: int = BRAKE):
        for motor in self.motors:
            motor.set_power(power)

        def reset():
            for motor in self.motors:
                motor.set_power(end)

        return FunctionBasedContextManager(reset)

    def wait(self, time: float | int):
        self._sleeper(time)


    def forwards_time(self, time: float | int = 0, power: int = DEFAULT_POWER, end: int = BRAKE):
        with self.forwards(power, end):
            self.wait(time)

    def backwards(self, power: int = DEFAULT_POWER, end: int = BRAKE):
        return self.forwards(-1 * power, end)

    def backwards_time(self, time: float | int = 0, power: int = DEFAULT_POWER, end: int = BRAKE):
        self.forwards_time(time, power * -1, end)
        