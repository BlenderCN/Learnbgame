from bpy.types import Menu

class MenuMain(Menu):
  bl_idname = "radixMenu.main"
  bl_label = "Radix"

  def draw(self, context):
    layout = self.layout

    layout.menu("radixMenu.walls", icon='MOD_BUILD')
    layout.menu("radixMenu.volumes", icon='MOD_FLUIDSIM')
    layout.menu("radixMenu.triggers", icon='MOD_SCREW')
    layout.menu("radixMenu.lights", icon='LAMP_POINT')

    layout.operator("object.camera_add", text="Spawn (Camera)", icon='OUTLINER_OB_CAMERA')
