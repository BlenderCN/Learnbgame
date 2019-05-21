# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, Daniel Genrich
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
"""Main PBRTv3 extension class definition"""

# System libs
import os
import multiprocessing
import time
import threading
import subprocess
import sys
import array
import math
import mathutils

# Blender libs
import bpy, bgl, bl_ui
from bpy.app.handlers import persistent

# Framework libs
from ..extensions_framework import util as efutil

# Exporter libs
from .. import PBRTv3Addon
from ..export import get_output_filename, get_worldscale
from ..export.scene import SceneExporter
from ..export.volumes import SmokeCache
from ..outputs import PBRTv3Manager, LuxFilmDisplay
from ..outputs import PBRTv3Log
from ..outputs.pure_api import PBRTv3_VERSION
from ..outputs.luxcore_api import ToValidPBRTv3CoreName
from ..outputs.luxcore_api import PYLUXCORE_AVAILABLE, UsePBRTv3Core, pyluxcore
from ..export.luxcore import PBRTv3CoreExporter
from ..export.luxcore.utils import get_elem_key

# Exporter Property Groups need to be imported to ensure initialisation
from ..properties import (
    accelerator, camera, engine, filter, integrator, ior_data, lamp, lampspectrum_data,
    material, node_material, node_inputs, node_texture, node_fresnel, node_converter, node_volume,
    mesh, object as prop_object, particles, rendermode, sampler, texture, world,
    luxcore_engine, luxcore_scene, luxcore_material, luxcore_lamp,
    luxcore_tile_highlighting, luxcore_imagepipeline, luxcore_translator, luxcore_rendering_controls, luxcore_global
)

# Exporter Interface Panels need to be imported to ensure initialisation
from ..ui import (
    render_panels, render_layers, camera, image, lamps, mesh, node_editor, object as ui_object, particles, world,
    imageeditor_panel
)

# Legacy material editor panels, node editor UI is initialized above
from ..ui.materials import (
    compositing, carpaint, cloth, glass, glass2, roughglass, glossytranslucent,
    glossycoating, glossy, layered, matte, mattetranslucent, metal, metal2, mirror, mix as mat_mix, null,
    scatter, shinymetal, velvet, main as mat_main
)

#Legacy texture editor panels
from ..ui.textures import (
    main as tex_main, abbe, add, band, blender, bilerp, blackbody, brick, cauchy, constant, colordepth,
    checkerboard, cloud, densitygrid, dots, equalenergy, exponential, fbm, fresnelcolor, fresnelname, gaussian,
    harlequin, hitpointcolor, hitpointalpha, hitpointgrey, imagemap, imagesampling, normalmap,
    lampspectrum, luxpop, marble, mix as tex_mix, multimix, sellmeier, scale, subtract, sopra, uv,
    uvmask, windy, wrinkled, mapping, tabulateddata, transform, pointiness, hsv
)

# Exporter Operators need to be imported to ensure initialisation
from .. import operators
from ..operators import lrmdb, export, materials, nodes, cycles_converter

def _register_elm(elm, required=False):
    try:
        elm.COMPAT_ENGINES.add('PBRTv3_RENDER')
    except:
        if required:
            PBRTv3Log('Failed to add PBRTv3 to ' + elm.__name__)

# Add standard Blender Interface elements
_register_elm(bl_ui.properties_render.RENDER_PT_render, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_dimensions, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_output, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_stamp)
_register_elm(bl_ui.properties_data_camera.DATA_PT_lens, required=True)
_register_elm(bl_ui.properties_data_camera.DATA_PT_camera, required=True)
_register_elm(bl_ui.properties_data_camera.DATA_PT_camera_display, required=True)
_register_elm(bl_ui.properties_data_camera.DATA_PT_camera_safe_areas, required=True)
#_register_elm(bl_ui.properties_data_camera.DATA_PT_custom_props_camera) # do we need these ?

#_register_elm(bl_ui.properties_render_layer.RENDERLAYER_PT_views) # multiview

_register_elm(bl_ui.properties_scene.SCENE_PT_scene, required=True)
_register_elm(bl_ui.properties_scene.SCENE_PT_audio)
_register_elm(bl_ui.properties_scene.SCENE_PT_physics)  # This is the gravity panel
_register_elm(bl_ui.properties_scene.SCENE_PT_keying_sets)
_register_elm(bl_ui.properties_scene.SCENE_PT_keying_set_paths)
_register_elm(bl_ui.properties_scene.SCENE_PT_unit)
_register_elm(bl_ui.properties_scene.SCENE_PT_color_management)
_register_elm(bl_ui.properties_scene.SCENE_PT_simplify)

_register_elm(bl_ui.properties_scene.SCENE_PT_rigid_body_world)
_register_elm(bl_ui.properties_scene.SCENE_PT_rigid_body_cache)
_register_elm(bl_ui.properties_scene.SCENE_PT_rigid_body_field_weights)

_register_elm(bl_ui.properties_scene.SCENE_PT_custom_props)

_register_elm(bl_ui.properties_world.WORLD_PT_context_world, required=True)

_register_elm(bl_ui.properties_material.MATERIAL_PT_preview)
_register_elm(bl_ui.properties_texture.TEXTURE_PT_preview)

_register_elm(bl_ui.properties_data_lamp.DATA_PT_context_lamp)

if bpy.app.version > (2, 77, 2):

    blender_psys_list = [
        # Common
        bl_ui.properties_physics_common.PHYSICS_PT_add,
        # Dynamic paint
        bl_ui.properties_physics_dynamicpaint.PHYSICS_PT_dynamic_paint,
        bl_ui.properties_physics_dynamicpaint.PHYSICS_PT_dp_advanced_canvas,
        bl_ui.properties_physics_dynamicpaint.PHYSICS_PT_dp_canvas_output,
        bl_ui.properties_physics_dynamicpaint.PHYSICS_PT_dp_canvas_initial_color,
        bl_ui.properties_physics_dynamicpaint.PHYSICS_PT_dp_effects,
        bl_ui.properties_physics_dynamicpaint.PHYSICS_PT_dp_cache,
        bl_ui.properties_physics_dynamicpaint.PHYSICS_PT_dp_brush_source,
        bl_ui.properties_physics_dynamicpaint.PHYSICS_PT_dp_brush_velocity,
        bl_ui.properties_physics_dynamicpaint.PHYSICS_PT_dp_brush_wave,
        # Forcefields
        bl_ui.properties_physics_field.PHYSICS_PT_field,
        # Collisions
        bl_ui.properties_physics_field.PHYSICS_PT_collision,
        # Fluid
        bl_ui.properties_physics_fluid.PHYSICS_PT_fluid,
        bl_ui.properties_physics_fluid.PHYSICS_PT_domain_gravity,
        bl_ui.properties_physics_fluid.PHYSICS_PT_domain_boundary,
        bl_ui.properties_physics_fluid.PHYSICS_PT_domain_particles,
        # Rigidbody
        bl_ui.properties_physics_rigidbody.PHYSICS_PT_rigid_body,
        bl_ui.properties_physics_rigidbody.PHYSICS_PT_rigid_body_dynamics,
        bl_ui.properties_physics_rigidbody.PHYSICS_PT_rigid_body_collisions,
        # Rigidbody constraints
        bl_ui.properties_physics_rigidbody_constraint.PHYSICS_PT_rigid_body_constraint,
        # Softbody
        bl_ui.properties_physics_softbody.PHYSICS_PT_softbody,
        bl_ui.properties_physics_softbody.PHYSICS_PT_softbody_cache,
        bl_ui.properties_physics_softbody.PHYSICS_PT_softbody_goal,
        bl_ui.properties_physics_softbody.PHYSICS_PT_softbody_edge,
        bl_ui.properties_physics_softbody.PHYSICS_PT_softbody_collision,
        bl_ui.properties_physics_softbody.PHYSICS_PT_softbody_solver,
        bl_ui.properties_physics_softbody.PHYSICS_PT_softbody_field_weights,
        # Cloth
        bl_ui.properties_physics_cloth.PHYSICS_PT_cloth,
        bl_ui.properties_physics_cloth.PHYSICS_PT_cloth_cache,
        bl_ui.properties_physics_cloth.PHYSICS_PT_cloth_collision,
        bl_ui.properties_physics_cloth.PHYSICS_PT_cloth_stiffness,
        bl_ui.properties_physics_cloth.PHYSICS_PT_cloth_sewing,
        bl_ui.properties_physics_cloth.PHYSICS_PT_cloth_field_weights,
        # Smoke
        bl_ui.properties_physics_smoke.PHYSICS_PT_smoke,
        bl_ui.properties_physics_smoke.PHYSICS_PT_smoke_groups,
        bl_ui.properties_physics_smoke.PHYSICS_PT_smoke_cache,
        bl_ui.properties_physics_smoke.PHYSICS_PT_smoke_highres,
        bl_ui.properties_physics_smoke.PHYSICS_PT_smoke_field_weights
    ]

    for blender_psys in blender_psys_list:
        _register_elm(blender_psys)

# Some additions to Blender panels for better allocation in context
# Use this example for such overrides
# Add output format flags to output panel
def lux_output_hints(self, context):
    if context.scene.render.engine == 'PBRTv3_RENDER' and not UsePBRTv3Core():

        # In this mode, we don't use use the regular interval write
        pipe_mode = (context.scene.pbrtv3_engine.export_type == 'INT' and
                     not context.scene.pbrtv3_engine.write_files)

        # in this case, none of these buttons do anything, so don't even bother drawing the label
        if not pipe_mode:
            col = self.layout.column()
            col.label("PBRTv3 Output Formats")
        row = self.layout.row()
        if not pipe_mode:
            row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "write_png", text="PNG")

            if context.scene.camera.data.pbrtv3_camera.pbrtv3_film.write_png:
                row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "write_png_16bit",
                         text="Use 16bit PNG")

            row = self.layout.row()
            row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "write_tga", text="TARGA")
            row = self.layout.row()
            row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "write_exr", text="OpenEXR")

            if context.scene.camera.data.pbrtv3_camera.pbrtv3_film.write_exr:
                row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "write_exr_applyimaging",
                         text="Tonemap EXR")
                row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "write_exr_halftype",
                         text="Use 16bit EXR")
                row = self.layout.row()
                row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "write_exr_compressiontype",
                         text="EXR Compression")

            if context.scene.camera.data.pbrtv3_camera.pbrtv3_film.write_tga or \
                    context.scene.camera.data.pbrtv3_camera.pbrtv3_film.write_exr:
                row = self.layout.row()
                row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "write_zbuf",
                         text="Enable Z-Buffer")

                if context.scene.camera.data.pbrtv3_camera.pbrtv3_film.write_zbuf:
                    row = self.layout.row()
                    row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "zbuf_normalization",
                             text="Z-Buffer Normalization")

            row = self.layout.row()
            row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "write_flm", text="Write FLM")

            if context.scene.camera.data.pbrtv3_camera.pbrtv3_film.write_flm:
                row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "restart_flm", text="Restart FLM")
                row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "write_flm_direct",
                         text="Write FLM Directly")
        row = self.layout.row()

        # Integrated imaging always with premul named according to Blender usage
        row.prop(context.scene.camera.data.pbrtv3_camera.pbrtv3_film, "output_alpha",
                 text="Transparent Background")


_register_elm(bl_ui.properties_render.RENDER_PT_output.append(lux_output_hints))


# Add view buttons for viewcontrol to preview panels
def lux_use_alternate_matview(self, context):
    if context.scene.render.engine == 'PBRTv3_RENDER':
        row = self.layout.row()

        if not UsePBRTv3Core():
            row.prop(context.scene.pbrtv3_world, "preview_object_size", text="Size")

        row.prop(context.material.pbrtv3_material, "preview_zoom", text="Zoom")

        if context.material.preview_render_type == 'FLAT' and not UsePBRTv3Core():
            row.prop(context.material.pbrtv3_material, "mat_preview_flip_xz", text="Flip XZ")


_register_elm(bl_ui.properties_material.MATERIAL_PT_preview.append(lux_use_alternate_matview))


def lux_use_alternate_texview(self, context):
    if context.scene.render.engine == 'PBRTv3_RENDER':
        row = self.layout.row()

        if not UsePBRTv3Core():
            row.prop(context.scene.pbrtv3_world, "preview_object_size", text="Size")

        if context.material:
            row.prop(context.material.pbrtv3_material, "preview_zoom", text="Zoom")

            if context.material.preview_render_type == 'FLAT' and not UsePBRTv3Core():
                row.prop(context.material.pbrtv3_material, "mat_preview_flip_xz", text="Flip XZ")


_register_elm(bl_ui.properties_texture.TEXTURE_PT_preview.append(lux_use_alternate_texview))


# Add use_clipping button to lens panel
def lux_use_clipping(self, context):
    if context.scene.render.engine == 'PBRTv3_RENDER':
        split = self.layout.split()
        split.label("")
        split.column().prop(context.camera.pbrtv3_camera, "use_clipping", text="Export Clipping")


_register_elm(bl_ui.properties_data_camera.DATA_PT_lens.append(lux_use_clipping))


