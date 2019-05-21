# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Simon Wendsche
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
import bpy

from .. import PBRTv3Addon

@PBRTv3Addon.addon_register_class
class PBRTv3_OT_convert_cycles_scene(bpy.types.Operator):
    bl_idname = 'luxrender.convert_cycles_scene'
    bl_label = 'Convert Cycles Scene'
    bl_description = 'Convert Cycles materials, lamps and world background to PBRTv3 materials and lamps'

    def invoke(self, context, event):
        # Show a popup asking for confirmation so the user does not accidentally overwrite materials etc.
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # Convert all materials
        bpy.ops.luxrender.convert_all_cycles_materials()

        # Convert object settings
        for obj in context.scene.objects:
            if not obj.cycles_visibility.camera:
                obj.hide_render = True

        # Convert light settings
        lights = [obj for obj in context.scene.objects if obj.type == 'LAMP']

        for light in lights:
            if light.data.type == 'SUN':
                print('Converting light %s (%s)' % (light.name, light.data.type))
                lux_sun = light.data.pbrtv3_lamp.pbrtv3_lamp_sun
                # Cycles sun lamps are always in "sun only" mode
                lux_sun.sunsky_type = 'sun'
                # Sun size
                lux_sun.relsize = max(light.data.shadow_soft_size * 200, 0.05)

            elif light.data.type == 'AREA':
                print('Converting light %s (%s)' % (light.name, light.data.type))
                lux_area = light.data.pbrtv3_lamp.pbrtv3_lamp_area
                output = None

                if light.data.node_tree:
                    for node in light.data.node_tree.nodes:
                        if node.type == 'OUTPUT_LAMP' and node.is_active_output:
                            output = node
                            break

                    if output:
                        emission_node = get_linked_node(output.inputs['Surface'])

                        if emission_node and emission_node.type == 'EMISSION':
                            socket_color = emission_node.inputs['Color']
                            socket_strength = emission_node.inputs['Strength']

                            lux_area.L_color = convert_rgba_to_rgb(socket_color.default_value)
                            lux_area.power = socket_strength.default_value

        # Convert world background settings
        print('Converting world background')
        create_sky = False
        sky_turbidity = 2.2

        create_background_hemi = False
        hemi_color = None
        hemi_hdri_path = None

        if context.scene.world.node_tree:
            world_output = None

            for node in context.scene.world.node_tree.nodes:
                if node.type == 'OUTPUT_WORLD' and node.is_active_output:
                    world_output = node
                    break

            if world_output:
                background_node = get_linked_node(world_output.inputs['Surface'])

                if background_node and background_node.type == 'BACKGROUND':
                    socket_color = background_node.inputs['Color']
                    socket_strength = background_node.inputs['Strength']

                    if socket_color.is_linked:
                        color_node = get_linked_node(socket_color)

                        if color_node.type == 'TEX_SKY':
                            create_sky = True
                            sky_turbidity = color_node.turbidity
                        elif color_node.type == 'TEX_ENVIRONMENT':
                            create_background_hemi = True

                            if color_node.image:
                                hemi_hdri_path = color_node.image.filepath
                    else:
                        if (socket_strength.default_value > 0 or socket_strength.is_linked):
                            converted_color = convert_rgba_to_rgb(socket_color.default_value)

                            if converted_color != (0, 0, 0):
                                create_background_hemi = True
                                hemi_color = converted_color
        else:
            # Don't create hemi if background is black (check Value component of HSV model)
            if context.scene.world.horizon_color.v > 0:
                create_background_hemi = True
                hemi_color = context.scene.world.horizon_color

        if create_background_hemi:
            hemi_name = 'Background_Lux_autoconverted'
            hemi_data = bpy.data.lamps.new(name=hemi_name, type='HEMI')
            hemi_object = bpy.data.objects.new(name=hemi_name, object_data=hemi_data)
            context.scene.objects.link(hemi_object)

            lux_hemi = hemi_data.pbrtv3_lamp.pbrtv3_lamp_hemi

            if hemi_color:
                lux_hemi.L_color = hemi_color

            if hemi_hdri_path:
                lux_hemi.infinite_map = hemi_hdri_path

        if create_sky:
            sky_name = 'Sky_Lux_autoconverted'
            sky_data = bpy.data.lamps.new(name=sky_name, type='SUN')
            sky_object = bpy.data.objects.new(name=sky_name, object_data=sky_data)
            context.scene.objects.link(sky_object)

            lux_sky = sky_data.pbrtv3_lamp.pbrtv3_lamp_sun

            # Set it to be sky only
            lux_sky.sunsky_type = 'sky'
            lux_sky.turbidity = sky_turbidity

        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_convert_all_cycles_materials(bpy.types.Operator):
    bl_idname = 'luxrender.convert_all_cycles_materials'
    bl_label = 'Convert all Cycles materials'

    def execute(self, context):
        success = 0
        failed = 0
        total = 0

        for blender_mat in bpy.data.materials:
            # Don't convert materials from linked-in files
            if blender_mat.library is None and blender_mat.node_tree:
                # Cycles nodetree available
                if not (hasattr(blender_mat, 'pbrtv3_material') and blender_mat.pbrtv3_material.nodetree):
                    # No Lux nodetree yet, convert the Cycles material
                    total += 1

                    result = cycles_material_converter(blender_mat, context)

                    if 'FINISHED' in result:
                        success += 1
                    elif 'CANCELLED' in result:
                        failed += 1

        self.report({'INFO'}, 'Converted %d of %d materials (%d failed)' % (success, total, failed))
        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class PBRTv3_OT_convert_cycles_material(bpy.types.Operator):
    bl_idname = 'luxrender.convert_cycles_material'
    bl_label = 'Convert this Cycles material'

    material_name = bpy.props.StringProperty(default='')

    def execute(self, context):
        if not self.properties.material_name:
            blender_mat = context.material
        else:
            blender_mat = bpy.data.materials[self.properties.material_name]

        if blender_mat.node_tree:
            # Cycles nodetree present
            result = cycles_material_converter(blender_mat, context)

            if 'FINISHED' in result:
                self.report({'INFO'}, 'Successfully converted material "%s"' % blender_mat.name)
            elif 'CANCELLED' in result:
                self.report({'ERROR'}, 'Failed to convert material "%s"' % blender_mat.name)

        return {'FINISHED'}


