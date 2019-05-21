# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber


:synopsis:


:description:


:applications:

:see_also:

:license:
    see license.txt and EULA.txt

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#

from .bpy_pynode_socket import CustomBlenderSocket


# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#
class ListSocket(CustomBlenderSocket):
    _is_list = True

    def draw_color(self, context, node):
        pass

    @classmethod
    def get_default_value(cls):
        raise NotImplementedError()

    @classmethod
    def get_from_values_code(cls):
        raise NotImplementedError()

    @classmethod
    def get_join_lists_code(cls):
        raise NotImplementedError()

    @classmethod
    def get_conversion_code(cls, data_type):
        pass

    @classmethod
    def correct_value(cls, value):
        pass


class PythonListSocket(ListSocket):
    @classmethod
    def get_default_value(cls):
        return []

    @classmethod
    def get_default_value_code(cls):
        return "[]"

    @classmethod
    def get_from_values_code(cls):
        return "value"

    @classmethod
    def get_join_lists_code(cls):
        return "list(itertools.chain(value))"

    @classmethod
    def correct_value(cls, value):
        pass

    @classmethod
    def get_conversion_code(cls, data_type):
        pass


class CListSocket(ListSocket):
    @classmethod
    def get_default_value(cls):
        return []

    @classmethod
    def get_default_value_code(cls):
        return "[]"

    @classmethod
    def get_from_values_code(cls):
        return "value"

    @classmethod
    def get_join_lists_code(cls):
        return "list(itertools.chain(value))"

    @classmethod
    def correct_value(cls, value):
        pass

    @classmethod
    def get_conversion_code(cls, data_type):
        pass