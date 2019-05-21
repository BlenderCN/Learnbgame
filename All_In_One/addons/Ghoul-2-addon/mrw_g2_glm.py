# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from . import mrw_g2_stringhelpers, mrw_g2_filesystem, mrw_g2_constants, mrw_g2_gla, mrw_g2_materialmanager, mrw_profiler
import struct, bpy

def buildBoneIndexLookupMap(gla_filepath_abs):
    print("Loading gla file for bone name -> bone index lookup")
    #open file
    try:
        file = open(gla_filepath_abs, mode="rb")
    except IOError:
        print("Could not open ", gla_filepath_abs, sep="")
        return False, "Could not open gla file for bone index lookup!"
    #read header
    header = mrw_g2_gla.MdxaHeader()
    success, message = header.loadFromFile(file)
    if not success:
        return False, message
    #read offsets
    boneOffsets = mrw_g2_gla.MdxaBoneOffsets()
    boneOffsets.loadFromFile(file, header.numBones) #cannot fail (except with exception)
    #read skeleton
    skeleton = mrw_g2_gla.MdxaSkel()
    skeleton.loadFromFile(file, boneOffsets)
    #build lookup map
    boneIndices = {}
    for bone in skeleton.bones:
        boneIndices[bone.name] = bone.index
    return boneIndices, "all right"

def getName(object):
    if object.g2_prop_name != "":
        return object.g2_prop_name
    return object.name

class GetBoneWeightException(Exception):
    pass

def getBoneWeights(vertex, meshObject, armatureObject, maxBones = -1):
    # find the armature modifier
    modifier = None
    for mod in meshObject.modifiers:
        if mod.type == 'ARMATURE':
            if modifier != None:
                raise GetBoneWeightException("Multiple armature modifiers on {}!".format(meshObject.name))
            modifier = mod
    if modifier == None:
        raise GetBoneWeightException("{} has no armature modifier!".format(meshObject.name))
    
    # this will eventually contain the weights per bone (by name) if not 0
    weights = {}
    
    # vertex groups take priority
    if modifier.use_vertex_groups:
        for group in vertex.groups:
            weight = group.weight
            index = group.group
            name = meshObject.vertex_groups[index].name
            if weight > 0 and name in armatureObject.data.bones:
                weights[name] = weight
    
    # if there are vertex group weights, envelopes are ignored
    if len(weights) == 0 and modifier.use_bone_envelopes:
        co_meshspace = vertex.co
        co_worldspace = meshObject.matrix_world * co_meshspace
        co_armaspace = armatureObject.matrix_world.inverted() * co_worldspace
        for bone in armatureObject.data.bones:
            weight = bone.evaluate_envelope(co_armaspace)
            if weight > 0:
                weights[bone.name] = weight
        
    # remove smallest weight while there are more than allowed
    if maxBones != -1:
        while len(weights) > maxBones:
            iter = weights.items().__iter__()
            minKey, minVal = next(iter)
            try:
                key, val = next(iter)
                if val < minVal:
                    minKey = key
                    minVal = val
            except StopIteration:
                pass
            del weights[minKey]
    
    # the combined weight must be normalized to 1
    sum = 0
    for weight in weights.values():
        sum += weight
    
    for key in weights.keys():
        weights[key] /= sum
    
    return weights

# returns whether two 2D vector are pretty much equal, taking floating point inaccuracies in account
EPSILON = 0.001
def vectorsAlmostEqual(v1, v2):
    return (abs(v1.x - v2.x) < EPSILON) and (abs(v1.y - v2.y) < EPSILON)

class MdxmHeader:
    
    def __init__(self):
        self.name = ""
        self.animName = ""
        self.numBones = -1
        self.numLODs = -1
        self.ofsLODs = -1
        self.numSurfaces = -1
        self.ofsSurfHierarchy = -1
        self.ofsEnd = -1
    
    def loadFromFile(self, file):
        #ident check
        ident, = struct.unpack("4s", file.read(4))
        if ident != mrw_g2_constants.GLM_IDENT:
            print("File does not start with ", mrw_g2_constants.GLM_IDENT, " but ", ident, " - no GLM!")
            return False, "Is no GLM file!"
        #version check
        version, = struct.unpack("i", file.read(4))
        if version != mrw_g2_constants.GLM_VERSION:
            return False, "Wrong glm file version! ("+str(version)+" should be "+str(mrw_g2_constants.GLM_VERSION)+")"
        # read data
        self.name, self.animName = struct.unpack("64s64s", file.read(mrw_g2_constants.MAX_QPATH*2))
        #4x is 4 ignored bytes - the animIndex which is only used ingame
        self.numBones, self.numLODs, self.ofsLODs, self.numSurfaces, self.ofsSurfHierarchy, self.ofsEnd = struct.unpack("4x6i", file.read(4*7))
        return True, ""
    
    def saveToFile(self, file):
        # 0 is animIndex, only used ingame
        file.write(struct.pack("4si64s64s7i", mrw_g2_constants.GLM_IDENT, mrw_g2_constants.GLM_VERSION, self.name, self.animName, 0, self.numBones, self.numLODs, self.ofsLODs, self.numSurfaces, self.ofsSurfHierarchy, self.ofsEnd))
        return True, ""
    
    def print(self):
        print("== GLM Header ==\nname: {self.name}\nanimName: {self.animName}\nnumBones: {self.numBones}\nnumLODs: {self.numLODs}\nnumSurfaces: {self.numSurfaces}".format(self=self))
    
    @staticmethod
    def getSize():
        # 2 ints, 2 string, 7 ints
        return 2*4 + 2*64 + 7*4

