"""
Name:    layers
Purpose: Provides functions for accessing and modifying layer values.

Description:
These property getters and setters use the bmesh from the global dict that gets
updated by the scene update handler found in init.
Creating bmeshes in the panels is bad practice as it causes unexpected
behavior.

"""

import bpy
import mathutils
from .common import *


def color_from_face(context):
    obj = context.object
    bm = get_edit_bmesh(obj)
    selmode = bpy.context.tool_settings.mesh_select_mode

    # vertex select mode
    if selmode[0]:
        verts = [v for v in bm.verts if v.select]
        if verts:
            col = get_average_vcol0(verts, bm.loops.layers.color.get("Col"))
            context.scene.revolt.vertex_color_picker = col
    # face select mode
    elif selmode[2]:
        faces = [f for f in bm.faces if f.select]
        if faces:
            col = get_average_vcol2(faces, bm.loops.layers.color.get("Col"))
            context.scene.revolt.vertex_color_picker = col

def get_average_vcol0(verts, layer):
    """ Gets the average vertex color of loops all given VERTS """
    len_cols = 0
    r = 0
    g = 0
    b = 0
    for vert in verts:
        cols = [loop[layer] for loop in vert.link_loops]
        r += sum([c[0] for c in cols])
        g += sum([c[1] for c in cols])
        b += sum([c[2] for c in cols])
        len_cols += len(cols)

    return (r / len_cols, g / len_cols, b / len_cols)

def get_average_vcol2(faces, layer):
    """ Gets the average vertex color of all loops of given FACES """
    len_cols = 0
    r = 0
    g = 0
    b = 0
    for face in faces:
        cols = [loop[layer] for loop in face.loops]
        r += sum([c[0] for c in cols])
        g += sum([c[1] for c in cols])
        b += sum([c[2] for c in cols])
        len_cols += len(cols)

    return (r / len_cols, g / len_cols, b / len_cols)


def set_vcol(faces, layer, color):
    for face in faces:
        for loop in face.loops:
            loop[layer][0] = color[0]
            loop[layer][1] = color[1]
            loop[layer][2] = color[2]


def set_vertex_color(context, number):
    eo = bpy.context.edit_object
    bm = dic.setdefault(eo.name, bmesh.from_edit_mesh(eo.data))
    mesh = context.object.data
    selmode = bpy.context.tool_settings.mesh_select_mode
    v_layer = bm.loops.layers.color.active
    if number == -1:
        cpick = context.scene.revolt.vertex_color_picker
        color = mathutils.Color((cpick[0], cpick[1], cpick[2]))
    else:
        color = mathutils.Color((number/100, number/100, number/100))

    # vertex select mode
    if selmode[0]:
        for face in bm.faces:
            for loop in face.loops:
                if loop.vert.select:
                    loop[v_layer][0] = color[0]
                    loop[v_layer][1] = color[1]
                    loop[v_layer][2] = color[2]
                    continue # since multiple select modes can be set
    # edge select mode
    elif selmode[1]:
        for face in bm.faces:
            for i, loop in enumerate(face.loops):
                if loop.edge.select or face.loops[i-1].edge.select:
                    loop[v_layer][0] = color[0]
                    loop[v_layer][1] = color[1]
                    loop[v_layer][2] = color[2]
                    continue
    # face select mode
    elif selmode[2]:
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    loop[v_layer][0] = color[0]
                    loop[v_layer][1] = color[1]
                    loop[v_layer][2] = color[2]

    bmesh.update_edit_mesh(mesh, tessface=False, destructive=False)


def get_face_material(self):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    layer = (bm.faces.layers.int.get("Material") or
             bm.faces.layers.int.new("Material"))

    selected_faces = [face for face in bm.faces if face.select]

    materials_differ = any(
        [face[layer] != selected_faces[0][layer] for face in selected_faces]
    )
    if len(selected_faces) == 0 or materials_differ:
        return -1
    else:
        return selected_faces[0][layer]


