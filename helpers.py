def sign(num: float | int | None):
    match num:
        case 0 | 0.0:
            return 0
        case float(x) | int(x) if x > 0:
            return 1
        case float(x) | int(x) if x < 0:
            return -1
        case None | _:
            return None