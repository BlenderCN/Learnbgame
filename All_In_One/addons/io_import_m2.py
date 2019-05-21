bl_info = {
    "name": "Blizzard .M2 importer",
    "author": "Philip Abbet",
    "blender": (2, 69, 0),
    "location": "File > Import",
    "description": "Import M2 models",
    "warning": "",
    "category": "Import-Export"
}

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector
import bmesh
from struct import unpack, calcsize
import os


######################################## CONSTANTS #######################################

OFF_M2_MAGIC                      = 0x000
OFF_M2_VERSION                    = 0x004
OFF_M2_NAME_LENGTH                = 0x008
OFF_M2_NAME_ADDR                  = 0x00C
OFF_M2_GLOBAL_MODEL_FLAGS         = 0x010
OFF_M2_BONES_COUNT                = 0x02C
OFF_M2_BONES_ADDR                 = 0x030
OFF_M2_KEY_BONE_LOOKUP_TABLE_SIZE = 0x034
OFF_M2_KEY_BONE_LOOKUP_TABLE_ADDR = 0x038
OFF_M2_VERTICES_COUNT             = 0x03C
OFF_M2_VERTICES_ADDR              = 0x040
OFF_M2_VIEWS_COUNT                = 0x044
OFF_M2_BONE_LOOKUP_TABLE_SIZE     = 0x078
OFF_M2_BONE_LOOKUP_TABLE_ADDR     = 0x07C


OFF_SKIN_MAGIC           = 0x00
OFF_SKIN_INDICES_COUNT   = 0x04
OFF_SKIN_INDICES_ADDR    = 0x08
OFF_SKIN_TRIANGLES_COUNT = 0x0C
OFF_SKIN_TRIANGLES_ADDR  = 0x10
OFF_SKIN_SUBMESHES_COUNT = 0x1C
OFF_SKIN_SUBMESHES_ADDR  = 0x20


CHARACTER_MESH_PART_IDS = {
    0: 'Hair',
    1: 'Facial1_',
    2: 'Facial2_',
    3: 'Facial3_',
    4: 'Braces',
    5: 'Boots',
    7: 'Ears',
    8: 'Wristbands',
    9: 'Kneepads',
    11: 'Pants',
    12: 'Tabard',
    13: 'Trousers',
    15: 'Cape',
    17: 'Eyeglows',
    18: 'Belt',
}


BONE_NAMES = [
    "ArmL",
    "ArmR",
    "ShoulderL",
    "ShoulderR",
    "SpineLow",
    "Waist",
    "Head",
    "Jaw",
    "IndexFingerR",
    "MiddleFingerR",
    "PinkyFingerR",
    "RingFingerR",
    "ThumbR",
    "IndexFingerL",
    "MiddleFingerL",
    "PinkyFingerL",
    "RingFingerL",
    "ThumbL",
    "BTH",
    "CSR",
    "CSL",
    "_Breath",
    "_Name",
    "_NameMount",
    "CHD",
    "CCH",
    "Root",
    "Wheel1",
    "Wheel2",
    "Wheel3",
    "Wheel4",
    "Wheel5",
    "Wheel6",
    "Wheel7",
    "Wheel8",
]


####################################### FILE READING #####################################

class Vertex:
    # 0x00  float   Position[3]         A vector to the position of the vertex.
    # 0x0C  uint8   BoneWeight[4]       The vertex weight for 4 bones.
    # 0x10  uint8   BoneIndices[4]      Which are referenced here.
    # 0x14  float   Normal[3]           A normal vector.
    # 0x20  float   TextureCoords[2]    Coordinates for a texture.
    # 0x28  float   Unknown[2]          Null?

    FORMAT = "<fffBBBBBBBBfffffff"

    def __init__(self, data):
        data = unpack(Vertex.FORMAT, data)
        self.position       = Vector( (data[0], data[1], data[2]) )
        self.bone_weights   = [ data[3], data[4], data[5], data[6] ]
        self.bone_indices   = [ data[7], data[8], data[9], data[10] ]
        self.normal         = Vector( (data[11], data[12], data[13]) )
        self.texture_coords = Vector( (data[14], data[15]) )


