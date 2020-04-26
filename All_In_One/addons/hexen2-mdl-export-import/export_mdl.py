# vim:ts=4:et
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

# <pep8 compliant>

import bpy
from bpy_extras.object_utils import object_data_add
from mathutils import Vector,Matrix

from .qfplist import pldata, PListError
from .h2pal import palette
from .h2norm import map_normal
from .mdl import MDL

def check_faces(mesh):
    #Check that all faces are tris because mdl does not support anything else.
    #Because the diagonal on which a quad is split can make a big difference,
    #quad to tri conversion will not be done automatically.
    faces_ok = True
    save_select = []
    for f in mesh.polygons:
        save_select.append(f.select)
        f.select = False
        if len(f.vertices) > 3:
            f.select = True
            faces_ok = False
    if not faces_ok:
        mesh.update()
        return False
    #reset selection to what it was before the check.
    for f, s in map(lambda x, y: (x, y), mesh.polygons, save_select):
        f.select = s
    mesh.update()
    return True

def convert_image(image):
    size = image.size
    skin = MDL.Skin()
    skin.type = 0
    skin.pixels = bytearray(size[0] * size[1]) # preallocate
    cache = {}
    pixels = image.pixels[:]
    for y in range(size[1]):
        for x in range(size[0]):
            outind = y * size[0] + x
            # quake textures are top to bottom, but blender images
            # are bottom to top
            inind = ((size[1] - 1 - y) * size[0] + x) * 4
            rgb = pixels[inind : inind + 3] # ignore alpha
            rgb = tuple(map(lambda x: int(x * 255 + 0.5), rgb))
            if rgb not in cache:
                best = (3*256*256, -1)
                for i, p in enumerate(palette):
                    if i > 255:     # should never happen
                        break
                    r = 0
                    for x in map(lambda a, b: (a - b) ** 2, rgb, p):
                        r += x
                    if r < best[0]:
                        best = (r, i)
                cache[rgb] = best[1]
            skin.pixels[outind] = cache[rgb]
    return skin

def null_skin(size):
    skin = MDL.Skin()
    skin.type = 0
    skin.pixels = bytearray(size[0] * size[1]) # black skin
    return skin

def active_uv(mesh):
    for uvt in mesh.uv_textures:
        if uvt.active:
            return uvt
    return None

def make_skin(mdl, mesh):
    uvt = active_uv(mesh)
    if (not uvt or not uvt.data or not uvt.data[0].image):
        mdl.skinwidth, mdl.skinheight = (4, 4)
        skin = null_skin((mdl.skinwidth, mdl.skinheight))
    else:
        image = uvt.data[0].image
        mdl.skinwidth, mdl.skinheight = image.size
        skin = convert_image(image)
    mdl.skins.append(skin)

def build_tris(mesh):
    # mdl files have a 1:1 relationship between stverts and 3d verts.
    # a bit sucky, but it does allow faces to take less memory
    #
    # modelgen's algorithm for generating UVs is very efficient in that no
    # vertices are duplicated (thanks to the onseam flag), but it can result
    # in fairly nasty UV layouts, and worse: the artist has no control over
    # the layout. However, there seems to be nothing in the mdl format
    # preventing the use of duplicate 3d vertices to allow complete freedom
    # of the UV layout.
    uvtex = active_uv(mesh)
    uvfaces = mesh.uv_layers[uvtex.name].data
    stverts = []
    tris = []
    vertmap = []    # map mdl vert num to blender vert num (for 3d verts)
    vuvdict = {}
    for face in mesh.polygons:
        fv = list(face.vertices)
        uv = uvfaces[face.loop_start:face.loop_start + face.loop_total]
        uv = list(map(lambda a: a.uv, uv))
        face_tris = []
        for i in range(1, len(fv) - 1):
            # blender's and quake's vertex order are opposed
            face_tris.append([(fv[0], tuple(uv[0])),
                              (fv[i + 1], tuple(uv[i + 1])),
                              (fv[i], tuple(uv[i]))])
        for ft in face_tris:
            tv = []
            for vuv in ft:
                if vuv not in vuvdict:
                    vuvdict[vuv] = len(stverts)
                    vertmap.append(vuv[0])
                    stverts.append(vuv[1])
                tv.append(vuvdict[vuv])
            tris.append(MDL.Tri(tv))
    return tris, stverts, vertmap

def convert_stverts(mdl, stverts):
    for i, st in enumerate(stverts):
        s, t = st
        # quake textures are top to bottom, but blender images
        # are bottom to top
        s = int(s * (mdl.skinwidth - 1) + 0.5)
        t = int((1 - t) * (mdl.skinheight - 1) + 0.5)
        # ensure st is within the skin
        s = ((s % mdl.skinwidth) + mdl.skinwidth) % mdl.skinwidth
        t = ((t % mdl.skinheight) + mdl.skinheight) % mdl.skinheight
        stverts[i] = MDL.STVert((s, t))

def make_frame(mesh, vertmap):
    frame = MDL.Frame()
    for v in vertmap:
        mv = mesh.vertices[v]
        vert = MDL.Vert(tuple(mv.co), map_normal(mv.normal))
        frame.add_vert(vert)
    return frame

def scale_verts(mdl):
    tf = MDL.Frame()
    for f in mdl.frames:
        tf.add_frame(f, 0.0)    # let the frame class do the dirty work for us
    size = Vector(tf.maxs) - Vector(tf.mins)
    rsqr = tuple(map(lambda a, b: max(abs(a), abs(b)) ** 2, tf.mins, tf.maxs))
    mdl.boundingradius = (rsqr[0] + rsqr[1] + rsqr[2]) ** 0.5
    mdl.scale_origin = tf.mins
    mdl.scale = tuple(map(lambda x: x / 255.0, size))
    for f in mdl.frames:
        f.scale(mdl)

