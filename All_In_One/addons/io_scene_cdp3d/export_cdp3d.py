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

import struct
import datetime


name_unique = []  # stores str, ascii only
name_mapping = {}  # stores {orig: byte} mapping


def sane_name(name):
    name_fixed = name_mapping.get(name)
    if name_fixed is not None:
        return name_fixed

    # strip non ascii chars
    new_name_clean = new_name = name.encode("ASCII", "replace").decode("ASCII")
    i = 0

    while new_name in name_unique:
        new_name = new_name_clean + ".%.3d" % i
        i += 1

    # note, appending the 'str' version.
    name_unique.append(new_name)
    name_mapping[name] = new_name = new_name.encode("ASCII", "replace")
    return new_name

def uv_key(uv):
    return round(uv[0], 6), round(1.0-uv[1], 6)

# size defines:
SZ_BYTE = 1
SZ_SHORT = 2
SZ_INT = 4
SZ_FLOAT = 4

class _3ds_byte(object):
    """Class representing a byte"""
    __slots__ = ("value", )

    def __init__(self, val=0):
        self.value = val

    def get_size(self):
        return SZ_BYTE

    def write(self, file):
        k = self.value
        file.write(struct.pack("<b", k))

    def __str__(self):
        return str(self.value)


class _3ds_short(object):
    """Class representing a short (2-byte integer)"""
    __slots__ = ("value", )

    def __init__(self, val=0):
        self.value = val

    def get_size(self):
        return SZ_SHORT

    def write(self, file):
        file.write(struct.pack("<h", self.value))

    def __str__(self):
        return str(self.value)



class _3ds_ushort(object):
    """Class representing an unsgined short (2-byte integer)"""
    __slots__ = ("value", )

    def __init__(self, val=0):
        self.value = val

    def get_size(self):
        return SZ_SHORT

    def write(self, file):
        file.write(struct.pack("<H", self.value))

    def __str__(self):
        return str(self.value)


class _3ds_uint(object):
    """Class representing an int (4-byte integer)"""
    __slots__ = ("value", )

    def __init__(self, val):
        self.value = val

    def get_size(self):
        return SZ_INT

    def write(self, file):
        file.write(struct.pack("<I", self.value))

    def __str__(self):
        return str(self.value)


class _3ds_float(object):
    """Class representing a 4-byte IEEE floating point number"""
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
    """Class representing a zero-terminated string"""
    __slots__ = ("value", )

    def __init__(self, val):
        assert(type(val) == bytes)
        self.value = val

    def get_size(self):
        return (len(self.value) + 1)

    def write(self, file):
        binary_format = "<%ds" % (len(self.value) + 1)
        file.write(struct.pack(binary_format, self.value))

    def __str__(self):
        return self.value


class _3ds_stringtag(object):
    """Class representing a zero-terminated string"""
    __slots__ = ("value", )
    def __init__(self, val):
        assert(type(val) == bytes)
        self.value = val

    def get_size(self):
        return (len(self.value))

    def write(self, file):
        binary_format = "<%ds" % (len(self.value))
        file.write(struct.pack(binary_format, self.value))

    def __str__(self):
        return self.value


class _3ds_point_3d(object):
    """Class representing a three-dimensional point"""
    __slots__ = "x", "y", "z"

    def __init__(self, point):
        self.x, self.y, self.z = point

    def get_size(self):
        return 3 * SZ_FLOAT

    def write(self, file):
        file.write(struct.pack('<3f', self.x, self.y, self.z))

    def __str__(self):
        return '(%f, %f, %f)' % (self.x, self.y, self.z)


class _3ds_point_uv(object):
    """Class representing a UV-coordinate"""
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