# offsets of the surface data
class MdxmSurfaceDataOffsets:
    def __init__(self):
        self.baseOffset = MdxmHeader.getSize() #always directly after the header
        self.offsets = []
    
    def loadFromFile(self, file, numSurfaces):
        assert(self.baseOffset == file.tell())
        for i in range(numSurfaces):
            self.offsets.append(struct.unpack("i", file.read(4))[0])
    
    def saveToFile(self, file):
        for offset in self.offsets:
            file.write(struct.pack("i", offset))
    
    def calculateOffsets(self, surfaceDataCollection):
        offset = 4 * len(surfaceDataCollection.surfaces)
        for surfaceData in surfaceDataCollection.surfaces:
            self.offsets.append(offset)
            offset += surfaceData.getSize()
    
    # returns the size of this in bytes (when written to file)
    def getSize():
        return 4 * len(self.offsets)

# originally called mdxmSurfaceHierarchy_t, I think that name is misleading (but mine's not too good, either)
class MdxmSurfaceData:
    def __init__(self):
        self.name = ""
        self.flags = -1
        self.shader = ""
        self.parentIndex = -1
        self.numChildren = -1
        self.children = []
        self.index = -1 #filled by MdxmSurfaceHierarchy.loadFromFile, not saved
    
    def loadFromFile(self, file):
        self.name, self.flags, self.shader = struct.unpack("64sI64s", file.read(64+4+64))
        # ignoring shaderIndex which is only used ingame
        self.parentIndex, self.numChildren = struct.unpack("4x2i", file.read(3*4))
        for i in range(self.numChildren):
            self.children.append(struct.unpack("i", file.read(4))[0])
    
    def loadFromBlender(self, object, surfaceIndexMap):
        self.name = getName(object).encode()
        self.shader = object.g2_prop_shader.encode()
        # set flags
        self.flags = 0
        if object.g2_prop_off:
            self.flags |= mrw_g2_constants.SURFACEFLAG_OFF
        if object.g2_prop_tag:
            self.flags |= mrw_g2_constants.SURFACEFLAG_TAG
        # set parent
        if object.parent != None and getName(object.parent)in surfaceIndexMap:
            self.parentIndex = surfaceIndexMap[getName(object.parent)]
        # set children
        self.numChildren = 0
        from . import mrw_g2_panels
        for child in object.children:
            if child.type == 'MESH': # working around non-mesh garbage in the hierarchy would be too much trouble, everything below that is ignored
                if not mrw_g2_panels.hasG2MeshProperties(child):
                    return False, "{} has no Ghoul 2 properties set!".format(child.name)
                childName = getName(child)
                if childName not in surfaceIndexMap:
                    surfaceIndexMap[childName] = len(surfaceIndexMap)
                self.children.append(surfaceIndexMap[childName])
                self.numChildren += 1
        return True, ""
    
    def saveToFile(self, file):
        # 0 is the shader index, only used ingame
        file.write(struct.pack("64sI64s3i", self.name, self.flags, self.shader, 0, self.parentIndex, self.numChildren))
        for i in range(self.numChildren):
            file.write(struct.pack("i", self.children[i]))
    
    def getSize(self):
        # string, int, string, 4 ints
        return 64 + 4 + 64 + 3*4 + 4*self.numChildren