def calc_average_area(mdl):
    frame = mdl.frames[0]
    if frame.type:
        frame = frame.frames[0]
    totalarea = 0.0
    for tri in mdl.tris:
        verts = tuple(map(lambda i: frame.verts[i], tri.verts))
        a = Vector(verts[0].r) - Vector(verts[1].r)
        b = Vector(verts[2].r) - Vector(verts[1].r)
        c = a.cross(b)
        totalarea += (c * c) ** 0.5 / 2.0
    return totalarea / len(mdl.tris)

def get_properties(operator, mdl, obj):
    mdl.eyeposition = tuple(obj.qfmdl.eyeposition)
    mdl.synctype = MDL.SYNCTYPE[obj.qfmdl.synctype]
    mdl.flags = ((obj.qfmdl.rotate and MDL.EF_ROTATE or 0)
                 | MDL.EFFECTS[obj.qfmdl.effects])
    if obj.qfmdl.md16:
        mdl.ident = "MD16"
    script = obj.qfmdl.script
    mdl.script = None
    if script:
        try:
            script = bpy.data.texts[script].as_string()
        except KeyError:
            operator.report({'ERROR'},
                            "Script '%s' not found." % script)
            return False
        pl = pldata(script)
        try:
            mdl.script = pl.parse()
        except PListError as err:
            operator.report({'ERROR'}, "Script error: %s." % err)
            return False
    return True

def process_skin(mdl, skin, ingroup=False):
    if 'skins' in skin:
        if ingroup:
            raise ValueError("nested skin group")
        intervals=['0.0']
        if 'intervals' in skin:
            intervals += list(skin['intervals'])
        intervals = list(map(lambda x: float(x), intervals))
        while len(intervals) < len(skin['skins']):
            intervals.append(intervals[-1] + 0.1)
        sk = MDL.Skin()
        sk.type = 1
        sk.times = intervals[1:len(skin['skins']) + 1]
        sk.skins = []
        for s in skin['skins']:
            sk.skins.append(process_skin(mdl, s, True))
        return sk
    else:
        #FIXME error handling
        name = skin['name']
        image = bpy.data.images[name]
        if hasattr(mdl, 'skinwidth'):
            if (mdl.skinwidth != image.size[0]
                or mdl.skinheight != image.size[1]):
                raise ValueError("%s: different skin size (%d %d) (%d %d)"
                                 % (name, mdl.skinwidth, mdl.skinheight,
                                    int(image.size[0]), int(image.size[1])))
        else:
            mdl.skinwidth, mdl.skinheight = image.size
        sk = convert_image(image)
        return sk

def process_frame(mdl, scene, frame, vertmap, ingroup = False,
                  frameno = None, name = 'frame'):
    sc = bpy.context.scene
    if frameno == None:
        frameno = scene.frame_current + scene.frame_subframe
    if 'frameno' in frame:
        frameno = float(frame['frameno'])
    if 'name' in frame:
        name = frame['name']
    if 'frames' in frame:
        if ingroup:
            raise ValueError("nested frames group")
        intervals=['0.0']
        if 'intervals' in frame:
            intervals += list(frame['intervals'])
        intervals = list(map(lambda x: float(x), intervals))
        while len(intervals) < len(frame['frames']) + 1:
            intervals.append(intervals[-1] + 0.1)
        fr = MDL.Frame()
        for i, f in enumerate(frame['frames']):
            fr.add_frame(process_frame(mdl, scene, f, vertmap, True,
                                       frameno + i, name + str(i + 1)),
                         intervals[i + 1])
        if 'intervals' in frame:
            return fr
        mdl.frames += fr.frames[:-1]
        return fr.frames[-1]
    scene.frame_set(int(frameno), frameno - int(frameno))
    mesh = mdl.obj.to_mesh(scene, True, 'PREVIEW') #wysiwyg?
    if mdl.obj.qfmdl.xform:
        mesh.transform(mdl.obj.matrix_world)
    fr = make_frame(mesh, vertmap)
    fr.name = name
    return fr

def export_mdl(operator, context, filepath):
    obj = context.active_object
    mesh = obj.to_mesh(context.scene, True, 'PREVIEW') #wysiwyg?
    #if not check_faces(mesh):
    #    operator.report({'ERROR'},
    #                    "Mesh has faces with more than 3 vertices.")
    #    return {'CANCELLED'}
    mdl = MDL(obj.name)
    mdl.obj = obj
    if not get_properties(operator, mdl, obj):
        return {'CANCELLED'}
    mdl.tris, mdl.stverts, vertmap = build_tris(mesh)
    if mdl.script:
        if 'skins' in mdl.script:
            for skin in mdl.script['skins']:
                mdl.skins.append(process_skin(mdl, skin))
        if 'frames' in mdl.script:
            for frame in mdl.script['frames']:
                mdl.frames.append(process_frame(mdl, context.scene, frame,
                                                vertmap))
    if not mdl.skins:
        make_skin(mdl, mesh)
    if not mdl.frames:
        curframe = context.scene.frame_current
        for fno in range(1, curframe + 1):
            context.scene.frame_set(fno)
            mesh = obj.to_mesh(context.scene, True, 'PREVIEW') #wysiwyg?
            if mdl.obj.qfmdl.xform:
                mesh.transform(mdl.obj.matrix_world)
            mdl.frames.append(make_frame(mesh, vertmap))
    convert_stverts(mdl, mdl.stverts)
    mdl.size = calc_average_area(mdl)
    scale_verts(mdl)
    mdl.write(filepath)
    return {'FINISHED'}
