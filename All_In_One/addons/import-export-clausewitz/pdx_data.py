import io
import struct
from . import (utils)

class PdxFile():
    """Class representing a Paradox Clausewitz Engine .mesh File."""
    def __init__(self, filename):
        self.filename = filename
        self.__file_reference__ = None
        self.rawData = []
        self.nodes = []

    def read(self):
        """Read and Parse the specified File."""
        self.__file_reference__ = io.open(self.filename, "rb")
        self.rawData = self.__file_reference__.read()

        self.__parse__()

    def __parse__(self):
        data = self.rawData.lstrip(b"@@b@")

        buffer = utils.BufferReader(data)

        while not buffer.IsEOF():
            char = buffer.NextChar()

            if char == "!":
                self.nodes.append(self.read_property(buffer))
            elif char == "[":
                self.nodes.append(self.read_object(buffer, 0, None))

        utils.Log.info("Parsed")

        self.__file_reference__.close()

    def read_property(self, buffer: utils.BufferReader):
        """Read a .mesh Property using the provided Buffer"""
        name = ""
        property_data = []

        lower_bound = buffer.GetCurrentOffset()

        name_length = buffer.NextInt8()

        for i in range(name_length):
            name += buffer.NextChar()

        utils.Log.info("Property: " + name)

        char = buffer.NextChar()

        if char == "i":
            data_count = buffer.NextUInt32()
            #utils.Log.info("Count: " + str(data_count))
            for i in range(data_count):
                temp = buffer.NextInt32()
                property_data.append(temp)
                #utils.Log.info("Integer: " + str(temp))

            if name == "pdxasset":
                utils.Log.info("PDXAsset: " + str(property_data))
        elif char == "f":
            data_count = buffer.NextUInt32()
            #utils.Log.info("Count: " + str(data_count))
            for i in range(data_count):
                temp = buffer.NextFloat32()
                property_data.append(temp)
                #utils.Log.info("Float: " + str(temp))
        elif char == "s":
            value = ""
            stringType = buffer.NextUInt32()
            dataCount = buffer.NextUInt32()

            value = utils.ReadNullByteString(buffer)
            #utils.Log.info("String: " + value)

            property_data = value

        upper_bound = buffer.GetCurrentOffset()

        if name == "pdxasset":
            result = PdxAsset()
            result.bounds = (lower_bound, upper_bound)

            if len(property_data) >= 2:
                result.version = (property_data[0], property_data[1])
        else:
            result = PdxProperty(name, (lower_bound, upper_bound))
            result.value = property_data

        return result

    def read_object(self, buffer: utils.BufferReader, depth, prev_obj):
        """Reads object Data"""
        char = buffer.NextChar()
        object_properties = []
        sub_objects = []

        if char == "[":
            depth_temp = 0

            while buffer.NextChar(True) == '[':
                buffer.NextChar()
                depth_temp += 1

            return self.read_object(buffer, depth_temp, prev_obj)
        else:
            object_name = char + utils.ReadNullByteString(buffer)
            utils.Log.info((" "*depth) + "Object Name: " + object_name)

            if object_name == "object":
                result = PdxWorld()
            elif object_name == "mesh":
                result = PdxMesh()
            elif object_name == "skeleton":
                result = PdxSkeleton()
            elif object_name == "locator":
                result = PdxLocators()
            elif object_name == "info":
                result = PdxAnimInfo()
            else:
                result = PdxObject(object_name, [], depth)

            while not buffer.IsEOF():
                char = buffer.NextChar(True)

                if char == "!":
                    buffer.NextChar()
                    object_properties.append(self.read_property(buffer))
                elif char == "[":
                    nextDepth = utils.PreviewObjectDepth(buffer)
                    if depth < nextDepth:
                        sub_objects.append(self.read_object(buffer, 0, result))
                    else:
                        break

            if object_name == "object":
                result = PdxWorld()

                for o in sub_objects:
                    if isinstance(o, PdxShape):
                        result.objects.append(o)
                    else:
                        utils.Log.info("ERROR ::: World contains invalid Sub-Object: " + str(type(o)))

                for p in object_properties:
                    utils.Log.info("ERROR ::: Invalid Property in World: \"" + p.name + "\"")
            elif object_name == "mesh":
                result = PdxMesh()

                for o in sub_objects:
                    if isinstance(o, PdxMaterial):
                        result.material = o
                    elif isinstance(o, PdxBounds):
                        result.meshBounds = o
                    elif isinstance(o, PdxSkin):
                        result.skin = o
                    else:
                        utils.Log.info("ERROR ::: Mesh contains invalid Sub-Object: " + str(type(o)))

                for p in object_properties:
                    if p.name == "p":
                        utils.Log.info("Positions: " + str(len(p.value)) + " representing " + str(len(p.value) / 3) + " Vertices")
                        result.verts = utils.TransposeCoordinateArray3D(p.value)
                    elif p.name == "n":
                        utils.Log.info("Normals: " + str(len(p.value)) + " representing " + str(len(p.value) / 3) + " Vertices")
                        result.normals = utils.TransposeCoordinateArray3D(p.value)
                    elif p.name == "ta":
                        utils.Log.info("Tangents: " + str(len(p.value)) + " representing " + str(len(p.value) / 4) + " Vertices")
                        result.tangents = p.value
                    elif p.name == "u0": # u1, u2, u3 still not implemented
                        utils.Log.info("UV's: " + str(len(p.value)) + " representing " + str(len(p.value) / 2) + " Vertices")
                        result.uv_coords = utils.TransposeCoordinateArray2D(p.value)
                    elif p.name == "tri":
                        utils.Log.info("Indices: " + str(len(p.value)) + " representing " + str(len(p.value) / 3) + " Triangles")
                        result.faces = utils.TransposeCoordinateArray3D(p.value)
                    else:
                        utils.Log.info("ERROR ::: Invalid Property in Mesh: \"" + p.name + "\"")
            elif object_name == "aabb":
                result = PdxBounds(None, None)

                for o in sub_objects:
                    utils.Log.info("ERROR ::: Bounds contains invalid Sub-Object: " + str(type(o)))

                for p in object_properties:
                    if(p.name == "min"):
                        result.min = p.value
                    elif(p.name == "max"):
                        result.max = p.value
                    else:
                        utils.Log.info("ERROR ::: Invalid Property in Bounds: \"" + p.name + "\"")
            elif object_name == "skin":
                result = PdxSkin()

                for o in sub_objects:
                    utils.Log.info("ERROR ::: Skin contains invalid Sub-Object: " + str(type(o)))

                for p in object_properties:
                    if p.name == "bones":
                        if len(p.value) == 1:
                            #utils.Log.info("Bones per Vertice: " + str(p.value[0]))
                            result.bonesPerVertice = p.value[0]
                        else:
                            utils.Log.info("ERROR ::: Bones per Vertice has more than 1 Value")
                    elif p.name == "ix":
                        #utils.Log.info("Indices: " + str(len(p.value)))
                        result.indices = p.value
                    elif p.name == "w":
                        #utils.Log.info("Weights: " + str(len(p.value)))
                        result.weight = p.value
                    else:
                        utils.Log.info("ERROR ::: Invalid Property in Skin: \"" + p.name + "\"")
            elif object_name == "material":
                result = PdxMaterial()

                for o in sub_objects:
                    utils.Log.info("ERROR ::: Material contains invalid Sub-Object: " + str(type(o)))

                for p in object_properties:
                    if p.name == "shader":
                        result.shader = p.value
                    elif p.name == "diff":
                        result.diff = p.value
                    elif p.name == "n":
                        result.normal = p.value
                    elif p.name == "spec":
                        result.spec = p.value
                    else:
                        utils.Log.info("ERROR ::: Invalid Property in Material: \"" + p.name + "\"")
            elif object_name == "skeleton":
                result = PdxSkeleton()

                for o in sub_objects:
                    if isinstance(o, PdxJoint):
                        result.joints.append(o)
                    else:
                        utils.Log.info("ERROR ::: Skeleton contains invalid Sub-Object: " + str(type(o)))

                for p in object_properties:
                    utils.Log.info("ERROR ::: Invalid Property in Skeleton: \"" + p.name + "\"")
            elif object_name == "locator":
                result = PdxLocators()

                for o in sub_objects:
                    if isinstance(o, PdxLocator):
                        result.locators.append(o)
                    else:
                        utils.Log.info("ERROR ::: Locators contains invalid Sub-Object: " + str(type(o)))

                for p in object_properties:
                    utils.Log.info("ERROR ::: Invalid Property in Locators: \"" + p.name + "\"")
            elif object_name == "info":
                result = PdxAnimInfo()

                for o in sub_objects:
                    if isinstance(o, PdxAnimJoint):
                        result.animJoints.append(o)
                    else:
                        utils.Log.info("ERROR ::: AnimInfo contains invalid Sub-Object: " + str(type(o)))

                for p in object_properties:
                    if p.name == "fps":
                        if len(p.value) == 1:
                            result.fps = p.value[0]
                        else:
                            utils.Log.info("ERROR ::: fps has more than 1 Value")
                    elif p.name == "sa":
                        if len(p.value) == 1:
                            result.samples = p.value[0]
                        else:
                            utils.Log.info("ERROR ::: samples has more than 1 Value")
                    elif p.name == "j":
                        if len(p.value) == 1:
                            result.jointCount = p.value[0]
                        else:
                            utils.Log.info("ERROR ::: joints has more than 1 Value")
                    else:
                        utils.Log.info("ERROR ::: Invalid Property in AnimInfo: \"" + p.name + "\"")
            elif object_name == "samples":
                result = PdxAnimSamples()

                for o in sub_objects:
                    utils.Log.info("ERROR ::: AnimSamples contains invalid Sub-Object: " + str(type(o)))

                for p in object_properties:
                    if p.name == "t":
                        result.t = p.value
                    elif p.name == "q":
                        result.q = p.value
                    elif p.name == "s":
                        result.s = p.value
                    else:
                        utils.Log.info("ERROR ::: Invalid Property in AnimSamples: \"" + p.name + "\"")
            else:
                if isinstance(prev_obj, PdxLocators):
                    result = PdxLocator(object_name, None)
                    for o in sub_objects:
                        utils.Log.info("ERROR ::: Locator \"" + object_name + "\" contains invalid Sub-Object: " + str(type(o)))

                    for p in object_properties:
                        if p.name == "p":
                            if len(p.value) == 3:
                                result.pos = p.value
                            else:
                                utils.Log.info("ERROR ::: Locator Position does not have 3 Values")
                        elif p.name == "q":
                            if len(p.value) == 4:
                                result.quaternion = p.value
                            else:
                                utils.Log.info("ERROR ::: Locator Quaternion does not have 4 Values")
                        elif p.name == "pa":
                            result.parent = p.value
                        else:
                            utils.Log.info("ERROR ::: Invalid Property in Locator: \"" + p.name + "\"")
                elif isinstance(prev_obj, PdxWorld):
                    result = PdxShape(object_name)

                    for o in sub_objects:
                        if isinstance(o, PdxSkeleton):
                            result.skeleton = o
                        elif isinstance(o, PdxMesh):
                            result.meshes.append(o)
                        else:
                            utils.Log.info("ERROR ::: Shape \"" + object_name + "\" contains invalid Sub-Object: " + str(type(o)))

                    for p in object_properties:
                        utils.Log.info("ERROR ::: Invalid Property in Shape: \"" + p.name + "\"")
                elif isinstance(prev_obj, PdxSkeleton):
                    result = PdxJoint(object_name)

                    for o in sub_objects:
                        utils.Log.info("ERROR ::: Joint \"" + object_name + "\" contains invalid Sub-Object: " + str(type(o)))

                    for p in object_properties:
                        if p.name == "ix":
                            if len(p.value) == 1:
                                #utils.Log.info("Joint Index: " + str(p.value[0]))
                                result.index = p.value[0]
                            else:
                                utils.Log.info("ERROR ::: Joint Index has more than 1 Value")
                        elif p.name == "pa":
                            if len(p.value) == 1:
                                #utils.Log.info("Parent Index: " + str(p.value[0]))
                                result.parent = p.value[0]
                            else:
                                utils.Log.info("ERROR ::: Parent Index has more than 1 Value")
                        elif p.name == "tx":
                            if len(p.value) == 12:
                                result.transform = p.value
                                print(p.value[9:12])
                            else:
                                utils.Log.info("ERROR ::: Joint Transform not 12 Values")
                        else:
                            utils.Log.info("ERROR ::: Invalid Property in Joint: \"" + p.name + "\"")
                elif isinstance(prev_obj, PdxAnimInfo):
                    result = PdxAnimJoint(object_name)

                    for o in sub_objects:
                        utils.Log.info("ERROR ::: AnimJoint \"" + object_name + "\" contains invalid Sub-Object: " + str(type(o)))

                    for p in object_properties:
                        if p.name == "sa":
                            result.sampleMode = p.value
                        elif p.name == "t":
                            if len(p.value) == 3:
                                result.translation = p.value
                            else:
                                utils.Log.info("ERROR ::: AnimJoint Translation has a length of " + str(len(p.value)))
                        elif p.name == "q":
                            if len(p.value) == 4:
                                result.quaternion = p.value
                            else:
                                utils.Log.info("ERROR ::: AnimJoint Quaternion has a length of " + str(len(p.value)))
                        elif p.name == "s":
                            if len(p.value) == 1:
                                result.size = p.value[0]
                            else:
                                utils.Log.info("ERROR ::: AnimJoint Size has a length of " + str(len(p.value)))
                        else:
                            utils.Log.info("ERROR ::: Invalid Property in AnimJoint: \"" + p.name + "\"")
                else:
                    result = PdxObject(object_name, object_properties, depth)

            return result

