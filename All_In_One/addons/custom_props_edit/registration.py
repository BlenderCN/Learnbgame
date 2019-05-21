import bpy
from bpy.props import *

class PropertyEditSettings(bpy.types.PropertyGroup):
    property_name = StringProperty(name = "Property Name")
    remove = BoolProperty(name = "Remove", default = False)


class CustomPropsEditProperties(bpy.types.PropertyGroup):
    property_edit_settings = CollectionProperty(type = PropertyEditSettings)
    
    def remove_all_changed(self, context):
        for item in self.property_edit_settings:
            item.remove = self.remove_all
    
    remove_all = BoolProperty(name = "Remove All", update = remove_all_changed)


def register():
    bpy.types.Scene.custom_props_edit = PointerProperty(type = CustomPropsEditProperties, options = {"SKIP_SAVE"})

def unregister():
    del bpy.types.Scene.custom_props_edit