# all the surface hierarchy/shader/name/flag/... information entries (MdxmSurfaceInfo)
class MdxmSurfaceDataCollection:
    def __init__(self):
        self.surfaces = []
    
    def loadFromFile(self, file, surfaceInfoOffsets):
        for i, offset in enumerate(surfaceInfoOffsets.offsets):
            file.seek(surfaceInfoOffsets.baseOffset + offset)
            surfaceInfo = MdxmSurfaceData()
            surfaceInfo.loadFromFile(file)
            surfaceInfo.index = i
            self.surfaces.append(surfaceInfo)
    
    def loadFromBlender(self, rootObject, surfaceIndexMap):
        from . import mrw_g2_panels
        def addChildren(object):
            for child in object.children:
                # only meshes supported in hierarchy, I couldn't always use the parent otherwise
                if child.type != 'MESH':
                    print("Warning: {} is no mesh, neither it nor its children will be exported!".format(child.name))
                elif not mrw_g2_panels.hasG2MeshProperties(child):
                    return False, "{} has no Ghoul 2 properties set! (Also, the exporter should've detected this earlier.)".format(child.name)
                else:
                    # assign the child an index, if it doesn't have one already
                    if getName(child) not in surfaceIndexMap:
                        surfaceIndexMap[getName(child)] = len(surfaceIndexMap)
                    index = surfaceIndexMap[getName(child)]
                    # extend the surface list to include the index, if necessary
                    if index >= len(self.surfaces):
                        self.surfaces.extend([None] * (index + 1 - len(self.surfaces)))
                    # create the surface
                    surface = MdxmSurfaceData()
                    surface.index = index
                    
                    success, message = surface.loadFromBlender(child, surfaceIndexMap)
                    if not success:
                        return False, message
                    
                    self.surfaces[index] = surface
                    
                    success, message = addChildren(child)
                    if not success:
                        return False, message
            return True, ""
        success, message = addChildren(rootObject)
        if not success:
            return False, message
        for index, surface in enumerate(self.surfaces):
            if surface == None: # a surface that was referenced did not get created
                return False, "Internal error during hierarchy creation!({}/{})".format(index, len(self.surfaces))
        return True, ""
    
    def saveToFile(self, file):
        for surfaceInfo in self.surfaces:
            surfaceInfo.saveToFile(file)
    
    def getSize(self):
        size = 0
        for surface in self.surfaces:
            size += surface.getSize()
        return size

class MdxmVertex:
    def __init__(self):
        self.co = []
        self.normal = []
        self.uv = []
        self.numWeights = 1
        self.weights = []
        self.boneIndices = []
    
    # doesn't load UV since that comes later
    def loadFromFile(self, file):
        self.normal.extend(struct.unpack("3f", file.read(3*4)))
        self.co.extend(struct.unpack("3f", file.read(3*4)))
        #this is a packed structure that contains all kinds of things...
        packedStuff, = struct.unpack("I", file.read(4))
        #this is not the complete weights, parts of it are in the packed stuff
        weights = []
        weights.extend(struct.unpack("4B", file.read(4)))
        #packedStuff bits 31 & 30: weight count
        self.numWeights = (packedStuff>>30)+1
        #packedStuff bits 29 & 28: nothing
        #packedStuff bits 20f, 22f, 24f, 26f: weight overflow
        totalWeight = 0
        for i in range(self.numWeights):
            # add overflow bits to the weight (MSBs!)
            weights[i] = weights[i] | (((packedStuff>>(20+2*i)) & 0b11)<<8)
            # convert to float (0..1023 -> 0.0..1.0)
            weights[i] = weights[i] / 1023
            if i+1 < self.numWeights:
                totalWeight += weights[i]
                self.weights.append(weights[i])
            else: # i+1 == self.numWeights:
                self.weights.append(1 - totalWeight)
        #packedStuff 0-19: bone indices, 5 bit each
        for i in range(self.numWeights):
            self.boneIndices.append((packedStuff >> (5*i)) & 0b11111)
    
    #index: this surface's index
    #does not save UV (comes later)
    def saveToFile(self, file):
        assert(len(self.weights) == self.numWeights)
        #  pack the stuff that needs packing
        #num weights
        packedStuff = (self.numWeights - 1) << 30
        weights = [0, 0, 0, 0]
        for index, weight in enumerate(self.weights):
            #convert weight to 10 bit integer
            weight = round(weight * 1023)
            #lower 8 bits
            weights[index] = weight & 0xff
            #higher 2 bits
            hiWeight = (weight & 0x300) >> 8
            packedStuff |= hiWeight << (20 + 2*index)
            #bone index - 5 bits
            boneIndex = (self.boneIndices[index]) & 0b11111
            packedStuff |= boneIndex << (5*index)
        assert(packedStuff < 1<<32)
        file.write(struct.pack("6fI4B", self.normal[0], self.normal[1], self.normal[2], self.co[0], self.co[1], self.co[2], packedStuff, weights[0], weights[1], weights[2], weights[3]))
    
    #vertex :: Blender MeshVertex
    #uv :: [int, int] (blender style, will be y-flipped)
    #boneIndices :: { string -> int } (bone name -> index, may be changed)
    def loadFromBlender(self, vertex, uv, boneIndices, meshObject, armatureObject):
        # I'm taking the world matrix in case the object is not at the origin, but I really want the coordinates in scene_root-space, so I'm using that, too.
        rootMat = bpy.data.objects["scene_root"].matrix_world.inverted()
        co = rootMat * meshObject.matrix_world * vertex.co
        normal = rootMat.to_quaternion() * meshObject.matrix_world.to_quaternion() * vertex.normal
        for i in range(3):
            self.co.append(co[i])
            self.normal.append(normal[i])
        
        self.uv = [uv[0], 1-uv[1]] #flip Y
        
        #weight/bone indices
        
        assert(len(self.weights) == 0)
        global g_defaultSkeleton
        if g_defaultSkeleton:
            self.weights.append(1.0)
            self.boneIndices.append(0)
            self.numWeights = 1
        else:
            weights = None
            try:
                weights = getBoneWeights(vertex, meshObject, armatureObject, 4)
            except GetBoneWeightException as e:
                return False, "Could not retrieve vertex bone weights: {}".format(str(e))
            self.numWeights = len(weights)
            if self.numWeights == 0:
                return False, "Unweighted vertex found!"
            for boneName, weight in weights.items():
                self.weights.append(weight)
                boneIndex = -1
                if boneName in boneIndices:
                    self.boneIndices.append(boneIndices[boneName])
                else:
                    index = len(boneIndices)
                    boneIndices[boneName] = index
                    self.boneIndices.append(index)
                    if len(boneIndices) > 32:
                        return False, "More than 32 bones!"
                
        
        assert(len(self.weights) == self.numWeights)
        
        return True, ""