def cycles_material_converter(blender_mat, context):
    try:
        print('Converting material %s' % blender_mat.name)

        # Create Lux nodetree
        lux_nodetree = bpy.data.node_groups.new(blender_mat.name, type='pbrtv3_material_nodes')
        lux_nodetree.use_fake_user = True
        blender_mat.pbrtv3_material.nodetree = lux_nodetree.name

        # Find several Cycles nodetypes needed to start the export (or just useful later)
        output = None
        first_image_node = None
        emission = None

        for node in blender_mat.node_tree.nodes:
            if node.type == 'OUTPUT_MATERIAL' and node.is_active_output:
                output = node
            elif node.type == 'TEX_IMAGE' and node.outputs[0].is_linked:
                first_image_node = node
            elif node.type == 'EMISSION' and node.outputs[0].is_linked:
                emission = node

        # Convert surface socket
        first_surface_node, default_value = convert_socket(output.inputs['Surface'], lux_nodetree)

        # Create Lux output node
        lux_output = lux_nodetree.nodes.new('pbrtv3_material_output_node')
        lux_output.location = output.location
        # Connect Lux output to first converted node (if it could be converted)
        if first_surface_node:
            lux_nodetree.links.new(first_surface_node.outputs[0], lux_output.inputs[0])
        else:
            # Backup material in case nothing could be converted
            backup_matte_node = lux_nodetree.nodes.new('pbrtv3_material_matte_node')
            backup_matte_node.location = lux_output.location.x - 300, lux_output.location.y
            lux_nodetree.links.new(backup_matte_node.outputs[0], lux_output.inputs[0])

            backup_matte_node.inputs[0].default_value = context.scene.luxcore_global.cycles_converter_fallback_color

            # If nothing at all could be converted, try at least to find an image texture
            if first_image_node:
                backup_image_node = lux_nodetree.nodes.new('pbrtv3_texture_blender_image_map_node')
                backup_image_node.location = backup_matte_node.location.x - 300, backup_matte_node.location.y
                lux_nodetree.links.new(backup_image_node.outputs[0], backup_matte_node.inputs[0])

                backup_image_node.image_name = first_image_node.image.name

        # Use the first emission node if there are any
        if emission:
            lux_emission = lux_nodetree.nodes.new('pbrtv3_light_area_node')
            lux_emission.location = lux_output.location.x - 230, lux_output.location.y - 180

            # Color
            linked_node, default_value = convert_socket(emission.inputs['Color'], lux_nodetree)
            # The default value of a Cycles color is always RGBA, but we only need RGB
            default_value = convert_rgba_to_rgb(default_value)
            copy_socket_properties(lux_emission, 0, lux_nodetree, linked_node, default_value)

            # Strenght (gain)
            linked_node, default_value = convert_socket(emission.inputs['Strength'], lux_nodetree)
            if default_value:
                # Gain is not a socket in Lux emission node
                lux_emission.gain = default_value

            # Connect
            lux_nodetree.links.new(lux_emission.outputs[0], lux_output.inputs[1])

        # TODO: displacement socket

        return {'FINISHED'}
    except Exception as err:
        print('ERROR: Cannot convert material "%s": %s' % (blender_mat.name, err))
        import traceback
        traceback.print_exc()
        return {'CANCELLED'}

