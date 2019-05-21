import bpy
import os
import xml.etree.cElementTree as tree
import xml.dom.minidom as minidom
import math
import re

from .managers import MaterialManager as MM
from .importer import Importer


class Exporter():
  filePath = ""
  decimalPoints = 4

  def __init__(self, filePath, decimalPoints=4):
    self.filePath = filePath
    self.decimalPoints = decimalPoints

  def writeMaterials(self, root, mats):
    materials = ((k, mats[k]) for k in sorted(mats, key=mats.get))
    materialElement = tree.SubElement(root, "materials")

    for name, index in materials:
      element = tree.SubElement(materialElement, "material")
      element.set("id", str(index))
      element.set("name", name)

  def storePosition(self, element, object):
    element.set("x", str(round(object.location[0], self.decimalPoints)))
    element.set("y", str(round(object.location[2], self.decimalPoints)))
    element.set("z", str(-round(object.location[1], self.decimalPoints)))

  def prepareRot(self, degree):
    return str(round(degree % 360, self.decimalPoints))

  def checkRotation(self, object):
    rotation = object.matrix_world.to_euler('XYZ')

    for i in rotation:
      if self.prepareRot(i) != "0.0":
        return True
    return False

  def storeRotation(self, element, object):
    rotation = object.matrix_world.to_euler('XYZ')

    element.set("x", self.prepareRot(math.degrees(rotation.x)))
    element.set("y", self.prepareRot(math.degrees(rotation.z)))
    element.set("z", self.prepareRot(math.degrees(-rotation.y)))

  def storeScale(self, element, object):
    element.set("x", str(round(object.dimensions[0], self.decimalPoints)))
    element.set("y", str(round(object.dimensions[2], self.decimalPoints)))
    element.set("z", str(round(object.dimensions[1], self.decimalPoints)))

  def storeColor(self, element, color):
    element.set("r", str(round(color[0], self.decimalPoints)))
    element.set("g", str(round(color[1], self.decimalPoints)))
    element.set("b", str(round(color[2], self.decimalPoints)))

  def storeName(self, element, name):
    if name:
      element.set("name", name)

  def writeLampToTree(self, object, targetTree):
    lamp = object.data

    colorArray = lamp.color
    lightDistance = lamp.distance
    lightEnergy = lamp.energy

    lightElement = tree.SubElement(targetTree, "light")
    self.storeName(lightElement, object.radixName)

    positionElement = tree.SubElement(lightElement, "position")
    self.storePosition(positionElement, object)

    colorElement = tree.SubElement(lightElement, "color")
    self.storeColor(colorElement, colorArray)

    lightElement.set("distance", str(round(lightDistance, self.decimalPoints)))
    lightElement.set("energy", str(round(lightEnergy, self.decimalPoints)))

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

    if os.path.isfile(self.filePath):
      oldMap = Importer(self.filePath)
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
        if object.radixTypes in {"spawn", "destination"}:
          boxElement = tree.SubElement(root, object.radixTypes)
        else:
          continue

        self.storeName(boxElement, object.radixName)

        positionElement = tree.SubElement(boxElement, "position")
        self.storePosition(positionElement, object)

        rotation = object.matrix_world.to_euler('XYZ')

        rotationElement = tree.SubElement(boxElement, "rotation")
        rotationElement.set("x", self.prepareRot(math.degrees(rotation.x) - 90))
        rotationElement.set("y", self.prepareRot(math.degrees(rotation.z)))
        rotationElement.set("z", "0.0")
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

            if object.radixTriggerTypes in {"map", "screen"}:
              boxElement.set("file", object.radixTriggerFilepath)

            if object.radixTriggerTypes == "audio":
              boxElement.set("file", object.radixTriggerFilepath)
              boxElement.set("loop", self.setBool(object.radixTriggerAudioLoop))

            if object.radixTriggerTypes in {"teleport", "checkpoint"}:
              boxElement.set("destination", object.radixTriggerDestination)

            if object.radixTriggerTypes == "remove":
              boxElement.set("action", self.setBool(object.radixTriggerRemoveAction))
              boxElement.set("ref", object.radixTriggerRemoveReference)
              boxElement.set("toogle", self.setBool(object.radixTriggerRemoveToogle))
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
          self.storeName(boxElement, object.radixName)
          positionElement = tree.SubElement(boxElement, "position")
          self.storePosition(positionElement, object)

          if self.checkRotation(object):
            rotationElement = tree.SubElement(boxElement, "rotation")
            self.storeRotation(rotationElement, object)

          scaleElement = tree.SubElement(boxElement, "scale")
          self.storeScale(scaleElement, object)

    xml = minidom.parseString(tree.tostring(root))

    file = open(self.filePath, "w")
    fix = re.compile(r"((?<=>)(\n[\t]*)(?=[^<\t]))|(?<=[^>\t])(\n[\t]*)(?=<)")
    fixed_output = re.sub(fix, "", xml.toprettyxml())
    file.write(fixed_output)
    file.close()
    return {'FINISHED'}
