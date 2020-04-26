import bpy


def datablock_lookup(type):
    """Decorator for reusing datablocks by name. The decorator must specify the
    attribute from bpy.data it wishes to use and the first argument of the
    wrapped function must be 'name'

    Example:
        @datablock_lookup('images')
        def get_image(name):
            # Do image logic here
            return image
    """

    def decorator(func):
        data = None

        def wrapper(name, *args, **kwargs):
            nonlocal data

            try:
                if data.get(name):
                    return data.get(name)

            except AttributeError:
                data = getattr(bpy.data, type)

            return func(name, *args, **kwargs)

        return wrapper

    return decorator