class MdxmTriangle:
    def __init__(self, indices = None):
        self.indices = indices
        if self.indices == None:
            self.indices = [] #order gets reversed during load/save
    
    def loadFromFile(self, file):
        self.indices.extend(struct.unpack("3i", file.read(3*4)))
        #flip CW/CCW
        temp = self.indices[0]
        self.indices[0] = self.indices[2]
        self.indices[2] = temp
        #make sure last index is not 0, eeekadoodle or something...
        if self.indices[2] == 0:
            temp = self.indices[0]
            self.indices[0] = self.indices[2]
            self.indices[2] = self.indices[1]
            self.indices[1] = temp
    
    def saveToFile(self, file):
        # triangles are flipped because otherwise they'd face the wrong way.
        file.write(struct.pack("3i", self.indices[2], self.indices[1], self.indices[0]))

class MdxmSurface:
    def __init__(self):
        self.index = -1
        self.numVerts = -1
        self.ofsVerts = -1
        self.numTriangles = -1
        self.ofsTriangles = -1
        self.numBoneReferences = -1
        self.ofsBoneReferences = -1
        self.ofsEnd = -1 # = size
        self.vertices = []
        self.triangles = []
        self.boneReferences = [] #integers: bone indices. maximum of 32, thus can be stored in 5 bit in vertices, saves space.
    
    def loadFromFile(self, file):
        startPos = file.tell()
        #  load surface header
        #in the beginning I ignore the ident, which is usually 0 and shouldn't matter
        self.index, ofsHeader, self.numVerts, self.ofsVerts, self.numTriangles, self.ofsTriangles, self.numBoneReferences, self.ofsBoneReferences, self.ofsEnd = struct.unpack("4x9i", file.read(10*4))
        assert(ofsHeader == -startPos)
        
        #  load vertices
        file.seek(startPos + self.ofsVerts)
        for i in range(self.numVerts):
            vert = MdxmVertex()
            vert.loadFromFile(file)
            self.vertices.append(vert)
        
        #uv textures come later
        for vert in self.vertices:
            vert.uv.extend(struct.unpack("2f", file.read(2*4)))
        
        #  load triangles
        file.seek(startPos + self.ofsTriangles)
        for i in range(self.numTriangles):
            t = MdxmTriangle()
            t.loadFromFile(file)
            self.triangles.append(t)
        
        #  load bone references
        file.seek(startPos + self.ofsBoneReferences)
        assert(len(self.boneReferences) == 0)
        self.boneReferences.extend(struct.unpack(str(self.numBoneReferences)+"i", file.read(4*self.numBoneReferences)))
        
        print("surface {self.index}: numBoneReferences: {self.numBoneReferences}".format(self=self))
        for i, boneRef in enumerate(self.boneReferences):
            print("bone ref {}: {}".format(i, boneRef))
        
        if file.tell() != startPos + self.ofsEnd:
            print("Warning: Surface structure unordered (bone references not last) or read error")
            file.seek(startPos + self.ofsEnd)
    
    def loadFromBlender(self, object, boneIndexMap, armatureObject):
        if object.type != 'MESH':
            return False, "Object is not of type Mesh!"
        mesh = object.data
        
        self.numVerts = len(mesh.vertices)
        self.numTriangles = len(mesh.faces)
        
        if self.numVerts > 1000:
            print("Warning: {} has over 1000 vertices ({})".format(object.name, self.numVerts))
        
        # create UV lookup map
        UVs = [None] * self.numVerts
        first = True
        for uv_tex in mesh.uv_textures:
            if uv_tex.active and first: #there shouldn't be multiple active uv textures, but safety first!
                first = False
                for face, uvdata in zip(mesh.faces, uv_tex.data):
                    if len(face.vertices) != 3:
                        return False, "Non-triangle face found!"
                    for vertexIndex, uv in zip(face.vertices, [uvdata.uv1, uvdata.uv2, uvdata.uv3]):
                        if UVs[vertexIndex]: #already had UV coordinates for this face?
                            if not vectorsAlmostEqual(uv, UVs[vertexIndex]): # better be the same then
                                return False, "UV seam found! Split meshes at UV seams."
                        else:
                            UVs[vertexIndex] = uv
        if first:
            return False, "No UV coordinates found!"
        
        if UVs.count(None) > 0:
            return False, "Vertex without UV coordinates found!"
        
        # bone name -> index, filled by vertices
        boneIndices = {}
        for sourceVertex, uv in zip(mesh.vertices, UVs):
            vertex = MdxmVertex()
            success, message = vertex.loadFromBlender(sourceVertex, uv, boneIndices, object, armatureObject)
            if not success:
                return False, "Could not load a vertex: {}".format(message)
            self.vertices.append(vertex)
        
        self.triangles = [MdxmTriangle([face.vertices[0], face.vertices[1], face.vertices[2]]) for face in mesh.faces]
        
        assert(len(self.vertices) == self.numVerts)
        assert(len(self.triangles) == self.numTriangles)
        
        # fill bone references
        global g_defaultSkeleton
        if g_defaultSkeleton:
            self.boneReferences = [0]
        else:
            self.boneReferences = [None] * len(boneIndices)
            for boneName, index in boneIndices.items():
                self.boneReferences[index] = boneIndexMap[boneName]
        
        self._calculateOffsets()
        return True, ""
    
    # if a surface does not exist on a lower LOD, an empty one gets created
    def makeEmpty(self):
        self.numVerts = 0
        self.numTriangles = 0
        self.numBoneReferences = 0
        self._calculateOffsets()
    
    def saveToFile(self, file):
        startPos = file.tell()
        #  write header (= this)
        #0 = ident
        file.write(struct.pack("10i", 0, self.index, -startPos, self.numVerts, self.ofsVerts, self.numTriangles, self.ofsTriangles, self.numBoneReferences, self.ofsBoneReferences, self.ofsEnd))
        
        # I don't know if triangles *have* to come first, but when I export they do, hence the assertions.
        
        #  write triangles
        assert(file.tell() == startPos + self.ofsTriangles)
        for tri in self.triangles:
            tri.saveToFile(file)
        
        #  write vertices
        assert(file.tell() == startPos + self.ofsVerts)
        # write packed part
        for vert in self.vertices:
            vert.saveToFile(file)
        # write UVs
        for vert in self.vertices:
            file.write(struct.pack("2f", vert.uv[0], vert.uv[1]))
        
        #  write bone indices
        assert(file.tell() == startPos + self.ofsBoneReferences)
        for ref in self.boneReferences:
            file.write(struct.pack("i", ref))
        
        assert(file.tell() == startPos + self.ofsEnd)
    
    # returns the created object
    def saveToBlender(self, data, lodLevel):
        #  retrieve metadata (same across LODs)
        surfaceData = data.surfaceDataCollection.surfaces[self.index]
        # blender won't let us create multiple things with the same name, so we add a LOD-suffix
        name =  mrw_g2_stringhelpers.decode(surfaceData.name)
        blenderName = name + "_" + str(lodLevel)
        
        #  create mesh
        mesh = bpy.data.meshes.new(blenderName)
        
        #create vertices
        mesh.vertices.add(self.numVerts)
        for vert, bvert in zip(self.vertices, mesh.vertices):
            bvert.co = vert.co
            bvert.normal = vert.normal
        
        #create faces
        mesh.faces.add(self.numTriangles)
        for i, face in enumerate(mesh.faces):
            tri = self.triangles[i]
            face.vertices = tri.indices
        
        #create uv coordinates
        material = data.materialManager.getMaterial(name, surfaceData.shader)
        image = None
        if material and material.active_texture:
            #assert(material.active_texture) # loading may fail...
            assert(material.active_texture.type == 'IMAGE')
            image = material.active_texture.image
        
        mesh.uv_textures.new()
        for i, uv_face in enumerate(mesh.uv_textures.active.data):
            tri = self.triangles[i]
            uv_face.uv1 = self.vertices[tri.indices[0]].uv
            uv_face.uv1[1] = 1 - uv_face.uv1[1] #flip y
            uv_face.uv2 = self.vertices[tri.indices[1]].uv
            uv_face.uv2[1] = 1 - uv_face.uv2[1]
            uv_face.uv3 = self.vertices[tri.indices[2]].uv
            uv_face.uv3[1] = 1 - uv_face.uv3[1]
            uv_face.image = image
        
        mesh.validate()
        mesh.update()
        
        #  create object
        obj = bpy.data.objects.new(blenderName, mesh)
        
        # in the case of the default skeleton, no weighting is needed.
        if not data.gla.isDefault:
            
            #  create armature modifier
            armatureModifier = obj.modifiers.new("skin", 'ARMATURE')
            armatureModifier.object = data.gla.skeleton_object
            armatureModifier.use_bone_envelopes = False #only use vertex groups by default
            
            #  create vertex groups (indices will match)
            for index in self.boneReferences:
                if index not in data.boneNames:
                    raise Exception("Bone Index {} not in LookupTable!".format(index))
                obj.vertex_groups.new(data.boneNames[index])
            
            #set weights
            for vertIndex, vert in enumerate(self.vertices):
                for weightIndex in range(vert.numWeights):
                    obj.vertex_groups[vert.boneIndices[weightIndex]].add([vertIndex], vert.weights[weightIndex], 'ADD')
        
        #link object to scene
        bpy.context.scene.objects.link(obj)
        
        #make object active - needed for this smoothing operator and possibly for material adding later
        bpy.context.scene.objects.active = obj
        #smooth
        #todo smooth does not work
        bpy.ops.object.shade_smooth()
        #set material
        if material:
            bpy.ops.object.material_slot_add()
            obj.material_slots[0].material = material
            
        #set ghoul2 specific properties
        obj.g2_prop_name = name
        obj.g2_prop_shader = surfaceData.shader.decode()
        obj.g2_prop_tag = surfaceData.flags & mrw_g2_constants.SURFACEFLAG_TAG
        obj.g2_prop_off = surfaceData.flags & mrw_g2_constants.SURFACEFLAG_OFF
        
        # return object so hierarchy etc. can be set
        return obj
    
    # fill offset and number variables
    def _calculateOffsets(self):
        offset = 10*4 # header: 4 ints
        #triangles
        self.ofsTriangles = offset
        self.numTriangles = len(self.triangles)
        offset += 3*4*self.numTriangles #3 ints
        #vertices
        self.ofsVerts = offset
        self.numVerts = len(self.vertices)
        offset += 10*4*self.numVerts # 6 floats co/normal, 8 bytes packed, 2 floats UV
        #bone references
        self.ofsBoneReferences = offset
        self.numBoneReferences = len(self.boneReferences)
        offset += 4*self.numBoneReferences # 1 int each
        #that's all the content, so we've got total size now.
        self.ofsEnd = offset

