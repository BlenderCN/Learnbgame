"""
.. module:: vsim2blender
   :platform: Blender add-on
   :synopsis: A module which interfaces with Blender to illustrate phonon modes.
              Includes importer from v_sim ascii files, and routines to build and render a model.

.. moduleauthor:: Adam J. Jackson

"""

import os
import configparser
from json import loads

bl_info = {
    "name": "ascii phonons",
    "description": "Generate phonon mode visualisations from ASCII input files",
    "author": "Adam J. Jackson",
    "version": (1, 1, 0),
    "blender": (2, 70, 0),
    "location": "",
    "category": "Import-Export",
    "tracker_url": "https://github.com/ajjackson/ascii-phonons/issues"
    }


def read_config(user_config=''):
    """
    Read configuration files elements.conf, settings.conf and optional user conf

    :param user_config: Path to a user-specified configuration file
    :type user_config: str

    :returns: config
    :rtype: configparser.ConfigParser
    """
    config = configparser.ConfigParser(allow_no_value=True)

    # Change formatter to capitalise words, making periodic table readable
    config.optionxform = lambda option: option.capitalize()

    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'elements.conf'))
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'settings.conf'))
    if user_config == '':
        pass
    else:
        config.read(user_config)

    return config


def parse_tuple(tuple_string, value_type=float):
    """Get a tuple back from string representation

    Three representations are recognised:
    '[1,2,3]' : JSON-style
    '1 2 3' : Simple space-separated
    '1,2,3': Simple comma-separated

    :param tuple_string: Serialised tuple
    :type tuple_string: str
    :param value_type: Type to cast values to
    :type value_type: type
    """
    if '[' in tuple_string:
        return tuple(map(value_type, loads(tuple_string)))
    elif ',' in tuple_string:
        return tuple(map(value_type,
                         tuple_string.split(',')))
    else:
        return tuple(map(value_type,
                         tuple_string.split()))


class Opts(object):
    def __init__(self, options, parser=False):
        """Robust option-handling

        Prioritises named options over config files.
        If a configparser object is not explicitly provided, looks for
        file in 'config' option.

        Note that Opts objects use the original dictionary object rather
        than a copy, and hence tracks the state of the options as they
        are updated.

        :param options: Collection of named options. Typically obtained
            by defining an outer function as fun(**options).
        :type options: dict
        :param parser: Optionally provide a ConfigParser object which
            has already been instantiated. If not provided, a new one
            will be created if there is a 'config' item in ``options``.
        :type parser: configparser.ConfigParser

        """
        self.options = options
        self.config = parser

        if not parser and 'config' in options:
            self.config = read_config(user_config=options['config'])
        else:
            self.config = read_config()

        self.bool_keys = (
            'gif',
            'gui',
            'montage',
            'normalise_vectors',
            'orthographic',
            'show_box',
            'static',
            'vectors')

        self.float_keys = (
            'box_thickness',
            'camera_rot',
            'mass_weighting',
            'outline_thickness',
            'scale_arrow',
            'scale_atom',
            'scale_vib',
            'zoom')

        self.float_tuple_keys = (
            'miller',
            'offset_box')

        self.int_keys = (
            'end_frame',
            'mode_index',
            'n_frames',
            'start_frame')

        self.int_tuple_keys = (
            'supercell')

    def get(self, key, fallback):
        """Get parameter, prioritising named options over config file

        :param key: Name of option
        :type key: str
        :param fallback: Fallback value if key is not found in options
            or config
        :type fallback: any

        """
        if key in self.options:
            return self.options[key]
        elif self.config and self.config.has_option('general', key):
            if key in self.bool_keys:
                return self.config.getboolean('general', key)
            elif key in self.float_keys:
                return self.config.getfloat('general', key)
            elif key in self.int_keys:
                return self.config.getint('general', key)
            elif key in self.float_tuple_keys:
                return parse_tuple(self.config.get('general', key))
            elif key in self.int_tuple_keys:
                return parse_tuple(self.config.get('general', key),
                                   value_type=int)
            else:
                return self.config.get('general', key)
        else:
            return fallback

