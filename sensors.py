from dataclasses import dataclass, field
import itertools
import json
import math
import os
from pathlib import Path
import statistics

import numpy as np
from sbot import arduino, vision
from sbot.marker import Marker

class Ultrasound:
    def __init__(self, trigger_pin: int, echo_pin: int):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
    def get_distance(self) -> int:
        return arduino.measure_ultrasound_distance(self.trigger_pin, self.echo_pin)

@dataclass
class Position:
    """Bottom-left is 0, 0, horizontal x, vertical y, measured in millimeters (mm)"""
    x: int
    y: int
    error_x: int | None = field(default=None)
    error_y: int | None = field(default=None)
    @property
    def error(self):
        if self.error_x is None or self.error_y is None:
            return None
        return math.sqrt((self.error_x**2 + self.error_y**2))
@dataclass
class MarkerPosition:
    x: int
    y: int
    angle: float # upwards is zero, rightwards is 90 degrees, but this is measured in radians

class Camera:
    def __init__(self):
        markers_path = Path(os.path.dirname(os.path.realpath(__file__)))/"markers.json"
        with open(markers_path) as file:
            self.markers_positions = json.load(file)

    def get_markers(self):
        return vision.detect_markers() #type: ignore
    def calculate_position(self, id: set[int] | None = None) ->  Position | None:
        markers = self.get_markers()
        if len(markers) == 0:
            return None

        if id is None:
            positions = [self._calculate_position(marker) for marker in markers]
        else:
            positions = [self._calculate_position(marker) for marker in markers if marker.id in id]

        x_coordinates = [x.x for x in positions]
        y_coordinates = [x.y for x in positions]

        x_error = max(x_coordinates) - min(x_coordinates)
        y_error = max(y_coordinates) - min(y_coordinates)

        best_x = statistics.median(x_coordinates)
        best_y = statistics.median(y_coordinates)

        return Position(round(best_x), round(best_y), x_error, y_error)

    def get_marker_coordinate(self, marker_id: int) -> MarkerPosition:
        coord = self.markers_positions[str(marker_id)]
        return MarkerPosition(coord[0], coord[1], math.radians(coord[2]))

    def _calculate_position(self, marker: Marker) -> Position:
        marker_position = self.get_marker_coordinate(marker.id)

        horizontal_angle = marker.position.horizontal_angle
        distance = marker.position.distance

        naive_x = math.sin(horizontal_angle) * distance + marker_position.x
        naive_y = marker_position.y - (math.cos(horizontal_angle) * distance)

        
        return self._rotate_naive_position(naive_x=naive_x, naive_y=naive_y, marker_position=marker_position)

    
    
    def _rotate_naive_position(self, naive_x: float, naive_y: float, marker_position: MarkerPosition) -> Position:
        sin = math.sin(math.pi + marker_position.angle)
        cos = math.cos(math.pi + marker_position.angle)
        a = marker_position.x
        b = marker_position.y


        rotation_matrix = np.array([
            [cos, -sin, a * (-cos) + a + b * sin],
            [sin, cos, -a*sin + b * (-cos) + b],
            [0, 0, 1]
        ])

        naive_vector = np.array([naive_x, naive_y, 1])

        result_vector = rotation_matrix @ naive_vector

        result_vector_list = result_vector.tolist()[:-1]
        result_vector_list = [round(x) for x in result_vector_list]

        return Position(result_vector_list[0], result_vector_list[1])



    
    