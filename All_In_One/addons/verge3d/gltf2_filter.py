# Copyright (c) 2017 The Khronos Group Inc.
# Modifications Copyright (c) 2017-2018 Soft8Soft LLC
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

#
# Imports
#

from string import Template

import bpy

from .gltf2_get import *
from .gltf2_extract import *
from .node_material_wrapper import NodeMaterialWrapper
from .utils import *

#
# Globals
#

TO_MESH_SOURCE_CUSTOM_PROP = "v3d_to_mesh_source_object"
WORLD_NODE_MAT_NAME = Template('Verge3D_Environment_${name}')

#
# Functions
#

def flatten_collection_unique(collection, dest_set):

    for bl_obj in collection.all_objects:

        is_unique = bl_obj not in dest_set
        dest_set.add(bl_obj)

        if bl_obj.instance_type == 'COLLECTION' and bl_obj.instance_collection != None:
            # prevent possible infinite recursion for collections
            if is_unique:
                flatten_collection_unique(bl_obj.instance_collection, dest_set)

def filter_apply(export_settings):
    """
    Gathers and filters the objects and assets to export.
    Also filters out invalid, deleted and not exportable elements.
    """

    if bpy.app.version < (2,80,0):
        filtered_objects_shallow = []
        filtered_objects_with_dg = []

        for bl_obj in bpy.data.objects:

            if bl_obj.users == 0:
                continue

            if not is_on_exported_layer(bl_obj):
                continue

            filtered_objects_shallow.append(bl_obj)

            # handle instance collections / dupli groups
            if bl_obj not in filtered_objects_with_dg:
                filtered_objects_with_dg.append(bl_obj)

            if bl_obj.dupli_type == 'GROUP' and bl_obj.dupli_group != None:
                for blender_dupli_object in bl_obj.dupli_group.objects:

                    if not is_dupli_obj_visible_in_group(bl_obj.dupli_group,
                            blender_dupli_object):
                        continue

                    if blender_dupli_object not in filtered_objects_with_dg:
                        filtered_objects_with_dg.append(blender_dupli_object)
    else:
        filtered_objects_shallow = set()
        filtered_objects_with_dg = set()
        for bl_scene in bpy.data.scenes:
            filtered_objects_shallow.update(bl_scene.objects)
            flatten_collection_unique(bl_scene.collection, filtered_objects_with_dg)

        def collExpFilter(obj):
            return all(coll.v3d.enable_export for coll in getObjectAllCollections(obj))

        filtered_objects_shallow = list(filter(collExpFilter, filtered_objects_shallow))
        filtered_objects_with_dg = list(filter(collExpFilter, filtered_objects_with_dg))

    export_settings['filtered_objects_shallow'] = filtered_objects_shallow
    export_settings['filtered_objects_with_dg'] = filtered_objects_with_dg

    # Meshes

    filtered_meshes = []
    filtered_vertex_groups = {}
    temporary_meshes = []

    for blender_mesh in bpy.data.meshes:

        if blender_mesh.users == 0:
            continue

        current_blender_mesh = blender_mesh

        current_blender_object = None

        skip = True

        for blender_object in filtered_objects_with_dg:

            current_blender_object = blender_object

            if current_blender_object.type != 'MESH':
                continue

            if current_blender_object.data == current_blender_mesh:

                skip = False

                use_auto_smooth = current_blender_mesh.use_auto_smooth
                if use_auto_smooth and current_blender_mesh.shape_keys is not None:
                    use_auto_smooth = False

                    printLog('WARNING', 'Auto smooth and shape keys cannot'
                            + ' be exported in parallel. Falling back to non auto smooth.')

                need_triangulation = False
                if current_blender_mesh.uv_layers.active and len(current_blender_mesh.uv_layers) > 0:
                    for poly in current_blender_mesh.polygons:
                        # tangents can only be calculated for tris/quads
                        # (later via mesh.calc_tangents())
                        if poly.loop_total > 4:
                            need_triangulation = True

                got_modifiers = False
                for mod in current_blender_object.modifiers:
                    if mod.show_render:
                        got_modifiers = True

                if (got_modifiers and export_settings['gltf_bake_modifiers']) or use_auto_smooth or need_triangulation:

                    copy_obj = current_blender_object.copy()

                    # don't apply the ARMATURE modifier, which is always
                    # used for a skinned mesh
                    for mod in copy_obj.modifiers:
                        if mod.type == 'ARMATURE':
                            copy_obj.modifiers.remove(mod)

                    if use_auto_smooth and not export_settings['gltf_bake_modifiers']:
                        copy_obj.modifiers.clear()

                    if use_auto_smooth:
                        blender_modifier = copy_obj.modifiers.new('Temporary_Auto_Smooth', 'EDGE_SPLIT')

                        blender_modifier.split_angle = current_blender_mesh.auto_smooth_angle
                        blender_modifier.use_edge_angle = current_blender_mesh.has_custom_normals == False

                    if need_triangulation:
                        blender_modifier = copy_obj.modifiers.new('Temporary_Triangulation', 'TRIANGULATE')
                        # seems to produce smoother results
                        blender_modifier.ngon_method = 'CLIP'

                    if bpy.app.version < (2,80,0):
                        current_blender_mesh = copy_obj.to_mesh(bpy.context.scene, True, 'PREVIEW', calc_tessface=True)
                    else:
                        # NOTE: link copy_obj and update the view layer to make
                        # the depsgraph able to apply modifiers to the object
                        dg = bpy.context.depsgraph
                        dg.scene.collection.objects.link(copy_obj)
                        copy_obj.update_tag()
                        bpy.context.view_layer.update()
                        current_blender_mesh = copy_obj.to_mesh(dg, apply_modifiers=True)
                        dg.scene.collection.objects.unlink(copy_obj)

                    if current_blender_mesh is not None:
                        current_blender_mesh[TO_MESH_SOURCE_CUSTOM_PROP] = current_blender_object
                        temporary_meshes.append(current_blender_mesh)
                    else:
                        skip = True

                    bpy.data.objects.remove(copy_obj)

                break

        if skip:
            continue

        filtered_meshes.append(current_blender_mesh)
        filtered_vertex_groups[getPtr(blender_mesh)] = current_blender_object.vertex_groups

    # CURVES (as well as surfaces and texts)

    filtered_curves = []

    for bl_curve in bpy.data.curves:

        if bl_curve.users == 0:
            continue

        # supported curve
        if isinstance(bl_curve, bpy.types.TextCurve) and not export_settings['gltf_bake_text']:
            filtered_curves.append(bl_curve)

        # convert to mesh
        else:
            current_blender_curve = bl_curve
            current_blender_mesh = None
            current_blender_object = None

            skip = True

            for blender_object in filtered_objects_with_dg:

                current_blender_object = blender_object

                if current_blender_object.type not in ['CURVE', 'SURFACE', 'FONT']:
                    continue

                if current_blender_object.data == current_blender_curve:

                    skip = False

                    copy_obj = current_blender_object.copy()

                    if not export_settings['gltf_bake_modifiers']:
                        copy_obj.modifiers.clear()

                    if bpy.app.version < (2,80,0):
                        current_blender_mesh = copy_obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
                    else:
                        current_blender_mesh = copy_obj.to_mesh(bpy.context.depsgraph, True)
                    if current_blender_mesh is not None:
                        current_blender_mesh.name = bl_curve.name
                        current_blender_mesh[TO_MESH_SOURCE_CUSTOM_PROP] = current_blender_object
                        temporary_meshes.append(current_blender_mesh)
                    else:
                        skip = True

                    bpy.data.objects.remove(copy_obj)

                    break

            if skip:
                continue

            filtered_meshes.append(current_blender_mesh)
            filtered_vertex_groups[getPtr(bl_curve)] = current_blender_object.vertex_groups


    export_settings['filtered_curves'] = filtered_curves
    export_settings['filtered_meshes'] = filtered_meshes
    export_settings['filtered_vertex_groups'] = filtered_vertex_groups
    export_settings['temporary_meshes'] = temporary_meshes

    # MATERIALS

    filtered_materials = []
    temporary_materials = []

    for blender_material in get_used_materials():

        if blender_material.users == 0:
            continue

        for blender_mesh in filtered_meshes:
            for mat in blender_mesh.materials:
                if mat == blender_material and mat not in filtered_materials:
                    filtered_materials.append(mat)

        for blender_object in filtered_objects_with_dg:
            if blender_object.material_slots:
                for blender_material_slot in blender_object.material_slots:
                    if blender_material_slot.link == 'DATA':
                        continue

                    mat = blender_material_slot.material
                    if mat == blender_material and mat not in filtered_materials:
                        filtered_materials.append(mat)

        for bl_curve in filtered_curves:
            for mat in bl_curve.materials:
                if mat == blender_material and mat not in filtered_materials:
                    filtered_materials.append(mat)

    curr_world = bpy.context.scene.world
    if export_settings['gltf_format'] != 'FB' and curr_world is not None:

        world_mat = bpy.data.materials.new(WORLD_NODE_MAT_NAME.substitute(
                name=curr_world.name))
        world_mat.use_nodes = True

        world_mat_wrapper = NodeMaterialWrapper(world_mat)

        if isCyclesRender(bpy.context) and curr_world.use_nodes:
            mat_node_tree = curr_world.node_tree.copy()
        else:
            mat_node_tree = world_mat.node_tree.copy()
            mat_node_tree.nodes.clear()

            bkg_node = mat_node_tree.nodes.new('ShaderNodeBackground')
            if bpy.app.version < (2,80,0):
                bkg_node.inputs['Color'].default_value[0] = curr_world.horizon_color[0]
                bkg_node.inputs['Color'].default_value[1] = curr_world.horizon_color[1]
                bkg_node.inputs['Color'].default_value[2] = curr_world.horizon_color[2]
            else:
                bkg_node.inputs['Color'].default_value[0] = curr_world.color[0]
                bkg_node.inputs['Color'].default_value[1] = curr_world.color[1]
                bkg_node.inputs['Color'].default_value[2] = curr_world.color[2]
            bkg_node.inputs['Color'].default_value[3] = 1
            bkg_node.inputs['Strength'].default_value = 1

            out_node = mat_node_tree.nodes.new('ShaderNodeOutputWorld')

            mat_node_tree.links.new(bkg_node.outputs['Background'], out_node.inputs['Surface'])

            # when in non-cycles profile trying to use an environment texture
            if not isCyclesRender(bpy.context):
                tex_slot = get_world_first_valid_texture_slot(curr_world)
                if tex_slot is not None:
                    if isinstance(tex_slot.texture, bpy.types.EnvironmentMapTexture):
                        tex_node = mat_node_tree.nodes.new('ShaderNodeTexture')
                        tex_node.texture = tex_slot.texture
                        mat_node_tree.links.new(tex_node.outputs['Color'], bkg_node.inputs['Color'])

                        tc_node = mat_node_tree.nodes.new('ShaderNodeTexCoord')
                        mat_node_tree.links.new(tc_node.outputs['Generated'], tex_node.inputs['Vector'])
                    else:
                        tex_node = mat_node_tree.nodes.new('ShaderNodeTexEnvironment')
                        tex_node.image = tex_slot.texture.image
                        mat_node_tree.links.new(tex_node.outputs['Color'], bkg_node.inputs['Color'])

        world_mat_wrapper.node_tree = mat_node_tree

        temporary_materials.append(world_mat)
        filtered_materials.append(world_mat_wrapper)

    export_settings['filtered_materials'] = filtered_materials
    export_settings['temporary_materials'] = temporary_materials

    filtered_node_groups = []
    for group in bpy.data.node_groups:
        if group.users == 0:
            continue

        # only groups used by 'NODE' and 'CYCLES' materials
        for bl_material in filtered_materials:
            mat_type = get_material_type(bl_material)
            if mat_type == 'NODE' or mat_type == 'CYCLES':
                if (group not in filtered_node_groups and
                        group in extract_material_node_trees(bl_material.node_tree)):
                    filtered_node_groups.append(group)

    export_settings['filtered_node_groups'] = filtered_node_groups

    filtered_textures = []

    for blender_material in filtered_materials:
        # PBR, NODE, CYCLES materials
        if blender_material.node_tree and blender_material.use_nodes:
            for bl_node in blender_material.node_tree.nodes:
                if (isinstance(bl_node, (bpy.types.ShaderNodeTexImage, bpy.types.ShaderNodeTexEnvironment)) and
                        get_tex_image(bl_node) is not None and
                        get_tex_image(bl_node).users != 0 and
                        get_tex_image(bl_node).size[0] > 0 and
                        get_tex_image(bl_node).size[1] > 0 and
                        bl_node not in filtered_textures):
                    filtered_textures.append(bl_node)

                elif (bpy.app.version < (2,80,0) and
                        isinstance(bl_node, bpy.types.ShaderNodeTexture) and
                        bl_node.texture is not None and
                        get_tex_image(bl_node.texture) is not None and
                        get_tex_image(bl_node.texture).users != 0 and
                        get_tex_image(bl_node.texture).size[0] > 0 and
                        get_tex_image(bl_node.texture).size[1] > 0 and
                        bl_node not in filtered_textures):
                    filtered_textures.append(bl_node)
        # BASIC materials
        elif bpy.app.version < (2,80,0):
            for blender_texture_slot in blender_material.texture_slots:

                if (blender_texture_slot is not None and
                        blender_texture_slot.texture and
                        blender_texture_slot.texture.users != 0 and
                        blender_texture_slot.texture.type == 'IMAGE' and
                        get_tex_image(blender_texture_slot.texture) is not None and
                        get_tex_image(blender_texture_slot.texture).users != 0 and
                        get_tex_image(blender_texture_slot.texture).size[0] > 0 and
                        get_tex_image(blender_texture_slot.texture).size[1] > 0):

                    # NOTE: removed blender_texture_slot.name not in temp_filtered_texture_names

                    if blender_texture_slot not in filtered_textures:
                        accept = False

                        if blender_texture_slot.use_map_color_diffuse:
                            accept = True
                        if blender_texture_slot.use_map_alpha:
                            accept = True
                        if blender_texture_slot.use_map_color_spec:
                            accept = True

                        if blender_texture_slot.use_map_emit:
                            accept = True
                        if blender_texture_slot.use_map_normal:
                            accept = True

                        if export_settings['gltf_displacement']:
                            if blender_texture_slot.use_map_displacement:
                                accept = True

                        if accept:
                            filtered_textures.append(blender_texture_slot)

    for node_group in filtered_node_groups:
        for bl_node in node_group.nodes:
            if (isinstance(bl_node, (bpy.types.ShaderNodeTexImage, bpy.types.ShaderNodeTexEnvironment)) and
                    get_tex_image(bl_node) is not None and
                    get_tex_image(bl_node).users != 0 and
                    get_tex_image(bl_node).size[0] > 0 and
                    get_tex_image(bl_node).size[1] > 0 and
                    bl_node not in filtered_textures):
                filtered_textures.append(bl_node)

            if bpy.app.version < (2,80,0):
                if (isinstance(bl_node, bpy.types.ShaderNodeTexture) and
                        bl_node.texture is not None and
                        get_tex_image(bl_node.texture) is not None and
                        bl_node not in filtered_textures):
                    filtered_textures.append(bl_node)

    export_settings['filtered_textures'] = filtered_textures

    filtered_images = []

    for blender_texture in filtered_textures:

        img = (get_tex_image(blender_texture) if isinstance(blender_texture,
                (bpy.types.ShaderNodeTexImage, bpy.types.ShaderNodeTexEnvironment))
                else get_tex_image(blender_texture.texture))

        if (img is not None and img not in filtered_images and img.users != 0
                and img.size[0] > 0 and img.size[1] > 0):
            filtered_images.append(img)

    export_settings['filtered_images'] = filtered_images


    filtered_cameras = []

    for blender_camera in bpy.data.cameras:

        if blender_camera.users == 0:
            continue

        filtered_cameras.append(blender_camera)

    export_settings['filtered_cameras'] = filtered_cameras

    #
    #

    filtered_lights = []

    for blender_light in bpy.data.lamps if bpy.app.version < (2,80,0) else bpy.data.lights:

        if blender_light.users == 0:
            continue

        if blender_light.type == 'AREA':
            continue

        filtered_lights.append(blender_light)

    export_settings['filtered_lights'] = filtered_lights

    joint_indices = {}

    if export_settings['gltf_skins']:
        for blender_object in filtered_objects_with_dg:

            if blender_object.type != 'MESH':
                continue

            armature_object = find_armature(blender_object)
            if armature_object is None or len(armature_object.pose.bones) == 0:
                continue

            grp = joint_indices[blender_object.data.name] = {}

            for blender_bone in armature_object.pose.bones:
                grp[blender_bone.name] = len(grp)

    export_settings['joint_indices'] = joint_indices