class PdxAsset():
    """Asset Object"""
    def __init__(self):
        self.bounds = (0, 0)
        self.name = "pdxasset"
        self.version = (0, 0) # Version x.y formated like (x, y)

    def get_binary_data(self):
        """Returns the Byte encoded Object Data"""
        result = bytearray()

        result.extend(struct.pack("<cb" + str(len(self.name)) + "s", b'!', len(self.name), self.name.encode('UTF-8')))
        result.extend(struct.pack("<cb", b'i', 2))
        result.extend(struct.pack(">iibbb", 1, 0, 0, 0, 0))

        return result

    def get_gfx_data(self):
        result = ""

        return result

class PdxWorld():
    def __init__(self):
        self.objects = []

    def get_binary_data(self):
        """Returns the Byte encoded Object Data"""
        result = bytearray()

        result.extend(struct.pack("<7sb", b'[object', 0))

        for o in self.objects:
            result.extend(o.get_binary_data())
        
        return result

    def get_gfx_data(self):
        result = ""

        for o in self.objects:
            result += o.get_gfx_data()

        return result

class PdxShape():
    def __init__(self, name):
        self.name = name
        self.meshes = []
        self.skeleton = None

    def get_binary_data(self):
        result = bytearray()

        result.extend(struct.pack("<2s", b'[['))
        result.extend(struct.pack("<" + str(len(self.name)) + "sb", self.name.encode('UTF-8'), 0))
        
        if self.meshes is not None:
            for mesh in self.meshes:
                result.extend(mesh.get_binary_data())
        else:
            utils.Log.info("ERROR ::: No Mesh found!")

        if not(self.skeleton is None):
            result.extend(self.skeleton.get_binary_data())

        return result


    def get_gfx_data(self):
        result = ""

        if self.meshes is not None:
            for i in range(len(self.meshes)):
                result += self.meshes[i].get_gfx_data(self.name, i)

        return result

