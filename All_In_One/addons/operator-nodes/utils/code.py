import functools

def code_to_function(verbose = False):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            code = "\n".join(function(*args, **kwargs))
            if verbose: print(code)
            container = {}
            exec(code, container, container)
            return container["main"]
        return wrapper
    return decorator