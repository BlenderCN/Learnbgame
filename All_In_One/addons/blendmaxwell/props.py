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

import os
import math

import bpy
from bpy.props import PointerProperty, FloatProperty, IntProperty, BoolProperty, StringProperty, EnumProperty, FloatVectorProperty, IntVectorProperty, CollectionProperty
from bpy.types import PropertyGroup
from mathutils import Vector

from . import utils
from . import ops


class MaterialEditorCallbacks():
    def __init__(self):
        raise Exception("no instance of this..")
    
    def bsdf_weight_map_get(self):
        p = 'weight'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def bsdf_weight_map_set(self, v):
        p = 'weight'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def bsdf_reflectance_0_map_get(self):
        p = 'reflectance_0'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def bsdf_reflectance_0_map_set(self, v):
        p = 'reflectance_0'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def bsdf_reflectance_90_map_get(self):
        p = 'reflectance_90'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def bsdf_reflectance_90_map_set(self, v):
        p = 'reflectance_90'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def bsdf_transmittance_map_get(self):
        p = 'transmittance'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def bsdf_transmittance_map_set(self, v):
        p = 'transmittance'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def bsdf_roughness_map_get(self):
        p = 'roughness'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def bsdf_roughness_map_set(self, v):
        p = 'roughness'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def bsdf_bump_map_get(self):
        p = 'bump'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def bsdf_bump_map_set(self, v):
        p = 'bump'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def bsdf_anisotropy_map_get(self):
        p = 'anisotropy'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def bsdf_anisotropy_map_set(self, v):
        p = 'anisotropy'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def bsdf_anisotropy_angle_map_get(self):
        p = 'anisotropy_angle'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def bsdf_anisotropy_angle_map_set(self, v):
        p = 'anisotropy_angle'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def bsdf_single_sided_map_get(self):
        p = 'single_sided'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def bsdf_single_sided_map_set(self, v):
        p = 'single_sided'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def coating_thickness_map_get(self):
        p = 'thickness'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def coating_thickness_map_set(self, v):
        p = 'thickness'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def coating_reflectance_0_map_get(self):
        p = 'reflectance_0'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def coating_reflectance_0_map_set(self, v):
        p = 'reflectance_0'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def coating_reflectance_90_map_get(self):
        p = 'reflectance_90'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def coating_reflectance_90_map_set(self, v):
        p = 'reflectance_90'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def emitter_spot_map_get(self):
        p = 'spot'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def emitter_spot_map_set(self, v):
        p = 'spot'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def layer_opacity_map_get(self):
        p = 'opacity'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def layer_opacity_map_set(self, v):
        p = 'opacity'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def global_bump_map_get(self):
        p = 'global_bump'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def global_bump_map_set(self, v):
        p = 'global_bump'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def ext_emitter_spot_map_get(self):
        p = 'emitter_spot'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_emitter_spot_map_set(self, v):
        p = 'emitter_spot'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_map_enabled'.format(p)] = True
        else:
            self['{}_map_enabled'.format(p)] = False
    
    def ext_opaque_color_map_get(self):
        p = 'opaque_color'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_opaque_color_map_set(self, v):
        p = 'opaque_color'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_opaque_shininess_map_get(self):
        p = 'opaque_shininess'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_opaque_shininess_map_set(self, v):
        p = 'opaque_shininess'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_opaque_roughness_map_get(self):
        p = 'opaque_roughness'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_opaque_roughness_map_set(self, v):
        p = 'opaque_roughness'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_transparent_color_map_get(self):
        p = 'transparent_color'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_transparent_color_map_set(self, v):
        p = 'transparent_color'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_transparent_roughness_map_get(self):
        p = 'transparent_roughness'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_transparent_roughness_map_set(self, v):
        p = 'transparent_roughness'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_metal_color_map_get(self):
        p = 'metal_color'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_metal_color_map_set(self, v):
        p = 'metal_color'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_metal_roughness_map_get(self):
        p = 'metal_roughness'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_metal_roughness_map_set(self, v):
        p = 'metal_roughness'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_metal_anisotropy_map_get(self):
        p = 'metal_anisotropy'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_metal_anisotropy_map_set(self, v):
        p = 'metal_anisotropy'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_metal_angle_map_get(self):
        p = 'metal_angle'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_metal_angle_map_set(self, v):
        p = 'metal_angle'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_metal_dust_map_get(self):
        p = 'metal_dust'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_metal_dust_map_set(self, v):
        p = 'metal_dust'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_metal_perforation_map_get(self):
        p = 'metal_perforation'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_metal_perforation_map_set(self, v):
        p = 'metal_perforation'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_enabled'.format(p)] = True
        else:
            self['{}_enabled'.format(p)] = False
    
    def ext_translucent_color_map_get(self):
        p = 'translucent_color'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_translucent_color_map_set(self, v):
        p = 'translucent_color'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_translucent_roughness_map_get(self):
        p = 'translucent_roughness'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_translucent_roughness_map_set(self, v):
        p = 'translucent_roughness'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_hair_color_map_get(self):
        p = 'hair_color'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_hair_color_map_set(self, v):
        p = 'hair_color'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False
    
    def ext_hair_root_tip_weight_map_get(self):
        p = 'hair_root_tip_weight'
        try:
            return self['{}_map'.format(p)]
        except KeyError:
            return ''
    
    def ext_hair_root_tip_weight_map_set(self, v):
        p = 'hair_root_tip_weight'
        self['{}_map'.format(p)] = v
        if(v != ''):
            self['{}_type'.format(p)] = True
        else:
            self['{}_type'.format(p)] = False


class CustomAlphaGroupsProperties(PropertyGroup):
    custom_alpha_use = BoolProperty(name="Use", default=False, )
    custom_alpha_opaque = BoolProperty(name="Opaque", default=False, )
    
    @classmethod
    def register(cls):
        bpy.types.Group.maxwell_render = PointerProperty(type=cls)
    
    @classmethod
    def unregister(cls):
        del bpy.types.Group.maxwell_render


class ManualCustomAlphasObjectItem(PropertyGroup):
    name = StringProperty(name="Name", default="Layer", )


class ManualCustomAlphasMaterialItem(PropertyGroup):
    name = StringProperty(name="Name", default="Layer", )


class ManualCustomAlphaItem(PropertyGroup):
    name = StringProperty(name="Name", default="Custom Alpha", )
    objects = CollectionProperty(name="Objects", type=ManualCustomAlphasObjectItem, )
    materials = CollectionProperty(name="Materials", type=ManualCustomAlphasMaterialItem, )
    opaque = BoolProperty(name="Opaque", default=False, )
    o_index = IntProperty(name="Active Object", default=-1, )
    m_index = IntProperty(name="Active Material", default=-1, )


class ManualCustomAlphas(PropertyGroup):
    alphas = CollectionProperty(name="Alphas", type=ManualCustomAlphaItem, )
    index = IntProperty(name="Active", default=-1, )


