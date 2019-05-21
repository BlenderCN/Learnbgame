import bpy
import os

bl_info = {
  'name': "UE4Rig",
  "author": 'Mack Thompson',
  'version': (0, 0, 1),
  'blender': (2, 79, 0),
  'description': 'Creates rigs using the UE4 skeleton',
  'license': 'MIT',
  'category': 'Animation'
}

class AddRig(bpy.types.Operator):
  """Adds a new rig"""
  bl_label = "Add Rig"
  bl_idname = "ue4rig.add_rig"

  def execute(self, context):

    TemplateFilepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Mannequin.blend")
    Section = "\\Object"
    ObjectName = "SK_Mannequin.001"
    TemplateDirectory = TemplateFilepath + Section

    bpy.ops.wm.append(
        filepath=TemplateFilepath + Section + ObjectName,
        filename=ObjectName,
        directory=TemplateDirectory,
        autoselect=True
      )
    return {'FINISHED'}

class UE4Rig_Tools(bpy.types.Panel):
  """UE4Rig Panel"""
  bl_label = "UE4Rig"
  bl_space_type = "VIEW_3D"
  bl_region_type = 'TOOLS'
  bl_category = "UE4Rig"

  def draw(self, context):
    layout = self.layout

    row = layout.row()
    row.label("Setup")
    row = layout.row()
    row.operator("ue4rig.add_rig")

def register():
  bpy.utils.register_module(__name__)

def unregister():
  bpy.utils.unregister_module(__name__)

  if __name__ == "__main__":
    register()