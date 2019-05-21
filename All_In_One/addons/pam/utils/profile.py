"""Profile Module"""

import cProfile
import logging

logger = logging.getLogger(__package__)


def profiling(func):
    """Profiling functions in miliseconds"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        profiler.print_stats()
        return result
    return wrapper