class SceneProperties(PropertyGroup):
    lock_output_image = BoolProperty(default=False, options={'HIDDEN'}, )
    lock_output_mxi = BoolProperty(default=False, options={'HIDDEN'}, )
    
    def _output_depth_items(scene, context):
        items = [('RGB8', "RGB 8 bpc", "", 0),
                 ('RGB16', "RGB 16 bpc", "", 1),
                 ('RGB32', "RGB 32 bpc", "", 2), ]
        
        m = bpy.context.scene.maxwell_render
        e = os.path.splitext(os.path.split(m.output_image)[1])[1][1:].lower()
        v = ''
        if(e == "tga" or e == "jpg"):
            return items[:1]
        elif(e == "png"):
            return items[:2]
        else:
            return items
    
    def _output_file_types(scene, context):
        a = [('EXR32', "EXR 32", ""),
             ('EXR16', "EXR 16", ""),
             ('TIF32', "TIF 32", ""),
             ('TIF16', "TIF 16", ""),
             ('TIF8', "TIF 8", ""),
             ('PSD32', "PSD 32", ""),
             ('PSD16', "PSD 16", ""),
             ('PSD8', "PSD 8", ""),
             ('PNG16', "PNG 16", ""),
             ('PNG8', "PNG 8", ""),
             ('JPG', "JPG", ""),
             ('JP2', "JP2", ""),
             ('TGA', "TGA", ""), ]
        return a
    
    def _override_output_image(self, context):
        if(self.lock_output_image):
            return
        self.lock_output_image = True
        
        self.output_image = bpy.path.abspath(self.output_image)
        
        h, t = os.path.split(self.output_image)
        n, e = os.path.splitext(t)
        es = ['.png', '.psd', '.jpg', '.tga', '.tif', '.jp2', '.hdr', '.exr', '.bmp', ]
        if(not e.lower() in es):
            e = '.png'
        
        p = bpy.path.ensure_ext(self.output_image, e, case_sensitive=False, )
        if(p != self.output_image and p != e):
            self.output_image = p
        
        self.lock_output_image = False
    
    def _override_output_mxi(self, context):
        if(self.lock_output_mxi):
            return
        self.lock_output_mxi = True
        
        self.output_mxi = bpy.path.abspath(self.output_mxi)
        
        e = '.mxi'
        p = bpy.path.ensure_ext(self.output_mxi, '.mxi', case_sensitive=False, )
        if(p != self.output_mxi and p != e):
            self.output_mxi = p
        
        self.lock_output_mxi = False
    
    def _get_custom_alphas(self, context):
        r = []
        for i, g in enumerate(bpy.data.groups):
            gmx = g.maxwell_render
            if(gmx.custom_alpha_use):
                r.append((g.name, g.name, '', ))
        if(len(r) == 0):
            # return empty list if no groups in scene
            return [("0", "", ""), ]
        return r
    
    def _get_default_material():
        import platform
        p = platform.system()
        mp = ""
        if(p == 'Darwin'):
            # from . import system
            # mp = bpy.path.abspath(system.prefs().maxwell_path)
            mp = '/Applications/Maxwell 3/'
        elif(p == 'Linux'):
            mp = os.environ.get("MAXWELL3_ROOT")
        elif(p == 'Windows'):
            mp = os.environ.get("MAXWELL3_ROOT")
        if(mp != ""):
            m = os.path.abspath(os.path.join(mp, 'materials database', 'mxm files', 'default.mxm', ))
            if(os.path.exists(m)):
                return m
        return ""
    
    scene_time = IntProperty(name="Time (minutes)", default=60, min=1, max=50000, description="Maximum render time (in minutes) for the render", )
    scene_sampling_level = FloatProperty(name="Sampling Level", default=12.0, min=1.0, max=50.00, precision=2, description="Maximum sampling level required", )
    scene_multilight = EnumProperty(name="Multilight", items=[('DISABLED_0', "Disabled", ""), ('INTENSITY_1', "Intensity", ""), ('COLOR_2', "Color", "")], default='DISABLED_0', description="Multilight type", )
    scene_multilight_type = EnumProperty(name="Multilight Type", items=[('COMPOSITE_0', "Composite", ""), ('SEPARATE_1', "Separate", "")], default='COMPOSITE_0', description="Multilight layers type", )
    scene_cpu_threads = IntProperty(name="CPU Threads", default=0, min=0, max=1024, description="Number of CPU threads, set to 0 to use all", )
    # scene_priority = EnumProperty(name="Priority", items=[('LOW', "Low", ""), ('NORMAL', "Normal", "")], default='LOW', )
    scene_quality = EnumProperty(name="Quality", items=[('RS0', "Draft", ""), ('RS1', "Production", "")], default='RS1', description="Which type of render engine to use", )
    # scene_command_line = StringProperty(name="Command Line", default="", )
    
    output_depth = EnumProperty(name="Output Depth", items=_output_depth_items, description="Bit depth per channel for image output", )
    output_image_enabled = BoolProperty(name="Image", default=True, description="Render image", )
    output_image = StringProperty(name="Image", default="", subtype='FILE_PATH', description="Image path", update=_override_output_image, )
    output_mxi_enabled = BoolProperty(name="MXI", default=True, description="Render .MXI", )
    output_mxi = StringProperty(name="MXI", default="", subtype='FILE_PATH', description=".MXI path", update=_override_output_mxi, )
    
    materials_override = BoolProperty(name="Override", default=False, description="Override all materials in scene with one material", )
    materials_override_path = StringProperty(name="Override File", default="", subtype='FILE_PATH', description="Path to override material (.MXM)", )
    materials_search_path = StringProperty(name="Search Path", default="", subtype='DIR_PATH', description="Set the path where Studio should look for any textures and other files used in your scene to avoid 'missing textures' errors when rendering.", )
    materials_default_material = StringProperty(name="Default Material", default=_get_default_material(), subtype='FILE_PATH', )
    
    materials_directory = StringProperty(name="Default Material Directory", default="//", subtype='DIR_PATH', description="Default directory where new materials are created upon running operator 'Create Material'", )
    
    globals_motion_blur = BoolProperty(name="Motion Blur", default=False, description="Global enable/disable motion blur", )
    globals_motion_blur_num_substeps = IntProperty(name="Substeps", default=2, min=0, max=1000, description="Number of frame substeps, always value + 1, ie value of 2 will be exported as step when shutter is opened, one at the middle, and one wjen shutter is closed.", )
    globals_motion_blur_shutter_open_offset = FloatProperty(name="Shutter Open Offset", default=0.0, min=0.0, max=1.0, precision=2, subtype='PERCENTAGE', description="When set to 0, the shutter opens at the start of the frame, so the future movement is captured, while a value of 1 makes the shutter close at the start of the frame, so only the past movement is seen. A value of 0.5 centers the exposure interval on the current frame.", )
    globals_motion_blur_export = EnumProperty(name="Type", items=[('MOVEMENT_DEFORMATION', "Movement and Deformation", ""), ('MOVEMENT', "Movement", ""), ('NONE', "None", ""), ], default='MOVEMENT_DEFORMATION', )
    
    globals_diplacement = BoolProperty(name="Displacement", default=True, description="Global enable/disable displacement", )
    globals_dispersion = BoolProperty(name="Dispersion", default=True, description="Global enable/disable dispaersion", )
    
    extra_sampling_enabled = BoolProperty(name="Enabled", default=False, description="Enable rendering extra-sampling based on custom-alpha/alpha/user-input-bitmap.", )
    extra_sampling_sl = FloatProperty(name="Sampling Level", default=14.0, min=1.0, max=50.00, precision=2, description="Target SL when DO EXTRA SAMPLING is enabled.", )
    extra_sampling_mask = EnumProperty(name="Mask", items=[('CUSTOM_ALPHA_0', "Custom Alpha", ""), ('ALPHA_1', "Alpha", ""), ('BITMAP_2', "Bitmap", "")], default='CUSTOM_ALPHA_0', description="Sets the extra-sampling mask.", )
    extra_sampling_custom_alpha = EnumProperty(name="Mask", items=_get_custom_alphas, description="The name of the custom alpha to be used when mask is Custom Alpha.", )
    extra_sampling_user_bitmap = StringProperty(name="Bitmap", default="", subtype='FILE_PATH', description="Path of the image to use when mask is Birmap", )
    extra_sampling_invert = BoolProperty(name="Invert Mask", default=False, description="Inverts alpha mask for render extra-sampling.", )
    
    channels_output_mode = EnumProperty(name="Output Mode", items=[('SEPARATE_0', "Separate", ""), ('EMBEDDED_1', "Embedded", "")], default='SEPARATE_0', )
    channels_render = BoolProperty(name="Render", default=True, )
    channels_render_type = EnumProperty(name="Type", items=[('RENDER_LAYER_ALL_0', "All", ""),
                                                            ('RENDER_LAYER_DIFFUSE_1', "Diffuse", ""),
                                                            ('RENDER_LAYER_REFLECTIONS_2', "Reflections", ""),
                                                            ('RENDER_LAYER_REFRACTIONS_3', "Refractions", ""),
                                                            ('RENDER_LAYER_DIFFUSE_AND_REFLECTIONS_4', "Diffuse and Reflections", ""),
                                                            ('RENDER_LAYER_REFLECTIONS_AND_REFRACTIONS_5', "Reflections and Refractions", ""), ], default='RENDER_LAYER_ALL_0', )
    
    channels_alpha = BoolProperty(name="Alpha", default=False, )
    channels_alpha_file = EnumProperty(name="Alpha File", items=_output_file_types, )
    channels_alpha_opaque = BoolProperty(name="Opaque", default=False, )
    channels_z_buffer = BoolProperty(name="Z-buffer", default=False, )
    channels_z_buffer_file = EnumProperty(name="Z-buffer File", items=_output_file_types, )
    channels_z_buffer_near = FloatProperty(name="Near (m)", default=0.0, min=-100000.000, max=100000.000, precision=3, )
    channels_z_buffer_far = FloatProperty(name="Far (m)", default=0.0, min=-100000.000, max=100000.000, precision=3, )
    channels_shadow = BoolProperty(name="Shadow", default=False, )
    channels_shadow_file = EnumProperty(name="Shadow File", items=_output_file_types, )
    channels_material_id = BoolProperty(name="Material ID", default=False, )
    channels_material_id_file = EnumProperty(name="Material ID File", items=_output_file_types, )
    channels_object_id = BoolProperty(name="Object ID", default=False, )
    channels_object_id_file = EnumProperty(name="Object ID File", items=_output_file_types, )
    channels_motion_vector = BoolProperty(name="Motion Vector", default=False, )
    channels_motion_vector_file = EnumProperty(name="Motion Vector File", items=_output_file_types, )
    channels_roughness = BoolProperty(name="Roughness", default=False, )
    channels_roughness_file = EnumProperty(name="Roughness File", items=_output_file_types, )
    channels_fresnel = BoolProperty(name="Fresnel", default=False, )
    channels_fresnel_file = EnumProperty(name="Fresnel File", items=_output_file_types, )
    channels_normals = BoolProperty(name="Normals", default=False, )
    channels_normals_file = EnumProperty(name="Normals File", items=_output_file_types, )
    channels_normals_space = EnumProperty(name="Space", items=[('WORLD_0', "World", ""), ('CAMERA_1', "Camera", "")], default='WORLD_0', )
    channels_position = BoolProperty(name="Position", default=False, )
    channels_position_file = EnumProperty(name="Position File", items=_output_file_types, )
    channels_position_space = EnumProperty(name="Space", items=[('WORLD_0', "World", ""), ('CAMERA_1', "Camera", "")], default='WORLD_0', )
    channels_deep = BoolProperty(name="Deep", default=False, )
    channels_deep_file = EnumProperty(name="Deep File", items=[('EXR_DEEP', "EXR DEEP", ""), ('DTEX', "DTEX", "")], default='EXR_DEEP', )
    channels_deep_type = EnumProperty(name="Type", items=[('ALPHA_0', "Alpha", ""), ('RGBA_1', "RGBA", "")], default='ALPHA_0', )
    channels_deep_min_dist = FloatProperty(name="Min dist (m)", default=0.2, min=0.0, max=1000.000, precision=3, )
    channels_deep_max_samples = IntProperty(name="Max samples", default=20, min=1, max=100000, )
    channels_uv = BoolProperty(name="UV", default=False, )
    channels_uv_file = EnumProperty(name="UV File", items=_output_file_types, )
    channels_custom_alpha = BoolProperty(name="Custom Alpha", default=False, )
    channels_custom_alpha_file = EnumProperty(name="Custom Alpha File", items=_output_file_types, )
    channels_reflectance = BoolProperty(name="Reflectance", default=False, )
    channels_reflectance_file = EnumProperty(name="Reflectance File", items=_output_file_types, )
    
    tone_color_space = EnumProperty(name="Color Space",
                                    items=[('SRGB_0', "sRGB IEC61966-2.1", ""),
                                           ('ADOBE98_1', "Adobe RGB 98", ""),
                                           ('APPLE_2', "Apple RGB / SGI", ""),
                                           ('PAL_3', "PAL / SECAM (EBU3213)", ""),
                                           ('NTSC_4', "NTSC 1953", ""),
                                           ('NTSC1979_5', "NTSC 1979 (SMPTE-C)", ""),
                                           ('WIDEGAMUT_6', "Wide Gamut RGB", ""),
                                           ('PROPHOTO_7', "ProPhoto RGB (ROMM)", ""),
                                           ('ECIRRGB_8', "ECI RGB", ""),
                                           ('CIE1931_9', "CIE 1931", ""),
                                           ('BRUCERGB_10', "Bruce RGB", ""),
                                           ('COLORMATCH_11', "ColorMatch RGB", ""),
                                           ('BESTRGB_12', "Best RGB", ""),
                                           ('DONRGB4_13', "Don RGB 4", ""),
                                           ('HDTV_14', "HDTV (Rec.709)", ""),
                                           ('ACES_15', "ACES", ""), ],
                                    default='SRGB_0', description="Image color space", )
    tone_burn = FloatProperty(name="Burn", default=0.8, min=0.0, max=1.0, precision=2, description="Image burn value", )
    tone_gamma = FloatProperty(name="Monitor Gamma", default=2.20, min=0.10, max=3.50, precision=2, description="Image gamma value", )
    tone_sharpness = BoolProperty(name="Sharpness", default=False, description="Image sharpness", )
    tone_sharpness_value = FloatProperty(name="Sharpness", default=60.0, min=0.0, max=100.0, precision=2, description="Image sharpness value", subtype='PERCENTAGE', )
    tone_whitepoint = FloatProperty(name="White Point (K)", default=6500.0, min=2000.0, max=20000.0, precision=1, description="", )
    tone_tint = FloatProperty(name="Tint", default=0.0, min=-100.0, max=100.0, precision=1, description="", )
    
    simulens_aperture_map = StringProperty(name="Aperture Map", default="", subtype='FILE_PATH', description="Path to aperture map", )
    simulens_obstacle_map = StringProperty(name="Obstacle Map", default="", subtype='FILE_PATH', description="Path to obstacle map", )
    simulens_diffraction = BoolProperty(name="Diffraction", default=False, description="Use lens diffraction", )
    simulens_diffraction_value = FloatProperty(name="Diffraction Value", default=50.0, min=0.0, max=2500.0, precision=2, description="Lens diffraction value", )
    simulens_frequency = FloatProperty(name="Frequency", default=50.0, min=0.0, max=2500.0, precision=2, description="Lens frequency value", )
    simulens_scattering = BoolProperty(name="Scattering", default=False, description="Use lens scattering", )
    simulens_scattering_value = FloatProperty(name="Scattering Value", default=0.0, min=0.0, max=2500.0, precision=2, description="Lens scattering value", )
    simulens_devignetting = BoolProperty(name="Devigneting (%)", default=False, description="Use lens devignetting", )
    simulens_devignetting_value = FloatProperty(name="Devigneting", default=0.0, min=-100.0, max=100.0, precision=2, description="Lens devignetting value", )
    
    illum_caustics_illumination = EnumProperty(name="Illumination", items=[('BOTH_0', "Both", ""), ('DIRECT_1', "Direct", ""), ('INDIRECT_2', "Indirect", ""), ('NONE_3', "None", "")], default='BOTH_0', description="Illumination", )
    illum_caustics_refl_caustics = EnumProperty(name="Refl. Caustics", items=[('BOTH_0', "Both", ""), ('DIRECT_1', "Direct", ""), ('INDIRECT_2', "Indirect", ""), ('NONE_3', "None", "")], default='BOTH_0', description="Reflection caustics", )
    illum_caustics_refr_caustics = EnumProperty(name="Refr. Caustics", items=[('BOTH_0', "Both", ""), ('DIRECT_1', "Direct", ""), ('INDIRECT_2', "Indirect", ""), ('NONE_3', "None", "")], default='BOTH_0', description="Refraction caustics", )
    
    overlay_enabled = BoolProperty(name="Overlay", default=False, )
    overlay_text = StringProperty(name="Overlay Text", default="", )
    overlay_position = EnumProperty(name="Position", items=[('BOTTOM_0', "Bottom", ""), ('TOP_1', "Top", "")], default='BOTTOM_0', )
    overlay_color = FloatVectorProperty(name="Color", description="", default=[v ** 2.2 for v in (26 / 255, 26 / 255, 26 / 255)], min=0.0, max=1.0, subtype='COLOR', )
    overlay_background = BoolProperty(name="Background", default=False, )
    overlay_background_color = FloatVectorProperty(name="Background Color", description="", default=[v ** 2.2 for v in (178 / 255, 178 / 255, 178 / 255)], min=0.0, max=1.0, subtype='COLOR', )
    
    export_protect_mxs = BoolProperty(name="Protect MXS", default=False, description="Protect MXS from importing.", )
    
    export_output_directory = StringProperty(name="Output Directory", subtype='DIR_PATH', default="//", description="Output directory for Maxwell scene (.MXS) file", )
    export_use_instances = BoolProperty(name="Use Instances", default=True, description="Convert multi-user mesh objects to instances", )
    export_keep_intermediates = BoolProperty(name="Keep Intermediates", default=False, description="Do not remove intermediate files used for scene export (usable only for debugging purposes)", )
    
    export_open_with = EnumProperty(name="Open With", items=[('STUDIO', "Studio", ""), ('MAXWELL', "Maxwell", ""), ('NONE', "None", "")], default='STUDIO', description="After export, open in ...", )
    instance_app = BoolProperty(name="Open a new instance of application", default=False, description="Open a new instance of the application even if one is already running", )
    
    export_use_wireframe = BoolProperty(name="Wireframe", default=False, description="Wireframe and Clay scene export", )
    export_wire_edge_radius = FloatProperty(name="Edge Radius", default=0.00025, min=0.0, max=1.0, precision=6, description="Wireframe edge radius (meters)", )
    export_wire_edge_resolution = IntProperty(name="Edge Resolution", default=32, min=3, max=128, description="Wireframe edge resolution", )
    export_clay_override_object_material = BoolProperty(name="Override Object Material", default=True, )
    export_wire_wire_material = StringProperty(name="Wire Material", default="", )
    export_wire_clay_material = StringProperty(name="Clay Material", default="", )
    
    export_overwrite = BoolProperty(name="Overwrite Existing", default=True, description="", )
    export_incremental = BoolProperty(name="Incremental", default=False, description="Always export a new file", )
    
    export_log_open = BoolProperty(name="Open Log", default=False, description="Open export log in text editor when finished", )
    export_warning_log_write = BoolProperty(name="Write Log", default=True, description="Write log file next to scene file on warnings. When running blender from terminal you can skip that and read warnings in it.", )
    export_suppress_warning_popups = BoolProperty(name="Suppress Warnings", default=False, description="Don't popup number of warnings next to mouse cursor.", )
    
    export_remove_unused_materials = BoolProperty(name="Remove Unused Materials", default=False, description="Remove all materials that is not used by any object in scene. Might not work as intended in 3.1.99.9.", )
    export_use_subdivision = BoolProperty(name="Use Subdivision Modifiers", default=False, description="Export all Subdivision modifiers if they are Catmull-Clark type and at the end of modifier stack on regular mesh objects. Manually added Subdivision will override automatic one.", )
    
    exporting_animation_now = BoolProperty(default=False, options={'HIDDEN'}, )
    exporting_animation_frame_number = IntProperty(default=1, options={'HIDDEN'}, )
    exporting_animation_first_frame = BoolProperty(default=True, options={'HIDDEN'}, )
    private_name = StringProperty(default="", options={'HIDDEN'}, )
    private_increment = StringProperty(default="", options={'HIDDEN'}, )
    private_suffix = StringProperty(default="", options={'HIDDEN'}, )
    private_path = StringProperty(default="", options={'HIDDEN'}, )
    private_basepath = StringProperty(default="", options={'HIDDEN'}, )
    private_image = StringProperty(default="", options={'HIDDEN'}, )
    private_mxi = StringProperty(default="", options={'HIDDEN'}, )
    
    blocked_emitters_deep_check = BoolProperty(name="Deep Check", default=False, description="Check object materials for emitter layer. Might be very slow on Mac OS X..", )
    
    custom_alphas_use_groups = BoolProperty(name="Use Object Groups", default=False, description="", )
    custom_alphas_manual = PointerProperty(name="Manual Custom Alphas", type=ManualCustomAlphas, )
    
    private_draw_references = bpy.props.IntProperty(name="Draw MXS References in Viewport", default=0, )
    
    material_preview_show = BoolProperty(name="Options", default=False, )
    material_preview_sl = IntProperty(name="Sampling Level", default=10, min=1, max=25, )
    material_preview_time = IntProperty(name="Time Limit (m)", default=1, min=1, max=10, )
    material_preview_scale = IntProperty(name="Scale (%)", default=100, min=20, max=100, subtype='PERCENTAGE', )
    material_preview_quality = EnumProperty(name="Quality", items=[('RS0', "Draft", ""), ('RS1', "Production", "")], default='RS0', )
    material_preview_external = BoolProperty(name="Load Preview From Referenced MXMs", default=True, description="Prefer loading preview from referenced MXMs, rendering will start only when MXM has no saved preview. Uncheck to always render preview.", )
    material_preview_verbosity = IntProperty(name="Verbosity Level", default=1, min=0, max=4, description="0: no information given, 1: errors, 2: warnings, 3: info, 4: all", )
    material_preview_enable = BoolProperty(name="Enable Material Preview Rendering", default=False, )
    
    viewport_render_enabled = BoolProperty(name="Enabled", default=False, )
    viewport_render_sl = IntProperty(name="Sampling Level", default=10, min=1, max=25, )
    viewport_render_time = IntProperty(name="Time Limit (m)", default=10, min=1, max=60, )
    viewport_render_quality = EnumProperty(name="Quality", items=[('RS0', "Draft", ""), ('RS1', "Production", "")], default='RS1', )
    viewport_render_verbosity = IntProperty(name="Verbosity Level", default=1, min=0, max=4, description="0: no information given, 1: errors, 2: warnings, 3: info, 4: all", )
    viewport_render_autofocus = BoolProperty(name="Autofocus Viewport Camera", default=True, description="Focus camera on object in center if available, otherwise focus distance will be taken from active camera", )
    viewport_render_update_interval = FloatProperty(name="Update Interval (s)", default=3.0, min=1.0, max=15.0, precision=1, )
    
    @classmethod
    def register(cls):
        bpy.types.Scene.maxwell_render = PointerProperty(type=cls)
    
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.maxwell_render


