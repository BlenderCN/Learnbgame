import bpy
from bpy.types import Panel

class MyCustomUIElement(bpy.types.Panel):
  bl_space_type = "VIEW_3D"
  bl_region_type = "TOOLS"
  bl_category = "Hellmouth"
  bl_label = "My cool custom property panel"

  def draw(self, context):
    layout = self.layout
    obj = context.object
    if obj is None:
      return
    my_custom_props = obj.my_custom_property_group
    col = layout.column(align=True)
    row = col.row(align=True)
    row.prop(my_custom_props, "skip_export", text="Skip export")

def register():
  bpy.utils.register_class(MyCustomUIElement)

def unregister():
  bpy.utils.unregister_class(MyCustomUIElement)