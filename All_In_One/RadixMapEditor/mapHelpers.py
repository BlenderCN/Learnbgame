import bpy
import os
from bpy.props import IntProperty


def fixObjects(self):
  objects = bpy.context.scene.objects
  bpy.ops.object.select_all(action='DESELECT')

  for object in objects:
    if object.type == 'MESH':
      type = object.radixTypes

      if type in {"wall", "trigger", "volume"}:
        bpy.context.scene.objects.active = object
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')


def isOverObject(self, object):
  pMin = object.location[0] - abs(object.dimensions[0]) / 2
  pMax = object.location[0] + abs(object.dimensions[0]) / 2

  if self.location[0] > pMin and self.location[0] < pMax:
    pMin = object.location[1] - abs(object.dimensions[1]) / 2
    pMax = object.location[1] + abs(object.dimensions[1]) / 2

    if self.location[1] > pMin and self.location[1] < pMax:
      pMax = object.location[2] + abs(object.dimensions[2]) / 2

      if self.location[2] >= pMax + 1:
        return 1
      elif self.location[2] >= pMax:
        return 2
  return 0


def checkSpawnPosition(objects):
  for object in objects:
    if object.type == 'CAMERA':
      camera = object
      break

  if not camera:
    return 0

  for object in objects:
    if object.type == 'MESH' and object.radixTypes == "wall":
      isOver = camera.isOverObject(object)
      if isOver != 0:
        return isOver
  return 0


def countObjects(self, objects=None):
  prefs = bpy.context.user_preferences.addons[__package__].preferences
  dataDir = os.path.expanduser(prefs.dataDir)

  if not objects:
    objects = self.objects

  result = {
    "camera":       0,
    "wall":         0,
    "acid":         0,
    "triggerDeath": 0,
    "triggerMapEmpty": 0,
    "triggerMapWrong": 0,
    "triggerAudioEmpty": 0,
    "triggerAudioWrong": 0,
    "light":        0,
    "objectNoMat":  0  # Objects Without Material
  }

  for object in objects:
    if object.radixTypes:
      type = object.radixTypes
    else:
      type = "None"

    if object.type == 'LAMP':
      result["light"] += 1
    elif object.type == 'CAMERA':
      result["camera"] += 1
    elif object.type == 'MESH':
      if type == "trigger":
        triggerType = object.radixTriggerTypes
        filepath = object.radixTriggerFilepath

        if triggerType == "death":
          result["triggerDeath"] += 1
        elif triggerType == "map":
          if not filepath:
            result["triggerMapEmpty"] += 1
          elif not os.path.isfile(os.path.join(dataDir, "maps", filepath)):
            result["triggerMapWrong"] += 1
        elif triggerType == "audio":
          if not filepath:
            result["triggerAudioEmpty"] += 1
          elif not os.path.isfile(os.path.join(dataDir, "audio", filepath)):
            result["triggerAudioWrong"] += 1
      if type == "wall":
        result["wall"] += 1
      if type == "volume":
        if object.radixVolumeTypes == "acid":
          result["acid"] += 1
      if type in {"model", "wall"}:
        if not object.radixMaterial or object.radixMaterial == "none":
          result["objectNoMat"] += 1
  return result


class CheckMapDialog(bpy.types.Operator):
  bl_idname = "object.map_check_dialog"
  bl_label = "Check map results"

  camera = IntProperty(name="Number of cameras")
  light = IntProperty(name="Number of lights")
  wall = IntProperty(name="Number of walls")
  modelsNoMat = IntProperty(name="Number of models without material")
  triggerMapEmpty = IntProperty(name="Number of map triggers without file path")
  triggerMapWrong = IntProperty(name="Number of map triggers with wrong file path")
  triggerAudioEmpty = IntProperty(name="Number of audio triggers without file path")
  triggerAudioWrong = IntProperty(name="Number of audio triggers with wrong file path")

  def execute(self, context):
    return {'FINISHED'}

  def invoke(self, context, event):
    return context.window_manager.invoke_props_dialog(self, 400)

  def draw(self, context):
    objects = context.scene.objects
    result = context.scene.countObjects(objects)
    layout = self.layout
    error = False

    if result["camera"] != 1:
      self.camera = result["camera"]
      error = True

      layout.prop(self, "camera")

      if result["camera"] == 0:
        layout.label(text="There is no camera.", icon='CANCEL')
      else:
        layout.label(text="There are too many cameras.", icon='ERROR')

      layout.label(text="The camera object is used for determining the spawn position.",
                   icon='INFO')
      layout.label(text="Use it exactly once.", icon='INFO')
      layout.separator()
    if result["light"] == 0:
      error = True

      layout.label(text="There is no light in the map you need at least one light.", icon='CANCEL')
      layout.separator()
    elif result["light"] > 5:
      self.light = result["light"]
      error = True

      layout.prop(self, "light")
      layout.label(text="There are too many lights.", icon='INFO')
      layout.label(text="This is a performance issue and has to be fixed..", icon='INFO')
      layout.separator()
    if result["wall"] == 0:
      self.wall = result["wall"]
      error = True

      layout.prop(self, "wall")
      layout.label(text="There isn't a wall.", icon='ERROR')
      layout.separator()
    if result['triggerDeath'] < result['acid']:
      error = True

      layout.label(text="Acid without death trigger.", icon='ERROR')
      layout.label(text="Use death trigger for each volume of acid.", icon='INFO')
      layout.separator()
    if result["camera"] == 1:
      isOver = checkSpawnPosition(objects)

      if isOver == 0 or isOver == 2:
        if isOver == 0:
          error = True

          layout.label(text="Camera is in the air.", icon='CANCEL')
        else:
          error = True

          layout.label(text="Camera is very close to the floor.", icon='ERROR')
          layout.label(text="Player can get stuck in the floor or unable to go through portal.",
                       icon='INFO')

        layout.label(text="Remember, we are using camera as spawn position.", icon='INFO')
        layout.separator()
    if result["objectNoMat"] != 0:
      error = True
      self.modelsNoMat = result["objectNoMat"]

      layout.prop(self, "modelsNoMat")

      row = layout.split(0.75)
      row.label(text="There are objects without assigned material.", icon='ERROR')
      row.operator("radix.fix_materials")

      layout.separator()
    if result["triggerMapEmpty"] > 0:
      error = True
      self.triggerMapEmpty = result["triggerMapEmpty"]

      layout.prop(self, "triggerMapEmpty")
      layout.separator()
    if result["triggerMapWrong"] > 0:
      error = True
      self.triggerMapWrong = result["triggerMapWrong"]

      layout.prop(self, "triggerMapWrong")
      layout.separator()
    if result["triggerAudioEmpty"] > 0:
      error = True
      self.triggerAudioEmpty = result["triggerAudioEmpty"]

      layout.prop(self, "triggerAudioEmpty")
      layout.separator()
    if result["triggerAudioWrong"] > 0:
      error = True
      self.triggerAudioWrong = result["triggerAudioWrong"]

      layout.prop(self, "triggerAudioWrong")
      layout.separator()

    if not error:
      layout.label(text="Nice work. There are no errors or warnings.", icon='FILE_TICK')
