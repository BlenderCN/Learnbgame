import bpy
import os
import xml.etree.cElementTree as ET

from math import radians
from mathutils import Euler

from .managers import ModelManager
from .operatorHelpers import simpleCube


class Importer():
  filePath = ""
  cleanScene = True

  def __init__(self, filePath, cleanScene=True):
    self.filePath = filePath
    self.cleanScene = cleanScene

  def clearScene(self):
    """Clean current scene"""
    scene = bpy.context.scene

    for ob in scene.objects:
      ob.select = True
      bpy.ops.object.delete()

  def extractMaterials(self, root):
    materials = {}

    for child in root:
      if child.tag == "materials":
        for mat in child:
          mid = mat.get("id")
          name = mat.get("name")

          materials[mid] = name
    return materials

  def extractPosition(self, param):
    x = float(param.get("x"))
    y = float(param.get("y"))
    z = float(param.get("z"))
    return [x, -z, y]

  def extractDimensions(self, param):
    x = float(param.get("x"))
    y = float(param.get("y"))
    z = float(param.get("z"))
    return [x, z, y]

  def extractRotation(self, param):
    x = float(param.get("x"))
    y = float(param.get("y"))
    z = -float(param.get("z"))
    return Euler(map(radians, (x, z, y)), 'XYZ')

  def extrackColor(self, param):
    r = float(param.get("r"))
    g = float(param.get("g"))
    b = float(param.get("b"))
    return [r, g, b]

  def extractName(self, element):
    if "name" in element.attrib:
      return element.get("name")
    else:
      return ""

  def createCube(self, child):
    if simpleCube():
      object = bpy.context.selected_objects[0]

      if object:
        object.radixName = self.extractName(child)

        for param in child:
          if param.tag == "position":
            object.location = self.extractPosition(param)
          elif param.tag == "rotation":
            object.rotation_euler = self.extractRotation(param)
          elif param.tag == "scale":
            object.dimensions = self.extractDimensions(param)

        return object
    return False

  def getMaterials(self):
    realpath = os.path.realpath(os.path.expanduser(self.filePath))
    tree = ET.parse(realpath)
    root = tree.getroot()

    return self.extractMaterials(root)

  def xmlGetBool(self, value):
    trueValues = ('true', 'yes')

    return value.lower() in trueValues

  def execute(self, context):
    if self.cleanScene:
      self.clearScene()

    prefs = bpy.context.user_preferences.addons[__package__].preferences
    realpath = os.path.realpath(os.path.expanduser(self.filePath))
    tree = ET.parse(realpath)
    root = tree.getroot()
    materials = self.extractMaterials(root)

    for child in root:
      if child.tag == "wall":
        object = self.createCube(child)
        if object:
          object.radixTypes = "wall"

          if "material" in child.attrib:
            mid = child.get("material")
            object.radixMaterial = materials[mid]
          else:
            object.radixMaterial = prefs.defaultMaterial
      elif child.tag == "acid":
        object = self.createCube(child)
        if object:
          bpy.ops.radix.volume_set_acid()
      elif child.tag in {"spawn", "destination"}:
        bpy.ops.object.camera_add()

        object = bpy.context.active_object
        if object:
          if child.tag == "spawn":
            bpy.ops.radix.camera_set_spawn()
          elif child.tag == "destination":
            bpy.ops.radix.camera_set_destination()
          else:
            bpy.data.objects.remove(object)
            continue

          object.radixName = self.extractName(child)

          object.rotation_euler = Euler(map(radians, (90.0, 0.0, 0.0)), 'XYZ')

          for param in child:
            if param.tag == "position":
              object.location = self.extractPosition(param)
            elif param.tag == "rotation":
              rotation = [
                float(param.get("x")) + 90.0,
                0.0,
                float(param.get("y"))
              ]
              object.rotation_euler = Euler(map(radians, rotation), 'XYZ')
      elif child.tag == "light":
        bpy.ops.object.lamp_add(type='POINT')

        object = bpy.context.active_object
        if object:
          lamp = object.data
          object.radixName = self.extractName(child)

          for param in child:
            if param.tag == "position":
              object.location = self.extractPosition(param)
            elif param.tag == "color":
              lamp.color = self.extrackColor(param)

          lamp.distance = float(child.get("distance"))
          lamp.energy = float(child.get("energy"))

          lamp.use_specular = False
          if "specular" in child.attrib and child.get("specular") == "1":
            lamp.use_specular = True
      elif child.tag == "trigger":
        object = self.createCube(child)
        if object:
          type = child.get("type")
          if type == "death":
            bpy.ops.radix.trigger_set_death()
          elif type == "radiation":
            bpy.ops.radix.trigger_set_radiation()
          elif type == "win":
            bpy.ops.radix.trigger_set_win()
          elif type == "map":
            if 'file' in child.attrib:
              bpy.ops.radix.trigger_set_map(filePath=child.get('file'))
            else:
              bpy.data.objects.remove(object)
          elif type == "audio":
            loop = False
            if 'loop' in child.attrib:
              loop = self.xmlGetBool(child.get('loop'))

            if 'file' in child.attrib:
              bpy.ops.radix.trigger_set_audio(filePath=child.get('file'), loop=loop)
            else:
              bpy.data.objects.remove(object)
          elif type == "teleport":
            if 'destination' in child.attrib:
              bpy.ops.radix.trigger_set_teleport(filePath=child.get('destination'))
            else:
              bpy.data.objects.remove(object)
          elif type == "checkpoint":
            if 'destination' in child.attrib:
              bpy.ops.radix.trigger_set_checkpoint(filePath=child.get('destination'))
            else:
              bpy.data.objects.remove(object)
          elif type == "screen":
            if 'file' in child.attrib:
              bpy.ops.radix.trigger_set_screen(filePath=child.get('file'))
            else:
              bpy.data.objects.remove(object)
          elif type == "remove":
            if 'ref' in child.attrib:
              removeToogle = False
              removeAction = False

              if "toogle" in child.attrib:
                removeToogle = self.xmlGetBool(child.get('toogle'))

              if "action" in child.attrib:
                removeAction = self.xmlGetBool(child.get('action'))

              bpy.ops.radix.trigger_set_remove(
                filePath=child.get('ref'),
                removeToogle=removeToogle,
                removeAction=removeAction
              )
            else:
              bpy.data.objects.remove(object)
          else:
            bpy.data.objects.remove(object)
      elif child.tag == "model":
        mesh = child.get("mesh")
        matAttr = "material"

        if matAttr in child.attrib:
          materialId = child.get(matAttr)
          if not ModelManager.create(mesh, materials[materialId]):
            continue
        elif not ModelManager.create(mesh):
          continue

        object = bpy.context.selected_objects[0]
        if object:
          object.radixName = self.extractName(child)

          for param in child:
            if param.tag == "position":
              object.location = self.extractPosition(param)
            elif param.tag == "rotation":
              object.rotation_euler = self.extractRotation(param)
            elif param.tag == "scale":
              object.dimensions = self.extractDimensions(param)

    bpy.ops.object.select_all(action='DESELECT')

    return {'FINISHED'}
