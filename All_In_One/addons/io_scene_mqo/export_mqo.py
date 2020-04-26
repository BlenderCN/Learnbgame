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

# Script copyright (C) Thomas PORTASSAU (50thomatoes50)
# Contributors: Campbell Barton, Jiri Hnidek, Paolo Ciccone, Thomas Larsson, http://blender.stackexchange.com/users/185/adhi

# <pep8 compliant>
"""
This script exports a Metasequoia(*.mqo) files to Blender.

Usage:
Run this script from "File->Export" menu and then load the desired MQO file.

NO WIKI FOR THE MOMENT
http://wiki.blender.org/index.php/Scripts/Manual/Export/MQO


base source from :
http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Multi-File_packages#Simple_obj_export
"""

import os
import time
import pprint
import bpy
import mathutils
import math
import bpy_extras.io_utils


def export_mqo(op, filepath, objects, rot90, invert, edge, uv_exp, uv_cor, mat_exp, mod_exp, vcol_exp, scale):

        # Exit edit mode before exporting, so current object states are exported properly.
    #if bpy.ops.object.mode_set.poll():
    #    bpy.ops.object.mode_set(mode='OBJECT')

    if objects == None:
        msg = ".mqo export: No MESH objects to export."
        print(msg)
        op.report({'ERROR'}, msg)
        return
    with open(filepath, 'w') as fp:
        fw = fp.write
        msg = ".mqo export: Writing %s" % filepath
        print(msg)
        op.report({'INFO'}, msg)

        fw("Metasequoia Document\nFormat Text Ver 1.0\n\nScene {\n    pos 0.0000 0.0000 1500.0000\n    lookat 0.0000 0.0000 0.0000\n    head -0.5236\n    pich 0.5236\n    bank 0.0000\n    ortho 0\n    zoom2 5.0000\n    amb 0.250 0.250 0.250\n    dirlights 1 {\n        light {\n            dir 0.408 0.408 0.816\n            color 1.000 1.000 1.000\n        }\n    }\n}\n")

        inte_mat = 0
        tmp_mat = []
        obj_tmp = []

        for ob in objects:
            inte_mat, obj_tmp = exp_obj(op, obj_tmp, ob, rot90, invert, edge, uv_exp, uv_cor, scale, mat_exp, inte_mat, tmp_mat, mod_exp, vcol_exp)

        if mat_exp:
            mat_fw(fw, tmp_mat)

        for data in obj_tmp:
            fw(data)

        fw("\nEof\n")
        msg = ".mqo export: Export finished. Created %s" % filepath
        print(msg,"\n")
        op.report({'INFO'}, msg)
    return

