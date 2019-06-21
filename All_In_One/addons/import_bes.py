# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  version 2 as published by the Free Software Foundation.
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

import os
import struct
import bpy
import functools
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty, IntProperty, BoolProperty
from mathutils import Euler, Vector

bl_info = {
    "name"       : "Vietcong BES (.bes)",
    "author"     : "Jan Havran",
    "version"    : (0, 3),
    "blender"    : (2, 70, 0),
    "location"   : "File > Import > BES (.bes)",
    "description": "Import Vietcong BES files",
    "wiki_url"   : "https://github.com/OpenVietcong/blender-plugin-vietcong",
    "tracker_url": "https://github.com/OpenVietcong/blender-plugin-vietcong/issues",
    "category": "Learnbgame",
}

class BESError(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

class BESObject(object):
    def __init__(self, name):
        self.name = name
        self.children = []
        self.meshes = []
        self.materials = []
        self.translation = (0.0, 0.0, 0.0)
        self.rotation    = (0.0, 0.0, 0.0)
        self.scale       = (1.0, 1.0, 1.0)

class BESMesh(object):
    def __init__(self, vertices, faces, material):
        self.vertices = vertices
        self.faces = faces
        self.material = material

class BESVertex(object):
    class Flags:
        XYZ    = 0x002
        Normal = 0x010

        Tex0   = 0x000
        Tex1   = 0x100
        Tex2   = 0x200
        Tex3   = 0x300
        Tex4   = 0x400
        Tex5   = 0x500
        Tex6   = 0x600
        Tex7   = 0x700
        Tex8   = 0x800

        TexcountMask  = 0xf00
        TexcountShift = 8
        TexcountMax   = 8

    def __init__(self, coords, normals, uv = []):
        self.coords = coords
        self.normals = normals
        self.uv = uv

class BESMaterial(object):
    NoneMaterial = 0xFFFFFFFF
    # Texture extensions used by engine (sorted by priority)
    TexExtensions = ["DDS", "TGA", "BMP"]

    def __init__(self, transparency, textures):
        self.transparent = transparency
        self.textures = textures

class BESBitmap(BESMaterial):
    class Texture:
        Diffuse      = 0x00
        Displacement = 0x01
        Filter       = 0x09

    texOffset = 0x00
    texCnt    = 12
    uv_pri = [2, 11, 8, 1, 3, 4, 5, 6, texCnt, 7, 9, 10]

    def __init__(self, textures):
        super().__init__(False, textures)
        self.textures.sort(key=lambda tex: tex.uv_order)

class BESPteroMat(BESMaterial):
    class Texture:
        Ground       = 0x10
        Multitexture = 0x11
        Overlay      = 0x12

    texOffset = 0x10
    texCnt    = 8
    uv_pri = [1, 3, 2, 5, 4, texCnt, 5, 2]

    trans_types = [0x3023, # transparent, zbufwrite, sort
                   0x3123, # transparent, zbufwrite, sort, 1-bit alpha
                   0x3223, # translucent, no_zbufwrite, sort
                   0x3323, # transparent, zbufwrite, nosort, 1-bit alpha
                   0x3423] # translucent, add with background, no_zbufwrite, sort

    def __init__(self, name, transparency, textures):
        super().__init__(transparency, textures)
        self.name = name
        self.textures.sort(key=lambda tex: tex.uv_order)

class BESTexture(object):
    def __init__(self, use_alpha, blend_type, file_name, uv_order):
        self.use_alpha = use_alpha
        self.blend_type = blend_type
        self.file_name = file_name
        self.uv_order = uv_order

class BESTextureDiffuse(BESTexture):
    def __init__(self, file_name, uv_order):
        super().__init__(True, 'MIX', file_name, uv_order)

class BESTextureDisplacement(BESTexture):
    def __init__(self, file_name, uv_order):
        super().__init__(False, 'MULTIPLY', file_name, uv_order)

class BESTextureFilter(BESTexture):
    def __init__(self, file_name, uv_order):
        super().__init__(False, 'MIX', file_name, uv_order)

class BESTextureUnknown(BESTexture):
    def __init__(self, file_name, uv_order):
        super().__init__(False, 'MIX', file_name, uv_order)

class BES(object):
    class Header:
        sig = b'BES\x00'
        vers = [b'0100']

    class BlockID:
        Object         = 0x0001
        Model          = 0x0030
        Mesh           = 0x0031
        Vertices       = 0x0032
        Faces          = 0x0033
        Properties     = 0x0034
        Transformation = 0x0035
        Unk36          = 0x0036
        Unk38          = 0x0038
        UserInfo       = 0x0070
        Material       = 0x1000
        Bitmap         = 0x1001
        PteroMat       = 0x1002

    class BlockPresence:
        OptSingle   = 0  # <0;1>
        OptMultiple = 1  # <0;N>
        ReqSingle   = 2  # <1;1>
        ReqMultiple = 3  # <1;N>

    def __init__(self, fname):
        self.objects = []
        try:
            self.f = open(fname, "rb")
        except Exception as e:
            raise BESError(str(e))

        self.read_header()
        self.read_preview()
        self.read_data()

    def unpack(self, fmt, data):
        st_fmt = fmt
        st_len = struct.calcsize(st_fmt)
        st_unpack = struct.Struct(st_fmt).unpack_from
        return st_unpack(data[:st_len])

    def read_header(self):
        data = self.f.read(0x10)
        (sig, ver, unk1, unk2) = self.unpack("<4s4sII", data)

        if sig != BES.Header.sig:
            raise BESError("Invalid BES header signature")

        if ver not in BES.Header.vers:
            raise BESError("Unsupported BES version: {}".format(ver))

        return ver

    def read_preview(self):
        self.f.read(0x3000)

    def read_data(self):
        data = self.f.read()
        self.parse_data(data)

    def parse_data(self, data):
        res = self.parse_blocks({BES.BlockID.Object   : BES.BlockPresence.ReqSingle,
                                 BES.BlockID.UserInfo : BES.BlockPresence.ReqSingle},
                                data)
        self.objects.append(res[BES.BlockID.Object])

    def parse_block_desc(self, data):
        return self.unpack("<II", data)

    def parse_block_by_label(self, label, data):
        try:
            if   label == BES.BlockID.Object:
                return self.parse_block_object(data)
            elif label == BES.BlockID.Model:
                return self.parse_block_model(data)
            elif label == BES.BlockID.Mesh:
                return self.parse_block_mesh(data)
            elif label == BES.BlockID.Vertices:
                return self.parse_block_vertices(data)
            elif label == BES.BlockID.Faces:
                return self.parse_block_faces(data)
            elif label == BES.BlockID.Properties:
                return self.parse_block_properties(data)
            elif label == BES.BlockID.Transformation:
                return self.parse_block_transformation(data)
            elif label == BES.BlockID.Unk36:
                return self.parse_block_unk36(data)
            elif label == BES.BlockID.Unk38:
                return self.parse_block_unk38(data)
            elif label == BES.BlockID.UserInfo:
                return self.parse_block_user_info(data)
            elif label == BES.BlockID.Material:
                return self.parse_block_material(data)
            elif label == BES.BlockID.Bitmap:
                return self.parse_block_bitmap(data)
            elif label == BES.BlockID.PteroMat:
                return self.parse_block_pteromat(data)
            else:
                raise BESError("Unknown block")
        except BESError as e:
            raise BESError("{:04X}->{}".format(label, e.msg))

    def parse_blocks(self, blocks, data):
        # Init return values
        ret = dict()
        for label in blocks:
            if blocks[label] == BES.BlockPresence.OptSingle or blocks[label] == BES.BlockPresence.ReqSingle:
                ret[label] = None
            else:
                ret[label] = []

        # Search for all blocks
        start = 0
        while len(data[start:]) > 8:
            (label, size) = self.parse_block_desc(data[start:])

            if label in blocks:
                subblock = data[start + 8: start + size]

                if blocks[label] == BES.BlockPresence.OptSingle or blocks[label] == BES.BlockPresence.ReqSingle:
                    blocks.pop(label)
                    ret[label] = self.parse_block_by_label(label, subblock)
                else:
                    ret[label].append(self.parse_block_by_label(label, subblock))
            else:
                raise BESError("Unexpected block {:04X} in this location".format(label))
            start += size

        if start != len(data):
            raise BESError("Block contains more data than expected")

        # Check if all required blocks were found in this block
        for label in blocks:
            if blocks[label] == BES.BlockPresence.ReqSingle:
                raise BESError("Required block {:04X} not found in this location".format(label))
            elif blocks[label] == BES.BlockPresence.ReqMultiple and label not in ret:
                raise BESError("Required block {:04X} not found in this location".format(label))

        return ret

    def parse_block_object(self, data):
        (children, name_size) = self.unpack("<II", data)
        (name,) = self.unpack("<" + str(name_size) + "s", data[8:])
        name = str(name, 'ascii').strip(chr(0))

        model = BESObject(name)

        res = self.parse_blocks({BES.BlockID.Object         : BES.BlockPresence.OptMultiple,
                                 BES.BlockID.Model          : BES.BlockPresence.OptSingle,
                                 BES.BlockID.Properties     : BES.BlockPresence.OptSingle,
                                 BES.BlockID.Transformation : BES.BlockPresence.OptSingle,
                                 BES.BlockID.Unk38          : BES.BlockPresence.OptSingle,
                                 BES.BlockID.Material       : BES.BlockPresence.OptSingle},
                                data[8 + name_size:])

        if len(res[BES.BlockID.Object]) != children:
            raise BESError("Number of object children does not match")

        for obj in res[BES.BlockID.Object]:
            model.children.append(obj)
        if res[BES.BlockID.Transformation]:
            (model.translation, model.rotation, model.scale) = res[BES.BlockID.Transformation]
        if res[BES.BlockID.Model]:
            if res[BES.BlockID.Model][BES.BlockID.Mesh]:
                model.meshes = res[BES.BlockID.Model][BES.BlockID.Mesh]
            if res[BES.BlockID.Model][BES.BlockID.Transformation]:
                (model.translation, model.rotation, model.scale) = res[BES.BlockID.Model][BES.BlockID.Transformation]
        if res[BES.BlockID.Material]:
            model.materials = res[BES.BlockID.Material]
            # TODO check all children meshes for valid materials

        return model

    def parse_block_model(self, data):
        (mesh_children,) = self.unpack("<I", data)

        res = self.parse_blocks({BES.BlockID.Mesh           : BES.BlockPresence.OptMultiple,
                                 BES.BlockID.Properties     : BES.BlockPresence.ReqSingle,
                                 BES.BlockID.Transformation : BES.BlockPresence.ReqSingle,
                                 BES.BlockID.Unk36          : BES.BlockPresence.OptSingle},
                                data[4:])

        if mesh_children != len(res[BES.BlockID.Mesh]):
            raise BESError("Number of meshes does not match")

        return res

    def parse_block_mesh(self, data):
        """ Parse Mesh block and return BESMesh instance """
        (material,) = self.unpack("<I", data)
        vertices = None
        faces = None

        res = self.parse_blocks({BES.BlockID.Vertices  : BES.BlockPresence.ReqSingle,
                                 BES.BlockID.Faces     : BES.BlockPresence.ReqSingle},
                                data[4:])
        vertices = res[BES.BlockID.Vertices]
        faces    = res[BES.BlockID.Faces]

        if max(max(faces, key=lambda item:item[1])) > len(vertices):
            raise BESError("Invalid faces number")

        return BESMesh(vertices, faces, material)

    def parse_block_vertices(self, data):
        """ Parse Vertices block and return list of BESVertex instances """
        (count, size, flags) = self.unpack("<III", data)
        texCnt = (flags & BESVertex.Flags.TexcountMask) >> BESVertex.Flags.TexcountShift
        flagsMin = BESVertex.Flags.XYZ | BESVertex.Flags.Normal
        flagsMax = flagsMin | BESVertex.Flags.TexcountMask
        vertices = []

        if (flags & flagsMin) != flagsMin or (flags | flagsMax) != flagsMax:
            raise("Unsupported vertex flags: {:08x}".format(flags))
        if texCnt > BESVertex.Flags.TexcountMax:
            raise("Texture count over limit: {}".format(texCnt))
        if 24 + 8 * texCnt != size:
            raise BESError("Vertex size ({}) do not match".format(size))
        if count * size != len(data[12:]):
            raise BESError("Block size mismatch")

        ptr = 12
        for i in range(count):
            coords = self.unpack("<fff", data[ptr:])
            ptr += 12
            normals = self.unpack("<fff", data[ptr:])
            ptr += 12

            uv_array = []
            for texID in range(texCnt):
                uv = self.unpack("<ff", data[ptr:])
                uv_array.append(uv)
                ptr += 8

            vertices.append(BESVertex(coords, normals, uv_array))

        return vertices

    def parse_block_faces(self, data):
        """
        Parse Faces block and return list of tuples.
        Each tuple means one face made of 3 integers (vertices IDs)
        """
        (count,) = self.unpack("<I", data)
        faces = []

        if count * 12 != len(data[4:]):
            raise BESError("Block size mismatch")

        ptr = 4
        for i in range(count):
            face = self.unpack("<III", data[ptr:])
            faces.append(face)
            ptr += 12

        return faces

    def parse_block_properties(self, data):
        pass

    def parse_block_transformation(self, data):
        """
        Parse Transformation block and return tuple of tuples - translation, rotation, scale.
        Each tuple means tranformation values (x, y, z).
        """
        if len(data) != 100:
            raise BESError("Block size mismatch")

        translation = self.unpack("<fff", data[00:12])
        rotation    = self.unpack("<fff", data[12:24])
        scale       = self.unpack("<fff", data[24:36])

        return (translation, rotation, scale)

    def parse_block_unk36(self, data):
        pass
    def parse_block_unk38(self, data):
        pass
    def parse_block_user_info(self, data):
        pass

    def parse_block_material(self, data):
        (materialCnt,) = self.unpack("<I", data)
        materials = []

        # Info about materials order must preserve, therefore we can not use parse_blocks
        # func, instead of this we use parse_block_by_label directly
        start = 4
        for matID in range(materialCnt):
            (label, size) = self.parse_block_desc(data[start:])

            if label not in [BES.BlockID.Bitmap, BES.BlockID.PteroMat]:
                raise BESError("Invalid material")

            subblock = data[start + 8: start + size]
            materials.append(self.parse_block_by_label(label, subblock))
            start += size

        if materialCnt != len(materials):
            raise BESError("Number of meshes does not match")

        return materials

    def parse_block_bitmap(self, data):
        (unk1, unk2, texMask) = self.unpack("<I4sI", data)

        textures = []
        ptr = 12
        for texID in range(BESBitmap.texOffset, BESBitmap.texOffset + BESBitmap.texCnt):
            if texMask & 1 << texID:
                (tex_name_size, coord) = self.unpack("<II", data[ptr:])
                (tex_name,) = self.unpack("<" + str(tex_name_size) + "s", data[ptr + 8:])
                tex_name = str(tex_name, 'ascii').strip(chr(0))
                uv_order = BESBitmap.uv_pri[texID - BESBitmap.texOffset]

                if texID == BESBitmap.Texture.Diffuse:
                    tex = BESTextureDiffuse(tex_name, uv_order)
                elif texID == BESBitmap.Texture.Displacement:
                    tex = BESTextureDisplacement(tex_name, uv_order)
                elif texID == BESBitmap.Texture.Filter:
                    tex = BESTextureFilter(tex_name, uv_order)
                else:
                    tex = BESTextureUnknown(tex_name, uv_order)
                textures.append(tex)

                ptr += 8 + tex_name_size

        return BESBitmap(textures)

    def parse_block_pteromat(self, data):
        (sides, texMask, collis_mat, trans_type, veget) = self.unpack("<II4sI4s", data)
        (name_size,) = self.unpack("<I", data[20:])
        (name,) = self.unpack("<" + str(name_size) + "s", data[24:])
        name = str(name, 'ascii').strip(chr(0))

        transparent = trans_type in BESPteroMat.trans_types

        textures = []
        ptr = 24 + name_size
        texCnt = 0
        for texID in range(BESPteroMat.texOffset, BESPteroMat.texOffset + BESPteroMat.texCnt):
            if texMask & 1 << texID:
                texCnt += 1

        for tex in range(texCnt):
                (coord, tex_name_size) = self.unpack("<II", data[ptr:])
                (tex_name,) = self.unpack("<" + str(tex_name_size) + "s", data[ptr + 8:])
                tex_name = str(tex_name, 'ascii').strip(chr(0))

                # Texture type is stored in 'coord', but textures are not sorted by their mask.
                # Find what type is current texture
                texID = 0
                for texPos in range(BESPteroMat.texCnt):
                    if coord >> BESPteroMat.texOffset == 1 << texPos:
                        texID = texPos + BESPteroMat.texOffset
                if texID == 0:
                    raise("Invalid texture mask")

                uv_order = BESPteroMat.uv_pri[texID - BESPteroMat.texOffset]

                if texID == BESPteroMat.Texture.Ground:
                    tex = BESTextureDiffuse(tex_name, uv_order)
                elif texID == BESPteroMat.Texture.Multitexture:
                    tex = BESTextureDisplacement(tex_name, uv_order)
                elif texID == BESPteroMat.Texture.Overlay:
                    tex = BESTextureFilter(tex_name, uv_order)
                else:
                    tex = BESTextureUnknown(tex_name, uv_order)
                textures.append(tex)

                ptr += 8 + tex_name_size

        return BESPteroMat(name, transparent, textures)

class AddDirs(bpy.types.Operator):
    bl_idname = "import_mesh.add_dirs"
    bl_label = "Add Directories"

    # Collection of currently selected directories and files
    dir_paths = CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):
        tex_dirs = context.active_operator.tex_dirs

        # Fill layout template_list by selected directories by user
        for tex_dir in self.dir_paths:
            if tex_dir.name not in (tex_dir.name for tex_dir in tex_dirs):
                item = tex_dirs.add()
                item.name = tex_dir.name

        return {'FINISHED'}

