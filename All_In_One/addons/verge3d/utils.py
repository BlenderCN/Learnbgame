# Copyright (c) 2017-2018 Soft8Soft LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import bpy
import numpy as np
import mathutils

ORTHO_EPS = 1e-5
DEFAULT_MAT_NAME = 'v3d_default_material'

selectedObject = None
selectedObjectsSave = []
# 2.79
prevActiveObject = None

def integer_to_bl_suffix(val):

    suf = str(val)

    for i in range(0, 3 - len(suf)):
        suf = '0' + suf

    return suf

def get_world_first_valid_texture_slot(world):

    for blender_texture_slot in world.texture_slots:
        if (blender_texture_slot is not None and
                blender_texture_slot.texture and
                blender_texture_slot.texture.users != 0 and
                (blender_texture_slot.texture.type == 'ENVIRONMENT_MAP'
                or blender_texture_slot.texture.type == 'IMAGE'
                and blender_texture_slot.texture_coords == 'EQUIRECT') and
                get_tex_image(blender_texture_slot.texture) is not None and
                get_tex_image(blender_texture_slot.texture).users != 0 and
                get_tex_image(blender_texture_slot.texture).size[0] > 0 and
                get_tex_image(blender_texture_slot.texture).size[1] > 0):

            return blender_texture_slot

    return None

def isCyclesRender(context):
    # NOTE: temporary, need to rename/refactor in Blender 2.80
    return (context.scene.render.engine == 'CYCLES' or bpy.app.version >= (2,80,0))

def getWorldCyclesEnvTexture(world):

    if world.node_tree is not None and world.use_nodes:
        for bl_node in world.node_tree.nodes:
            if (bl_node.type == 'TEX_ENVIRONMENT' and
                    get_tex_image(bl_node) is not None and
                    get_tex_image(bl_node).users != 0 and
                    get_tex_image(bl_node).size[0] > 0 and
                    get_tex_image(bl_node).size[1] > 0):

                return bl_node

    return None

def getWorldCyclesBkgStrength(world):

    if world.node_tree is not None and world.use_nodes:
        for bl_node in world.node_tree.nodes:
            if bl_node.type == 'BACKGROUND':
                return bl_node.inputs['Strength'].default_value

        return 0
    else:
        return 1

def getWorldCyclesBkgColor(world):

    if world.node_tree is not None and world.use_nodes:
        for bl_node in world.node_tree.nodes:
            if bl_node.type == 'BACKGROUND':
                return bl_node.inputs['Color'].default_value

        return [0, 0, 0]
    else:
        # Blender default grey color
        return [0.041, 0.041, 0.041]

def getLightCyclesStrength(bl_light):
    if bpy.app.version < (2,80,0):
        if bl_light.node_tree is not None and bl_light.use_nodes:
            for bl_node in bl_light.node_tree.nodes:
                if bl_node.type == 'EMISSION':
                    return bl_node.inputs['Strength'].default_value

        # point and spot light have 100 as default strength
        if bl_light.type == 'POINT' or bl_light.type == 'SPOT':
            return 100
        else:
            return 1
    else:
        # point and spot light have 100 as default strength
        if bl_light.type == 'POINT' or bl_light.type == 'SPOT':
            return 100 * bl_light.energy
        else:
            return bl_light.energy


def getLightCyclesColor(bl_light):
    if bl_light.node_tree is not None and bl_light.use_nodes and bpy.app.version < (2,80,0):
        for bl_node in bl_light.node_tree.nodes:
            if bl_node.type == 'EMISSION':
                col = bl_node.inputs['Color'].default_value
                return [col[0], col[1], col[2]]

    col = bl_light.color
    return [col[0], col[1], col[2]]

def setSelectedObject(bl_obj):
    """
    Select object for NLA baking
    """
    global prevActiveObject

    if bpy.app.version < (2,80,0):
        prevActiveObject = bpy.context.object
        bpy.context.scene.objects.active = bl_obj
    else:
        global selectedObject, selectedObjectsSave

        selectedObject = bl_obj
        selectedObjectsSave = bpy.context.selected_objects.copy()

        # NOTE: seems like we need both selection and setting active object
        for o in selectedObjectsSave:
            o.select_set(False)

        prevActiveObject = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = bl_obj

        bl_obj.select_set(True)

def restoreSelectedObjects():
    global prevActiveObject

    if bpy.app.version < (2,80,0):
        bpy.context.scene.objects.active = prevActiveObject
        prevActiveObject = None
    else:
        global selectedObject, selectedObjectsSave

        selectedObject.select_set(False)

        for o in selectedObjectsSave:
            o.select_set(True)

        bpy.context.view_layer.objects.active = prevActiveObject
        prevActiveObject = None

        selectedObject = None
        selectedObjectsSave = []

def get_scene_by_object(obj):

    for scene in bpy.data.scenes:
        index = scene.objects.find(obj.name)
        if index > -1 and scene.objects[index] == obj:
            return scene

    return None

def is_on_exported_layer(obj):

    if bpy.app.version >= (2,80,0):
        return True

    scene = get_scene_by_object(obj)
    if scene is None:
        scene = bpy.context.scene

    for i in range(len(obj.layers)):
        if obj.layers[i] and scene.v3d.export_layers[i]:
            return True

    return False

