import bpy
import math
import os
import xml.etree.cElementTree as ET

from .managers import ModelManager
from .operatorHelpers import simpleCube


class Importer():
  def __init__(self, filePath, deleteWorld=True):
    self.__filePath = filePath
    self.__deleteWorld = deleteWorld

  def deleteWorld(self):
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
    x = math.radians(float(param.get("x")))
    y = math.radians(float(param.get("y")))
    z = math.radians(-float(param.get("z")))
    return [x, z, y]

  def extrackColor(self, param):
    r = float(param.get("r"))
    g = float(param.get("g"))
    b = float(param.get("b"))
    return [r, g, b]

  def createCube(self, child):
    if simpleCube():
      object = bpy.context.selected_objects[0]

      if object:
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
    realpath = os.path.realpath(os.path.expanduser(self.__filePath))
    tree = ET.parse(realpath)
    root = tree.getroot()

    return self.extractMaterials(root)

  def getBool(self, value):
    trueValues = ('true', 'yes')

    return value.lower() in trueValues

  def execute(self, context):
    if self.__deleteWorld:
      self.deleteWorld()

    prefs = bpy.context.user_preferences.addons[__package__].preferences
    realpath = os.path.realpath(os.path.expanduser(self.__filePath))
    tree = ET.parse(realpath)
    root = tree.getroot()
    materials = self.extractMaterials(root)

    for child in root:
      if child.tag == "wall":
        object = self.createCube(child)
        if object:
          object.radixTypes = "wall"

          matAttr = "material"

          if matAttr in child.attrib:
            mid = child.get(matAttr)
            object.radixMaterial = materials[mid]
          else:
            object.radixMaterial = prefs.defaultMaterial
      elif child.tag == "acid":
        object = self.createCube(child)
        if object:
          bpy.ops.radix.volume_set_acid()
      elif child.tag == "spawn":
        bpy.ops.object.camera_add()

        object = bpy.context.active_object
        if object:
          for param in child:
            if param.tag == "position":
              object.location = self.extractPosition(param)
            elif param.tag == "rotation":
              rotation = [
                math.radians(float(param.get("x")) + 90),
                math.radians(0),
                math.radians(float(param.get("y")))
              ]
              object.rotation_euler = rotation
      elif child.tag == "light":
        bpy.ops.object.lamp_add(type='POINT')

        object = bpy.context.active_object
        if object:
          lamp = object.data

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
              loop = self.getBool(child.get('loop'))

            if 'file' in child.attrib:
              bpy.ops.radix.trigger_set_audio(filePath=child.get('file'), loop=loop)
            else:
              bpy.data.objects.remove(object)
          else:
            bpy.data.objects.remove(object)
      elif child.tag == "object" or child.tag == "model":
        mesh = child.get("mesh")
        matAttr = "material"

        if matAttr in child.attrib:
          mid = child.get(matAttr)
          if not ModelManager.create(mesh, materials[mid]):
            continue
        elif not ModelManager.create(mesh):
          continue

        object = bpy.context.selected_objects[0]
        if object:
          for param in child:
            if param.tag == "position":
              object.location = self.extractPosition(param)
            elif param.tag == "rotation":
              object.rotation_euler = self.extractRotation(param)
            elif param.tag == "scale":
              object.dimensions = self.extractDimensions(param)
    return {'FINISHED'}