class Triangle:
    # 3 * uint16

    FORMAT = "<HHH"

    def __init__(self, data):
        data = unpack(Triangle.FORMAT, data)
        self.v1 = data[0]
        self.v2 = data[1]
        self.v3 = data[2]

    def to_tuple(self, offset=0):
        return (self.v1 - offset, self.v2 - offset, self.v3 - offset)


class Submesh:
    # 0x00  uint32  ID                  Mesh part ID, see below.
    # 0x04  uint16  StartIndex          Starting index number.
    # 0x06  uint16  nIndices            Number of indices.
    # 0x08  uint16  StartTriangle       Starting triangle index (that's 3* the number of triangles drawn so far).
    # 0x0A  uint16  nTriangles          Number of triangle indices.
    # 0x0C  uint16  nBones              Number of elements in the bone lookup table.
    # 0x0E  uint16  StartBones          Starting index in the bone lookup table.
    # 0x10  uint16  Unknown
    # 0x12  uint16  RootBone            Not sure.
    # 0x14  Vec3F   CenterMass          Average position of all the vertices in the submesh.
    # 0x20  Vec3F   CenterBoundingBox   The center of the box when an axis aligned box is built around the vertices in the submesh.
    # 0x2C  float   Radius              Distance of the vertex farthest from CenterBoundingBox.

    FORMAT = "<IHHHHHHHHfffffff"

    def __init__(self, data):
        data = unpack(Submesh.FORMAT, data)

        if data[0] == 0:
            self.name = 'Body'
        else:
            mesh_part_id_cat = data[0] // 100
            if mesh_part_id_cat in CHARACTER_MESH_PART_IDS:
                self.name = '%s%02d' % (CHARACTER_MESH_PART_IDS[mesh_part_id_cat], data[0] - mesh_part_id_cat * 100)
            else:
                self.name = 'Submesh%d' % data[0]

        self.indices_start = data[1]
        self.indices_count = data[2]
        self.triangles_start = data[3] // 3
        self.triangles_count = data[4] // 3
        self.bones_count = data[5]
        self.bones_start = data[6]


class Bone:
    # 0x00  int32   KeyBoneID       Back-reference to the key bone lookup table. -1 if this is no key bone.
    # 0x04  uint32  Flags           Only known flags: 8 - billborded and 512 - transformed
    # 0x08  int16   ParentBone      Parent bone ID or -1 if there is none.
    # 0x0A  uint16  Unknown[3]      The first one might be related to the parts of the bodies.
    # 0x10  ABlock  Translation     An animationblock for translation. Should be 3*floats.
    # 0x24  ABlock  Rotation        An animationblock for rotation. Should be 4*shorts, see Quaternion values and 2.x.
    # 0x38  ABlock  Scaling         An animationblock for scaling. Should be 3*floats.
    # 0x4C  float   PivotPoint[3]   The pivot point of that bone. Its a vector.


    FORMAT = "<iIhHHH" + "b" * (0x4C - 0x10) + "fff"

    def __init__(self, data, index):
        data = unpack(Bone.FORMAT, data)

        self.index = index
        self.used = False

        self.key_bone_id = data[0]
        self.parent_bone_id = data[2]
        self.pivot_point = Vector( (data[-3], data[-2], data[-1]) )

        self.parent = None
        self.children = []

        self.bl_bone = None

    def addChild(self, child):
        child.parent = self
        self.children.append(child)

    def name(self):
        if (self.key_bone_id == -1) or (self.key_bone_id >= len(BONE_NAMES)):
            return 'Bone%02d' % self.index

        return BONE_NAMES[self.key_bone_id]

    def markAsUsed(self):
        if not(self.used):
            self.used = True
            if self.parent is not None:
                self.parent.markAsUsed()

    def usedChildren(self):
        return list(filter(lambda x: x.used, self.children))

    def usedChildrenCount(self):
        return len(self.usedChildren())

    def depth(self, used_only=True):
        if used_only:
            if self.usedChildrenCount() == 0:
                return 0
            return sum(map(lambda x: x.depth(used_only), self.usedChildren())) + self.usedChildrenCount()
        else:
            if len(self.children) == 0:
                return 0
            return sum(map(lambda x: x.depth(used_only), self.children)) + len(self.children)