def exp_obj(op, fw, ob, rot90, invert, edge, uv_exp, uv_cor, scale, mat_exp, inte_mat, tmp_mat, mod_exp, vcol_exp):
    me = ob.data
    pi = 3.141594
    if mod_exp:
        mod = modif(op, ob.modifiers)
    #fw("Object \"%s\" {\n\tdepth 0\n\tfolding 0\n\tscale %.6f %.6f %.6f\n\trotation %.6f %.6f %.6f\n\ttranslation %.6f %.6f %.6f\n\tvisible 15\n\tlocking 0\n\tshading 1\n\tfacet 59.5\n\tcolor 0.898 0.498 0.698\n\tcolor_type 0\n" % (me.name, scale[0], scale[1], scale[2], 180*rotat.x/pi, 180*rotat.y/pi, 180*rotat.z/pi, loca[0], loca[1], loca[2]))
    fw.append("Object \"%s\" {\n\tdepth 0\n\tfolding 0\n\tscale 1.0 1.0 1.0\n\trotation 1.0 1.0 1.0\n\ttranslation 1.0 1.0 1.0\n\tvisible 15\n\tlocking 0\n\tshading 1\n\tfacet 59.5\n\tcolor 0.898 0.498 0.698\n\tcolor_type 0\n" % (ob.name))
    for mod_fw in mod:
        fw.append(mod_fw)

    msg = ".mqo export: Exporting obj=\"%s\" inte_mat=%i" %(ob.name, inte_mat)
    print(msg)
    op.report({'INFO'}, msg)
    inte_mat_obj = inte_mat
    if mat_exp:
        for mat in me.materials:
            inte_mat = mat_extract(op, mat, tmp_mat, inte_mat)

    me.update(False, True)
    has_vcol = False
    if bool(me.tessface_vertex_colors):
        vcol = me.tessface_vertex_colors.active
        if vcol:
            vcol = vcol.data
            has_vcol = True
    if vcol_exp and has_vcol:
        msg = ".mqo export: exporting vertex colors"
        print(msg)
        op.report({'INFO'}, msg)

    fw.append("\tvertex %i {\n"% (len(me.vertices)))
    e = mathutils.Euler();
    e.rotate_axis('X', math.radians(-90))
    m = e.to_matrix()
    for v in me.vertices:
        if rot90:
            # rotate -90 degrees about X axis
            vv = m*v.co
            fw.append("\t\t%.5f %.5f %.5f\n" % (vv[0]*scale, vv[1]*scale, vv[2]*scale))
        else:
            fw.append("\t\t%.5f %.5f %.5f\n" % (v.co[0]*scale, v.co[1]*scale, v.co[2]*scale))
    fw.append("\t}\n")

    me.update(False, True)
    faces = me.tessfaces
    lostEdges = 0
    for e in me.edges:
        if e.is_loose:
            lostEdges+=1
    if edge:
        fw.append("\tface %i {\n" % (len(faces)+lostEdges))
        for e in me.edges:
            if e.is_loose:
                fw.append("\t\t2 V(%i %i)\n" % (e.vertices[0], e.vertices[1]))
    else:
        fw.append("\tface %i {\n" % (len(faces)))

    me.update(False, True)
    for i, f in enumerate(faces):
        vs = f.vertices
        if len(f.vertices) == 3:
            if invert:
                fw.append("\t\t3 V(%d %d %d)" % (vs[0], vs[2], vs[1]))
            else:
                fw.append("\t\t3 V(%d %d %d)" % (vs[0], vs[1], vs[2]))
        if len(f.vertices) == 4:
            if invert:
                fw.append("\t\t4 V(%d %d %d %d)" % (vs[0], vs[3], vs[2], vs[1]))
            else:
                fw.append("\t\t4 V(%d %d %d %d)" % (vs[0], vs[1], vs[2], vs[3]))

        fw.append(" M(%d)" % (f.material_index+inte_mat_obj))

        try:
            data = me.tessface_uv_textures.active.data[f.index]
            if (uv_exp):
                if not invert:
                    if len(f.vertices) == 3:
                        if uv_cor:
                            fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], 1-data.uv1[1], data.uv2[0], 1-data.uv2[1], data.uv3[0], 1-data.uv3[1]))
                        else:
                            fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], data.uv1[1], data.uv2[0], data.uv2[1], data.uv3[0], data.uv3[1]))
                    if len(f.vertices) == 4:
                        if uv_cor:
                            fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], 1-data.uv1[1], data.uv2[0], 1-data.uv2[1], data.uv3[0], 1-data.uv3[1], data.uv4[0], 1-data.uv4[1]))
                        else:
                            fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], data.uv1[1], data.uv2[0], data.uv2[1], data.uv3[0], data.uv3[1], data.uv4[0], data.uv4[1]))
                else:
                    if len(f.vertices) == 3:
                        if uv_cor:
                            fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], 1-data.uv1[1], data.uv3[0], 1-data.uv3[1], data.uv2[0], 1-data.uv2[1]))
                        else:
                            fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], data.uv1[1], data.uv3[0], data.uv3[1], data.uv2[0], data.uv2[1]))
                    if len(f.vertices) == 4:
                        if uv_cor:
                            fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], 1-data.uv1[1], data.uv4[0], 1-data.uv4[1], data.uv3[0], 1-data.uv3[1], data.uv2[0], 1-data.uv2[1]))
                        else:
                            fw.append(" UV(%.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f)" % (data.uv1[0], data.uv1[1], data.uv4[0], data.uv4[1], data.uv3[0], data.uv3[1], data.uv2[0], data.uv2[1]))

        except AttributeError:
            pass

        if vcol_exp and has_vcol:
            col = vcol[i];
            col = col.color1[:], col.color2[:], col.color3[:], col.color4[:]
            if len(f.vertices) == 3:
                rgba0 = (int(col[0][0]*255)) | (int(col[0][1]*255)<<8) | (int(col[0][2]*255)<<16) | (255<<24)
                rgba1 = (int(col[1][0]*255)) | (int(col[1][1]*255)<<8) | (int(col[1][2]*255)<<16) | (255<<24)
                rgba2 = (int(col[2][0]*255)) | (int(col[2][1]*255)<<8) | (int(col[2][2]*255)<<16) | (255<<24)
                if invert:
                    fw.append(" COL(%d %d %d)" % (rgba0, rgba2, rgba1))
                else:
                    fw.append(" COL(%d %d %d)" % (rgba0, rgba1, rgba2))
            if len(f.vertices) == 4:
                rgba0 = (int(col[0][0]*255)) | (int(col[0][1]*255)<<8) | (int(col[0][2]*255)<<16) | (255<<24)
                rgba1 = (int(col[1][0]*255)) | (int(col[1][1]*255)<<8) | (int(col[1][2]*255)<<16) | (255<<24)
                rgba2 = (int(col[2][0]*255)) | (int(col[2][1]*255)<<8) | (int(col[2][2]*255)<<16) | (255<<24)
                rgba3 = (int(col[3][0]*255)) | (int(col[3][1]*255)<<8) | (int(col[3][2]*255)<<16) | (255<<24)
                if invert:
                    fw.append(" COL(%d %d %d %d)" % (rgba0, rgba3, rgba2, rgba1))
                else:
                    fw.append(" COL(%d %d %d %d)" % (rgba0, rgba1, rgba2, rgba3))

        fw.append("\n")
    fw.append("\t}\n")

    fw.append("}\n")
    return inte_mat, fw