# Add options by render image/anim buttons
def render_start_options(self, context):
    if context.scene.render.engine == 'PBRTv3_RENDER':
        col = self.layout.column()
        row = self.layout.row()

        if UsePBRTv3Core() and context.scene.render.display_mode == 'WINDOW':
            col.label("Window mode can cause crashes!", icon="ERROR")

        col.prop(context.scene.pbrtv3_engine, "selected_pbrtv3_api", text="PBRTv3 API")

        if UsePBRTv3Core():
            col.prop(context.scene.luxcore_translatorsettings, "export_type")
            if context.scene.luxcore_translatorsettings.export_type == "luxcoreui":
                sub = col.row()
                sub.alignment = 'RIGHT'
                sub.prop(context.scene.luxcore_translatorsettings, "run_luxcoreui")
        else:
            col.prop(context.scene.pbrtv3_engine, "export_type", text="Export Type")
            if context.scene.pbrtv3_engine.export_type == 'EXT':
                col.prop(context.scene.pbrtv3_engine, "binary_name", text="Render Using")
            if context.scene.pbrtv3_engine.export_type == 'INT':
                row.prop(context.scene.pbrtv3_engine, "write_files", text="Write to Disk")
                row.prop(context.scene.pbrtv3_engine, "integratedimaging", text="Integrated Imaging")

        col.separator()
        row = col.row()
        split = row.split(percentage=0.9, align=True)
        split.operator("luxrender.convert_cycles_scene", icon='EXPORT')
        # Usability design is crap, but it has to do for now
        split.prop(context.scene.luxcore_global, 'cycles_converter_fallback_color', text='')


_register_elm(bl_ui.properties_render.RENDER_PT_render.append(render_start_options))


# Add standard Blender elements for legacy texture editor
@classmethod
def blender_texture_poll(cls, context):
    tex = context.texture
    show = tex and ((tex.type == cls.tex_type and not tex.use_nodes) and
                    (context.scene.render.engine in cls.COMPAT_ENGINES))

    if context.scene.render.engine == 'PBRTv3_RENDER':
        show = show and tex.pbrtv3_texture.type == 'BLENDER'

    return show


_register_elm(bl_ui.properties_texture.TEXTURE_PT_context_texture)
blender_texture_ui_list = [
    bl_ui.properties_texture.TEXTURE_PT_blend,
    bl_ui.properties_texture.TEXTURE_PT_clouds,
    bl_ui.properties_texture.TEXTURE_PT_distortednoise,
    bl_ui.properties_texture.TEXTURE_PT_image,
    bl_ui.properties_texture.TEXTURE_PT_magic,
    bl_ui.properties_texture.TEXTURE_PT_marble,
    bl_ui.properties_texture.TEXTURE_PT_musgrave,
    bl_ui.properties_texture.TEXTURE_PT_stucci,
    bl_ui.properties_texture.TEXTURE_PT_voronoi,
    bl_ui.properties_texture.TEXTURE_PT_wood,
    bl_ui.properties_texture.TEXTURE_PT_ocean,
]

# Particle texture influence panel
@classmethod
def blender_psys_poll(cls, context):
    psys = context.particle_system
    tex = context.texture
    brush = context.brush
    show = tex and not brush and (context.scene.render.engine in cls.COMPAT_ENGINES)

    if context.scene.render.engine == 'PBRTv3_RENDER':
        show = show and psys

    return show

blender_psys_ui_list = [
    bl_ui.properties_texture.TEXTURE_PT_influence,
]

for blender_psys_ui in blender_psys_ui_list:
    _register_elm(blender_psys_ui)
    blender_psys_ui.poll = blender_psys_poll


def lux_texture_chooser(self, context):
    if context.scene.render.engine == 'PBRTv3_RENDER':
        self.layout.separator()
        row = self.layout.row(align=True)
        if context.texture:
            row.label('PBRTv3 type')
            row.menu('TEXTURE_MT_pbrtv3_type', text=context.texture.pbrtv3_texture.type_label)

            if UsePBRTv3Core():
                self.layout.separator()
                self.layout.prop(context.texture, 'use_color_ramp', text='Use Color Ramp')
                if context.texture.use_color_ramp:
                    self.layout.template_color_ramp(context.texture, 'color_ramp', expand=True)

                    # The first element has a default alpha of 0, which makes no sense for PBRTv3 - set it to 1
                    first_color = context.texture.color_ramp.elements[0].color
                    if first_color[3] < 1:
                        first_color[3] = 1

_register_elm(bl_ui.properties_texture.TEXTURE_PT_context_texture.append(lux_texture_chooser))

for blender_texture_ui in blender_texture_ui_list:
    _register_elm(blender_texture_ui)
    blender_texture_ui.poll = blender_texture_poll


# compatible() copied from blender repository (netrender)
def compatible(mod):
    mod = getattr(bl_ui, mod)
    for subclass in mod.__dict__.values():
        _register_elm(subclass)
    del mod


compatible("properties_data_mesh")
#compatible("properties_data_camera") # we register only needed  panels now
compatible("properties_particle")
compatible("properties_data_speaker")

# To draw the preview pause button
def DrawButtonPause(self, context):
    scene = context.scene

    if scene.render.engine == "PBRTv3_RENDER" and UsePBRTv3Core():
        view = context.space_data

        if view.viewport_shade == "RENDERED":
            self.layout.prop(scene.luxcore_rendering_controls, "pause_viewport_render", icon="PAUSE", text="")

_register_elm(bpy.types.VIEW3D_HT_header.append(DrawButtonPause))


def draw_button_show_imagemap_previews(self, context):
    if context.scene.render.engine == "PBRTv3_RENDER" and UsePBRTv3Core():
        self.layout.prop(context.scene.luxcore_global, 'nodeeditor_show_imagemap_previews',
                         toggle=True,
                         icon='IMAGE_COL')

_register_elm(bpy.types.NODE_HT_header.append(draw_button_show_imagemap_previews))


