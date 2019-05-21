# -*- python-indent: 4; coding: iso-8859-1; mode: python -*-
# Copyright (C) 2008 Cedric Pinson, Jeremy Moles
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#  Cedric Pinson <cedric.pinson@plopbyte.com>
#  Jeremy Moles <jeremy@emperorlinux.com>


import bpy
import json
import mathutils
from collections import OrderedDict

Matrix = mathutils.Matrix
Vector = mathutils.Vector
FLOATPRE = 5
CONCAT = lambda s, j="": j.join(str(v) for v in s)
STRFLT = lambda f: "%%.%df" % FLOATPRE % float(f)
INDENT = 2
VERSION = (0, 0, 0)


def findNode(name, root):
    if root.name == name:
        return root
    if isinstance(root, Group) is False:
        return None
    for i in root.children:
        found = findNode(name, i)
        if found is not None:
            return found
    return None


def findMaterial(name, root):
    if root.stateset is not None:
        for i in root.stateset.attributes:
            if isinstance(i, Material) is True and i.name == name:
                return i
    if isinstance(root, Geode) is True:
        for i in root.drawables:
            found = findMaterial(name, i)
            if found is not None:
                return found
    if isinstance(root, Group) is True:
        for i in root.children:
            found = findMaterial(name, i)
            if found is not None:
                return found
    return None


class Writer(object):
    instances = {}
    wrote_elements = {}
    file_object = None

    def __init__(self, comment=None):
        object.__init__(self)
        self.comment = comment
        self.indent_level = 0
        self.counter = len(Writer.instances)
        Writer.instances[self] = True

    def writeFile(self, output):
        self.writeHeader(output)
        self.write(output)

    def writeHeader(self, output):
        output.write("#Ascii Scene\n".encode('utf-8'))
        output.write("#Version 92\n".encode('utf-8'))
        output.write(("#Generator osgexport %d.%d.%d\n\n" % VERSION).encode('utf-8'))

    def write(self, output):
        Writer.serializeInstanceOrUseIt(self, output)

    def encode(self, string):
        text = string.replace("\t", "") \
                     .replace("#", (" " * INDENT)) \
                     .replace("$", (" " * (INDENT * self.indent_level)))
        return text.encode('utf-8')

    def writeMatrix(self, output, matrix):
        if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 62:
            for i in range(0, 4):
                output.write(self.encode("$##%s %s %s %s\n" % (STRFLT(matrix[0][i]),
                                                               STRFLT(matrix[1][i]),
                                                               STRFLT(matrix[2][i]),
                                                               STRFLT(matrix[3][i]))))
        else:
            for i in range(0, 4):
                output.write(self.encode("$##%s %s %s %s\n" % (STRFLT(matrix[i][0]),
                                                               STRFLT(matrix[i][1]),
                                                               STRFLT(matrix[i][2]),
                                                               STRFLT(matrix[i][3]))))
        output.write(self.encode("$#}\n"))

    @staticmethod
    def resetWriter():
        Writer.instances = {}
        ArrayData.instance = 0
        Object.instance = 0

    @staticmethod
    def serializeInstanceOrUseIt(obj, output):
        if obj in Writer.wrote_elements and \
           hasattr(obj, "uniqueID") and \
           obj.uniqueID is not None and \
           hasattr(obj, 'serializeReference'):
            return obj.serializeReference(output)

        Writer.wrote_elements[obj] = True
        return obj.serialize(output)


class Object(Writer):
    instance = 0

    def __init__(self, *args, **kwargs):
        Writer.__init__(self, *args)
        self.dataVariance = "UNKNOWN"
        self.name = kwargs.get('name', "None")
        self.uniqueID = None
        self.userdata = None

    def generateID(self):
        self.uniqueID = Object.instance
        Object.instance += 1

    def copyFrom(self, obj):
        self.name = obj.name
        self.dataVariance = obj.dataVariance

    def serializeReference(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        output.write(self.encode("$#UniqueID %d\n" % self.uniqueID))
        output.write(self.encode("$}\n"))

    def getOrCreateUserData(self):
        if self.userdata is None:
            self.userdata = DefaultUserDataContainer()
        return self.userdata

    def getNameSpaceClass(self):
        return "{}::{}".format(self.nameSpace(), self.className())

    def setName(self, name):
        self.name = name

    def className(self):
        return "Object"

    def nameSpace(self):
        return "osg"

    def serializeContent(self, output):
        if self.uniqueID is not None:
            output.write(self.encode("$#UniqueID {}\n".format(self.uniqueID)))

        if self.name is not "None":
            output.write(self.encode("$#Name \"{}\"\n".format(self.name)))

        if self.dataVariance is not "UNKNOWN":
            output.write(self.encode("$#DataVariance {}\n".format(self.dataVariance)))

        if self.userdata is not None:
            output.write(self.encode("$#UserDataContainer TRUE {\n"))
            self.userdata.indent_level = self.indent_level + 2
            self.userdata.write(output)
            output.write(self.encode("$#}\n"))


class StringValueObject(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self)
        self.generateID()
        self.key = args[0]
        self.value = args[1]

    def className(self):
        return "StringValueObject"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)

        output.write(self.encode("$#Name %s\n" % json.dumps(self.key)))
        output.write(self.encode("$#Value %s\n" % json.dumps(self.value)))

        output.write(self.encode("$}\n"))


