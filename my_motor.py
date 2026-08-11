from dataclasses import dataclass
from sbot import motors
from type_aliases import *


@dataclass
class MyMotor:
    reversed: bool
    identifier: int
    @property
    def coefficient(self):
        return 1 if not self.reversed else -1
    
    def set_power(self, power: power_type):
        motors.set_power(self.identifier, power * self.coefficient)