import pytest

from .command_log import CommandLog, CommandType
from .my_motor_mock import MyMotorMock
from .sleeper_mock import SleeperMock
from .type_aliases import *
from .base_movement import BaseMovement, Direction, MyMotor

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
    return SleeperMock(logger, sleep_factor=0)


@pytest.fixture
def base_movement(sleeper: SleeperMock, left_motor: MyMotorMock, right_motor: MyMotorMock):
    return BaseMovement(sleeper.sleep, left_motor, right_motor)

def power_values(neg_allowed: bool = False):
    return [x/100 for x in range(-100 if neg_allowed else 0, 110, 10)]

@pytest.mark.parametrize("power_value", power_values())
def test_forwards(motors: list[MyMotorMock], base_movement: BaseMovement, power_value: power_type, logger: CommandLog):
    base_movement.move(Direction.FORWARDS, axis_power=power_value)
    for motor in motors:
        assert logger.exists_log(CommandType.SET_POWER, motor.identifier, power_value)

@pytest.mark.parametrize("power_value", power_values())
def test_backwards(motors: list[MyMotorMock], base_movement: BaseMovement, power_value: power_type, logger: CommandLog):
    base_movement.move(Direction.BACKWARDS, axis_power=power_value)
    for motor in motors:
        assert logger.exists_log(CommandType.SET_POWER, motor.identifier, power_value * -1)

def skip_invalid_turn_test(turn_speed: power_type, offset: power_type):
    if abs(turn_speed) + abs(offset) > 1 or turn_speed <= 0:
            pytest.skip()

@pytest.mark.parametrize("turn_speed", power_values())
@pytest.mark.parametrize("offset", power_values(True))
def test_turn_left(left_motor: MyMotorMock, right_motor: MyMotorMock, base_movement: BaseMovement, turn_speed: power_type, offset: power_type):
    skip_invalid_turn_test(turn_speed, offset)
    base_movement.move(Direction.LEFT, turn_power = turn_speed, offset=offset)
    assert left_motor.power == (offset - turn_speed) and right_motor.power == (turn_speed + offset)
    assert left_motor.power < right_motor.power, f"{turn_speed}, {offset}" # turning left so left tyre must spin slower

@pytest.mark.parametrize("turn_speed", power_values())
@pytest.mark.parametrize("offset", power_values(True))
def test_turn_right(left_motor: MyMotorMock, right_motor: MyMotorMock, base_movement: BaseMovement, turn_speed: power_type, offset: power_type):
    skip_invalid_turn_test(turn_speed, offset)
    base_movement.move(Direction.RIGHT, turn_power = turn_speed, offset=offset)
    assert left_motor.power == (turn_speed + offset) and right_motor.power == (offset - turn_speed)
    assert left_motor.power > right_motor.power # turning right so right tyre must spin slower

directions = [Direction.FORWARDS, Direction.BACKWARDS, Direction.LEFT, Direction.RIGHT]

@pytest.mark.parametrize("direction", directions)
@pytest.mark.parametrize("end_value", power_values(True))
def test_stop(left_motor: MyMotorMock, right_motor: MyMotorMock, base_movement: BaseMovement, direction: Direction, end_value: power_type):
    base_movement.move(direction)
    base_movement.move(Direction.STOP, end_power=end_value)
    assert left_motor.power == right_motor.power == end_value


@pytest.mark.parametrize("direction", directions)
@pytest.mark.parametrize("end_value", power_values(True))
def test_move_context_manager(left_motor: MyMotorMock, right_motor: MyMotorMock, base_movement: BaseMovement, direction: Direction, end_value: power_type):
    if not (left_motor.power == right_motor.power == 0):
        pytest.skip("Motors were not initialized to zero power!")

    with base_movement.move_context_manager(direction, end_power=end_value):
        assert left_motor.power != 0 and  right_motor.power != 0
    assert left_motor.power == right_motor.power == end_value

@pytest.mark.parametrize("direction", directions)
@pytest.mark.parametrize("time", [0, 0.5, 1/3, 1, 10])
def test_move_time(time: float, direction: Direction, motors: list[MyMotor], base_movement: BaseMovement, logger: CommandLog):
    base_movement.move_time_blocking(time, direction)
    assert logger.exists_log_predicate(lambda x: x[0] == CommandType.SLEEP), logger.log
    for motor in motors:
        assert logger.exists_log(CommandType.SET_POWER, motor.identifier, 0)
        assert logger.exists_log_predicate(lambda x: x[0] == CommandType.SET_POWER and x[1][0] == motor.identifier and x[1][1] != 0)
@pytest.mark.parametrize("direction", directions)
def test_move_none_power__sets_to_nonnull(direction: Direction, base_movement: BaseMovement, logger: CommandLog, motors: list[MyMotor]):
    base_movement.move(direction, axis_power=None, turn_power=None, offset=None, end_power=None)
    for motor in motors:
        assert logger.exists_log_predicate(lambda x: x[0] == CommandType.SET_POWER and x[1][0] == motor.identifier and x[1][1] is not None)
