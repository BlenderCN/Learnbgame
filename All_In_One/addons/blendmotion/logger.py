import bpy

import logging
from logging import getLogger, FileHandler

_logger = None

def get_logger():
    global _logger
    if _logger is None:
        raise RuntimeError("call configure_logger() before getting logger")
    return _logger

def configure_logger(name):
    global _logger

    prefs = bpy.context.user_preferences.addons[name].preferences

    if _logger is None:
        _logger = getLogger(name)
        handler = FileHandler(prefs.log_file, 'a+')
        _logger.addHandler(handler)

    _logger.setLevel(getattr(logging, prefs.log_level))

    return _logger
