import functools
import logging
import time
from logging import Logger
from typing import Callable

import requests
from requests import Response

LOGGER = logging.getLogger(__name__)


def print_runtime(logger: Logger) -> Callable:
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            start_time = time.perf_counter()
            result = f(*args, **kwargs)
            end_time = time.perf_counter()
            duration = end_time - start_time
            logger.info(f"Function {f.__name__!r} took: {duration:.4f} seconds.")
            return result

        return wrapped

    return decorator


def parse_bool(val: str) -> bool:
    val = val.lower()
    match val:
        case "true":
            return True
        case "false":
            return False
        case _:
            raise ValueError(f"Couldn't parse {val} as bool.")


@print_runtime(LOGGER)
def send_request(url: str) -> Response:
    LOGGER.info(f"Sending request to: {url}")
    response = requests.get(url)
    response.raise_for_status()
    LOGGER.info(f"Response from: {url} successful, code: {response.status_code}.")
    return response
