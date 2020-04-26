import bpy

from ..managers import MaterialManager


class ObjectPanel(bpy.types.Panel):
  bl_label = "Radix"
  bl_space_type = 'PROPERTIES'
  bl_region_type = 'WINDOW'
  bl_context = "object"

  @classmethod
  def poll(cls, context):
    if context.object.radixTypes != "none":
      return True
    return False

  def drawMaterialSelection(self, context):
    object = context.active_object
    layout = self.layout
    layout.label(text="Material properties", icon='MATERIAL')

    layout.prop(object, "radixMaterial", text="Name ")

    if object.radixMaterial != "none":
      mat = MaterialManager.MATERIALS[object.radixMaterial]

      row = layout.row(align=True)
      row.alignment = 'EXPAND'
      row.label(text="Portalable : ")
      if mat['portalable']:
        row.label(text="Yes")
      else:
        row.label(text="No")

      row = layout.row(align=True)
      row.alignment = 'EXPAND'
      row.label(text="Kind : ")
      row.label(text=mat["kind"])

  def draw(self, context):
    object = context.active_object
    layout = self.layout
    type        = object.radixTypes
    triggerType = object.radixTriggerTypes
    layout.prop(object, "radixTypes")
    if type == "trigger":
      layout.prop(object, "radixTriggerTypes")

      if triggerType in {"map", "audio"}:
        layout.prop(object, "radixTriggerFilepath")

        if triggerType == "audio":
          layout.prop(object, "radixTriggerAudioLoop")

    elif type == "volume":
      layout.prop(object, "radixVolumeTypes")
    elif type == "destination":
      layout.prop(object, "radixDestinationName", text="Name ")
    if type in {"model", "wall", "volume"}:
      self.drawMaterialSelection(context)
