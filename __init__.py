from base_movement import MyMotor, BaseMovement
from sensors import *
from sbot import utils
def initialize():
    utils.load_boards()
    utils.wait_start()