class EnvironmentProperties(PropertyGroup):
    def _gmt_auto(self, context):
        if(self.sun_latlong_gmt_auto):
            # http://stackoverflow.com/questions/1058342/rough-estimate-of-the-time-offset-from-gmt-from-latitude-longitude
            # direction is 1 for east, -1 for west, and longitude is in (-180,180)
            # not sure which to choose, prague is gmt+1 and longitude ~14, and it works for this combination..
            offset = 1 * self.sun_latlong_lon * 24 / 360
            self.sun_latlong_gmt = round(offset)
    
    lock_sun_color = BoolProperty(default=False, options={'HIDDEN'}, )
    
    def update_sun_color(self, context):
        if(self.sun_type != 'PHYSICAL'):
            return
        if(self.lock_sun_color):
            return
        self.lock_sun_color = True
        self.sun_color = utils.color_temperature_to_rgb(self.sun_temp)
        self.lock_sun_color = False
    
    env_type = EnumProperty(name="Type", items=[('NONE', "None", ""), ('PHYSICAL_SKY', "Physical Sky", ""), ('IMAGE_BASED', "Image Based", "")], default='PHYSICAL_SKY', description="Environment type", )
    
    sky_type = EnumProperty(name="Type", items=[('PHYSICAL', "Physical", ""), ('CONSTANT', "Constant Dome", "")], default='PHYSICAL', description="Sky type", )
    
    sky_use_preset = BoolProperty(name="Use Sky Preset", default=False, description="Use saved sky preset", )
    sky_preset = StringProperty(name="Sky Preset", default="", subtype='FILE_PATH', description="Saved sky preset path (.SKY)", )
    
    sky_intensity = FloatProperty(name="Intensity", default=1.0, min=0.0, max=10000.00, precision=2, )
    sky_planet_refl = FloatProperty(name="Planet Refl (%)", default=25.0, min=1.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    sky_ozone = FloatProperty(name="Ozone (cm)", default=0.4, min=0.0, max=50.0, precision=3, )
    sky_water = FloatProperty(name="Water (cm)", default=2.0, min=0.0, max=500.0, precision=3, )
    sky_turbidity_coeff = FloatProperty(name="Turbidity Coeff", default=0.040, min=0.0, max=10.0, precision=3, )
    sky_wavelength_exp = FloatProperty(name="Wavelength Exp", default=1.200, min=0.0, max=300.000, precision=3, )
    sky_reflectance = FloatProperty(name="Reflectance (%)", default=80.0, min=0.0, max=100.0, precision=3, subtype='PERCENTAGE', )
    sky_asymmetry = FloatProperty(name="Assymetry", default=0.7, min=-0.999, max=0.999, precision=3, )
    
    dome_intensity = FloatProperty(name="Intensity (cd/m)", default=10000.0, min=0.0, max=1000000.0, precision=1, )
    dome_zenith = FloatVectorProperty(name="Zenith Color", default=(1.0, 1.0, 1.0), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    dome_horizon = FloatVectorProperty(name="Horizon Color", default=(1.0, 1.0, 1.0), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    dome_mid_point = FloatProperty(name="Mid Point", default=math.radians(45.000), min=math.radians(0.000), max=math.radians(90.000), precision=1, subtype='ANGLE', )
    
    use_sun_lamp = BoolProperty(name="Use Sun Lamp", default=False, description="Use specific Sun lamp.", )
    sun_lamp = StringProperty(name="Sun Lamp", default="", )
    
    sun_type = EnumProperty(name="Type", items=[('DISABLED', "Disabled", ""), ('PHYSICAL', "Physical", ""), ('CUSTOM', "Custom", "")], default='PHYSICAL', update=update_sun_color, )
    sun_power = FloatProperty(name="Power", default=1.0, min=0.010, max=100.000, precision=3, )
    sun_radius_factor = FloatProperty(name="Radius Factor (x)", default=1.0, min=0.01, max=100.00, precision=2, )
    sun_temp = FloatProperty(name="Temperature (K)", default=5776.0, min=1.0, max=10000.0, precision=1, update=update_sun_color, )
    sun_color = FloatVectorProperty(name="Color", default=(1.0, 1.0, 1.0), min=0.0, max=1.0, precision=2, subtype='COLOR', update=update_sun_color, )
    sun_location_type = EnumProperty(name="Location", items=[('LATLONG', "Lat / Long", ""), ('ANGLES', "Angles", ""), ('DIRECTION', "Direction", "")], default='DIRECTION', )
    sun_latlong_lat = FloatProperty(name="Lat", default=40.000, min=-90.000, max=90.000, precision=3, )
    sun_latlong_lon = FloatProperty(name="Long", default=-3.000, min=-180.000, max=180.000, precision=3, update=_gmt_auto, )
    
    sun_date = StringProperty(name="Date", default="DD.MM.YYYY", description="Date in format DD.MM.YYYY", )
    sun_time = StringProperty(name="Time", default="HH:MM", description="Time in format HH:MM", )
    
    sun_latlong_gmt = IntProperty(name="GMT", default=0, min=-12, max=12, )
    sun_latlong_gmt_auto = BoolProperty(name="Auto", default=False, update=_gmt_auto, description="When enabled, GMT will be approximatelly calculated", )
    sun_latlong_ground_rotation = FloatProperty(name="Ground Rotation", default=math.radians(0.000), min=math.radians(0.000), max=math.radians(360.000), precision=3, subtype='ANGLE', )
    sun_angles_zenith = FloatProperty(name="Zenith", default=math.radians(45.000), min=math.radians(0.000), max=math.radians(90.000), precision=3, subtype='ANGLE', )
    sun_angles_azimuth = FloatProperty(name="Azimuth", default=math.radians(45.000), min=math.radians(0.000), max=math.radians(360.00), precision=3, subtype='ANGLE', )
    sun_dir_x = FloatProperty(name="X", default=0.0, min=-1000.000, max=1000.000, precision=3, )
    sun_dir_y = FloatProperty(name="Y", default=0.0, min=-1000.000, max=1000.000, precision=3, )
    sun_dir_z = FloatProperty(name="Z", default=1.0, min=-1000.000, max=1000.000, precision=3, )
    
    ibl_intensity = FloatProperty(name="Intensity", default=1.0, min=0.0, max=1000000.0, precision=1, )
    ibl_interpolation = BoolProperty(name="Interpolation", default=False, )
    ibl_screen_mapping = BoolProperty(name="Screen Mapping", default=False, )
    
    ibl_bg_type = EnumProperty(name="Type", items=[('HDR_IMAGE', "Hdr Image", ""), ('ACTIVE_SKY', "Active Sky", ""), ('DISABLED', "Disabled", "")], default='HDR_IMAGE', )
    ibl_bg_map = StringProperty(name="Image", default="", subtype='FILE_PATH', )
    ibl_bg_intensity = FloatProperty(name="Intensity", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_bg_scale_x = FloatProperty(name="Scale X", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_bg_scale_y = FloatProperty(name="Scale Y", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_bg_offset_x = FloatProperty(name="Offset X", default=0.0, min=-360.000, max=360.000, precision=3, )
    ibl_bg_offset_y = FloatProperty(name="Offset Y", default=0.0, min=-360.000, max=360.000, precision=3, )
    
    ibl_refl_type = EnumProperty(name="Type", items=[('HDR_IMAGE', "Hdr Image", ""), ('ACTIVE_SKY', "Active Sky", ""), ('SAME_AS_BG', "Same As Background", ""), ('DISABLED', "Disabled", "")], default='SAME_AS_BG', )
    ibl_refl_map = StringProperty(name="Image", default="", subtype='FILE_PATH', )
    ibl_refl_intensity = FloatProperty(name="Intensity", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_refl_scale_x = FloatProperty(name="Scale X", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_refl_scale_y = FloatProperty(name="Scale Y", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_refl_offset_x = FloatProperty(name="Offset X", default=0.0, min=-360.000, max=360.000, precision=3, )
    ibl_refl_offset_y = FloatProperty(name="Offset Y", default=0.0, min=-360.000, max=360.000, precision=3, )
    
    ibl_refr_type = EnumProperty(name="Type", items=[('HDR_IMAGE', "Hdr Image", ""), ('ACTIVE_SKY', "Active Sky", ""), ('SAME_AS_BG', "Same As Background", ""), ('DISABLED', "Disabled", "")], default='SAME_AS_BG', )
    ibl_refr_map = StringProperty(name="Image", default="", subtype='FILE_PATH', )
    ibl_refr_intensity = FloatProperty(name="Intensity", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_refr_scale_x = FloatProperty(name="Scale X", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_refr_scale_y = FloatProperty(name="Scale Y", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_refr_offset_x = FloatProperty(name="Offset X", default=0.0, min=-360.000, max=360.000, precision=3, )
    ibl_refr_offset_y = FloatProperty(name="Offset Y", default=0.0, min=-360.000, max=360.000, precision=3, )
    
    ibl_illum_type = EnumProperty(name="Type", items=[('HDR_IMAGE', "Hdr Image", ""), ('ACTIVE_SKY', "Active Sky", ""), ('SAME_AS_BG', "Same As Background", ""), ('DISABLED', "Disabled", "")], default='SAME_AS_BG', )
    ibl_illum_map = StringProperty(name="Image", default="", subtype='FILE_PATH', )
    ibl_illum_intensity = FloatProperty(name="Intensity", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_illum_scale_x = FloatProperty(name="Scale X", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_illum_scale_y = FloatProperty(name="Scale Y", default=1.0, min=0.0, max=1000.000, precision=3, )
    ibl_illum_offset_x = FloatProperty(name="Offset X", default=0.0, min=-360.000, max=360.000, precision=3, )
    ibl_illum_offset_y = FloatProperty(name="Offset Y", default=0.0, min=-360.000, max=360.000, precision=3, )
    
    @classmethod
    def register(cls):
        bpy.types.World.maxwell_render = PointerProperty(type=cls)
    
    @classmethod
    def unregister(cls):
        del bpy.types.World.maxwell_render


class CameraProperties(PropertyGroup):
    def _update_camera_projection(self, context):
        c = context.active_object
        cd = c.data
        
        l = self.lens
        if(l == 'TYPE_ORTHO_2'):
            cd.type = 'ORTHO'
            cd.ortho_scale = cd.dof_distance
            cd.lens = 32.0
            if(cd.dof_object is not None):
                cd.dof_object = None
        else:
            cd.type = 'PERSP'
    
    def _lock_exposure_update_shutter(self, context):
        # fstop = 11
        # time = 250
        # t = 1 / 250
        # ev = math.log2((fstop ** 2) / t)
        # fstop = math.sqrt((2 ** ev) * t)
        # time = 1 / (1 / ((2 ** ev) / (fstop ** 2)))
        if(self.lock):
            return
        
        self.lock = True
        
        fstop = self.fstop
        shutter = self.shutter
        t = 1 / shutter
        
        if(self.lock_exposure):
            ev = self.ev
            fstop = math.sqrt((2 ** ev) * t)
            self.fstop = fstop
        else:
            ev = math.log2((fstop ** 2) / t)
            self.ev = ev
        
        fps = bpy.context.scene.render.fps
        self.shutter_angle = math.radians(360 * (fps / self.shutter))
        
        self.lock = False
    
    def _lock_exposure_update_fstop(self, context):
        if(self.lock):
            return
        
        self.lock = True
        
        fstop = self.fstop
        shutter = self.shutter
        t = 1 / shutter
        
        if(self.lock_exposure):
            ev = self.ev
            shutter = 1 / (1 / ((2 ** ev) / (fstop ** 2)))
            self.shutter = shutter
            
            fps = bpy.context.scene.render.fps
            self.shutter_angle = math.radians(360 * (fps / self.shutter))
        else:
            ev = math.log2((fstop ** 2) / t)
            self.ev = ev
        
        self.lock = False
        
        # update fstop in dof options to have a dof in viewport
        context.camera.gpu_dof.fstop = self.fstop
    
    def _lock_exposure_update_ev(self, context):
        if(self.lock):
            return
        
        self.lock = True
        
        fstop = self.fstop
        shutter = self.shutter
        t = 1 / shutter
        ev = self.ev
        shutter = 1 / (1 / ((2 ** ev) / (fstop ** 2)))
        self.shutter = shutter
        
        fps = bpy.context.scene.render.fps
        self.shutter_angle = math.radians(360 * (fps / self.shutter))
        
        self.lock = False
    
    def _lock_exposure_update_angle(self, context):
        if(self.lock):
            return
        self.lock = True
        
        fps = bpy.context.scene.render.fps
        
        fstop = self.fstop
        shutter = self.shutter
        t = 1 / shutter
        
        try:
            self.shutter = fps / (math.degrees(self.shutter_angle) / 360)
        except ZeroDivisionError:
            self.shutter = 16000.0
        
        if(self.lock_exposure):
            ev = self.ev
            fstop = math.sqrt((2 ** ev) * t)
            self.fstop = fstop
        else:
            ev = math.log2((fstop ** 2) / t)
            self.ev = ev
        
        self.lock = False
    
    # optics
    lens = EnumProperty(name="Lens", items=[('TYPE_THIN_LENS_0', "Thin Lens", ""),
                                            ('TYPE_PINHOLE_1', "Pin Hole", ""),
                                            ('TYPE_ORTHO_2', "Ortho", ""),
                                            ('TYPE_FISHEYE_3', "Fish Eye", ""),
                                            ('TYPE_SPHERICAL_4', "Spherical", ""),
                                            ('TYPE_CYLINDRICAL_5', "Cylindical", ""),
                                            ('TYPE_LAT_LONG_STEREO_6', "Lat-Long Stereo", ""),
                                            ('TYPE_FISH_STEREO_7', "Fish Stereo", ""), ], default='TYPE_THIN_LENS_0', update=_update_camera_projection, )
    
    shutter = FloatProperty(name="Shutter Speed", default=250.0, min=0.01, max=16000.0, precision=3, description="1 / shutter speed", update=_lock_exposure_update_shutter, )
    # fstop = FloatProperty(name="f-Stop", default=11.0, min=1.0, max=100000.0, update=_lock_exposure_update_fstop, )
    fstop = FloatProperty(name="f-Stop", default=11.0, min=1.0, max=math.sqrt(2 ** 24), update=_lock_exposure_update_fstop, )
    # ev = FloatProperty(name="EV Number", default=14.885, min=1.0, max=100000.0, precision=3, update=_lock_exposure_update_ev, )
    ev = FloatProperty(name="EV Number", default=14.885, min=1.0, max=1000.0, precision=3, update=_lock_exposure_update_ev, )
    lock_exposure = BoolProperty(name="Lock Exposure", default=False, )
    
    lock = BoolProperty(default=False, options={'HIDDEN'}, )
    
    fov = FloatProperty(name="FOV", default=math.radians(180.0), min=math.radians(0.0), max=math.radians(360.0), subtype='ANGLE', )
    azimuth = FloatProperty(name="Azimuth", default=math.radians(180.0), min=math.radians(0.0), max=math.radians(360.0), subtype='ANGLE', )
    angle = FloatProperty(name="Angle", default=math.radians(180.0), min=math.radians(0.0), max=math.radians(360.0), subtype='ANGLE', )
    
    lls_type = EnumProperty(name="Type", items=[('CENTER_0', "Center", ""), ('LEFT_1', "Left", ""), ('RIGHT_2', "Right", ""), ], default='LEFT_1', )
    lls_fovv = FloatProperty(name="Vertical", default=math.radians(180.0), min=math.radians(0.0), max=math.radians(180.0), subtype='ANGLE', )
    lls_fovh = FloatProperty(name="Horizontal", default=math.radians(360.0), min=math.radians(0.0), max=math.radians(360.0), subtype='ANGLE', )
    lls_flip_ray_x = BoolProperty(name="X", default=False, )
    lls_flip_ray_y = BoolProperty(name="Y", default=False, )
    lls_parallax_distance = FloatProperty(name="Parallax Distance", default=math.radians(360.0), min=math.radians(0.0), max=math.radians(360.0), subtype='ANGLE', )
    lls_zenith_mode = BoolProperty(name="Zenith Mode", default=False, )
    lls_separation = FloatProperty(name="Separation", default=6.0, min=0.0, max=1000000.0, )
    lls_separation_map = StringProperty(name="Separation Map", default="", description="Path to separation map", )
    fs_type = EnumProperty(name="Type", items=[('CENTER_0', "Center", ""), ('LEFT_1', "Left", ""), ('RIGHT_2', "Right", ""), ], default='CENTER_0', )
    fs_fov = FloatProperty(name="FOV", default=math.radians(180.0), min=math.radians(0.0), max=math.radians(360.0), subtype='ANGLE', )
    fs_separation = FloatProperty(name="Separation", default=6.0, min=0.0, max=1000000.0, )
    fs_separation_map = StringProperty(name="Separation Map", default="", description="Path to separation map", )
    fs_vertical_mode = EnumProperty(name="Vertical Mode", items=[('OFF_0', "Off", ""), ('ON_1', "On", ""), ], default='OFF_0', )
    fs_dome_radius = FloatProperty(name="Dome Radius", default=136.0, min=1.0, max=1000000.0, )
    fs_head_turn_map = StringProperty(name="Head Turn Map", default="", description="Path to separation map", )
    fs_dome_tilt_compensation = EnumProperty(name="Dome Tilt Compensation", items=[('OFF_0', "Off", ""), ('ON_1', "On", ""), ], default='OFF_0', )
    fs_dome_tilt = FloatProperty(name="Dome Tilt", default=0.0, min=0.0, max=90.0, )
    fs_head_tilt_map = StringProperty(name="Head Tilt Map", default="", description="Path to separation map", )
    
    # sensor
    # resolution_width = IntProperty(name="Width", default=640, min=32, max=65536, subtype="PIXEL", )
    # resolution_height = IntProperty(name="Height", default=480, min=32, max=65536, subtype="PIXEL", )
    # pixel_aspect = FloatProperty(name="Pixel Aspect", default=1.0, min=0.010, max=100.000, precision=3, )
    iso = FloatProperty(name="ISO", default=100.0, min=1.0, max=16000.0, )
    screen_region = EnumProperty(name="Selection", items=[('NONE', "Full", ""), ('REGION', "Region", ""), ('BLOW UP', "Blow Up", "")], default='NONE', )
    screen_region_x = IntProperty(name="X", default=0, min=0, max=65000, subtype="PIXEL", )
    screen_region_y = IntProperty(name="Y", default=0, min=0, max=65000, subtype="PIXEL", )
    screen_region_w = IntProperty(name="Width", default=1, min=0, max=65000, subtype="PIXEL", )
    screen_region_h = IntProperty(name="Height", default=1, min=0, max=65000, subtype="PIXEL", )
    # diaphragm
    aperture = EnumProperty(name="Aperture", items=[('CIRCULAR', "Circular", ""), ('POLYGONAL', "Polygonal", "")], default='CIRCULAR', )
    diaphragm_blades = IntProperty(name="Blades", default=6, min=3, max=96, )
    diaphragm_angle = FloatProperty(name="Angle", default=math.radians(60.0), min=math.radians(0.0), max=math.radians(720.0), subtype='ANGLE', )
    custom_bokeh = BoolProperty(name="Custom Bokeh", default=False, )
    bokeh_ratio = FloatProperty(name="Bokeh Ratio", default=1.0, min=0.0, max=10000.0, )
    bokeh_angle = FloatProperty(name="Bokeh Angle", default=math.radians(0.0), min=math.radians(0.0), max=math.radians(20520.0), subtype='ANGLE', )
    # rotary disc shutter
    # shutter_angle = FloatProperty(name="Shutter Angle", default=math.radians(17.280), min=math.radians(0.0), max=math.radians(5000.000), subtype='ANGLE', )
    shutter_angle = FloatProperty(name="Shutter Angle", default=math.radians(34.56), min=math.radians(0.0), max=math.radians(5000.000), subtype='ANGLE', update=_lock_exposure_update_angle, )
    frame_rate = IntProperty(name="Frame Rate", default=24, min=1, max=10000, )
    # z-clip planes
    zclip = BoolProperty(name="Z-cLip", default=False, )
    
    movement = BoolProperty(name="Movement", default=True, description="Export for movement motion blur", )
    custom_substeps = BoolProperty(name="Custom Substeps", default=False, )
    substeps = IntProperty(name="Substeps", default=2, min=0, max=1000, )
    
    hide = BoolProperty(name="Hide (in Maxwell Studio)", default=False, )
    response = EnumProperty(name="Response", items=[('Maxwell', 'Maxwell', "", ), ('Advantix 100', 'Advantix 100', "", ), ('Advantix 200', 'Advantix 200', "", ),
                                                    ('Advantix 400', 'Advantix 400', "", ), ('Agfachrome CTPrecisa 200', 'Agfachrome CTPrecisa 200', "", ),
                                                    ('Agfachrome CTPrecisa 100', 'Agfachrome CTPrecisa 100', "", ), ('Agfachrome rsx2 050', 'Agfachrome rsx2 050', "", ),
                                                    ('Agfachrome rsx2 100', 'Agfachrome rsx2 100', "", ), ('Agfachrome rsx2 200', 'Agfachrome rsx2 200', "", ),
                                                    ('Agfacolor Futura 100', 'Agfacolor Futura 100', "", ), ('Agfacolor Futura 200', 'Agfacolor Futura 200', "", ),
                                                    ('Agfacolor Futura 400', 'Agfacolor Futura 400', "", ), ('Agfacolor Futura II 100', 'Agfacolor Futura II 100', "", ),
                                                    ('Agfacolor Futura II 200', 'Agfacolor Futura II 200', "", ), ('Agfacolor Futura II 400', 'Agfacolor Futura II 400', "", ),
                                                    ('Agfacolor HDC 100 Plus', 'Agfacolor HDC 100 Plus', "", ), ('Agfacolor HDC 200 Plus', 'Agfacolor HDC 200 Plus', "", ),
                                                    ('Agfacolor HDC 400 Plus', 'Agfacolor HDC 400 Plus', "", ), ('Agfacolor Optima II 100', 'Agfacolor Optima II 100', "", ),
                                                    ('Agfacolor Optima II 200', 'Agfacolor Optima II 200', "", ), ('Agfacolor Ultra 050', 'Agfacolor Ultra 050', "", ),
                                                    ('Agfacolor Vista 100', 'Agfacolor Vista 100', "", ), ('Agfacolor Vista 200', 'Agfacolor Vista 200', "", ),
                                                    ('Agfacolor Vista 400', 'Agfacolor Vista 400', "", ), ('Agfacolor Vista 800', 'Agfacolor Vista 800', "", ),
                                                    ('Agfapan APX 025 (B&W)', 'Agfapan APX 025 (B&W)', "", ), ('Agfapan APX 100 (B&W)', 'Agfapan APX 100 (B&W)', "", ),
                                                    ('Agfapan APX 400 (B&W)', 'Agfapan APX 400 (B&W)', "", ), ('Ektachrome 100 Plus (Color Rev.)', 'Ektachrome 100 Plus (Color Rev.)', "", ),
                                                    ('Ektachrome 100 (Color Rev.)', 'Ektachrome 100 (Color Rev.)', "", ), ('Ektachrome 320T (Color Rev.)', 'Ektachrome 320T (Color Rev.)', "", ),
                                                    ('Ektachrome 400X (Color Rev.)', 'Ektachrome 400X (Color Rev.)', "", ), ('Ektachrome 64 (Color Rev.)', 'Ektachrome 64 (Color Rev.)', "", ),
                                                    ('Ektachrome 64T (Color Rev.)', 'Ektachrome 64T (Color Rev.)', "", ), ('Ektachrome E100S', 'Ektachrome E100S', "", ),
                                                    ('Fujifilm Cine F-125', 'Fujifilm Cine F-125', "", ), ('Fujifilm Cine F-250', 'Fujifilm Cine F-250', "", ),
                                                    ('Fujifilm Cine F-400', 'Fujifilm Cine F-400', "", ), ('Fujifilm Cine FCI', 'Fujifilm Cine FCI', "", ),
                                                    ('Kodak Gold 100', 'Kodak Gold 100', "", ), ('Kodak Gold 200', 'Kodak Gold 200', "", ), ('Kodachrome 200', 'Kodachrome 200', "", ),
                                                    ('Kodachrome 25', 'Kodachrome 25', "", ), ('Kodachrome 64', 'Kodachrome 64', "", ), ('Kodak Max Zoom 800', 'Kodak Max Zoom 800', "", ),
                                                    ('Kodak Portra 100T', 'Kodak Portra 100T', "", ), ('Kodak Portra 160NC', 'Kodak Portra 160NC', "", ),
                                                    ('Kodak Portra 160VC', 'Kodak Portra 160VC', "", ), ('Kodak Portra 400NC', 'Kodak Portra 400NC', "", ),
                                                    ('Kodak Portra 400VC', 'Kodak Portra 400VC', "", ), ('Kodak Portra 800', 'Kodak Portra 800', "", ), ], default='Maxwell', )
    
    @classmethod
    def register(cls):
        bpy.types.Camera.maxwell_render = PointerProperty(type=cls)
    
    @classmethod
    def unregister(cls):
        del bpy.types.Camera.maxwell_render


class ObjectBlockedEmittersItem(PropertyGroup):
    name = StringProperty(name="Name", default="Blocked Emitter Name", )


class ObjectBlockedEmitters(PropertyGroup):
    emitters = CollectionProperty(name="Blocked Emitters", type=ObjectBlockedEmittersItem, )
    index = IntProperty(name="Active", default=-1, )


class ReferenceProperties(PropertyGroup):
    enabled = BoolProperty(name="Enabled", default=False, )
    path = StringProperty(name="MXS File", default="", subtype='FILE_PATH', )
    flag_override_hide = BoolProperty(name="Hidden", default=False, )
    flag_override_hide_to_camera = BoolProperty(name="Camera", default=False, )
    flag_override_hide_to_refl_refr = BoolProperty(name="Reflections/Refractions", default=False, )
    flag_override_hide_to_gi = BoolProperty(name="Global Illumination", default=False, )
    
    material = StringProperty(name="Material", default="", )
    backface_material = StringProperty(name="Backface Material", default="", )
    
    def _draw_update(self, context):
        p = os.path.realpath(bpy.path.abspath(self.path))
        r = self.refresh
        ops.MXSReferenceCache.draw(p, self.draw, context, r, )
    
    draw = BoolProperty(name="Draw in Viewport", default=False, update=_draw_update, description="", )
    refresh = BoolProperty(name="Refresh", default=False, description="Force loading vertices from MXS when enabling drawing", )
    
    draw_options = BoolProperty(name="Show Options", default=False, )
    
    current_theme = bpy.context.user_preferences.themes.items()[0][0]
    point_color = FloatVectorProperty(name="Color",
                                      default=tuple(bpy.context.user_preferences.themes[current_theme].view_3d.wire),
                                      min=0.0, max=1.0, precision=2, subtype='COLOR', )
    point_color_selected = FloatVectorProperty(name="Selected",
                                               default=tuple(bpy.context.user_preferences.themes[current_theme].view_3d.object_selected),
                                               min=0.0, max=1.0, precision=2, subtype='COLOR', )
    point_color_active = FloatVectorProperty(name="Active",
                                             default=tuple(bpy.context.user_preferences.themes[current_theme].view_3d.object_active),
                                             min=0.0, max=1.0, precision=2, subtype='COLOR', )
    point_size = IntProperty(name="Size",
                             default=bpy.context.user_preferences.themes[current_theme].view_3d.vertex_size,
                             min=1, max=10, )
    bbox_color = FloatVectorProperty(name="Color",
                                     default=tuple(bpy.context.user_preferences.themes[current_theme].view_3d.wire),
                                     min=0.0, max=1.0, precision=2, subtype='COLOR', )
    bbox_color_selected = FloatVectorProperty(name="Selected",
                                              default=tuple(bpy.context.user_preferences.themes[current_theme].view_3d.object_selected),
                                              min=0.0, max=1.0, precision=2, subtype='COLOR', )
    bbox_color_active = FloatVectorProperty(name="Active",
                                            default=tuple(bpy.context.user_preferences.themes[current_theme].view_3d.object_active),
                                            min=0.0, max=1.0, precision=2, subtype='COLOR', )
    bbox_line_width = IntProperty(name="Width",
                                  default=bpy.context.user_preferences.themes[current_theme].view_3d.outline_width,
                                  min=1, max=10, )
    
    bbox_line_stipple = BoolProperty(name="Dashed", default=True, )
    
    display_percent = FloatProperty(name="Display Percent (%)", default=10.0, min=0.0, max=100.0, precision=0, subtype='PERCENTAGE', )
    display_max_points = IntProperty(name="Display Max. Points", default=10000, min=0, max=1000000, )


class ExtGrassProperties(PropertyGroup):
    enabled = BoolProperty(name="Maxwell Grass", default=False, )
    
    material = StringProperty(name="Material", default="", )
    backface_material = StringProperty(name="Backface Material", default="", )
    primitive_type = EnumProperty(name="Primitive Type", items=[('0', "Curve", ""), ('1', "Flat", ""), ('2', "Cylinder", "")], default='1', )
    points_per_blade = IntProperty(name="Points Per Blade", default=8, min=2, max=20, )
    primitive_expand = BoolProperty(name="Expand", default=True, )
    
    density = IntProperty(name="Density (blades/m2)", default=3000, min=0, max=100000000, )
    density_map = StringProperty(name="Density Map", default="", )
    seed = IntProperty(name="Random Seed", default=0, min=0, max=16300, )
    density_expand = BoolProperty(name="Expand", default=True, )
    
    length = FloatProperty(name="Length (cm)", default=7.5, min=0.0, max=100000.0, precision=3, )
    length_map = StringProperty(name="Length Map", default="", )
    length_variation = FloatProperty(name="Length Variation (%)", default=60.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    length_expand = BoolProperty(name="Expand", default=False, )
    
    root_width = FloatProperty(name="Root Width (mm)", default=6.0, min=0.00001, max=100000.0, precision=3, )
    tip_width = FloatProperty(name="Tip Width (mm)", default=2.5, min=0.00001, max=100000.0, precision=3, )
    width_expand = BoolProperty(name="Expand", default=False, )
    
    direction_type = FloatProperty(name="Grow Towards World-Y (%)", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    
    initial_angle = FloatProperty(name="Initial Angle", default=math.radians(60.000), min=math.radians(0.000), max=math.radians(90.000), precision=1, subtype='ANGLE', )
    initial_angle_variation = FloatProperty(name="Initial Angle Variation (%)", default=50.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    initial_angle_map = StringProperty(name="Initial Angle Map", default="", )
    angle_expand = BoolProperty(name="Expand", default=False, )
    
    start_bend = FloatProperty(name="Start Bend (%)", default=40.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    start_bend_variation = FloatProperty(name="Start Bend Variation (%)", default=25.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    start_bend_map = StringProperty(name="Start Bend Map", default="", )
    
    bend_radius = FloatProperty(name="Bend Radius (cm)", default=5.0, min=0.0, max=10000.0, precision=1, )
    bend_radius_variation = FloatProperty(name="Bend Radius Variation (%)", default=50.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    bend_radius_map = StringProperty(name="Bend Radius Map", default="", )
    
    bend_angle = FloatProperty(name="Bend Angle", default=math.radians(80.000), min=math.radians(0.000), max=math.radians(360.000), precision=1, subtype='ANGLE', )
    bend_angle_variation = FloatProperty(name="Bend Radius Variation (%)", default=50.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    bend_angle_map = StringProperty(name="Bend Radius Map", default="", )
    
    bend_expand = BoolProperty(name="Expand", default=False, )
    
    cut_off = FloatProperty(name="Cut Off (%)", default=100.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    cut_off_variation = FloatProperty(name="Cut Off Variation (%)", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    cut_off_map = StringProperty(name="Cut Off Map", default="", )
    cut_off_expand = BoolProperty(name="Expand", default=False, )
    
    lod = BoolProperty(name="Enabled", default=False, )
    lod_min_distance = FloatProperty(name="Min Distance (m)", default=10.0, min=0.0, max=100000.0, precision=2, )
    lod_max_distance = FloatProperty(name="Max Distance (m)", default=50.0, min=0.0, max=100000.0, precision=2, )
    lod_max_distance_density = FloatProperty(name="Max Distance Density (%)", default=10.0, min=0.0, max=100.0, precision=2, subtype='PERCENTAGE', )
    lod_expand = BoolProperty(name="Expand", default=False, )
    
    display_percent = FloatProperty(name="Display Percent (%)", default=10.0, min=0.0, max=100.0, precision=0, subtype='PERCENTAGE', )
    display_max_blades = IntProperty(name="Display Max. Blades", default=1000, min=0, max=100000, )
    display_expand = BoolProperty(name="Expand", default=False, )


class ExtScatterProperties(PropertyGroup):
    enabled = BoolProperty(name="Maxwell Scatter", default=False, )
    
    scatter_object = StringProperty(name="Scatter Object", default="", )
    inherit_objectid = BoolProperty(name="Inherit ObjectID", default=False, )
    
    density = FloatProperty(name="Density (Units/m2)", default=100.0, min=0.0001, max=100000000.0, precision=3, )
    density_map = StringProperty(name="Density Map", default="", )
    remove_overlapped = BoolProperty(name="Remove Overlaps", default=False, )
    seed = IntProperty(name="Random Seed", default=0, min=0, max=16300, )
    density_expand = BoolProperty(name="Expand", default=True, )
    
    direction_type = FloatProperty(name="Grow Towards World-Y (%)", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    initial_angle = FloatProperty(name="Initial Angle", default=math.radians(90.0), min=math.radians(0.0), max=math.radians(90.0), precision=1, subtype='ANGLE', )
    initial_angle_variation = FloatProperty(name="Initial Angle Variation (%)", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    initial_angle_map = StringProperty(name="Initial Angle Map", default="", )
    angle_expand = BoolProperty(name="Expand", default=False, )
    
    scale_x = FloatProperty(name="X", default=1.0, min=0.0, max=100000.0, precision=3, )
    scale_y = FloatProperty(name="Y", default=1.0, min=0.0, max=100000.0, precision=3, )
    scale_z = FloatProperty(name="Z", default=1.0, min=0.0, max=100000.0, precision=3, )
    scale_uniform = BoolProperty(name="Uniform Scale", default=False, )
    scale_map = StringProperty(name="Scale Map", default="", )
    scale_variation_x = FloatProperty(name="X", default=20.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    scale_variation_y = FloatProperty(name="X", default=20.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    scale_variation_z = FloatProperty(name="X", default=20.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    scale_expand = BoolProperty(name="Expand", default=False, )
    
    rotation_x = FloatProperty(name="X", default=math.radians(0.000), min=math.radians(0.000), max=math.radians(360.000), precision=1, subtype='ANGLE', )
    rotation_y = FloatProperty(name="Y", default=math.radians(0.000), min=math.radians(0.000), max=math.radians(360.000), precision=1, subtype='ANGLE', )
    rotation_z = FloatProperty(name="Z", default=math.radians(0.000), min=math.radians(0.000), max=math.radians(360.000), precision=1, subtype='ANGLE', )
    rotation_map = StringProperty(name="Rotation Map", default="", )
    rotation_variation_x = FloatProperty(name="X", default=10.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    rotation_variation_y = FloatProperty(name="Y", default=10.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    rotation_variation_z = FloatProperty(name="Z", default=10.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    rotation_direction = EnumProperty(name="Direction", items=[('0', "Polygon Normal", ""), ('1', "World Z", "")], default='0', )
    rotation_expand = BoolProperty(name="Expand", default=False, )
    
    lod = BoolProperty(name="Enabled", default=False, )
    lod_min_distance = FloatProperty(name="Min Distance (m)", default=10.0, min=0.0, max=100000.0, precision=2, )
    lod_max_distance = FloatProperty(name="Max Distance (m)", default=50.0, min=0.0, max=100000.0, precision=2, )
    lod_max_distance_density = FloatProperty(name="Max Distance Density (%)", default=10.0, min=0.0, max=100.0, precision=2, subtype='PERCENTAGE', )
    lod_expand = BoolProperty(name="Expand", default=False, )
    
    display_percent = FloatProperty(name="Display Percent (%)", default=10.0, min=0.0, max=100.0, precision=0, subtype='PERCENTAGE', )
    display_max_blades = IntProperty(name="Display Max. Instances", default=1000, min=0, max=100000, )
    display_expand = BoolProperty(name="Expand", default=False, )
    
    # included but not shown in Studio ui
    # 19: ('Initial Angle', [90.0], 0.0, 90.0, '3 FLOAT', 4, 1, True)
    # 20: ('Initial Angle Variation', [0.0], 0.0, 100.0, '3 FLOAT', 4, 1, True)
    # 21: ('Initial Angle Map', <pymaxwell.MXparamList; proxy of <Swig Object of type 'MXparamList *' at 0x10107c390> >, 0, 0, '10 MXPARAMLIST', 0, 1, True)
    
    # new, something to investigate
    # 29: ('TRIANGLES_WITH_CLONES', [0], 0, 0, '8 BYTEARRAY', 1, 1, True)


class ExtSubdivisionProperties(PropertyGroup):
    enabled = BoolProperty(name="Subdivision Modifier", default=False, )
    level = IntProperty(name="Subdivision Level", default=2, min=0, max=99, )
    scheme = EnumProperty(name="Subdivision Scheme", items=[('0', "Catmull-Clark", ""), ('1', "Loop", "")], default='0', )
    interpolation = EnumProperty(name="UV Interpolation", items=[('0', "None", ""), ('1', "Edges", ""), ('2', "Edges And Corners", ""), ('3', "Sharp", "")], default='2', )
    crease = FloatProperty(name="Edge Crease (%)", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    smooth = FloatProperty(name="Smooth Angle", default=math.radians(90.000), min=math.radians(0.000), max=math.radians(360.000), precision=1, subtype='ANGLE', )


class ExtSeaProperties(PropertyGroup):
    enabled = BoolProperty(name="Maxwell Sea", default=False, )
    hide = BoolProperty(name="Export as Hidden Object", default=False, description="Object will be exported, but with visibility set to Hidden. Useful for finishing scene in Studio")
    
    material = StringProperty(name="Material", default="", )
    backface_material = StringProperty(name="Backface Material", default="", )
    
    resolution = EnumProperty(name="Quality", items=[('0', "4x4", ""), ('1', "8x8", ""), ('2', "16x16", ""), ('3', "32x32", ""), ('4', "64x64", ""),
                                                     ('5', "128x128", ""), ('6', "256x256", ""), ('7', "512x512", ""), ('8', "1024x1024", ""),
                                                     ('9', "2048x2048", ""), ('10', "4096x4096", ""), ('11', "8192x8192", ""), ], default='6', )
    reference_time = FloatProperty(name="Reference Time (s)", default=0.0, min=0.0, max=100000.0, precision=4, )
    ocean_wind_mod = FloatProperty(name="Wind Speed (m/s)", default=30.0, min=0.0, max=100000.0, precision=3, )
    ocean_wind_dir = FloatProperty(name="Wind Direction (º)", default=math.radians(45.000), min=math.radians(0.000), max=math.radians(360.000), precision=1, subtype='ANGLE', )
    vertical_scale = FloatProperty(name="Vertical Scale", default=0.1, min=0.0, max=100000.0, precision=5, )
    damp_factor_against_wind = FloatProperty(name="Weight Against Wind", default=0.5, min=0.0, max=1.0, precision=4, subtype='PERCENTAGE', )
    ocean_wind_alignment = FloatProperty(name="Wind Alignment", default=2.0, min=0.0, max=100000.0, precision=4, )
    ocean_min_wave_length = FloatProperty(name="Min Wave Length (m)", default=0.1, min=0.0, max=100000.0, precision=4, )
    ocean_dim = FloatProperty(name="Dimension (m)", default=250.0, min=0.0, max=1000000.0, precision=2, )
    ocean_depth = FloatProperty(name="Depth (m)", default=200.0, min=0.0, max=100000.0, precision=2, )
    ocean_seed = IntProperty(name="Seed", default=4217, min=0, max=65535, )
    enable_choppyness = BoolProperty(name="Enable Choppyness", default=False, )
    choppy_factor = FloatProperty(name="Choppy Factor", default=0.0, min=0.0, max=100000.0, precision=2, )
    enable_white_caps = BoolProperty(name="Enable White Caps", default=False, )


class ExtVolumetricsProperties(PropertyGroup):
    enabled = BoolProperty(name="Enabled", default=False, )
    vtype = EnumProperty(name="Type", items=[('CONSTANT_1', "Constant", ""), ('NOISE3D_2', "Noise 3D", "")], default='CONSTANT_1', )
    
    density = FloatProperty(name="Field Density", default=1.0, min=0.000001, max=10000.0, precision=6, )
    
    noise_seed = IntProperty(name="Seed", default=4357, min=0, max=1000000, )
    noise_low = FloatProperty(name="Low Value", default=0.0, min=0.0, max=1.0, precision=6, )
    noise_high = FloatProperty(name="High Value", default=1.0, min=0.000001, max=1.0, precision=6, )
    noise_detail = FloatProperty(name="Detail", default=2.2, min=1.0, max=100.0, precision=4, )
    noise_octaves = IntProperty(name="Octaves", default=4, min=1, max=50, )
    noise_persistence = FloatProperty(name="Persistance", default=0.55, min=0.0, max=1.0, precision=4, )
    
    material = StringProperty(name="Material", default="", )
    backface_material = StringProperty(name="Backface Material", default="", )


class ObjectProperties(PropertyGroup):
    opacity = FloatProperty(name="Opacity", default=100.0, min=0.0, max=100.0, subtype='PERCENTAGE', )
    hidden_camera = BoolProperty(name="Camera", default=False, )
    hidden_camera_in_shadow_channel = BoolProperty(name="Camera In Shadow Channel", default=False, )
    hidden_global_illumination = BoolProperty(name="Global Illumination", default=False, )
    hidden_reflections_refractions = BoolProperty(name="Reflections/Refractions", default=False, )
    hidden_zclip_planes = BoolProperty(name="Z-clip Planes", default=False, )
    object_id = FloatVectorProperty(name="Object ID", default=(0.0, 0.0, 0.0), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    
    backface_material = StringProperty(name="Backface Material", default="", )
    
    hide = BoolProperty(name="Export as Hidden Object", default=False, description="Object will be exported, but with visibility set to Hidden. Useful for finishing scene in Studio")
    override_instance = BoolProperty(name="Override Instancing", default=False, description="Enable when object is an instance, but has different modifiers then original.", )
    
    blocked_emitters = PointerProperty(name="Blocked Emitters", type=ObjectBlockedEmitters, )
    reference = PointerProperty(name="Reference", type=ReferenceProperties, )
    grass = PointerProperty(name="Grass", type=ExtGrassProperties, )
    scatter = PointerProperty(name="Scatter", type=ExtScatterProperties, )
    subdivision = PointerProperty(name="Subdivision", type=ExtSubdivisionProperties, )
    sea = PointerProperty(name="Sea", type=ExtSeaProperties, )
    volumetrics = PointerProperty(name="Volumetrics", type=ExtVolumetricsProperties, )
    
    movement = BoolProperty(name="Movement", default=True, description="Export for movement motion blur", )
    deformation = BoolProperty(name="Deformation", default=False, description="Export for deformation motion blur", )
    custom_substeps = BoolProperty(name="Custom Substeps", default=False, )
    substeps = IntProperty(name="Substeps", default=2, min=0, max=1000, )
    
    @classmethod
    def register(cls):
        bpy.types.Object.maxwell_render = PointerProperty(type=cls)
    
    @classmethod
    def unregister(cls):
        del bpy.types.Object.maxwell_render


class ProceduralTextureItemProperties(PropertyGroup):
    brick_brick_width = FloatProperty(name="Brick Width", default=0.21, min=0.0, max=1.0, precision=4, )
    brick_brick_height = FloatProperty(name="Brick Height", default=0.1, min=0.0, max=1.0, precision=4, )
    brick_brick_offset = IntProperty(name="Brick Offset", default=50, min=0, max=100, )
    brick_random_offset = IntProperty(name="Random Offset", default=20, min=0, max=100, )
    brick_double_brick = BoolProperty(name="Double Brick", default=False, )
    brick_small_brick_width = FloatProperty(name="Small Brick Width", default=0.1050, min=0.0, max=1.0, precision=4, )
    brick_round_corners = BoolProperty(name="Round Corners", default=False, )
    brick_boundary_sharpness_u = FloatProperty(name="Transition Sharpness U", default=0.9, min=0.0, max=1.0, precision=4, )
    brick_boundary_sharpness_v = FloatProperty(name="Transition Sharpness V", default=0.9, min=0.0, max=1.0, precision=4, )
    brick_boundary_noise_detail = IntProperty(name="Boundary Noise Detail", default=0, min=0, max=100, )
    brick_boundary_noise_region_u = FloatProperty(name="Boundary Noise Region U", default=0.0, min=0.0, max=1.0, precision=4, )
    brick_boundary_noise_region_v = FloatProperty(name="Boundary Noise Region V", default=0.0, min=0.0, max=1.0, precision=4, )
    brick_seed = IntProperty(name="Seed", default=4357, min=0, max=1000000, )
    brick_random_rotation = BoolProperty(name="Random Rotation", default=True, )
    brick_color_variation = IntProperty(name="Brightness Variation", default=20, min=0, max=100, )
    brick_brick_color_0 = FloatVectorProperty(name="Brick Color 1", default=(1.0, 1.0, 1.0), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    brick_brick_texture_0 = StringProperty(name="Brick Texture 1", default="", )
    brick_sampling_factor_0 = IntProperty(name="Sample Size 1", default=10, min=0, max=100, )
    brick_weight_0 = IntProperty(name="Weight 1", default=100, min=0, max=100, )
    brick_brick_color_1 = FloatVectorProperty(name="Brick Color 2", default=(0.0, 0.0, 0.0), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    brick_brick_texture_1 = StringProperty(name="Brick Texture 2", default="", )
    brick_sampling_factor_1 = IntProperty(name="Sample Size 2", default=9, min=0, max=100, )
    brick_weight_1 = IntProperty(name="Weight 2", default=100, min=0, max=100, )
    brick_brick_color_2 = FloatVectorProperty(name="Brick Color 3", default=(255 / 89.250, 255 / 89.250, 255 / 89.250), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    brick_brick_texture_2 = StringProperty(name="Brick Texture 3", default="", )
    brick_sampling_factor_2 = IntProperty(name="Sample Size 3", default=12, min=0, max=100, )
    brick_weight_2 = IntProperty(name="Weight 3", default=100, min=0, max=100, )
    brick_mortar_thickness = FloatProperty(name="Mortar Thickness", default=0.012, min=0.0, max=1.0, precision=4, )
    brick_mortar_color = FloatVectorProperty(name="Mortar Color", default=(255 / 129.795, 255 / 129.795, 255 / 129.795), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    brick_mortar_texture = StringProperty(name="Mortar Texture", default="", )
    
    checker_number_of_elements_u = IntProperty(name="Checks U", default=4, min=0, max=1000, )
    checker_number_of_elements_v = IntProperty(name="Checks V", default=4, min=0, max=1000, )
    checker_color_0 = FloatVectorProperty(name="Background Color", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    checker_color_1 = FloatVectorProperty(name="Checker Color", default=(0 / 255, 0 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    checker_transition_sharpness = FloatProperty(name="Sharpness", default=1.0, min=0.0, max=1.0, precision=3, )
    checker_falloff = EnumProperty(name="Fall-off", items=[('0', "Linear", ""), ('1', "Quadratic", ""), ('2', "Sinusoidal", ""), ], default='0', )
    
    circle_background_color = FloatVectorProperty(name="Background Color", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    circle_circle_color = FloatVectorProperty(name="Circle Color", default=(0 / 255, 0 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    circle_radius_u = FloatProperty(name="Radius U", default=1.0, min=0.0, max=1.0, precision=3, )
    circle_radius_v = FloatProperty(name="Radius U", default=1.0, min=0.0, max=1.0, precision=3, )
    circle_transition_factor = FloatProperty(name="Sharpness", default=1.0, min=0.0, max=1.0, precision=3, )
    circle_falloff = EnumProperty(name="Fall-off", items=[('0', "Linear", ""), ('1', "Quadratic", ""), ('2', "Sinusoidal", ""), ], default='0', )
    
    gradient3_gradient_u = BoolProperty(name="Active", default=True, )
    gradient3_color0_u = FloatVectorProperty(name="Start Color", default=(255 / 255, 0 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    gradient3_color1_u = FloatVectorProperty(name="Mid Color", default=(0 / 255, 255 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    gradient3_color2_u = FloatVectorProperty(name="End Color", default=(0 / 255, 0 / 255, 255 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    gradient3_gradient_type_u = EnumProperty(name="Transition Type", items=[('0', "Linear", ""), ('1', "Quadratic", ""), ('2', "Sinusoidal", ""), ], default='0', )
    gradient3_color1_u_position = FloatProperty(name="Mid Color Position", default=0.5, min=0.0, max=1.0, precision=3, )
    gradient3_gradient_v = BoolProperty(name="Active", default=False, )
    gradient3_color0_v = FloatVectorProperty(name="Start Color", default=(255 / 255, 0 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    gradient3_color1_v = FloatVectorProperty(name="Mid Color", default=(0 / 255, 255 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    gradient3_color2_v = FloatVectorProperty(name="End Color", default=(0 / 255, 0 / 255, 255 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    gradient3_gradient_type_v = EnumProperty(name="Transition Type", items=[('0', "Linear", ""), ('1', "Quadratic", ""), ('2', "Sinusoidal", ""), ], default='0', )
    gradient3_color1_v_position = FloatProperty(name="Mid Color Position", default=0.5, min=0.0, max=1.0, precision=3, )
    
    gradient_gradient_u = BoolProperty(name="Active", default=True, )
    gradient_color0_u = FloatVectorProperty(name="Start Color", default=(255 / 255, 0 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    gradient_color1_u = FloatVectorProperty(name="End Color", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    gradient_gradient_type_u = EnumProperty(name="Transition Type", items=[('0', "Linear", ""), ('1', "Quadratic", ""), ('2', "Sinusoidal", ""), ], default='0', )
    gradient_transition_factor_u = FloatProperty(name="Transition Position", default=1.0, min=0.0, max=1.0, precision=3, )
    gradient_gradient_v = BoolProperty(name="Active", default=False, )
    gradient_color0_v = FloatVectorProperty(name="Start Color", default=(0 / 255, 0 / 255, 255 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    gradient_color1_v = FloatVectorProperty(name="End Color", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    gradient_gradient_type_v = EnumProperty(name="Transition Type", items=[('0', "Linear", ""), ('1', "Quadratic", ""), ('2', "Sinusoidal", ""), ], default='0', )
    gradient_transition_factor_v = FloatProperty(name="Transition Position", default=1.0, min=0.0, max=1.0, precision=3, )
    
    grid_horizontal_lines = BoolProperty(name="Grid U", default=True, )
    grid_vertical_lines = BoolProperty(name="Grid V", default=True, )
    grid_cell_width = FloatProperty(name="Cell Width", default=0.2500, min=0.0, max=1.0, precision=4, )
    grid_cell_height = FloatProperty(name="Cell Height", default=0.1250, min=0.0, max=1.0, precision=4, )
    grid_boundary_thickness_u = FloatProperty(name="Background Thickness U", default=0.0650, min=0.0, max=1.0, precision=4, )
    grid_boundary_thickness_v = FloatProperty(name="Background Thickness V", default=0.0650, min=0.0, max=1.0, precision=4, )
    grid_transition_sharpness = FloatProperty(name="Sharpness", default=0.0, min=0.0, max=1.0, precision=4, )
    grid_cell_color = FloatVectorProperty(name="Cell Color", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    grid_boundary_color = FloatVectorProperty(name="Boundary Color", default=(0 / 255, 0 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    grid_falloff = EnumProperty(name="Fall-off", items=[('0', "Linear", ""), ('1', "Quadratic", ""), ('2', "Sinusoidal", ""), ], default='0', )
    
    marble_coordinates_type = EnumProperty(name="Coordinates Type", items=[('0', "Texture coordinates", ""), ('1', "World coordinates", ""), ], default='1', )
    marble_color0 = FloatVectorProperty(name="Vein Color 1", default=(199 / 255, 202 / 255, 210 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    marble_color1 = FloatVectorProperty(name="Vein Color 2", default=(152 / 255, 156 / 255, 168 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    marble_color2 = FloatVectorProperty(name="Vein Color 3", default=(87 / 255, 91 / 255, 98 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    marble_frequency = FloatProperty(name="Frequency", default=0.6, min=0.0, max=1000.0, precision=3, )
    marble_detail = FloatProperty(name="Detail", default=4.0, min=0.0, max=100.0, precision=3, )
    marble_octaves = IntProperty(name="Octaves", default=7, min=1, max=100, )
    marble_seed = IntProperty(name="Seed", default=4372, min=1, max=1000000, )
    
    noise_coordinates_type = EnumProperty(name="Coordinates Type", items=[('0', "Texture coordinates", ""), ('1', "World coordinates", ""), ], default='0', )
    noise_noise_color = FloatVectorProperty(name="Vein Color 1", default=(0 / 255, 0 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    noise_background_color = FloatVectorProperty(name="Vein Color 1", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    noise_detail = FloatProperty(name="Detail", default=6.2, min=1.0, max=1000.0, precision=4, )
    noise_persistance = FloatProperty(name="Persistance", default=0.55, min=0.0, max=1.0, precision=4, )
    noise_octaves = IntProperty(name="Octaves", default=4, min=1, max=50, )
    noise_low_value = FloatProperty(name="Low Clip", default=0.0, min=0.0, max=1.0, precision=4, )
    noise_high_value = FloatProperty(name="High Clip", default=1.0, min=0.0, max=1.0, precision=4, )
    noise_seed = IntProperty(name="Seed", default=4357, min=1, max=1000000, )
    
    voronoi_coordinates_type = EnumProperty(name="Coordinates Type", items=[('0', "Texture coordinates", ""), ('1', "World coordinates", ""), ], default='0', )
    voronoi_color0 = FloatVectorProperty(name="Background Color", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    voronoi_color1 = FloatVectorProperty(name="Cell Color", default=(0 / 255, 0 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    voronoi_detail = IntProperty(name="Detail", default=8, min=1, max=10000, )
    voronoi_distance = EnumProperty(name="Distance", items=[('0', "Euclidian", ""), ('1', "Manhattan", ""), ('2', "Minkowski4", ""), ('3', "Chebyshev", ""), ], default='0', )
    voronoi_combination = EnumProperty(name="Combination", items=[('0', "D1", ""), ('1', "D2", ""), ('2', "D3", ""), ('3', "D1+D2", ""), ('4', "D2-D1", ""), ('5', "D3-D2", ""),
                                                                  ('6', "D1*D2", ""), ('7', "D1*D3", ""), ('8', "D2*D3", ""), ('9', "1-D1", ""), ('10', "1-D2", ""),
                                                                  ('11', "1-(D1+D2)", ""), ('12', "1-(D1*D2)", ""), ], default='0', )
    voronoi_low_value = FloatProperty(name="Low Clip", default=0.0, min=0.0, max=1.0, precision=4, )
    voronoi_high_value = FloatProperty(name="High Clip", default=1.0, min=0.0, max=1.0, precision=4, )
    voronoi_seed = IntProperty(name="Seed", default=4357, min=1, max=1000000, )
    
    tiled_filename = StringProperty(name="File Name", default="", subtype='FILE_PATH', )
    tiled_token_mask = StringProperty(name="Token mask", default="texture.<UDIM>.png", )
    tiled_base_color = FloatVectorProperty(name="Base Color", default=(204 / 255, 204 / 255, 204 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    tiled_use_base_color = BoolProperty(name="Use Base Color", default=True, )
    
    wireframe_fill_color = FloatVectorProperty(name="Fill Color", default=(204 / 255, 204 / 255, 204 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    wireframe_edge_color = FloatVectorProperty(name="Edge Color", default=(0 / 255, 0 / 255, 0 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    wireframe_coplanar_edge_color = FloatVectorProperty(name="Coplanar Edge Color", default=(76.5 / 255, 76.5 / 255, 76.5 / 255), min=0.0, max=1.0, precision=3, subtype='COLOR', )
    wireframe_edge_width = FloatProperty(name="Edge Width (cm)", default=2.00, min=0.0, max=1000000.0, precision=3, )
    wireframe_coplanar_edge_width = FloatProperty(name="Coplanar Edge Width (cm)", default=1.00, min=0.0, max=1000000.0, precision=3, )
    wireframe_coplanar_threshold = FloatProperty(name="Coplanar Threshold", default=math.radians(20.000), min=math.radians(0.000), max=math.radians(100.000), precision=1, subtype='ANGLE', )
    
    enabled = BoolProperty(name="Enabled", default=True, )
    # blending_factor = FloatProperty(name="Blending Factor", default=0.0, min=0.0, max=100.0, precision=3, subtype='PERCENTAGE', )
    blending_factor = FloatProperty(name="Blending Factor", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    
    name = StringProperty(name="Name", default="Texture", )
    index = IntProperty(name="Index", default=-1, )
    use = EnumProperty(name="Type", items=[('BRICK', "Brick", ""), ('CHECKER', "Checker", ""), ('CIRCLE', "Circle", ""), ('GRADIENT3', "Gradient3", ""),
                                           ('GRADIENT', "Gradient", ""), ('GRID', "Grid", ""), ('MARBLE', "Marble", ""), ('NOISE', "Noise", ""),
                                           ('VORONOI', "Voronoi", ""), ('TILED', "Tiled", ""), ('WIREFRAME', "Wireframe", ""), ], default='NOISE', )


class ProceduralTexturesCollection(PropertyGroup):
    textures = CollectionProperty(name="Procedural Textures", type=ProceduralTextureItemProperties, )
    index = IntProperty(name="Active", default=-1, )


class TextureProperties(PropertyGroup):
    path = StringProperty(name="Path", default="", subtype='FILE_PATH', description="", )
    use_global_map = BoolProperty(name="Use Override Map", default=False, )
    
    channel = IntProperty(name="Channel", default=0, min=0, max=254, )
    
    tiling_method = EnumProperty(name="Tiling Method", items=[('TILE_XY', "Tile XY", ""), ('TILE_X', "Tile X", ""), ('TILE_Y', "Tile Y", ""), ('NO_TILING', "No Tiling", ""), ], default='TILE_XY', )
    tiling_units = EnumProperty(name="Tiling Units", items=[('0', "Relative", ""), ('1', "Meters", ""), ], default='0', )
    repeat = FloatVectorProperty(name="Repeat", default=(1.0, 1.0), min=-1000.0, max=1000.0, precision=3, size=2, )
    mirror_x = BoolProperty(name="Mirror X", default=False, )
    mirror_y = BoolProperty(name="Mirror Y", default=False, )
    offset = FloatVectorProperty(name="Offset", default=(0.0, 0.0), min=-1000.0, max=1000.0, precision=3, size=2, )
    rotation = FloatProperty(name="Rotation", default=math.radians(0.000), min=math.radians(0.000), max=math.radians(360.000), precision=3, subtype='ANGLE', )
    invert = BoolProperty(name="Invert", default=False, )
    use_alpha = BoolProperty(name="Alpha Only", default=False, )
    interpolation = BoolProperty(name="Interpolation", default=False, )
    brightness = FloatProperty(name="Brightness", default=0.0, min=-100.0, max=100.0, precision=3, subtype='PERCENTAGE', )
    contrast = FloatProperty(name="Contrast", default=0.0, min=-100.0, max=100.0, precision=3, subtype='PERCENTAGE', )
    saturation = FloatProperty(name="Saturation", default=0.0, min=-100.0, max=100.0, precision=3, subtype='PERCENTAGE', )
    hue = FloatProperty(name="Hue", default=0.0, min=-180.0, max=180.0, precision=3, subtype='PERCENTAGE', )
    clamp = IntVectorProperty(name="RGB Clamp", default=(0, 255), min=0, max=255, subtype='NONE', size=2, )
    
    normal_mapping_flip_red = BoolProperty(name="Flip X", default=False, )
    normal_mapping_flip_green = BoolProperty(name="Flip Y", default=True, )
    normal_mapping_full_range_blue = BoolProperty(name="Wide", default=False, )
    
    use = EnumProperty(name="Type", items=[('IMAGE', "Image", ""), ], default='IMAGE', )
    
    procedural = PointerProperty(name="Procedural Textures", type=ProceduralTexturesCollection, )
    
    @classmethod
    def register(cls):
        bpy.types.Texture.maxwell_render = PointerProperty(type=cls)
    
    @classmethod
    def unregister(cls):
        del bpy.types.Texture.maxwell_render


class SunProperties(PropertyGroup):
    lock_sun_skip = BoolProperty(default=False, options={'HIDDEN'}, )
    
    def _override_sun(self, context):
        if(self.lock_sun_skip):
            return
        self.lock_sun_skip = True
        suns = [o for o in bpy.data.objects if (o and o.type == 'LAMP' and o.data.type == 'SUN')]
        
        for o in suns:
            mx = o.data.maxwell_render
            if(mx == self):
                m = bpy.context.scene.world.maxwell_render
                s = o
                w = s.matrix_world
                _, r, _ = w.decompose()
                v = Vector((0, 0, 1))
                v.rotate(r)
                m.sun_dir_x = v.x
                m.sun_dir_y = v.y
                m.sun_dir_z = v.z
            else:
                mx.override = False
        
        self.lock_sun_skip = False
    
    override = BoolProperty(name="Override Environment Settings", default=False, description="When True, this lamp will override Sun direction from Environment Settings", update=_override_sun, )
    
    @classmethod
    def register(cls):
        bpy.types.SunLamp.maxwell_render = PointerProperty(type=cls)
    
    @classmethod
    def unregister(cls):
        del bpy.types.SunLamp.maxwell_render


class ExtParticlesProperties(PropertyGroup):
    material = StringProperty(name="Material", default="", )
    backface_material = StringProperty(name="Backface Material", default="", )
    
    opacity = FloatProperty(name="Opacity", default=100.0, min=0.0, max=100.0, subtype='PERCENTAGE', )
    hidden_camera = BoolProperty(name="Camera", default=False, )
    hidden_camera_in_shadow_channel = BoolProperty(name="Camera In Shadow Channel", default=False, )
    hidden_global_illumination = BoolProperty(name="Global Illumination", default=False, )
    hidden_reflections_refractions = BoolProperty(name="Reflections/Refractions", default=False, )
    hidden_zclip_planes = BoolProperty(name="Z-clip Planes", default=False, )
    object_id = FloatVectorProperty(name="Object ID", default=(0.0, 0.0, 0.0), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    
    hide = BoolProperty(name="Export as Hidden Object", default=False, description="Object will be exported, but with visibility set to Hidden. Useful for finishing scene in Studio")
    
    source = EnumProperty(name="Source", items=[('BLENDER_PARTICLES', "Blender Particles", ""), ('EXTERNAL_BIN', "External Bin", "")], default='BLENDER_PARTICLES', )
    bin_directory = StringProperty(name=".bin Output Directory", default="//", subtype='DIR_PATH', description="Output directory for .bin file(s)", )
    bin_overwrite = BoolProperty(name="Overwrite Existing", default=True, )
    embed = BoolProperty(name="Embed in MXS", default=True, )
    bl_use_velocity = BoolProperty(name="Particle Velocity", default=False, )
    bl_use_size = BoolProperty(name="Size Per Particle", default=False, )
    bl_size = FloatProperty(name="Size", default=0.1, min=0.000001, max=1000000.0, step=3, precision=6, )
    
    bin_type = EnumProperty(name="Type", items=[('STATIC', "Static", ""), ('SEQUENCE', "Sequence", "")], default='STATIC', )
    seq_limit = BoolProperty(name="Limit Sequence", default=False, )
    seq_start = IntProperty(name="Start Frame", default=0, min=0, max=100000000, )
    seq_end = IntProperty(name="Stop Frame", default=100, min=0, max=100000000, )
    private_bin_filename = StringProperty(name="File Name", default="", subtype='FILE_PATH', )
    
    bin_filename = StringProperty(name="File Name", default="", subtype='FILE_PATH', )
    bin_radius_multiplier = FloatProperty(name="Radius Multiplier", default=1.0, min=0.000001, max=1000000.0, step=3, precision=6, )
    bin_motion_blur_multiplier = FloatProperty(name="Motion Blur Multiplier", default=1.0, min=0.000001, max=1000000.0, step=3, precision=6, )
    bin_shutter_speed = FloatProperty(name="Shutter Speed", default=125.0, min=0.000001, max=1000000.0, step=2, precision=2, )
    bin_load_particles = FloatProperty(name="Load Particles (%)", default=100.0, min=0.0, max=100.0, step=2, precision=2, subtype='PERCENTAGE', )
    bin_axis_system = EnumProperty(name="Axis System", items=[('YZX_0', "YZX (xsi maya houdini)", ""), ('ZXY_1', "ZXY (3dsmax maya)", ""), ('YXZ_2', "YXZ (lw c4d rf)", "")], default='YZX_0', )
    bin_frame_number = IntProperty(name="Frame Number", default=0, min=-100000000, max=100000000, )
    bin_fps = FloatProperty(name="FPS", default=24.0, min=0.0, max=1000000.0, step=2, precision=2, )
    
    bin_advanced = BoolProperty(name="Advanced", default=False, )
    
    bin_extra_create_np_pp = IntProperty(name="Extra Particles Per Particle", default=0, min=0, max=100000000, )
    bin_extra_dispersion = FloatProperty(name="Extra Particles Dispersion", default=0.0, min=0.0, max=1000000.0, step=3, precision=6, )
    bin_extra_deformation = FloatProperty(name="Extra Particles Deformation", default=0.0, min=0.0, max=1000000.0, step=3, precision=6, )
    bin_load_force = BoolProperty(name="Load Force", default=False, )
    bin_load_vorticity = BoolProperty(name="Load Vorticity", default=False, )
    bin_load_normal = BoolProperty(name="Load Normal", default=False, )
    bin_load_neighbors_num = BoolProperty(name="Load Neighbours", default=False, )
    bin_load_uv = BoolProperty(name="Load UV", default=False, )
    bin_load_age = BoolProperty(name="Load Age", default=False, )
    bin_load_isolation_time = BoolProperty(name="Load Isolation Time", default=False, )
    bin_load_viscosity = BoolProperty(name="Load Viscosity", default=False, )
    bin_load_density = BoolProperty(name="Load Density", default=False, )
    bin_load_pressure = BoolProperty(name="Load Pressure", default=False, )
    bin_load_mass = BoolProperty(name="Load Mass", default=False, )
    bin_load_temperature = BoolProperty(name="Load Temperature", default=False, )
    bin_load_id = BoolProperty(name="Load ID", default=False, )
    bin_min_force = FloatProperty(name="Min Force", default=0.0, min=0.0, max=1000000.0, step=3, )
    bin_max_force = FloatProperty(name="Max Force", default=1.0, min=0.0, max=1000000.0, step=3, )
    bin_min_vorticity = FloatProperty(name="Min Vorticity", default=0.0, min=0.0, max=1000000.0, step=3, )
    bin_max_vorticity = FloatProperty(name="Max Vorticity", default=1.0, min=0.0, max=1000000.0, step=3, )
    bin_min_nneighbors = IntProperty(name="Min Neighbours", default=0, min=0, max=1000000, step=3, )
    bin_max_nneighbors = IntProperty(name="Max Neighbours", default=1, min=0, max=1000000, step=3, )
    bin_min_age = FloatProperty(name="Min Age", default=0.0, min=0.0, max=1000000.0, step=3, )
    bin_max_age = FloatProperty(name="Max Age", default=1.0, min=0.0, max=1000000.0, step=3, )
    bin_min_isolation_time = FloatProperty(name="Min Isolation Time", default=0.0, min=0.0, max=1000000.0, step=3, )
    bin_max_isolation_time = FloatProperty(name="Max Isolation Time", default=1.0, min=0.0, max=1000000.0, step=3, )
    bin_min_viscosity = FloatProperty(name="Min Viscosity", default=0.0, min=0.0, max=1000000.0, step=3, )
    bin_max_viscosity = FloatProperty(name="Max Viscosity", default=1.0, min=0.0, max=1000000.0, step=3, )
    bin_min_density = FloatProperty(name="Min Density", default=0.0, min=0.0, max=1000000.0, step=3, )
    bin_max_density = FloatProperty(name="Max Density", default=1.0, min=0.0, max=1000000.0, step=3, )
    bin_min_pressure = FloatProperty(name="Min Pressure", default=0.0, min=0.0, max=1000000.0, step=3, )
    bin_max_pressure = FloatProperty(name="Max Pressure", default=1.0, min=0.0, max=1000000.0, step=3, )
    bin_min_mass = FloatProperty(name="Min Mass", default=0.0, min=0.0, max=1000000.0, step=3, )
    bin_max_mass = FloatProperty(name="Max Mass", default=1.0, min=0.0, max=1000000.0, step=3, )
    bin_min_temperature = FloatProperty(name="Min Temperature", default=0.0, min=0.0, max=1000000.0, step=3, )
    bin_max_temperature = FloatProperty(name="Max Temperature", default=1.0, min=0.0, max=1000000.0, step=3, )
    bin_min_velocity = FloatProperty(name="Min Velocity Modulus", default=0.0, min=0.0, max=1000000.0, step=3, )
    bin_max_velocity = FloatProperty(name="Max Velocity Modulus", default=1.0, min=0.0, max=1000000.0, step=3, )
    
    uv_layer = StringProperty(name="UV Layer", default="", )


class ExtHairProperties(PropertyGroup):
    material = StringProperty(name="Material", default="", )
    backface_material = StringProperty(name="Backface Material", default="", )
    
    opacity = FloatProperty(name="Opacity", default=100.0, min=0.0, max=100.0, subtype='PERCENTAGE', )
    hidden_camera = BoolProperty(name="Camera", default=False, )
    hidden_camera_in_shadow_channel = BoolProperty(name="Camera In Shadow Channel", default=False, )
    hidden_global_illumination = BoolProperty(name="Global Illumination", default=False, )
    hidden_reflections_refractions = BoolProperty(name="Reflections/Refractions", default=False, )
    hidden_zclip_planes = BoolProperty(name="Z-clip Planes", default=False, )
    object_id = FloatVectorProperty(name="Object ID", default=(0.0, 0.0, 0.0), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    hide = BoolProperty(name="Export as Hidden Object", default=False, description="Object will be exported, but with visibility set to Hidden. Useful for finishing scene in Studio")
    
    hair_type = EnumProperty(name="Hair Type", items=[('HAIR', "Hair", ""), ('GRASS', "Grass", ""), ], default='HAIR', )
    
    hair_root_radius = FloatProperty(name="Root Radius (mm)", default=0.1, min=0.001, max=100000.0, precision=3, )
    hair_tip_radius = FloatProperty(name="Tip Radius (mm)", default=0.05, min=0.001, max=100000.0, precision=3, )
    grass_root_width = FloatProperty(name="Root Width (mm)", default=5.0, min=0.001, max=100000.0, precision=3, )
    grass_tip_width = FloatProperty(name="Tip Width (mm)", default=1.0, min=0.001, max=100000.0, precision=3, )
    
    uv_layer = StringProperty(name="UV Layer", default="", )
    
    display_percent = FloatProperty(name="Display Percent (%)", default=10.0, min=0.0, max=100.0, precision=0, subtype='PERCENTAGE', )
    display_max_blades = IntProperty(name="Display Max. Blades", default=1000, min=0, max=100000, )
    display_max_hairs = IntProperty(name="Display Max. Hairs", default=1000, min=0, max=100000, )


class ExtClonerProperties(PropertyGroup):
    source = EnumProperty(name="Source", items=[('BLENDER_PARTICLES', "Blender Particles", ""), ('EXTERNAL_BIN', "External Bin", "")], default='BLENDER_PARTICLES', )
    directory = StringProperty(name=".bin Output Directory", default="//", subtype='DIR_PATH', description="Output directory for .bin file(s)", )
    overwrite = BoolProperty(name="Overwrite Existing", default=True, )
    bl_use_velocity = BoolProperty(name="Particle Velocity", default=True, )
    bl_use_size = BoolProperty(name="Size Per Particle", default=False, )
    bl_size = FloatProperty(name="Size", default=0.1, min=0.000001, max=1000000.0, step=3, precision=6, )
    
    filename = StringProperty(name="File Name", default="", subtype='FILE_PATH', )
    embed = BoolProperty(name="Embed in MXS", default=True, )
    
    radius = FloatProperty(name="Radius Multiplier", default=1.0, min=0.000001, max=1000000.0, )
    mb_factor = FloatProperty(name="Motion Blur Multiplier", default=1.0, min=0.0, max=1000000.0, )
    load_percent = FloatProperty(name="Load (%)", default=100.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    start_offset = IntProperty(name="Start Offset", default=0, min=0, max=100000000, )
    extra_npp = IntProperty(name="Extra Part. Per Particle", default=0, min=0, max=100000000, )
    extra_p_dispersion = FloatProperty(name="Extra Part. Dispersion", default=0.0, min=0.0, max=1000000.0, )
    extra_p_deformation = FloatProperty(name="Extra Part. Deformation", default=0.0, min=0.0, max=1000000.0, )
    align_to_velocity = BoolProperty(name="Align To Velocity", default=False, )
    scale_with_radius = BoolProperty(name="Scale With Particle Radius", default=False, )
    inherit_obj_id = BoolProperty(name="Inherit Object Id", default=False, )
    
    display_percent = FloatProperty(name="Display Percent (%)", default=10.0, min=0.0, max=100.0, precision=0, subtype='PERCENTAGE', )
    display_max = IntProperty(name="Display Max. Particles", default=1000, min=0, max=100000, )


class ParticleInstancesProperties(PropertyGroup):
    hide = BoolProperty(name="Export Instances as Hidden Objects", default=False, description="Objects will be exported, but with visibility set to Hidden. Useful for finishing scene in Studio")


class ParticlesProperties(PropertyGroup):
    use = EnumProperty(name="Type", items=[('HAIR', "Hair", ""),
                                           ('PARTICLES', "Particles", ""),
                                           ('CLONER', "Cloner", ""),
                                           ('PARTICLE_INSTANCES', "Instances", ""),
                                           ('NONE', "None", "")], default='NONE', )
    
    particles = PointerProperty(name="Particles", type=ExtParticlesProperties, )
    hair = PointerProperty(name="Hair", type=ExtHairProperties, )
    cloner = PointerProperty(name="Cloner", type=ExtClonerProperties, )
    instances = PointerProperty(name="Instances", type=ParticleInstancesProperties, )
    
    @classmethod
    def register(cls):
        bpy.types.ParticleSettings.maxwell_render = PointerProperty(type=cls)
    
    @classmethod
    def unregister(cls):
        del bpy.types.ParticleSettings.maxwell_render


class MaterialBSDFProperties(PropertyGroup):
    expanded_ior = BoolProperty(name="Expanded", default=True, )
    expanded_surface = BoolProperty(name="Expanded", default=True, )
    expanded_subsurface = BoolProperty(name="Expanded", default=False, )
    
    visible = BoolProperty(name="Visible", default=True, )
    
    weight = FloatProperty(name="Weight", default=100.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    weight_map_enabled = BoolProperty(name="Weight Map Enabled", default=False, )
    weight_map = StringProperty(name="Weight Map", default="", get=MaterialEditorCallbacks.bsdf_weight_map_get, set=MaterialEditorCallbacks.bsdf_weight_map_set, )
    
    ior = EnumProperty(name="IOR", items=[('0', "Custom", ""), ('1', "Measured Data", ""), ], default='0', )
    complex_ior = StringProperty(name="Complex IOR", default="", subtype='FILE_PATH', )
    
    reflectance_0 = FloatVectorProperty(name="Reflectance 0", default=(0.6, 0.6, 0.6), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    reflectance_0_map_enabled = BoolProperty(name="Reflectance 0 Map Enabled", default=False, )
    reflectance_0_map = StringProperty(name="Reflectance 0 Map", default="", get=MaterialEditorCallbacks.bsdf_reflectance_0_map_get, set=MaterialEditorCallbacks.bsdf_reflectance_0_map_set, )
    reflectance_90 = FloatVectorProperty(name="Reflectance 90", default=(1.0, 1.0, 1.0), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    reflectance_90_map_enabled = BoolProperty(name="Reflectance 90 Map Enabled", default=False, )
    reflectance_90_map = StringProperty(name="Reflectance 90 Map", default="", get=MaterialEditorCallbacks.bsdf_reflectance_90_map_get, set=MaterialEditorCallbacks.bsdf_reflectance_90_map_set, )
    transmittance = FloatVectorProperty(name="Transmittance", default=(0.0, 0.0, 0.0), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    transmittance_map_enabled = BoolProperty(name="Transmittance Map Enabled", default=False, )
    transmittance_map = StringProperty(name="Transmittance Map", default="", get=MaterialEditorCallbacks.bsdf_transmittance_map_get, set=MaterialEditorCallbacks.bsdf_transmittance_map_set, )
    
    attenuation = FloatProperty(name="Attenuation", default=1.0, min=0.0, max=999.0, precision=1, )
    attenuation_units = EnumProperty(name="Attenuation Units", items=[('0', "nm", ""), ('1', "um", ""), ('2', "mm", ""), ('3', "cm", ""), ('4', "dm", ""), ('5', "m", ""), ], default='0', )
    
    nd = FloatProperty(name="Nd", default=3.0, min=0.01, max=1000.0, precision=3, )
    force_fresnel = BoolProperty(name="Force Fresnel", default=False, )
    
    k = FloatProperty(name="K", default=0.0, min=0.0, max=1000.0, precision=3, )
    abbe = FloatProperty(name="Abbe", default=1.0, min=1.0, max=2000.0, precision=3, )
    r2_enabled = BoolProperty(name="R2 Enabled", default=False, )
    r2_falloff_angle = FloatProperty(name="R2 Falloff Angle", default=math.radians(75.0), min=math.radians(0.0), max=math.radians(90.0), precision=2, subtype='ANGLE', )
    r2_influence = FloatProperty(name="R2 Influence", default=0.0, min=0.0, max=100.0, precision=2, subtype='PERCENTAGE', )
    
    roughness = FloatProperty(name="Roughness", default=100.0, min=0.0, max=100.0, precision=2, subtype='PERCENTAGE', )
    roughness_map_enabled = BoolProperty(name="Roughness Map Enabled", default=False, )
    roughness_map = StringProperty(name="Roughness Map", default="", get=MaterialEditorCallbacks.bsdf_roughness_map_get, set=MaterialEditorCallbacks.bsdf_roughness_map_set, )
    
    bump = FloatProperty(name="Bump", default=30.0, min=-2000.0, max=2000.0, precision=2, )
    bump_map_enabled = BoolProperty(name="Bump Map Enabled", default=False, )
    bump_map = StringProperty(name="Bump Map", default="", get=MaterialEditorCallbacks.bsdf_bump_map_get, set=MaterialEditorCallbacks.bsdf_bump_map_set, )
    bump_map_use_normal = BoolProperty(name="Bump Map Use Normal", default=False, )
    bump_normal = FloatProperty(name="Bump", default=100.0, min=-2000.0, max=2000.0, precision=2, )
    
    anisotropy = FloatProperty(name="Anisotropy", default=0.0, min=0.0, max=100.0, precision=2, subtype='PERCENTAGE', )
    anisotropy_map_enabled = BoolProperty(name="Anisotropy Map Enabled", default=False, )
    anisotropy_map = StringProperty(name="Anisotropy Map", default="", get=MaterialEditorCallbacks.bsdf_anisotropy_map_get, set=MaterialEditorCallbacks.bsdf_anisotropy_map_set, )
    
    anisotropy_angle = FloatProperty(name="Anisotropy Angle", default=math.radians(0.0), min=math.radians(0.0), max=math.radians(360.0), precision=2, subtype='ANGLE', )
    anisotropy_angle_map_enabled = BoolProperty(name="Anisotropy Angle Map Enabled", default=False, )
    anisotropy_angle_map = StringProperty(name="Anisotropy Angle Map", default="", get=MaterialEditorCallbacks.bsdf_anisotropy_angle_map_get, set=MaterialEditorCallbacks.bsdf_anisotropy_angle_map_set, )
    
    scattering = FloatVectorProperty(name="Scattering", default=(0.5, 0.5, 0.5), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    coef = FloatProperty(name="Coef", default=0.0, min=0.0, max=99999.0, precision=2, )
    asymmetry = FloatProperty(name="Asymmetry", default=0.0, min=-1.0, max=1.0, precision=3, )
    single_sided = BoolProperty(name="Single Sided", default=False, )
    single_sided_value = FloatProperty(name="Value (mm)", default=1.0, min=0.001, max=1000.0, precision=3, )
    single_sided_map_enabled = BoolProperty(name="Single Sided Map Enabled", default=False, )
    single_sided_map = StringProperty(name="Single Sided Map", default="", get=MaterialEditorCallbacks.bsdf_single_sided_map_get, set=MaterialEditorCallbacks.bsdf_single_sided_map_set, )
    single_sided_min = FloatProperty(name="Min", default=0.001, min=0.001, max=1000.0, precision=3, )
    single_sided_max = FloatProperty(name="Max", default=10.0, min=0.001, max=1000.0, precision=3, )


class MaterialCoatingProperties(PropertyGroup):
    expanded = BoolProperty(name="Expanded", default=False, )
    enabled = BoolProperty(name="Enabled", default=False, )
    
    thickness = FloatProperty(name="Thickness (nm)", default=500.0, min=1.0, max=1000000.0, precision=3, )
    thickness_map_enabled = BoolProperty(name="Thickness Map Enabled", default=False, )
    thickness_map = StringProperty(name="Thickness Map", default="", get=MaterialEditorCallbacks.coating_thickness_map_get, set=MaterialEditorCallbacks.coating_thickness_map_set, )
    thickness_map_min = FloatProperty(name="Thickness Map Min", default=100.0, min=1.0, max=1000000.0, precision=3, )
    thickness_map_max = FloatProperty(name="Thickness Map Max", default=1000.0, min=1.0, max=1000000.0, precision=3, )
    
    ior = EnumProperty(name="IOR", items=[('0', "Custom", ""), ('1', "Measured Data", ""), ], default='0', )
    complex_ior = StringProperty(name="Complex IOR", default="", subtype='FILE_PATH', )
    
    reflectance_0 = FloatVectorProperty(name="Reflectance 0", default=(0.6, 0.6, 0.6), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    reflectance_0_map_enabled = BoolProperty(name="Reflectance 0 Map Enabled", default=False, )
    reflectance_0_map = StringProperty(name="Reflectance 0 Map", default="", get=MaterialEditorCallbacks.coating_reflectance_0_map_get, set=MaterialEditorCallbacks.coating_reflectance_0_map_set, )
    reflectance_90 = FloatVectorProperty(name="Reflectance 90", default=(1.0, 1.0, 1.0), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    reflectance_90_map_enabled = BoolProperty(name="Reflectance 90 Map Enabled", default=False, )
    reflectance_90_map = StringProperty(name="Reflectance 90 Map", default="", get=MaterialEditorCallbacks.coating_reflectance_90_map_get, set=MaterialEditorCallbacks.coating_reflectance_90_map_set, )
    
    nd = FloatProperty(name="Nd", default=3.0, min=0.01, max=1000.0, precision=3, )
    force_fresnel = BoolProperty(name="Force Fresnel", default=False, )
    k = FloatProperty(name="K", default=0.0, min=0.0, max=1000.0, precision=3, )
    r2_enabled = BoolProperty(name="R2 Enabled", default=False, )
    r2_falloff_angle = FloatProperty(name="R2 Falloff Angle", default=math.radians(75.0), min=math.radians(0.0), max=math.radians(90.0), precision=2, subtype='ANGLE', )


class MaterialDisplacementProperties(PropertyGroup):
    expanded = BoolProperty(name="Expanded", default=False, )
    enabled = BoolProperty(name="Enabled", default=False, )
    
    map = StringProperty(name="Map", default="", )
    type = EnumProperty(name="Type", items=[('0', "On The Fly", ""), ('1', "Pretessellated", ""), ('2', "Vector", ""), ], default='1', )
    subdivision = IntProperty(name="Subdivision", default=5, min=0, max=10000, )
    adaptive = BoolProperty(name="Adaptive", default=False, )
    subdivision_method = EnumProperty(name="Subdivision Method", items=[('0', "Flat", ""), ('1', "Catmull/Loop", ""), ], default='0', )
    offset = FloatProperty(name="Offset", default=0.5, min=0.0, max=1.0, precision=1, subtype='PERCENTAGE', )
    smoothing = BoolProperty(name="Smoothing", default=True, )
    uv_interpolation = EnumProperty(name="UV Interpolation", items=[('0', "None", ""), ('1', "Edges", ""), ('2', "Edges And Corners", ""), ('3', "Sharp", ""), ], default='2', )
    
    height = FloatProperty(name="Height", default=2.0, min=-1000.0, max=1000.0, precision=3, )
    height_units = EnumProperty(name="Height Units", items=[('0', "%", ""), ('1', "cm", ""), ], default='0', )
    
    v3d_preset = EnumProperty(name="Preset", items=[('0', "Custom", ""), ('1', "Zbrush Tangent", ""), ('2', "Zbrush World", ""), ('3', "Mudbox Absolute Tangent", ""), ('4', "Mudbox Object", ""), ('5', "Mudbox World", ""), ('6', "Realflow", ""), ('7', "Modo", ""), ], default='0', )
    v3d_transform = EnumProperty(name="Transform", items=[('0', "Tangent", ""), ('1', "Object", ""), ('2', "World", ""), ], default='0', )
    v3d_rgb_mapping = EnumProperty(name="RGB Mapping", items=[('0', "XYZ", ""), ('1', "XZY", ""), ('2', "YZX", ""), ('3', "YXZ", ""), ('4', "ZXY", ""), ('5', "ZYX", ""), ], default='0', )
    v3d_scale = FloatVectorProperty(name="Scale", default=(1.0, 1.0, 1.0), min=-100000.0, max=100000.0, precision=2, subtype='XYZ', )
    

class MaterialEmitterProperties(PropertyGroup):
    expanded = BoolProperty(name="Expanded", default=False, )
    enabled = BoolProperty(name="Enabled", default=False, )
    
    lock_color = BoolProperty(default=False, options={'HIDDEN'}, )
    
    def update_color(self, context):
        if(self.lock_color):
            return
        self.lock_color = True
        
        if(self.emission == '0' and self.color_black_body_enabled):
            self.color = utils.color_temperature_to_rgb(self.color_black_body)
        
        self.lock_color = False
    
    type = EnumProperty(name="Type", items=[('0', "Area", ""), ('1', "IES", ""), ('2', "Spot", ""), ], default='0', )
    ies_data = StringProperty(name="Data", default="", subtype='FILE_PATH', )
    ies_intensity = FloatProperty(name="Intensity", default=1.0, min=0.0, max=100000.0, precision=1, )
    spot_map_enabled = BoolProperty(name="Spot Map Enabled", default=False, )
    spot_map = StringProperty(name="Spot Map", default="", get=MaterialEditorCallbacks.emitter_spot_map_get, set=MaterialEditorCallbacks.emitter_spot_map_set, )
    spot_cone_angle = FloatProperty(name="Cone Angle", default=math.radians(45.0), min=math.radians(0.01), max=math.radians(179.99), precision=2, subtype='ANGLE', )
    spot_falloff_angle = FloatProperty(name="FallOff Angle", default=math.radians(10.0), min=math.radians(0.0), max=math.radians(89.99), precision=2, subtype='ANGLE', )
    spot_falloff_type = EnumProperty(name="FallOff Type", items=[('0', "Linear", ""), ('1', "Square Root", ""), ('2', "Sinusoidal", ""), ('3', "Squared Sinusoidal", ""),
                                                                 ('4', "Quadratic", ""), ('5', "Cubic", ""), ], default='0', )
    spot_blur = FloatProperty(name="Blur", default=1.0, min=0.01, max=1000.00, precision=2, )
    emission = EnumProperty(name="Emission", items=[('0', "Color", ""), ('1', "Temperature", ""), ('2', "HDR Image", ""), ], default='0', )
    color = FloatVectorProperty(name="Color", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, subtype='COLOR', update=update_color, )
    color_black_body_enabled = BoolProperty(name="Temperature Enabled", default=False, update=update_color, )
    color_black_body = FloatProperty(name="Temperature (K)", default=6500.0, min=273.0, max=100000.0, precision=1, update=update_color, )
    luminance = EnumProperty(name="Luminance", items=[('0', "Power & Efficacy", ""), ('1', "Lumen", ""), ('2', "Lux", ""), ('3', "Candela", ""), ('4', "Luminance", ""), ], default='0', )
    luminance_power = FloatProperty(name="Power (W)", default=40.0, min=0.0, max=1000000000.0, precision=1, )
    luminance_efficacy = FloatProperty(name="Efficacy (lm/W)", default=17.6, min=0.0, max=683.0, precision=1, )
    luminance_output = FloatProperty(name="Output (lm, lm, lm/m, cd, cd/m)", default=100.0, min=0.0, max=1000000000.0, precision=1, )
    temperature_value = FloatProperty(name="Value (K)", default=6500.0, min=273.0, max=100000.0, precision=3, )
    hdr_map = StringProperty(name="Image", default="", )
    hdr_intensity = FloatProperty(name="Intensity", default=1.0, min=0.0, max=1000000.0, precision=1, )


class MaterialCustomLayerBSDFsItem(PropertyGroup):
    name = StringProperty(name="Name", default="Layer", )
    bsdf = PointerProperty(name="BSDF", type=MaterialBSDFProperties, )
    coating = PointerProperty(name="Emitter", type=MaterialCoatingProperties, )


class MaterialCustomLayerBSDFs(PropertyGroup):
    bsdfs = CollectionProperty(name="Material Layers", type=MaterialCustomLayerBSDFsItem, )
    index = IntProperty(name="Active", default=-1, )


class MaterialLayerProperties(PropertyGroup):
    expanded = BoolProperty(name="Expanded", default=True, )
    
    visible = BoolProperty(name="Visible", default=True, )
    
    opacity = FloatProperty(name="Opacity/Mask", default=100.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    opacity_map_enabled = BoolProperty(name="Opacity/Mask Map Enabled", default=False, )
    opacity_map = StringProperty(name="Opacity/Mask Map", default="", get=MaterialEditorCallbacks.layer_opacity_map_get, set=MaterialEditorCallbacks.layer_opacity_map_set, )
    blending = EnumProperty(name="Layer Blending", items=[('0', "N", ""), ('1', "A", ""), ], default='0', )
    
    bsdfs = PointerProperty(name="BSDFs", type=MaterialCustomLayerBSDFs, )


class MaterialCustomLayersItem(PropertyGroup):
    name = StringProperty(name="Name", default="Layer", )
    layer = PointerProperty(name="Layer", type=MaterialLayerProperties, )
    emitter = PointerProperty(type=MaterialEmitterProperties, )


class MaterialCustomLayers(PropertyGroup):
    layers = CollectionProperty(name="Material Layers", type=MaterialCustomLayersItem, )
    index = IntProperty(name="Active", default=-1, )


class ExtMaterialProperties(PropertyGroup):
    lock_emitter_color = BoolProperty(default=False, options={'HIDDEN'}, )
    
    def update_emitter_color(self, context):
        if(self.lock_emitter_color):
            return
        self.lock_emitter_color = True
        
        if(self.emitter_emission == '0' and self.emitter_color_black_body_enabled):
            self.emitter_color = utils.color_temperature_to_rgb(self.emitter_color_black_body)
        
        self.lock_emitter_color = False
    
    emitter_type = EnumProperty(name="Type", items=[('0', "Area", ""), ('1', "IES", ""), ('2', "Spot", ""), ], default='0', )
    emitter_ies_data = StringProperty(name="Data", default="", subtype='FILE_PATH', )
    emitter_ies_intensity = FloatProperty(name="Intensity", default=1.0, min=0.0, max=100000.0, precision=1, )
    emitter_spot_map_enabled = BoolProperty(name="Spot Map Enabled", default=False, )
    emitter_spot_map = StringProperty(name="Spot Map", default="", get=MaterialEditorCallbacks.ext_emitter_spot_map_get, set=MaterialEditorCallbacks.ext_emitter_spot_map_set, )
    emitter_spot_cone_angle = FloatProperty(name="Cone Angle", default=math.radians(45.0), min=math.radians(0.01), max=math.radians(179.99), precision=2, subtype='ANGLE', )
    emitter_spot_falloff_angle = FloatProperty(name="FallOff Angle", default=math.radians(10.0), min=math.radians(0.0), max=math.radians(89.99), precision=2, subtype='ANGLE', )
    emitter_spot_falloff_type = EnumProperty(name="FallOff Type", items=[('0', "Linear", ""), ('1', "Square Root", ""), ('2', "Sinusoidal", ""), ('3', "Squared Sinusoidal", ""),
                                                                         ('4', "Quadratic", ""), ('5', "Cubic", ""), ], default='0', )
    emitter_spot_blur = FloatProperty(name="Blur", default=1.0, min=0.01, max=1000.00, precision=2, )
    emitter_emission = EnumProperty(name="Emission", items=[('0', "Color", ""), ('1', "Temperature", ""), ('2', "HDR Image", ""), ], default='0', )
    emitter_color = FloatVectorProperty(name="Color", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, subtype='COLOR', update=update_emitter_color, )
    emitter_color_black_body_enabled = BoolProperty(name="Temperature Enabled", default=False, update=update_emitter_color, )
    emitter_color_black_body = FloatProperty(name="Temperature (K)", default=6500.0, min=273.0, max=100000.0, precision=1, update=update_emitter_color, )
    emitter_luminance = EnumProperty(name="Luminance", items=[('0', "Power & Efficacy", ""), ('1', "Lumen", ""), ('2', "Lux", ""), ('3', "Candela", ""), ('4', "Luminance", ""), ], default='0', )
    emitter_luminance_power = FloatProperty(name="Power (W)", default=40.0, min=0.0, max=1000000000.0, precision=1, )
    emitter_luminance_efficacy = FloatProperty(name="Efficacy (lm/W)", default=17.6, min=0.0, max=683.0, precision=1, )
    emitter_luminance_output = FloatProperty(name="Output (lm, lm, lm/m, cd, cd/m)", default=100.0, min=0.0, max=1000000000.0, precision=1, )
    emitter_temperature_value = FloatProperty(name="Value (K)", default=6500.0, min=273.0, max=100000.0, precision=3, )
    emitter_hdr_map = StringProperty(name="Image", default="", )
    emitter_hdr_intensity = FloatProperty(name="Intensity", default=1.0, min=0.0, max=1000000.0, precision=1, )
    
    ags_color = FloatVectorProperty(name="Color", default=(1.0, 1.0, 1.0), min=0.0, max=1.0, subtype='COLOR', )
    ags_reflection = FloatProperty(name="Reflection (%)", default=12.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    ags_type = EnumProperty(name="Type", items=[('0', "Normal", ""), ('1', "Clear", "")], default='0', )
    
    opaque_color_type = BoolProperty(name="Color Type", default=False, )
    opaque_color = FloatVectorProperty(name="Color", default=(220 / 255, 220 / 255, 220 / 255), min=0.0, max=1.0, subtype='COLOR', )
    opaque_color_map = StringProperty(name="Color Map", default="", get=MaterialEditorCallbacks.ext_opaque_color_map_get, set=MaterialEditorCallbacks.ext_opaque_color_map_set, )
    opaque_shininess_type = BoolProperty(name="Shininess Type", default=False, )
    opaque_shininess = FloatProperty(name="Shininess (%)", default=40.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    opaque_shininess_map = StringProperty(name="Shininess Map", default="", get=MaterialEditorCallbacks.ext_opaque_shininess_map_get, set=MaterialEditorCallbacks.ext_opaque_shininess_map_set, )
    opaque_roughness_type = BoolProperty(name="Roughness Type", default=False, )
    opaque_roughness = FloatProperty(name="Roughness (%)", default=25.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    opaque_roughness_map = StringProperty(name="Roughness Map", default="", get=MaterialEditorCallbacks.ext_opaque_roughness_map_get, set=MaterialEditorCallbacks.ext_opaque_roughness_map_set, )
    opaque_clearcoat = BoolProperty(name="Clearcoat", default=False, )
    
    transparent_color_type = BoolProperty(name="Color Type", default=False, )
    transparent_color = FloatVectorProperty(name="Color", default=(182 / 255, 182 / 255, 182 / 255), min=0.0, max=1.0, subtype='COLOR', )
    transparent_color_map = StringProperty(name="Color Map", default="", get=MaterialEditorCallbacks.ext_transparent_color_map_get, set=MaterialEditorCallbacks.ext_transparent_color_map_set, )
    transparent_ior = FloatProperty(name="Ref. Index", default=1.51, min=1.001, max=2.5, precision=3, )
    transparent_transparency = FloatProperty(name="Transparency (cm)", default=30.0, min=0.1, max=999.0, precision=1, )
    transparent_roughness_type = BoolProperty(name="Roughness Type", default=False, )
    transparent_roughness = FloatProperty(name="Roughness (%)", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    transparent_roughness_map = StringProperty(name="Roughness Map", default="", get=MaterialEditorCallbacks.ext_transparent_roughness_map_get, set=MaterialEditorCallbacks.ext_transparent_roughness_map_set, )
    transparent_specular_tint = FloatProperty(name="Specular Tint (%)", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    transparent_dispersion = FloatProperty(name="Dispersion (%)", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    transparent_clearcoat = BoolProperty(name="Clearcoat", default=False, )
    
    metal_ior = EnumProperty(name="Type", items=[('0', "Aluminium", ""), ('1', "Chromium", ""), ('2', "Cobalt", ""), ('3', "Copper", ""), ('4', "Germanium", ""), ('5', "Gold", ""),
                                                 ('6', "Iron", ""), ('7', "Nickel", ""), ('8', "Silver", ""), ('9', "Titanium", ""), ('10', "Vanadium", ""), ], default='0', )
    metal_tint = FloatProperty(name="Tint", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    metal_color_type = BoolProperty(name="Color Type", default=False, )
    metal_color = FloatVectorProperty(name="Color", default=(167 / 255, 167 / 255, 167 / 255), min=0.0, max=1.0, subtype='COLOR', )
    metal_color_map = StringProperty(name="Color Map", default="", get=MaterialEditorCallbacks.ext_metal_color_map_get, set=MaterialEditorCallbacks.ext_metal_color_map_set, )
    metal_roughness_type = BoolProperty(name="Roughness Type", default=False, )
    metal_roughness = FloatProperty(name="Roughness", default=30.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    metal_roughness_map = StringProperty(name="Roughness Map", default="", get=MaterialEditorCallbacks.ext_metal_roughness_map_get, set=MaterialEditorCallbacks.ext_metal_roughness_map_set, )
    metal_anisotropy_type = BoolProperty(name="Anisotropy Type", default=False, )
    metal_anisotropy = FloatProperty(name="Anisotropy", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    metal_anisotropy_map = StringProperty(name="Anisotropy Map", default="", get=MaterialEditorCallbacks.ext_metal_anisotropy_map_get, set=MaterialEditorCallbacks.ext_metal_anisotropy_map_set, )
    metal_angle_type = BoolProperty(name="Angle Type", default=False, )
    metal_angle = FloatProperty(name="Angle", default=math.radians(0.0), min=math.radians(0.0), max=math.radians(360.0), precision=1, subtype='ANGLE', )
    metal_angle_map = StringProperty(name="Angle Map", default="", get=MaterialEditorCallbacks.ext_metal_angle_map_get, set=MaterialEditorCallbacks.ext_metal_angle_map_set, )
    metal_dust_type = BoolProperty(name="Dust & Dirt Type", default=False, )
    metal_dust = FloatProperty(name="Dust & Dirt", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    metal_dust_map = StringProperty(name="Dust & Dirt Map", default="", get=MaterialEditorCallbacks.ext_metal_dust_map_get, set=MaterialEditorCallbacks.ext_metal_dust_map_set, )
    metal_perforation_enabled = BoolProperty(name="Perforation Enabled", default=False, )
    metal_perforation_map = StringProperty(name="Perforation Map", default="", get=MaterialEditorCallbacks.ext_metal_perforation_map_get, set=MaterialEditorCallbacks.ext_metal_perforation_map_set, )
    
    translucent_scale = FloatProperty(name="Scale (x10 cm)", default=8.0, min=0.00001, max=1000000.0, precision=2, )
    translucent_ior = FloatProperty(name="Ref. Index", default=1.3, min=1.001, max=2.5, precision=3, )
    translucent_color_type = BoolProperty(name="Color Type", default=False, )
    translucent_color = FloatVectorProperty(name="Color", default=(250 / 255, 245 / 255, 230 / 255), min=0.0, max=1.0, subtype='COLOR', )
    translucent_color_map = StringProperty(name="Color Map", default="", get=MaterialEditorCallbacks.ext_translucent_color_map_get, set=MaterialEditorCallbacks.ext_translucent_color_map_set, )
    translucent_hue_shift = FloatProperty(name="Hue Shift", default=0.0, min=-120.0, max=120.0, precision=1, )
    translucent_invert_hue = BoolProperty(name="Invert Hue", default=True, )
    translucent_vibrance = FloatProperty(name="Vibrance", default=11.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    translucent_density = FloatProperty(name="Density", default=90.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    translucent_opacity = FloatProperty(name="Opacity", default=50.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    translucent_roughness_type = BoolProperty(name="Roughness Type", default=False, )
    translucent_roughness = FloatProperty(name="Roughness", default=17.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    translucent_roughness_map = StringProperty(name="Roughness Map", default="", get=MaterialEditorCallbacks.ext_translucent_roughness_map_get, set=MaterialEditorCallbacks.ext_translucent_roughness_map_set, )
    translucent_specular_tint = FloatProperty(name="Specular Tint (%)", default=0.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    translucent_clearcoat = BoolProperty(name="Clearcoat", default=False, )
    translucent_clearcoat_ior = FloatProperty(name="Clearcoat IOR", default=1.3, min=1.001, max=2.5, precision=3, )
    
    carpaint_color = FloatVectorProperty(name="Color", default=(100 / 255, 0 / 255, 16 / 255), min=0.0, max=1.0, subtype='COLOR', )
    carpaint_metallic = FloatProperty(name="Metallic", default=100.0, min=0.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    carpaint_topcoat = FloatProperty(name="Topcoat", default=50.0, min=1.001, max=100.0, precision=3, subtype='PERCENTAGE', )
    
    hair_color_type = BoolProperty(name="Color Type", default=False, )
    hair_color = FloatVectorProperty(name="Color", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, subtype='COLOR', )
    hair_color_map = StringProperty(name="Color Map", default="", get=MaterialEditorCallbacks.ext_hair_color_map_get, set=MaterialEditorCallbacks.ext_hair_color_map_set, )
    hair_root_tip_map = StringProperty(name="Root-Tip Map", default="", )
    hair_root_tip_weight_type = BoolProperty(name="Root-Tip Weight Type", default=False, )
    hair_root_tip_weight = FloatProperty(name="Root-Tip Weight", default=50.0, min=1.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    hair_root_tip_weight_map = StringProperty(name="Root-Tip Weight Map", default="", get=MaterialEditorCallbacks.ext_hair_root_tip_weight_map_get, set=MaterialEditorCallbacks.ext_hair_root_tip_weight_map_set, )
    hair_primary_highlight_strength = FloatProperty(name="Strength", default=40.0, min=1.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    hair_primary_highlight_spread = FloatProperty(name="Spread", default=36.0, min=1.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    hair_primary_highlight_tint = FloatVectorProperty(name="Tint", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, subtype='COLOR', )
    hair_secondary_highlight_strength = FloatProperty(name="Strength", default=40.0, min=1.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    hair_secondary_highlight_spread = FloatProperty(name="Spread", default=45.0, min=1.0, max=100.0, precision=1, subtype='PERCENTAGE', )
    hair_secondary_highlight_tint = FloatVectorProperty(name="Tint", default=(255 / 255, 255 / 255, 255 / 255), min=0.0, max=1.0, subtype='COLOR', )
    
    displacement = PointerProperty(name="Displacement", type=MaterialDisplacementProperties, )


class MaterialWizards(PropertyGroup):
    types = EnumProperty(name="Wizard", items=[('NONE', "Choose material wizard", ""), ('GREASY', "Greasy", ""), ('TEXTURED', "Textured", ""), ('VELVET', "Velvet", ""), ], default='NONE', )
    
    greasy_color = FloatVectorProperty(name="Color", default=(0.0008046585621626175, 0.0008046585621626175, 0.0008046585621626175), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    
    # # Plastic wizard is the same as Opaque extension..
    # plastic_shininess = FloatProperty(name="Shininess", default=30.0, min=0.0, max=100.0, precision=0, subtype='PERCENTAGE', )
    # plastic_roughness = FloatProperty(name="Roughness", default=0.0, min=0.0, max=100.0, precision=0, subtype='PERCENTAGE', )
    # plastic_color = FloatVectorProperty(name="Color", default=(0.07805659603547627, 0.12752978241224922, 0.26735808898200775), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    
    textured_diffuse = StringProperty(name="Diffuse Map", default="", subtype='FILE_PATH', )
    textured_specular = StringProperty(name="Specular Map", default="", subtype='FILE_PATH', )
    textured_bump = StringProperty(name="Bump Map", default="", subtype='FILE_PATH', )
    textured_bump_strength = FloatProperty(name="Bump Strength", default=20.0, min=0.0, max=200.0, precision=2, )
    textured_normal = StringProperty(name="Normal Map", default="", subtype='FILE_PATH', )
    textured_alpha = StringProperty(name="Alpha Map", default="", subtype='FILE_PATH', )
    
    velvet_color = FloatVectorProperty(name="Color", default=(0.05112205630307245, 0.010397803645369345, 0.10114516973592808), min=0.0, max=1.0, precision=2, subtype='COLOR', )


class MaterialProperties(PropertyGroup):
    def _get_material_preview_scenes(self, context):
        from . import system
        l = system.mxed_get_preview_scenes()
        return l
    
    embed = BoolProperty(name="Embed Into Scene", default=True, description="When enabled, material file (.MXM) will be embedded to scene, otherwise will be referenced", )
    mxm_file = StringProperty(name="MXM File", default="", subtype='FILE_PATH', description="Path to material (.MXM) file", )
    
    use = EnumProperty(name="Type", items=[('REFERENCE', "Reference", ""), ('CUSTOM', "Custom", ""), ('EMITTER', "Emitter", ""), ('AGS', "AGS", ""), ('OPAQUE', "Opaque", ""),
                                           ('TRANSPARENT', "Transparent", ""), ('METAL', "Metal", ""), ('TRANSLUCENT', "Translucent", ""), ('CARPAINT', "Carpaint", ""),
                                           ('HAIR', "Hair", ""), ], default='CUSTOM', )
    
    override_global_properties = BoolProperty(name="Override Global Properties In MXM", default=False, )
    
    global_override_map = StringProperty(name="Override Map", default="", )
    
    global_bump = FloatProperty(name="Global Bump", default=30.0, min=-2000.0, max=2000.0, precision=2, )
    global_bump_map_enabled = BoolProperty(name="Global Bump Map Enabled", default=False, )
    global_bump_map = StringProperty(name="Global Bump Map", default="", get=MaterialEditorCallbacks.global_bump_map_get, set=MaterialEditorCallbacks.global_bump_map_set, )
    global_bump_map_use_normal = BoolProperty(name="Global Bump Map Use Normal", default=False, )
    global_bump_normal = FloatProperty(name="Global Bump", default=100.0, min=-2000.0, max=2000.0, precision=2, )
    
    global_dispersion = BoolProperty(name="Dispersion", default=False, )
    global_shadow = BoolProperty(name="Shadow", default=False, )
    global_matte = BoolProperty(name="Matte", default=False, )
    global_priority = IntProperty(name="Nested Priority", default=0, min=0, max=1000, )
    global_id = FloatVectorProperty(name="Material Id", default=(0.0, 0.0, 0.0), min=0.0, max=1.0, subtype='COLOR', )
    
    force_preview = BoolProperty(name="Force Preview", default=True, description="Force preview rendering when opened in Mxed", )
    force_preview_scene = EnumProperty(name="Force Preview Scene", items=_get_material_preview_scenes, description="Force preview Mxed scene", )
    
    custom_layers = PointerProperty(name="Custom Layers", type=MaterialCustomLayers, )
    custom_displacement = PointerProperty(name="Displacement", type=MaterialDisplacementProperties, )
    active_display_map = StringProperty(name="Active Display Map", description="Set texture displayed in Studio viewport", default="", )
    custom_open_in_mxed_after_save = BoolProperty(name="Open In Mxed", default=True, description="Open in Mxed after save", )
    
    extension = PointerProperty(name="Extension", type=ExtMaterialProperties, )
    wizards = PointerProperty(name="Material Wizards", type=MaterialWizards, )
    
    preview_scene = EnumProperty(name="Preview Scene", items=_get_material_preview_scenes, )
    preview_size = EnumProperty(name="Size", items=[('50', "25%", ""), ('100', "50%", ""), ('200', "100%", ""), ('305', "150%", ""), ], default='200', )
    preview_flag = BoolProperty(name="Update", default=False, options={'SKIP_SAVE'}, )
    
    @classmethod
    def register(cls):
        bpy.types.Material.maxwell_render = PointerProperty(type=cls)
    
    @classmethod
    def unregister(cls):
        del bpy.types.Material.maxwell_render
