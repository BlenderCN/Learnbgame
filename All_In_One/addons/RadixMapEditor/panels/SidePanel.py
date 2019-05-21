import bpy


class SidePanel(bpy.types.Panel):
  bl_label = "Set Type"
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'TOOLS'
  bl_category = "Radix"

  def draw(self, context):
    layout = self.layout

    layout.label("Objects:")
    layout.operator("radix.manager_search_set_material", icon='MATERIAL')

    layout.label("Wall:")
    layout.operator("radix.wall_set_portalable", icon='MESH_PLANE', text="Portalable")
    layout.operator("radix.wall_set_metal", icon='META_PLANE', text="Metal")

    layout.label("Volume:")
    layout.operator("radix.volume_set_acid", icon='MESH_CUBE', text="Acid")

    layout.label("Trigger:")
    layout.operator("radix.trigger_set_death", icon='MESH_CUBE', text="Death")
    layout.operator("radix.trigger_set_radiation", icon='RADIO', text="Radiation")
    layout.operator("radix.trigger_set_win", icon='MESH_CUBE', text="Win")
    layout.operator("radix.trigger_search_map", icon='MESH_CUBE', text="Map")
    layout.operator("radix.trigger_search_audio", icon='MESH_CUBE', text="Audio")
    layout.operator("radix.trigger_set_teleport", icon='MESH_CUBE', text="Teleport")
    layout.separator()
    layout.operator("radix.set_destination", icon='MESH_CUBE', text="Destination")

    layout.label("Light:")
    layout.operator("radix.set_light_common", icon='LAMP_POINT')
    layout.operator("radix.set_light_end", icon='LAMP_POINT')

    layout.label("Map:")
    layout.operator("radix.fix_map", icon='SCRIPTWIN')
    layout.operator("radix.check_map", icon='QUESTION')
    layout.operator("radix.run_game", icon='GAME')
    layout.operator("radix.fast_export", icon='GAME')

    layout.label("Others:")
    layout.operator("radix.reload_materials", icon='SCRIPTWIN')