def mat_extract(op, mat, tmp, index):
    #l = "\t\"" + mat.name + "\" " + "col(" + str(mat.diffuse_color[0]) + " " + str(mat.diffuse_color[1]) + " " + str(mat.diffuse_color[2]) + " " + str(mat.alpha) + ")" + " dif(" + str(mat.diffuse_intensity) + ")" + " amb(" + str(mat.ambient) + ")" + " emi(" + str(mat.emit) + ")" + " spc(" + str(mat.specular_intensity) + ")" + " power(5)\n"
    alpha = ''
    diffuse = ''
    msg = ".mqo export: added mat %s / index #%i" % (mat.name,index)
    print(msg)
    op.report({'INFO'}, msg)
    l = "\t\"%s\" col(%.3f %.3f %.3f %.3f) dif(%.3f) amb(%.3f) emi(%.3f) spc(%.3f) power(5) vcol(%d)" % (mat.name, mat.diffuse_color[0], mat.diffuse_color[1], mat.diffuse_color[2], mat.alpha, mat.diffuse_intensity, mat.ambient, mat.emit, mat.specular_intensity, mat.use_vertex_color_paint)
    for tex in mat.texture_slots.values():
        if tex != None:
            if tex.use and tex.texture.type == 'IMAGE' and tex.texture.image != None:
                if tex.use_map_alpha and alpha == '' :
                    if tex.texture.image.filepath.find("//") != -1:
                        alpha = tex.texture.image.name
                    else:
                        alpha = tex.texture.image.filepath
                if tex.use_map_color_diffuse and diffuse == '' :
                    if tex.texture.image.filepath.find("//") != -1:
                        diffuse = tex.texture.image.name
                    else:
                        diffuse = tex.texture.image.filepath
    l = l +  " tex(\"" + diffuse + "\") aplane(\"" + alpha + "\")"

    tmp.append(l+"\n")
    return index + 1


def mat_fw(fw, tmp):
    fw("Material  %d {\n" % (len(tmp)))
    for mat in tmp:
        fw("%s" % (mat))
    fw("}\n")

def modif(op, modifiers):
    tmp = []
    axis = 0
    for mod in modifiers.values():
        if mod.type == "MIRROR":
            msg = ".mqo export: exporting mirror"
            print(msg)
            op.report({'INFO'}, msg)
            if mod.use_mirror_merge:
                tmp.append("\tmirror 2\n\tmirror_dis %.3f\n" % mod.merge_threshold)
            else:
                tmp.append("\tmirror 1\n")
            if mod.use_x:
                axis = 1
            if mod.use_y:
                axis = axis + 2
            if mod.use_z:
                axis = axis + 4
        if mod.type == "SUBSURF":
            msg = ".mqo export: exporting subsurf"
            print(msg)
            op.report({'INFO'}, msg)
            tmp.append("\tpatch 3\n\tpatchtri 0\n\tsegment %i\n" % mod.render_levels)
    return tmp
