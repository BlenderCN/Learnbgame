# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber

:synopsis:
    Module for 'dynamically' duck typing and creating Blender Properties on the fly

:description:
    This is an advanced module used for creating Blender Properties.
    The properties are created "dynamically" and during runtime. 
    @dynamic for creating dynamic properties
    @node_paramater for converting node_params you wish to expose to the UI

:applications:


:see_also:
   https://blender.stackexchange.com/questions/86612/creating-dynamic-blender-properties
   ./node_parameters.py  -- create_property_group()
   ./base_node.py -- create_parameter() 

:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#

import bpy
from bpy.props import *
from .io import IO


# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#
def dynamic(func):
    """

    @:keyword: dynamic - Function Generator that creates properties for 
                            Blender data types on the fly
    :param func: Function to generate
    :return: dynamic_property(): returns decorated function
    """

    def dynamic_property(*args, **kwargs):
        """

        :param args: first argument is always *prop_dict (from func in outer scope)
        :parameter *prop_dict: One Blender Property Mapped to a dict: 
                    e.g. prop_dict = {'mapname': bpy.props.StringProperty(
                                                            default="some_path_to_map")}
        :param kwargs: specific keywords needed by enclosed methods
        :return: Pointer to newly registered/assigned property
        """
        Prop = type(str("Parameters"), (bpy.types.PropertyGroup,), func(*args))
        bpy.utils.register_class(Prop)
        PropPointer = bpy.props.PointerProperty(name=func(kwargs.get('param_type')),
                                                type=Prop)
        setattr(func(kwargs.get('blender_type')), func(kwargs.get('param_type')),
                PropPointer)
        return PropPointer

    return dynamic_property


def node_parameter(func):
    """
    Decorator to convert a node parameter into a property that can be exposed to the UI
    and Blender's Python API during runtime. 
    :param func: 
    :return: 
    """

    def node_param_convert(*args, **kwargs):
        new_arg = func(*args)
        if 'INT' in func(kwargs.get('type')):
            prop = IntProperty(default=int(new_arg))
            return prop
        elif 'VALUE' in func(kwargs.get('type')):
            prop = FloatProperty(default=float(new_arg))
            return prop
        elif 'BOOL' in func(kwargs.get('type')):
            if (func(*args)) == '0':
                new_arg = False
                IO.debug(new_arg)
                prop = BoolProperty(default=new_arg)
            else:
                new_arg = True
                IO.debug(new_arg)
                prop = BoolProperty(default=new_arg)
            return prop
        elif 'STRING' in func(kwargs.get('type')):
            prop = StringProperty(default=new_arg)
            return prop
        elif 'RGBA' in func(kwargs.get('type')):
            size = len(new_arg)
            prop = FloatVectorProperty(default=[float(new_arg) for new_arg in new_arg],
                                       subtype='COLOR_GAMMA',
                                       size=size)
            return prop
        elif 'VECTOR' in func(kwargs.get('type')):
            size = len(new_arg)
            prop = FloatVectorProperty(default=[float(new_arg) for new_arg in new_arg],
                                       subtype='XYZ',
                                       size=size)
            return prop
        elif func(kwargs.get('type')) is None:
            pass
        else:
            pass

    return node_param_convert

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