def set_face_material(self, value):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    mesh = eo.data
    layer = (bm.faces.layers.int.get("Material") or
             bm.faces.layers.int.new("Material"))
    vc_layer = (bm.loops.layers.color.get("NCPPreview") or
                bm.loops.layers.color.new("NCPPreview"))

    for face in bm.faces:
        if face.select:
            face[layer] = value
            for loop in face.loops:
                loop[vc_layer][0] = COLORS[value][0]
                loop[vc_layer][1] = COLORS[value][1]
                loop[vc_layer][2] = COLORS[value][2]
    bmesh.update_edit_mesh(mesh, tessface=False, destructive=False)
    redraw_3d()


def get_face_texture(self):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    layer = (bm.faces.layers.int.get("Texture Number") or
             bm.faces.layers.int.new("Texture Number"))

    selected_faces = [face for face in bm.faces if face.select]
    textures_differ = any(
        [face[layer] != selected_faces[0][layer] for face in selected_faces]
    )
    if len(selected_faces) == 0:
        return -3
    elif textures_differ:
        return -2
    else:
        return selected_faces[0][layer]


def set_face_texture(self, value):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    layer = (bm.faces.layers.int.get("Texture Number") or
             bm.faces.layers.int.new("Texture Number"))
    for face in bm.faces:
        if face.select:
            face[layer] = value


def set_face_env(self, value):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    env_layer = (bm.loops.layers.color.get("Env") or
                 bm.loops.layers.color.new("Env"))
    env_alpha_layer = (bm.faces.layers.float.get("EnvAlpha") or
                       bm.faces.layers.float.new("EnvAlpha"))
    for face in bm.faces:
        if face.select:
            for loop in face.loops:
                loop[env_layer][0] = value[:3][0]
                loop[env_layer][1] = value[:3][1]
                loop[env_layer][2] = value[:3][2]
            face[env_alpha_layer] = value[-1]
    redraw_3d()


def get_face_env(self):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    env_layer = (bm.loops.layers.color.get("Env")
                 or bm.loops.layers.color.new("Env"))
    env_alpha_layer = (bm.faces.layers.float.get("EnvAlpha")
                       or bm.faces.layers.float.new("EnvAlpha"))

    # Gets the average color for all selected faces
    selected_faces = [face for face in bm.faces if face.select]
    col = get_average_vcol2(selected_faces, env_layer)

    return [*col, selected_faces[0][env_alpha_layer]]


def get_face_property(self):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    layer = bm.faces.layers.int.get("Type") or bm.faces.layers.int.new("Type")
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0:
        return 0
    prop = selected_faces[0][layer]
    for face in selected_faces:
        prop = prop & face[layer]
    return prop


def set_face_property(self, value, mask):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    layer = bm.faces.layers.int.get("Type") or bm.faces.layers.int.new("Type")
    for face in bm.faces:
        if face.select:
            face[layer] = face[layer] | mask if value else face[layer] & ~mask


def get_face_ncp_property(self):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    layer = (bm.faces.layers.int.get("NCPType") or
             bm.faces.layers.int.new("NCPType"))
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0:
        return 0
    prop = selected_faces[0][layer]
    for face in selected_faces:
        prop = prop & face[layer]
    return prop


def set_face_ncp_property(self, value, mask):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    layer = (bm.faces.layers.int.get("NCPType") or
             bm.faces.layers.int.new("NCPType"))
    for face in bm.faces:
        if face.select:
            face[layer] = face[layer] | mask if value else face[layer] & ~mask


def select_faces(context, prop):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    flag_layer = (bm.faces.layers.int.get("Type") or
                  bm.faces.layers.int.new("Type"))

    for face in bm.faces:
        if face[flag_layer] & prop:
            face.select = not face.select
    redraw()


def select_ncp_faces(context, prop):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    flag_layer = (bm.faces.layers.int.get("NCPType") or
                  bm.faces.layers.int.new("NCPType"))

    for face in bm.faces:
        if face[flag_layer] & prop:
            face.select = not face.select
    redraw()


def select_ncp_material(self, context):
    eo = bpy.context.edit_object
    bm = get_edit_bmesh(eo)
    mat = int(self.select_material)

    material_layer = (bm.faces.layers.int.get("Material") or
                      bm.faces.layers.int.new("Material"))
    count = 0
    count_sel = 0
    for face in bm.faces:
        if face[material_layer] == mat:
            count += 1
            if not face.select:
                face.select = True
            else:
                count_sel += 1

    if count == 0:
        msg_box("No {} materials found.".format(MATERIALS[mat+1][1]))
    redraw()
