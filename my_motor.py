from dataclasses import dataclass
from sbot import motors


@dataclass
class MyMotor:
    reversed: bool
    identifier: int
    @property
    def coefficient(self):
        return 1 if not self.reversed else -1
    
    def set_power(self, power: int):
        motors.set_power(self.identifier, power * self.coefficient)