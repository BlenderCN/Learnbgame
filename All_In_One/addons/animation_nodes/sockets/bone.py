import bpy
from bpy.props import *
from bpy.types import Bone
from .. base_types import AnimationNodeSocket

class BoneSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_BoneSocket"
    bl_label = "Bone Socket"
    dataType = "Bone"
    allowedInputTypes = ["Bone"]
    drawColor = (0.33, 0.63, 0.83, 1)
    storable = False
    comparable = True

    @classmethod
    def getDefaultValue(cls):
        return None

    @classmethod
    def getDefaultValueCode(cls):
        return "None"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Bone) or value is None:
            return value, 0
        return cls.getDefaultValue(), 2


class BoneListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_BoneListSocket"
    bl_label = "Bone List Socket"
    dataType = "Bone List"
    baseDataType = "Bone"
    allowedInputTypes = ["Bone List"]
    drawColor = (0.33, 0.63, 0.83, 0.5)
    storable = False
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return []

    @classmethod
    def getDefaultValueCode(cls):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, Bone) or element is None for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