class Importer:

    def __init__(self, only_used_bones=True, smart_bone_parenting=True,
                 enable_armature_xray=False, display_bone_names=False):
        self.m2_file   = None
        self.skin_file = None

        self.only_used_bones      = only_used_bones
        self.smart_bone_parenting = smart_bone_parenting
        self.enable_armature_xray = enable_armature_xray
        self.display_bone_names   = display_bone_names

    def __del__(self):
        if self.m2_file is not None:
            self.m2_file.close()

        if self.skin_file is not None:
            self.skin_file.close()

    def process(self, filename):

        #_____ Open the files __________

        print("Open the files...")
        (root, ext) = os.path.splitext(filename)

        try:
            if ext.lower() == ".m2":
                self.m2_file = open(filename, "rb")
                self.skin_file = open(root + "00.skin", "rb")
            elif ext.lower() == ".skin":
                self.m2_file = open(root[:-2] + ".M2", "rb")
                self.skin_file = open(filename, "rb")
            else:
                Report_Dialog.show("ERROR - Unsupported file type: '%s'" % ext)
                return False
        except IOError as e:
            Report_Dialog.show(str(e))
            return False


        #_____ Check the .M2 file __________

        print("Checking the .M2 file...")

        # Magic number
        magic = self.m2_file.read(4)
        if magic != b"MD20":
            Report_Dialog.show("ERROR - Doesn't look like a .M2 file, invalid magic number: '%s'" % magic)
            return False

        # Version
        version = self._getUInt32(self.m2_file, OFF_M2_VERSION)
        if version != 272:
            Report_Dialog.show("ERROR - Unsupported version: '%s'" % version)
            return False


        #_____ Check the .skin file __________

        print("Checking the .skin file...")

        # Magic number
        magic = self.skin_file.read(4)
        if magic != b"SKIN":
            Report_Dialog.show("ERROR - Doesn't look like a .skin file, invalid magic number: '%s'" % magic)
            return False


        #_____ Importation of the vertices __________

        print("Importation of the vertices...")

        vertices_count = self._getUInt32(self.m2_file, OFF_M2_VERTICES_COUNT)
        vertices_addr = self._getUInt32(self.m2_file, OFF_M2_VERTICES_ADDR)

        print("    %d vertices found" % vertices_count)

        vertices = []

        self.m2_file.seek(vertices_addr)
        for i in range(0, vertices_count):
            data = self.m2_file.read(calcsize(Vertex.FORMAT))
            vertices.append(Vertex(data))


        #_____ Importation of the indices __________

        print("Importation of the indices...")

        indices_count = self._getUInt32(self.skin_file, OFF_SKIN_INDICES_COUNT)
        indices_addr = self._getUInt32(self.skin_file, OFF_SKIN_INDICES_ADDR)

        print("    %d indices found" % indices_count)

        indices = []

        self.skin_file.seek(indices_addr)
        for i in range(0, indices_count):
            indices.append(unpack("<H", self.skin_file.read(2))[0])


        #_____ Importation of the triangles __________

        print("Importation of the triangles...")

        triangles_count = self._getUInt32(self.skin_file, OFF_SKIN_TRIANGLES_COUNT) // 3
        triangles_addr = self._getUInt32(self.skin_file, OFF_SKIN_TRIANGLES_ADDR)

        print("    %d triangles found" % triangles_count)

        triangles = []

        self.skin_file.seek(triangles_addr)
        for i in range(0, triangles_count):
            data = self.skin_file.read(calcsize(Triangle.FORMAT))
            triangles.append(Triangle(data))


        #_____ Importation of the bone lookup table __________

        print("Importation of the bone lookup table...")

        bone_lookup_table_size = self._getUInt32(self.m2_file, OFF_M2_BONE_LOOKUP_TABLE_SIZE)
        bone_lookup_table_addr = self._getUInt32(self.m2_file, OFF_M2_BONE_LOOKUP_TABLE_ADDR)

        print("    %d bones found in the lookup table" % bone_lookup_table_size)

        bone_lookup_table = []

        self.m2_file.seek(bone_lookup_table_addr)
        for i in range(0, bone_lookup_table_size):
            bone_lookup_table.append(unpack("<H", self.m2_file.read(2))[0])


        #_____ Importation of the key bone lookup table __________

        print("Importation of the key bone lookup table...")

        key_bone_lookup_table_size = self._getUInt32(self.m2_file, OFF_M2_KEY_BONE_LOOKUP_TABLE_SIZE)
        key_bone_lookup_table_addr = self._getUInt32(self.m2_file, OFF_M2_KEY_BONE_LOOKUP_TABLE_ADDR)

        print("    %d key bones found in the lookup table" % key_bone_lookup_table_size)

        key_bone_lookup_table = []

        self.m2_file.seek(key_bone_lookup_table_addr)
        for i in range(0, key_bone_lookup_table_size):
            key_bone_lookup_table.append(unpack("<H", self.m2_file.read(2))[0])


        #_____ Importation of the submeshes __________

        print("Importation of the submeshes...")

        submeshes_count = self._getUInt32(self.skin_file, OFF_SKIN_SUBMESHES_COUNT)
        submeshes_addr = self._getUInt32(self.skin_file, OFF_SKIN_SUBMESHES_ADDR)

        print("    %d submeshes found" % submeshes_count)

        submeshes = []

        self.skin_file.seek(submeshes_addr)
        for i in range(0, submeshes_count):
            data = self.skin_file.read(calcsize(Submesh.FORMAT))
            submeshes.append(Submesh(data))


        #_____ Importation of the bones __________

        print("Importation of the bones...")

        bones_count = self._getUInt32(self.m2_file, OFF_M2_BONES_COUNT)
        bones_addr = self._getUInt32(self.m2_file, OFF_M2_BONES_ADDR)

        print("    %d bones found" % bones_count)

        bones = []

        self.m2_file.seek(bones_addr)
        for i in range(0, bones_count):
            data = self.m2_file.read(calcsize(Bone.FORMAT))
            bones.append(Bone(data, len(bones)))

        for bone in bones:
            if bone.parent_bone_id >= 0:
                bones[bone.parent_bone_id].addChild(bone)

        key_bones = list(filter(lambda x: x.key_bone_id >= 0, bones))
        print("    %d key bones found" % len(key_bones))

        root_bones = list(filter(lambda x: x.parent is None, key_bones))
        print("    %d root bones found" % len(root_bones))

        for bone in bones:
            for submesh in submeshes:
                filtered_bone_lookup_table = bone_lookup_table[submesh.bones_start:submesh.bones_start+submesh.bones_count]
                if bone.index in filtered_bone_lookup_table:
                    bone.markAsUsed()

        used_bones = list(filter(lambda x: x.used, bones))
        print("    %d used bones found" % len(used_bones))


        #_____ Importation of the name of the model __________

        print("Importation of the name of the model...")

        name_length = self._getUInt32(self.m2_file, OFF_M2_NAME_LENGTH) - 1
        name_addr = self._getUInt32(self.m2_file, OFF_M2_NAME_ADDR)

        self.m2_file.seek(name_addr)
        mesh_name = self.m2_file.read(name_length).decode()


        #_____ Creation of the blender model __________

        print("Creation of the blender model...")

        print("  Creation of the armature...")

        # Create the blender armature and object
        armature = bpy.data.armatures.new('%s_Armature' % mesh_name)
        rig = bpy.data.objects.new(mesh_name, armature)
        rig.location = (0, 0, 0)
        rig.show_x_ray = self.enable_armature_xray
        armature.show_names = self.display_bone_names

        # Link the object to the scene
        scene = bpy.context.scene
        scene.objects.link(rig)
        scene.objects.active = rig
        scene.update()

        # Creation of the bones
        bpy.ops.object.editmode_toggle()

        if self.only_used_bones:
            bones_to_import = used_bones
        else:
            bones_to_import = bones

        for bone in bones_to_import:
            self._createBone(bone, armature)

        bpy.ops.object.mode_set(mode='OBJECT')

        # Creation of the submeshes
        for submesh in submeshes:
            print("  Creation of the submesh '%s'..." % submesh.name)

            # Create the blender mesh and object
            mesh = bpy.data.meshes.new('%s_Mesh' % submesh.name)
            obj = bpy.data.objects.new(submesh.name, mesh)
            obj.location = (0, 0, 0)

            # Link the object to the scene
            scene.objects.link(obj)
            scene.objects.active = obj
            scene.update()

            # Retrieve the triangles of the submesh
            print("    - %s triangles, from %d" % (submesh.triangles_count, submesh.triangles_start))
            submesh_triangles = triangles[submesh.triangles_start:submesh.triangles_start+submesh.triangles_count]

            # Retrieve the indices of the submesh
            print("    - %s indices, from %d" % (submesh.indices_count, submesh.indices_start))
            submesh_indices = indices[submesh.indices_start:submesh.indices_start+submesh.indices_count]

            # Retrieve the list of vertex coordinates
            submesh_vertices = [ vertices[index] for index in submesh_indices ]
            verts = [ vertex.position.to_tuple() for vertex in submesh_vertices ]

            # Retrieve the list of faces
            faces = list(map(lambda x: x.to_tuple(offset=submesh.indices_start), submesh_triangles))

            # Create the mesh
            mesh.from_pydata(verts, [], faces)

            # Update the mesh with the new data
            mesh.update(calc_edges=True)

            # Normals
            for n, vertex in enumerate(mesh.vertices):
                vertex.normal = submesh_vertices[n].normal

            # UV coordinates
            uvtex = mesh.uv_textures.new(submesh.name)
            bm = bmesh.new()
            bm.from_mesh(mesh)

            uv_layer = bm.loops.layers.uv[0]

            for face in bm.faces:
                for loop in face.loops:
                    loop[uv_layer].uv.x = submesh_vertices[loop.vert.index].texture_coords[0]
                    loop[uv_layer].uv.y = 1.0 - submesh_vertices[loop.vert.index].texture_coords[1]

            # Create the vertex groups
            vgroups = {}
            for bone in bones_to_import:
                vgroups[bone.name()] = []

            for v_index, vertex in enumerate(submesh_vertices):
                for b_index, bone_index in enumerate(filter(lambda x: x > 0, vertex.bone_indices)):
                    vgroups[bones[bone_index].name()].append( (v_index, vertex.bone_weights[b_index] / 255) )

            for name in vgroups.keys():
                if len(vgroups[name]) > 0:
                    grp = obj.vertex_groups.new(name)
                    for (v, w) in vgroups[name]:
                        grp.add([v], w, 'REPLACE')

            # Give the mesh object an armature modifier, using the vertex groups
            rig.select = True
            obj.select = True
            scene.objects.active = rig

            bpy.ops.object.parent_set(type='ARMATURE')
            obj.modifiers['Armature'].use_bone_envelopes = False
            obj.modifiers['Armature'].use_vertex_groups = True

            rig.select = False
            obj.select = False


        Report_Dialog.show("OK")

        self.m2_file.close()
        self.skin_file.close()

        self.m2_file   = None
        self.skin_file = None

        return True

    def _getUInt32(self, file, offset):
        file.seek(offset)
        return unpack("<I", file.read(4))[0]

    def _getUInt16(self, file, offset):
        file.seek(offset)
        return unpack("<H", file.read(2))[0]

    def _createBone(self, bone, armature):
        name = bone.name()

        print("  Creation of the bone '%s'..." % name)

        bl_bone = armature.edit_bones.new(name)
        bl_bone.head = bone.pivot_point.to_tuple()

        if bone.usedChildrenCount() == 1:
            bl_bone.tail = bone.children[0].pivot_point.to_tuple()
        elif bone.usedChildrenCount() > 1:
            done = False
            if self.smart_bone_parenting:
                max_depth = 0
                max_depth_bones = []
                for child in bone.usedChildren():
                    depth = child.depth(self.only_used_bones)
                    if depth > max_depth:
                        max_depth = depth
                        max_depth_bones = [child]
                    elif depth == max_depth:
                        max_depth_bones.append(child)

                print("%s - %d - %d" % (bone.name(), max_depth, len(max_depth_bones)))

                if len(max_depth_bones) == 1:
                    bl_bone.tail = max_depth_bones[0].pivot_point.to_tuple()
                    done = True

            if not(done):
                v = Vector( (0, 0, 0) )
                for child in bone.usedChildren():
                    v += child.pivot_point
                bl_bone.tail = (v / bone.usedChildrenCount()).to_tuple()
        elif bone.parent is not None:
            if bone.parent.bl_bone is None:
                self._createBone(bone.parent, armature)

            v = (bone.pivot_point - bone.parent.pivot_point)
            if v.length >= 0.001:
                v.normalize()
                bl_bone.tail = (bone.parent.bl_bone.length * v + bone.pivot_point).to_tuple()
            else:
                bl_bone.tail = (bone.parent.bl_bone.length * bone.pivot_point.normalized() + bone.pivot_point).to_tuple()
        else:
            bl_bone.tail = (bone.pivot_point * 2).to_tuple()

        if bone.parent is not None:
            bl_bone.parent = bone.parent.bl_bone
            bl_bone.use_connect = (bone.parent.usedChildrenCount() == 1)

        bone.bl_bone = bl_bone


