# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
# Blender Libs
import bpy, bl_operators
import json, math, os, struct, mathutils

# LuxRender Libs
from .. import LuxRenderAddon
from ..outputs import LuxLog, LuxManager
from ..export.scene import SceneExporter
from ..export import materials as export_materials

from ..extensions_framework import util as efutil

# Per-IDPropertyGroup preset handling

class LUXRENDER_MT_base(bpy.types.Menu):
    preset_operator = "script.execute_preset"

    def draw(self, context):
        return bpy.types.Menu.draw_preset(self, context)


@LuxRenderAddon.addon_register_class
class LUXRENDER_MT_presets_engine(LUXRENDER_MT_base):
    bl_label = "LuxRender Engine Presets"
    preset_subdir = "luxrender/engine"


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_add_material_nodetree(bpy.types.Operator):
    """"""
    bl_idname = "luxrender.add_material_nodetree"
    bl_label = "Add LuxRender Material Nodetree"
    bl_description = "Add a LuxRender node tree linked to this material"

    # idtype = StringProperty(name="ID Type", default="material")

    def execute(self, context):
        # idtype = self.properties.idtype
        idtype = 'material'
        context_data = {'material': context.material, 'lamp': context.lamp}
        idblock = context_data[idtype]

        nt = bpy.data.node_groups.new(idblock.name, type='luxrender_material_nodes')
        nt.use_fake_user = True
        idblock.luxrender_material.nodetree = nt.name

        ctx_vol = context.scene.luxrender_volumes
        ctx_mat = context.material.luxrender_material

        # Get the mat type set in editor, todo: find a more iterative way to get context
        node_type = 'luxrender_material_%s_node' % ctx_mat.type

        if ctx_mat.type == 'matte':
            editor_type = ctx_mat.luxrender_mat_matte
        if ctx_mat.type == 'mattetranslucent':
            editor_type = ctx_mat.luxrender_mat_mattetranslucent
        if ctx_mat.type == 'glossy':
            editor_type = ctx_mat.luxrender_mat_glossy
        if ctx_mat.type == 'glossycoating':
            editor_type = ctx_mat.luxrender_mat_glossycoating
        if ctx_mat.type == 'glossytranslucent':
            editor_type = ctx_mat.luxrender_mat_glossytranslucent
        if ctx_mat.type == 'glass':
            editor_type = ctx_mat.luxrender_mat_glass
        if ctx_mat.type == 'glass2':
            editor_type = ctx_mat.luxrender_mat_glass2
        if ctx_mat.type == 'roughglass':
            editor_type = ctx_mat.luxrender_mat_roughglass
        if ctx_mat.type == 'mirror':
            editor_type = ctx_mat.luxrender_mat_mirror
        if ctx_mat.type == 'carpaint':
            editor_type = ctx_mat.luxrender_mat_carpaint
        if ctx_mat.type == 'metal':
            editor_type = ctx_mat.luxrender_mat_metal
        if ctx_mat.type == 'metal2':
            editor_type = ctx_mat.luxrender_mat_metal2
        if ctx_mat.type == 'velvet':
            editor_type = ctx_mat.luxrender_mat_velvet
        if ctx_mat.type == 'cloth':
            editor_type = ctx_mat.luxrender_mat_cloth
        if ctx_mat.type == 'scatter':
            editor_type = ctx_mat.luxrender_mat_scatter
        if ctx_mat.type == 'mix':
            editor_type = ctx_mat.luxrender_mat_mix
        if ctx_mat.type == 'layered':
            editor_type = ctx_mat.luxrender_mat_layered

        # handling for not existent shinymetal node, just hack atm.
        if ctx_mat.type == 'shinymetal':
            editor_type = ctx_mat.luxrender_mat_metal2
            node_type = 'luxrender_material_metal2_node'

        if idtype == 'material':
            shader = nt.nodes.new(node_type)  # create also matnode from editor type
            shader.location = 200, 570
            sh_out = nt.nodes.new('luxrender_material_output_node')
            sh_out.location = 500, 400
            nt.links.new(shader.outputs[0], sh_out.inputs[0])

            # Get material settings ( color )
            if 'Absorption Color' in shader.inputs:
                shader.inputs['Absorption Color'].color = editor_type.Ka_color
            if 'Diffuse Color' in shader.inputs:
                shader.inputs['Diffuse Color'].color = editor_type.Kd_color
            if 'Reflection Color' in shader.inputs:
                shader.inputs['Reflection Color'].color = editor_type.Kr_color
            if 'Specular Color' in shader.inputs:
                shader.inputs['Specular Color'].color = editor_type.Ks_color
            if 'Specular Color 1' in shader.inputs:
                shader.inputs['Specular Color 1'].color = editor_type.Ks1_color
            if 'Specular Color 2' in shader.inputs:
                shader.inputs['Specular Color 2'].color = editor_type.Ks2_color
            if 'Specular Color 3' in shader.inputs:
                shader.inputs['Specular Color 3'].color = editor_type.Ks3_color
            if 'Transmission Color' in shader.inputs:
                shader.inputs['Transmission Color'].color = editor_type.Kt_color
            if 'Warp Diffuse Color' in shader.inputs:
                shader.inputs['Warp Diffuse Color'].color = editor_type.warp_Kd_color
            if 'Warp Specular Color' in shader.inputs:
                shader.inputs['Warp Specular Color'].color = editor_type.warp_Ks_color
            if 'Weft Diffuse Color' in shader.inputs:
                shader.inputs['Weft Diffuse Color'].color = editor_type.weft_Kd_color
            if 'Weft Specular Color' in shader.inputs:
                shader.inputs['Weft Specular Color'].color = editor_type.weft_Ks_color
            if 'Backface Absorption Color' in shader.inputs:
                shader.inputs['Backface Absorption Color'].color = editor_type.backface_Ka_color
            if 'Backface Specular Color' in shader.inputs:
                shader.inputs['Backface Specular Color'].color = editor_type.backface_Ks_color

            # Get various material settings ( float )
            if 'Mix Amount' in shader.inputs:
                shader.inputs['Mix Amount'].amount = editor_type.amount_floatvalue

            if 'Cauchy B' in shader.inputs:
                shader.inputs['Cauchy B'].cauchyb = editor_type.cauchyb_floatvalue

            if 'Film IOR' in shader.inputs:
                shader.inputs['Film IOR'].filmindex = editor_type.filmindex_floatvalue

            if 'Film Thickness (nm)' in shader.inputs:
                shader.inputs['Film Thickness (nm)'].film = editor_type.film_floatvalue

            if 'IOR' in shader.inputs and hasattr(shader.inputs['IOR'], 'index'):
                shader.inputs['IOR'].index = editor_type.index_floatvalue  # not fresnel IOR

            if 'U-Roughness' in shader.inputs:
                shader.inputs['U-Roughness'].uroughness = editor_type.uroughness_floatvalue

            if 'V-Roughness' in shader.inputs:
                shader.inputs['V-Roughness'].vroughness = editor_type.vroughness_floatvalue

            if 'Sigma' in shader.inputs:
                shader.inputs['Sigma'].sigma = editor_type.sigma_floatvalue

            # non-socket parameters ( bool )
            if hasattr(shader, 'use_ior'):
                shader.use_ior = editor_type.useior

            if hasattr(shader, 'multibounce'):
                shader.multibounce = editor_type.multibounce

            if hasattr(shader, 'use_anisotropy'):
                shader.use_anisotropy = editor_type.anisotropic

            if hasattr(shader, 'dispersion'):
                shader.dispersion = editor_type.dispersion

            if hasattr(shader, 'arch'):
                shader.arch = editor_type.architectural

            if hasattr(shader, 'advanced'):
                shader.advanced = editor_type.advanced

            # non-socket parameters ( other )
            # velvet
            if hasattr(shader, 'thickness'):
                shader.thickness = editor_type.thickness

            if hasattr(shader, 'p1'):
                shader.p1 = editor_type.p1

            if hasattr(shader, 'p2'):
                shader.p2 = editor_type.p2

            if hasattr(shader, 'p3'):
                shader.p3 = editor_type.p3

            # metal 1
            if hasattr(shader, 'metal_preset'):
                shader.metal_preset = editor_type.name

            if hasattr(shader, 'metal_nkfile'):
                shader.metal_nkfile = editor_type.filename

            # Get the volumes
            def get_vol_type(name):
                for vol in ctx_vol.volumes:
                    if vol.name == name:
                        volume_type = 'luxrender_volume_%s_node' % (vol.type)
                return volume_type

            if ctx_mat.Interior_volume:
                vol_node = get_vol_type(ctx_mat.Interior_volume)
                volume_int = nt.nodes.new(vol_node)
                volume_int.location = 200, 200
                nt.links.new(volume_int.outputs[0], sh_out.inputs[1])
                volume_int.inputs['IOR'].fresnel = ctx_vol.volumes[ctx_mat.Interior_volume].fresnel_fresnelvalue

            if ctx_mat.Exterior_volume:
                vol_node = get_vol_type(ctx_mat.Exterior_volume)
                volume_ext = nt.nodes.new(vol_node)
                volume_ext.location = 200, -50
                nt.links.new(volume_ext.outputs[0], sh_out.inputs[2])
                volume_ext.inputs['IOR'].fresnel = ctx_vol.volumes[ctx_mat.Exterior_volume].fresnel_fresnelvalue

        #else:
        #   nt.nodes.new('OutputLightShaderNode')

        return {'FINISHED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_preset_engine_add(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    """Save the current settings as a preset"""
    bl_idname = 'luxrender.preset_engine_add'
    bl_label = 'Add LuxRender Engine settings preset'
    preset_menu = 'LUXRENDER_MT_presets_engine'
    preset_values = []
    preset_subdir = 'luxrender/engine'

    def execute(self, context):
        self.preset_values = [
                                 'bpy.context.scene.luxrender_engine.%s' % v['attr'] for v in
                                 bpy.types.luxrender_engine.get_exportable_properties()
                             ] + [
                                 'bpy.context.scene.luxrender_sampler.%s' % v['attr'] for v in
                                 bpy.types.luxrender_sampler.get_exportable_properties()
                             ] + [
                                 'bpy.context.scene.luxrender_integrator.%s' % v['attr'] for v in
                                 bpy.types.luxrender_integrator.get_exportable_properties()
                             ] + [
                                 'bpy.context.scene.luxrender_volumeintegrator.%s' % v['attr'] for v in
                                 bpy.types.luxrender_volumeintegrator.get_exportable_properties()
                             ] + [
                                 'bpy.context.scene.luxrender_filter.%s' % v['attr'] for v in
                                 bpy.types.luxrender_filter.get_exportable_properties()
                             ] + [
                                 'bpy.context.scene.luxrender_accelerator.%s' % v['attr'] for v in
                                 bpy.types.luxrender_accelerator.get_exportable_properties()
                             ]
        return super().execute(context)


@LuxRenderAddon.addon_register_class
class LUXRENDER_MT_presets_networking(LUXRENDER_MT_base):
    bl_label = "LuxRender Networking Presets"
    preset_subdir = "luxrender/networking"


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_preset_networking_add(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    '''Save the current settings as a preset'''
    bl_idname = 'luxrender.preset_networking_add'
    bl_label = 'Add LuxRender Networking settings preset'
    preset_menu = 'LUXRENDER_MT_presets_networking'
    preset_values = []
    preset_subdir = 'luxrender/networking'

    def execute(self, context):
        self.preset_values = [
            'bpy.context.scene.luxrender_networking.%s' % v['attr'] for v in
            bpy.types.luxrender_networking.get_exportable_properties()
        ]
        return super().execute(context)


# Volume data handling

@LuxRenderAddon.addon_register_class
class LUXRENDER_MT_presets_volume(LUXRENDER_MT_base):
    bl_label = "LuxRender Volume Presets"
    preset_subdir = "luxrender/volume"


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_preset_volume_add(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    """Save the current settings as a preset"""
    bl_idname = 'luxrender.preset_volume_add'
    bl_label = 'Add LuxRender Volume settings preset'
    preset_menu = 'LUXRENDER_MT_presets_volume'
    preset_values = []
    preset_subdir = 'luxrender/volume'

    def execute(self, context):
        ks = 'bpy.context.scene.luxrender_volumes.volumes[bpy.context.scene.luxrender_volumes.volumes_index].%s'
        pv = [
            ks % v['attr'] for v in bpy.types.luxrender_volume_data.get_exportable_properties()
        ]

        self.preset_values = pv
        return super().execute(context)


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_volume_add(bpy.types.Operator):
    """Add a new material volume definition to the scene"""

    bl_idname = "luxrender.volume_add"
    bl_label = "Add LuxRender Volume"

    new_volume_name = bpy.props.StringProperty(default='New Volume')

    def invoke(self, context, event):
        v = context.scene.luxrender_volumes.volumes
        v.add()
        new_vol = v[len(v) - 1]
        new_vol.name = self.properties.new_volume_name
        return {'FINISHED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_volume_remove(bpy.types.Operator):
    """Remove the selected material volume definition"""

    bl_idname = "luxrender.volume_remove"
    bl_label = "Remove LuxRender Volume"

    def invoke(self, context, event):
        w = context.scene.luxrender_volumes
        w.volumes.remove(w.volumes_index)
        w.volumes_index = len(w.volumes) - 1
        return {'FINISHED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_lightgroup_add(bpy.types.Operator):
    """Add a new light group definition to the scene"""

    bl_idname = "luxrender.lightgroup_add"
    bl_label = "Add LuxRender Light Group"

    lg_count = 0
    new_lightgroup_name = bpy.props.StringProperty(default='New Light Group ')

    def invoke(self, context, event):
        lg = context.scene.luxrender_lightgroups.lightgroups
        lg.add()
        new_lg = lg[len(lg) - 1]
        new_lg.name = self.properties.new_lightgroup_name + str(LUXRENDER_OT_lightgroup_add.lg_count)
        LUXRENDER_OT_lightgroup_add.lg_count += 1
        return {'FINISHED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_lightgroup_remove(bpy.types.Operator):
    """Remove the selected lightgroup definition"""

    bl_idname = "luxrender.lightgroup_remove"
    bl_label = "Remove LuxRender Light Group"

    lg_index = bpy.props.IntProperty(default=-1)

    def invoke(self, context, event):
        w = context.scene.luxrender_lightgroups
        if self.properties.lg_index == -1:
            w.lightgroups.remove(w.lightgroups_index)
        else:
            w.lightgroups.remove(self.properties.lg_index)
        w.lightgroups_index = len(w.lightgroups) - 1
        return {'FINISHED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_opencl_device_list_update(bpy.types.Operator):
    """Update the OpenCL device list"""

    bl_idname = "luxrender.opencl_device_list_update"
    bl_label = "Update the OpenCL device list"

    def invoke(self, context, event):
        devs = context.scene.luxcore_enginesettings.luxcore_opencl_devices
        # Clear the list
        for i in range(len(devs)):
            devs.remove(0)

        # Create the new list
        from ..outputs.luxcore_api import pyluxcore

        deviceList = pyluxcore.GetOpenCLDeviceList()
        for dev in deviceList:
            devs.add()
            index = len(devs) - 1
            new_dev = devs[index]
            new_dev.name = 'Device ' + str(index) + ': ' + dev[0] + ' (' + dev[1] + ')'

        return {'FINISHED'}


# Export process

@LuxRenderAddon.addon_register_class
class EXPORT_OT_luxrender(bpy.types.Operator):
    bl_idname = 'export.luxrender'
    bl_label = 'Export LuxRender Scene (.lxs)'

    filter_glob = bpy.props.StringProperty(default='*.lxs', options={'HIDDEN'})
    use_filter = bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    filename = bpy.props.StringProperty(name='LXS filename')
    directory = bpy.props.StringProperty(name='LXS directory')

    api_type = bpy.props.StringProperty(options={'HIDDEN'}, default='FILE')  # Export target ['FILE','API',...]
    write_files = bpy.props.BoolProperty(options={'HIDDEN'}, default=True)  # Write any files ?
    write_all_files = bpy.props.BoolProperty(options={'HIDDEN'},
                                             default=True)  # Force writing all files, don't obey UI settings

    scene = bpy.props.StringProperty(options={'HIDDEN'}, default='')  # Specify scene to export

    def invoke(self, context, event):
        self.filename = efutil.scene_filename() + '.lxs'  # prefill with blender (temp-) filename
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.properties.scene:
            scene = context.scene
        else:
            scene = bpy.data.scenes[self.properties.scene]

        LuxManager.SetActive(None)

        return SceneExporter() \
            .set_report(self.report) \
            .set_properties(self.properties) \
            .set_scene(scene) \
            .export()


menu_func = lambda self, context: self.layout.operator("export.luxrender", text="Export LuxRender Scene")
bpy.types.INFO_MT_file_export.append(menu_func)


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_load_material(bpy.types.Operator):
    bl_idname = 'luxrender.load_material'
    bl_label = 'Load material'
    bl_description = 'Load material from LBM2 file'

    filter_glob = bpy.props.StringProperty(default='*.lbm2', options={'HIDDEN'})
    use_filter = bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    filename = bpy.props.StringProperty(name='Destination filename')
    directory = bpy.props.StringProperty(name='Destination directory')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            if not self.properties.filename or not self.properties.directory:
                raise Exception('No filename or directory given.')

            blender_mat = context.material
            luxrender_mat = context.material.luxrender_material

            fullpath = os.path.join(
                self.properties.directory,
                self.properties.filename
            )
            with open(fullpath, 'r') as lbm2_file:
                lbm2_data = json.load(lbm2_file)

            luxrender_mat.load_lbm2(context, lbm2_data, blender_mat, context.object)

            return {'FINISHED'}

        except Exception as err:
            self.report({'ERROR'}, 'Cannot load: %s' % err)
            return {'CANCELLED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_save_material(bpy.types.Operator):
    bl_idname = 'luxrender.save_material'
    bl_label = 'Save material'
    bl_description = 'Save material as LXM or LBM2 file'

    filter_glob = bpy.props.StringProperty(default='*.lbm2;*.lxm', options={'HIDDEN'})
    use_filter = bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    filename = bpy.props.StringProperty(name='Destination filename')
    directory = bpy.props.StringProperty(name='Destination directory')

    material_file_type = bpy.props.EnumProperty(name="Exported file type",
                                                items=[('LBM2', 'LBM2', 'LBM2'), ('LXM', 'LXM', 'LXM')])

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            if not self.properties.filename or not self.properties.directory:
                raise Exception('No filename or directory given.')

            blender_mat = context.material
            luxrender_mat = context.material.luxrender_material

            LM = LuxManager("material_save", self.properties.material_file_type)
            LuxManager.SetActive(LM)
            LM.SetCurrentScene(context.scene)

            material_context = LM.lux_context

            fullpath = os.path.join(
                self.properties.directory,
                self.properties.filename
            )

            # Make sure the filename has the correct extension
            if not fullpath.lower().endswith('.%s' % self.properties.material_file_type.lower()):
                fullpath += '.%s' % self.properties.material_file_type.lower()

            export_materials.ExportedMaterials.clear()
            export_materials.ExportedTextures.clear()

            # This causes lb25 to embed all external data ...
            context.scene.luxrender_engine.is_saving_lbm2 = True

            # Include interior/exterior for this material
            for volume in context.scene.luxrender_volumes.volumes:
                if volume.name in [luxrender_mat.Interior_volume, luxrender_mat.Exterior_volume]:
                    material_context.makeNamedVolume(volume.name, *volume.api_output(material_context))

            cr = context.scene.luxrender_testing.clay_render
            context.scene.luxrender_testing.clay_render = False
            luxrender_mat.export(context.scene, material_context, blender_mat)
            context.scene.luxrender_testing.clay_render = cr

            material_context.set_material_name(blender_mat.name)
            material_context.update_material_metadata(
                interior=luxrender_mat.Interior_volume,
                exterior=luxrender_mat.Exterior_volume
            )

            material_context.write(fullpath)

            # .. and must be reset!
            context.scene.luxrender_engine.is_saving_lbm2 = False

            LM.reset()
            LuxManager.SetActive(None)

            self.report({'INFO'}, 'Material "%s" saved to %s' % (blender_mat.name, fullpath))
            return {'FINISHED'}

        except Exception as err:
            self.report({'ERROR'}, 'Cannot save: %s' % err)
            return {'CANCELLED'}


def material_converter(report, scene, blender_mat):
    try:
        luxrender_mat = blender_mat.luxrender_material

        # TODO - check values marked #ASV - Arbitrary Scale Value

        luxrender_mat.Interior_volume = ''
        luxrender_mat.Exterior_volume = ''

        luxrender_mat.reset(prnt=blender_mat)

        if blender_mat.raytrace_mirror.use and blender_mat.raytrace_mirror.reflect_factor >= 0.9:
            # for high mirror reflection values switch to mirror material
            luxrender_mat.set_type('mirror')
            lmm = luxrender_mat.luxrender_mat_mirror
            lmm.Kr_color = [i for i in blender_mat.mirror_color]
            luxmat = lmm
        elif blender_mat.specular_intensity < 0.01:
            # use matte as glossy mat with very low specular is not equal matte
            luxrender_mat.set_type('matte')
            lms = luxrender_mat.luxrender_mat_matte
            lms.Kd_color = [blender_mat.diffuse_intensity * i for i in blender_mat.diffuse_color]
            lms.sigma_floatvalue = 0.0
            luxmat = lms
        else:
            luxrender_mat.set_type('glossy')
            lmg = luxrender_mat.luxrender_mat_glossy
            lmg.multibounce = False
            lmg.useior = False
            lmg.Kd_color = [blender_mat.diffuse_intensity * i for i in blender_mat.diffuse_color]

            logHardness = math.log(blender_mat.specular_hardness)

            # fit based on empirical measurements
            # measurements based on intensity of 0.5, use linear scale for other intensities
            specular_scale = 2.0 * max(0.0128415 * logHardness ** 2 - 0.171266 * logHardness + 0.575631, 0.0)

            lmg.Ks_color = [min(specular_scale * blender_mat.specular_intensity * i, 0.25) for i in
                            blender_mat.specular_color]

            # fit based on empirical measurements
            roughness = min(max(0.757198 - 0.120395 * logHardness, 0.0), 1.0)

            lmg.uroughness_floatvalue = roughness
            lmg.vroughness_floatvalue = roughness
            lmg.uroughness_usefloattexture = lmg.vroughness_usefloattexture = False
            luxmat = lmg


        # Emission
        lme = blender_mat.luxrender_emission
        if blender_mat.emit > 0:
            lme.use_emission = True
            lme.L_color = [1.0, 1.0, 1.0]
            lme.gain = blender_mat.emit
        else:
            lme.use_emission = False

        # Transparency
        lmt = blender_mat.luxrender_transparency
        if blender_mat.use_transparency:
            lmt.transparent = True
            lmt.alpha_source = 'constant'
            lmt.alpha_value = blender_mat.alpha
        else:
            lmt.transparent = False

        # iterate textures and build mix stacks according to influences
        Kd_stack = []
        Ks_stack = []
        Lux_TexName = []
        bump_tex = None
        for tex_slot in blender_mat.texture_slots:
            if tex_slot is not None:
                if tex_slot.use and tex_slot.texture.type != 'NONE' and \
                                tex_slot.texture.luxrender_texture.type != 'BLENDER':
                    tex_slot.texture.luxrender_texture.type = 'BLENDER'

                    if tex_slot.use_map_color_diffuse:
                        dcf = tex_slot.diffuse_color_factor

                        if tex_slot.use_map_diffuse:
                            dcf *= tex_slot.diffuse_factor
                        Kd_stack.append((tex_slot.texture, dcf, tex_slot.color))

                    if tex_slot.use_map_color_spec:
                        scf = tex_slot.specular_color_factor

                        if tex_slot.use_map_specular:
                            scf *= tex_slot.specular_factor
                        Ks_stack.append((tex_slot.texture, scf))

                    if tex_slot.use_map_normal:
                        bump_tex = (tex_slot.texture, tex_slot.normal_factor)

        if luxrender_mat.type in ('matte', 'glossy'):
            # print(len(Kd_stack))
            if len(Kd_stack) == 1:
                tex = Kd_stack[0][0]
                dcf = Kd_stack[0][1]
                color = Kd_stack[0][2]
                variant = tex.luxrender_texture.get_paramset(scene, tex)[0]

                if variant == 'color':
                    # assign the texture directly
                    luxmat.Kd_usecolortexture = True
                    luxmat.Kd_colortexturename = tex.name
                    luxmat.Kd_color = [i * Kd_stack[0][1] for i in luxmat.Kd_color]
                    luxmat.Kd_multiplycolor = True
                else:
                    # TODO - insert mix texture
                    # check there are enough free empty texture slots !

                    if tex.use_color_ramp:
                        if len(Kd_stack) < 16:
                            mix_tex_slot = blender_mat.texture_slots.add()
                            color_tex_slot = blender_mat.texture_slots.add()
                            alpha_tex_slot = blender_mat.texture_slots.add()
                            mix_tex_slot.use = True
                            color_tex_slot.use = True
                            alpha_tex_slot.use = True

                            mix_tex = mix_tex_slot.texture = bpy.data.textures.new('Lux::%s' % tex.name, 'NONE')
                            color_tex = color_tex_slot.texture = bpy.data.textures.new('Lux::color:%s' % tex.name,
                                                                                       'NONE')
                            alpha_tex = alpha_tex_slot.texture = bpy.data.textures.new('Lux::alpha:%s' % tex.name,
                                                                                       'NONE')
                            mix_lux_tex = mix_tex.luxrender_texture
                            lux_tex = color_tex.luxrender_texture
                            alpha_lux_tex = alpha_tex.luxrender_texture

                            col_ramp = tex.color_ramp.elements
                            mix_lux_tex.type = 'mix'
                            lux_tex.type = 'band'
                            alpha_lux_tex.type = 'band'
                            mix_params = mix_lux_tex.luxrender_tex_mix
                            color_params = lux_tex.luxrender_tex_band
                            alpha_params = alpha_lux_tex.luxrender_tex_band

                            color_params.variant = 'color'
                            color_params.noffsets = len(col_ramp)
                            color_params.amount_usefloattexture = True
                            color_params.amount_floattexturename = tex.name
                            alpha_params.variant = 'float'
                            alpha_params.noffsets = len(col_ramp)
                            alpha_params.amount_usefloattexture = True
                            alpha_params.amount_floattexturename = tex.name
                            mix_params.variant = 'color'
                            mix_params.amount_usefloattexture = True
                            mix_params.amount_floattexturename = alpha_tex.name
                            mix_params.tex1_usecolortexture = False
                            mix_params.tex1_color = blender_mat.diffuse_color
                            mix_params.tex2_usecolortexture = True
                            mix_params.tex2_colortexturename = color_tex.name

                            for i in range(len(col_ramp)):
                                if hasattr(color_params, 'offsetcolor%d' % (i + 1)):
                                    setattr(color_params, 'offsetcolor%d' % (i + 1), col_ramp[i].position)
                                    setattr(alpha_params, 'offsetfloat%d' % (i + 1), col_ramp[i].position)
                                    setattr(color_params, 'tex%d_color' % (i + 1),
                                            (col_ramp[i].color[0], col_ramp[i].color[1], col_ramp[i].color[2]))
                                    setattr(alpha_params, 'tex%d_floatvalue' % (i + 1), col_ramp[i].color[3])

                            luxmat.Kd_usecolortexture = True
                            luxmat.Kd_colortexturename = mix_tex.name
                    pass
            elif len(Kd_stack) > 1:
                # TODO - set up a mix stack.
                # check there are enough free empty texture slots !
                if (len(Kd_stack) * 3 - 1) < 18:
                    for n in range(len(Kd_stack)):
                        tex = Kd_stack[n][0]
                        dcf = Kd_stack[n][1]
                        color = Kd_stack[n][2]

                        if tex.use_color_ramp:
                            # TODO: Implement band texture conversion
                            mix_tex_slot = blender_mat.texture_slots.add()
                            alpha_tex_slot = blender_mat.texture_slots.add()
                            color_tex_slot = blender_mat.texture_slots.add()
                            mix_tex_slot.use = True
                            color_tex_slot.use = True
                            alpha_tex_slot.use = True
                            mix_tex = mix_tex_slot.texture = bpy.data.textures.new('Lux::%s' % tex.name, 'NONE')
                            color_tex = color_tex_slot.texture = bpy.data.textures.new('Lux::color:%s' % tex.name,
                                                                                       'NONE')
                            alpha_tex = alpha_tex_slot.texture = bpy.data.textures.new('Lux::alpha:%s' % tex.name,
                                                                                       'NONE')

                            Lux_TexName.append(mix_tex.name)

                            mix_lux_tex = mix_tex.luxrender_texture
                            color_lux_tex = color_tex.luxrender_texture
                            alpha_lux_tex = alpha_tex.luxrender_texture

                            mix_params = mix_lux_tex.luxrender_tex_mix
                            mix_params.variant = 'color'
                            mix_params.amount_floatvalue = dcf
                            mix_params.amount_usefloattexture = True

                            col_ramp = tex.color_ramp.elements
                            mix_lux_tex.type = 'mix'
                            color_lux_tex.type = 'band'
                            alpha_lux_tex.type = 'band'

                            color_params = color_lux_tex.luxrender_tex_band
                            alpha_params = alpha_lux_tex.luxrender_tex_band

                            color_params.variant = 'color'
                            color_params.noffsets = len(col_ramp)
                            color_params.amount_usefloattexture = True
                            color_params.amount_floattexturename = tex.name

                            alpha_params.variant = 'float'
                            alpha_params.noffsets = len(col_ramp)
                            alpha_params.amount_usefloattexture = True
                            alpha_params.amount_floattexturename = tex.name

                            for i in range(len(col_ramp)):
                                if hasattr(color_params, 'offsetcolor%d' % (i + 1)):
                                    setattr(color_params, 'offsetcolor%d' % (i + 1), col_ramp[i].position)
                                    setattr(alpha_params, 'offsetfloat%d' % (i + 1), col_ramp[i].position)
                                    setattr(color_params, 'tex%d_color' % (i + 1),
                                            (col_ramp[i].color[0], col_ramp[i].color[1], col_ramp[i].color[2]))
                                    setattr(alpha_params, 'tex%d_floatvalue' % (i + 1), col_ramp[i].color[3])

                            mix_params.amount_floattexturename = alpha_tex.name
                            mix_params.amount_multiplyfloat = True
                            mix_params.tex2_usecolortexture = True
                            mix_params.tex2_colortexturename = color_tex.name

                            if n == 0:
                                mix_params.tex1_color = blender_mat.diffuse_color

                            else:
                                mix_params.tex1_usecolortexture = True
                                mix_params.tex1_colortexturename = Lux_TexName[n - 1]
                        else:
                            # Add mix texture for blender internal textures
                            mix_tex_slot = blender_mat.texture_slots.add()
                            mix_tex_slot.use = True
                            mix_tex = mix_tex_slot.texture = bpy.data.textures.new('Lux::%s' % tex.name, 'NONE')
                            Lux_TexName.append(mix_tex.name)
                            mix_lux_tex = mix_tex.luxrender_texture
                            mix_lux_tex.type = 'mix'
                            mix_params = mix_lux_tex.luxrender_tex_mix
                            mix_params.variant = 'color'
                            mix_params.amount_floatvalue = dcf
                            mix_params.amount_usefloattexture = True
                            mix_params.amount_floattexturename = tex.name
                            mix_params.amount_multiplyfloat = True
                            mix_params.tex2_color = color
                            if n == 0:
                                mix_params.tex1_color = blender_mat.diffuse_color
                            else:
                                mix_params.tex1_usecolortexture = True
                                mix_params.tex1_colortexturename = Lux_TexName[n - 1]

                    luxmat.Kd_usecolortexture = True
                    luxmat.Kd_colortexturename = mix_tex.name

                pass
                # else:
                #luxmat.Kd_usecolortexture = False

        if luxrender_mat.type in ('glossy'):
            if len(Ks_stack) == 1:
                tex = Ks_stack[0][0]
                variant = tex.luxrender_texture.get_paramset(scene, tex)[0]
                if variant == 'color':
                    # assign the texture directly
                    luxmat.Ks_usecolortexture = True
                    luxmat.Ks_colortexturename = tex.name
                    luxmat.Ks_color = [i * Ks_stack[0][1] for i in luxmat.Ks_color]
                    luxmat.Ks_multiplycolor = True
                else:
                    # TODO - insert mix texture
                    # check there are enough free empty texture slots !
                    pass
            elif len(Ks_stack) > 1:
                # TODO - set up a mix stack.
                # check there are enough free empty texture slots !
                pass
            else:
                luxmat.Ks_usecolortexture = False

        if bump_tex is not None:
            tex = bump_tex[0]
            variant = tex.luxrender_texture.get_paramset(scene, tex)[0]
            if variant == 'float':
                luxrender_mat.bumpmap_usefloattexture = True
                luxrender_mat.bumpmap_floattexturename = tex.name
                luxrender_mat.bumpmap_floatvalue = bump_tex[1] / 50.0  # ASV
                luxrender_mat.bumpmap_multiplyfloat = True
            else:
                # TODO - insert mix texture
                # check there are enough free empty texture slots !
                pass
        else:
            luxrender_mat.bumpmap_floatvalue = 0.0
            luxrender_mat.bumpmap_usefloattexture = False

        report({'INFO'}, 'Converted blender material "%s"' % blender_mat.name)
        return {'FINISHED'}
    except Exception as err:
        report({'ERROR'}, 'Cannot convert material: %s' % err)
        # print('Material conversion failed on line %d' % err.__traceback__.tb_lineno)
        return {'CANCELLED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_material_reset(bpy.types.Operator):
    bl_idname = 'luxrender.material_reset'
    bl_label = 'Reset material to defaults'

    def execute(self, context):
        if context.material and hasattr(context.material, 'luxrender_material'):
            context.material.luxrender_material.reset(prnt=context.material)
        return {'FINISHED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_convert_all_materials(bpy.types.Operator):
    bl_idname = 'luxrender.convert_all_materials'
    bl_label = 'Convert all Blender materials'

    def report_log(self, level, msg):
        LuxLog('Material conversion %s: %s' % (level, msg))

    def execute(self, context):
        for blender_mat in bpy.data.materials:
            # Don't convert materials from linked-in files
            if blender_mat.library is None:
                material_converter(self.report_log, context.scene, blender_mat)
        return {'FINISHED'}


@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_convert_material(bpy.types.Operator):
    bl_idname = 'luxrender.convert_material'
    bl_label = 'Convert selected Blender material'

    material_name = bpy.props.StringProperty(default='')

    def execute(self, context):
        if not self.properties.material_name:
            blender_mat = context.material
        else:
            blender_mat = bpy.data.materials[self.properties.material_name]

        material_converter(self.report, context.scene, blender_mat)
        return {'FINISHED'}
        
@LuxRenderAddon.addon_register_class
class ConfirmDialog(bpy.types.Operator):
    """
    Shows a popup and asks for confirmation (user has to press OK button)
    Written for use inside proxy export operator
    """

    bl_idname = "luxrender.confirm_dialog_operator"
    bl_label = "Overwrite Existing PLY File?"

    ask_again = bpy.props.BoolProperty(default=False, name="Ask again")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
       
class InvalidGeometryException(Exception):
    pass

class UnexportableObjectException(Exception):
    pass
        
@LuxRenderAddon.addon_register_class
class LUXRENDER_OT_export_luxrender_proxy(bpy.types.Operator):
    """Export an object as ply file, replace the original mesh with a preview version and set path to the exported ply file."""
    
    bl_idname = 'export.export_luxrender_proxy'
    bl_label = 'Export as LuxRender Proxy'
    bl_description = 'Converts selected objects to LuxRender proxies (simple preview geometry, original mesh is loaded at rendertime)'

    original_facecount = bpy.props.IntProperty(name = 'Original Facecount', default = 1)
    # hidden properties
    directory = bpy.props.StringProperty(name = 'PLY directory')
    filter_glob = bpy.props.StringProperty(default = '*.ply', options = {'HIDDEN'})
    use_filter = bpy.props.BoolProperty(default = True, options = {'HIDDEN'})

    def set_proxy_facecount(self, value):
        self["proxy_facecount"] = value
        self["proxy_quality"] = float(value) / float(self.original_facecount)

    def get_proxy_facecount(self):
        try:
            return self["proxy_facecount"]
        except KeyError:
            print("keyerror in get proxy facecount")
            return 0

    def set_proxy_quality(self, value):
        self["proxy_quality"] = value
        self["proxy_facecount"] = self.original_facecount * self.proxy_quality

    def get_proxy_quality(self):
        try:
            return self["proxy_quality"]
        except KeyError:
            print("keyerror in get proxy quality")
            return .5

    proxy_facecount = bpy.props.IntProperty(name = 'Proxy Facecount',
                                            min = 1,
                                            default = 5000,
                                            subtype = 'UNSIGNED',
                                            set = set_proxy_facecount,
                                            get = get_proxy_facecount)
    proxy_quality = bpy.props.FloatProperty(name = 'Preview Mesh Quality',
                                            default = 0.02,
                                            soft_min = 0.001,
                                            max = 1.0,
                                            soft_max = 0.5,
                                            subtype = 'UNSIGNED',
                                            set = set_proxy_quality,
                                            get = get_proxy_quality)

    overwrite = bpy.props.BoolProperty(default = True, name = "Overwrite Existing Files")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)

        active_obj = context.active_object
        if active_obj is not None:
            test_mesh = active_obj.to_mesh(context.scene, True, 'RENDER')
            self.original_facecount = len(test_mesh.polygons) * 2
            bpy.data.meshes.remove(test_mesh)

        self.proxy_facecount = 5000

        return {'RUNNING_MODAL'}

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT']:
                # make sure mesh has only one user (is NOT duplicated with Alt+D
                if obj.data.users > 1:
                    print("[Object: %s] Can't make proxy from multiuser mesh" % obj.name)
                    print("-----------------")
                    continue

                #################################################################
                # Prepare object for PLY export
                #################################################################
                # don't make curves a proxy when their geometry contains no faces
                if obj.type == 'CURVE':
                    test_mesh = obj.to_mesh(context.scene, True, 'RENDER')
                    if len(test_mesh.polygons) == 0:
                        print("[Object: %s] Skipping curve object because of missing faces" % obj.name)
                        print("-----------------")
                        continue
                    bpy.data.meshes.remove(test_mesh)

                # make sure object is of type 'MESH'
                if obj.type in ['CURVE', 'SURFACE', 'META', 'FONT']:
                    bpy.ops.object.convert(target = 'MESH')

                # rename object
                obj.name = obj.name + '_lux_proxy'

                # apply all modifiers
                bpy.ops.object.mode_set(mode = 'OBJECT')
                context.scene.objects.active = obj
                for modifier in obj.modifiers:
                    bpy.ops.object.modifier_apply(modifier = modifier.name)

                # find out how many materials are actually used
                used_material_indices = []
                for face in obj.data.polygons:
                    mi = face.material_index
                    if mi not in used_material_indices:
                        used_material_indices.append(mi)
                used_materials_amount = len(used_material_indices)

                # save bounding box for later use
                dimensions = obj.dimensions.copy()
                # clear parent
                bpy.ops.object.parent_clear(type = 'CLEAR_KEEP_TRANSFORM')

                # split object by materials
                bpy.ops.mesh.separate(type = 'MATERIAL')

                # create list of references to the created objects
                names = [obj.name]
                for i in range(0, used_materials_amount - 1):
                    names.append('%s.%03d' % (obj.name, i + 1))

                created_objects = []
                for name in names:
                    created_objects.append(bpy.data.objects[name])

                # create bounding box cube and parent objects to it
                if used_materials_amount > 1:
                    bpy.ops.mesh.primitive_cube_add(rotation = obj.rotation_euler,
                                                    location = obj.location,
                                                    layers = obj.layers)

                    bounding_cube = context.active_object
                    bounding_cube.name = obj.name + '_boundingBox'
                    bounding_cube.draw_type = 'WIRE'
                    bounding_cube.hide_render = True

                    bounding_cube.dimensions = dimensions
                    bpy.ops.object.transform_apply(location = False,
                                                   rotation = False,
                                                   scale = True)

                    for object in created_objects:
                        object.select = True
                        bpy.ops.object.parent_set(type = 'OBJECT', keep_transform = False)
                        object.select = False

                #################################################################
                # Export split objects to PLY files
                #################################################################
                for object in created_objects:
                    proxy_mesh, ply_path = self.export_ply(context, object)

                    if proxy_mesh is None or ply_path is None:
                        print("[Object: %s] Could not export object" % object.name)
                        continue

                    #################################################################
                    # Create lowpoly preview mesh with decimate modifier
                    #################################################################
                    context.scene.objects.active = object
                    decimate = object.modifiers.new('proxy_decimate', 'DECIMATE')
                    decimate.ratio = self.proxy_quality
                    bpy.ops.object.modifier_apply(apply_as = 'DATA', modifier = decimate.name)

                    #################################################################
                    # Set exported PLY as proxy file
                    #################################################################
                    object.luxrender_object.append_proxy = True

                    # check if the object had smooth faces

                    was_smooth = False
                    for poly in proxy_mesh.polygons:
                        if poly.use_smooth:
                            was_smooth = True
                            break

                    if was_smooth:
                        object.luxrender_object.use_smoothing = True

                    # set path to PLY
                    object.luxrender_object.external_mesh = ply_path

                    print("[Object: %s] Created proxy object" % object.name)
                    print("-----------------")
            
        return {'FINISHED'}

    def export_ply(self, context, obj):
        try:
            ply_path = None
            mesh = obj.to_mesh(context.scene, True, 'RENDER')
            if mesh is None:
                raise UnexportableObjectException('Failed to create export mesh from Blender object')
            mesh.name = obj.data.name + '_proxy'
            print('[Object: %s] Exporting PLY...' % obj.name)

            # Collate faces by mat index
            ffaces_mats = {}
            mesh_faces = mesh.tessfaces

            for f in mesh_faces:
                mi = f.material_index

                if mi not in ffaces_mats.keys():
                    ffaces_mats[mi] = []
                ffaces_mats[mi].append(f)

            material_indices = ffaces_mats.keys()
            number_of_mats = len(mesh.materials)

            if number_of_mats > 0:
                iterator_range = range(number_of_mats)
            else:
                iterator_range = [0]

            for i in iterator_range:
                try:
                    if i not in material_indices:
                        continue

                    def make_plyfilename():
                        _mesh_name = '%s_m%03d' % (obj.data.name, i)
                        _ply_filename = '%s.ply' % bpy.path.clean_name(_mesh_name)
                        _ply_path = self.directory + _ply_filename

                        return _mesh_name, _ply_path

                    mesh_name, ply_path = make_plyfilename()

                    if (not os.path.exists(ply_path) or self.overwrite) and not obj.luxrender_object.append_proxy:
                        uv_textures = mesh.tessface_uv_textures
                        vertex_color = mesh.tessface_vertex_colors.active

                        uv_layer = None
                        vertex_color_layer = None

                        if len(uv_textures) > 0:
                            if mesh.uv_textures.active and uv_textures.active.data:
                                uv_layer = uv_textures.active.data

                        if vertex_color:
                            vertex_color_layer = vertex_color.data

                        # Here we work out exactly which vert+normal combinations
                        # we need to export. This is done first, and the export
                        # combinations cached before writing to file because the
                        # number of verts needed needs to be written in the header
                        # and that number is not known before this is done.

                        # Export data
                        co_no_uv_vc_cache = []
                        face_vert_indices = {}  # mapping of face index to list of exported vert indices for that face

                        # Caches
                        # mapping of vert index to exported vert index for verts with vert normals

                        vert_vno_indices = {}
                        vert_use_vno = set()  # Set of vert indices that use vert normals
                        vert_index = 0  # exported vert index

                        c1 = c2 = c3 = c4 = None

                        for fidx, face in enumerate(ffaces_mats[i]):
                            fvi = []
                            if vertex_color_layer:
                                c1 = vertex_color_layer[fidx].color1
                                c2 = vertex_color_layer[fidx].color2
                                c3 = vertex_color_layer[fidx].color3
                                c4 = vertex_color_layer[fidx].color4

                            for j, vertex in enumerate(face.vertices):
                                v = mesh.vertices[vertex]

                                if vertex_color_layer:
                                    if j == 0:
                                        vert_col = c1
                                    elif j == 1:
                                        vert_col = c2
                                    elif j == 2:
                                        vert_col = c3
                                    elif j == 3:
                                        vert_col = c4

                                if face.use_smooth:
                                    if uv_layer:
                                        if vertex_color_layer:
                                            vert_data = (v.co[:], v.normal[:], uv_layer[face.index].uv[j][:],
                                                         (int(255 * vert_col[0]),
                                                          int(255 * vert_col[1]),
                                                          int(255 * vert_col[2]))[:])
                                        else:
                                            vert_data = (v.co[:], v.normal[:], uv_layer[face.index].uv[j][:])
                                    else:
                                        if vertex_color_layer:
                                            vert_data = (v.co[:], v.normal[:],
                                                         (int(255 * vert_col[0]),
                                                          int(255 * vert_col[1]),
                                                          int(255 * vert_col[2]))[:])
                                        else:
                                            vert_data = (v.co[:], v.normal[:])

                                    if vert_data not in vert_use_vno:
                                        vert_use_vno.add(vert_data)

                                        co_no_uv_vc_cache.append(vert_data)

                                        vert_vno_indices[vert_data] = vert_index
                                        fvi.append(vert_index)

                                        vert_index += 1
                                    else:
                                        fvi.append(vert_vno_indices[vert_data])
                                else:
                                    if uv_layer:
                                        if vertex_color_layer:
                                            vert_data = (v.co[:], face.normal[:], uv_layer[face.index].uv[j][:],
                                                         (int(255 * vert_col[0]),
                                                          int(255 * vert_col[1]),
                                                          int(255 * vert_col[2]))[:])
                                        else:
                                            vert_data = (v.co[:], face.normal[:], uv_layer[face.index].uv[j][:])
                                    else:
                                        if vertex_color_layer:
                                            vert_data = (v.co[:], face.normal[:],
                                                         (int(255 * vert_col[0]),
                                                          int(255 * vert_col[1]),
                                                          int(255 * vert_col[2]))[:])
                                        else:
                                            vert_data = (v.co[:], face.normal[:])

                                    # All face-vert-co-no are unique, we cannot
                                    # cache them
                                    co_no_uv_vc_cache.append(vert_data)
                                    fvi.append(vert_index)
                                    vert_index += 1

                            face_vert_indices[face.index] = fvi

                        del vert_vno_indices
                        del vert_use_vno

                        with open(ply_path, 'wb') as ply:
                            ply.write(b'ply\n')
                            ply.write(b'format binary_little_endian 1.0\n')
                            ply.write(b'comment Created by LuxBlend 2.6 exporter for LuxRender - www.luxrender.net\n')

                            # vert_index == the number of actual verts needed
                            ply.write(('element vertex %d\n' % vert_index).encode())
                            ply.write(b'property float x\n')
                            ply.write(b'property float y\n')
                            ply.write(b'property float z\n')

                            ply.write(b'property float nx\n')
                            ply.write(b'property float ny\n')
                            ply.write(b'property float nz\n')

                            if uv_layer:
                                ply.write(b'property float s\n')
                                ply.write(b'property float t\n')

                            if vertex_color_layer:
                                ply.write(b'property uchar red\n')
                                ply.write(b'property uchar green\n')
                                ply.write(b'property uchar blue\n')

                            ply.write(('element face %d\n' % len(ffaces_mats[i])).encode())
                            ply.write(b'property list uchar uint vertex_indices\n')

                            ply.write(b'end_header\n')

                            # dump cached co/no/uv/vc
                            if uv_layer:
                                if vertex_color_layer:
                                    for co, no, uv, vc in co_no_uv_vc_cache:
                                        ply.write(struct.pack('<3f', *co))
                                        ply.write(struct.pack('<3f', *no))
                                        ply.write(struct.pack('<2f', *uv))
                                        ply.write(struct.pack('<3B', *vc))
                                else:
                                    for co, no, uv in co_no_uv_vc_cache:
                                        ply.write(struct.pack('<3f', *co))
                                        ply.write(struct.pack('<3f', *no))
                                        ply.write(struct.pack('<2f', *uv))
                            else:
                                if vertex_color_layer:
                                    for co, no, vc in co_no_uv_vc_cache:
                                        ply.write(struct.pack('<3f', *co))
                                        ply.write(struct.pack('<3f', *no))
                                        ply.write(struct.pack('<3B', *vc))
                                else:
                                    for co, no in co_no_uv_vc_cache:
                                        ply.write(struct.pack('<3f', *co))
                                        ply.write(struct.pack('<3f', *no))

                            # dump face vert indices
                            for face in ffaces_mats[i]:
                                lfvi = len(face_vert_indices[face.index])
                                ply.write(struct.pack('<B', lfvi))
                                ply.write(struct.pack('<%dI' % lfvi, *face_vert_indices[face.index]))

                            del co_no_uv_vc_cache
                            del face_vert_indices

                        print('[Object: %s] Binary PLY file written: %s' % (obj.name, ply_path))
                        return mesh, ply_path
                    else:
                        print('[Object: %s] PLY file %s already exists or object is already a proxy, skipping it' % (
                            obj.name, ply_path))

                except InvalidGeometryException as err:
                    print('[Object: %s] Mesh export failed, skipping this mesh: %s' % (obj.name, err))

            del ffaces_mats
            return mesh, ply_path

        except UnexportableObjectException as err:
            print('[Object: %s] Object export failed, skipping this object: %s' % (obj.name, err))
            return None, None

# Register operator in Blender File -> Export menu
proxy_menu_func = lambda self, context: self.layout.operator("export.export_luxrender_proxy", text="Export LuxRender Proxy")
bpy.types.INFO_MT_file_export.append(proxy_menu_func)

