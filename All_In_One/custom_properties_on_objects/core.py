import bpy
from bpy.props import BoolProperty, PointerProperty
from bpy.types import PropertyGroup

class MyCustomPropertyGroup(PropertyGroup):
  skip_export = BoolProperty(
    name="Skip export",
    description="Should Blender omit this object from the exported scene",
    default=False
  )

def register():
  bpy.utils.register_class(MyCustomPropertyGroup)
  bpy.types.Object.my_custom_property_group = PointerProperty(type=MyCustomPropertyGroup)

def unregister():
  bpy.utils.unregister_class(MyCustomPropertyGroup)
  del bpy.types.Object.my_custom_property_group