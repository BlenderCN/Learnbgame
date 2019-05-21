import bpy,sys
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty
        )
class Property_add_subproperty():
    def add_int_parameter(self, Property, attr, attr_default = 0, attr_min = -2**31, attr_max =2**31 - 1):

        # assert isinstance(Property, bpy.types.PropertyGroup)
        
        setattr(Property, attr, IntProperty(
            min = attr_min,
            max = attr_max,
            default = attr_default,
        ))
        
    def add_float_parameter(self, Property, attr, attr_default = 0, attr_min = sys.float_info.min, attr_max = sys.float_info.max):
        # print(dir(Property))
        # print(dir(bpy.types.PropertyGroup))

        # assert isinstance(Property, bpy.types.PropertyGroup)
        setattr(Property, attr, FloatProperty(
            min = attr_min,
            max = attr_max,
            default = attr_default,
        ))
    def add_enum_parameter(self, Property, attr, _items, attr_default = 0, attr_min = sys.float_info.min, attr_max = sys.float_info.max):
        # assert isinstance(Property, bpy.types.PropertyGroup)
        attr_items = tuple((item, item, item) for item in _items.split('/'))
        print(_items.split('/'))
        setattr(Property, attr, EnumProperty(
            name = attr,
            items = attr_items
        ))        
        
    def add_pointer(self, Property, attr, attr_type):
        setattr(Property, attr, PointerProperty(
            type = eval(attr_type)
        ))

    def add_string_parameter(self, Property, attr, attr_default = ''):
        setattr(Property, attr, StringProperty(
            name = '',
            default = attr_default
        ))
    
    def add_bool_parameter(self, Property, attr, attr_default = True):
        setattr(Property, attr, BoolProperty(
            name = attr,
            default = attr_default
        ))
