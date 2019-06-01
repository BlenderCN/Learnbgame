# ##### BEGIN MIT LICENSE BLOCK #####
# MIT License
# 
# Copyright (c) 2018 Insma Software
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ##### END MIT LICENSE BLOCK #####

# ----------------------------------------------------------
# Author: Maciej Klemarczyk (mklemarczyk)
# ----------------------------------------------------------

import bpy
from math import sin, cos, radians
from mathutils import Vector, Matrix, Euler
from os import path
import json

debug_level = 3

# --------------------------------------------------------------------
# Writes text to the log
# --------------------------------------------------------------------
def log_write(level, text_to_write):
    l = 0
    levels = {"INFO":0, "DEBUG":1, "WARNING":2, "ERROR":3, "CRITICAL":4, }
    if level in levels:
        l = levels[level]        
    if l >= debug_level:
        print(level +": " + text_to_write)

# --------------------------------------------------------------------
# Set normals
# True = faces to inside
# --------------------------------------------------------------------
def set_normals(myobject, direction=False):
    bpy.context.scene.objects.active = myobject
    # go edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    # select all faces
    bpy.ops.mesh.select_all(action='SELECT')
    # recalculate outside normals
    bpy.ops.mesh.normals_make_consistent(inside=direction)
    # go object mode again
    bpy.ops.object.editmode_toggle()

# --------------------------------------------------------------------
# Set shade smooth
# --------------------------------------------------------------------
def set_smooth(myobject):
    # deactivate others
    for o in bpy.data.objects:
        if o.select is True:
            o.select = False

    myobject.select = True
    bpy.context.scene.objects.active = myobject
    if bpy.context.scene.objects.active.name == myobject.name:
        bpy.ops.object.shade_smooth()

# --------------------------------------------------------------------
# Remove doubles
# --------------------------------------------------------------------
def remove_doubles(myobject):
    bpy.context.scene.objects.active = myobject
    # go edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    # select all faces
    bpy.ops.mesh.select_all(action='SELECT')
    # remove
    bpy.ops.mesh.remove_doubles()
    # go object mode again
    bpy.ops.object.editmode_toggle()

# --------------------------------------------------------------------
# Adds material, creates new if material not exists
# --------------------------------------------------------------------
def set_material(ob, matname, index = 0):
    # Get material
    mat = bpy.data.materials.get(matname)
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name=matname)
    # Assign it to object
    if ob.data.materials:
        # assign to (index) material slot
        ob.data.materials[index] = mat
    else:
        # no slots
        ob.data.materials.append(mat)
    return mat

# --------------------------------------------------------------------
# Adds armature modifier
# --------------------------------------------------------------------
def set_modifier_armature(myobject, armatureobject, modname = "Armature ArchLib"):
    modid = myobject.modifiers.find(modname)
    if (modid == -1):
        mod = myobject.modifiers.new(name=modname, type="ARMATURE")
    else:
        mod = myobject.modifiers[modname]
    mod.object = armatureobject

# --------------------------------------------------------------------
# Adds array modifier
# --------------------------------------------------------------------
def set_modifier_array(myobject, relativeoffset = (1.0, 0.0, 0.0), count = 2, modname = "Array ArchLib"):
    modid = myobject.modifiers.find(modname)
    if (modid == -1):
        mod = myobject.modifiers.new(name=modname, type="ARRAY")
    else:
        mod = myobject.modifiers[modname]
    mod.relative_offset_displace = relativeoffset
    mod.count = count

# --------------------------------------------------------------------
# Adds solidify modifier
# --------------------------------------------------------------------
def set_modifier_solidify(myobject, width = 0.01, modname = "Solidify ArchLib"):
    modid = myobject.modifiers.find(modname)
    if (modid == -1):
        mod = myobject.modifiers.new(name=modname, type="SOLIDIFY")
    else:
        mod = myobject.modifiers[modname]
    mod.thickness = width
    mod.offset = 0
    mod.use_even_offset = True
    mod.use_quality_normals = True

# --------------------------------------------------------------------
# Adds subdivision modifier
# --------------------------------------------------------------------
def set_modifier_subsurf(myobject, levels = 1, renderlevels = 2, modname = "Subsurf ArchLib"):
    modid = myobject.modifiers.find(modname)
    if (modid == -1):
        mod = myobject.modifiers.new(name=modname, type="SUBSURF")
    else:
        mod = myobject.modifiers[modname]
    mod.levels = levels
    mod.render_levels = renderlevels

# --------------------------------------------------------------------
# Rotates a point in 2D space with specified angle
# --------------------------------------------------------------------
def rotate_point2d(posx, posy, angle):
    v1 = Vector([posx, posy])
    rada1 = radians(angle)
    cosa1 = cos(rada1)
    sina1 = sin(rada1)
    mat1 = Matrix([[cosa1, -sina1],
                    [sina1, cosa1]])
    v2 = mat1 * v1
    return v2