class PdxSkeleton():
    def __init__(self):
        self.joints = []

    def get_binary_data(self):
        result = bytearray()

        result.extend(struct.pack("<11sb", b'[[[skeleton', 0))

        for joint in self.joints:
            result.extend(joint.get_binary_data())

        return result

    def get_gfx_data(self):
        result = ""

        return result

class PdxJoint():
    def __init__(self, name):
        self.name = name
        self.index = -1
        self.parent = -1
        self.transform = []

    def get_binary_data(self):
        result = bytearray()

        result.extend(struct.pack("<4s", b'[[[['))
        result.extend(struct.pack("<" + str(len(self.name)) + "sb", self.name.encode('UTF-8'), 0))

        result.extend(struct.pack("<cb3sII", b'!', 2, b'ixi', 1, self.index))

        if self.parent != -1:
            result.extend(struct.pack("<cb3sII", b'!', 2, b'pai', 1, self.parent))

        if len(self.transform) == 12:
            result.extend(struct.pack("<cb3sI", b'!', 2, b'txf', 12))
            for t in self.transform:
                result.extend(struct.pack("<f",t))

        return result

    def get_gfx_data(self):
        result = ""

        return result

class PdxMesh():
    def __init__(self):
        self.verts = []
        self.faces = []

        self.tangents = []
        self.normals = []
        self.uv_coords = []

        self.meshBounds = None
        self.material = None
        self.skin = None

    def get_binary_data(self):
        """Returns the Byte encoded Object Data"""
        result = bytearray()

        result.extend(struct.pack("<7sb", b'[[[mesh', 0))

        if len(self.verts) > 0:
            result.extend(struct.pack("<cb2sI", b'!', 1, b'pf', len(self.verts) * 3))

            for i in range(len(self.verts)):
                for j in range(3):
                    result.extend(struct.pack("<f", self.verts[i][j]))
        else:
            utils.Log.info("ERROR ::: No Vertices found!")

        if len(self.faces) > 0:
            result.extend(struct.pack("<cb4sI", b'!', 3, b'trii', len(self.faces) * 3))

            for i in range(len(self.faces)):
                for j in range(3):
                    result.extend(struct.pack("<I", self.faces[i][j]))
        else:
            utils.Log.info("ERROR ::: No Faces found!")

        if len(self.normals) > 0:
            result.extend(struct.pack("<cb2sI", b'!', 1, b'nf', len(self.normals) * 3))

            for i in range(len(self.normals)):
                for j in range(3):
                    result.extend(struct.pack("<f", self.normals[i][j]))
        else:
            utils.Log.info("WARNING ::: No Normals found! (Ok for Collision Material)")

        if len(self.tangents) > 0:
            result.extend(struct.pack("<cb3sI", b'!', 2, b'taf', len(self.tangents) * 4))

            for i in range(len(self.tangents)):
                for j in range(4):
                    result.extend(struct.pack("<f", self.tangents[i][j]))
        else:
            utils.Log.info("WARNING ::: No Tangents found! (Ok for Collision Material)")

        if len(self.uv_coords) > 0:
            result.extend(struct.pack("<cb3sI", b'!', 2, b'u0f', len(self.uv_coords) * 2))

            for i in range(len(self.uv_coords)):
                for j in range(2):
                    result.extend(struct.pack("<f", self.uv_coords[i][j]))
        else:
            utils.Log.info("WARNING ::: No UV0 found! (Ok for Collision Material)")

        if self.meshBounds is not None:
            result.extend(self.meshBounds.get_binary_data())
        else:
            utils.Log.info("ERROR ::: No Mesh Bounds found!")

        if self.material is not None:
            result.extend(self.material.get_binary_data())
        else:
            utils.Log.info("ERROR ::: No Material found!")

        if self.skin is not None:
            result.extend(self.skin.get_binary_data())
        else:
            utils.Log.info("WARNING ::: No Skin found!")

        return result

    def get_gfx_data(self, name, index):
        result = "\n"

        result += "        meshsettings = {\n"

        result += "            name = \"" + name + "\"\n"
        result += "            index = " + str(index) + "\n"

        result += self.material.get_gfx_data()

        result += "        }\n"

        return result

