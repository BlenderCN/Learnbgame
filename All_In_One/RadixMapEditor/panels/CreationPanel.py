import bpy


class CreationPanel(bpy.types.Panel):
  bl_label = "Radix"
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'TOOLS'
  bl_context = "objectmode"
  bl_category = "Create"

  def draw(self, context):
    layout = self.layout

    layout.label("Objects:")
    layout.operator("radix.manager_search_add_model", icon='MESH_CUBE')
    layout.operator("radix.manager_search_set_material", icon='MATERIAL')

    layout.label("Walls:")
    layout.operator("radix.wall_add_portalable", icon='MESH_PLANE', text="Portalable")
    layout.operator("radix.wall_add_metal", icon='META_PLANE', text="Wall")

    layout.label("Volumes:")
    layout.operator("radix.volume_add_acid", icon='MESH_CUBE', text="Acid")

    layout.label("Triggers:")
    layout.operator("radix.trigger_add_death", icon='MESH_CUBE', text="Death")
    layout.operator("radix.trigger_add_radiation", icon='RADIO', text="Radiation")
    layout.operator("radix.trigger_add_win", icon='MESH_CUBE', text="Win")
    layout.operator("radix.trigger_add_map", icon='MESH_CUBE', text="Map")
    layout.operator("radix.trigger_add_audio", icon='MESH_CUBE', text="Audio")
    layout.operator("radix.trigger_add_teleport", icon='MESH_CUBE', text="Teleport")
    layout.separator()
    layout.operator("radix.trigger_add_destination", icon='MESH_CUBE', text="Destination")
    
    layout.label("Lights:")
    layout.operator("radix.add_light_common", icon='LAMP_POINT')
    layout.operator("radix.add_light_end", icon='LAMP_POINT')
