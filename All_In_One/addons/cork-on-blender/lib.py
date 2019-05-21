from .exceptions import *

def get_addon_name():
    return __name__.split('.')[0]


def get_cork_filepath(context):
    """preference set in the addon"""
    addon = get_addon_name()
    preferences = context.user_preferences.addons[addon].preferences
    return preferences.cork_filepath


def validate_executable(filepath):
    """returns True if file is valid and executable"""
    import os

    if not os.path.isfile(filepath):
        raise InvalidPathException(filepath)

    if not os.access(filepath, os.X_OK):
        raise NonExecutableException(filepath)

    return True
