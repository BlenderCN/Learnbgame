import bpy
import os

from . import MPTypes
from .managers import MaterialManager as MM


class SaveMaterial(bpy.types.Operator):
  bl_idname = "radix.mp_save_material"
  bl_label = "Save"

  def execute(self, context):
    wm = bpy.context.window_manager

    name = wm.MPMaterials[wm.MPItemId].matName
    material = MM.MATERIALS[name]

    material["fancyname"] = wm.radixMatFancyName
    material["kind"] = wm.radixMatKind
    material["tags"] = wm.radixMatTags
    material["portalable"] = wm.radixMatPortalable

    MM.saveMaterial(name)
    initRow(wm.MPMaterials[wm.MPItemId], wm.MPItemId, name, material)

    return {'FINISHED'}


class EditMaterial(bpy.types.Operator):
  bl_idname = "radix.mp_edit_material"
  bl_label = "Toogle Edit"
  bl_description = "Edit selected material"

  def execute(self, context):
    wm = bpy.context.window_manager

    wm.radixMatEdit = not wm.radixMatEdit

    if wm.radixMatEdit:
      MPTypes.MPItemIdUpdate(self, context)

    return {'FINISHED'}


class SetMaterial(bpy.types.Operator):
  bl_idname = "radix.mp_set_material"
  bl_label = "Set"
  bl_description = "Set material to selected objects"
  bl_options = {'UNDO'}

  def execute(self, context):
    wm = bpy.context.window_manager

    material = wm.MPMaterials[wm.MPItemId].matName

    if material != "none":
      objects = bpy.context.selected_objects
      for object in objects:
        if object.type == 'MESH' and object.radixTypes != "none":
          object.radixMaterial = material
    return {'FINISHED'}


class UIList(bpy.types.UIList):
  def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
    if self.layout_type in {'DEFAULT', 'COMPACT'}:
      split = layout.split(0.3)
      split.label(item.label)
      split.label(item.description)
    elif self.layout_type in {'GRID'}:
      pass

    self.use_filter_show = True

  def check(self, context):
    return True


class MaterialPanel(bpy.types.Panel):
  bl_label = "Radix Material UI"
  bl_space_type = 'PROPERTIES'
  bl_region_type = 'WINDOW'
  bl_context = "material"

  @classmethod
  def poll(cls, context):
    # MPItemIdUpdate(self, context)
    return True

  def draw(self, context):
    wm = bpy.context.window_manager

    layout = self.layout

    name = wm.MPMaterials[wm.MPItemId].matName
    material = MM.MATERIALS[name]

#    if name != "none":
#      layout.template_preview(bpy.data.textures[material["fancyname"]], show_buttons=True)

    layout.template_list("UIList", "", wm, "MPMaterials", wm, "MPItemId")

    row = layout.row(align=True)
    row.alignment = 'EXPAND'
    row.operator("radix.mp_set_material")
    row.operator("radix.mp_edit_material")

    layout.label(text="Material properties", icon='MATERIAL')

    if name != "none":
      row = layout.row(align=True)
      row.alignment = 'EXPAND'
      row.label(text="Name : ")
      row.label(text=name)

      if wm.radixMatEdit:
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(wm, "radixMatFancyName")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(wm, "radixMatPortalable")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(wm, "radixMatKind")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.prop(wm, "radixMatTags")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("radix.mp_save_material")
      else:
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="FancyName : ")
        row.label(text=material["fancyname"])

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Portalable : ")
        if material["portalable"]:
          row.label(text="Yes")
        else:
          row.label(text="No")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Kind : ")
        row.label(text=material["kind"])

        if "tags" in material:
          row = layout.row(align=True)
          row.alignment = 'EXPAND'
          row.label(text="Tags : ")
          row.label(text=material["tags"])
    else:
      layout.label(text="Nothing is here")

  def check(self, context):
    # MPItemIdUpdate(self, context)
    return True


def initRow(item, i, name, data):
  item.name = "".join(
    (data["fancyname"], str(i), name, data["kind"], data["tags"] if "tags" in data else "")
  )
  item.label = data["fancyname"]
  item.description = data["kind"]
  item.matName = name

  if "tags" in data:
    item.description += " - " + data["tags"]


def initRows():
  wm = bpy.context.window_manager

  try:
    wm.MPMaterials.clear()
  except:
    pass

  for i, (name, data) in enumerate(MM.MATERIALS.items(), 1):
    item = wm.MPMaterials.add()
    initRow(item, i, name, data)
