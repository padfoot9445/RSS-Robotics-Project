from enum import Enum, auto
from typing import Callable
from type_aliases import *

from FunctionBasedContextManager import FunctionBasedContextManager
from sbot import utils, BRAKE
from my_motor import *

DEFAULT_POWER = 1
DEFAULT_TURN_POWER = .2
DEFAULT_END = BRAKE
DEFAULT_OFFSET = 0

class Direction(Enum):
    STOP = auto()
    FORWARDS = auto()
    BACKWARDS = auto()
    LEFT = auto()
    RIGHT = auto()

class BaseMovement:
    def __init__(self, sleeper: Callable[[float], None], left_motor: MyMotor, right_motor: MyMotor):
        self.motors = [left_motor, right_motor]
        self._sleeper = sleeper
        self.left_motor = left_motor
        self.right_motor = right_motor

    def _stop(self, *, end: power_type = DEFAULT_END):
        for motor in self.motors:
            motor.set_power(end)

    def move(self, direction: Direction, *, axis_power: power_type = DEFAULT_POWER, turn_power: power_type = DEFAULT_TURN_POWER, offset: power_type = DEFAULT_OFFSET, end_power: power_type = DEFAULT_END):
        assert axis_power >= 0 and turn_power >= 0

        match direction:
            case Direction.STOP:
                self._stop(end=end_power)
            case Direction.FORWARDS:
                self._forwards(power=axis_power, end=end_power)
            case Direction.BACKWARDS:
                self._forwards(power=-1*axis_power, end=end_power)
            case Direction.LEFT:
                self._turn_left(power=turn_power, offset=offset, end=end_power)
            case Direction.RIGHT:
                self._turn_right(power=turn_power, offset=offset, end=end_power)

    def _get_stop_context_manager(self, end_power: power_type):
        return FunctionBasedContextManager(lambda: self.move(Direction.STOP, end_power=end_power))

    def _turn_left(self, power: power_type = DEFAULT_TURN_POWER, offset: power_type = DEFAULT_OFFSET, *, end: power_type = DEFAULT_END):
        self.left_motor.set_power(offset - power)
        self.right_motor.set_power(power + offset)

    def _turn_right(self, power: power_type = DEFAULT_TURN_POWER, offset: power_type = DEFAULT_OFFSET, *, end: power_type = DEFAULT_END):
        self.right_motor.set_power(offset - power)
        self.left_motor.set_power(power + offset)

    
    def _forwards(self, power: power_type = DEFAULT_POWER, *, end: power_type = DEFAULT_END):
        for motor in self.motors:
            motor.set_power(power)


    def wait(self, time: float | int):
        self._sleeper(time)


    # def forwards_time(self, time: float = 0, power: power_type = DEFAULT_POWER, *, end: power_type = DEFAULT_END):
    #     with self._forwards(power, end=end):
    #         self.wait(time)

    # def backwards(self, power: power_type = DEFAULT_POWER, *, end: power_type = DEFAULT_END):
    #     return self._forwards(-1 * power, end=end)

    # def backwards_time(self, time: float = 0, power: power_type = DEFAULT_POWER, *, end: power_type = DEFAULT_END):
    #     self.forwards_time(time, power * -1, end=end)

    # def move_until_blocking(self, predicate: Callable[[], bool], movement: Callable[[], FunctionBasedContextManager], ivl: float = 0.1):
    #     with movement():
    #         while not predicate():
    #             self.wait(ivl)
        

    # def move_time_blocking(self, time: float, movement: Callable[[], FunctionBasedContextManager]):
    #     with movement():
    #         self.wait(time)
        


    @staticmethod
    def get_sleep_prod() -> Callable[[float], None]:
        return utils.sleep