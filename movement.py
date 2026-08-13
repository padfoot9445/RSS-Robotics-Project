import math
from typing import Callable

from controller import Controller
from helpers import sign

from .sensors import Camera, RobotCoordinate, RobotPosition
from .base_movement import BaseMovement, Direction
from .type_aliases import *


class Movement:
    def __init__(self, base_movement: BaseMovement, camera: Camera, controller_factory: controller_factory[Controller]):
        self.base_movement = base_movement
        self.camera = camera
        self.controller_factory = controller_factory
        self.last_orientation_error = None

    def get_position(self) -> RobotPosition:
        pass

    def seek_coordinate(self, target_coordinate: RobotCoordinate, current_position: RobotPosition):
        
        error = self.get_axis_error(target_coordinate)
        

        def move_axis(direction: Direction, target_angle: float):
            def inner(step: float, power: power_type | None):
                self.seek_orientation(target_angle)
                self.base_movement.move_time_blocking(step, direction, axis_power=power)
            return inner

        target_angle = math.radians()

        # seek x-axis first
        self.controller_factory(
            lambda: self.get_axis_error(target_coordinate), # error
            move_axis(Direction.BACKWARDS), # lower_error
            move_axis(Direction.FORWARDS), # increase error
            move_axis(Direction.BACKWARDS)
        )

    def get_axis_error(self, target_coordinate: RobotCoordinate):
        """assume error_x and error_y of robot coordinate are None

            returns: RobotCoordinate
                - x: error on x-axis, if actual > tgt then positive; if actual < tgt then negative
                - y: error on y-axis, if actual > tgt then positive; if actual < tgt then negative
                - error_x: current_coordinate.error_x
                - error_y: current_coordinate.error_y
        """
        current_coordinate = self.get_position().coordinate

        return RobotCoordinate(
            x=current_coordinate.x - target_coordinate.x,
            y=current_coordinate.y - target_coordinate.y,
            error_x=current_coordinate.error_x,
            error_y=current_coordinate.error_y
        )


    def get_orientation_error(self, target_orientation: float):
        """target_orientation: radians
            Tracks the last error and sign of error. If the magnitude of the naive error increases immensely but the sign does not change, make it so that this does not happen. This should only happen
            returns: difference in orientation, where if the robot is too clockwise, then positive; if the robot is too ccw, then negative
        
            """
        naive_error = self.get_position().orientation.angle_radians - target_orientation
        
        if self.last_orientation_error is None or naive_error == 0:
            self.last_orientation_error = naive_error
            return naive_error

        else:
            if sign(naive_error) == sign(self.last_orientation_error) and abs(self.last_orientation_error - naive_error) > math.pi:
                if sign(naive_error) == -1:
                    self.last_orientation_error = naive_error + 2 * math.pi
                else:
                    self.last_orientation_error = naive_error - 2 * math.pi
            else:
                self.last_orientation_error = naive_error
            return self.last_orientation_error

    def seek_orientation(self, target_orientation: float):
        """target_orientation: radians, if the robot is too clockwise, then positive; if the robot is too ccw, then negative"""
        # TODO: Handle edge case where we are targeting something close to 0
        current_error = self.get_orientation_error(target_orientation)
        handle_null_error_direction: Direction

        match current_error:
            case 0 | 0.0:
                return
            case x if x > 0: # error > 0, so robot is pointing too far right, so
                handle_null_error_direction = Direction.LEFT
            case x if x < 0: # error < 0, so robot is pointing too far left, so
                handle_null_error_direction = Direction.RIGHT
            case _:
                handle_null_error_direction = Direction.RIGHT # default clockwise

        def get_error_handler(direction: Direction):
                def inner(step: float, power: power_type | None):
                    self.base_movement.move_time_blocking(step, direction, turn_power=power)
                return inner
        

        self.controller_factory(
            lambda : self.get_orientation_error(target_orientation), # error
            get_error_handler(Direction.LEFT), # lower_error
            get_error_handler(Direction.RIGHT), # increase_error
            get_error_handler(handle_null_error_direction) # handle_null_error
        ).lower_absolute_error()