# --------------------------------------------------------------------
# Rotates a point in 3D space with specified angle in deg
# --------------------------------------------------------------------
def rotate_point3d(pos, anglex=0.0, angley=0.0, anglez=0.0):
    return rotate_point3d_rad(
        pos,
        anglex=radians(anglex),
        angley=radians(angley),
        anglez=radians(anglez)
    )

# --------------------------------------------------------------------
# Rotates a point in 3D space with specified angle in radians
# --------------------------------------------------------------------
def rotate_point3d_rad(pos, anglex=0.0, angley=0.0, anglez=0.0):
    genvector = Vector(pos)
    myEuler = Euler((anglex, angley, anglez),'XYZ')
    genvector.rotate(myEuler)
    return genvector

# --------------------------------------------------------------------
# Rotates a point in 2D space with specified angle
# --------------------------------------------------------------------
def slide_point3d(startpoint, endpoint, scale):
    v1 = Vector(startpoint)
    v2 = Vector(endpoint)
    return v2 + (v1 - v2) * scale

# -----------------------------------------------------
# Truncate circle ngon mesh
# -----------------------------------------------------
def truncate_circle_mesh(verts, faces, trunc_val):
    myverts = []
    vertnum = len(verts)
    tscal = 0.5 * trunc_val
    for t in range(vertnum):
        pprev = verts[(t+vertnum-1) % vertnum]
        p1 = verts[t]
        pnext = verts[(t+1) % vertnum]
        v1 = slide_point3d(pprev, p1, tscal)
        v2 = slide_point3d(pnext, p1, tscal)
        myverts.append((v1))
        myverts.append((v2))
    myfaces = [list(range(len(myverts)))]
    return myverts, myfaces

# -----------------------------------------------------
# Subdivide ico sphere mesh
# -----------------------------------------------------
def subdivide_icosphere_mesh(verts, faces, radius):
    myverts = verts
    myfaces = []
    vertnum = len(faces)
    for f in faces:
        laste = f[-1]
        newface = []
        for ts in range(len(f)):
            v1 = slide_point3d(verts[laste], verts[f[ts]], 0.5)
            v1.normalize()
            v1 = v1 * radius
            newface.append(len(myverts))
            myverts.append(v1)
            laste = f[ts]
        myfaces.append((newface[0], newface[1], newface[2]))
        myfaces.append((newface[0], newface[1], f[0]))
        myfaces.append((newface[1], newface[2], f[1]))
        myfaces.append((newface[2], newface[0], f[2]))
    return myverts, myfaces

# --------------------------------------------------------------------
# Gets mesh data from json file
# --------------------------------------------------------------------
def load_mesh_data_from_library(meshname):
    meshlibrary = load_meshlibrary_data()
    return meshlibrary['Meshes'][meshname]

# --------------------------------------------------------------------
# Loads meshes json file
# --------------------------------------------------------------------
def load_meshlibrary_data():
    json_data = None
    library_path = get_meshlibrary_path()
    with open(library_path, 'r') as f:
        json_data = json.load(f)
    return json_data

# --------------------------------------------------------------------
# Gets mesh library file path
# --------------------------------------------------------------------
def get_meshlibrary_path():
    data_path = get_data_path()
    if data_path:
        return path.join(data_path, "meshes.json")
    else:
        log_write("CRITICAL", "Mesh library not found. Please check your Blender addons directory.")
        return None

# --------------------------------------------------------------------
# Gets addon data dir path
# --------------------------------------------------------------------
def get_data_path():
    addon_directory = path.dirname(path.realpath(__file__))
    data_dir = path.join(addon_directory, "data")
    log_write("INFO", "Looking for the retarget data in the folder {0}...".format(reduce_path(data_dir)))
    if path.isdir(data_dir):
        return data_dir
    else:
        log_write("CRITICAL", "Tools data not found. Please check your Blender addons directory.")
        return None

# --------------------------------------------------------------------
# Return the last part of long paths
# --------------------------------------------------------------------
def reduce_path(input_path, use_basename = True, max_len=50):
    if use_basename == True:
        return path.basename(input_path)
    else:
        if len(input_path) > max_len:
            return("[Trunked].."+input_path[len(input_path)-max_len:])
        else:
            return input_path


# --------------------------------------------------------------------
# Extracts vertices from selected object
# --------------------------------------------------------------------
def extract_vertices():
    print("".join(["[", ",".join(str(v.co).replace("<Vector ", "").replace(">", "") for v in bpy.context.object.data.vertices), "]"]))

# --------------------------------------------------------------------
# Extracts edges from selected object
# --------------------------------------------------------------------
def extract_edges():
    print("".join(["[(", "),(".join(",".join(str(v) for v in e.vertices) for e in bpy.context.object.data.edges), ")]"]))

# --------------------------------------------------------------------
# Extracts faces from selected object
# --------------------------------------------------------------------
def extract_faces():
    print("".join(["[(", "),(".join(",".join(str(v) for v in p.vertices) for p in bpy.context.object.data.polygons), ")]"]))