class DefaultUserDataContainer(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.value = []

    def append(self, value):
        self.value.append(value)

    def className(self):
        return "DefaultUserDataContainer"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#UDC_UserObjects %d {\n" % len(self.value)))
        for s in self.value:
            s.indent_level = self.indent_level + 2
            s.write(output)
        output.write(self.encode("$#}\n"))


class UpdateMatrixTransform(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.stacked_transforms = []

    def className(self):
        return "UpdateMatrixTransform"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#StackedTransforms %d {\n" % len(self.stacked_transforms)))
        for s in self.stacked_transforms:
            s.indent_level = self.indent_level + 2
            s.write(output)
        output.write(self.encode("$#}\n"))


class UpdateMaterial(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)

    def className(self):
        return "UpdateMaterial"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        output.write(self.encode("$}\n"))


class StackedMatrixElement(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        if self.name == "None":
            self.name = "matrix"
        m = Matrix().to_4x4()
        m.identity()
        self.matrix = kwargs.get('matrix', m)

    def className(self):
        return "StackedMatrixElement"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#Matrix {\n"))
        self.writeMatrix(output, self.matrix)


class StackedTranslateElement(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.translate = Vector((0, 0, 0))
        self.name = "translate"

    def className(self):
        return "StackedTranslateElement"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#Translate %s %s %s\n" % (STRFLT(self.translate[0]),
                                                             STRFLT(self.translate[1]),
                                                             STRFLT(self.translate[2]))))


class StackedScaleElement(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.scale = Vector((1, 1, 1))
        self.name = "scale"

    def className(self):
        return "StackedScaleElement"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#Scale %s %s %s\n" % (STRFLT(self.scale[0]),
                                                         STRFLT(self.scale[1]),
                                                         STRFLT(self.scale[2]))))


class StackedRotateAxisElement(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.axis = kwargs.get('axis', Vector((1, 0, 0)))
        self.angle = kwargs.get('angle', 0)

    def className(self):
        return "StackedRotateAxisElement"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#Axis %s %s %s\n" % (STRFLT(self.axis[0]),
                                                        STRFLT(self.axis[1]),
                                                        STRFLT(self.axis[2]))))
        output.write(self.encode("$#Angle %s\n" % (STRFLT(self.angle))))


class StackedQuaternionElement(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        m = Matrix().to_4x4()
        m.identity()
        self.quaternion = m.to_quaternion()
        self.name = "quaternion"

    def className(self):
        return "StackedQuaternionElement"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#Quaternion %s %s %s %s\n" % (STRFLT(self.quaternion.x),
                                                                 STRFLT(self.quaternion.y),
                                                                 STRFLT(self.quaternion.z),
                                                                 STRFLT(self.quaternion.w))))


