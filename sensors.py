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
class RobotOrientation:
    angle_radians: float # angle in radians, vertically upwards is 0, right is pi/2, left is 3pi/2
    error: float | None = field(default=None)
    @property
    def angle_degrees(self):
        return math.degrees(self.angle_radians)


@dataclass
class RobotCoordinate:
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
class RobotPosition:
    coordinate: RobotCoordinate
    orientation: RobotOrientation
@dataclass
class MarkerPosition:
    x: int
    y: int
    angle_radians: float # upwards is zero, rightwards is 90 degrees, but this is measured in radians
    @property
    def angle_degrees(self):
        math.degrees(self.angle_radians)

class Camera:
    def __init__(self):
        markers_path = Path(os.path.dirname(os.path.realpath(__file__)))/"markers.json"
        with open(markers_path) as file:
            self.markers_positions = json.load(file)
        self.reversed = False

    def get_markers(self):
        return vision.detect_markers() #type: ignore

    def calculate_position(self):
        if len(self.get_markers()) == 0:
            return None
        coord, orientation = self.calculate_coordinate(), self.calculate_orientation()
        return None if coord is None or orientation is None else RobotPosition(coord, orientation)
    
    def calculate_coordinate(self, id: set[int] | None = None) ->  RobotCoordinate | None:
        markers = self.get_markers()
        if len(markers) == 0:
            return None
        
        orientation = self.calculate_orientation()
        if orientation is None:
            return None

        if id is None:
            positions = [self._calculate_position(marker, orientation) for marker in markers]
        else:
            positions = [self._calculate_position(marker, orientation) for marker in markers if marker.id in id]

        x_coordinates = [x.x for x in positions]
        y_coordinates = [x.y for x in positions]

        x_error = max(x_coordinates) - min(x_coordinates)
        y_error = max(y_coordinates) - min(y_coordinates)

        best_x = statistics.median(x_coordinates)
        best_y = statistics.median(y_coordinates)

        return RobotCoordinate(round(best_x), round(best_y), x_error, y_error)

    def get_marker_coordinate(self, marker_id: int) -> MarkerPosition:
        coord = self.markers_positions[str(marker_id)]
        marker_degrees = coord[2]
        marker_coordinates = np.array([coord[0], coord[1]])
        if self.reversed:
            marker_degrees = (marker_degrees + 180) % 360
            rotation_matrix = np.array([
                [0, -1],
                [-1, 0]
            ])
            marker_coordinates = rotation_matrix @ marker_coordinates
        return MarkerPosition(marker_coordinates[0], marker_coordinates[1], math.radians(marker_degrees))
    # TODO: Handle when to be reversed

    def _calculate_position(self, marker: Marker, orientation: RobotOrientation) -> RobotCoordinate:
        marker_position = self.get_marker_coordinate(marker.id)

        horizontal_angle = marker.position.horizontal_angle
        distance = marker.position.distance

        # naive_x = -math.sin(horizontal_angle) * distance + marker_position.x
        # naive_y = marker_position.y - (math.cos(horizontal_angle) * distance)


        robot_marker_line_true_orientation = orientation.angle_radians + horizontal_angle
        
        snapped_line = (orientation.angle_radians % (math.pi * 2)) // (math.pi/2)
        triangle_subtended_angle = robot_marker_line_true_orientation - snapped_line * math.pi/2
        if horizontal_angle > 0:
            snapped_line += 1

        opp = math.sin(triangle_subtended_angle) * distance
        adj = math.cos(triangle_subtended_angle) * distance
        x: float
        y: float

        match int(snapped_line):
            case 0:
                x, y = opp, adj
            case 1:
                x, y = adj, -opp
            case 2:
                x, y = -opp, -adj
            case 3:
                x, y = -adj, opp
            case _:
                raise Exception()

        return RobotCoordinate(
            x = round(marker_position.x + x),
            y = round(marker_position.y + y)
        )
        # return self._rotate_naive_position(naive_x=naive_x, naive_y=naive_y, marker_position=marker_position)

    
    
    def _rotate_naive_position(self, naive_x: float, naive_y: float, marker_position: MarkerPosition) -> RobotCoordinate:
        sin = math.sin(math.pi + marker_position.angle_radians)
        cos = math.cos(math.pi + marker_position.angle_radians)
        a = marker_position.x
        b = marker_position.y

        marker_centre_vector = np.array([a, b])

    

        # rotation_matrix = np.array([
        #     [cos, -sin, a * (-cos) + a + b * sin],
        #     [sin, cos, -a*sin + b * (-cos) + b],
        #     [0, 0, 1]
        # ])

        rotation_matrix = np.array([
            [cos, -sin],
            [sin, cos]
        ])

        naive_vector = np.array([naive_x, naive_y])

        result_vector = (rotation_matrix @ (naive_vector - marker_centre_vector)) + marker_centre_vector

        result_vector_list = result_vector.tolist()
        result_vector_list = [round(x) for x in result_vector_list]

        return RobotCoordinate(result_vector_list[0], result_vector_list[1])

    
    def current_angle_marker(self, marker: Marker):
        yaw = marker.orientation.yaw
        angle = self.get_marker_coordinate(marker.id).angle_radians

        neg_yaw = -yaw

        return angle + neg_yaw

    def calculate_orientation(self) -> RobotOrientation | None:
        if len(self.get_markers()) == 0:
            return None
        orientations = [self.current_angle_marker(marker) for marker in self.get_markers()]
        error = max(orientations) - min(orientations)
        best_orientation = statistics.median(orientations)
        return RobotOrientation(best_orientation, error)









    
    