class PdxMaterial():
    def __init__(self):
        #Initialized to Collision for ease of use in exporter
        self.shader = "Collision"
        self.diff = ""
        self.normal = ""
        self.spec = ""

    #Is implemented incomplete (Only 1 Texture)
    def get_binary_data(self):
        """Returns the Byte encoded Object Data"""
        result = bytearray()

        result.extend(struct.pack("<12sb", b'[[[[material', 0))

        result.extend(struct.pack("<cb7s", b'!', 6, b'shaders'))
        result.extend(struct.pack("<II", 1, len(self.shader) + 1))
        result.extend(struct.pack("<" + str(len(self.shader)) + "sb", self.shader.encode("UTF-8"), 0))

        if self.shader != "Collision":

            result.extend(struct.pack("<cb5s", b'!', 4, b'diffs'))
            result.extend(struct.pack("<II", 1, len(self.diff) + 1))
            result.extend(struct.pack("<" + str(len(self.diff)) + "sb", self.diff.encode("UTF-8"), 0))

            result.extend(struct.pack("<cb2s", b'!', 1, b'ns'))
            result.extend(struct.pack("<II", 1, len(self.normal) + 1))
            result.extend(struct.pack("<" + str(len(self.normal)) + "sb", self.normal.encode("UTF-8"), 0))

            result.extend(struct.pack("<cb5s", b'!', 4, b'specs'))
            result.extend(struct.pack("<II", 1, len(self.spec) + 1))
            result.extend(struct.pack("<" + str(len(self.spec)) + "sb", self.spec.encode("UTF-8"), 0))

        return result

    def get_gfx_data(self):
        result = ""

        result += "            texture_diffuse = \"" + self.diff + "\"\n"
        result += "            texture_normal = \"" + self.normal + "\"\n"
        result += "            texture_specular = \"" + self.spec + "\"\n"
        result += "            shader = \"" + self.shader + "\"\n"

        return result

