from sbot import arduino, vision

class Ultrasound:
    def __init__(self, trigger_pin: int, echo_pin: int):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
    def get_distance(self) -> int:
        return arduino.measure_ultrasound_distance(self.trigger_pin, self.echo_pin)

class Camera:
    def __init__(self):
        pass

    def get_markers(self):
        return vision.detect_markers() #type: ignore

    
    