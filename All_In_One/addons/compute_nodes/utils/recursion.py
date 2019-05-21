import functools

active_functions = set()

def no_recursion(function):
    """The decorated function should not return any values"""
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        identifier = id(function)
        if identifier not in active_functions:
            active_functions.add(identifier)
            result = function(*args, **kwargs)
            active_functions.remove(identifier)
            return result
    return wrapper
