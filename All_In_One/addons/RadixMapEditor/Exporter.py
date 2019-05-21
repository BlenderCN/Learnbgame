import bpy
import os
import xml.etree.cElementTree as tree
import xml.dom.minidom as minidom
import math
import re

from .managers import MaterialManager as MM
from .importer import Importer


class Exporter():
  def __init__(self, filePath, d_p=4):
    self.__filePath = filePath
    self.__d_p = d_p

  def writeMaterials(self, root, mats):
    materials = ((k, mats[k]) for k in sorted(mats, key=mats.get))
    materialElement = tree.SubElement(root, "materials")

    for name, index in materials:
      element = tree.SubElement(materialElement, "material")
      element.set("id", str(index))
      element.set("name", name)

  def storePosition(self, element, object):
    element.set("x", str(round(object.location[0], self.__d_p)))
    element.set("y", str(round(object.location[2], self.__d_p)))
    element.set("z", str(-round(object.location[1], self.__d_p)))

  def prepareRot(self, degree):
    return str(round(degree % 360, self.__d_p))

  def checkRotation(self, object):
    x = math.degrees(object.rotation_euler[0])
    y = math.degrees(object.rotation_euler[2])
    z = math.degrees(-object.rotation_euler[1])

    if self.prepareRot(x) == "0.0" and self.prepareRot(y) == "0.0" and self.prepareRot(z) == "0.0":
      return False
    return True

  def storeRotation(self, element, object):
    element.set("x", self.prepareRot(math.degrees(object.rotation_euler[0])))
    element.set("y", self.prepareRot(math.degrees(object.rotation_euler[2])))
    element.set("z", self.prepareRot(math.degrees(-object.rotation_euler[1])))

  def storeScale(self, element, object):
    element.set("x", str(round(object.dimensions[0], self.__d_p)))
    element.set("y", str(round(object.dimensions[2], self.__d_p)))
    element.set("z", str(round(object.dimensions[1], self.__d_p)))

  def storeColor(self, element, color):
    element.set("r", str(round(color[0], self.__d_p)))
    element.set("g", str(round(color[1], self.__d_p)))
    element.set("b", str(round(color[2], self.__d_p)))

  def writeLampToTree(self, object, targetTree):
    lamp = object.data

    colorArray = lamp.color
    lightDistance = lamp.distance
    lightEnergy = lamp.energy

    lightElement = tree.SubElement(targetTree, "light")

    positionElement = tree.SubElement(lightElement, "position")
    self.storePosition(positionElement, object)

    colorElement = tree.SubElement(lightElement, "color")
    self.storeColor(colorElement, colorArray)

    lightElement.set("distance", str(round(lightDistance, self.__d_p)))
    lightElement.set("energy", str(round(lightEnergy, self.__d_p)))

    if lamp.use_specular:
      lightElement.set("specular", "1")

  def setBool(self, value):
    if value:
      return "true"
    else:
      return "false"

  def execute(self, context):
    bpy.context.scene.fixObjects()

    prefs = bpy.context.user_preferences.addons[__package__].preferences
    objects = context.scene.objects
    root = tree.Element("map")

    matAttr = "material"

    if os.path.isfile(self.__filePath):
      oldMap = Importer(self.__filePath)
      oldMaterials = oldMap.getMaterials()
    else:
      oldMaterials = {}

    materials = MM.prepareExport(oldMaterials)
    self.writeMaterials(root, materials)

    for object in reversed(objects):
      if object.radixTypes:
        type = object.radixTypes
      else:
        type = "None"

      if object.type == 'LAMP':
        self.writeLampToTree(object, root)
      elif object.type == 'CAMERA':
        boxElement = tree.SubElement(root, "spawn")

        positionElement = tree.SubElement(boxElement, "position")
        self.storePosition(positionElement, object)

        rotationElement = tree.SubElement(boxElement, "rotation")
        rotationElement.set("x", self.prepareRot(math.degrees(object.rotation_euler[0]) - 90))
        rotationElement.set("y", self.prepareRot(math.degrees(object.rotation_euler[2])))
        rotationElement.set("z", "0")
      elif object.type == 'MESH':
        boxElement = None

        if type == "model":
          boxElement = tree.SubElement(root, "model")
          boxElement.set("mesh", object.radixModel)

          if object.radixMaterial in materials and object.radixMaterial not in MM.BLACKLIST:
            boxElement.set(matAttr, str(materials[object.radixMaterial]))
          else:
            boxElement.set(matAttr, str(materials[prefs.defaultMaterial]))
        elif type == "trigger":
          boxElement = tree.SubElement(root, "trigger")

          if object.radixTriggerTypes:
            boxElement.set("type", object.radixTriggerTypes)

            if object.radixTriggerTypes == "map":
              boxElement.set("file", object.radixTriggerFilepath)

            if object.radixTriggerTypes == "audio":
              boxElement.set("file", object.radixTriggerFilepath)
              boxElement.set("loop", self.setBool(object.radixTriggerAudioLoop))
        elif type == "wall":
          boxElement = tree.SubElement(root, "wall")

          if object.radixMaterial in materials and object.radixMaterial not in MM.BLACKLIST:
            boxElement.set(matAttr, str(materials[object.radixMaterial]))
          else:
            boxElement.set(matAttr, str(materials[prefs.defaultMaterial]))
        elif type == "volume":
          if object.radixVolumeTypes == "acid":
            boxElement = tree.SubElement(root, "acid")

        if boxElement is not None:
          positionElement = tree.SubElement(boxElement, "position")
          self.storePosition(positionElement, object)

          if self.checkRotation(object):
            rotationElement = tree.SubElement(boxElement, "rotation")
            self.storeRotation(rotationElement, object)

          scaleElement = tree.SubElement(boxElement, "scale")
          self.storeScale(scaleElement, object)

    xml = minidom.parseString(tree.tostring(root))

    file = open(self.__filePath, "w")
    fix = re.compile(r"((?<=>)(\n[\t]*)(?=[^<\t]))|(?<=[^>\t])(\n[\t]*)(?=<)")
    fixed_output = re.sub(fix, "", xml.toprettyxml())
    file.write(fixed_output)
    file.close()
    return {'FINISHED'}
