import math
from typing import Callable

from helpers import sign
from .type_aliases import *
STEP = 0.2
POWER = None

class Controller:
    def __init__(self, error: error_reporter, f_lower_error: error_changer, f_increase_error: error_changer, f_handle_null_error: error_changer):
        self._error = error
        self._lower_error = f_lower_error
        self._increase_error = f_increase_error
        self._handle_null_error = f_handle_null_error

    def _error_and_sign(self):
        error = self._error()

        match error:
            case float(x) | int(x):
                return float(error), sign(x)
            case None:
                return None, None
        


    def _acquire_error_and_sign(self) -> tuple[float, int]:
        error, sign = self._error_and_sign()
        while error is None or sign is None: #or sign is None to make null analysis happy
            self._handle_null_error(STEP, POWER)
            error, sign = self._error_and_sign()

        return error, sign

    def lower_absolute_error(self, stop_switch_null: bool = False):

        """stop_switch_null determines if the error correction process should be determined to be finished if the error was non-null but became null"""
        _, starting_sign = self._acquire_error_and_sign()

        if starting_sign == 0:
            return

        fn_main = self._lower_error if starting_sign == 1 else self._increase_error
        fn_other = self._increase_error if starting_sign == 1 else self._lower_error



        sign = starting_sign

        # we know to be true that error is not non-null because acquire error and sign guarantees that
        while sign == starting_sign:

            fn_main(STEP, POWER)
            if stop_switch_null:
                _, sign = self._error_and_sign()
                if sign == None:
                    return
            else:
                _, sign = self._acquire_error_and_sign()

        fn_other(STEP, POWER)