def is_dupli_obj_visible_in_group(dgroup, dobj):
    """
    Blender version prior to 2.80 only
    """
    for a, b in zip(dobj.layers, dgroup.layers):
        if a and b:
            return True

    return False

def get_tex_image(bl_tex):

    """
    Get texture image from a texture, avoiding AttributeError for textures
    without an image (e.g. a texture of type 'NONE').
    """

    return getattr(bl_tex, 'image', None)

def get_texture_name(bl_texture):
    if (isinstance(bl_texture, (bpy.types.ShaderNodeTexImage,
            bpy.types.ShaderNodeTexEnvironment))):
        tex_name = bl_texture.image.name
    elif (isinstance(bl_texture, (bpy.types.ShaderNodeTexture,
            bpy.types.MaterialTextureSlot, bpy.types.WorldTextureSlot))):
        tex_name = bl_texture.texture.name
    else:
        tex_name = bl_texture.name

    return tex_name

def mat4_is_identity(mat4):
    return mat4 == mathutils.Matrix.Identity(4)

def mat4_is_trs_decomposable(mat4):
    # don't use mathutils.Matrix.is_orthogonal_axis_vectors property, because it
    # doesn't normalize vectors before checking

    mat = mat4.to_3x3().transposed()
    v0 = mat[0].normalized()
    v1 = mat[1].normalized()
    v2 = mat[2].normalized()

    return (abs(v0.dot(v1)) < ORTHO_EPS
            and abs(v0.dot(v2)) < ORTHO_EPS
            and abs(v1.dot(v2)) < ORTHO_EPS)

def mat4_svd_decompose_to_mats(mat4):
    """
    Decompose the given matrix into a couple of TRS-decomposable matrices or
    Returns None in case of an error.
    """

    try:
        u, s, vh = np.linalg.svd(mat4.to_3x3())
        mat_u = mathutils.Matrix(u)
        mat_s = mathutils.Matrix([[s[0], 0, 0], [0, s[1], 0], [0, 0, s[2]]])
        mat_vh = mathutils.Matrix(vh)

        # NOTE: a potential reflection part in U and VH matrices isn't considered
        mat_trans = mathutils.Matrix.Translation(mat4.to_translation())
        if bpy.app.version < (2,80,0):
            mat_left = mat_trans * (mat_u * mat_s).to_4x4()
        else:
            mat_left = mat_trans @ (mat_u @ mat_s).to_4x4()

        return (mat_left, mat_vh.to_4x4())

    except np.linalg.LinAlgError:
        # numpy failed to decompose the matrix
        return None

def find_armature(obj):

    for mod in obj.modifiers:
        if mod.type == 'ARMATURE' and mod.object is not None:
            return mod.object

    # use obj.find_armature as a last resort, because it doesn't work with many
    # armature modifiers
    return obj.find_armature()

def material_has_blend_backside(bl_mat):
    # >= (2,80,0) API
    return (material_is_blend(bl_mat) and (
        # NOTE: compatibility for some pre-beta Blender build
        (hasattr(bl_mat, 'show_transparent_backside') and bl_mat.show_transparent_backside) or
        (hasattr(bl_mat, 'show_transparent_back') and bl_mat.show_transparent_back)))

def material_is_blend(bl_mat):
    # >= (2,80,0) API
    return bl_mat.blend_method in ['BLEND', 'MULTIPLY', 'ADD']

def update_orbit_camera_view(cam_obj, scene):

    target_obj = cam_obj.data.v3d.orbit_target_object

    eye = cam_obj.matrix_world.to_translation()
    target = (cam_obj.data.v3d.orbit_target if target_obj is None
            else target_obj.matrix_world.to_translation())

    quat = get_lookat_aligned_up_matrix(eye, target).to_quaternion()
    quat.rotate(cam_obj.matrix_world.inverted())
    quat.rotate(cam_obj.matrix_basis)

    rot_mode = cam_obj.rotation_mode
    cam_obj.rotation_mode = 'QUATERNION'
    cam_obj.rotation_quaternion = quat
    cam_obj.rotation_mode = rot_mode

    # need to update the camera state (i.e. world matrix) immediately in case of
    # several consecutive UI updates
    scene.update()

def get_lookat_aligned_up_matrix(eye, target):

    """
    This method uses camera axes for building the matrix.
    """

    axis_z = (eye - target).normalized()

    if axis_z.length == 0:
        axis_z = mathutils.Vector((0, -1, 0))

    axis_x = mathutils.Vector((0, 0, 1)).cross(axis_z)

    if axis_x.length == 0:
        axis_x = mathutils.Vector((1, 0, 0))

    axis_y = axis_z.cross(axis_x)

    return mathutils.Matrix([
        axis_x,
        axis_y,
        axis_z,
    ]).transposed()

def obj_data_uses_line_rendering(bl_obj_data):
    line_settings = getattr(getattr(bl_obj_data, 'v3d', None), 'line_rendering_settings', None)
    return bool(line_settings and line_settings.enable)

def getObjectAllCollections(blObj):
    return [coll for coll in bpy.data.collections if blObj in coll.all_objects[:]]