class UpdateMorph(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.targetNames = []
        self.nested_callback = None

    def nameSpace(self):
        return "osgAnimation"

    def className(self):
        return "UpdateMorph"

    def addNestedCallback(self, update_callback):
        callback = self
        while callback.nested_callback is not None:
            callback = callback.nested_callback
        callback.nested_callback = update_callback

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        if self.nested_callback:
            self.nested_callback.indent_level = self.indent_level + 2
            output.write(self.encode("$#NestedCallback TRUE {\n"))
            self.nested_callback.serialize(output)
            output.write(self.encode("$#}\n"))
        output.write(self.encode("$#TargetNames %s {\n" % len(self.targetNames)))
        for target in self.targetNames:
            output.write(self.encode("$##%s \n" % target))
        output.write(self.encode("$#}\n"))
        output.write(self.encode("$}\n"))


class UpdateBone(UpdateMatrixTransform):
    def __init__(self, *args, **kwargs):
        UpdateMatrixTransform.__init__(self, *args, **kwargs)

    def nameSpace(self):
        return "osgAnimation"

    def className(self):
        return "UpdateBone"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        UpdateMatrixTransform.serializeContent(self, output)
        output.write(self.encode("$}\n"))


class UpdateMorphGeometry(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()

    def setName(self, name):
        self.name = name

    def className(self):
        return "UpdateMorphGeometry"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        Object.serializeContent(self, output)
        output.write(self.encode("$}\n"))


class UpdateSkeleton(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()

    def className(self):
        return "UpdateSkeleton"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        Object.serializeContent(self, output)
        output.write(self.encode("$}\n"))


class Node(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.cullingActive = "TRUE"
        self.stateset = None
        self.update_callbacks = []

    def className(self):
        return "Node"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        if len(self.update_callbacks) > 0:
            output.write(self.encode("$#UpdateCallback TRUE {\n"))
            for i in self.update_callbacks:
                i.indent_level = self.indent_level + 2
                i.write(output)
            output.write(self.encode("$#}\n"))

        if self.stateset is not None:
            output.write(self.encode("$#StateSet TRUE {\n"))
            self.stateset.indent_level = self.indent_level + 2
            self.stateset.write(output)
            output.write(self.encode("$#}\n"))


class Geode(Node):
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.drawables = []
        self.update_callbacks = []

    def setName(self, name):
        self.name = self.className() + name

    def className(self):
        return "Geode"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        Object.serializeContent(self, output)
        Node.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#Drawables %d {\n" % (len(self.drawables))))

        for i in self.drawables:
            if i is not None:
                i.indent_level = self.indent_level + 2
                i.write(output)
        output.write(self.encode("$#}\n"))


class Group(Node):
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.children = []

    def className(self):
        return "Group"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        Object.serializeContent(self, output)
        Node.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        if len(self.children) > 0:
            output.write(self.encode("$#Children %d {\n" % (len(self.children))))
            for i in self.children:
                i.indent_level = self.indent_level + 2
                i.write(output)
            output.write(self.encode("$#}\n"))


class MatrixTransform(Group):
    def __init__(self, *args, **kwargs):
        Group.__init__(self, *args, **kwargs)
        self.matrix = Matrix().to_4x4()
        self.matrix.identity()

    def className(self):
        return "MatrixTransform"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        Object.serializeContent(self, output)
        Node.serializeContent(self, output)
        Group.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#Matrix {\n"))
        self.writeMatrix(output, self.matrix)


class StateAttribute(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.update_callbacks = []

    def className(self):
        return "StateAttribute"

    def serializeContent(self, output):
        Object.serializeContent(self, output)
        if len(self.update_callbacks) > 0:
            output.write(self.encode("$#UpdateCallback TRUE {\n"))
            for i in self.update_callbacks:
                i.indent_level = self.indent_level + 2
                i.write(output)
            output.write(self.encode("$#}\n"))


class StateTextureAttribute(StateAttribute):
    def __init__(self, *args, **kwargs):
        StateAttribute.__init__(self, *args, **kwargs)
        self.unit = 0

    def className(self):
        return "StateTextureAttribute"

    def serializeContent(self, output):
        StateAttribute.serializeContent(self, output)


class Light(StateAttribute):
    def __init__(self, *args, **kwargs):
        StateAttribute.__init__(self, *args, **kwargs)
        self.light_num = 0
        self.ambient = (0.0, 0.0, 0.0, 1.0)
        self.diffuse = (0.8, 0.8, 0.8, 1.0)
        self.specular = (1.0, 1.0, 1.0, 1.0)
        self.position = (0.0, 0.0, 1.0, 0.0)
        self.direction = (0.0, 0.0, -1.0)
        self.spot_exponent = 0.0
        self.spot_cutoff = 180.0
        self.constant_attenuation = 1.0
        self.linear_attenuation = 0.0
        self.quadratic_attenuation = 0.0

    def className(self):
        return "Light"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        StateAttribute.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#LightNum %s\n" % self.light_num))
        output.write(self.encode("$#Ambient %s %s %s %s\n" % (STRFLT(self.ambient[0]),
                                                              STRFLT(self.ambient[1]),
                                                              STRFLT(self.ambient[2]),
                                                              STRFLT(self.ambient[3]))))

        output.write(self.encode("$#Diffuse %s %s %s %s\n" % (STRFLT(self.diffuse[0]),
                                                              STRFLT(self.diffuse[1]),
                                                              STRFLT(self.diffuse[2]),
                                                              STRFLT(self.diffuse[3]))))

        output.write(self.encode("$#Specular %s %s %s %s\n" % (STRFLT(self.specular[0]),
                                                               STRFLT(self.specular[1]),
                                                               STRFLT(self.specular[2]),
                                                               STRFLT(self.specular[3]))))

        output.write(self.encode("$#Position %s %s %s %s\n" % (STRFLT(self.position[0]),
                                                               STRFLT(self.position[1]),
                                                               STRFLT(self.position[2]),
                                                               STRFLT(self.position[3]))))

        output.write(self.encode("$#Direction %s %s %s\n" % (STRFLT(self.direction[0]),
                                                             STRFLT(self.direction[1]),
                                                             STRFLT(self.direction[2]))))

        output.write(self.encode("$#ConstantAttenuation %s\n" % STRFLT(self.constant_attenuation)))
        output.write(self.encode("$#LinearAttenuation %s\n" % STRFLT(self.linear_attenuation)))
        output.write(self.encode("$#QuadraticAttenuation %s\n" % STRFLT(self.quadratic_attenuation)))

        output.write(self.encode("$#SpotExponent %s\n" % STRFLT(self.spot_exponent)))
        output.write(self.encode("$#SpotCutoff %s\n" % STRFLT(self.spot_cutoff)))


class LightSource(Group):
    def __init__(self, *args, **kwargs):
        Group.__init__(self, *args, **kwargs)
        self.light = Light()
        self.cullingActive = "FALSE"

    def className(self):
        return "LightSource"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        Object.serializeContent(self, output)
        Node.serializeContent(self, output)
        Group.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        if self.light is not None:
            output.write(self.encode("$#Light TRUE {\n"))
            self.light.indent_level = self.indent_level + 2
            self.light.write(output)
            output.write(self.encode("$#}\n"))


class Texture2D(StateTextureAttribute):
    def __init__(self, *args, **kwargs):
        StateTextureAttribute.__init__(self, *args, **kwargs)
        self.source_image = None
        self.file = "none"
        self.wrap_s = "REPEAT"
        self.wrap_t = "REPEAT"
        self.wrap_r = "REPEAT"
        self.min_filter = "LINEAR_MIPMAP_LINEAR"
        self.mag_filter = "LINEAR"
        self.internalFormatMode = "USE_IMAGE_DATA_FORMAT"

    def className(self):
        return "Texture2D"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        StateTextureAttribute.serializeContent(self, output)
        output.write(self.encode("$#WRAP_S %s\n" % self.wrap_s))
        output.write(self.encode("$#WRAP_T %s\n" % self.wrap_t))
        output.write(self.encode("$#WRAP_R %s\n" % self.wrap_r))
        output.write(self.encode("$#MIN_FILTER %s\n" % self.min_filter))
        output.write(self.encode("$#MAG_FILTER %s\n" % self.mag_filter))
        image = Image(filename=self.file)
        output.write(self.encode("$#Image TRUE {\n"))
        image.indent_level = self.indent_level + 1
        image.write(output)
        output.write(self.encode("$#}\n"))


class Image(Object):
    def __init__(self, *args, **kwargs):
        self.filename = kwargs.get("filename")
        Object.__init__(self, *args, **kwargs)
        self.generateID()

    def serialize(self, output):
        Object.serializeContent(self, output)
        output.write(self.encode("$#FileName \"%s\"\n" % self.filename))
        output.write(self.encode("$#WriteHint 0 2\n"))


class Material(StateAttribute):
    def __init__(self, *args, **kwargs):
        StateAttribute.__init__(self, *args, **kwargs)
        diffuse_energy = 0.8
        self.colormode = "OFF"
        self.emission = (0.0, 0.0, 0.0, 1.0)
        self.ambient = (0.0, 0.0, 0.0, 1.0)
        self.diffuse = (0.8 * diffuse_energy, 0.8 * diffuse_energy, 0.8 * diffuse_energy, 1.0)
        self.specular = (0.5, 0.5, 0.5, 1.0)
        self.shininess = 40 / (512 / 128)  # blender encode shininess to 512 and opengl to 128

    def className(self):
        return "Material"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        StateAttribute.serializeContent(self, output)
        output.write(self.encode("$#Ambient TRUE Front %s %s %s %s Back %s %s %s %s\n" % (STRFLT(self.ambient[0]),
                                                                                          STRFLT(self.ambient[1]),
                                                                                          STRFLT(self.ambient[2]),
                                                                                          STRFLT(self.ambient[3]),
                                                                                          STRFLT(self.ambient[0]),
                                                                                          STRFLT(self.ambient[1]),
                                                                                          STRFLT(self.ambient[2]),
                                                                                          STRFLT(self.ambient[3]))))

        output.write(self.encode("$#Diffuse TRUE Front %s %s %s %s Back %s %s %s %s\n" % (STRFLT(self.diffuse[0]),
                                                                                          STRFLT(self.diffuse[1]),
                                                                                          STRFLT(self.diffuse[2]),
                                                                                          STRFLT(self.diffuse[3]),
                                                                                          STRFLT(self.diffuse[0]),
                                                                                          STRFLT(self.diffuse[1]),
                                                                                          STRFLT(self.diffuse[2]),
                                                                                          STRFLT(self.diffuse[3]))))

        output.write(self.encode("$#Specular TRUE Front %s %s %s %s Back %s %s %s %s\n" % (STRFLT(self.specular[0]),
                                                                                           STRFLT(self.specular[1]),
                                                                                           STRFLT(self.specular[2]),
                                                                                           STRFLT(self.specular[3]),
                                                                                           STRFLT(self.specular[0]),
                                                                                           STRFLT(self.specular[1]),
                                                                                           STRFLT(self.specular[2]),
                                                                                           STRFLT(self.specular[3]))))

        output.write(self.encode("$#Emission TRUE Front %s %s %s %s Back %s %s %s %s\n" % (STRFLT(self.emission[0]),
                                                                                           STRFLT(self.emission[1]),
                                                                                           STRFLT(self.emission[2]),
                                                                                           STRFLT(self.emission[3]),
                                                                                           STRFLT(self.emission[0]),
                                                                                           STRFLT(self.emission[1]),
                                                                                           STRFLT(self.emission[2]),
                                                                                           STRFLT(self.emission[3]))))

        output.write(self.encode("$#Shininess TRUE Front %s Back %s\n" % (STRFLT(self.shininess),
                                                                          STRFLT(self.shininess))))


class LightModel(StateAttribute):
    def __init__(self, *args, **kwargs):
        StateAttribute.__init__(self, *args, **kwargs)
        self.local_viewer = "FALSE"
        self.color_control = "SEPARATE_SPECULAR_COLOR"
        self.ambient = (0.2, 0.2, 0.2, 1.0)

    def className(self):
        return "LightModel"

    def nameSpace(self):
        return "osg"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        StateAttribute.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#AmbientIntensity %s %s %s %s\n" % (STRFLT(self.ambient[0]),
                                                                       STRFLT(self.ambient[1]),
                                                                       STRFLT(self.ambient[2]),
                                                                       STRFLT(self.ambient[3]))))
        output.write(self.encode("$#ColorControl %s\n" % self.color_control))
        output.write(self.encode("$#LocalViewer %s\n" % self.local_viewer))


class StateSet(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.modes = {}
        self.attributes = []
        self.texture_attributes = {}

    def getMaxTextureUnitUsed(self):
        max_texture_unit = 0
        for i in self.texture_attributes.keys():
            if i > max_texture_unit:
                max_texture_unit = i
        return max_texture_unit

    def className(self):
        return "StateSet"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.getNameSpaceClass())))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        if len(self.modes) > 0:
            output.write(self.encode("$#ModeList %d {\n" % (len(self.modes))))
            for i in self.modes.items():
                if i is not None:
                    output.write(self.encode("$##%s %s\n" % i))
            output.write(self.encode("$#}\n"))

        if len(self.attributes) > 0:
            output.write(self.encode("$#AttributeList %d {\n" % (len(self.attributes))))
            for i in self.attributes:
                if i is not None:
                    i.indent_level = self.indent_level + 2
                    i.write(output)
                    output.write(self.encode("$##Value OFF\n"))
            output.write(self.encode("$#}\n"))

        if len(self.texture_attributes) > 0:
            max_texture_used = self.getMaxTextureUnitUsed()
            output.write(self.encode("$#TextureModeList %d {\n" % (1 + max_texture_used)))
            for i in range(0, max_texture_used + 1):
                if i in self.texture_attributes:
                    output.write(self.encode("$##Data 1 {\n"))
                    output.write(self.encode("$###GL_TEXTURE_2D ON\n"))
                    output.write(self.encode("$##}\n"))
                else:
                    output.write(self.encode("$##Data 0\n"))
            output.write(self.encode("$#}\n"))

            output.write(self.encode("$#TextureAttributeList %d {\n" % (1 + max_texture_used)))
            for i in range(0, max_texture_used + 1):
                if i in self.texture_attributes:
                    attributes = self.texture_attributes.get(i)
                    output.write(self.encode("$##Data %d {\n" % len(attributes)))
                    for a in attributes:
                        if a is not None:
                            a.indent_level = self.indent_level + 3
                            a.write(output)
                        output.write(self.encode("$###Value OFF\n"))
                    output.write(self.encode("$##}\n"))
                else:
                    output.write(self.encode("$##Data 0\n"))
            output.write(self.encode("$#}\n"))
            
        if "GL_BLEND" in self.modes and self.modes["GL_BLEND"] == "ON":
            output.write(self.encode("$#RenderingHint 2\n"))


