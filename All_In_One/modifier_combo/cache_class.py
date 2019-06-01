import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, FloatVectorProperty, CollectionProperty


class PropCache(bpy.types.PropertyGroup): #consistent with prop_list
    int_val = IntProperty()
    float_val = FloatProperty()
    string_val = StringProperty()
    bool_val = BoolProperty()
    color_val = FloatVectorProperty()
    set_val = StringProperty()
    none_val = StringProperty()
    store_type = StringProperty()
    

class ComboCache(bpy.types.PropertyGroup):
    mod_type = StringProperty() 
    props = CollectionProperty(type = PropCache) #modifier properties array


class ComboListCache(bpy.types.PropertyGroup):
    combo_name = StringProperty() 
    combo = CollectionProperty(type = ComboCache) #mods array