class _3ds_array(object):
    """Class representing an array of variables

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


class _3ds_bytearray(object):
    """Class representing an array of variables

    Consists of a _3ds_byte to indicate the number of items, followed by the items themselves.
    """
    __slots__ = "values", "size"

    def __init__(self):
        self.values = []
        self.size = SZ_BYTE

    # add an item:
    def add(self, item):
        self.values.append(item)
        self.size += item.get_size()

    def get_size(self):
        return self.size

    def validate(self):
        return len(self.values) <= 255

    def write(self, file):
        _3ds_byte(len(self.values)).write(file)
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
    """Class representing a chunk

    Chunks contain zero or more variables, followed by zero or more subchunks.
    """
    __slots__ = "ID", "size", "variables", "subchunks", "write_size"

    def __init__(self, chunk_id="", write_size = True):
        self.ID = _3ds_stringtag(chunk_id)
        self.size = _3ds_uint(0)
        self.variables = []
        self.subchunks = []
        self.write_size = write_size

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
        tmpsize = 0
        for variable in self.variables:
            tmpsize += variable.get_size()
        for subchunk in self.subchunks:
            tmpsize += subchunk.get_size()
        self.size.value = tmpsize
        return self.size.value + self.ID.get_size() + self.size.get_size()

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
        if (self.write_size): 
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



class _3ds_unnamed_chunk(object):
    """Class representing a chunk, but does not print name or size when written

    Chunks contain zero or more variables, followed by zero or more subchunks.
    """
    __slots__ = "variables", "subchunks"

    def __init__(self, chunk_id=""):
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
        tmpsize = 0
        for variable in self.variables:
            tmpsize += variable.get_size()
        for subchunk in self.subchunks:
            tmpsize += subchunk.get_size()
        return tmpsize

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
        for variable in self.variables:
            variable.write(file)
        for subchunk in self.subchunks:
            subchunk.write(file)

    def dump(self, indent=0):
        """Write the chunk to a file.

        Dump is used for debugging purposes, to dump the contents of a chunk to the standard output.
        Uses the dump function of the named variables and the subchunks to do the actual work."""
        for variable in self.variables:
            variable.dump(indent + 1)
        for subchunk in self.subchunks:
            subchunk.dump(indent + 1)


######################################################
# EXPORT
######################################################

class tri_wrapper(object):
    """Class representing a face."""
    __slots__ = "vertex_index", "mat", "image", "faceuvs", "offset"

    def __init__(self, vindex=(0, 0, 0), mat=None, faceuvs=None):
        self.vertex_index = vindex
        self.mat = mat
        self.faceuvs = faceuvs
        self.offset = [0, 0, 0]


def extract_triangles(mesh, materials_list):
    """Extract triangles from a mesh.

    If the mesh contains quads, they will be split into triangles."""
    tri_list = []
    do_uv = bool(mesh.tessface_uv_textures)

    for mat in materials_list:
        for i, face in enumerate(mesh.tessfaces):
            f_v = face.vertices
            if mesh.materials[face.material_index].name != mat: continue

            uf = mesh.tessface_uv_textures.active.data[i] if do_uv else None

            fmt = 0
            if(do_uv): fmt = face.material_index

            if do_uv:
                f_uv = uf.uv

            if len(f_v) == 3:
                new_tri = tri_wrapper((f_v[0], f_v[1], f_v[2]), fmt)
                if (do_uv):
                    new_tri.faceuvs = uv_key(f_uv[0]), uv_key(f_uv[1]), uv_key(f_uv[2])
                else: new_tri.faceuvs = uv_key((0.0,0.0)), uv_key((1.0,0.0)), uv_key((0.0,1.0))
                tri_list.append(new_tri)

            else:  # it's a quad
                new_tri = tri_wrapper((f_v[0], f_v[1], f_v[2]), fmt)
                new_tri_2 = tri_wrapper((f_v[0], f_v[2], f_v[3]), fmt)

                if (do_uv):
                    new_tri.faceuvs = uv_key(f_uv[0]), uv_key(f_uv[1]), uv_key(f_uv[2])
                    new_tri_2.faceuvs = uv_key(f_uv[0]), uv_key(f_uv[2]), uv_key(f_uv[3])
                else:
                    new_tri.faceuvs = uv_key((0.0,0.0)), uv_key((1.0,0.0)), uv_key((0.0,1.0))
                    new_tri_2.faceuvs = uv_key((0.0,0.0)), uv_key((1.0,0.0)), uv_key((0.0,1.0))

                tri_list.append(new_tri)
                tri_list.append(new_tri_2)

    return tri_list



def save(operator,
         context, filepath="",
         use_selection=True,
         enable_corona=False,
         enable_flares=True,
         enable_environment=True, 
         center_objects_to_origin=False, ):

    import bpy
    import mathutils

    import time
    from bpy_extras.io_utils import create_derived_objects, free_derived_objects

    #get the folder where file will be saved and add a log in that folder
    workingpath = '\\'.join(filepath.split('\\')[0:-1])
    log_file = open(workingpath + "//export-log.txt", 'a')
    # Time the export
    time1 = time.clock()
    date = datetime.datetime.now()

    log_file.write("Started exporting on " + date.strftime("%d-%m-%Y %H:%M:%S") + "\n" + "File path: " + filepath + "\n")

    global_matrix = mathutils.Matrix()

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    # Make a list of all materials used in the selected meshes 
    materials_list = ["colwhite"]
    mesh_objects = []
    lamp_objects = []

    collfound = False
    shadfound = False

    meshes_list = ""

    scene = context.scene

    if use_selection:
        objects = (ob for ob in scene.objects if ob.is_visible(scene) and ob.select)
    else:
        objects = (ob for ob in scene.objects if ob.is_visible(scene))

    for ob in objects:
        free, derived = create_derived_objects(scene, ob)

        if derived is None:
            continue

        for ob_derived, mat in derived:
            if ob.type == 'MESH':
                try:
                    data = ob_derived.to_mesh(scene, True, 'PREVIEW')
                except:
                    data = None

                if "mainshad" in ob.name: shadfound = True
                elif "maincoll" in ob.name: collfound = True

                meshes_list += ob.name + " "

                if data:
                    matrix = global_matrix * mat
                    data.transform(matrix)
                    mesh_objects.append((ob_derived, data, matrix))
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
                                    mat_index = f.mat = 0
                                mat = mat_ls[mat_index]
                                mat_name = None if mat is None else mat.name
                            # else there already set to none

                            if mat_name not in materials_list:
                                materials_list.append(mat_name)

                    else:
                        log_file.write("No UVs found on mesh" + str(ob.name) + ". Using default UVs.\n")
                        for mat in mat_ls:
                            if mat:  # material may be None so check its not.
                                if mat.name not in materials_list:
                                    materials_list.append(mat.name)

                        # Why 0 Why!
                        for f in data.tessfaces:
                            if f.material_index >= mat_ls_len:
                                f.material_index = 0

            if ob.type == 'LAMP':
                lamp_objects.append(ob)


        if free:
            free_derived_objects(ob)


    #write all the meshes list into the log, so we can use it when setting up the carinfo.cca
    log_file.write("Meshes: " + meshes_list + "\n")


    # Initialize the main chunk (primary):
    primary = _3ds_chunk(sane_name("P3D"), write_size = False)

    tex = _3ds_chunk(sane_name("TEX"))
    tex_array = _3ds_bytearray()
    for m in materials_list:
        tex_array.add(_3ds_string(sane_name(m + ".tga")))
    tex.add_variable("textures", tex_array)


    lights = _3ds_chunk(sane_name("LIGHTS"))
    lights_array = _3ds_array()

    for l in lamp_objects:
        lamp = _3ds_unnamed_chunk()
        lamp.add_variable("name", _3ds_string(sane_name(l.name)))
        pos = l.matrix_world.to_translation()
        lamp.add_variable("pos", _3ds_point_3d((pos[0], pos[2], pos[1])))
        lamp.add_variable("range", _3ds_float(l.data.energy))
        lamp.add_variable("color", _3ds_uint(int('%02x%02x%02x' % (int(l.data.color[0]*255), int(l.data.color[1]*255), int(l.data.color[2]*255)), 16)))

        lamp.add_variable("corona", _3ds_byte(int(enable_corona)))
        lamp.add_variable("flares", _3ds_byte(int(enable_flares)))
        lamp.add_variable("environment", _3ds_byte(int(enable_environment)))
        lights_array.add(lamp)

    lights.add_variable("lights", lights_array)


    meshes = _3ds_chunk(sane_name("MESHES"))
    meshes_array = _3ds_array()

    length = 0.0
    height = 0.0
    depth = 0.0

    objcenterx = 0.0
    objcentery = 0.0
    objcenterz = 0.0

    #we have to get the main meshes dimensions before 
    #we save all the other meshes, so we could properly center them if needed
    for ob, blender_mesh, matrix in mesh_objects:
        if ob.name == "main":
            v = blender_mesh.vertices[0].co
            lowx = v[0]
            highx = v[0]
            lowy = v[1]
            highy = v[1]
            lowz = v[2]
            highz = v[2]

            for vert in blender_mesh.vertices:
                pos = vert.co
                if pos[0] < lowx: lowx = pos[0]
                elif pos[0] > highx: highx = pos[0]

                if pos[1] < lowy: lowy = pos[1]
                elif pos[1] > highy: highy = pos[1]

                if pos[2] < lowz: lowz = pos[2]
                elif pos[2] > highz: highz = pos[2]

            length = highx-lowx
            height = highz-lowz
            depth = highy-lowy

            objcenterx = (highx+lowx)/2
            objcentery = (highy+lowy)/2
            objcenterz = (highz+lowz)/2



    for ob, blender_mesh, matrix in mesh_objects:
        submesh = _3ds_chunk(sane_name("SUBMESH"))
        
        # Extract the triangles from the mesh:
        tri_list = extract_triangles(blender_mesh, materials_list)

        material_size = []

        for i in range(len(materials_list)):
            material_size.append(0)

        polys = _3ds_array()
        for tri in tri_list:
            poly = _3ds_unnamed_chunk()

            n = materials_list.index(blender_mesh.materials[tri.mat].name)
            material_size[n] += 1

            poly.add_variable("p1", _3ds_short(tri.vertex_index[0]))
            poly.add_variable("uv1", _3ds_point_uv(tri.faceuvs[0]))

            poly.add_variable("p2", _3ds_short(tri.vertex_index[2]))
            poly.add_variable("uv2", _3ds_point_uv(tri.faceuvs[2]))

            poly.add_variable("p3", _3ds_short(tri.vertex_index[1]))
            poly.add_variable("uv3", _3ds_point_uv(tri.faceuvs[1]))

            polys.add(poly)

        flags = 0

        #if "coll" not in ob.name and "shad" not in ob.name: flags = flags | 2
        if "shad" in ob.name: flags = flags | 4
        elif "coll" in ob.name: flags = flags | 8
        elif "main" in ob.name: 
            flags = flags | 3
            if shadfound == False: 
                flags = flags | 4
                log_file.write("! shadow mesh was not found, using main mesh for shadow.\n")
            if collfound == False: 
                flags = flags | 8
                log_file.write("! collision mesh was not found, using main mesh for collisions.\n")
        else: flags = flags | 2

        #for some reason these are not used?
        """if "det_" in ob.name: flags = flags | 16
        if "gls_" in ob.name: flags = flags | 32
        if "plas_" in ob.name: flags = flags | 64
        if "wood_" in ob.name: flags = flags | 128
        if "metl_" in ob.name: flags = flags | 256
        if "expl_" in ob.name: flags = flags | 256 #????

        if "headl_" in ob.name: flags = flags | 1024
        if "brakel_" in ob.name: flags = flags | 2048"""

        submesh.add_variable("name", _3ds_string(sane_name(ob.name)))
        submesh.add_variable("flags", _3ds_uint(flags))

        v = blender_mesh.vertices[0].co
        lowx = v[0]
        highx = v[0]
        lowy = v[1]
        highy = v[1]
        lowz = v[2]
        highz = v[2]

        vertices = _3ds_array()
        #find dimensions of every mesh
        for vert in blender_mesh.vertices:
            pos = vert.co
            if pos[0] < lowx: lowx = pos[0]
            elif pos[0] > highx: highx = pos[0]

            if pos[1] < lowy: lowy = pos[1]
            elif pos[1] > highy: highy = pos[1]

            if pos[2] < lowz: lowz = pos[2]
            elif pos[2] > highz: highz = pos[2]

        #construct vertices array
        for vert in blender_mesh.vertices:
            pos = vert.co
            if(center_objects_to_origin == True):
                vertices.add(_3ds_point_3d( (pos[0] - (highx+lowx)/2, pos[2] - (highz+lowz)/2, pos[1] - (highy+lowy)/2) ))
            else:
                vertices.add(_3ds_point_3d( (pos[0], pos[2], pos[1]) ))

        #construct mesh positions array
        pos = ob.matrix_world.to_translation()
        if(center_objects_to_origin == True):
            submesh.add_variable("pos", _3ds_point_3d(((highx+lowx)/2 - objcenterx, (highz+lowz)/2 - objcenterz, (highy+lowy)/2 - objcentery)))
        else:
            submesh.add_variable("pos", _3ds_point_3d((pos[0], pos[2], pos[1])))

        #save mesh dimensions
        submesh.add_variable("Length", _3ds_float(highx-lowx))
        submesh.add_variable("Height", _3ds_float(highz-lowz))
        submesh.add_variable("Depth", _3ds_float(highy-lowy))

        s = 0
        for i in range(len(materials_list)):
            submesh.add_variable("texstart", _3ds_short(s))
            submesh.add_variable("numflat", _3ds_short(0))
            submesh.add_variable("numflatmetal", _3ds_short(0))
            submesh.add_variable("gourad", _3ds_short(material_size[i]))
            submesh.add_variable("gouradmetal", _3ds_short(0))
            submesh.add_variable("gouradmetalenv", _3ds_short(0))
            submesh.add_variable("shining", _3ds_short(0))
            s += material_size[i]


        submesh.add_variable("vertices", vertices)
        submesh.add_variable("polygons", polys)


        if submesh.validate():
            meshes_array.add(submesh)
        else:
            operator.report({'WARNING'}, "Object %r can't be written into a 3DS file")

        if not blender_mesh.users:
            bpy.data.meshes.remove(blender_mesh)


    meshes.add_variable("meshes", meshes_array)

    user = _3ds_chunk(sane_name("USER"))
    user.add_variable("userdatasize", _3ds_uint(0))
    user.add_variable("userdata", _3ds_stringtag(sane_name("")))


    primary.add_variable("version", _3ds_byte(2))

    primary.add_variable("Length", _3ds_float(length))
    primary.add_variable("Height", _3ds_float(height))
    primary.add_variable("Depth", _3ds_float(depth))

    primary.add_subchunk(tex)
    primary.add_subchunk(lights)
    primary.add_subchunk(meshes)
    primary.add_subchunk(user)


    
    #calculate all the sizes
    primary.get_size()
    # Open the file for writing:
    file = open(filepath, 'wb')

    # Recursively write the chunks to file:
    primary.write(file)

    # Close the file:
    file.close()

    # Clear name mapping vars, could make locals too
    del name_unique[:]
    name_mapping.clear()

    print("p3d export time: %.2f" % (time.clock() - time1))
    log_file.write("Finished p3d export. Time taken: %.2f \n\n\n" % (time.clock() - time1))
    log_file.close()

    return {'FINISHED'}