##################################### BLENDER CLASSES ####################################

class Report_Dialog(bpy.types.Menu):
    bl_label = "M2 Importer Results | (see console for full report)"

    message = ""

    def draw(self, context):
        layout = self.layout
        for line in Report_Dialog.message.splitlines():
            layout.label(text=line)

    @staticmethod
    def show(message=None):
        if message is not None:
            Report_Dialog.message = message
        print(Report_Dialog.message)
        bpy.ops.wm.call_menu(name='Report_Dialog')

    @staticmethod
    def append(line):
        Report_Dialog.message += line + "\n"


class ImportM2(bpy.types.Operator, ImportHelper):
    '''Import a Blizzard M2 file'''

    bl_idname = "import_mesh.m2"
    bl_label = "Import M2"

    filter_glob = StringProperty(default="*.M2;*.skin", options={'HIDDEN'})

    only_used_bones = BoolProperty(name="Used bones", description="Import only the bones affecting the vertices", default=True)
    smart_bone_parenting = BoolProperty(name="Smart bone parenting",
                                        description="Try to guess the best tail position of the bones when one as several children",
                                        default=True)
    enable_armature_xray = BoolProperty(name="Enable armature X-Ray", default=False)
    display_bone_names = BoolProperty(name="Display bone names", default=False)


    def execute(self, context):
        keywords = self.as_keywords(ignore=("filter_glob",))

        importer = Importer(self.only_used_bones, self.smart_bone_parenting,
                            self.enable_armature_xray, self.display_bone_names)
        importer.process(self.filepath)
        return {'FINISHED'}


################################## BLENDER REGISTRATION ##################################

def menu_func_import(self, context):
    self.layout.operator(ImportM2.bl_idname, text="Blizzard M2 (.M2)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
