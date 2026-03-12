import time


def start_timer() -> float:
    return time.monotonic()


def calc_request_duration(start: float) -> int:
    return round((time.monotonic() - start) * 1000)
