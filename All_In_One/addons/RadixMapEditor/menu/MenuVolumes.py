from bpy.types import Menu

class MenuVolumes(Menu):
  bl_idname = "radixMenu.volumes"
  bl_label = "Volumes"

  def draw(self, context):
    layout = self.layout

    layout.operator("radix.volume_add_acid", icon='MESH_CUBE', text="Acid")
