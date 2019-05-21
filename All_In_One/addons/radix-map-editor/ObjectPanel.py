import bpy

from .managers import MaterialManager


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

  def draw(self, context):
    object = context.active_object
    layout = self.layout

    layout.prop(object, "radixName")
    layout.prop(object, "radixTypes")
    if object.radixTypes == "trigger":
      layout.prop(object, "radixTriggerTypes")

      if object.radixTriggerTypes in {"map", "audio", "screen"}:
        layout.prop(object, "radixTriggerFilepath")

        if object.radixTriggerTypes == "audio":
          layout.prop(object, "radixTriggerAudioLoop")
      elif object.radixTriggerTypes in {"teleport", "checkpoint"}:
        layout.prop(object, "radixTriggerDestination")
      elif object.radixTriggerTypes == "remove":
        layout.prop(object, "radixTriggerRemoveReference")
        layout.prop(object, "radixTriggerRemoveAction")
        layout.prop(object, "radixTriggerRemoveToogle")
    elif object.radixTypes == "volume":
      layout.prop(object, "radixVolumeTypes")

    if object.radixMaterial and object.type == 'MESH':
      layout.label(text="Material properties", icon='MATERIAL')

      layout.prop(object, "radixMaterial", text="Name")

      if object.radixMaterial != "none":
        mat = MaterialManager.MATERIALS[object.radixMaterial]

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Portalable: ")
        if mat['portalable']:
          row.label(text="Yes")
        else:
          row.label(text="No")

        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Kind: ")
        row.label(text=mat["kind"])
