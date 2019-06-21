from bpy.types import Menu

class MenuWalls(Menu):
  bl_idname = "radixMenu.walls"
  bl_label = "Walls"

  def draw(self, context):
    layout = self.layout

    layout.operator("radix.wall_add_portalable", icon='MESH_PLANE', text="Portalable")
    layout.operator("radix.wall_add_metal", icon='META_PLANE', text="Metal")