@PBRTv3Addon.addon_register_class
class RENDERENGINE_luxrender(bpy.types.RenderEngine):
    """
    PBRTv3 Engine Exporter/Integration class
    """

    bl_idname = 'PBRTv3_RENDER'
    bl_label = 'PBRTv3'
    bl_use_preview = True
    bl_use_texture_preview = True

    render_lock = threading.Lock()



    def render(self, scene):
        """
        scene:  bpy.types.Scene

        Export the given scene to PBRTv3.
        Choose from one of several methods depending on what needs to be rendered.

        Returns None
        """

        with RENDERENGINE_luxrender.render_lock:  # just render one thing at a time
            if scene is None:
                PBRTv3Log('ERROR: Scene to render is not valid')
                return

            if UsePBRTv3Core():
                self.luxcore_render(scene)
            else:
                self.pbrtv3_render(scene)

    def view_update(self, context):
        if UsePBRTv3Core():
            self.luxcore_view_update(context)
        else:
            self.update_stats('ERROR: Viewport rendering is only available when PBRTv3Core API is selected!', '')

    def view_draw(self, context):
        if UsePBRTv3Core():
            self.luxcore_view_draw(context)

    ############################################################################
    #
    # PBRTv3 classic API
    #
    ############################################################################

    def pbrtv3_render(self, scene):
        prev_cwd = os.getcwd()
        try:
            self.PBRTv3Manager = None
            self.render_update_timer = None
            self.output_dir = efutil.temp_directory()
            self.output_file = 'default.png'

            if scene.name == 'preview':
                self.pbrtv3_render_preview(scene)
                return

            if scene.display_settings.display_device != "sRGB":
                PBRTv3Log('WARNING: Colour Management not set to sRGB, render results may look too dark.')

            api_type, write_files = self.set_export_path(scene)

            os.chdir(efutil.export_path)

            is_animation = hasattr(self, 'is_animation') and self.is_animation
            make_queue = scene.pbrtv3_engine.export_type == 'EXT' and \
                         scene.pbrtv3_engine.binary_name == 'luxrender' and write_files

            if is_animation and make_queue:
                queue_file = efutil.export_path + '%s.%s.lxq' % (
                    efutil.scene_filename(), bpy.path.clean_name(scene.name))

                # Open/reset a queue file
                if scene.frame_current == scene.frame_start:
                    open(queue_file, 'w').close()

                if hasattr(self, 'update_progress'):
                    fr = scene.frame_end - scene.frame_start
                    fo = scene.frame_current - scene.frame_start
                    self.update_progress(fo / fr)

            exported_file = self.export_scene(scene)
            if not exported_file:
                return  # Export frame failed, abort rendering

            if is_animation and make_queue:
                self.PBRTv3Manager = PBRTv3Manager.GetActive()
                self.PBRTv3Manager.lux_context.worldEnd()
                with open(queue_file, 'a') as qf:
                    qf.write("%s\n" % exported_file)

                if scene.frame_current == scene.frame_end:
                    # run the queue
                    self.render_queue(scene, queue_file)
            else:
                self.render_start(scene)

        except Exception as err:
            PBRTv3Log('%s' % err)
            self.report({'ERROR'}, '%s' % err)

        os.chdir(prev_cwd)

    def pbrtv3_render_preview(self, scene):
        if sys.platform == 'darwin':
            self.output_dir = efutil.filesystem_path(bpy.app.tempdir)
        else:
            self.output_dir = efutil.temp_directory()

        if self.output_dir[-1] != '/':
            self.output_dir += '/'

        efutil.export_path = self.output_dir

        from ..outputs.pure_api import PYLUX_AVAILABLE

        if not PYLUX_AVAILABLE:
            PBRTv3Log('ERROR: Material previews require pylux')
            return

        from ..export import materials as export_materials

        # Iterate through the preview scene, finding objects with materials attached
        objects_mats = {}
        for obj in [ob for ob in scene.objects if ob.is_visible(scene) and not ob.hide_render]:
            for mat in export_materials.get_instance_materials(obj):
                if mat is not None:
                    if not obj.name in objects_mats.keys():
                        objects_mats[obj] = []
                    objects_mats[obj].append(mat)

        preview_type = None  # 'MATERIAL' or 'TEXTURE'

        # find objects that are likely to be the preview objects
        preview_objects = [o for o in objects_mats.keys() if o.name.startswith('preview')]
        if len(preview_objects) > 0:
            preview_type = 'MATERIAL'
        else:
            preview_objects = [o for o in objects_mats.keys() if o.name.startswith('texture')]
            if len(preview_objects) > 0:
                preview_type = 'TEXTURE'

        if preview_type is None:
            return

        # Find the materials attached to the likely preview object
        likely_materials = objects_mats[preview_objects[0]]
        if len(likely_materials) < 1:
            print('no preview materials')
            return

        pm = likely_materials[0]
        pt = None
        PBRTv3Log('Rendering material preview: %s' % pm.name)

        if preview_type == 'TEXTURE':
            pt = pm.active_texture

        LM = PBRTv3Manager(
            scene.name,
            api_type='API',
        )
        PBRTv3Manager.SetCurrentScene(scene)
        PBRTv3Manager.SetActive(LM)

        file_based_preview = False

        if file_based_preview:
            # Dump to file in temp dir for debugging
            from ..outputs.file_api import Custom_Context as lxs_writer

            preview_context = lxs_writer(scene.name)
            preview_context.set_filename(scene, 'luxblend25-preview', LXV=False)
            LM.lux_context = preview_context
        else:
            preview_context = LM.lux_context
            preview_context.logVerbosity('quiet')

        try:
            export_materials.ExportedMaterials.clear()
            export_materials.ExportedTextures.clear()

            from ..export import preview_scene

            xres, yres = scene.camera.data.pbrtv3_camera.pbrtv3_film.resolution(scene)

            # Don't render the tiny images
            if xres <= 96:
                raise Exception('Skipping material thumbnail update, image too small (%ix%i)' % (xres, yres))

            preview_scene.preview_scene(scene, preview_context, obj=preview_objects[0], mat=pm, tex=pt)

            # render !
            preview_context.worldEnd()

            if file_based_preview:
                preview_context = preview_context.parse('luxblend25-preview.lxs', True)
                LM.lux_context = preview_context

            while not preview_context.statistics('sceneIsReady'):
                time.sleep(0.05)

            def is_finished(ctx):
                return ctx.getAttribute('film', 'enoughSamples')

            def interruptible_sleep(sec, increment=0.05):
                sec_elapsed = 0.0
                while not self.test_break() and sec_elapsed <= sec:
                    sec_elapsed += increment
                    time.sleep(increment)

            for i in range(multiprocessing.cpu_count() - 2):
                # -2 since 1 thread already created and leave 1 spare
                if is_finished(preview_context):
                    break
                preview_context.addThread()

            while not is_finished(preview_context):
                if self.test_break() or bpy.context.scene.render.engine != 'PBRTv3_RENDER':
                    raise Exception('Render interrupted')

                # progressively update the preview
                time.sleep(0.2)  # safety-sleep

                if preview_context.getAttribute('renderer_statistics', 'samplesPerPixel') > 6:
                    if preview_type == 'TEXTURE':
                        interruptible_sleep(0.8)  # reduce update to every 1.0 sec until haltthreshold kills the render
                    else:
                        interruptible_sleep(1.8)  # reduce update to every 2.0 sec until haltthreshold kills the render

                preview_context.updateStatisticsWindow()
                PBRTv3Log('Updating preview (%ix%i - %s)' % (xres, yres,
                        preview_context.getAttribute('renderer_statistics_formatted_short', '_recommended_string')))

                result = self.begin_result(0, 0, xres, yres)

                if hasattr(preview_context, 'blenderCombinedDepthBuffers'):
                    # use fast buffers
                    pb, zb = preview_context.blenderCombinedDepthBuffers()
                    result.layers.foreach_set("rect", pb) if bpy.app.version < (2, 74, 4 ) \
                        else result.layers[0].passes.foreach_set("rect", pb)
                else:
                    lay = result.layers[0] if bpy.app.version < (2, 74, 4 ) else result.layers[0].passes[0]
                    lay.rect = preview_context.blenderCombinedDepthRects()[0]

                # Cycles tiles adaption
                self.end_result(result, 0) if bpy.app.version > (2, 63, 17 ) else self.end_result(result)
        except Exception as exc:
            PBRTv3Log('Preview aborted: %s' % exc)
            import traceback
            traceback.print_exc()

        preview_context.exit()
        preview_context.wait()

        # cleanup() destroys the pylux Context
        preview_context.cleanup()

        LM.reset()

    def set_export_path(self, scene):
        # replace /tmp/ with the real %temp% folder on Windows
        # OSX also has a special temp location that we should use
        fp = scene.render.filepath
        output_path_split = list(os.path.split(fp))

        if sys.platform in ('win32', 'darwin') and output_path_split[0] == '/tmp':
            output_path_split[0] = efutil.temp_directory()
            fp = '/'.join(output_path_split)

        scene_path = efutil.filesystem_path(fp)

        if os.path.isdir(scene_path):
            self.output_dir = scene_path
        else:
            self.output_dir = os.path.dirname(scene_path)

        if self.output_dir[-1] not in ('/', '\\'):
            self.output_dir += '/'

        if scene.pbrtv3_engine.export_type == 'INT':
            write_files = scene.pbrtv3_engine.write_files
            if write_files:
                api_type = 'FILE'
            else:
                api_type = 'API'
                if sys.platform == 'darwin':
                    self.output_dir = efutil.filesystem_path(bpy.app.tempdir)
                else:
                    self.output_dir = efutil.temp_directory()
        else:
            api_type = 'FILE'
            write_files = True

        efutil.export_path = self.output_dir

        return api_type, write_files

    def export_scene(self, scene):
        api_type, write_files = self.set_export_path(scene)

        # Pre-allocate the PBRTv3Manager so that we can set up the network servers before export
        LM = PBRTv3Manager(
            scene.name,
            api_type=api_type,
        )
        PBRTv3Manager.SetActive(LM)

        if scene.pbrtv3_engine.export_type == 'INT':
            # Set up networking before export so that we get better server usage
            if scene.pbrtv3_networking.use_network_servers and scene.pbrtv3_networking.servers:
                LM.lux_context.setNetworkServerUpdateInterval(scene.pbrtv3_networking.serverinterval)
                for server in scene.pbrtv3_networking.servers.split(','):
                    LM.lux_context.addServer(server.strip())

        output_filename = get_output_filename(scene)

        scene_exporter = SceneExporter()
        scene_exporter.properties.directory = self.output_dir
        scene_exporter.properties.filename = output_filename
        scene_exporter.properties.api_type = api_type  # Set export target
        scene_exporter.properties.write_files = write_files  # Use file write decision from above
        scene_exporter.properties.write_all_files = False  # Use UI file write settings
        scene_exporter.set_scene(scene)

        export_result = scene_exporter.export()

        if 'CANCELLED' in export_result:
            return False

        # Look for an output image to load
        if scene.camera.data.pbrtv3_camera.pbrtv3_film.write_png:
            self.output_file = efutil.path_relative_to_export(
                '%s/%s.png' % (self.output_dir, output_filename)
            )
        elif scene.camera.data.pbrtv3_camera.pbrtv3_film.write_tga:
            self.output_file = efutil.path_relative_to_export(
                '%s/%s.tga' % (self.output_dir, output_filename)
            )
        elif scene.camera.data.pbrtv3_camera.pbrtv3_film.write_exr:
            self.output_file = efutil.path_relative_to_export(
                '%s/%s.exr' % (self.output_dir, output_filename)
            )

        return "%s.PBRTv3s" % output_filename

    def rendering_behaviour(self, scene):
        internal = (scene.pbrtv3_engine.export_type in ['INT'])
        write_files = scene.pbrtv3_engine.write_files and (scene.pbrtv3_engine.export_type in ['INT', 'EXT'])
        render = scene.pbrtv3_engine.render

        # Handle various option combinations using simplified variable names !
        if internal:
            if write_files:
                if render:
                    start_rendering = True
                    parse = True
                    worldEnd = False
                else:
                    start_rendering = False
                    parse = False
                    worldEnd = False
            else:
                # will always render
                start_rendering = True
                parse = False
                worldEnd = True
        else:
            # external always writes files
            if render:
                start_rendering = True
                parse = False
                worldEnd = False
            else:
                start_rendering = False
                parse = False
                worldEnd = False

        return internal, start_rendering, parse, worldEnd

    def render_queue(self, scene, queue_file):
        internal, start_rendering, parse, worldEnd = self.rendering_behaviour(scene)

        if start_rendering:
            cmd_args = self.get_process_args(scene, start_rendering)

            cmd_args.extend(['-L', queue_file])

            PBRTv3Log('Launching Queue: %s' % cmd_args)
            # PBRTv3Log(' in %s' % self.outout_dir)
            pbrtv3_process = subprocess.Popen(cmd_args, cwd=self.output_dir)

    def append_lux_binary_name(self, scene, pbrtv3_path, binary_name):
        if sys.platform == 'darwin':
            # Get binary from OSX bundle
            pbrtv3_path += 'PBRTv3.app/Contents/MacOS/%s' % binary_name
            if not os.path.exists(pbrtv3_path):
                PBRTv3Log('PBRTv3 not found at path: %s' % pbrtv3_path, ', trying default PBRTv3 location')
                pbrtv3_path = '/Applications/PBRTv3/PBRTv3.app/Contents/MacOS/%s' % \
                                 binary_name  # try fallback to default installation path
        elif sys.platform == 'win32':
            pbrtv3_path += '%s.exe' % binary_name
        else:
            pbrtv3_path += binary_name

        return pbrtv3_path

    def get_lux_binary_path(self, scene, binary_name):
        pbrtv3_path = efutil.filesystem_path(efutil.find_config_value(
                              'luxrender', 'defaults', 'install_path', ''))

        print('pbrtv3_path: ', pbrtv3_path)

        if not pbrtv3_path:
            return ['']

        if pbrtv3_path[-1] != '/':
            pbrtv3_path += '/'

        pbrtv3_path = self.append_lux_binary_name(scene, pbrtv3_path, binary_name)

        if not os.path.exists(pbrtv3_path):
            raise Exception('PBRTv3 not found at path: %s' % pbrtv3_path)

        return pbrtv3_path

    def get_process_args(self, scene, start_rendering):
        config_updates = {
            'auto_start': start_rendering
        }

        pbrtv3_path = self.get_lux_binary_path(scene, scene.pbrtv3_engine.binary_name)

        cmd_args = [pbrtv3_path]

        # set log verbosity
        if scene.pbrtv3_engine.log_verbosity != 'default':
            cmd_args.append('--' + scene.pbrtv3_engine.log_verbosity)

        # Epsilon values if any
        if scene.pbrtv3_engine.binary_name != 'luxvr':
            if scene.pbrtv3_engine.min_epsilon:
                cmd_args.append('--minepsilon=%.8f' % scene.pbrtv3_engine.min_epsilon)
            if scene.pbrtv3_engine.max_epsilon:
                cmd_args.append('--maxepsilon=%.8f' % scene.pbrtv3_engine.max_epsilon)

        if scene.pbrtv3_engine.binary_name == 'luxrender':
            # Copy the GUI log to the console
            cmd_args.append('--logconsole')

        # Set number of threads for external processes
        if not scene.pbrtv3_engine.threads_auto:
            cmd_args.append('--threads=%i' % scene.pbrtv3_engine.threads)

        # Set fixed seeds, if enabled
        if scene.pbrtv3_engine.fixed_seed:
            cmd_args.append('--fixedseed')

        if scene.pbrtv3_networking.use_network_servers and scene.pbrtv3_networking.servers:
            for server in scene.pbrtv3_networking.servers.split(','):
                cmd_args.append('--useserver')
                cmd_args.append(server.strip())

            cmd_args.append('--serverinterval')
            cmd_args.append('%i' % scene.pbrtv3_networking.serverinterval)

            config_updates['servers'] = scene.pbrtv3_networking.servers
            config_updates['serverinterval'] = '%i' % scene.pbrtv3_networking.serverinterval

        config_updates['use_network_servers'] = scene.pbrtv3_networking.use_network_servers

        # Save changed config items and then launch Lux

        try:
            for k, v in config_updates.items():
                efutil.write_config_value('luxrender', 'defaults', k, v)
        except Exception as err:
            PBRTv3Log('WARNING: Saving PBRTv3 config failed, please set your user scripts dir: %s' % err)

        return cmd_args

    def render_start(self, scene):
        self.PBRTv3Manager = PBRTv3Manager.GetActive()

        # Remove previous rendering, to prevent loading old data
        # if the update timer fires before the image is written
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        internal, start_rendering, parse, worldEnd = self.rendering_behaviour(scene)

        if self.PBRTv3Manager.lux_context.API_TYPE == 'FILE':
            fn = self.PBRTv3Manager.lux_context.file_names[0]
            self.PBRTv3Manager.lux_context.worldEnd()
            if parse:
                # file_api.parse() creates a real pylux context. we must replace
                # PBRTv3Manager's context with that one so that the running renderer
                # can be controlled.
                ctx = self.PBRTv3Manager.lux_context.parse(fn, True)
                self.PBRTv3Manager.lux_context = ctx
                self.PBRTv3Manager.stats_thread.LocalStorage['lux_context'] = ctx
                self.PBRTv3Manager.fb_thread.LocalStorage['lux_context'] = ctx
        elif worldEnd:
            self.PBRTv3Manager.lux_context.worldEnd()

        # Begin rendering
        if start_rendering:
            PBRTv3Log('Starting PBRTv3')
            if internal:

                self.PBRTv3Manager.lux_context.logVerbosity(scene.pbrtv3_engine.log_verbosity)

                self.update_stats('', 'PBRTv3: Building %s' % scene.pbrtv3_accelerator.accelerator)
                self.PBRTv3Manager.start()

                self.PBRTv3Manager.fb_thread.LocalStorage['integratedimaging'] = scene.pbrtv3_engine.integratedimaging

                # Update the image from disk only as often as it is written
                self.PBRTv3Manager.fb_thread.set_kick_period(
                    scene.camera.data.pbrtv3_camera.pbrtv3_film.internal_updateinterval)

                # Start the stats and framebuffer threads and add additional threads to Lux renderer
                self.PBRTv3Manager.start_worker_threads(self)

                if scene.pbrtv3_engine.threads_auto:
                    try:
                        thread_count = multiprocessing.cpu_count()
                    except:
                        thread_count = 1
                else:
                    thread_count = scene.pbrtv3_engine.threads

                # Run rendering with specified number of threads
                for i in range(thread_count - 1):
                    self.PBRTv3Manager.lux_context.addThread()

                while self.PBRTv3Manager.started:
                    self.render_update_timer = threading.Timer(1, self.stats_timer)
                    self.render_update_timer.start()
                    if self.render_update_timer.isAlive():
                        self.render_update_timer.join()
            else:
                cmd_args = self.get_process_args(scene, start_rendering)

                cmd_args.append(fn.replace('//', '/'))

                PBRTv3Log('Launching: %s' % cmd_args)
                # PBRTv3Log(' in %s' % self.outout_dir)
                pbrtv3_process = subprocess.Popen(cmd_args, cwd=self.output_dir)

                if not (
                        scene.pbrtv3_engine.binary_name == 'luxrender' and not
                        scene.pbrtv3_engine.monitor_external):
                    framebuffer_thread = LuxFilmDisplay({
                        'resolution': scene.camera.data.pbrtv3_camera.pbrtv3_film.resolution(scene),
                        'RE': self,
                    })
                    framebuffer_thread.set_kick_period(scene.camera.data.pbrtv3_camera.pbrtv3_film.writeinterval)
                    framebuffer_thread.start()
                    while pbrtv3_process.poll() is None and not self.test_break():
                        self.render_update_timer = threading.Timer(1, self.process_wait_timer)
                        self.render_update_timer.start()
                        if self.render_update_timer.isAlive():
                            self.render_update_timer.join()

                    # If we exit the wait loop (user cancelled) and luxconsole is still running, then send SIGINT
                    if pbrtv3_process.poll() is None and scene.pbrtv3_engine.binary_name != 'luxrender':
                        # Use SIGTERM because that's the only one supported on Windows
                        pbrtv3_process.send_signal(subprocess.signal.SIGTERM)

                    # Stop updating the render result and load the final image
                    framebuffer_thread.stop()
                    framebuffer_thread.join()
                    framebuffer_thread.kick(render_end=True)

    def process_wait_timer(self):
        # Nothing to do here
        pass

    def stats_timer(self):
        """
        Update the displayed rendering statistics and detect end of rendering

        Returns None
        """

        LC = self.PBRTv3Manager.lux_context

        self.update_stats('', 'PBRTv3: Rendering %s' % self.PBRTv3Manager.stats_thread.stats_string)

        if hasattr(self, 'update_progress') and LC.getAttribute('renderer_statistics', 'percentComplete') > 0:
            prg = LC.getAttribute('renderer_statistics', 'percentComplete') / 100.0
            self.update_progress(prg)

        if self.test_break() or \
                        LC.statistics('filmIsReady') == 1.0 or \
                        LC.statistics('terminated') == 1.0 or \
                        LC.getAttribute('film', 'enoughSamples'):
            self.PBRTv3Manager.reset()
            self.update_stats('', '')

    ############################################################################
    #
    # PBRTv3Core code
    #
    ############################################################################

    def set_export_path_luxcore(self, scene):
        # replace /tmp/ with the real %temp% folder on Windows
        # OSX also has a special temp location that we should use
        fp = scene.render.filepath
        output_path_split = list(os.path.split(fp))

        if fp == '' or (sys.platform in ('win32', 'darwin') and output_path_split[0] == '/tmp'):
            output_path_split[0] = efutil.temp_directory()
            fp = '/'.join(output_path_split)

        scene_path = efutil.filesystem_path(fp)

        if os.path.isdir(scene_path):
            self.output_dir = scene_path
        else:
            self.output_dir = os.path.dirname(scene_path)

        if self.output_dir[-1] not in ('/', '\\'):
            self.output_dir += '/'

        efutil.export_path = self.output_dir

    mem_peak = 0

    def CreateBlenderStats(self, lcConfig, stats, scene, realtime_preview=False, time_until_update=-1, display_interval=-1,
                           export_errors=False):
        """
        Returns: string of formatted statistics
        """
        rendering_controls = scene.luxcore_rendering_controls

        engine = lcConfig.GetProperties().Get('renderengine.type').GetString()
        engine_dict = {
            'PATHCPU' : 'Path CPU',
            'PATHOCL' : 'Path OpenCL',
            'TILEPATHCPU' : 'Tile Path CPU',
            'TILEPATHOCL' : 'Tile Path OpenCL',
            'BIDIRCPU' : 'Bidir CPU',
            'BIDIRVMCPU' : 'BidirVCM CPU',
            'RTPATHOCL': 'RT Path OpenCL',
            'RTPATHCPU': 'RT Path CPU',
        }

        sampler = lcConfig.GetProperties().Get('sampler.type').GetString()
        sampler_dict = {
            'RANDOM' : 'Random',
            'SOBOL' : 'Sobol',
            'METROPOLIS' : 'Metropolis',
            'RTPATHCPUSAMPLER': 'RT Path Sampler',
            'TILEPATHSAMPLER': 'Tile Path Sampler'
        }

        settings = scene.luxcore_enginesettings
        halt_samples = settings.halt_samples_preview if realtime_preview else settings.halt_samples
        halt_time = settings.halt_time_preview if realtime_preview else settings.halt_time
        halt_noise = settings.halt_noise

        # Progress
        progress_time = 0.0
        progress_samples = 0.0
        progress_tiles = 0.0

        stats_list = []

        # Time stats
        time_running = stats.Get('stats.renderengine.time').GetFloat()
        # Add time stats for realtime preview because Blender doesn't display it there
        # For final renderings, only display time if it is set as halt condition
        # Don't show when engine is TILEPATH because it uses different halt conditions
        if (not realtime_preview and settings.use_halt_time) or (realtime_preview and settings.use_halt_time_preview):
            stats_list.append('Time: %.1fs/%ds' % (time_running, halt_time))
            if not realtime_preview:
                progress_time = time_running / halt_time

        # Samples/Passes stats
        if rendering_controls.stats_samples:
            samples_count = stats.Get('stats.renderengine.pass').GetInt()
            samples_term = 'Pass' if engine in ['TILEPATHCPU', 'TILEPATHOCL'] else 'Samples'

            # Do not show when engine is TILEPATH because it uses different halt conditions
            if ((not realtime_preview and settings.use_halt_samples) or (realtime_preview and settings.use_halt_samples_preview)) \
                    and engine not in ['TILEPATHCPU', 'TILEPATHOCL']:
                stats_list.append('%s: %d/%d' % (samples_term, samples_count, halt_samples))
                if not realtime_preview:
                    progress_samples = samples_count / halt_samples
            else:
                stats_list.append('%s: %d' % (samples_term, samples_count))

        # Tile stats
        if engine in ['TILEPATHCPU', 'TILEPATHOCL'] and rendering_controls.stats_tiles:
            converged = stats.Get('stats.tilepath.tiles.converged.count').GetInt()
            notconverged = stats.Get('stats.tilepath.tiles.notconverged.count').GetInt()
            pending = stats.Get('stats.tilepath.tiles.pending.count').GetInt()

            tiles_amount = converged + notconverged + pending
            stats_list.append('Tiles: %d/%d Converged' % (converged, tiles_amount))
            progress_tiles = converged / tiles_amount

        # Samples per second
        if rendering_controls.stats_samples_per_sec:
            samples_per_sec = stats.Get('stats.renderengine.total.samplesec').GetFloat()

            if samples_per_sec > 10**6 - 1:
                # Use megasamples as unit
                stats_list.append('Samples/Sec %.1f M' % (samples_per_sec / 10**6))
            else:
                # Use kilosamples as unit
                stats_list.append('Samples/Sec %d k' % (samples_per_sec / 10**3))

        if rendering_controls.stats_rays_per_sample:
            samplesec = stats.Get("stats.renderengine.total.samplesec").GetFloat()

            if samplesec > 0:
                rays_per_sample = stats.Get("stats.renderengine.performance.total").GetFloat() / samplesec
            else:
                rays_per_sample = 0

            stats_list.append('Rays/Sample %.1f' % rays_per_sample)

        # Convergence stats
        if rendering_controls.stats_convergence:
            convergence = stats.Get('stats.renderengine.convergence').GetFloat()
            # Flip convergence so 1.0 is not converged and 0.0 is fully converged, to be consistent with noise settings
            # in the UI (e.g. target noise level = 0.04)
            convergence = 1.0 - convergence

            if settings.use_halt_noise:
                stats_list.append('Noise Level: %f/%f' % (convergence, halt_noise))
            else:
                stats_list.append('Noise Level: %f' % convergence)

        # Memory usage (only available for OpenCL engines)
        if str.endswith(engine, 'OCL') and rendering_controls.stats_memory:
            device_stats = stats.Get("stats.renderengine.devices")

            max_memory = float('inf')
            used_memory = 0

            for i in range(device_stats.GetSize()):
                device_name = device_stats.GetString(i)

                # Max memory available is limited by the device with least amount of memory
                device_max_memory = stats.Get("stats.renderengine.devices." + device_name + ".memory.total").GetFloat()
                device_max_memory = int(device_max_memory / (1024 * 1024))
                if device_max_memory < max_memory:
                    max_memory = device_max_memory

                device_used_memory = stats.Get("stats.renderengine.devices." + device_name + ".memory.used").GetFloat()
                device_used_memory = int(device_used_memory / (1024 * 1024))
                if device_used_memory > used_memory:
                    used_memory = device_used_memory

            if used_memory > self.mem_peak:
                self.mem_peak = used_memory

            stats_list.append('Memory: %d MB/%d MB' % (used_memory, max_memory))

        # Show triangle count (formatted with commas, like so: 5,123,001 Tris)
        if rendering_controls.stats_tris:
            triangle_count = int(stats.Get("stats.dataset.trianglecount").GetFloat())
            stats_list.append('{:,} Tris'.format(triangle_count))

        # Engine and sampler info
        if rendering_controls.stats_engine_info:
            try:
                engine_info = engine_dict[engine]
                if not 'TILEPATH' in engine:
                    engine_info += ' + ' + sampler_dict[sampler]
            except KeyError:
                engine_info = 'Unkown engine or sampler'

            stats_list.append(engine_info)

        # Show remaining time until next film update (final render only)
        if scene.luxcore_rendering_controls.pause_render:
            stats_list.append('Rendering Paused')
        else:
            if not realtime_preview and time_until_update > 0:
                text = 'Next update in %ds ' % math.ceil(time_until_update)
                # Show a useless progress bar that looks something like this: (-----+--)
                bar_length = 15
                percent = math.ceil(time_until_update / display_interval * bar_length)
                l = ['-' for i in range(bar_length)]
                l[bar_length - percent] = '+'
                text += '(' + ''.join(l) + ')'
                stats_list.append(text)
            elif time_until_update != -1:
                stats_list.append('Updating preview...')

        # Inform the user when errors happened during export (e.g. failed to export a particle system)
        if export_errors:
            stats_list.append('Errors happened during export, open system console for details')

        # Update progressbar (final render only)
        if not realtime_preview:
            progress = max([progress_time, progress_samples, progress_tiles])
            self.update_progress(progress)

        # Pass memory usage information to Blender (only available when using OpenCL engines)
        if str.endswith(engine, 'OCL') and rendering_controls.stats_memory:
            self.update_memory_stats(used_memory, self.mem_peak)

        return ' | '.join(stats_list)

    def haltConditionMet(self, scene, stats, realtime_preview=False):
        """
        Checks if any halt conditions are met
        """
        settings = scene.luxcore_enginesettings

        use_halt_samples = settings.use_halt_samples_preview if realtime_preview else settings.use_halt_samples
        use_halt_time = settings.use_halt_time_preview if realtime_preview else settings.use_halt_time

        halt_samples = settings.halt_samples_preview if realtime_preview else settings.halt_samples
        halt_time = settings.halt_time_preview if realtime_preview else settings.halt_time
        halt_noise = settings.halt_noise

        rendered_samples = stats.Get('stats.renderengine.pass').GetInt()
        rendered_time = stats.Get('stats.renderengine.time').GetFloat()
        rendered_noise = stats.Get('stats.renderengine.convergence').GetFloat()

        halt_samples_met = use_halt_samples and rendered_samples >= halt_samples
        halt_time_met = use_halt_time and rendered_time >= halt_time

        if settings.use_halt_noise:
            halt_noise_met = rendered_noise > (1.0 - halt_noise)
        else:
            halt_noise_met = rendered_noise == 1.0

        # Samples make no sense as halt condition when TILEPATH is used
        if not realtime_preview and settings.renderengine_type == 'TILEPATH':
            return halt_noise_met or halt_time_met

        return halt_samples_met or halt_time_met or halt_noise_met or scene.luxcore_rendering_controls.pause_viewport_render

    def convertChannelToImage(self, lcSession, scene, passes, filmWidth, filmHeight, channelType, saveToDisk,
                              normalize = False, buffer_id = -1):
        """
        Convert AOVs to Blender images
        """
        from ..outputs.luxcore_api import pyluxcore

        # Structure: {channelType: [pyluxcoreType, is HDR, arrayDepth, optional matching Blender pass]}
        attributes = {
                'RGB': [pyluxcore.FilmOutputType.RGB, True, 3],
                'RGBA': [pyluxcore.FilmOutputType.RGBA, True, 4],
                'RGB_TONEMAPPED': [pyluxcore.FilmOutputType.RGB_TONEMAPPED, False, 3],
                'RGBA_TONEMAPPED': [pyluxcore.FilmOutputType.RGBA_TONEMAPPED, False, 4],
                'ALPHA': [pyluxcore.FilmOutputType.ALPHA, False, 1],
                'DEPTH': [pyluxcore.FilmOutputType.DEPTH, True, 1, 'Z'],
                'POSITION': [pyluxcore.FilmOutputType.POSITION, True, 3],
                'GEOMETRY_NORMAL': [pyluxcore.FilmOutputType.GEOMETRY_NORMAL, True, 3],
                'SHADING_NORMAL': [pyluxcore.FilmOutputType.SHADING_NORMAL, True, 3, 'NORMAL'],
                'MATERIAL_ID': [pyluxcore.FilmOutputType.MATERIAL_ID, False, 1],
                'OBJECT_ID': [pyluxcore.FilmOutputType.OBJECT_ID, False, 1],
                'DIRECT_DIFFUSE': [pyluxcore.FilmOutputType.DIRECT_DIFFUSE, True, 3, 'DIFFUSE_DIRECT'],
                'DIRECT_GLOSSY': [pyluxcore.FilmOutputType.DIRECT_GLOSSY, True, 3, 'GLOSSY_DIRECT'],
                'EMISSION': [pyluxcore.FilmOutputType.EMISSION, True, 3, 'EMIT'],
                'INDIRECT_DIFFUSE': [pyluxcore.FilmOutputType.INDIRECT_DIFFUSE, True, 3, 'DIFFUSE_INDIRECT'],
                'INDIRECT_GLOSSY': [pyluxcore.FilmOutputType.INDIRECT_GLOSSY, True, 3, 'GLOSSY_INDIRECT'],
                'INDIRECT_SPECULAR': [pyluxcore.FilmOutputType.INDIRECT_SPECULAR, True, 3, 'TRANSMISSION_INDIRECT'],
                'DIRECT_SHADOW_MASK': [pyluxcore.FilmOutputType.DIRECT_SHADOW_MASK, False, 1],
                'INDIRECT_SHADOW_MASK': [pyluxcore.FilmOutputType.INDIRECT_SHADOW_MASK, False, 1],
                'UV': [pyluxcore.FilmOutputType.UV, True, 2],
                'RAYCOUNT': [pyluxcore.FilmOutputType.RAYCOUNT, True, 1],
                'IRRADIANCE': [pyluxcore.FilmOutputType.IRRADIANCE, True, 3],
                'MATERIAL_ID_MASK': [pyluxcore.FilmOutputType.MATERIAL_ID_MASK, False, 1],
                'BY_MATERIAL_ID': [pyluxcore.FilmOutputType.BY_MATERIAL_ID, True, 3],
                'RADIANCE_GROUP': [pyluxcore.FilmOutputType.RADIANCE_GROUP, True, 3]
        }

        outputType = attributes[channelType][0]
        use_hdr = attributes[channelType][1]
        arrayType = 'I' if channelType in ('MATERIAL_ID', 'OBJECT_ID') else 'f'
        arrayInitValue = 0 if channelType in ('MATERIAL_ID', 'OBJECT_ID') else 0.0
        arrayDepth = attributes[channelType][2]
        pass_type = attributes[channelType][3] if len(attributes[channelType]) == 4 else None

        # show info about imported passes
        message = 'Pass: ' + channelType
        if buffer_id != -1:
            message += ' ID: ' + str(buffer_id)
        self.update_stats('Importing AOV passes into Blender...', message)
        PBRTv3Log('Importing AOV ' + message)

        # raw channel buffer
        channel_buffer = array.array(arrayType, [arrayInitValue] * (filmWidth * filmHeight * arrayDepth))

        # buffer for converted array (to RGBA)
        channel_buffer_converted = []

        if channelType in ('MATERIAL_ID', 'OBJECT_ID'):
            # MATERIAL_ID needs special treatment
            channel_buffer_converted = [None] * (filmWidth * filmHeight * 4)
            lcSession.GetFilm().GetOutputUInt(outputType, channel_buffer)

            mask_red = 0xff0000
            mask_green = 0xff00
            mask_blue = 0xff

            k = 0
            for i in range(0, len(channel_buffer)):
                rgba_raw = channel_buffer[i]

                rgba_converted = [
                    float((rgba_raw & mask_red) >> 16) / 255.0,
                    float((rgba_raw & mask_green) >> 8) / 255.0,
                    float(rgba_raw & mask_blue) / 255.0,
                    1.0
                ]

                channel_buffer_converted[k:k + 4] = rgba_converted
                k += 4
        else:
            if channelType in ['MATERIAL_ID_MASK', 'BY_MATERIAL_ID', 'RADIANCE_GROUP'] and buffer_id != -1:
                lcSession.GetFilm().GetOutputFloat(outputType, channel_buffer, buffer_id)
            else:
                lcSession.GetFilm().GetOutputFloat(outputType, channel_buffer)

            # Import into Blender passes
            if pass_type is not None and scene.pbrtv3_channels.import_compatible:
                nested_list = [channel_buffer[i:i+arrayDepth] for i in range(0, len(channel_buffer), arrayDepth)]

                for renderpass in passes:
                    if renderpass.type == pass_type:
                        renderpass.rect = nested_list
                        break
            else:
                # Pass is not compatible with Blender passes, import as Blender image
                # spread value to RGBA format
                if arrayDepth == 1:
                    channel_buffer_converted = pyluxcore.ConvertFilmChannelOutput_1xFloat_To_4xFloatList(filmWidth,
                                                                                                         filmHeight,
                                                                                                         channel_buffer,
                                                                                                         normalize)
                # UV channel, just add 0.0 for B and 1.0 for A components
                elif arrayDepth == 2:
                    channel_buffer_converted = pyluxcore.ConvertFilmChannelOutput_2xFloat_To_4xFloatList(filmWidth,
                                                                                                         filmHeight,
                                                                                                         channel_buffer,
                                                                                                         normalize)
                # RGB channels: just add 1.0 as alpha component
                elif arrayDepth == 3:
                    channel_buffer_converted = pyluxcore.ConvertFilmChannelOutput_3xFloat_To_4xFloatList(filmWidth,
                                                                                                         filmHeight,
                                                                                                         channel_buffer,
                                                                                                         normalize)
                # RGBA channels: just use the original list
                else:
                    channel_buffer_converted = channel_buffer

        if pass_type is None or not scene.pbrtv3_channels.import_compatible:
            # Pass is incompatible with Blender passes or import of compatible passes was disabled

            imageName = 'pass_' + str(channelType)
            if buffer_id != -1:
                imageName += '_' + str(buffer_id)

            if normalize:
                imageName += '_normalized'

            # remove pass image from Blender if it already exists (to prevent duplicates)
            for bl_image in bpy.data.images:
                if bl_image.name == imageName:
                    bl_image.user_clear()
                    if not bl_image.users:
                        bpy.data.images.remove(bl_image)

            if scene.render.use_border and not scene.render.use_crop_to_border:
                # border rendering without cropping: fit the rendered area into a blank image
                imageWidth, imageHeight = scene.camera.data.pbrtv3_camera.pbrtv3_film.resolution(scene)

                # construct an empty Blender image
                blenderImage = bpy.data.images.new(imageName, alpha = True,
                                                    width = imageWidth, height = imageHeight, float_buffer = use_hdr)

                # copy the buffer content to the correct position in the Blender image
                offsetFromLeft = int(imageWidth * scene.render.border_min_x) * 4
                offsetFromTop = int(imageHeight * scene.render.border_min_y)

                # we use an intermediate temp image because blenderImage.pixels doesn't support list slicing
                tempImage = [0.0] * (imageWidth * imageHeight * 4)

                for y in range(offsetFromTop, offsetFromTop + filmHeight):
                    imageSliceStart = y * imageWidth * 4 + offsetFromLeft
                    imageSliceEnd = imageSliceStart + filmWidth * 4
                    bufferSliceStart = (y - offsetFromTop) * filmWidth * 4
                    bufferSliceEnd = bufferSliceStart + filmWidth * 4

                    tempImage[imageSliceStart:imageSliceEnd] = channel_buffer_converted[bufferSliceStart:bufferSliceEnd]

                blenderImage.pixels = tempImage
            else:
                # no border rendering or border rendering with cropping: just copy the buffer to a Blender image
                blenderImage = bpy.data.images.new(imageName, alpha = False,
                                                    width = filmWidth, height = filmHeight, float_buffer = use_hdr)
                blenderImage.pixels = channel_buffer_converted

            # write image to file
            suffix = '.png'
            image_format = 'PNG'
            if use_hdr and not normalize:
                suffix = '.exr'
                image_format = 'OPEN_EXR'

            imageName = get_output_filename(scene) + '_' + imageName + suffix
            blenderImage.filepath_raw = self.output_dir + imageName
            blenderImage.file_format = image_format

    def draw_tiles(self, scene, stats, imageBuffer, filmWidth, filmHeight):
        """
        draws tile outlines directly into the imageBuffer

        scene: Blender scene object
        stats: PBRTv3Core stats (from PBRTv3Core session)
        imageBuffer: list of tuples of floats, e.g. [(r, g, b, a), ...], must be sliceable!
        """
        tile_size = scene.luxcore_enginesettings.tile_size
        show_converged = scene.luxcore_tile_highlighting.show_converged
        show_unconverged = scene.luxcore_tile_highlighting.show_unconverged
        show_pending = scene.luxcore_tile_highlighting.show_pending

        def draw_tile_type(count, coords, color):
            """
            draws all tiles at the given coordinates with given color
            """
            for i in range(count):
                offset_x = coords[i * 2]
                offset_y = coords[i * 2 + 1]
                width = min(tile_size + 1, filmWidth - offset_x)
                height = min(tile_size + 1, filmHeight - offset_y)

                draw_tile_outline(offset_x, offset_y, width, height, color)

        def draw_tile_outline(offset_x, offset_y, width, height, color):
            """
            draws the outline of one tile
            """
            for y in range(offset_y, offset_y + height):
                sliceStart = y * filmWidth + offset_x
                sliceEnd = sliceStart + width

                if y == offset_y or y == offset_y + height - 1:
                    # bottom and top lines
                    imageBuffer[sliceStart:sliceEnd] = [color] * width
                else:
                    # left and right sides
                    imageBuffer[sliceStart] = color
                    try:
                        imageBuffer[sliceEnd - 1] = color
                    except IndexError:
                        # catch this so render does not crash when we try to draw outside the imageBuffer
                        # (should not be possible anymore, but leave it in in case there's an unknown bug)
                        pass

        # collect stats
        count_converged = stats.Get('stats.tilepath.tiles.converged.count').GetInt()
        count_notconverged = stats.Get('stats.tilepath.tiles.notconverged.count').GetInt()
        count_pending = stats.Get('stats.tilepath.tiles.pending.count').GetInt()

        if count_converged > 0 and show_converged:
            coords_converged = stats.Get('stats.tilepath.tiles.converged.coords').GetInts()
            color_green = (0.0, 1.0, 0.0, 1.0)
            draw_tile_type(count_converged, coords_converged, color_green)

        if count_notconverged > 0 and show_unconverged:
            coords_notconverged = stats.Get('stats.tilepath.tiles.notconverged.coords').GetInts()
            color_red = (1.0, 0.0, 0.0, 1.0)
            draw_tile_type(count_notconverged, coords_notconverged, color_red)

        if count_pending > 0 and show_pending:
            coords_pending = stats.Get('stats.tilepath.tiles.pending.coords').GetInts()
            color_yellow = (1.0, 1.0, 0.0, 1.0)
            draw_tile_type(count_pending, coords_pending, color_yellow)

    transparent_film = False

    def luxcore_render(self, scene):
        if self.is_preview:
            self.luxcore_render_preview(scene)
            return

        # PBRTv3Core libs
        if not PYLUXCORE_AVAILABLE:
            PBRTv3Log('ERROR: PBRTv3Core rendering requires pyluxcore')
            self.report({'ERROR'}, 'PBRTv3Core rendering requires pyluxcore')
            return
        from ..outputs.luxcore_api import pyluxcore

        try:
            scene.luxcore_rendering_controls.pause_render = False

            if self.is_animation:
                # Check if a halt condition is set, cancel the rendering and warn the user otherwise
                settings = scene.luxcore_enginesettings

                if settings.renderengine_type == 'TILEPATH':
                    halt_enabled = (not settings.tile_multipass_enable
                                    or not settings.tile_multipass_use_threshold_reduction) or settings.use_halt_time
                else:
                    halt_enabled = settings.use_halt_samples or settings.use_halt_noise or settings.use_halt_time

                if not halt_enabled:
                    raise Exception('You need to set a halt condition for animations, otherwise the rendering of the '
                                    'first frame will never stop!')

            self.set_export_path_luxcore(scene)
            # Stay compatible to old pyluxcore versions
            self.transparent_film = (scene.camera.data.pbrtv3_camera.luxcore_imagepipeline.transparent_film and
                                     hasattr(pyluxcore, 'ConvertFilmChannelOutput_4xFloat_To_4xFloatList'))

            filmWidth, filmHeight = self.get_film_size(scene)

            luxcore_exporter = PBRTv3CoreExporter(scene, self)
            luxcore_config = luxcore_exporter.convert(filmWidth, filmHeight)

            # Maybe export was cancelled by user, don't start the rendering with an incomplete scene then
            if self.test_break() or luxcore_config is None:
                return

            luxcore_session = pyluxcore.RenderSession(luxcore_config)
            # Start the rendering
            PBRTv3Log('Starting the rendering process...')
            luxcore_session.Start()

            # Print a summary of errors that happened during export, if there are any
            luxcore_exporter.error_cache.print_errors()
            export_errors = luxcore_exporter.error_cache.contains_errors()

            # Immediately end the rendering if 'FILESAVER' engine is used
            if scene.luxcore_translatorsettings.export_type == 'luxcoreui':
                luxcore_session.Stop()

                if scene.luxcore_translatorsettings.run_luxcoreui:
                    pbrtv3_path = self.get_lux_binary_path(scene, 'luxcoreui')

                    if not os.path.exists(pbrtv3_path):
                        self.report({'ERROR'}, 'PBRTv3CoreUI executable not found at path "%s"' % pbrtv3_path)
                        return

                    cmd_args = [pbrtv3_path, '-o', 'render.cfg']

                    env = os.environ.copy()

                    if 'linux' in sys.platform:
                        env['LD_LIBRARY_PATH'] = os.path.dirname(pbrtv3_path)

                    pbrtv3_process = subprocess.Popen(cmd_args, cwd=efutil.export_path, env=env)

                return

            bufferdepth = 4 if self.transparent_film else 3
            imageBufferFloat = array.array('f', [0.0] * (filmWidth * filmHeight * bufferdepth))

            imagepipeline_settings = scene.camera.data.pbrtv3_camera.luxcore_imagepipeline
            start_time = time.time()
            last_image_display = start_time
            done = False

            if self.is_animation or not imagepipeline_settings.fast_initial_preview:
                # Use normal display interval from the beginning in animations to speed up the rendering
                display_interval = imagepipeline_settings.displayinterval
            else:
                # Magic formula to compute optimal display interval (found through testing)
                display_interval = float(filmWidth * filmHeight) / 852272.0 * 1.1
                PBRTv3Log('Set initial display interval to %.1fs' % display_interval)

            # Cache imagepipeline settings to detect changes
            session_props = luxcore_exporter.convert_imagepipeline()
            session_props.Set(luxcore_exporter.convert_lightgroup_scales())

            cached_session_props = str(session_props)

            while not self.test_break() and not done:
                time.sleep(0.2)

                # Check if imagepipeline settings have changed
                session_was_updated = False
                new_session_props = luxcore_exporter.convert_imagepipeline()
                new_session_props.Set(luxcore_exporter.convert_lightgroup_scales())

                if str(new_session_props) != cached_session_props:
                    cached_session_props = str(new_session_props)

                    # Safety check for old pyluxcore versions compatibility
                    luxcore_session.Parse(new_session_props)
                    print('Set session settings:\n%s' % cached_session_props)
                    session_was_updated = True

                # Pause/Resume of rendering prcess
                if scene.luxcore_rendering_controls.pause_render:
                    if not luxcore_session.IsInPause():
                        luxcore_session.UpdateStats()

                        luxcore_session.Pause()
                        print('Rendering paused.')

                        stats = luxcore_session.GetStats()
                        result = self.create_result(luxcore_session, imageBufferFloat, scene, stats, filmWidth, filmHeight, False)
                        self.end_result(result)
                        last_image_display = now
                else:
                    if luxcore_session.IsInPause():
                        luxcore_session.Resume()
                        print('Resuming rendering')

                if not luxcore_session.IsInPause():
                    now = time.time()
                    time_since_display = now - last_image_display
                    time_since_start = now - start_time

                # Use user-defined display interval after the first 15 seconds
                if time_since_start > 15.0 and display_interval != imagepipeline_settings.displayinterval:
                    display_interval = imagepipeline_settings.displayinterval
                    PBRTv3Log('Set display interval to %.1fs' % display_interval)

                # Update statistics
                if not luxcore_session.IsInPause():
                    luxcore_session.UpdateStats()

                stats = luxcore_session.GetStats()
                time_until_update = display_interval - time_since_display
                blender_stats = self.CreateBlenderStats(luxcore_config, stats, scene, False, time_until_update,
                                                        display_interval, export_errors)
                self.update_stats('Rendering...', blender_stats)

                # check if any halt conditions are met
                done = self.haltConditionMet(scene, stats)

                if time_since_display > display_interval or session_was_updated:
                    result = self.create_result(luxcore_session, imageBufferFloat, scene, stats, filmWidth, filmHeight, False)
                    self.end_result(result)
                    last_image_display = now

            PBRTv3Log('Ending the rendering process...')
            luxcore_session.Stop()

            # Get the final result
            stats = luxcore_session.GetStats()
            result = self.create_result(luxcore_session, imageBufferFloat, scene, stats, filmWidth, filmHeight, True)

            if scene.pbrtv3_channels.enable_aovs:
                if scene.pbrtv3_channels.saveToDisk:
                    output_path = efutil.filesystem_path(scene.render.filepath)
                    self.update_stats('Saving AOV passes to disk', 'Output path: ' + str(output_path))
                    PBRTv3Log('Saving AOV passes to disk, output path: ' + str(output_path))
                    luxcore_session.GetFilm().Save()

                if scene.pbrtv3_channels.import_into_blender:
                    self.import_aov_channels(scene, luxcore_session, filmWidth, filmHeight, result.layers[0].passes)

            self.end_result(result)
            PBRTv3Log('Done.\n')
        except Exception as exc:
            PBRTv3Log('Rendering aborted: %s' % exc)
            self.report({'ERROR'}, str(exc))
            import traceback

            traceback.print_exc()

    def create_result(self, luxcore_session, imageBufferFloat, scene, stats, filmWidth, filmHeight, is_final_result):
        """
        Updates the film and creates a RenderResult.
        Remember to call self.end_result(result) on the returned result after calling this function!
        """

        if self.transparent_film:
            output_type = pyluxcore.FilmOutputType.RGBA_TONEMAPPED
            def convert(filmWidth, filmHeight, imageBufferFloat):
                # Need the extra "False" because this function has an additional "normalize" argument
                return pyluxcore.ConvertFilmChannelOutput_4xFloat_To_4xFloatList(filmWidth, filmHeight, imageBufferFloat, False)
        else:
            output_type = pyluxcore.FilmOutputType.RGB_TONEMAPPED
            def convert(filmWidth, filmHeight, imageBufferFloat):
                return pyluxcore.ConvertFilmChannelOutput_3xFloat_To_3xFloatList(filmWidth, filmHeight, imageBufferFloat)

        # Update the image
        luxcore_session.GetFilm().GetOutputFloat(output_type, imageBufferFloat)

        result = self.begin_result(0, 0, filmWidth, filmHeight)
        layer = result.layers[0] if bpy.app.version < (2, 74, 4) else result.layers[0].passes[0]

        if (scene.luxcore_enginesettings.renderengine_type == 'TILEPATH' and
                scene.luxcore_tile_highlighting.use_tile_highlighting and not is_final_result):
            # Use a temp image because layer.rect does not support list slicing
            tempImage = convert(filmWidth, filmHeight, imageBufferFloat)
            # Draw tile outlines
            self.draw_tiles(scene, stats, tempImage, filmWidth, filmHeight)
            layer.rect = tempImage
        else:
            layer.rect = convert(filmWidth, filmHeight, imageBufferFloat)

        return result

    def get_film_size(self, scene):
        width, height = scene.camera.data.pbrtv3_camera.pbrtv3_film.resolution(scene)

        if scene.render.use_border:
            x_min, x_max, y_min, y_max = [
                scene.render.border_min_x, scene.render.border_max_x,
                scene.render.border_min_y, scene.render.border_max_y
            ]

            width = int(x_max * width) - int(x_min * width)
            height = int(y_max * height) - int(y_min * height)

            # In case border becomes too small
            width = max(width, 1)
            height = max(height, 1)

        return width, height

    def import_aov_channels(self, scene, lcSession, filmWidth, filmHeight, passes):
        channelCalcStartTime = time.time()
        channels = scene.pbrtv3_channels

        if channels.RGB:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'RGB', channels.saveToDisk)
        if channels.RGBA:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'RGBA', channels.saveToDisk)
        #if channels.RGB_TONEMAPPED:
        #    self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
        #                               'RGB_TONEMAPPED', channels.saveToDisk)
        # When the film is transparent the RGBA_TONEMAPPED channel is already imported as the main render result
        if channels.RGBA_TONEMAPPED and not self.transparent_film:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'RGBA_TONEMAPPED', channels.saveToDisk)
        if channels.ALPHA:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'ALPHA', channels.saveToDisk)
        if channels.DEPTH:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'DEPTH', channels.saveToDisk,
                                       normalize = channels.normalize_DEPTH)
        if channels.POSITION:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'POSITION', channels.saveToDisk)
        if channels.GEOMETRY_NORMAL:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'GEOMETRY_NORMAL', channels.saveToDisk)
        if channels.SHADING_NORMAL:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'SHADING_NORMAL', channels.saveToDisk)
        if channels.MATERIAL_ID:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'MATERIAL_ID', channels.saveToDisk)
        if channels.OBJECT_ID:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'OBJECT_ID', channels.saveToDisk)
        if channels.DIRECT_DIFFUSE:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'DIRECT_DIFFUSE', channels.saveToDisk,
                                       normalize = channels.normalize_DIRECT_DIFFUSE)
        if channels.DIRECT_GLOSSY:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'DIRECT_GLOSSY', channels.saveToDisk,
                                       normalize = channels.normalize_DIRECT_GLOSSY)
        if channels.EMISSION:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'EMISSION', channels.saveToDisk)
        if channels.INDIRECT_DIFFUSE:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'INDIRECT_DIFFUSE', channels.saveToDisk,
                                       normalize = channels.normalize_INDIRECT_DIFFUSE)
        if channels.INDIRECT_GLOSSY:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'INDIRECT_GLOSSY', channels.saveToDisk,
                                       normalize = channels.normalize_INDIRECT_GLOSSY)
        if channels.INDIRECT_SPECULAR:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'INDIRECT_SPECULAR', channels.saveToDisk,
                                       normalize = channels.normalize_INDIRECT_SPECULAR)
        if channels.DIRECT_SHADOW_MASK:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'DIRECT_SHADOW_MASK', channels.saveToDisk)
        if channels.INDIRECT_SHADOW_MASK:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'INDIRECT_SHADOW_MASK', channels.saveToDisk)
        if channels.UV:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'UV', channels.saveToDisk)
        if channels.RAYCOUNT:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'RAYCOUNT', channels.saveToDisk,
                                       normalize = channels.normalize_RAYCOUNT)
        if channels.IRRADIANCE:
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'IRRADIANCE', channels.saveToDisk)

        props = lcSession.GetRenderConfig().GetProperties()
        # Convert all MATERIAL_ID_MASK channels
        mask_ids = set()
        for i in props.GetAllUniqueSubNames('film.outputs'):
            if props.Get(i + '.type').GetString() == 'MATERIAL_ID_MASK':
                mask_ids.add(props.Get(i + '.id').GetInt())

        for i in range(len(mask_ids)):
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'MATERIAL_ID_MASK', channels.saveToDisk, buffer_id = i)

        # Convert all BY_MATERIAL_ID channels
        ids = set()
        for i in props.GetAllUniqueSubNames('film.outputs'):
            if props.Get(i + '.type').GetString() == 'BY_MATERIAL_ID':
                ids.add(props.Get(i + '.id').GetInt())

        for i in range(len(ids)):
            self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                       'BY_MATERIAL_ID', channels.saveToDisk, buffer_id = i)

        # Convert all RADIANCE_GROUP channels
        lightgroup_count = lcSession.GetFilm().GetRadianceGroupCount()

        # don't import the standard lightgroup that contains all lights even if no groups are set
        if lightgroup_count > 1:
            for i in range(lightgroup_count):
                self.convertChannelToImage(lcSession, scene, passes, filmWidth, filmHeight,
                                           'RADIANCE_GROUP', channels.saveToDisk, buffer_id = i)

        channelCalcTime = time.time() - channelCalcStartTime
        if channelCalcTime > 0.1:
            PBRTv3Log('AOV import took %.1f seconds' % channelCalcTime)

    cached_preview_properties = ''

    def determine_preview_settings(self, scene):
        # Find out what exactly we have to do for material preview, if it's actually texture preview etc.
        from ..export import materials as export_materials

        # Iterate through the preview scene, finding objects with materials attached
        objects_mats = {}
        for obj in [ob for ob in scene.objects if ob.is_visible(scene) and not ob.hide_render]:
            for mat in export_materials.get_instance_materials(obj):
                if mat is not None:
                    if not obj.name in objects_mats.keys():
                        objects_mats[obj] = []
                    objects_mats[obj].append(mat)

        preview_type = None  # 'MATERIAL' or 'TEXTURE'

        # find objects that are likely to be the preview objects
        preview_objects = [o for o in objects_mats.keys() if o.name.startswith('preview')]
        if len(preview_objects) > 0:
            preview_type = 'MATERIAL'
        else:
            preview_objects = [o for o in objects_mats.keys() if o.name.startswith('texture')]
            if len(preview_objects) > 0:
                preview_type = 'TEXTURE'

        if preview_type is None:
            return

        # Find the materials attached to the likely preview object
        likely_materials = objects_mats[preview_objects[0]]
        if len(likely_materials) < 1:
            print('no preview materials')
            return

        preview_material = likely_materials[0]
        preview_texture = None

        if preview_type == 'TEXTURE':
            preview_texture = preview_material.active_texture

        return preview_type, preview_material, preview_texture, preview_objects[0]

    def luxcore_render_preview(self, scene):
        # PBRTv3Core libs
        if not PYLUXCORE_AVAILABLE:
            PBRTv3Log('ERROR: PBRTv3Core preview rendering requires pyluxcore')
            return
        from ..outputs.luxcore_api import pyluxcore
        from ..export.luxcore.materialpreview import MaterialPreviewExporter

        try:
            def update_result(luxcore_session, imageBufferFloat, filmWidth, filmHeight):
                # Update the image
                luxcore_session.GetFilm().GetOutputFloat(pyluxcore.FilmOutputType.RGB_TONEMAPPED, imageBufferFloat)

                # Here we write the pixel values to the RenderResult
                result = self.begin_result(0, 0, filmWidth, filmHeight)
                layer = result.layers[0] if bpy.app.version < (2, 74, 4) else result.layers[0].passes[0]

                layer.rect = pyluxcore.ConvertFilmChannelOutput_3xFloat_To_3xFloatList(filmWidth, filmHeight,
                                                                                   imageBufferFloat)
                self.end_result(result)

            filmWidth, filmHeight = scene.camera.data.pbrtv3_camera.pbrtv3_film.resolution(scene)
            is_thumbnail = filmWidth <= 96

            # don't render thumbnails
            if is_thumbnail:
                return

            preview_type, preview_material, preview_texture, preview_object = self.determine_preview_settings(scene)

            if preview_type is None:
                return

            exporter = MaterialPreviewExporter(scene, self, is_thumbnail, preview_type, preview_material,
                                               preview_texture, preview_object)
            luxcore_config = exporter.convert(filmWidth, filmHeight)

            if luxcore_config is None:
                return

            # Create preview rendersession
            luxcore_session = pyluxcore.RenderSession(luxcore_config)

            buffer_depth = 4 if is_thumbnail else 3
            imageBufferFloat = array.array('f', [0.0] * (filmWidth * filmHeight * buffer_depth))

            # Start the rendering
            thumbnail_info = '(thumbnail)' if is_thumbnail else ''
            PBRTv3Log('Starting', preview_type, 'preview render', thumbnail_info)
            startTime = time.time()
            luxcore_session.Start()

            done = False

            if is_thumbnail or preview_type == 'TEXTURE':
                while not self.test_break() and not done:
                    time.sleep(0.02)
                    luxcore_session.UpdateStats()
                    stats = luxcore_session.GetStats()
                    done = (stats.Get('stats.renderengine.convergence').GetFloat() == 1.0 or
                            stats.Get('stats.renderengine.pass').GetInt() > 10)
            else:
                stopTime = 6.0

                while not self.test_break() and time.time() - startTime < stopTime and not done:
                    time.sleep(0.1)
                    update_result(luxcore_session, imageBufferFloat, filmWidth, filmHeight)

                    # Update statistics
                    luxcore_session.UpdateStats()
                    stats = luxcore_session.GetStats()
                    done = stats.Get('stats.renderengine.convergence').GetFloat() == 1.0

            update_result(luxcore_session, imageBufferFloat, filmWidth, filmHeight)

            luxcore_session.Stop()
            PBRTv3Log('Preview render done (%.2fs)' % (time.time() - startTime))
        except Exception as exc:
            PBRTv3Log('Rendering aborted: %s' % exc)
            import traceback

            traceback.print_exc()

    ############################################################################
    # Viewport render
    ############################################################################

    luxcore_exporter = None
    space = None # The VIEW_3D space this viewport render is running in
    critical_errors = False # Flag that tells wether critical errors prevent the viewport render from running

    viewFilmWidth = -1
    viewFilmHeight = -1
    viewImageBufferFloat = None
    last_update_time = 0
    # store renderengine configuration of last update
    lastRenderSettings = ''
    lastVolumeSettings = ''
    lastSessionSettings = ''
    lastHaltTime = -1
    lastHaltSamples = -1
    lastCameraSettings = ''
    lastVisibilitySettings = None
    lastNodeMatSettings = ''
    update_counter = 0

    def create_view_buffer(self, width, height):
        bufferdepth = 4 if self.transparent_film else 3
        self.viewImageBufferFloat = array.array('f', [0.0] * (width * height * bufferdepth))

    def luxcore_view_draw(self, context):
        def draw_framebuffer():
            # Update the screen

            if self.transparent_film:
                bufferdepth = 4
                buffertype = bgl.GL_RGBA
                # Enable GL_BLEND so the alpha channel is visible
                bgl.glEnable(bgl.GL_BLEND)
            else:
                bufferdepth = 3
                buffertype = bgl.GL_RGB

            buffersize = self.viewFilmWidth * self.viewFilmHeight * bufferdepth
            glBuffer = bgl.Buffer(bgl.GL_FLOAT, [buffersize], self.viewImageBufferFloat)

            bgl.glRasterPos2i(0, 0)
            bgl.glDrawPixels(self.viewFilmWidth, self.viewFilmHeight, buffertype, bgl.GL_FLOAT, glBuffer)
            # restore the default
            bgl.glDisable(bgl.GL_BLEND)

        view_draw_startTime = time.time()
        elapsed = view_draw_startTime - self.last_update_time

        if context.scene.camera:
            interval = context.scene.camera.data.pbrtv3_camera.luxcore_imagepipeline.viewport_interval / 1000
        else:
            interval = 0.05

        # Run at fixed fps
        if elapsed < interval:
            draw_framebuffer()
            self.tag_redraw()
            return

        # Check for errors
        if self.critical_errors:
            return

        # PBRTv3Core libs
        if not PYLUXCORE_AVAILABLE:
            PBRTv3Log('ERROR: PBRTv3Core real-time rendering requires pyluxcore')
            return

        stop_redraw = False

        # Check if the size of the window is changed
        if (self.viewFilmWidth != context.region.width) or (
                self.viewFilmHeight != context.region.height):
            update_changes = UpdateChanges()
            update_changes.set_cause(config = True)
            self.luxcore_view_update(context, update_changes)

        # check if camera settings have changed
        self.luxcore_exporter.convert_camera()
        newCameraSettings = str(self.luxcore_exporter.pop_updated_scene_properties())

        if self.lastCameraSettings == '':
            self.lastCameraSettings = newCameraSettings
        elif self.lastCameraSettings != newCameraSettings and newCameraSettings.strip() != '':
            update_changes = UpdateChanges()
            update_changes.set_cause(camera = True)
            self.lastCameraSettings = newCameraSettings
            self.luxcore_view_update(context, update_changes)

        session = PBRTv3CoreSessionManager.get_session(self.space)

        # Update statistics
        if PBRTv3CoreSessionManager.is_session_active(self.space):
            session.luxcore_session.UpdateStats()
            stats = session.luxcore_session.GetStats()

            stop_redraw = self.haltConditionMet(context.scene, stats, realtime_preview = True)

            if not session.is_in_scene_edit():
                # update statistic display in Blender
                luxcore_config = session.luxcore_session.GetRenderConfig()
                blender_stats = self.CreateBlenderStats(luxcore_config, stats, context.scene, realtime_preview=True)
                status = 'Paused' if stop_redraw else 'Rendering'

                if context.space_data.local_view:
                    status = '[Local] ' + status

                self.update_stats(status, blender_stats)

        # Update the image buffer
        if self.transparent_film:
            output_type = pyluxcore.FilmOutputType.RGBA_TONEMAPPED
        else:
            output_type = pyluxcore.FilmOutputType.RGB_TONEMAPPED

        session.luxcore_session.WaitNewFrame()
        session.luxcore_session.GetFilm().GetOutputFloat(output_type, self.viewImageBufferFloat)
        draw_framebuffer()

        self.last_update_time = view_draw_startTime

        if stop_redraw:
            # Pause rendering
            PBRTv3CoreSessionManager.pause(self.space)
        else:
            # Trigger another update
            self.tag_redraw()

    def find_update_changes(self, context):
        """
        Find out what triggered the update (default: unknown)
        """
        update_changes = UpdateChanges()

        try:
            # check if visibility of objects was changed
            if self.lastVisibilitySettings is None:
                self.lastVisibilitySettings = set(context.visible_objects)
            else:
                objectsToAdd = set(context.visible_objects) - self.lastVisibilitySettings
                objectsToRemove = self.lastVisibilitySettings - set(context.visible_objects)

                if len(objectsToAdd) > 0:
                    update_changes.set_cause(mesh = True)
                    update_changes.changed_objects_mesh.update(objectsToAdd)

                if len(objectsToRemove) > 0:
                    update_changes.set_cause(objectsRemoved = True)
                    update_changes.removed_objects.update(objectsToRemove)

            self.lastVisibilitySettings = set(context.visible_objects)

            if (not PBRTv3CoreSessionManager.is_session_active(self.space) or
                    self.luxcore_exporter is None):
                update_changes.set_cause(startViewportRender = True)

                # PBRTv3CoreExporter instance for viewport rendering is only created here
                self.luxcore_exporter = PBRTv3CoreExporter(context.scene, self, True, context)

            # check if filmsize has changed
            if (self.viewFilmWidth == -1) or (self.viewFilmHeight == -1) or (
                    self.viewFilmWidth != context.region.width) or (
                    self.viewFilmHeight != context.region.height):
                update_changes.set_cause(config = True)

            if bpy.data.objects.is_updated:
                # check objects for updates
                for ob in bpy.data.objects:
                    if ob is None:
                        continue

                    if ob.is_updated_data:
                        if ob.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT']:
                            update_changes.set_cause(mesh = True)
                            update_changes.changed_objects_mesh.add(ob)
                        elif ob.type in ['LAMP']:
                            update_changes.set_cause(light = True)
                            update_changes.changed_objects_transform.add(ob)
                        elif ob.type in ['CAMERA'] and ob.name == context.scene.camera.name:
                            update_changes.set_cause(camera = True)

                    if ob.is_updated:
                        if ob.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'EMPTY']:
                            # check if a new material was assigned
                            if ob.data is not None and ob.data.is_updated:
                                update_changes.set_cause(mesh = True)
                                update_changes.changed_objects_mesh.add(ob)
                            else:
                                update_changes.set_cause(objectTransform = True)
                                update_changes.changed_objects_transform.add(ob)
                        elif ob.type in ['LAMP']:
                            update_changes.set_cause(light = True)
                            update_changes.changed_objects_transform.add(ob)
                        elif ob.type in ['CAMERA'] and ob.name == context.scene.camera.name:
                            update_changes.set_cause(camera = True)

            if bpy.data.materials.is_updated:
                for mat in bpy.data.materials:
                    nodetree_name = mat.pbrtv3_material.nodetree

                    mat_updated = False

                    if nodetree_name and nodetree_name in bpy.data.node_groups:
                        # Check for nodetree updates
                        nodetree = bpy.data.node_groups[nodetree_name]

                        if nodetree.is_updated or nodetree.is_updated_data:
                            self.luxcore_exporter.convert_material(mat)
                            newNodeMatSettings = str(self.luxcore_exporter.pop_updated_scene_properties())

                            if self.lastNodeMatSettings == '':
                                self.lastNodeMatSettings = newNodeMatSettings
                                mat_updated = True
                            elif self.lastNodeMatSettings != newNodeMatSettings:
                                self.lastNodeMatSettings = newNodeMatSettings
                                mat_updated = True
                    else:
                        mat_updated = mat.is_updated

                    if mat_updated:
                        # only update this material
                        update_changes.changed_materials.add(mat)
                        update_changes.set_cause(materials = True)

            if bpy.data.textures.is_updated:
                for tex in bpy.data.textures:
                    if tex.is_updated:
                        for mat in tex.users_material:
                            update_changes.changed_materials.add(mat)
                            update_changes.set_cause(materials = True)

            # check for changes in volume configuration
            for volume in context.scene.pbrtv3_volumes.volumes:
                self.luxcore_exporter.convert_volume(volume)

            # Exclude all densitygrid data properties from the update check
            # All lines of the form "scene.textures.<densitygrid_tex_name>.data = [...]" will be removed
            # This allows us to avoid re-exports of the smoke for every volume update check
            newVolumeProperties = self.luxcore_exporter.pop_updated_scene_properties()
            lines = str(newVolumeProperties).split('\n')
            densitygrid_textures = [line for line in lines if 'type = "densitygrid"' in line]
            names = [elem.split('.')[2] for elem in densitygrid_textures]
            to_delete = ['scene.textures.' + name + '.data' for name in names]
            newVolumeProperties.DeleteAll(to_delete)

            newVolumeSettings = str(newVolumeProperties)

            if self.lastVolumeSettings == '':
                self.lastVolumeSettings = newVolumeSettings
            elif self.lastVolumeSettings != newVolumeSettings:
                update_changes.set_cause(volumes = True)
                self.lastVolumeSettings = newVolumeSettings
                # reset the smoke cache because we need to redefine volume properties
                SmokeCache.reset()

            # Check for changes in halt conditions
            newHaltTime = context.scene.luxcore_enginesettings.halt_time_preview
            newHaltSamples = context.scene.luxcore_enginesettings.halt_samples_preview

            if self.lastHaltTime != -1 and self.lastHaltSamples != -1:
                if newHaltTime > self.lastHaltTime or newHaltSamples > self.lastHaltSamples:
                    update_changes.set_cause(haltconditions = True)

            self.lastHaltTime = newHaltTime
            self.lastHaltSamples = newHaltSamples

            # Check for config changes that need a restart of the rendering
            self.luxcore_exporter.convert_config(self.viewFilmWidth, self.viewFilmHeight)
            newRenderSettings = str(self.luxcore_exporter.config_exporter.properties)

            if self.lastRenderSettings == '':
                self.lastRenderSettings = newRenderSettings
            elif self.lastRenderSettings != newRenderSettings:
                update_changes.set_cause(config = True)
                self.lastRenderSettings = newRenderSettings

            # Check for config changes that do not require the rendering to be restarted (tonemapping, lightgroups)
            session_props = self.luxcore_exporter.convert_imagepipeline()
            session_props.Set(self.luxcore_exporter.convert_lightgroup_scales())
            newSessionSettings = str(session_props)

            if self.lastSessionSettings == '':
                self.lastSessionSettings = newSessionSettings
            elif self.lastSessionSettings != newSessionSettings:
                update_changes.set_cause(session = True)
                self.lastSessionSettings = newSessionSettings

        except Exception as exc:
            PBRTv3Log('Update check failed: %s' % exc)
            self.report({'ERROR'}, str(exc))
            import traceback
            traceback.print_exc()

        return update_changes

    def luxcore_view_update(self, context, update_changes=None):
        # PBRTv3Core libs
        if not PYLUXCORE_AVAILABLE:
            PBRTv3Log('ERROR: PBRTv3Core real-time rendering requires pyluxcore')
            return

        if self.test_break() or context.scene.luxcore_rendering_controls.pause_viewport_render:
            return

        print('\n###########################################################')

        # get update starttime in milliseconds
        view_update_startTime = int(round(time.time() * 1000))
        # debug
        self.update_counter += 1
        print('Viewport Update', self.update_counter)

        ##########################################################################
        #                        Dynamic Updates
        ##########################################################################

        # check which changes took place
        if update_changes is None:
            update_changes = self.find_update_changes(context)

        update_changes.print_updates()

        if update_changes.cause_unknown:
            print('Update cause unknown, skipping update', self.update_counter)

        elif update_changes.cause_haltconditions:
            PBRTv3CoreSessionManager.resume(self.space)

        elif update_changes.cause_startViewportRender:
            try:
                # Find out in which space this rendersession is running.
                # This code assumes that only one VIEW_3D is set to RENDERED mode at a time - scripts that set
                # many views to rendered at once might break this detection, but I fear we can't implement a better
                # detection algorithm
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if (space.type == 'VIEW_3D' and space.viewport_shade == 'RENDERED' and
                                        space not in PBRTv3CoreSessionManager.sessions.keys()):
                                self.space = space
                                break

                PBRTv3CoreSessionManager.stop_luxcore_session(self.space)

                if context.scene.camera:
                    self.transparent_film = context.scene.camera.data.pbrtv3_camera.luxcore_imagepipeline.transparent_film
                else:
                    self.transparent_film = False

                self.lastRenderSettings = ''
                self.lastVolumeSettings = ''
                self.lastSessionSettings = ''
                self.lastHaltTime = -1
                self.lastHaltSamples = -1
                self.lastCameraSettings = ''
                self.lastVisibilitySettings = None
                self.update_counter = 0

                PBRTv3Manager.SetCurrentScene(context.scene)

                self.viewFilmWidth = context.region.width
                self.viewFilmHeight = context.region.height
                self.create_view_buffer(self.viewFilmWidth, self.viewFilmHeight)

                # Export the Blender scene
                luxcore_config = self.luxcore_exporter.convert(self.viewFilmWidth, self.viewFilmHeight)
                if luxcore_config is None:
                    PBRTv3Log('ERROR: not a valid luxcore config')
                    return

                PBRTv3CoreSessionManager.create_luxcore_session(luxcore_config, self.space)
                PBRTv3CoreSessionManager.start_luxcore_session(self.space)

                self.critical_errors = False
            except Exception as exc:
                # This flag is used to prevent the luxcore_draw() function from crashing Blender
                self.critical_errors = True

                PBRTv3Log('View update aborted: %s' % exc)
                # Show error message to user in the viewport UI
                self.update_stats('Error: ', str(exc))

                import traceback
                traceback.print_exc()

        else:
            # config update
            if update_changes.cause_config:
                PBRTv3Log('Configuration update')

                if context.scene.camera:
                    self.transparent_film = context.scene.camera.data.pbrtv3_camera.luxcore_imagepipeline.transparent_film
                else:
                    self.transparent_film = False

                self.viewFilmWidth = context.region.width
                self.viewFilmHeight = context.region.height

                self.create_view_buffer(self.viewFilmWidth, self.viewFilmHeight)

                luxcore_config = PBRTv3CoreSessionManager.get_session(self.space).luxcore_session.GetRenderConfig()
                PBRTv3CoreSessionManager.stop_luxcore_session(self.space)

                self.luxcore_exporter.convert_config(self.viewFilmWidth, self.viewFilmHeight)

                # change config
                luxcore_config.Parse(self.luxcore_exporter.config_properties)
                if luxcore_config is None:
                    PBRTv3Log('ERROR: not a valid luxcore config')
                    return

                PBRTv3CoreSessionManager.create_luxcore_session(luxcore_config, self.space)
                PBRTv3CoreSessionManager.start_luxcore_session(self.space)

            if update_changes.scene_edit_necessary:
                # begin sceneEdit
                luxcore_scene = PBRTv3CoreSessionManager.get_session(self.space).luxcore_session.GetRenderConfig().GetScene()
                PBRTv3CoreSessionManager.begin_scene_edit(self.space)

                if update_changes.cause_camera:
                    PBRTv3Log('Camera update')
                    self.luxcore_exporter.convert_camera()

                if update_changes.cause_materials:
                    PBRTv3Log('Materials update')
                    for material in update_changes.changed_materials:
                        self.luxcore_exporter.convert_material(material)

                if update_changes.cause_mesh:
                    for ob in update_changes.changed_objects_mesh:
                        PBRTv3Log('Mesh update: ' + ob.name)
                        self.luxcore_exporter.convert_object(ob, luxcore_scene, update_mesh=True, update_material=False)

                if update_changes.cause_light or update_changes.cause_objectTransform:
                    for ob in update_changes.changed_objects_transform:
                        PBRTv3Log('Transformation update: ' + ob.name)

                        self.luxcore_exporter.convert_object(ob, luxcore_scene, update_mesh=False, update_material=False)

                if update_changes.cause_objectsRemoved:
                    for ob in update_changes.removed_objects:
                        key = get_elem_key(ob)

                        if ob.type == 'LAMP':
                            if key in self.luxcore_exporter.light_cache:
                                # In case of sunsky there might be multiple light sources, loop through them
                                for exported_light in self.luxcore_exporter.light_cache[key].exported_lights:
                                    luxcore_name = exported_light.luxcore_name

                                    if exported_light.type == 'AREA':
                                        # Area lights are meshlights and treated like objects with glowing materials
                                        luxcore_scene.DeleteObject(luxcore_name)
                                    else:
                                        luxcore_scene.DeleteLight(luxcore_name)
                        else:
                            if key in self.luxcore_exporter.object_cache:
                                # loop through object components (split by materials)
                                for exported_object in self.luxcore_exporter.object_cache[key].exported_objects:
                                    luxcore_name = exported_object.luxcore_object_name
                                    luxcore_scene.DeleteObject(luxcore_name)

                if update_changes.cause_volumes:
                    for volume in context.scene.pbrtv3_volumes.volumes:
                        self.luxcore_exporter.convert_volume(volume)

                updated_properties = self.luxcore_exporter.pop_updated_scene_properties()

                if context.space_data.local_view:
                    # Add a uniform white background light in local view so we have a lightsource
                    updated_properties.Set(pyluxcore.Property('scene.lights.LOCALVIEW_BACKGROUND.type', 'constantinfinite'))
                else:
                    luxcore_scene.DeleteLight('LOCALVIEW_BACKGROUND')

                if context.scene.luxcore_translatorsettings.print_scn:
                    # Debug output
                    print('Updated scene properties:')
                    print(updated_properties, '\n')

                # parse scene changes and end sceneEdit
                luxcore_scene.Parse(updated_properties)

                PBRTv3CoreSessionManager.end_scene_edit(self.space)

            if update_changes.cause_session:
                # Only update the session without restarting the rendering
                props = self.luxcore_exporter.convert_imagepipeline()
                props.Set(self.luxcore_exporter.convert_lightgroup_scales())

                PBRTv3CoreSessionManager.get_session(self.space).luxcore_session.Parse(props)

            # Resume in case the session was paused
            PBRTv3CoreSessionManager.resume(self.space)

        # report time it took to update
        view_update_time = int(round(time.time() * 1000)) - view_update_startTime
        PBRTv3Log('Dynamic updates: update took %dms' % view_update_time)

        self.last_update_time = time.time()


