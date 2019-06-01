from bpy.types import Menu

class MenuLights(Menu):
  bl_idname = "radixMenu.lights"
  bl_label = "Lights"

  def draw(self, context):
    layout = self.layout

    layout.operator("radix.add_light_common", icon='LAMP_POINT')
    layout.operator("radix.add_light_end", icon='LAMP_POINT')
