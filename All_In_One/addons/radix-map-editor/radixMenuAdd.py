from bpy.types import Menu


def radix_add_menu(self, context):
  layout = self.layout

  layout.menu("radixMenu.main", icon='WORLD')
  layout.separator()


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


class MenuWalls(Menu):
  bl_idname = "radixMenu.walls"
  bl_label = "Walls"

  def draw(self, context):
    layout = self.layout

    layout.operator("radix.wall_add_portalable", icon='MESH_PLANE', text="Portalable")
    layout.operator("radix.wall_add_metal", icon='META_PLANE', text="Metal")


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


class MenuVolumes(Menu):
  bl_idname = "radixMenu.volumes"
  bl_label = "Volumes"

  def draw(self, context):
    layout = self.layout

    layout.operator("radix.volume_add_acid", icon='MESH_CUBE', text="Acid")


class MenuLights(Menu):
  bl_idname = "radixMenu.lights"
  bl_label = "Lights"

  def draw(self, context):
    layout = self.layout

    layout.operator("radix.add_light_common", icon='LAMP_POINT')
    layout.operator("radix.add_light_end", icon='LAMP_POINT')