class RemoveDir(bpy.types.Operator):
    bl_idname = "import_mesh.remove_dir"
    bl_label = "Remove Directory"

    # Index of currently selected directory from template_list
    index = IntProperty()

    @classmethod
    def poll(self, context):
        return len(context.active_operator.tex_dirs) > 0

    def execute(self, context):
        try:
            context.active_operator.tex_dirs.remove(self.index)
        except IndexError:
            pass

        return {'FINISHED'}

class BESImporter(bpy.types.Operator, ImportHelper):
    bl_idname = "import_mesh.bes"
    bl_label  = "Import BES files"

    # Show only "*.bes" files for import
    filter_glob = StringProperty(
            default="*.bes",
            options={'HIDDEN'}
            )

    # Active directory
    directory = StringProperty(options={'HIDDEN'})

    # Search directories recursively
    dir_search_r = BoolProperty(
            name="Search directories recursively",
            description="Search directories recursively for textures (may be slow)",
            default=False,
            )

    # Ignore texture extensions checkbox
    dir_ext_ignore = BoolProperty(
            name="Ignore texture extensions",
            description="Load texture by given name with any of these extensions: dds, tga, bmp",
            default=False,
            )

    # All directories currently chosen by user
    dirs = CollectionProperty(type=bpy.types.PropertyGroup)

    # Collection of selected files for import
    files = CollectionProperty(
            name="File name",
            type=bpy.types.OperatorFileListElement
            )

    # Properties whose content will be used by template_list
    # Filled by AddDirs, drew by BESImporter
    tex_dirs = CollectionProperty(type=bpy.types.PropertyGroup)
    tex_dirs_index = IntProperty()

    def draw(self, context):
        layout = self.layout

        # Show checkbox for recursive search
        layout.prop(self, "dir_search_r")

        # Show checkbox for ignoring extensions
        layout.prop(self, "dir_ext_ignore")

        # Row for adding/removing dirs where may be located textures
        row = layout.row(True)
        row.label("Search directories for textures")

        # Add AddDirs operator into row and fill its props
        props = row.operator(AddDirs.bl_idname, icon='ZOOMIN', text="")
        for f in self.dirs:
            item = props.dir_paths.add()
            item.name = os.path.join(self.directory, f.name)

        # Add RemoveDir operator into row and fill its props
        props = row.operator(RemoveDir.bl_idname, icon='ZOOMOUT', text="")
        props.index = self.tex_dirs_index

        # Show 'tex_dirs' items as a rows in widget list
        layout.template_list("UI_UL_list", "TexSubDirs", self, "tex_dirs", self, "tex_dirs_index")

    def execute(self, context):
        models = []

        # Make a list of all directories where script will search for textures
        search_dirs = [self.directory]
        search_dirs.extend(d.name for d in self.tex_dirs)
        if self.dir_search_r:
            # Add all subdirectories recursively
            for root_dir in search_dirs:
                 for sub_root, dirs, files in os.walk(root_dir):
                     for sub_dir in dirs:
                         new_dir = os.path.join(sub_root, sub_dir)
                         if new_dir not in search_dirs:
                             search_dirs.append(new_dir)

        # Parse all selected files
        for f in self.files:
            # Parse BES file
            try:
                bes = BES(os.path.join(self.directory, f.name))
                models.append(bes)
            except BESError as e:
                self.report({'ERROR'}, e.msg)

        # Load all parsed models
        for bes in models:
            # Parse all objects in BES file
            for bes_roots in bes.objects:
                # Create materials
                bpy_materials = []
                for mat in bes_roots.materials:
                    name = mat.name if isinstance(mat, BESPteroMat) else "bitmap"
                    bpy_mat = bpy.data.materials.new(name)
                    bpy_mat.use_transparency = mat.transparent
                    bpy_mat.alpha = 0.0 if mat.transparent else bpy_mat.alpha
                    bpy_materials.append(bpy_mat)

                    # Create textures
                    for idx, tex in enumerate(mat.textures):
                        tex_file = tex.file_name
                        bpy_tex = bpy.data.textures.new(os.path.splitext(tex_file)[0], 'IMAGE')
                        tex_paths = []

                        # Search for files with any extension supported by
                        # PteroEngine (which is BESMaterial.TexExtensions) if users
                        # chose to ignore extensions
                        tex_exts = BESMaterial.TexExtensions if self.dir_ext_ignore else []

                        # Since Vietcong is Windows game, we need to work with texture name as
                        # case insensitive. On top of that, the user has a possibility to choose
                        # directories where textures may be located
                        for tex_dir in search_dirs:
                            tex_paths.extend(get_case_insensitive_path(tex_dir, tex_file, tex_exts))

                        # Try to load image from file
                        if len(tex_paths) != 0:
                            # Sort found textures by extension (PteroEngine requires following
                            # priority: dds, tga, bmp)
                            tex_paths.sort(key=functools.cmp_to_key(sort_ext))

                            # Simply choose any texture with extension of the highest priority
                            tex_path = ".".join(tex_paths[0])
                            bpy_tex.image = bpy.data.images.load(tex_path)
                        else:
                            self.report({'WARNING'}, "Texture '{}' not found".format(tex_file))

                        slot = bpy_mat.texture_slots.add()
                        slot.texture = bpy_tex
                        slot.use_map_alpha = tex.use_alpha
                        slot.alpha_factor = 1.0 if tex.use_alpha else slot.alpha_factor
                        slot.blend_type = tex.blend_type
                        slot.uv_layer = "{}-{}.uv".format(bpy_mat.name, idx)

                # Create objects
                for bes_obj in bes_roots.children:
                    self.add_object(bes_obj, bpy_materials, bes_roots.materials, None)

        return {'FINISHED'}

    def add_object(self, bes_obj, bpy_mats, bes_mats, parent):
        # Create new object
        bpy_obj = bpy.data.objects.new(bes_obj.name, None)
        bpy_obj.parent = parent

        # Since Blender does not allow multiple meshes for single object (while BES does),
        # we have to create seperate object for every mesh.
        for mesh_id in range(len(bes_obj.meshes)):
            bes_mesh = bes_obj.meshes[mesh_id]

            # In BES the meshes do not have names, so we create one from object name and mesh ID
            mesh_name = "{}.{:08X}".format(bes_obj.name, mesh_id)

            # Create new mesh
            bpy_mesh = bpy.data.meshes.new(mesh_name)

            # Create new object from mesh and add it into scene
            mesh_obj = bpy.data.objects.new(mesh_name, bpy_mesh)
            mesh_obj.parent = bpy_obj
            bpy.context.scene.objects.link(mesh_obj)

            # Apply translation, rotation and scale
            mesh_obj.location = bes_obj.translation
            mesh_obj.rotation_euler = Euler(bes_obj.rotation, 'XYZ')
            mesh_obj.scale = bes_obj.scale

            # Update mesh data
            mesh_coords = list(vert.coords for vert in bes_mesh.vertices)
            bpy_mesh.from_pydata(mesh_coords, [], bes_mesh.faces)
            bpy_mesh.update(calc_edges = True)

            # Assign material to object
            if bes_mesh.material != BESMaterial.NoneMaterial:
                mesh_obj.data.materials.append(bpy_mats[bes_mesh.material])

                # Apply UV mapping
                uvtexs = []
                uvlayers = []
                # Create uv_texture for all material textures
                for idx, tex in enumerate(bes_mats[bes_mesh.material].textures):
                    uvtex = bpy_mesh.uv_textures.new()
                    uvtex.name = "{}-{}.uv".format(bpy_mats[bes_mesh.material].name, idx)
                    uvtex.active = True
                    uvlayer = bpy_mesh.uv_layers[uvtex.name]

                    uvtexs.append(uvtex)
                    uvlayers.append(uvlayer)

                # Update uv data for all vertices/textures
                for polygon in bpy_mesh.polygons:
                    for vert, loop in zip(polygon.vertices, polygon.loop_indices):
                        for idx, tex in enumerate(bes_mats[bes_mesh.material].textures):
                            uv_vect = Vector(bes_mesh.vertices[vert].uv[idx])
                            uv_vect.y = 1.0 - uv_vect.y # Convert UV coords from BES to Blender
                            uvlayers[idx].data[loop].uv = uv_vect

        # Add children
        for bes_child in bes_obj.children:
            self.add_object(bes_child, bpy_mats, bes_mats, bpy_obj)

        # Add object into scene
        bpy.context.scene.objects.link(bpy_obj)