class ArrayData(Object):
    instance = 0

    def __init__(self, *args, **kwargs):
        Object.__init__(self)
        self.array = kwargs.get('array')
        self.type = kwargs.get('type')
        self.uniqueID = ArrayData.instance
        ArrayData.instance += 1

    def serializeReference(self, output):
        output.write(self.encode("$Array TRUE ArrayID %d\n" % self.uniqueID))

    def serialize(self, output):
        output.write(self.encode("$Array TRUE ArrayID %s %s %d {\n" % (self.uniqueID, self.type, len(self.array))))
        dim = len(self.array[0])
        for i in self.array:
            if dim == 3:
                output.write(self.encode("$#%s %s %s\n" % (STRFLT(i[0]), STRFLT(i[1]), STRFLT(i[2]))))
            elif dim == 2:
                output.write(self.encode("$#%s %s\n" % (STRFLT(i[0]), STRFLT(i[1]))))
            elif dim == 4:
                output.write(self.encode("$#%s %s %s %s\n" % (STRFLT(i[0]), STRFLT(i[1]), STRFLT(i[2]), STRFLT(i[3]))))
        output.write(self.encode("$}\n"))


class VertexAttributeData(Writer):
    def __init__(self, *args, **kwargs):
        Writer.__init__(self)
        self.array = None
        if kwargs.get("array") is not None:
            self.array = ArrayData(array=kwargs.get('array', None),
                                   type=kwargs.get('type', None))

    def getArray(self):
        return self.array.array

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % (self.className())))
        if self.array is None:
            output.write(self.encode("$#Array FALSE\n"))
        else:
            self.array.indent_level = self.indent_level + 1
            self.array.write(output)
        output.write(self.encode("$#Indices FALSE\n"))
        output.write(self.encode("$#Binding BIND_PER_VERTEX\n"))
        output.write(self.encode("$#Normalize 0\n"))
        output.write(self.encode("$}\n"))


