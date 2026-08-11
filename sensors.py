from sbot import arduino

class Ultrasound:
    def __init__(self, trigger_pin: int, echo_pin: int):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
    def get_distance(self) -> int:
        return arduino.measure_ultrasound_distance(self.trigger_pin, self.echo_pin)
    