class MdxmLOD:
    def __init__(self):
        self.surfaceOffsets = []
        self.level = -1
        self.surfaces = []
        self.ofsEnd = -1 # = size
    
    def loadFromFile(self, file, header):
        startPos = file.tell()
        self.ofsEnd, = struct.unpack("i", file.read(4))
        for i in range(header.numSurfaces):
            # surface offsets - they're relative to a structure after the one containing ofsEnd, so I need to add sizeof(int) to them later.
            self.surfaceOffsets.append(struct.unpack("i", file.read(4))[0])
        for surfaceIndex, offset in enumerate(self.surfaceOffsets):
            if file.tell() != startPos + 4 + offset:
                print("Warning: Surface not completely read or unordered")
                file.seek(startPos + offset + 4)
            surface = MdxmSurface()
            surface.loadFromFile(file)
            assert(surface.index == surfaceIndex)
            self.surfaces.append(surface)
        assert(file.tell() == startPos + self.ofsEnd)
    
    def saveToFile(self, file):
        startPos = file.tell()
        # write ofsEnd
        file.write(struct.pack("i", self.ofsEnd))
        # write surface offsets
        for offset in self.surfaceOffsets:
            file.write(struct.pack("i", offset))
        # write surfaces
        for surface in self.surfaces:
            surface.saveToFile(file)
        # that's it, should've reached end.
        assert(file.tell() == startPos + self.ofsEnd)
    
    def loadFromBlender(self, model_root, surfaceIndexMap, boneIndexMap, armatureObject):
        # self.level gets set by caller
        
        # create dictionary of available objects
        from . import mrw_g2_panels
        def addChildren(dict, object):
            for child in object.children:
                if child.type == 'MESH' and mrw_g2_panels.hasG2MeshProperties(child):
                    dict[getName(child)] = child
                addChildren(dict, child)
        available = {}
        addChildren(available, model_root)
        
        self.surfaces = [None] * len(surfaceIndexMap)
        # for each required surface:
        for name, index in surfaceIndexMap.items():
            # create surface
            surf = MdxmSurface()
            # set correct index
            surf.index = index
            # if it is available:
            if name in available:
                # load from blender
                success, message = surf.loadFromBlender(available[name], boneIndexMap, armatureObject)
                if not success:
                    return False, "Could not load surface {} (LOD {}) from Blender: {}".format(name, self.level, message)
            # not available?
            else:
                # create empty one
                surf.makeEmpty()
            # add surface to list
            self.surfaces[index] = surf
        return True, ""
    
    def saveToBlender(self, data, root):
        # 1st pass: create objects
        objects = []
        for surface in self.surfaces:
            obj = surface.saveToBlender(data, self.level)
            objects.append(obj)
        # 2nd pass: set parent relations
        for i, obj in enumerate(objects):
            parentIndex = data.surfaceDataCollection.surfaces[i].parentIndex
            parent = root
            if parentIndex != -1:
                parent = objects[parentIndex]
            obj.parent = parent
    
    #fills self.surfaceOffsets and self.ofsEnd based on self.surfaces (must be initialized)
    def calculateOffsets(self, myOffset):
        self.surfaceOffsets = []
        # ofsEnd is in front of offsets, but they are relative to their start
        offset = 4 * len(self.surfaces)
        for surface in self.surfaces:
            self.surfaceOffsets.append(offset)
            surface.ofsHeader = - offset - myOffset
            offset += surface.ofsEnd # = size
        # memory required for ofsEnd
        self.ofsEnd = offset + 4
    
    def getSize(self):
        # ofsEnd + surface offsets
        size = 4 + 4 * len(self.surfaces)
        for surface in self.surfaces:
            size += surface.ofsEnd
        return size