class Session(object):
    """
    Wrapper for PBRTv3Core's rendersession class.
    """
    def __init__(self, luxcore_session):
        self.luxcore_session = luxcore_session
        self.is_active = False

    def is_in_scene_edit(self):
        return self.luxcore_session.IsInSceneEdit()

    def is_paused(self):
        return self.luxcore_session.IsInPause()


class PBRTv3CoreSessionManager(object):
    """
    Session manager for viewport render sessions only.
    Provides a mapping from Blender screen spaces to their respective PBRTv3Core session.
    """

    sessions = {}

    @classmethod
    def create_luxcore_session(cls, luxcore_config, space):
        # space: bpy.context.screen.areas[x].spaces[y] (areas[x].type == "VIEW_3D", spaces[y].type == "VIEW_3D")
        cls.sessions[space] = Session(pyluxcore.RenderSession(luxcore_config))

    @classmethod
    def get_session(cls, space):
        return cls.sessions[space]

    @classmethod
    def is_session_active(cls, space):
        return space in cls.sessions and cls.sessions[space].is_active

    @classmethod
    def start_luxcore_session(cls, space):
        if space in cls.sessions:
            session = cls.sessions[space]

            if not session.is_active:
                print('Starting viewport render')
                session.luxcore_session.Start()
                session.is_active = True

    @classmethod
    def stop_luxcore_session(cls, space):
        if space in cls.sessions:
            session = cls.sessions[space]

            if session.is_active:
                print('Stopping viewport render')
                cls.end_scene_edit(space)
                session.is_active = False

                session.luxcore_session.Stop()
                session.luxcore_session = None

                del cls.sessions[space]

    @classmethod
    def stop_orphaned_sessions(cls):
        # Cover the following cases that can happen to a running viewport render space:
        # - the space is removed from the Blender UI
        # - the editor type (area.type) is changed to something else than 'VIEW_3D'

        # TODO: rendersession in second window, window is closed --> session runs forever

        existing_spaces = []
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            existing_spaces.append(space)

        orphans = []
        for space, session in cls.sessions.items():
            if space not in existing_spaces and session.is_active and space is not None:
                orphans.append((space, session))

        for space, session in orphans:
            print('Stopping orphaned rendersession')
            if session.is_in_scene_edit():
                session.luxcore_session.EndSceneEdit()

            session.luxcore_session.Stop()
            session.luxcore_session = None

            del cls.sessions[space]

    @classmethod
    def begin_scene_edit(cls, space):
        if space in cls.sessions:
            session = cls.sessions[space]

            if session.is_active and not session.is_in_scene_edit():
                print('Beginning scene edit')
                session.luxcore_session.BeginSceneEdit()

    @classmethod
    def end_scene_edit(cls, space):
        if space in cls.sessions:
            session = cls.sessions[space]

            if session.is_active and session.is_in_scene_edit():
                print('Ending scene edit')
                session.luxcore_session.EndSceneEdit()

    @classmethod
    def pause(cls, space):
        if space in cls.sessions:
            session = cls.sessions[space]

            if session.is_active and not session.is_paused():
                print('Pausing viewport render')
                session.luxcore_session.Pause()

    @classmethod
    def resume(cls, space):
        if space in cls.sessions:
            session = cls.sessions[space]

            if session.is_active and session.is_paused():
                print('Resuming viewport render')
                session.luxcore_session.Resume()