def get_case_insensitive_path(dirname, tex, tex_exts = []):
    """
    Returns list of found files. Each file is a tuple of (full path, extension)
    """
    file_paths = []
    tex_name = os.path.splitext(tex)[0].upper()

    # If there are not given required extensions, we will take one from texture name
    if len(tex_exts) == 0:
        tex_exts.append(os.path.splitext(tex)[1].strip('.').upper())

    for dir_file in os.listdir(dirname):
        (f_name, f_ext) = os.path.splitext(dir_file)
        f_ext = f_ext.strip(".")

        if f_name.upper() == tex_name and f_ext.upper() in tex_exts:
            file_paths.append((os.path.join(dirname, f_name), f_ext))

    return file_paths

def sort_ext(a, b):
    """
    Sort tuples (full path, extension) by extension.
    Priority of extensions is given by BESMaterial.TexExtensions array
    """
    ext_array = BESMaterial.TexExtensions
    i = ext_array.index(a[1]) if a[1] in ext_array else len(ext_array)
    j = ext_array.index(b[1]) if b[1] in ext_array else len(ext_array)

    if i > j:
        return 1
    elif i < j:
        return -1
    else:
        return 0

def menu_import_bes(self, context):
    self.layout.operator(BESImporter.bl_idname, text="BES (.bes)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import_bes)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import_bes)

if __name__ == "__main__":
    register()