class PdxBounds():
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def get_binary_data(self):
        """Returns the Byte encoded Object Data"""
        result = bytearray()

        result.extend(struct.pack("<8sb", b'[[[[aabb', 0))

        result.extend(struct.pack("<cb4s", b'!', 3, b'minf'))
        result.extend(struct.pack("<Ifff", 3, self.min[0], self.min[1], self.min[2]))
        result.extend(struct.pack("<cb4s", b'!', 3, b'maxf'))
        result.extend(struct.pack("<Ifff", 3, self.max[0], self.max[1], self.max[2]))

        return result

    def get_gfx_data(self):
        result = ""

        return result

class PdxSkin():
    def __init__(self):
        self.bonesPerVertice = 0
        self.indices = []
        self.weight = []

    def get_binary_data(self):
        result = bytearray()

        result.extend(struct.pack("<8sb", b'[[[[skin', 0))

        result.extend(struct.pack("<cb6sII", b'!', 5, b'bonesi', 1, self.bonesPerVertice))
        result.extend(struct.pack("<cb3s", b'!', 2, b'ixf'))
        for i in range(len(self.indices)):
            result.extend(struct.pack("<I", self.indices[i]))
        result.extend(struct.pack("<cb2s", b'!', 1, b'wf'))
        for i in range(len(self.weight)):
            result.extend(struct.pack("<f", self.weight[i]))

        return result

    def get_gfx_data(self):
        result = ""

        return result