@persistent
def stop_viewport_render(context):
    PBRTv3CoreSessionManager.stop_orphaned_sessions()

    # Check registered spaces with rendersessions if they are still in RENDERED mode
    spaces = list(PBRTv3CoreSessionManager.sessions.keys())  # get a copy of the keys because we will modify the dict
    for space in spaces:
        if space is not None and space.viewport_shade != 'RENDERED':
            PBRTv3CoreSessionManager.stop_luxcore_session(space)

bpy.app.handlers.scene_update_post.append(stop_viewport_render)


class UpdateChanges(object):
    def __init__(self):
        self.changed_objects_transform = set()
        self.changed_objects_mesh = set()
        self.changed_materials = set()
        self.removed_objects = set()

        self.cause_unknown = True
        self.cause_startViewportRender = False
        self.cause_mesh = False
        self.cause_light = False
        self.cause_camera = False
        self.cause_objectTransform = False
        self.cause_layers = False
        self.cause_materials = False
        self.cause_config = False
        self.cause_session = False
        self.cause_objectsRemoved = False
        self.cause_volumes = False
        self.cause_haltconditions = False

        self.scene_edit_necessary = False

    def set_cause(self,
                  startViewportRender = None,
                  mesh = None,
                  light = None,
                  camera = None,
                  objectTransform = None,
                  layers = None,
                  materials = None,
                  config = None,
                  session = None,
                  objectsRemoved = None,
                  volumes = None,
                  haltconditions = None):
        # automatically switch off unkown
        self.cause_unknown = False

        if startViewportRender is not None:
            self.cause_startViewportRender = startViewportRender
        if mesh is not None:
            self.cause_mesh = mesh
            self.scene_edit_necessary |= mesh
        if light is not None:
            self.cause_light = light
            self.scene_edit_necessary |= light
        if camera is not None:
            self.cause_camera = camera
            self.scene_edit_necessary = camera
        if objectTransform is not None:
            self.cause_objectTransform = objectTransform
            self.scene_edit_necessary |= objectTransform
        if layers is not None:
            self.cause_layers = layers
        if materials is not None:
            self.cause_materials = materials
            self.scene_edit_necessary |= materials
        if config is not None:
            self.cause_config = config
        if session is not None:
            self.cause_session = session
        if objectsRemoved is not None:
            self.cause_objectsRemoved = objectsRemoved
            self.scene_edit_necessary |= objectsRemoved
        if volumes is not None:
            self.cause_volumes = volumes
            self.scene_edit_necessary |= volumes
        if haltconditions is not None:
            self.cause_haltconditions = haltconditions

    def print_updates(self):
        print('===== Realtime update information: =====')

        if self.cause_unknown:
            print('cause unknown')
        if self.cause_startViewportRender:
            print('realtime preview was started')
        if self.cause_mesh:
            print('object meshes were updated:')
            for obj in self.changed_objects_mesh:
                print('    ' + obj.name)
        if self.cause_light:
            print('light update')
        if self.cause_camera:
            print('camera update')
        if self.cause_objectTransform:
            print('objects where transformed:')
            for obj in self.changed_objects_transform:
                print('    ' + obj.name)
        if self.cause_layers:
            print('layer visibility was changed')
        if self.cause_materials:
            print('materials where changed:')
            for mat in self.changed_materials:
                print('    ' + mat.name)
        if self.cause_config:
            print('configuration was changed')
        if self.cause_session:
            print('session was changed')
        if self.cause_objectsRemoved:
            print('objects where removed')
        if self.cause_volumes:
            print('volumes changed')
        if self.cause_haltconditions:
            print('halt conditions changed')

        print('========================================')

