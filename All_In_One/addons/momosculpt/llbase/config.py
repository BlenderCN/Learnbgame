# file: config.py
# package: llbase.config
#
# $LicenseInfo:firstyear=2006&license=mit$
#
# Copyright (c) 2006-2009, Linden Research, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# $/LicenseInfo$

"""
Utility module for parsing and using configuration files.
"""

import copy
import errno
import os
import time

from . import llsd

_g_config = None


class Config(object):
    """
    Class for loading llsd files as configuration.

    Config loads an llsd file and into memory and provides a pythonic
    interface into that data. Typically, the llsd file wil be a map
    with simple key-value pairs. The value can be anything supported
    by llsd including another map with new childern. This
    representation in memory can get updated to overwrite values or
    add new values.

    The xml configuration file is considered a live file and changes
    to the file are checked and reloaded periodically. If a value had
    been overwritten via the update or set method, the loaded values
    from the file are ignored (the values from the update/set methods
    override)

    The config is implemented as 2 sets of configuration -- one comes
    from the file and the other is whatever has been set during
    runtime. When a key is set during runtime it is treated as a
    runtime override over the file config even if the file is updated.
    """
    def __init__(self, config_filename):
        """
        Construct a new Config object with config_filename for state.

        :param config_filename: file for loading config. None creates
           an empty config.
        """
        self._config_filename = config_filename
        self._reload_check_interval = 30  # seconds
        self._last_check_time = 0
        self._last_mod_time = 0

        self._config_overrides = {}
        self._config_file_dict = {}
        self._combined_dict = {}

        self._load()

    def _load(self):
        "load contents from the configuration file"
        if self._config_filename is None:
            return

        config_file = open(self._config_filename)
        self._config_file_dict = llsd.parse(config_file.read())
        self._combine_dictionaries()
        config_file.close()

        self._last_mod_time = self._get_last_modified_time()
        self._last_check_time = time.time()  # now

    def _get_last_modified_time(self):
        """
        Returns the mtime (last modified time) of the config file, if
        such exists.
        """
        if self._config_filename is not None:
            return os.path.getmtime(self._config_filename)
        return 0

    def _combine_dictionaries(self):
        """
        Bring the defaults and overrides togeter into a combined
        dictionary.
        """
        self._combined_dict = {}
        if(self._config_file_dict):
            self._combined_dict.update(self._config_file_dict)
        self._combined_dict.update(self._config_overrides)

    def _reload_if_necessary(self):
        """
        Reload config if the check interval has expired and file is
        modified.

        If the file goes missing, this is probably a transient error
        so the old config is kept until reload succeeds.
        """
        now = time.time()
        if (now - self._last_check_time) > self._reload_check_interval:
            self._last_check_time = now
            try:
                modtime = self._get_last_modified_time()
                if modtime > self._last_mod_time:
                    self._load()
            except OSError as exc:
                if exc.errno == errno.ENOENT:  # file not found
                    print('WARNING: Configuration file missing:', end=' ')
                    print(self._config_filename)
                    self._last_mod_time = 0
                else:
                    raise  # pass the exception along to the caller

    def __getitem__(self, key):
        """
        Get value of key via [].

        :param key: string key for the value to get.
        """
        self._reload_if_necessary()
        return self._combined_dict[key]

    def get(self, key, default=None):
        """
        Get the value for key.

        :param key: string key for the value to get.
        :param default: Default value to return if key not in config.
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __setitem__(self, key, value):
        """
        Set key to value in the overrides via [].

        :param key: The key to set.
        :param value: The value to set.

        Once any key/value pair is changed via the set method,
        that key/value pair will remain set with that value until
        change via the update or set method
        """
        self._config_overrides[key] = value
        self._combine_dictionaries()

    def set(self, key, newval):
        """
        Sets the value of the config setting of key to be newval

        :param key: The key to set.
        :param newval: The value to set.

        Once any key/value pair is changed via the set method, that
        key/value pair will remain set with that value until change
        via the update or set method or program termination.
        """
        return self.__setitem__(key, newval)

    def update(self, new_conf):
        """
        Updates new_conf into the config.

        :param new_conf: a dict, filename, or file-like object to
           update into the current config state.

        Load an XML file and apply its map as overrides or additions
        to the existing config. Update can be a file or a dict.

        Once any key/value pair is changed via the update method,
        that key/value pair will remain set with that value until
        change via the update or set method
        """
        if isinstance(new_conf, dict):
            overrides = new_conf
        elif isinstance(new_conf, str):
            config_file = open(new_conf)
            overrides = llsd.parse(config_file.read())
            config_file.close()
        else:
            # assume it is a file-like object
            overrides = llsd.parse(new_conf.read())

        self._config_overrides.update(overrides)
        self._combine_dictionaries()

    def as_dict(self):
        "Returns immutable copy of the combined config as a dictionary."
        return copy.deepcopy(self._combined_dict)


def load(config_xml_file):
    """
    Load module config from a file.

    :param config_xml_file: The name of the file to load.
    """
    global _g_config
    _g_config = Config(config_xml_file)


def update(new_conf):
    """
    Updates new_conf into the module config.

    :param new_conf: dict configuration to update into the current config.
    """
    global _g_config
    if _g_config is None:
        _g_config = Config(None)
    return _g_config.update(new_conf)


def get(key, default=None):
    """
    Get the value for key from the module config.

    :param key: The key of the config value to get
    :param default: What to return if key is not found.
    """
    global _g_config
    if _g_config is None:
        _g_config = Config(None)
    return _g_config.get(key, default)


def set(key, newval):
    """
    Sets the value of the module config setting of key to be newval

    :param key: The key to set.
    :param newval: The new value for key.

    Once any key/value pair is changed via the set method,
    that key/value pair will remain set with that value until
    change via the update or set method or program termination
    """
    global _g_config
    if _g_config is None:
        _g_config = Config(None)
    _g_config.set(key, newval)
