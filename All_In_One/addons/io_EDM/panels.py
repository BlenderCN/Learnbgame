"""
panels

Contains blender UI panels to allow editing of custom data
"""

import bpy

class DataPanel(object):
  bl_space_type = 'PROPERTIES'
  bl_region_type = 'WINDOW'
  bl_context = "data"

class EDMDataPanel(DataPanel, bpy.types.Panel):
  bl_idname = "OBJECT_PT_edmtools"
  bl_label = "EDM Tools"
  
  @classmethod
  def poll(cls, context):
    return context.object.type == 'EMPTY' or context.object.type == "MESH"

  def draw(self, context):
    if context.object.type == "EMPTY":
      self.layout.prop(context.object.edm, "is_connector")

    elif context.object.type == "MESH":
      self.layout.prop(context.object.edm, "is_renderable")
      self.layout.prop(context.object.edm, "is_collision_shell")
      row = self.layout.row()
      row.active = context.object.edm.is_renderable
      row.prop(context.object.edm, "damage_argument")

class EDMEmptyLODPanel(DataPanel, bpy.types.Panel):
  bl_idname = "OBJECT_PT_edmLOD"
  bl_label = "LOD Root"

  @classmethod
  def poll(cls, context):
    return context.object.type == "EMPTY"

  def draw_header(self, context):
    self.layout.prop(context.object.edm, "is_lod_root", text="")

  def draw(self, context):
    if not context.object.edm.is_lod_root:
      return
    # Sort LOD children by the LOD distance
    children = sorted(context.object.children, key=lambda x: (x.edm.lod_min_distance, x.edm.lod_max_distance))
    for i, child in enumerate(children):
      box = self.layout.box()
      row = box.row()

      row.label(text=child.name, icon="OBJECT_DATA")
      row.prop(child.edm, "nouse_lod_distance")

      box.prop(child.edm, "lod_min_distance")
      if not child.edm.nouse_lod_distance:
        row = box.row()
        row.active = not child.edm.nouse_lod_distance
        row.prop(child.edm, "lod_max_distance")

class DopeActionProperties(bpy.types.Panel):
  """Creates a Panel in the Object properties window"""
  bl_label = "EDM Action Properties"
  bl_idname = "OBJECT_PT_dope_action"
  bl_space_type = 'DOPESHEET_EDITOR'
  bl_region_type = 'UI'
  bl_context = "action"

  @classmethod
  def poll(self, context):
    try:
      return context.object.animation_data.action != None
    except AttributeError:
        return False

  def draw(self, context):
    row = self.layout.row()
    row.prop(context.object.animation_data.action, "argument")


class EDMMaterialPanel(bpy.types.Panel):
  bl_label = "EDM Material Properties"
  bl_idname = "SCENE_PT_edm_materials"
  bl_space_type = 'PROPERTIES'
  bl_region_type = 'WINDOW'
  bl_context = "material"

  @classmethod
  def poll(self, context):
    return context.object.active_material != None

  def draw(self, context):
      layout = self.layout
      layout.label(text="EDM Base material:")
      layout.prop(context.object.active_material, "edm_material", text="")
      layout.prop(context.object.active_material, "edm_blending", text="Opacity")


def draw_timeline_argument_property(self, context):
    scene = context.scene
    layout = self.layout
    layout.prop(scene, "active_edm_argument", text="Argument")


def register():
  bpy.utils.register_class(EDMDataPanel)
  bpy.utils.register_class(EDMEmptyLODPanel)
  bpy.utils.register_class(DopeActionProperties)
  bpy.utils.register_class(EDMMaterialPanel)
  # bpy.types.TIME_HT_header.append(draw_timeline_argument_property)

def unregister():
  # bpy.types.TIME_HT_header.remove(draw_timeline_argument_property)
  bpy.utils.unregister_class(EDMMaterialPanel)
  bpy.utils.unregister_class(DopeActionProperties)
  bpy.utils.unregister_class(EDMEmptyLODPanel)
  bpy.utils.unregister_class(EDMDataPanel)




#   import bpy

# #bpy.types.Object.is_connector = bpy.props.BoolProperty(
# ##      default=False, 
# #      name="Is Connector?", 
# #      description="Is this empty a connector object?")

# 

# def register():
#     bpy.utils.register_class(HelloWorldPanel)


# def unregister():
#     bpy.utils.unregister_class(HelloWorldPanel)


# if __name__ == "__main__":
#     register()
