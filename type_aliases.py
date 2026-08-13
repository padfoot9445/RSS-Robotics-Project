from typing import Callable


type power_type = float
type power_type_input = power_type | None
type error_changer = Callable[[float, power_type | None], None]
type error_reporter = Callable[[], float | None]
type controller_factory[T] = Callable[[error_reporter, error_changer, error_changer, error_changer], T]
