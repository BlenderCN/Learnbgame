import functools


def pyside_cache(propname):
    """Decorator, stores the result of the decorated callable in Python-managed memory.

    This is to work around the warning at
    https://www.blender.org/api/blender_python_api_master/bpy.props.html#bpy.props.EnumProperty
    """

    if callable(propname):
        raise TypeError('Usage: pyside_cache("property_name")')

    def decorator(wrapped):
        """Stores the result of the callable in Python-managed memory.

        This is to work around the warning at
        https://www.blender.org/api/blender_python_api_master/bpy.props.html#bpy.props.EnumProperty
        """

        @functools.wraps(wrapped)
        # We can't use (*args, **kwargs), because EnumProperty explicitly checks
        # for the number of fixed positional arguments.
        def wrapper(self, context):
            result = None
            try:
                result = wrapped(self, context)
                return result
            finally:
                rna_type, rna_info = getattr(self.bl_rna, propname)
                rna_info['_cached_result'] = result

        return wrapper

    return decorator


def lru_cache_1arg(wrapped):
    """Decorator, caches return value as long as the 1st arg doesn't change.

    The 1st arg MUST be a DNA datablock (e.g. have an as_pointer() function).
    """

    cached_value = ...
    cached_arg = ...

    def cache_clear():
        nonlocal cached_value, cached_arg
        cached_value = ...
        cached_arg = ...

    @functools.wraps(wrapped)
    def wrapper(*args, **kwargs):
        nonlocal cached_value, cached_arg

        if cached_value is not ... and len(args) and args[0].as_pointer() == cached_arg:
            return cached_value

        try:
            result = wrapped(*args, **kwargs)
        except:
            cache_clear()
            raise

        if len(args):
            cached_value = result
            cached_arg = args[0].as_pointer()
        else:
            cache_clear()

        return result

    wrapper.cache_clear = cache_clear
    return wrapper
