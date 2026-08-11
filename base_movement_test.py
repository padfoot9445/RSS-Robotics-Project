import pytest

from command_log import CommandLog, CommandType
from my_motor_mock import MyMotorMock
from sleeper_mock import SleeperMock
from type_aliases import *
from base_movement import BaseMovement, Direction, MyMotor

@pytest.fixture
def logger():
    return CommandLog()

@pytest.fixture
def left_motor(logger: CommandLog):
    return MyMotorMock(False, 0, logger)

@pytest.fixture
def right_motor(logger: CommandLog):
    return MyMotorMock(False, 1, logger)

@pytest.fixture
def motors(left_motor: MyMotorMock, right_motor: MyMotorMock):
    return [left_motor, right_motor]

@pytest.fixture
def sleeper(logger: CommandLog):
    return SleeperMock(logger)


@pytest.fixture
def base_movement(sleeper: SleeperMock, left_motor: MyMotorMock, right_motor: MyMotorMock):
    return BaseMovement(sleeper.sleep, left_motor, right_motor)

@pytest.fixture
def power_values():
    return [x/100 for x in range(-100, 105, 5)]

def test_forwards(motors: list[MyMotorMock], base_movement: BaseMovement, power_values: power_type, logger: CommandLog):
    base_movement.move(Direction.FORWARDS, axis_power=power_values)
    for motor in motors:
        assert logger.exists_log(CommandType.SET_POWER, motor.identifier, power_values)

def test_backwards(motors: list[MyMotorMock], base_movement: BaseMovement, power_values: power_type, logger: CommandLog):
    base_movement.move(Direction.BACKWARDS, axis_power=power_values)
    for motor in motors:
        assert logger.exists_log(CommandType.SET_POWER, motor.identifier, power_values * -1)

# def test_turn_left(left_motor: MyMotorMock, right_motor: MyMotorMock)