class VertexArray(VertexAttributeData):
    def __init__(self, *args, **kwargs):
        kwargs["array"] = kwargs.get("array", [])
        kwargs["type"] = "Vec3fArray"
        VertexAttributeData.__init__(self, *args, **kwargs)

    def className(self):
        return "VertexData"


class NormalArray(VertexArray):
    def __init__(self, *args, **kwargs):
        VertexArray.__init__(self, *args, **kwargs)

    def className(self):
        return "NormalData"


class ColorArray(VertexAttributeData):
    def __init__(self, *args, **kwargs):
        kwargs["type"] = "Vec3fArray"
        kwargs["array"] = kwargs.get("array", [])
        VertexAttributeData.__init__(self, *args, **kwargs)

    def className(self):
        return "ColorData"


class TexCoordArray(VertexAttributeData):
    def __init__(self, *args, **kwargs):
        kwargs["array"] = kwargs.get("array", [])
        kwargs["type"] = "Vec2fArray"
        VertexAttributeData.__init__(self, *args, **kwargs)
        self.index = 0

    def className(self):
        return "Data"


class DrawElements(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.indexes = []
        self.type = None

    def getSizeArray(self):
        # dont waste time here
        # return max drawElements
        # return "DrawElementsUInt"
        element = "DrawElementsUByte"
        for i in self.indexes:
            if i > 255 and element == "DrawElementsUByte":
                element = "DrawElementsUShort"
            elif i > 65535 and element == "DrawElementsUShort":
                element = "DrawElementsUInt"
                break
        return element

    def className(self):
        return "DrawElements"

    def serialize(self, output):
        element = self.getSizeArray()
        output.write(self.encode("$#%s %s %s {\n" % (element, self.type, str(len(self.indexes)))))
        n = 1
        if self.type == "GL_TRIANGLES":
            n = 3
        if self.type == "GL_QUADS":
            n = 4

        total = int(len(self.indexes) / n)
        for i in range(0, total):
            output.write(self.encode("$##"))
            for a in range(0, n):
                output.write(self.encode("%s " % self.indexes[i * n + a]))
            output.write(self.encode("\n"))
        output.write(self.encode("$#}\n"))


class Geometry(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.primitives = []
        self.vertexes = None
        self.normals = None
        self.colors = None
        self.uvs = OrderedDict()
        self.stateset = None
        self.update_callbacks = []

    def className(self):
        return "Geometry"

    def copyFrom(self, geometry):
        Object.copyFrom(self, geometry)
        self.primitives = geometry.primitives
        self.vertexes = geometry.vertexes
        self.normals = geometry.normals
        self.colors = geometry.colors
        self.uvs = geometry.uvs
        self.stateset = geometry.stateset

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        if len(self.update_callbacks) > 0:
            output.write(self.encode("$#UpdateCallback TRUE {\n"))
            for i in self.update_callbacks:
                i.indent_level = self.indent_level + 2
                i.write(output)
            output.write(self.encode("$#}\n"))

        if self.stateset is not None:
            output.write(self.encode("$#StateSet TRUE {\n"))
            self.stateset.indent_level = self.indent_level + 2
            self.stateset.write(output)
            output.write(self.encode("$#}\n"))

        if len(self.primitives):
            output.write(self.encode("$#PrimitiveSetList %d {\n" % (len(self.primitives))))
            for i in self.primitives:
                i.indent_level = self.indent_level + 2
                i.write(output)
            output.write(self.encode("$#}\n"))

        if self.vertexes:
            self.vertexes.indent_level = self.indent_level + 1
            self.vertexes.write(output)
        if self.normals:
            self.normals.indent_level = self.indent_level + 1
            self.normals.write(output)
        if self.colors:
            self.colors.indent_level = self.indent_level + 1
            self.colors.write(output)

        if len(self.uvs) > 0:
            output.write(self.encode("$#TexCoordData %d {\n" % (len(self.uvs))))
            for i in self.uvs.values():
                if i:
                    i.indent_level = self.indent_level + 2
                    i.write(output)
                else:
                    emptyTexCoord = TexCoordArray()
                    emptyTexCoord.indent_level = self.indent_level + 2
                    emptyTexCoord.write(output)
            output.write(self.encode("$#}\n"))


#  animation node ######################################
class Bone(MatrixTransform):
    def __init__(self, skeleton=None, bone=None, parent=None, **kwargs):
        MatrixTransform.__init__(self, **kwargs)
        self.dataVariance = "DYNAMIC"
        self.parent = parent
        self.skeleton = skeleton
        self.bone = bone
        # self.inverse_bind_matrix = Matrix().to_4x4().identity()
        self.bone_inv_bind_matrix_skeleton = Matrix().to_4x4()

    def buildBoneChildren(self, use_pose=False):
        if self.skeleton is None or self.bone is None:
            return

        bone_name = self.bone.name + '_' + self.skeleton.name
        self.setName(bone_name.replace(' ', '_'))
        update_callback = UpdateBone()
        update_callback.setName(self.name)
        self.update_callbacks.append(update_callback)

        if use_pose:
            bone_matrix = self.skeleton.pose.bones[self.bone.name].matrix.copy()
        else:
            bone_matrix = self.bone.matrix_local.copy()

        if self.parent:
            if use_pose:
                parent_matrix = self.skeleton.pose.bones[self.bone.name].parent.matrix.copy()
            else:
                parent_matrix = self.bone.parent.matrix_local.copy()
            # This matrix is not always invertible
            bone_matrix = parent_matrix.inverted_safe() * bone_matrix

        # add bind matrix in localspace callback
        update_callback.stacked_transforms.append(StackedMatrixElement(name="bindmatrix", matrix=bone_matrix))
        update_callback.stacked_transforms.append(StackedTranslateElement())
        update_callback.stacked_transforms.append(StackedQuaternionElement())
        update_callback.stacked_transforms.append(StackedScaleElement())

        self.bone_inv_bind_matrix_skeleton = self.bone.matrix_local.copy().inverted()
        if not self.bone.children:
            return

        for boneChild in self.bone.children:
            b = Bone(self.skeleton, boneChild, self)
            self.children.append(b)
            b.buildBoneChildren(use_pose)

    def getMatrixInArmatureSpace(self):
        return self.bone.matrix_local

    def collect(self, d):
        d[self.name] = self
        for boneChild in self.children:
            boneChild.collect(d)

    def className(self):
        return "Bone"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        Node.serializeContent(self, output)
        Group.serializeContent(self, output)
        MatrixTransform.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        matrix = self.bone_inv_bind_matrix_skeleton.copy()
        output.write(self.encode("$#InvBindMatrixInSkeletonSpace {\n"))
        self.writeMatrix(output, matrix)


class Skeleton(MatrixTransform):
    def __init__(self, name="", matrix=None):
        MatrixTransform.__init__(self)
        self.boneDict = {}
        self.matrix = matrix
        self.setName(name)
        self.update_callbacks = []
        self.update_callbacks.append(UpdateSkeleton())

    def collectBones(self):
        self.boneDict = {}
        for bone in self.children:
            bone.collect(self.boneDict)

    def getMatrixInArmatureSpace(self):
        return self.matrix

    def className(self):
        return "Skeleton"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        Node.serializeContent(self, output)
        Group.serializeContent(self, output)
        MatrixTransform.serializeContent(self, output)
        output.write(self.encode("$}\n"))


class MorphGeometry(Geometry):
    def __init__(self, *args, **kwargs):
        Geometry.__init__(self, *args, **kwargs)
        self.dataVariance = "DYNAMIC"
        self.morphTargets = []
        self.update_callbacks = []

    def className(self):
        return "MorphGeometry"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        Geometry.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        if self.morphTargets:
            output.write(self.encode("$#MorphTargets %s {\n" % len(self.morphTargets)))
            for target in self.morphTargets:
                factor = target.factor if hasattr(target, 'factor') else 0
                output.write(self.encode("$##MorphTarget %s \n" % factor))
                target.indent_level = self.indent_level + 2
                target.write(output)
            output.write(self.encode("$#}\n"))


class RigGeometry(Geometry):
    def __init__(self, *args, **kwargs):
        Geometry.__init__(self, *args, **kwargs)
        self.groups = {}
        self.dataVariance = "DYNAMIC"
        self.sourcegeometry = None

    def className(self):
        return "RigGeometry"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        Geometry.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#InfluenceMap %d {\n" % len(self.groups)))
        if len(self.groups) > 0:
            for name, grp in self.groups.items():
                grp.indent_level = self.indent_level + 2
                grp.write(output)
        output.write(self.encode("$#}\n"))

        if self.sourcegeometry is not None:
            output.write(self.encode("$#SourceGeometry TRUE {\n"))
            self.sourcegeometry.indent_level = self.indent_level + 2
            self.sourcegeometry.write(output)
            output.write(self.encode("$#}\n"))


class AnimationManagerBase(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.animations = []

    def className(self):
        return "AnimationManagerBase"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#Animations %d {\n" % len(self.animations)))
        for i in self.animations:
            i.indent_level = self.indent_level + 2
            i.write(output)
        output.write(self.encode("$#}\n"))


class BasicAnimationManager(AnimationManagerBase):
    def __init__(self, *args, **kwargs):
        AnimationManagerBase.__init__(self, *args, **kwargs)

    def className(self):
        return "BasicAnimationManager"

    def serialize(self, output):
        AnimationManagerBase.serialize(self, output)

    def serializeContent(self, output):
        AnimationManagerBase.serializeContent(self, output)


class VertexGroup(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.vertexes = []
        self.targetGroupName = "None"

    def className(self):
        return "VertexGroup"

    def serialize(self, output):
        self.setName(self.targetGroupName)
        output.write(self.encode("$VertexInfluence \"%s\" %d {\n" % (self.targetGroupName, len(self.vertexes))))
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        for i in self.vertexes:
            output.write(self.encode("$#%s %s\n" % (i[0], STRFLT(i[1]))))


class Animation(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.generateID()
        self.channels = []

    def className(self):
        return "Animation"

    def nameSpace(self):
        return "osgAnimation"

    def serialize(self, output):
        output.write(self.encode("$%s {\n" % self.getNameSpaceClass()))
        Object.serializeContent(self, output)
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#Channels %d {\n" % len(self.channels)))
        for i in self.channels:
            i.indent_level = self.indent_level + 2
            i.write(output)
        output.write(self.encode("$#}\n"))


class Channel(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self.keys = []
        self.target = "none"
        self.type = "Unknown"

    def generateID(self):
        return None

    def className(self):
        return "Channel"

    def serialize(self, output):
        output.write(self.encode("$Type %s {\n" % self.type))
        self.serializeContent(output)
        output.write(self.encode("$}\n"))

    def serializeContent(self, output):
        output.write(self.encode("$#Name %s\n" % self.name))
        output.write(self.encode("$#TargetName \"%s\" \n" % self.target))
        output.write(self.encode("$#KeyFrameContainer TRUE %d {\n" % (len(self.keys))))
        for i in self.keys:
            output.write(self.encode("$##"))
            for a in range(0, len(i)):
                output.write(self.encode(" %s" % (STRFLT(i[a]))))
            output.write(self.encode("\n"))
        output.write(self.encode("$#}\n"))