def convert_rgba_to_rgb(color):
        return color[:3] if color is not None else None

def get_linked_node(socket):
    if socket.is_linked:
        return socket.links[0].from_node
    else:
        return None

def copy_socket_properties(lux_node, socket_index, lux_nodetree, linked_node=None, default_value=None):
    if linked_node is not None:
        # Create the link
        lux_nodetree.links.new(linked_node.outputs[0], lux_node.inputs[socket_index])
    elif default_value is not None:
        # Set default value of the socket
        lux_node.inputs[socket_index].default_value = default_value

def convert_socket(socket, lux_nodetree):
    if socket.is_linked:
        node = socket.links[0].from_node
        # Get from_socket information, for nodes with multiple outputs (e.g. image map with color and alpha)
        from_socket = socket.links[0].from_socket
    elif hasattr(socket, 'default_value'):
        return None, socket.default_value
    else:
        # Sockets like NodeSocketShader do not have a default value
        return None, None

    lux_node = None

    if node.type in ('OUTPUT_MATERIAL', 'EMISSION'):
        pass # These node types are exported before recursive export

    ### Materials ###

    elif node.type == 'BSDF_DIFFUSE':
        # "Matte" in Lux
        lux_node = lux_nodetree.nodes.new('pbrtv3_material_matte_node')

        # Color
        linked_node, default_value = convert_socket(node.inputs['Color'], lux_nodetree)
        # The default value of a Cycles color is always RGBA, but we only need RGB
        default_value = convert_rgba_to_rgb(default_value)
        copy_socket_properties(lux_node, 0, lux_nodetree, linked_node, default_value)

    elif node.type == 'BSDF_GLOSSY':
        # "Metal2" in Lux
        lux_node = lux_nodetree.nodes.new('pbrtv3_material_metal2_node')

        # Color
        linked_node, default_value = convert_socket(node.inputs['Color'], lux_nodetree)
        # The default value of a Cycles color is always RGBA, but we only need RGB
        default_value = convert_rgba_to_rgb(default_value)
        copy_socket_properties(lux_node, 0, lux_nodetree, linked_node, default_value)

        # Roughness
        linked_node, default_value = convert_socket(node.inputs['Roughness'], lux_nodetree)
        copy_socket_properties(lux_node, 2, lux_nodetree, linked_node, default_value)

    elif node.type == 'MIX_SHADER':
        amount_node = get_linked_node(node.inputs['Fac'])
        mat1_node = get_linked_node(node.inputs[1])
        mat2_node = get_linked_node(node.inputs[2])

        if (amount_node and mat1_node and mat2_node) and (
                amount_node.type in ('FRESNEL', 'LAYER_WEIGHT') and
                mat1_node.type == 'BSDF_DIFFUSE' and mat2_node.type == 'BSDF_GLOSSY'):
            # This is the most common way to fake a glossy material in Cycles
            lux_node = lux_nodetree.nodes.new('pbrtv3_material_glossy_node')

            # Diffuse color (from BSDF_DIFFUSE)
            linked_node, default_value = convert_socket(mat1_node.inputs['Color'], lux_nodetree)
            # The default value of a Cycles color is always RGBA, but we only need RGB
            default_value = convert_rgba_to_rgb(default_value)
            copy_socket_properties(lux_node, 0, lux_nodetree, linked_node, default_value)

            # Roughness (from BSDF_GLOSSY)
            linked_node, default_value = convert_socket(mat2_node.inputs['Roughness'], lux_nodetree)
            copy_socket_properties(lux_node, 6, lux_nodetree, linked_node, default_value)

            # TODO: specular color (get brightness from fresnel/layerweight node and color from glossy node?)

        elif (mat1_node and mat2_node) and ((mat1_node.type == 'BSDF_GLASS' and mat2_node.type == 'BSDF_TRANSPARENT')
                                            or (mat1_node.type == 'BSDF_TRANSPARENT' and mat2_node.type == 'BSDF_GLASS')):
            # This is the most common way to fake an archglass material in Cycles
            glass_node = mat1_node if mat1_node.type == 'BSDF_GLASS' else mat2_node

            lux_node = lux_nodetree.nodes.new('pbrtv3_material_glass_node')
            # Set it to architectural mode
            lux_node.architectural = True

            # Glass transmission color (from BSDF_GLASS)
            linked_node, default_value = convert_socket(glass_node.inputs['Color'], lux_nodetree)
            # The default value of a Cycles color is always RGBA, but we only need RGB
            default_value = convert_rgba_to_rgb(default_value)
            copy_socket_properties(lux_node, 0, lux_nodetree, linked_node, default_value)
        else:
            # "Normal" mix material, no special treatment
            linked_node_amount, default_value_amount = convert_socket(node.inputs['Fac'], lux_nodetree)
            linked_node_1, default_value_1 = convert_socket(node.inputs[1], lux_nodetree)
            linked_node_2, default_value_2 = convert_socket(node.inputs[2], lux_nodetree)

            # Only create the mix material if at least one of the sub-shaders could be converted
            if linked_node_1 or linked_node_2:
                lux_node = lux_nodetree.nodes.new('pbrtv3_material_mix_node')
                # Amount
                copy_socket_properties(lux_node, 0, lux_nodetree, linked_node_amount, default_value_amount)
                # Material 1
                copy_socket_properties(lux_node, 1, lux_nodetree, linked_node_1, default_value_1)
                # Material 2
                copy_socket_properties(lux_node, 2, lux_nodetree, linked_node_2, default_value_2)

    elif node.type == 'ADD_SHADER':
        # Since there is no better euqivalent for the add shader in Lux we will use a mix material
        linked_node_1, default_value_1 = convert_socket(node.inputs[0], lux_nodetree)
        linked_node_2, default_value_2 = convert_socket(node.inputs[1], lux_nodetree)

        if linked_node_1 or linked_node_2:
            lux_node = lux_nodetree.nodes.new('pbrtv3_material_mix_node')
            # Material 1
            copy_socket_properties(lux_node, 1, lux_nodetree, linked_node_1, default_value_1)
            # Material 2
            copy_socket_properties(lux_node, 2, lux_nodetree, linked_node_2, default_value_2)

    elif node.type == 'BSDF_TRANSPARENT':
        lux_node = lux_nodetree.nodes.new('pbrtv3_material_null_node')

        linked_node, default_value = convert_socket(node.inputs['Color'], lux_nodetree)
        default_value = convert_rgba_to_rgb(default_value)

        copy_socket_properties(lux_node, 0, lux_nodetree, linked_node, default_value)

    elif node.type == 'BSDF_GLASS':
        lux_node = lux_nodetree.nodes.new('pbrtv3_material_glass_node')

        # Color (Transmission)
        linked_node, default_value = convert_socket(node.inputs['Color'], lux_nodetree)
        # The default value of a Cycles color is always RGBA, but we only need RGB
        default_value = convert_rgba_to_rgb(default_value)
        copy_socket_properties(lux_node, 0, lux_nodetree, linked_node, default_value)

        # Roughness
        linked_node, default_value = convert_socket(node.inputs['Roughness'], lux_nodetree)

        if (default_value and default_value > 0.000001) or linked_node:
            # Use roughness
            lux_node.rough = True
            copy_socket_properties(lux_node, 6, lux_nodetree, linked_node, default_value)

        # IOR
        linked_node, default_value = convert_socket(node.inputs['IOR'], lux_nodetree)
        copy_socket_properties(lux_node, 2, lux_nodetree, linked_node, default_value)

    elif node.type == 'BSDF_TRANSLUCENT':
        lux_node = lux_nodetree.nodes.new('pbrtv3_material_mattetranslucent_node')

        # Color (the cycles node only has one value that is used for both reflection and transmission in the Lux mat)
        linked_node, default_value = convert_socket(node.inputs['Color'], lux_nodetree)
        # The default value of a Cycles color is always RGBA, but we only need RGB
        default_value = convert_rgba_to_rgb(default_value)
        copy_socket_properties(lux_node, 0, lux_nodetree, linked_node, default_value)
        copy_socket_properties(lux_node, 1, lux_nodetree, linked_node, default_value)

    elif node.type == 'BSDF_VELVET':
        lux_node = lux_nodetree.nodes.new('pbrtv3_material_velvet_node')

        # Color (the cycles node only has one value that is used for both reflection and transmission in the Lux mat)
        linked_node, default_value = convert_socket(node.inputs['Color'], lux_nodetree)
        # The default value of a Cycles color is always RGBA, but we only need RGB
        default_value = convert_rgba_to_rgb(default_value)
        copy_socket_properties(lux_node, 0, lux_nodetree, linked_node, default_value)

    ### Textures ###

    elif node.type == 'TEX_IMAGE':
        lux_node = lux_nodetree.nodes.new('pbrtv3_texture_blender_image_map_node')

        if node.image:
            # Selected Blender image
            lux_node.image_name = node.image.name

        # Gamma (from color space)
        lux_node.gamma = 2.2 if node.color_space == 'COLOR' else 1

        # Alpha handling (if alpha output of TEX_IMAGE is used)
        if from_socket.name == 'Alpha':
            lux_node.channel = 'alpha'

    elif node.type == 'TEX_NOISE':
        lux_node = lux_nodetree.nodes.new('pbrtv3_texture_blender_clouds_node')

    elif node.type == 'TEX_VORONOI':
        lux_node = lux_nodetree.nodes.new('pbrtv3_texture_blender_voronoi_node')

    elif node.type == 'TEX_GRADIENT':
        lux_node = lux_nodetree.nodes.new('pbrtv3_texture_blender_blend_node')

    # No node support for magic texture yet (in LuxBlend)
    #elif node.type == 'TEX_MAGIC':
    #    lux_node = lux_nodetree.nodes.new('pbrtv3_texture_blender__node')

    elif node.type == 'TEX_MUSGRAVE':
        lux_node = lux_nodetree.nodes.new('pbrtv3_texture_blender_musgrave_node')

    elif node.type == 'TEX_CHECKER':
        lux_node = lux_nodetree.nodes.new('pbrtv3_texture_checker_node')

    # Brick is making problems (does not have outputs after creation, probably because of color/float switch which is
    # done in the draw() function... annoying concept
    #elif node.type == 'TEX_BRICK':
    #    lux_node = lux_nodetree.nodes.new('pbrtv3_texture_brick_node')

    elif node.type == 'BUMP':
        lux_node = lux_nodetree.nodes.new('pbrtv3_texture_math_node')
        lux_node.mode = 'scale'

        # Strength
        linked_node, default_value = convert_socket(node.inputs['Strength'], lux_nodetree)
        if default_value and node.invert:
            # TODO: extend this so it is able to invert linked nodes, too
            default_value = -default_value
        copy_socket_properties(lux_node, 0, lux_nodetree, linked_node, default_value)

        # Height
        linked_node, default_value = convert_socket(node.inputs['Height'], lux_nodetree)
        copy_socket_properties(lux_node, 1, lux_nodetree, linked_node, default_value)

    else:
        # In case of an unkown node, do nothing
        print('WARNING: Unsupported node type %s' % node.type)
        return None, None

    if lux_node:
        # Copy common properties shared by all nodes
        lux_node.location = node.location

        if 'BSDF' in node.type:
            # Bump
            if 'Normal' in node.inputs and 'Bump' in lux_node.inputs:
                linked_node, default_value = convert_socket(node.inputs['Normal'], lux_nodetree)
                # There is no valid default value for the bump slot, that's why we pass None
                copy_socket_properties(lux_node, 'Bump', lux_nodetree, linked_node, None)

    return lux_node, None