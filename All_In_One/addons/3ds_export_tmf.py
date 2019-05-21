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

bl_info = {
    "name": "Export 3DS for TrackMania Forever",
    "author": "Glauco Bacchi, Campbell Barton, Bob Holcomb, Richard Lärkäng, Damien McGinnes, Mark Stijnman, Sergey Savkin",
    "version": (1, 0, 5),
    "blender": (2, 7, 9),
    "location": "File > Export > 3DS for TMF (.3ds)",
    "description": "Export 3DS model for TrackMania Forever (.3ds)",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export"
}

import bpy
import bpy_extras
import time
import struct
import math
import mathutils
import bmesh

###### EXPORT OPERATOR #######
class Export_tmf(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export 3DS model for Trackmania Forever"""
    bl_idname = "export_scene.tmf"
    bl_label = "Export 3DS for TMF (.3ds)"

    filename_ext = ".3ds"
    filter_glob = bpy.props.StringProperty(
        default="*.3ds",
        options={'HIDDEN'},
        )

    use_selection = bpy.props.BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
        )

    def execute(self, context):

        keywords = self.as_keywords()

        start_time = time.time()
        print('\n_____START_____')
        props = self.properties
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        bpy.context.window.cursor_set('WAIT')
        exported = do_export(filepath,keywords["use_selection"])
        bpy.context.window.cursor_set('DEFAULT')

        if exported:
            print('finished export in %s seconds' %((time.time() - start_time)))
            print(filepath)

        return {'FINISHED'}

### REGISTER ###

def menu_func(self, context):
    self.layout.operator(Export_tmf.bl_idname, text="3DS for TMF (.3ds)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

######################################################
# Data Structures
######################################################

#Some of the chunks that we will export
#----- Primary Chunk, at the beginning of each file
PRIMARY                 = 0x4D4D

#------ Main Chunks
OBJECTINFO              = 0x3D3D  # This gives the version of the mesh and is found right before the material and object information
VERSION                 = 0x0002  # This gives the version of the .3ds file
KFDATA                  = 0xB000  # This is the header for all of the key frame info

#------ sub defines of OBJECTINFO
MATERIAL                = 45055  # 0xAFFF // This stored the texture info
OBJECT                  = 16384  # 0x4000 // This stores the faces, vertices, etc...

#>------ sub defines of MATERIAL
MATNAME                 = 0xA000  # This holds the material name
MATAMBIENT              = 0xA010  # Ambient color of the object/material
MATDIFFUSE              = 0xA020  # This holds the color of the object/material
MATSPECULAR             = 0xA030  # SPecular color of the object/material
MATSHINESS              = 0xA040  # Shininess of the object/material (percent)
MATSHIN2                = 0xA041  # Specularity of the object/material (percent)

MAT_DIFFUSEMAP          = 0xA200  # This is a header for a new diffuse texture
MAT_OPACMAP             = 0xA210  # head for opacity map
MAT_BUMPMAP             = 0xA230  # read for normal map
MAT_SPECMAP             = 0xA204  # read for specularity map

#>------ sub defines of MAT_???MAP
MATMAPFILE              = 0xA300  # This holds the file name of a texture
MAT_MAP_TILING          = 0xA351  # 2nd bit (from LSB) is mirror UV flag
MAT_MAP_USCALE          = 0xA354  # U axis scaling
MAT_MAP_VSCALE          = 0xA356  # V axis scaling
MAT_MAP_UOFFSET         = 0xA358  # U axis offset
MAT_MAP_VOFFSET         = 0xA35A  # V axis offset
MAT_MAP_ANG             = 0xA35C  # UV rotation around the z-axis in rad

MATTRANS                = 0xA050  # Transparency value (i.e. =100-OpacityValue) (percent)
PCT                     = 0x0030
MASTERSCALE             = 0x0100

RGB1                    = 0x0011
RGB2                    = 0x0012

#>------ sub defines of OBJECT
OBJECT_MESH             = 0x4100  # This lets us know that we are reading a new object
OBJECT_LIGHT            = 0x4600  # This lets un know we are reading a light object
OBJECT_CAMERA           = 0x4700  # This lets un know we are reading a camera object

#>------ sub defines of CAMERA
OBJECT_CAM_RANGES       = 0x4720  # The camera range values

#>------ sub defines of OBJECT_MESH
OBJECT_VERTICES         = 0x4110  # The objects vertices
OBJECT_FACES            = 0x4120  # The objects faces
OBJECT_MATERIAL         = 0x4130  # This is found if the object has a material, either texture map or color
OBJECT_UV               = 0x4140  # The UV texture coordinates
OBJECT_SMOOTH           = 0x4150  # Smooth group
OBJECT_TRANS_MATRIX     = 0x4160  # The Object Matrix

#>------ sub defines of KFDATA
KFDATA_KFHDR            = 0xB00A
KFDATA_KFSEG            = 0xB008
KFDATA_KFCURTIME        = 0xB009
KFDATA_OBJECT_NODE_TAG  = 0xB002

#>------ sub defines of OBJECT_NODE_TAG
OBJECT_NODE_ID          = 0xB030
OBJECT_NODE_HDR         = 0xB010
OBJECT_PIVOT            = 0xB013
OBJECT_INSTANCE_NAME    = 0xB011
POS_TRACK_TAG           = 0xB020
ROT_TRACK_TAG           = 0xB021
SCL_TRACK_TAG           = 0xB022

BOUNDBOX                = 0xB014

# So 3ds max can open files, limit names to 12 in length
# this is very annoying for filenames!
name_unique = []  # stores str, ascii only
name_mapping = {}  # stores {orig: byte} mapping


def sane_name(name):
    name_fixed = name_mapping.get(name)
    if name_fixed is not None:
        return name_fixed

    # strip non ascii chars
    new_name_clean = new_name = name.encode("ASCII", "replace").decode("ASCII")[:12]
    i = 0

    while new_name in name_unique:
        new_name = new_name_clean + ".%.3d" % i
        i += 1

    # note, appending the 'str' version.
    name_unique.append(new_name)
    name_mapping[name] = new_name = new_name.encode("ASCII", "replace")
    return new_name

def uv_key(uv):
    return round(uv[0], 6), round(uv[1], 6)

# size defines:
SZ_SHORT    = 2
SZ_INT      = 4
SZ_FLOAT    = 4

class _3ds_ushort(object):
    """Class representing a short (2-byte integer) for a 3ds file.
    *** This looks like an unsigned short H is unsigned from the struct docs - Cam***"""
    __slots__ = ("value", )

    def __init__(self, val=0):
        self.value = val

    def get_size(self):
        return SZ_SHORT

    def write(self, file):
        file.write(struct.pack("<H", self.value & 0xFFFF))

    def __str__(self):
        return str(self.value)

class _3ds_uint(object):
    """Class representing an int (4-byte integer) for a 3ds file."""
    __slots__ = ("value", )

    def __init__(self, val):
        self.value = val

    def get_size(self):
        return SZ_INT

    def write(self, file):
        file.write(struct.pack("<I", self.value & 0xFFFFFFFF))

    def __str__(self):
        return str(self.value)

class _3ds_float(object):
    """Class representing a 4-byte IEEE floating point number for a 3ds file."""
    __slots__ = ("value", )

    def __init__(self, val):
        self.value = val

    def get_size(self):
        return SZ_FLOAT

    def write(self, file):
        file.write(struct.pack("<f", self.value))

    def __str__(self):
        return str(self.value)

class _3ds_string(object):
    """Class representing a zero-terminated string for a 3ds file."""
    __slots__ = ("value", )

    def __init__(self, val=""):
        self.value = val

    def get_size(self):
        return (len(self.value) + 1)

    def write(self, file):
        binary_format = "<%ds" % (len(self.value) + 1)
        file.write(struct.pack(binary_format, self.value))

    def __str__(self):
        return str(self.value)

class _3ds_point_3d(object):
    """Class representing a three-dimensional point for a 3ds file."""
    __slots__ = "x", "y", "z"

    def __init__(self, point = (0.0,0.0,0.0)):
        self.x, self.y, self.z = point

    def get_size(self):
        return 3 * SZ_FLOAT

    def write(self, file):
        file.write(struct.pack('<3f', self.x, self.y, self.z))

    def __str__(self):
        return '(%f, %f, %f)' % (self.x, self.y, self.z)

# Used for writing a track
class _3ds_point_4d(object):
    '''Class representing a four-dimensional point for a 3ds file, for instance a quaternion.'''
    __slots__ = 'x','y','z','w'
    def __init__(self, point=(0.0,0.0,0.0,0.0)):
        self.x, self.y, self.z, self.w = point

    def get_size(self):
        return 4*SZ_FLOAT

    def write(self,file):
        data=struct.pack('<4f', self.x, self.y, self.z, self.w)
        file.write(data)

    def __str__(self):
        return '(%f, %f, %f, %f)' % (self.x, self.y, self.z, self.w)

class _3ds_point_uv(object):
    """Class representing a UV-coordinate for a 3ds file."""
    __slots__ = ("uv", )

    def __init__(self, point):
        self.uv = point

    def get_size(self):
        return 2 * SZ_FLOAT

    def write(self, file):
        data = struct.pack('<2f', self.uv[0], self.uv[1])
        file.write(data)

    def __str__(self):
        return '(%g, %g)' % self.uv

class _3ds_rgb_color(object):
    """Class representing a (24-bit) rgb color for a 3ds file."""
    __slots__ = "r", "g", "b"

    def __init__(self, col):
       self.r, self.g, self.b = col

    def get_size(self):
        return 3

    def write(self, file):
        file.write(struct.pack('<3B', int(255 * self.r), int(255 * self.g), int(255 * self.b)))

    def __str__(self):
        return '{%f, %f, %f}' % (self.r, self.g, self.b)

class _3ds_face(object):
    """Class representing a face for a 3ds file."""
    __slots__ = ("vindex", )

    def __init__(self, vindex):
        self.vindex = vindex

    def get_size(self):
        return 4 * SZ_SHORT

    # no need to validate every face vert. the oversized array will
    # catch this problem

    def write(self, file):
        # The last zero is only used by 3d studio
        file.write(struct.pack("<4H", self.vindex[0], self.vindex[1], self.vindex[2], 0))

    def __str__(self):
        return '[%d %d %d]' % (self.vindex[0], self.vindex[1], self.vindex[2])

class _3ds_array(object):
    """Class representing an array of variables for a 3ds file.

    Consists of a _3ds_ushort to indicate the number of items, followed by the items themselves.
    """
    __slots__ = "values", "size"

    def __init__(self):
        self.values = []
        self.size = SZ_SHORT

    # add an item:
    def add(self, item):
        self.values.append(item)
        self.size += item.get_size()

    def get_size(self):
        return self.size

    def validate(self):
        return len(self.values) <= 65535

    def write(self, file):
        _3ds_ushort(len(self.values)).write(file)
        for value in self.values:
            value.write(file)

    # To not overwhelm the output in a dump, a _3ds_array only
    # outputs the number of items, not all of the actual items.
    def __str__(self):
        return '(%d items)' % len(self.values)

class _3ds_named_variable(object):
    """Convenience class for named variables."""

    __slots__ = "value", "name"

    def __init__(self, name, val=None):
        self.name = name
        self.value = val

    def get_size(self):
        if self.value is None:
            return 0
        else:
            return self.value.get_size()

    def write(self, file):
        if self.value is not None:
            self.value.write(file)

    def dump(self, indent):
        if self.value is not None:
            print(indent * " ",
                  self.name if self.name else "[unnamed]",
                  " = ",
                  self.value)

#the chunk class
class _3ds_chunk(object):
    """Class representing a chunk in a 3ds file.

    Chunks contain zero or more variables, followed by zero or more subchunks.
    """
    __slots__ = "ID", "size", "variables", "subchunks"

    def __init__(self, chunk_id=0):
        self.ID = _3ds_ushort(chunk_id)
        self.size = _3ds_uint(0)
        self.variables = []
        self.subchunks = []

    def add_variable(self, name, var):
        """Add a named variable.

        The name is mostly for debugging purposes."""
        self.variables.append(_3ds_named_variable(name, var))

    def add_subchunk(self, chunk):
        """Add a subchunk."""
        self.subchunks.append(chunk)

    def get_size(self):
        """Calculate the size of the chunk and return it.

        The sizes of the variables and subchunks are used to determine this chunk\'s size."""
        tmpsize = self.ID.get_size() + self.size.get_size()
        for variable in self.variables:
            tmpsize += variable.get_size()
        for subchunk in self.subchunks:
            tmpsize += subchunk.get_size()
        self.size.value = tmpsize
        return self.size.value

    def validate(self):
        for var in self.variables:
            func = getattr(var.value, "validate", None)
            if (func is not None) and not func():
                return False

        for chunk in self.subchunks:
            func = getattr(chunk, "validate", None)
            if (func is not None) and not func():
                return False

        return True

    def write(self, file):
        """Write the chunk to a file.

        Uses the write function of the variables and the subchunks to do the actual work."""
        #write header
        self.ID.write(file)
        self.size.write(file)
        for variable in self.variables:
            variable.write(file)
        for subchunk in self.subchunks:
            subchunk.write(file)

    def dump(self, indent=0):
        """Write the chunk to a file.

        Dump is used for debugging purposes, to dump the contents of a chunk to the standard output.
        Uses the dump function of the named variables and the subchunks to do the actual work."""
        print(indent * " ",
              "ID=%r" % hex(self.ID.value),
              "size=%r" % self.get_size())
        for variable in self.variables:
            variable.dump(indent + 1)
        for subchunk in self.subchunks:
            subchunk.dump(indent + 1)

######################################################
# EXPORT
######################################################

def make_material_subchunk(id, color):
    """Make a material subchunk."""
    """Used for color subchunks, such as diffuse color or ambient color subchunks."""
    mat_sub = _3ds_chunk(id)
    col1 = _3ds_chunk(RGB1)
    col1.add_variable("color1", _3ds_rgb_color(color));
    mat_sub.add_subchunk(col1)
# optional:
    col2 = _3ds_chunk(RGB2)
    col2.add_variable("color2", _3ds_rgb_color(color));
    mat_sub.add_subchunk(col2)
    return mat_sub

def make_percent_subchunk(id, percentval):
    # Make a percentage based subchunk
    pct_sub = _3ds_chunk(id)
    pct1 = _3ds_chunk(PCT)
    pct1.add_variable("percent", _3ds_ushort(int(round(percentval*100,0))))
    pct_sub.add_subchunk(pct1)
    return pct_sub

def make_material_texture_chunk(id, images):
    """ Make Material Map texture chunk """
    # 4KEX: Add texture percentage value (100 = 1.0)
    mat_sub = make_percent_subchunk(id, 1)

    def add_image(img):
        filename = bpy.path.basename(image.filepath)
        mat_sub_file = _3ds_chunk(MATMAPFILE)
        mat_sub_file.add_variable("mapfile", _3ds_string(sane_name(filename)))
        mat_sub.add_subchunk(mat_sub_file)

    for image in images:
        add_image(image)

    return mat_sub

def make_material_chunk(material, image):
    """Make a material chunk out of a blender material."""
    material_chunk = _3ds_chunk(MATERIAL)
    name = _3ds_chunk(MATNAME)

    if material:
        name_str = material.name
    else:
        name_str = 'None'
    # 4KEX: Removed image name adding to material name
    if image:
        name_str += image.name

    name.add_variable("name", _3ds_string(sane_name(name_str)))
    material_chunk.add_subchunk(name)

    if not material:
        material_chunk.add_subchunk(make_material_subchunk(MATAMBIENT, (0,0,0) ))
        material_chunk.add_subchunk(make_material_subchunk(MATDIFFUSE, (.8, .8, .8) ))
        material_chunk.add_subchunk(make_material_subchunk(MATSPECULAR, (1,1,1) ))
        material_chunk.add_subchunk(make_percent_subchunk(MATSHINESS, .2))
        material_chunk.add_subchunk(make_percent_subchunk(MATSHIN2, 1))
        material_chunk.add_subchunk(make_percent_subchunk(MATTRANS, 0))

    else:
        material_chunk.add_subchunk(make_material_subchunk(MATAMBIENT, [a*material.ambient for a in material.diffuse_color] ))
        material_chunk.add_subchunk(make_material_subchunk(MATDIFFUSE, material.diffuse_color))
        material_chunk.add_subchunk(make_material_subchunk(MATSPECULAR, material.specular_color))
        material_chunk.add_subchunk(make_percent_subchunk(MATSHINESS, material.roughness))
        material_chunk.add_subchunk(make_percent_subchunk(MATSHIN2, material.specular_intensity))
        material_chunk.add_subchunk(make_percent_subchunk(MATTRANS, 1-material.alpha))

        # 4KEX: Removed call to get images for the material. Will export UV image ONLY.
        # images = get_material_images(material) # can be None
        images = []

        if image: images.append(image)

        if images:
            material_chunk.add_subchunk(make_material_texture_chunk(MAT_DIFFUSEMAP, images))

    return material_chunk

##### SMOOTH GROUP #############################################################

'''
def msb(x):
    return x.bit_length() - 1

def lsb(x):
    return msb(x & -x)

def has_sharp_edge(f) :
    for e in f.edges :
        if not e.smooth :
            return True

    return False

def not_allowed_mask(f,smg) :
    mask = 0
    for e in f.edges :
        if not e.smooth :
            for l in e.link_faces :
                if f.index != l.index :
                    mask |= l[smg]

    return mask

def set_smooth_group(f,smg,group) :
    f[smg] = group
    for e in f.edges :
        if e.smooth :
            for l in e.link_faces :
                if f.index != l.index :
                    l[smg] = l[smg] | group

def calc_smooth_group(bm) :
    """Calculate smoothing groups"""

    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    # face must have some group, 0 is not allowed here
    smg = bm.faces.layers.int.new("smooth_group_current")

    # assign common group for smooth faces
    for f in bm.faces :    
        if not has_sharp_edge(f) :
            # assign any group
            f[smg] = 1

    for f in bm.faces :
        if has_sharp_edge(f) :
            not_mask = not_allowed_mask(f,smg)
            group = 1 << lsb(0xFFFFFFFF & ~not_mask)
            set_smooth_group(f,smg,group)
'''

# Too slow
def tessface_polygon_index(mesh,tess) :
    for po in mesh.polygons :
        if set(tess.vertices).issubset(po.vertices) :
            return True,po.index
    return False,0
# Faster
def tessface_bmface_index(bm,mesh,tess) :
    # Take any point from tessface and iterate over linked faces of BMVert
    for bv in bm.verts :
        if bv.co == tess.vertices[0] :
            for bf in bv.link_faces :
                if set(tess.vertices).issubset(mesh.polygons[bf.index].vertices) :
                    return True,bf.index
    return False,0
# Fastest
# Use handmade issubset because native set.issubset() stuck for some reason
def issubset(lh, rh):
    for e in lh:
        if e not in rh:
            return False
    return True

def tessface_vert_index(bm,mesh,tess) :
    for bf in bm.verts[tess.vertices[0]].link_faces :
        if issubset(tess.vertices,mesh.polygons[bf.index].vertices) :
            return True,bf.index
    return False,0

################################################################################

class tri_wrapper(object):
    """Class representing a triangle.

    Used when converting faces to triangles"""

    __slots__ = "vertex_index", "mat", "image", "faceuvs", "offset", "group"

    def __init__(self, vindex=(0, 0, 0), mat=None, image=None, faceuvs=None, group=0):
        self.vertex_index = vindex
        self.mat = mat
        self.image = image
        self.faceuvs = faceuvs
        self.offset = [0, 0, 0]  # offset indices
        self.group = group

def extract_triangles(mesh):
    '''Extract triangles from a mesh.

    If the mesh contains quads, they will be split into triangles.'''

    (poly_group,group_count) = mesh.calc_smooth_groups(True)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    '''
    calc_smooth_group(bm)
    # face must have some group, 0 is not allowed here
    smg_cr = bm.faces.layers.int["smooth_group_current"]
    '''

    tri_list = []
    do_uv = mesh.tessface_uv_textures

    if not do_uv:
        face_uv = None

    img = None
    for i, face in enumerate(mesh.tessfaces):
        f_v = face.vertices

        uf = mesh.tessface_uv_textures.active.data[i] if do_uv else None

        if do_uv:
            f_uv = uf.uv
            img = uf.image
            if img: img = img.name

        # find parent polygon for tessface
        # p_found, p_index = tessface_polygon_index(mesh,face)
        # p_found, p_index = tessface_bmface_index(bm,mesh,face)
        p_found, p_index = tessface_vert_index(bm,mesh,face)

        # smooth_group = bm.faces[p_index][smg_cr] if p_found else 0
        smooth_group = poly_group[p_index] if p_found else 0

        if len(f_v)==3:
            new_tri = tri_wrapper((f_v[0], f_v[1], f_v[2]), face.material_index, img)
            if (do_uv): new_tri.faceuvs = uv_key(f_uv[0]), uv_key(f_uv[1]), uv_key(f_uv[2])
            new_tri.group = smooth_group
            tri_list.append(new_tri)

        else: #it's a quad
            new_tri = tri_wrapper((f_v[0], f_v[1], f_v[2]), face.material_index, img)
            new_tri_2 = tri_wrapper((f_v[0], f_v[2], f_v[3]), face.material_index, img)

            if (do_uv):
                new_tri.faceuvs= uv_key(f_uv[0]), uv_key(f_uv[1]), uv_key(f_uv[2])
                new_tri_2.faceuvs= uv_key(f_uv[0]), uv_key(f_uv[2]), uv_key(f_uv[3])
                
            new_tri.group = smooth_group
            new_tri_2.group = smooth_group

            tri_list.append( new_tri )
            tri_list.append( new_tri_2 )
            
    bm.free()

    return tri_list

def remove_face_uv(verts, tri_list):
    """Remove face UV coordinates from a list of triangles.

    Since 3ds files only support one pair of uv coordinates for each vertex, face uv coordinates
    need to be converted to vertex uv coordinates. That means that vertices need to be duplicated when
    there are multiple uv coordinates per vertex."""

    # initialize a list of UniqueLists, one per vertex:
    #uv_list = [UniqueList() for i in xrange(len(verts))]
    unique_uvs = [{} for i in range(len(verts))]

    # for each face uv coordinate, add it to the UniqueList of the vertex
    for tri in tri_list:
        for i in range(3):
            # store the index into the UniqueList for future reference:
            # offset.append(uv_list[tri.vertex_index[i]].add(_3ds_point_uv(tri.faceuvs[i])))

            context_uv_vert = unique_uvs[tri.vertex_index[i]]
            uvkey = tri.faceuvs[i]

            offset_index__uv_3ds = context_uv_vert.get(uvkey)

            if not offset_index__uv_3ds:
                offset_index__uv_3ds = context_uv_vert[uvkey] = len(context_uv_vert), _3ds_point_uv(uvkey)

            tri.offset[i] = offset_index__uv_3ds[0]

    # At this point, each vertex has a UniqueList containing every uv coordinate that is associated with it
    # only once.

    # Now we need to duplicate every vertex as many times as it has uv coordinates and make sure the
    # faces refer to the new face indices:
    vert_index = 0
    vert_array = _3ds_array()
    uv_array = _3ds_array()
    index_list = []
    for i, vert in enumerate(verts):
        index_list.append(vert_index)

        pt = _3ds_point_3d(vert.co)  # reuse, should be ok
        uvmap = [None] * len(unique_uvs[i])
        for ii, uv_3ds in unique_uvs[i].values():
            # add a vertex duplicate to the vertex_array for every uv associated with this vertex:
            vert_array.add(pt)
            # add the uv coordinate to the uv array:
            # This for loop does not give uv's ordered by ii, so we create a new map
            # and add the uv's later
            # uv_array.add(uv_3ds)
            uvmap[ii] = uv_3ds

        # Add the uv's in the correct order
        for uv_3ds in uvmap:
            # add the uv coordinate to the uv array:
            uv_array.add(uv_3ds)

        vert_index += len(unique_uvs[i])

    # Make sure the triangle vertex indices now refer to the new vertex list:
    for tri in tri_list:
        for i in range(3):
            tri.offset[i] += index_list[tri.vertex_index[i]]
        tri.vertex_index = tri.offset

    return vert_array, uv_array, tri_list

def make_faces_chunk(tri_list, mesh, materialDict):
    """Make a chunk for the faces.

    Also adds subchunks assigning materials to all faces."""

    materials = mesh.materials
    if not materials:
        mat = None

    face_chunk = _3ds_chunk(OBJECT_FACES)
    face_list = _3ds_array()

    if mesh.tessface_uv_textures:
        # Gather materials used in this mesh - mat/image pairs
        unique_mats = {}
        for i, tri in enumerate(tri_list):

            face_list.add(_3ds_face(tri.vertex_index))

            if materials:
                mat = materials[tri.mat]
                if mat:
                    mat = mat.name

            img = tri.image

            try:
                context_mat_face_array = unique_mats[mat, img][1]
            except:
                name_str = mat if mat else "None"
                if img:
                    name_str += img

                context_mat_face_array = _3ds_array()
                unique_mats[mat, img] = _3ds_string(sane_name(name_str)), context_mat_face_array

            context_mat_face_array.add(_3ds_ushort(i))
            # obj_material_faces[tri.mat].add(_3ds_ushort(i))

        face_chunk.add_variable("faces", face_list)
        for mat_name, mat_faces in unique_mats.values():
            obj_material_chunk = _3ds_chunk(OBJECT_MATERIAL)
            obj_material_chunk.add_variable("name", mat_name)
            obj_material_chunk.add_variable("face_list", mat_faces)
            face_chunk.add_subchunk(obj_material_chunk)

    else:

        obj_material_faces = []
        obj_material_names = []
        for m in materials:
            if m:
                obj_material_names.append(_3ds_string(sane_name(m.name)))
                obj_material_faces.append(_3ds_array())
        n_materials = len(obj_material_names)

        for i, tri in enumerate(tri_list):
            face_list.add(_3ds_face(tri.vertex_index))
            if (tri.mat < n_materials):
                obj_material_faces[tri.mat].add(_3ds_ushort(i))

        face_chunk.add_variable("faces", face_list)
        for i in range(n_materials):
            obj_material_chunk = _3ds_chunk(OBJECT_MATERIAL)
            obj_material_chunk.add_variable("name", obj_material_names[i])
            obj_material_chunk.add_variable("face_list", obj_material_faces[i])
            face_chunk.add_subchunk(obj_material_chunk)

    smooth_chunk = _3ds_chunk(OBJECT_SMOOTH)
    for i, tri in enumerate(tri_list) :
        smooth_chunk.add_variable("face_" + str(i),_3ds_uint(tri.group))
    face_chunk.add_subchunk(smooth_chunk)

    return face_chunk

def make_vert_chunk(vert_array):
    """Make a vertex chunk out of an array of vertices."""
    vert_chunk = _3ds_chunk(OBJECT_VERTICES)
    vert_chunk.add_variable("vertices", vert_array)
    return vert_chunk

def make_uv_chunk(uv_array):
    """Make a UV chunk out of an array of UVs."""
    uv_chunk = _3ds_chunk(OBJECT_UV)
    uv_chunk.add_variable("uv coords", uv_array)
    return uv_chunk

def make_mesh_chunk(mesh, materialDict, ob, name_to_id, name_to_scale, name_to_pos, name_to_rot):
    '''Make a chunk out of a Blender mesh.'''

    # Extract the triangles from the mesh:
    tri_list = extract_triangles(mesh)

    if mesh.tessface_uv_textures:
        # Remove the face UVs and convert it to vertex UV:
        vert_array, uv_array, tri_list = remove_face_uv(mesh.vertices, tri_list)
    else:
        # Add the vertices to the vertex array:
        vert_array = _3ds_array()
        for vert in mesh.vertices:
            vert_array.add(_3ds_point_3d(vert.co))
        # If the mesh has vertex UVs, create an array of UVs:
        # if mesh.vertexUV:
        #     uv_array = _3ds_array()
        #     for vert in mesh.vertices:
        #         uv_array.add(_3ds_point_uv(vert.uvco))
        # else:
        #     # no UV at all:
        uv_array = None

    # create the chunk:
    mesh_chunk = _3ds_chunk(OBJECT_MESH)

    # add vertex chunk:
    mesh_chunk.add_subchunk(make_vert_chunk(vert_array))
    # add faces chunk:

    mesh_chunk.add_subchunk(make_faces_chunk(tri_list, mesh, materialDict))

    mesh1 = _3ds_chunk(OBJECT_TRANS_MATRIX);

    # 4KEX: 3DS mesh matrix. Apply the worldspace scale and positioning relative to the parent (if any).
    if (ob.parent == None) or (ob.parent.name not in name_to_id):
        matrix_pos = (name_to_pos[ob.name][0],name_to_pos[ob.name][1],name_to_pos[ob.name][2])
        # this was originally
        # matrix_pos = (-name_to_pos[ob.name][0],-name_to_pos[ob.name][1],-name_to_pos[ob.name][2])
        # matrix_pos = (0.0,0.0,0.0)
    else:
        # this code has been left as found, Glauco Bacchi
        matrix_pos = mathutils.Vector((name_to_pos[ob.parent.name][0]-name_to_pos[ob.name][0],name_to_pos[ob.parent.name][1]-name_to_pos[ob.name][1],name_to_pos[ob.parent.name][2]-name_to_pos[ob.name][2])) * name_to_rot[ob.parent.name].to_matrix()

    ob_matrix = mathutils.Matrix()
    ob_matrix.identity()
    ob_matrix.resize_4x4()
    ob_matrix[3][0] = matrix_pos[0]
    ob_matrix[3][1] = matrix_pos[1]
    ob_matrix[3][2] = matrix_pos[2]

    # the original code is below but results in incorrect placement of the object when key frame data not output zzz
    # ob_matrix[0][0] = 1.0/name_to_scale[ob.name][0]
    # ob_matrix[1][1] = 1.0/name_to_scale[ob.name][1]
    # ob_matrix[2][2] = 1.0/name_to_scale[ob.name][2]

    #calculate the componenets of the transformation matrix from the rotation (parents zzz)
    # i think this should have scaling data included but everything works well for tmu as it stands zzz

    oneMinusCos = 1.0-math.cos(name_to_rot[ob.name].angle)
    sinAngle = math.sin(name_to_rot[ob.name].angle)
    cosAngle = math.cos(name_to_rot[ob.name].angle)

    ob_matrix[0][0] = cosAngle + oneMinusCos*(name_to_rot[ob.name].axis[0])*(name_to_rot[ob.name].axis[0])
    ob_matrix[0][1] = oneMinusCos*(name_to_rot[ob.name].axis[1])*(name_to_rot[ob.name].axis[0]) - (name_to_rot[ob.name].axis[2])* sinAngle
    ob_matrix[0][2] = oneMinusCos*(name_to_rot[ob.name].axis[2])*(name_to_rot[ob.name].axis[0]) + (name_to_rot[ob.name].axis[1])* sinAngle

    ob_matrix[1][0] = oneMinusCos*(name_to_rot[ob.name].axis[0])*(name_to_rot[ob.name].axis[1]) + (name_to_rot[ob.name].axis[2])* sinAngle
    ob_matrix[1][1] = cosAngle + oneMinusCos*(name_to_rot[ob.name].axis[1])*(name_to_rot[ob.name].axis[1])
    ob_matrix[1][2] = oneMinusCos*(name_to_rot[ob.name].axis[2])*(name_to_rot[ob.name].axis[1]) - (name_to_rot[ob.name].axis[0])* sinAngle

    ob_matrix[2][0] = oneMinusCos*(name_to_rot[ob.name].axis[0])*(name_to_rot[ob.name].axis[2]) - (name_to_rot[ob.name].axis[1])* sinAngle
    ob_matrix[2][1] = oneMinusCos*(name_to_rot[ob.name].axis[1])*(name_to_rot[ob.name].axis[2]) + (name_to_rot[ob.name].axis[0])* sinAngle
    ob_matrix[2][2] = cosAngle + oneMinusCos*(name_to_rot[ob.name].axis[2])*(name_to_rot[ob.name].axis[2])

    mesh1.add_variable("w1", _3ds_float(ob_matrix[0][0]))
    mesh1.add_variable("w2", _3ds_float(ob_matrix[0][1]))
    mesh1.add_variable("w3", _3ds_float(ob_matrix[0][2]))
    mesh1.add_variable("x1", _3ds_float(ob_matrix[1][0]))
    mesh1.add_variable("x2", _3ds_float(ob_matrix[1][1]))
    mesh1.add_variable("x3", _3ds_float(ob_matrix[1][2]))
    mesh1.add_variable("y1", _3ds_float(ob_matrix[2][0]))
    mesh1.add_variable("y2", _3ds_float(ob_matrix[2][1]))
    mesh1.add_variable("y3", _3ds_float(ob_matrix[2][2]))
    mesh1.add_variable("z1", _3ds_float(ob_matrix[3][0]))
    mesh1.add_variable("z2", _3ds_float(ob_matrix[3][1]))
    mesh1.add_variable("z3", _3ds_float(ob_matrix[3][2]))

    mesh_chunk.add_subchunk(mesh1)

    # if available, add uv chunk:
    if uv_array:
        mesh_chunk.add_subchunk(make_uv_chunk(uv_array))

    return mesh_chunk

# COMMENTED OUT FOR 2.42 RELEASE!! CRASHES 3DS MAX
def make_kfdata(start=0, stop=0, curtime=0, rev=0):
    """Make the basic keyframe data chunk"""
    kfdata = _3ds_chunk(KFDATA)

    kfhdr = _3ds_chunk(KFDATA_KFHDR)
    kfhdr.add_variable("revision", _3ds_ushort(rev))
    # Not really sure what filename is used for, but it seems it is usually used
    # to identify the program that generated the .3ds:
    # 4KEX: Based on observations some sample 3DS files typically used start stop of 100 with curtime = 0
    kfhdr.add_variable("filename", _3ds_string(b'Blender'))
    kfhdr.add_variable("animlen", _3ds_uint(stop - start))

    kfseg = _3ds_chunk(KFDATA_KFSEG)
    kfseg.add_variable("start", _3ds_uint(start))
    kfseg.add_variable("stop", _3ds_uint(stop))

    kfcurtime = _3ds_chunk(KFDATA_KFCURTIME)
    kfcurtime.add_variable("curtime", _3ds_uint(curtime))

    kfdata.add_subchunk(kfhdr)
    kfdata.add_subchunk(kfseg)
    kfdata.add_subchunk(kfcurtime)
    return kfdata

def make_track_chunk(ID, obj, obj_size, obj_pos, obj_rot):
    '''Make a chunk for track data.

    Depending on the ID, this will construct a position, rotation or scale track.'''
    track_chunk = _3ds_chunk(ID)
    track_chunk.add_variable("track_flags", _3ds_ushort())
    track_chunk.add_variable("unknown", _3ds_uint(0))
    track_chunk.add_variable("unknown", _3ds_uint(0))
    track_chunk.add_variable("nkeys", _3ds_uint(1))
    # Next section should be repeated for every keyframe, but for now, animation is not actually supported.
    track_chunk.add_variable("tcb_frame", _3ds_uint(0))
    track_chunk.add_variable("tcb_flags", _3ds_ushort())

    # 4KEX: New method simply inserts the parameter pos/rotation/scale
    if ID==POS_TRACK_TAG:
        # position vector:
        track_chunk.add_variable("position", _3ds_point_3d(obj_pos))
    elif ID==ROT_TRACK_TAG:
        # rotation (angle first [in radians], followed by axis):
        track_chunk.add_variable("rotation", _3ds_point_4d((obj_rot.angle, obj_rot.axis[0], obj_rot.axis[1], obj_rot.axis[2])))
    elif ID==SCL_TRACK_TAG:
        # scale vector:
        track_chunk.add_variable("scale", _3ds_point_3d(obj_size))



    '''
    # 4KEX: Eventually add bounding box. So far has not caused any problems.
    bb = _3ds_chunk(BOUNDBOX)
    bb.add_variable("minx",
    '''

    return track_chunk

def make_kf_obj_node(obj, name_to_id, name_to_scale, name_to_pos, name_to_rot):
    '''Make a node chunk for a Blender object.

    Takes the Blender object as a parameter. Object id's are taken from the dictionary name_to_id.
    Blender Empty objects are converted to dummy nodes.'''

    name = obj.name
    # main object node chunk:
    kf_obj_node = _3ds_chunk(KFDATA_OBJECT_NODE_TAG)
    # chunk for the object id:
    obj_id_chunk = _3ds_chunk(OBJECT_NODE_ID)
    # object id is from the name_to_id dictionary:
    obj_id_chunk.add_variable("node_id", _3ds_ushort(name_to_id[name]))

    # object node header:
    obj_node_header_chunk = _3ds_chunk(OBJECT_NODE_HDR)
    # object name:
    if obj.type == 'Empty' and False:	#Forcing to use the real name for empties 4KEX
        # Empties are called "$$$DUMMY" and use the OBJECT_INSTANCE_NAME chunk
        # for their 3name (see below):
        obj_node_header_chunk.add_variable("name", _3ds_string("$$$DUMMY"))
    else:
        # Add the name:
        obj_node_header_chunk.add_variable("name", _3ds_string(sane_name(name)))
    # Add Flag variables (not sure what they do):
    # 4KEX: Based on observation flags1 is usually 0x0040
    obj_node_header_chunk.add_variable("flags1", _3ds_ushort(0x0040))
    obj_node_header_chunk.add_variable("flags2", _3ds_ushort(0))

    # Check parent-child relationships:
    parent = obj.parent
    if (parent == None) or (parent.name not in name_to_id):
        # If no parent, or the parents name is not in the name_to_id dictionary,
        # parent id becomes -1:
        obj_node_header_chunk.add_variable("parent", _3ds_ushort(-1))
    else:
        # Get the parent's id from the name_to_id dictionary:
        obj_node_header_chunk.add_variable("parent", _3ds_ushort(name_to_id[parent.name]))

    # add subchunks for object id and node header:
    kf_obj_node.add_subchunk(obj_id_chunk)
    kf_obj_node.add_subchunk(obj_node_header_chunk)

    # 4KEX: Add a pivot point at the object centre
    if (parent == None) or (parent.name not in name_to_id):
        pivot_pos = (0.0,0.0,0.0)
        # this was originally as follows, Glauco Bacchi
        # pivot_pos = (name_to_pos[name][0],name_to_pos[name][1],name_to_pos[name][2])
    else:
        pivot_pos = mathutils.Vector(((name_to_pos[name][0]-name_to_pos[parent.name][0]),(name_to_pos[name][1]-name_to_pos[parent.name][1]),(name_to_pos[name][2]-name_to_pos[parent.name][2]))) * name_to_rot[parent.name].to_matrix()
    obj_pivot_chunk = _3ds_chunk(OBJECT_PIVOT)
    obj_pivot_chunk.add_variable("pivot", _3ds_point_3d(pivot_pos))
    kf_obj_node.add_subchunk(obj_pivot_chunk)

    # Empty objects need to have an extra chunk for the instance name:
    if obj.type == 'Empty' and False:	#Will use a real object name for empties for now 4KEX
        obj_instance_name_chunk = _3ds_chunk(OBJECT_INSTANCE_NAME)
        obj_instance_name_chunk.add_variable("name", _3ds_string(sane_name(name)))
        kf_obj_node.add_subchunk(obj_instance_name_chunk)

    # Add track chunks for position, rotation and scale:
    # 4KEX: Compute the position and rotation of the object centre
    # 4KEX: The mesh has already been positioned around the object centre and scaled appropriately
    if (parent == None) or (parent.name not in name_to_id):
        # this was as I found it and works for TMU
        # but means we do not apply any scaling at all, Glauco Bacchi
        obj_size = (1.0,1.0,1.0)
        obj_pos = name_to_pos[name]
        obj_rot = name_to_rot[name]
    else:
        obj_size = (1.0,1.0,1.0)
        obj_pos = mathutils.Vector(((name_to_pos[name][0]-name_to_pos[parent.name][0]),(name_to_pos[name][1]-name_to_pos[parent.name][1]),(name_to_pos[name][2]-name_to_pos[parent.name][2]))) * name_to_rot[parent.name].to_matrix()
        obj_rot = name_to_rot[name].cross(name_to_rot[parent.name].copy().inverted())

    kf_obj_node.add_subchunk(make_track_chunk(SCL_TRACK_TAG, obj, obj_size, obj_pos, obj_rot))
    kf_obj_node.add_subchunk(make_track_chunk(ROT_TRACK_TAG, obj, obj_size, obj_pos, obj_rot))
    kf_obj_node.add_subchunk(make_track_chunk(POS_TRACK_TAG, obj, obj_size, obj_pos, obj_rot))

    return kf_obj_node

def do_export(filename,use_selection=False):

    """Save the Blender scene to a 3ds file."""

    sce = bpy.context.scene

    # Initialize the main chunk (primary):
    primary = _3ds_chunk(PRIMARY)
    # Add version chunk:
    version_chunk = _3ds_chunk(VERSION)
    version_chunk.add_variable("version", _3ds_uint(3))
    primary.add_subchunk(version_chunk)

    # init main object info chunk:
    object_info = _3ds_chunk(OBJECTINFO)

    # COMMENTED OUT FOR 2.42 RELEASE!! CRASHES 3DS MAX
    # 4KEX: Enabled kfdata with changes. Hopefully will not crash 3DS MAX (not tested)
    # init main key frame data chunk:
    kfdata = make_kfdata(0, 100, 0, 1)

    # Make a list of all materials used in the selected meshes (use a dictionary,
    # each material is added once):
    materialDict = {}
    mesh_objects = []

    if use_selection:
        objects = [ob for ob in sce.objects if ob.is_visible(sce) and ob.select]
    else:
        objects = [ob for ob in sce.objects if ob.is_visible(sce)]

    empty_objects = [ ob for ob in objects if ob.type == 'EMPTY' ]

    for ob in objects:
        # get derived objects
        free, derived = bpy_extras.io_utils.create_derived_objects(sce, ob)

        if derived is None:
            continue

        for ob_derived, mat in derived:
            if ob.type not in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'}:
                continue

            try:
                data = ob_derived.to_mesh(sce, True, 'RENDER')
            except:
                data = None

            if data:
                # 4KEX: Removed mesh transformation. Will do this later based on parenting and other factors.
                # so vertices are in local coordinates
                # orig was the next line commented out
                data.transform(mat)
                # data.normal_update()
                mesh_objects.append((ob_derived, data))
                mat_ls = data.materials
                mat_ls_len = len(mat_ls)
                # get material/image tuples.
                if data.tessface_uv_textures:
                    if not mat_ls:
                        mat = mat_name = None

                    for f, uf in zip(data.tessfaces, data.tessface_uv_textures.active.data):
                        if mat_ls:
                            mat_index = f.material_index
                            if mat_index >= mat_ls_len:
                                mat_index = f.material_index = 0
                            mat = mat_ls[mat_index]
                            if mat: mat_name = mat.name
                            else:   mat_name = None
                        # else there alredy set to none

                        img = uf.image
                        if img: img_name = img.name
                        else:   img_name = None

                        materialDict.setdefault((mat_name, img_name), (mat, img))

                else:
                    for mat in mat_ls:
                        if mat: # material may be None so check its not.
                            materialDict.setdefault((mat.name, None), (mat, None) )

                    # Why 0 Why!
                    for f in data.tessfaces:
                        if f.material_index >= mat_ls_len:
                            f.material_index = 0

        if free:
            bpy_extras.io_utils.free_derived_objects(ob)

    # Make material chunks for all materials used in the meshes:
    for mat_and_image in materialDict.values():
        object_info.add_subchunk(make_material_chunk(mat_and_image[0], mat_and_image[1]))

    # 4KEX: Added MASTERSCALE element
    mscale = _3ds_chunk(MASTERSCALE)
    mscale.add_variable("scale", _3ds_float(1))
    object_info.add_subchunk(mscale)

    # Give all objects a unique ID and build a dictionary from object name to object id:
    name_to_id = {}
    name_to_scale = {}
    name_to_pos = {}
    name_to_rot = {}
    for ob, data in mesh_objects:
        name_to_id[ob.name]= len(name_to_id)
        name_to_scale[ob.name] = ob.dimensions
        name_to_pos[ob.name] = ob.location
        name_to_rot[ob.name] = ob.rotation_euler

        # applying toquat() produces angle and axis properties
        # but blender rotates the other way so need to inverse this too
        name_to_rot[ob.name] = name_to_rot[ob.name].to_quaternion().inverted()

    for ob in empty_objects:
        name_to_id[ob.name]= len(name_to_id)
        name_to_scale[ob.name] = ob.dimensions
        name_to_pos[ob.name] = ob.location
        name_to_rot[ob.name] = ob.rotation_euler

        name_to_rot[ob.name] = name_to_rot[ob.name].to_quaternion().inverted()

    # Create object chunks for all meshes:
    i = 0
    for ob, blender_mesh in mesh_objects:
        # create a new object chunk
        object_chunk = _3ds_chunk(OBJECT)

        # set the object name
        object_chunk.add_variable("name", _3ds_string(sane_name(ob.name)))

        # make a mesh chunk out of the mesh:
        object_chunk.add_subchunk(make_mesh_chunk(blender_mesh, materialDict, ob, name_to_id, name_to_scale, name_to_pos, name_to_rot))
        object_info.add_subchunk(object_chunk)

        # 4KEX: export kfdata node
        kfdata.add_subchunk(make_kf_obj_node(ob, name_to_id, name_to_scale, name_to_pos, name_to_rot))
        # blender_mesh.vertices = None
        i+=i

    # Create chunks for all empties:
    # 4KEX: Re-enabled kfdata. Empty objects not tested yet.
    for ob in empty_objects:
        # Empties only require a kf object node:
        kfdata.add_subchunk(make_kf_obj_node(ob, name_to_id, name_to_scale, name_to_pos, name_to_rot))

    # Add main object info chunk to primary chunk:
    primary.add_subchunk(object_info)

    # 4KEX: Export kfdata
    primary.add_subchunk(kfdata)

    # At this point, the chunk hierarchy is completely built.

    # Check the size:
    primary.get_size()
    # Open the file for writing:
    file = open(filename, 'wb')

    # Recursively write the chunks to file:
    primary.write(file)

    # Close the file:
    file.close()

    # Clear name mapping vars, could make locals too
    del name_unique[:]
    name_mapping.clear()

    return True

if __name__ == "__main__":
    do_export("/tmp/tmf_export.3ds")