class MdxmLODCollection:
    def __init__(self):
        self.LODs = []
    
    def loadFromFile(self, file, header):
        for i in range(header.numLODs):
            startPos = file.tell()
            curLOD = MdxmLOD()
            curLOD.loadFromFile(file, header)
            curLOD.level = i
            if file.tell() != startPos + curLOD.ofsEnd:
                print("Warning: Internal reading error or LODs not tightly packed!")
                file.seek(startPos + curLOD.ofsEnd)
            self.LODs.append(curLOD)
    
    def loadFromBlender(self, rootObjects, surfaceIndexMap, boneIndexMap, armatureObject):
        for lodLevel, model_root in enumerate(rootObjects):
            LOD = MdxmLOD()
            LOD.level = lodLevel
            success, message = LOD.loadFromBlender(model_root, surfaceIndexMap, boneIndexMap, armatureObject)
            if not success:
                return False, message
            self.LODs.append(LOD)
        return True, ""
    
    def calculateOffsets(self, ofsLODs):
        offset = ofsLODs
        for lod in self.LODs:
            lod.calculateOffsets(offset)
            offset += lod.getSize()
    
    def saveToFile(self, file):
        for LOD in self.LODs:
            LOD.saveToFile(file)
    
    def saveToBlender(self, data):
        for i, LOD in enumerate(self.LODs):
            root = bpy.data.objects.new("model_root_" + str(i), None)
            root.parent = data.scene_root
            bpy.context.scene.objects.link(root)
            LOD.saveToBlender(data, root)
    
    def getSize(self):
        size = 0
        for LOD in self.LODs:
            size += LOD.ofsEnd
        return size