class PdxLocators():
    def __init__(self):
        self.bounds = (0, 0)
        self.locators = []

    def get_binary_data(self):
        """Returns the Byte encoded Object Data"""
        result = bytearray()

        result.extend(struct.pack("<8sb", b'[locator', 0))

        for locator in self.locators:
            result.extend(locator.get_binary_data())

        return result

    def get_gfx_data(self):
        result = ""

        return result

class PdxLocator():
    def __init__(self, name, pos):
        self.bounds = (0, 0)
        self.name = name
        self.pos = pos
        self.quaternion = (0, 0, 0, 0)
        self.parent = ""

    def get_binary_data(self):
        """Returns the Byte encoded Object Data"""
        result = bytearray()

        result.extend(struct.pack("<2s", b'[['))
        result.extend(struct.pack("<" + str(len(self.name)) + "sb", self.name.encode('UTF-8'), 0))

        result.extend(struct.pack("<cb2sifff", b'!', 1, b'pf', 3, self.pos[0], self.pos[1], self.pos[2]))
        result.extend(struct.pack("<cb2siffff", b'!', 1, b'qf', 4, self.quaternion[0], self.quaternion[1], self.quaternion[2], self.quaternion[3]))
        if self.parent != "":
            result.extend(struct.pack("<cb5s", b'!', 2, b'pas'))
            result.extend(struct.pack("<II", 1, len(self.parent) + 1))
            result.extend(struct.pack("<" + str(len(self.parent)) + "sb", self.parent.encode("UTF-8"), 0))

        return result

    def get_gfx_data(self):
        result = ""

        return result

