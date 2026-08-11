import time

from command_log import CommandLog, CommandType


class SleeperMock:
    def __init__(self, logger: CommandLog, sleep_factor: float = 1.0):
        self.logger = logger
        self.sleep_factor = sleep_factor
    def sleep(self, duration: float):
        self.logger.log_command(CommandType.SLEEP, duration)
        time.sleep(duration * self.sleep_factor)