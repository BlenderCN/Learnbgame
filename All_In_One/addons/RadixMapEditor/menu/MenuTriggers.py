from bpy.types import Menu

class MenuTriggers(Menu):
  bl_idname = "radixMenu.triggers"
  bl_label = "Triggers"

  def draw(self, context):
    layout = self.layout

    layout.operator("radix.trigger_add_death", icon='MESH_CUBE', text="Death")
    layout.operator("radix.trigger_add_radiation", icon='RADIO', text="Radiation")
    layout.operator("radix.trigger_add_win", icon='MESH_CUBE', text="Win")
    layout.operator("radix.trigger_add_map", icon='MESH_CUBE', text="Map")
    layout.operator("radix.trigger_add_audio", icon='MESH_CUBE', text="Audio")