# Pdx Anim File
class PdxAnimInfo():
    def __init__(self):
        self.fps = 0.0
        self.samples = 0
        self.jointCount = 0

        self.animJoints = []

    def get_binary_data(self):
        result = bytearray()

        result.extend(struct.pack("<5sb", b'[info', 0))

        result.extend(struct.pack("<cb4sif", b'!', 3, b'fpsf', 1, self.fps))
        result.extend(struct.pack("<cb3siI", b'!', 2, b'sai', 1, self.samples))
        result.extend(struct.pack("<cb2siI", b'!', 1, b'ji', 1, self.jointCount))

        for animJoint in self.animJoints:
            result.extend(animJoint.get_binary_data())

        return result

    def get_gfx_data(self):
        result = ""

        return result

class PdxAnimJoint():
    def __init__(self, name):
        self.name = name
        self.sampleMode = ""
        self.translation = []
        self.quaternion = []
        self.size = 1

    def get_binary_data(self):
        result = bytearray()

        result.extend(struct.pack("<2s", b'[['))
        result.extend(struct.pack("<" + str(len(self.name)) + "sb", self.name.encode('UTF-8'), 0))

        result.extend(struct.pack("<cb3s", b'!', 2, b'sas'))
        result.extend(struct.pack("<II", 1, len(self.sampleMode) + 1))
        result.extend(struct.pack("<" + str(len(self.sampleMode)) + "sb", self.sampleMode.encode("UTF-8"), 0))

        if len(self.translation) == 3:
            result.extend(struct.pack("<cb2sI", b'!', 1, b'tf', 3))

            for t in self.translation:
                result.extend(struct.pack("<f", t))
        else:
            utils.Log.info("ERROR ::: AnimJoint Translation has invalid size")

        if len(self.quaternion) == 4:
            result.extend(struct.pack("<cb2sI", b'!', 1, b'qf', 4))

            for q in self.quaternion:
                result.extend(struct.pack("<f", q))
        else:
            utils.Log.info("ERROR ::: AnimJoint Quaternion has invalid size")

        result.extend(struct.pack("<cb2sII", b'!', 1, b'si', 1, self.size))

        return result

    def get_gfx_data(self):
        result = ""

        return result

class PdxAnimSamples:
    def __init__(self):
        self.t = []
        self.q = []
        self.s = []

    def get_binary_data(self):
        result = bytearray()

        result.extend(struct.pack("<5sb", b'[samples', 0))

        if len(self.t) % 3 == 0:
            result.extend(struct.pack("<cb2sI", b'!', 1, b'tf', len(self.t)))

            for t in self.t:
                result.extend(struct.pack("<f", t))
        else:
            utils.Log.info("ERROR ::: T-Samples are not multiples of 3")

        if len(self.q) % 4 == 0:
            result.extend(struct.pack("<cb2sI", b'!', 1, b'tf', len(self.q)))

            for q in self.q:
                result.extend(struct.pack("<f", q))
        else:
            utils.Log.info("ERROR ::: Q-Samples are not multiples of 4")

        if len(self.s) % 1 == 0:
            result.extend(struct.pack("<cb2sI", b'!', 1, b'tf', len(self.s)))

            for s in self.s:
                result.extend(struct.pack("<f", s))
        else:
            utils.Log.info("ERROR ::: S-Samples are not multiples of 1")

        return result

    def get_gfx_data(self):
        result = ""

        return result

# Temporary objects
class PdxObject():
    """Temporary class to hold the Values of a parsed Object until it gets mapped to the object"""
    def __init__(self, name, properties, depth):
        self.name = name
        self.properties = properties
        self.depth = depth

    def get_binary_data(self):
        return bytearray()

    def get_gfx_data(self):
        result = ""

        return result

class PdxProperty():
    """Temporary class to hold the Values of a parsed Property until it gets mapped to the object"""
    def __init__(self, name, bounds):
        self.name = name
        self.bounds = bounds
        self.value = []

    def get_binary_data(self):
        return bytearray()

    def get_gfx_data(self):
        result = ""

        return result