class GLM:
    def __init__(self):
        self.header = MdxmHeader()
        self.surfaceDataOffsets = MdxmSurfaceDataOffsets()
        self.surfaceDataCollection = MdxmSurfaceDataCollection()
        self.LODCollection = MdxmLODCollection()
    
    def loadFromFile(self, filepath_abs):
        print("Loading {}...".format(filepath_abs))
        profiler = mrw_profiler.SimpleProfiler(True)
        # open file
        try:
            file = open(filepath_abs, mode = "rb")
        except IOError:
            print("Could not open file: ", filepath_abs, sep="")
            return False, "Could not open file"
        profiler.start("reading header")
        success, message = self.header.loadFromFile(file)
        if not success:
            return False, message
        profiler.stop("reading header")
        
        # self.header.print()
        
        # load surface hierarchy offsets
        profiler.start("reading surface hierarchy")
        self.surfaceDataOffsets.loadFromFile(file, self.header.numSurfaces)
        
        # load surfaces' information - seeks positon using surfaceDataOffsets
        self.surfaceDataCollection.loadFromFile(file, self.surfaceDataOffsets)
        profiler.stop("reading surface hierarchy")
        
        # load LODs
        profiler.start("reading surfaces")
        file.seek(self.header.ofsLODs)
        self.LODCollection.loadFromFile(file, self.header)
        profiler.stop("reading surfaces")
        
        #should be at the end now, if the structures are in the expected order.
        if file.tell() != self.header.ofsEnd:
            print("Warning: File not completely read or LODs not last structure in file. The former would be a problem, the latter wouldn't.")
        return True, ""
    
    def loadFromBlender(self, glm_filepath_rel, gla_filepath_rel, basepath):
        self.header.name = glm_filepath_rel.replace("\\", "/").encode()
        self.header.animName = gla_filepath_rel.encode()
        # create BoneName->BoneIndex lookup table based on GLA file (keeping in mind it might be "*default"/"")
        global g_defaultSkeleton
        g_defaultSkeleton = (gla_filepath_rel == "" or gla_filepath_rel == "*default")
        skeleton_object = None
        skeleton_armature = None
        boneIndexMap = None
        if g_defaultSkeleton:
            self.header.numBones = 1
            self.header.animName = b"*default"
        else:
            # retrieve skeleton
            if not "skeleton_root" in bpy.data.objects:
                return False, "No skeleton_root found!"
            skeleton_object = bpy.data.objects["skeleton_root"]
            if skeleton_object.type != 'ARMATURE':
                return False, "skeleton_root is no Armature!"
            skeleton_armature = skeleton_object.data
            
            
            boneIndexMap, message = buildBoneIndexLookupMap(mrw_g2_filesystem.RemoveExtension(mrw_g2_filesystem.AbsPath(gla_filepath_rel, basepath)) + ".gla")
            if boneIndexMap == False:
                return False, message
            
            self.header.numBones = len(boneIndexMap)
            
            # check if skeleton matches the specified one
            for bone in skeleton_armature.bones:
                if bone.name not in boneIndexMap:
                    return False, "skeleton_root does not match specified gla"
            
        #   load from Blender
        
        # find all available LODs
        self.header.numLODs = 0
        rootObjects = []
        while "model_root_{}".format(self.header.numLODs) in bpy.data.objects:
            rootObjects.append(bpy.data.objects["model_root_{}".format(self.header.numLODs)])
            self.header.numLODs += 1
        print("Found {} model_roots, i.e. LOD levels".format(self.header.numLODs))
        
        if self.header.numLODs == 0:
            return False, "Could not find model_root_0"
        
        # build hierarchy from first LOD
        surfaceIndexMap = {} # surface name -> index
        success, message = self.surfaceDataCollection.loadFromBlender(rootObjects[0], surfaceIndexMap)
        if not success:
            return False, message
        self.surfaceDataOffsets.calculateOffsets(self.surfaceDataCollection)
        
        self.header.numSurfaces = len(self.surfaceDataCollection.surfaces)
        print("{} surfaces found".format(self.header.numSurfaces))
        
        # load all LODs
        success, message = self.LODCollection.loadFromBlender(rootObjects, surfaceIndexMap, boneIndexMap, skeleton_object)
        if not success:
            return False, message
        
        self.LODCollection.calculateOffsets(self.header.ofsLODs)
        
        #   calculate offsets etc.4
        self._calculateHeaderOffsets()
        return True, ""
    
    def saveToFile(self, filepath_abs):
        if mrw_g2_filesystem.FileExists(filepath_abs):
            print("Warning: File exists! Overwriting.")
        #open file
        try:
            file = open(filepath_abs, "wb")
        except IOError:
            print("Failed to open file for writing: ", filepath_abs, sep="")
            return False, "Could not open file!"
        #save header
        self.header.saveToFile(file)
        #save surface data offsets
        self.surfaceDataOffsets.saveToFile(file)
        #save surface ("hierarchy") data
        self.surfaceDataCollection.saveToFile(file)
        #save LODs to file
        self.LODCollection.saveToFile(file)
        return True, ""
    
    #calculates the offsets & counts saved in the header based on the rest
    def _calculateHeaderOffsets(self):
        # offset of "after header"
        baseOffset = MdxmHeader.getSize()
        # offset of "after hierarchy offset list"
        self.header.numSurfaces = len(self.surfaceDataOffsets.offsets)
        baseOffset += 4 * self.header.numSurfaces
        # first "hierarchy" entry comes here
        self.header.ofsSurfHierarchy = baseOffset
        baseOffset += self.surfaceDataCollection.getSize()
        # first LOD comes here
        self.header.ofsLODs = baseOffset
        baseOffset += self.LODCollection.getSize()
        # that's everything, we've reached the end.
        self.header.ofsEnd = baseOffset
    
    # basepath: ../GameData/.../
    # gla: mrw_g2_gla.GLA object - the Skeleton (for weighting purposes)
    # scene_root: "scene_root" object in Blender
    def saveToBlender(self, basepath, gla, scene_root, skin_rel, guessTextures):
        if gla.header.numBones != self.header.numBones:
            return False, "Bone number mismatch - gla has {} bones, model uses {}. Maybe you're trying to load a jk2 model with the jk3 skeleton or vice-versa?".format(gla.header.numBones, self.header.numBones)
        print("creating model...")
        profiler = mrw_profiler.SimpleProfiler(True)
        profiler.start("creating surfaces")
        class GeneralData:
            pass
        data = GeneralData()
        data.gla = gla
        data.scene_root = scene_root
        data.surfaceDataCollection = self.surfaceDataCollection
        data.materialManager = mrw_g2_materialmanager.MaterialManager()
        data.boneNames = {}
        for bone in gla.skeleton.bones:
            data.boneNames[bone.index] = bone.name
        success, message = data.materialManager.init(basepath, skin_rel, guessTextures)
        if not success:
            return False, message
        
        self.LODCollection.saveToBlender(data)
        profiler.stop("creating surfaces")
        return True, ""
    
    def getRequestedGLA(self):
        #todo
        return mrw_g2_stringhelpers.decode(self.header.animName)