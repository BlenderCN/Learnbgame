# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
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
"""Main LuxRender extension class definition"""

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
from .. import LuxRenderAddon
from ..export import get_output_filename, get_worldscale
from ..export.scene import SceneExporter
from ..outputs import LuxManager, LuxFilmDisplay
from ..outputs import LuxLog
from ..outputs.pure_api import LUXRENDER_VERSION
from ..outputs.luxcore_api import ToValidLuxCoreName
from ..outputs.luxcore_api import PYLUXCORE_AVAILABLE, UseLuxCore, pyluxcore
from ..export.luxcore import LuxCoreExporter

# Exporter Property Groups need to be imported to ensure initialisation
from ..properties import (
    accelerator, camera, engine, filter, integrator, ior_data, lamp, lampspectrum_data,
    material, node_material, node_inputs, node_texture, node_fresnel, node_converter,
    mesh, object as prop_object, particles, rendermode, sampler, texture, world,
    luxcore_engine, luxcore_scene, luxcore_material, luxcore_realtime, luxcore_lamp,
    luxcore_tile_highlighting, luxcore_imagepipeline, luxcore_translator
)

# Exporter Interface Panels need to be imported to ensure initialisation
from ..ui import (
    render_panels, camera, image, lamps, mesh, node_editor, object as ui_object, particles, world,
    imageeditor_panel
)

# Legacy material editor panels, node editor UI is initialized above
from ..ui.materials import (
    main as mat_main, compositing, carpaint, cloth, glass, glass2, roughglass, glossytranslucent,
    glossycoating, glossy, layered, matte, mattetranslucent, metal, metal2, mirror, mix as mat_mix, null,
    scatter, shinymetal, velvet
)

#Legacy texture editor panels
from ..ui.textures import (
    main as tex_main, abbe, add, band, blender, bilerp, blackbody, brick, cauchy, constant, colordepth,
    checkerboard, cloud, densitygrid, dots, equalenergy, exponential, fbm, fresnelcolor, fresnelname, gaussian,
    harlequin, hitpointcolor, hitpointalpha, hitpointgrey, imagemap, imagesampling, normalmap,
    lampspectrum, luxpop, marble, mix as tex_mix, multimix, sellmeier, scale, subtract, sopra, uv,
    uvmask, windy, wrinkled, mapping, tabulateddata, transform, pointiness
)

# Exporter Operators need to be imported to ensure initialisation
from .. import operators
from ..operators import lrmdb


def _register_elm(elm, required=False):
    try:
        elm.COMPAT_ENGINES.add('LUXRENDER_RENDER')
    except:
        if required:
            LuxLog('Failed to add LuxRender to ' + elm.__name__)

# Add standard Blender Interface elements
_register_elm(bl_ui.properties_render.RENDER_PT_render, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_dimensions, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_output, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_stamp)

#_register_elm(bl_ui.properties_render_layer.RENDERLAYER_PT_views) # multiview

_register_elm(bl_ui.properties_scene.SCENE_PT_scene, required=True)
_register_elm(bl_ui.properties_scene.SCENE_PT_audio)
_register_elm(bl_ui.properties_scene.SCENE_PT_physics)  # This is the gravity panel
_register_elm(bl_ui.properties_scene.SCENE_PT_keying_sets)
_register_elm(bl_ui.properties_scene.SCENE_PT_keying_set_paths)
_register_elm(bl_ui.properties_scene.SCENE_PT_unit)
_register_elm(bl_ui.properties_scene.SCENE_PT_color_management)

_register_elm(bl_ui.properties_scene.SCENE_PT_rigid_body_world)
_register_elm(bl_ui.properties_scene.SCENE_PT_rigid_body_cache)
_register_elm(bl_ui.properties_scene.SCENE_PT_rigid_body_field_weights)

_register_elm(bl_ui.properties_scene.SCENE_PT_custom_props)

_register_elm(bl_ui.properties_world.WORLD_PT_context_world, required=True)

_register_elm(bl_ui.properties_material.MATERIAL_PT_preview)
_register_elm(bl_ui.properties_texture.TEXTURE_PT_preview)

_register_elm(bl_ui.properties_data_lamp.DATA_PT_context_lamp)


# Some additions to Blender panels for better allocation in context
# Use this example for such overrides
# Add output format flags to output panel
def lux_output_hints(self, context):
    if context.scene.render.engine == 'LUXRENDER_RENDER':

        # In this mode, we don't use use the regular interval write
        pipe_mode = (context.scene.luxrender_engine.export_type == 'INT' and
                     not context.scene.luxrender_engine.write_files)

        # in this case, none of these buttons do anything, so don't even bother drawing the label
        if not pipe_mode:
            col = self.layout.column()
            col.label("LuxRender Output Formats")
        row = self.layout.row()
        if not pipe_mode:
            row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "write_png", text="PNG")

            if context.scene.camera.data.luxrender_camera.luxrender_film.write_png:
                row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "write_png_16bit",
                         text="Use 16bit PNG")

            row = self.layout.row()
            row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "write_tga", text="TARGA")
            row = self.layout.row()
            row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "write_exr", text="OpenEXR")

            if context.scene.camera.data.luxrender_camera.luxrender_film.write_exr:
                row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "write_exr_applyimaging",
                         text="Tonemap EXR")
                row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "write_exr_halftype",
                         text="Use 16bit EXR")
                row = self.layout.row()
                row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "write_exr_compressiontype",
                         text="EXR Compression")

            if context.scene.camera.data.luxrender_camera.luxrender_film.write_tga or \
                    context.scene.camera.data.luxrender_camera.luxrender_film.write_exr:
                row = self.layout.row()
                row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "write_zbuf",
                         text="Enable Z-Buffer")

                if context.scene.camera.data.luxrender_camera.luxrender_film.write_zbuf:
                    row = self.layout.row()
                    row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "zbuf_normalization",
                             text="Z-Buffer Normalization")

            row = self.layout.row()
            row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "write_flm", text="Write FLM")

            if context.scene.camera.data.luxrender_camera.luxrender_film.write_flm:
                row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "restart_flm", text="Restart FLM")
                row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "write_flm_direct",
                         text="Write FLM Directly")
        row = self.layout.row()

        # Integrated imaging always with premul named according to Blender usage
        row.prop(context.scene.camera.data.luxrender_camera.luxrender_film, "output_alpha",
                 text="Transparent Background")


_register_elm(bl_ui.properties_render.RENDER_PT_output.append(lux_output_hints))


# Add view buttons for viewcontrol to preview panels
def lux_use_alternate_matview(self, context):
    if context.scene.render.engine == 'LUXRENDER_RENDER':
        row = self.layout.row()
        row.prop(context.scene.luxrender_world, "preview_object_size", text="Size")
        row.prop(context.material.luxrender_material, "preview_zoom", text="Zoom")
        if context.material.preview_render_type == 'FLAT':
            row.prop(context.material.luxrender_material, "mat_preview_flip_xz", text="Flip XZ")


_register_elm(bl_ui.properties_material.MATERIAL_PT_preview.append(lux_use_alternate_matview))


def lux_use_alternate_texview(self, context):
    if context.scene.render.engine == 'LUXRENDER_RENDER':
        row = self.layout.row()
        row.prop(context.scene.luxrender_world, "preview_object_size", text="Size")
        row.prop(context.material.luxrender_material, "preview_zoom", text="Zoom")
        if context.material.preview_render_type == 'FLAT':
            row.prop(context.material.luxrender_material, "mat_preview_flip_xz", text="Flip XZ")


_register_elm(bl_ui.properties_texture.TEXTURE_PT_preview.append(lux_use_alternate_texview))


# Add use_clipping button to lens panel
def lux_use_clipping(self, context):
    if context.scene.render.engine == 'LUXRENDER_RENDER':

        self.layout.split().column().prop(context.camera.luxrender_camera, "use_clipping", text="Export Clipping")


_register_elm(bl_ui.properties_data_camera.DATA_PT_lens.append(lux_use_clipping))


# Add lux dof elements to blender dof panel
def lux_use_dof(self, context):
    if context.scene.render.engine == 'LUXRENDER_RENDER':
        row = self.layout.row()

        row.prop(context.camera.luxrender_camera, "use_dof", text="Use Depth of Field")
        if context.camera.luxrender_camera.use_dof:
            row.prop(context.camera.luxrender_camera, "autofocus", text="Auto Focus")

            row = self.layout.row()
            row.prop(context.camera.luxrender_camera, "blades", text="Blades")

            row = self.layout.row(align=True)
            row.prop(context.camera.luxrender_camera, "distribution", text="Distribution")
            row.prop(context.camera.luxrender_camera, "power", text="Power")


_register_elm(bl_ui.properties_data_camera.DATA_PT_camera_dof.append(lux_use_dof))


# Add options by render image/anim buttons
def render_start_options(self, context):
    if context.scene.render.engine == 'LUXRENDER_RENDER':
        col = self.layout.column()
        row = self.layout.row()

        col.prop(context.scene.luxrender_engine, "selected_luxrender_api", text="LuxRender API")

        if not UseLuxCore():
            col.prop(context.scene.luxrender_engine, "export_type", text="Export Type")
            if context.scene.luxrender_engine.export_type == 'EXT':
                col.prop(context.scene.luxrender_engine, "binary_name", text="Render Using")
            if context.scene.luxrender_engine.export_type == 'INT':
                row.prop(context.scene.luxrender_engine, "write_files", text="Write to Disk")
                row.prop(context.scene.luxrender_engine, "integratedimaging", text="Integrated Imaging")


_register_elm(bl_ui.properties_render.RENDER_PT_render.append(render_start_options))


# Add standard Blender elements for legacy texture editor
@classmethod
def blender_texture_poll(cls, context):
    tex = context.texture
    show = tex and ((tex.type == cls.tex_type and not tex.use_nodes) and
                    (context.scene.render.engine in cls.COMPAT_ENGINES))

    if context.scene.render.engine == 'LUXRENDER_RENDER':
        show = show and tex.luxrender_texture.type == 'BLENDER'

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

def lux_texture_chooser(self, context):
    if context.scene.render.engine == 'LUXRENDER_RENDER':
        self.layout.separator()
        row = self.layout.row(align=True)
        if context.texture:
            row.label('LuxRender type')
            row.menu('TEXTURE_MT_luxrender_type', text=context.texture.luxrender_texture.type_label)

            if UseLuxCore():
                self.layout.separator()
                self.layout.prop(context.texture, 'use_color_ramp', text='Use Color Ramp')
                if context.texture.use_color_ramp:
                    self.layout.template_color_ramp(context.texture, 'color_ramp', expand=True)

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
compatible("properties_data_camera")
compatible("properties_particle")
compatible("properties_data_speaker")

# To draw the preview pause button
def DrawButtonPause(self, context):
    layout = self.layout
    scene = context.scene

    if scene.render.engine == "LUXRENDER_RENDER":
        view = context.space_data

        if view.viewport_shade == "RENDERED":
            layout.prop(scene.luxrender_engine, "preview_stop", icon="PAUSE", text="")


_register_elm(bpy.types.VIEW3D_HT_header.append(DrawButtonPause))


@LuxRenderAddon.addon_register_class
class RENDERENGINE_luxrender(bpy.types.RenderEngine):
    """
    LuxRender Engine Exporter/Integration class
    """

    bl_idname = 'LUXRENDER_RENDER'
    bl_label = 'LuxRender'
    bl_use_preview = True
    bl_use_texture_preview = True

    render_lock = threading.Lock()

    def render(self, scene):
        """
        scene:  bpy.types.Scene

        Export the given scene to LuxRender.
        Choose from one of several methods depending on what needs to be rendered.

        Returns None
        """

        with RENDERENGINE_luxrender.render_lock:  # just render one thing at a time
            if scene is None:
                LuxLog('ERROR: Scene to render is not valid')
                return

            if UseLuxCore():
                self.luxcore_render(scene)
            else:
                self.luxrender_render(scene)

    def view_update(self, context):
        if UseLuxCore():
            self.luxcore_view_update(context)
        else:
            self.update_stats('ERROR: Viewport rendering is only available when API 2.x is selected!', '')

    def view_draw(self, context):
        if UseLuxCore():
            self.luxcore_view_draw(context)

    ############################################################################
    #
    # LuxRender classic API
    #
    ############################################################################

    def luxrender_render(self, scene):
        prev_cwd = os.getcwd()
        try:
            self.LuxManager = None
            self.render_update_timer = None
            self.output_dir = efutil.temp_directory()
            self.output_file = 'default.png'

            if scene.name == 'preview':
                self.luxrender_render_preview(scene)
                return

            if scene.display_settings.display_device != "sRGB":
                LuxLog('WARNING: Colour Management not set to sRGB, render results may look too dark.')

            api_type, write_files = self.set_export_path(scene)

            os.chdir(efutil.export_path)

            is_animation = hasattr(self, 'is_animation') and self.is_animation
            make_queue = scene.luxrender_engine.export_type == 'EXT' and \
                         scene.luxrender_engine.binary_name == 'luxrender' and write_files

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
                self.LuxManager = LuxManager.GetActive()
                self.LuxManager.lux_context.worldEnd()
                with open(queue_file, 'a') as qf:
                    qf.write("%s\n" % exported_file)

                if scene.frame_current == scene.frame_end:
                    # run the queue
                    self.render_queue(scene, queue_file)
            else:
                self.render_start(scene)

        except Exception as err:
            LuxLog('%s' % err)
            self.report({'ERROR'}, '%s' % err)

        os.chdir(prev_cwd)

    def luxrender_render_preview(self, scene):
        if sys.platform == 'darwin':
            self.output_dir = efutil.filesystem_path(bpy.app.tempdir)
        else:
            self.output_dir = efutil.temp_directory()

        if self.output_dir[-1] != '/':
            self.output_dir += '/'

        efutil.export_path = self.output_dir

        from ..outputs.pure_api import PYLUX_AVAILABLE

        if not PYLUX_AVAILABLE:
            LuxLog('ERROR: Material previews require pylux')
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

        # TODO: scene setup based on PREVIEW_TYPE

        # Find the materials attached to the likely preview object
        likely_materials = objects_mats[preview_objects[0]]
        if len(likely_materials) < 1:
            print('no preview materials')
            return

        pm = likely_materials[0]
        pt = None
        LuxLog('Rendering material preview: %s' % pm.name)

        if preview_type == 'TEXTURE':
            pt = pm.active_texture

        LM = LuxManager(
            scene.name,
            api_type='API',
        )
        LuxManager.SetCurrentScene(scene)
        LuxManager.SetActive(LM)

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

            xres, yres = scene.camera.data.luxrender_camera.luxrender_film.resolution(scene)

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
                if self.test_break() or bpy.context.scene.render.engine != 'LUXRENDER_RENDER':
                    raise Exception('Render interrupted')

                # progressively update the preview
                time.sleep(0.2)  # safety-sleep

                if preview_context.getAttribute('renderer_statistics', 'samplesPerPixel') > 6:
                    if preview_type == 'TEXTURE':
                        interruptible_sleep(0.8)  # reduce update to every 1.0 sec until haltthreshold kills the render
                    else:
                        interruptible_sleep(1.8)  # reduce update to every 2.0 sec until haltthreshold kills the render

                preview_context.updateStatisticsWindow()
                LuxLog('Updating preview (%ix%i - %s)' % (xres, yres,
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
            LuxLog('Preview aborted: %s' % exc)

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

        if scene.luxrender_engine.export_type == 'INT':
            write_files = scene.luxrender_engine.write_files
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

        # Pre-allocate the LuxManager so that we can set up the network servers before export
        LM = LuxManager(
            scene.name,
            api_type=api_type,
        )
        LuxManager.SetActive(LM)

        if scene.luxrender_engine.export_type == 'INT':
            # Set up networking before export so that we get better server usage
            if scene.luxrender_networking.use_network_servers and scene.luxrender_networking.servers:
                LM.lux_context.setNetworkServerUpdateInterval(scene.luxrender_networking.serverinterval)
                for server in scene.luxrender_networking.servers.split(','):
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
        if scene.camera.data.luxrender_camera.luxrender_film.write_png:
            self.output_file = efutil.path_relative_to_export(
                '%s/%s.png' % (self.output_dir, output_filename)
            )
        elif scene.camera.data.luxrender_camera.luxrender_film.write_tga:
            self.output_file = efutil.path_relative_to_export(
                '%s/%s.tga' % (self.output_dir, output_filename)
            )
        elif scene.camera.data.luxrender_camera.luxrender_film.write_exr:
            self.output_file = efutil.path_relative_to_export(
                '%s/%s.exr' % (self.output_dir, output_filename)
            )

        return "%s.lxs" % output_filename

    def rendering_behaviour(self, scene):
        internal = (scene.luxrender_engine.export_type in ['INT'])
        write_files = scene.luxrender_engine.write_files and (scene.luxrender_engine.export_type in ['INT', 'EXT'])
        render = scene.luxrender_engine.render

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

            LuxLog('Launching Queue: %s' % cmd_args)
            # LuxLog(' in %s' % self.outout_dir)
            luxrender_process = subprocess.Popen(cmd_args, cwd=self.output_dir)

    def get_process_args(self, scene, start_rendering):
        config_updates = {
            'auto_start': start_rendering
        }

        luxrender_path = efutil.filesystem_path(efutil.find_config_value(
                              'luxrender', 'defaults', 'install_path', ''))

        print('luxrender_path: ', luxrender_path)

        if not luxrender_path:
            return ['']

        if luxrender_path[-1] != '/':
            luxrender_path += '/'

        if sys.platform == 'darwin':
            # Get binary from OSX bundle
            luxrender_path += 'LuxRender.app/Contents/MacOS/%s' % scene.luxrender_engine.binary_name
            if not os.path.exists(luxrender_path):
                LuxLog('LuxRender not found at path: %s' % luxrender_path, ', trying default LuxRender location')
                luxrender_path = '/Applications/LuxRender/LuxRender.app/Contents/MacOS/%s' % \
                                 scene.luxrender_engine.binary_name  # try fallback to default installation path

        elif sys.platform == 'win32':
            luxrender_path += '%s.exe' % scene.luxrender_engine.binary_name
        else:
            luxrender_path += scene.luxrender_engine.binary_name

        if not os.path.exists(luxrender_path):
            raise Exception('LuxRender not found at path: %s' % luxrender_path)

        cmd_args = [luxrender_path]

        # set log verbosity
        if scene.luxrender_engine.log_verbosity != 'default':
            cmd_args.append('--' + scene.luxrender_engine.log_verbosity)

        # Epsilon values if any
        if scene.luxrender_engine.binary_name != 'luxvr':
            if scene.luxrender_engine.min_epsilon:
                cmd_args.append('--minepsilon=%.8f' % scene.luxrender_engine.min_epsilon)
            if scene.luxrender_engine.max_epsilon:
                cmd_args.append('--maxepsilon=%.8f' % scene.luxrender_engine.max_epsilon)

        if scene.luxrender_engine.binary_name == 'luxrender':
            # Copy the GUI log to the console
            cmd_args.append('--logconsole')

        # Set number of threads for external processes
        if not scene.luxrender_engine.threads_auto:
            cmd_args.append('--threads=%i' % scene.luxrender_engine.threads)

        # Set fixed seeds, if enabled
        if scene.luxrender_engine.fixed_seed:
            cmd_args.append('--fixedseed')

        if scene.luxrender_networking.use_network_servers and scene.luxrender_networking.servers:
            for server in scene.luxrender_networking.servers.split(','):
                cmd_args.append('--useserver')
                cmd_args.append(server.strip())

            cmd_args.append('--serverinterval')
            cmd_args.append('%i' % scene.luxrender_networking.serverinterval)

            config_updates['servers'] = scene.luxrender_networking.servers
            config_updates['serverinterval'] = '%i' % scene.luxrender_networking.serverinterval

        config_updates['use_network_servers'] = scene.luxrender_networking.use_network_servers

        # Save changed config items and then launch Lux

        try:
            for k, v in config_updates.items():
                efutil.write_config_value('luxrender', 'defaults', k, v)
        except Exception as err:
            LuxLog('WARNING: Saving LuxRender config failed, please set your user scripts dir: %s' % err)

        return cmd_args

    def render_start(self, scene):
        self.LuxManager = LuxManager.GetActive()

        # Remove previous rendering, to prevent loading old data
        # if the update timer fires before the image is written
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        internal, start_rendering, parse, worldEnd = self.rendering_behaviour(scene)

        if self.LuxManager.lux_context.API_TYPE == 'FILE':
            fn = self.LuxManager.lux_context.file_names[0]
            self.LuxManager.lux_context.worldEnd()
            if parse:
                # file_api.parse() creates a real pylux context. we must replace
                # LuxManager's context with that one so that the running renderer
                # can be controlled.
                ctx = self.LuxManager.lux_context.parse(fn, True)
                self.LuxManager.lux_context = ctx
                self.LuxManager.stats_thread.LocalStorage['lux_context'] = ctx
                self.LuxManager.fb_thread.LocalStorage['lux_context'] = ctx
        elif worldEnd:
            self.LuxManager.lux_context.worldEnd()

        # Begin rendering
        if start_rendering:
            LuxLog('Starting LuxRender')
            if internal:

                self.LuxManager.lux_context.logVerbosity(scene.luxrender_engine.log_verbosity)

                self.update_stats('', 'LuxRender: Building %s' % scene.luxrender_accelerator.accelerator)
                self.LuxManager.start()

                self.LuxManager.fb_thread.LocalStorage['integratedimaging'] = scene.luxrender_engine.integratedimaging

                # Update the image from disk only as often as it is written
                self.LuxManager.fb_thread.set_kick_period(
                    scene.camera.data.luxrender_camera.luxrender_film.internal_updateinterval)

                # Start the stats and framebuffer threads and add additional threads to Lux renderer
                self.LuxManager.start_worker_threads(self)

                if scene.luxrender_engine.threads_auto:
                    try:
                        thread_count = multiprocessing.cpu_count()
                    except:
                        thread_count = 1
                else:
                    thread_count = scene.luxrender_engine.threads

                # Run rendering with specified number of threads
                for i in range(thread_count - 1):
                    self.LuxManager.lux_context.addThread()

                while self.LuxManager.started:
                    self.render_update_timer = threading.Timer(1, self.stats_timer)
                    self.render_update_timer.start()
                    if self.render_update_timer.isAlive():
                        self.render_update_timer.join()
            else:
                cmd_args = self.get_process_args(scene, start_rendering)

                cmd_args.append(fn.replace('//', '/'))

                LuxLog('Launching: %s' % cmd_args)
                # LuxLog(' in %s' % self.outout_dir)
                luxrender_process = subprocess.Popen(cmd_args, cwd=self.output_dir)

                if not (
                        scene.luxrender_engine.binary_name == 'luxrender' and not
                        scene.luxrender_engine.monitor_external):
                    framebuffer_thread = LuxFilmDisplay({
                        'resolution': scene.camera.data.luxrender_camera.luxrender_film.resolution(scene),
                        'RE': self,
                    })
                    framebuffer_thread.set_kick_period(scene.camera.data.luxrender_camera.luxrender_film.writeinterval)
                    framebuffer_thread.start()
                    while luxrender_process.poll() is None and not self.test_break():
                        self.render_update_timer = threading.Timer(1, self.process_wait_timer)
                        self.render_update_timer.start()
                        if self.render_update_timer.isAlive():
                            self.render_update_timer.join()

                    # If we exit the wait loop (user cancelled) and luxconsole is still running, then send SIGINT
                    if luxrender_process.poll() is None and scene.luxrender_engine.binary_name != 'luxrender':
                        # Use SIGTERM because that's the only one supported on Windows
                        luxrender_process.send_signal(subprocess.signal.SIGTERM)

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

        LC = self.LuxManager.lux_context

        self.update_stats('', 'LuxRender: Rendering %s' % self.LuxManager.stats_thread.stats_string)

        if hasattr(self, 'update_progress') and LC.getAttribute('renderer_statistics', 'percentComplete') > 0:
            prg = LC.getAttribute('renderer_statistics', 'percentComplete') / 100.0
            self.update_progress(prg)

        if self.test_break() or \
                        LC.statistics('filmIsReady') == 1.0 or \
                        LC.statistics('terminated') == 1.0 or \
                        LC.getAttribute('film', 'enoughSamples'):
            self.LuxManager.reset()
            self.update_stats('', '')

    ############################################################################
    #
    # LuxCore code
    #
    ############################################################################

    def set_export_path_luxcore(self, scene):
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

        efutil.export_path = self.output_dir

    def PrintStats(self, lcConfig, stats):
        lc_engine = lcConfig.GetProperties().Get('renderengine.type').GetString()

        if lc_engine in ['BIASPATHCPU', 'BIASPATHOCL']:
            converged = stats.Get('stats.biaspath.tiles.converged.count').GetInt()
            notconverged = stats.Get('stats.biaspath.tiles.notconverged.count').GetInt()
            pending = stats.Get('stats.biaspath.tiles.pending.count').GetInt()

            LuxLog('[Elapsed time: %3d][Pass %4d][Convergence %d/%d][Avg. samples/sec % 3.2fM on %.1fK tris]' % (
                stats.Get('stats.renderengine.time').GetFloat(),
                stats.Get('stats.renderengine.pass').GetInt(),
                converged, converged + notconverged + pending,
                (stats.Get('stats.renderengine.total.samplesec').GetFloat() / 1000000.0),
                (stats.Get('stats.dataset.trianglecount').GetFloat() / 1000.0)))
        else:
            LuxLog('[Elapsed time: %3d][Samples %4d][Avg. samples/sec % 3.2fM on %.1fK tris]' % (
                stats.Get('stats.renderengine.time').GetFloat(),
                stats.Get('stats.renderengine.pass').GetInt(),
                (stats.Get('stats.renderengine.total.samplesec').GetFloat() / 1000000.0),
                (stats.Get('stats.dataset.trianglecount').GetFloat() / 1000.0)))

    mem_peak = 0

    def CreateBlenderStats(self, lcConfig, stats, scene, realtime_preview = False, time_until_update = -1.0):
        """
        Returns: string of formatted statistics
        """

        engine = lcConfig.GetProperties().Get('renderengine.type').GetString()
        engine_dict = {
            'PATHCPU' : 'Path',
            'PATHOCL' : 'Path OpenCL',
            'BIASPATHCPU' : 'Biased Path',
            'BIASPATHOCL' : 'Biased Path OpenCL',
            'BIDIRCPU' : 'Bidir',
            'BIDIRVMCPU' : 'BidirVCM'
        }
        
        sampler = lcConfig.GetProperties().Get('sampler.type').GetString()
        sampler_dict = {
            'RANDOM' : 'Random',
            'SOBOL' : 'Sobol',
            'METROPOLIS' : 'Metropolis'
        }

        if realtime_preview:
            halt_samples = scene.luxcore_realtimesettings.halt_samples
            halt_time = scene.luxcore_realtimesettings.halt_time
        else:
            halt_samples = scene.luxcore_enginesettings.halt_samples
            halt_time = scene.luxcore_enginesettings.halt_time

        # Progress
        progress_time = 0.0
        progress_samples = 0.0
        progress_tiles = 0.0

        stats_list = []

        # Time stats
        time_running = stats.Get('stats.renderengine.time').GetFloat()
        # Add time stats for realtime preview because Blender doesn't display it there
        if realtime_preview and halt_time == 0:
            stats_list.append('Time: %.1fs' % (time_running))
        # For final renderings, only display time if it is set as halt condition
        elif halt_time != 0:
            stats_list.append('Time: %.1fs/%ds' % (time_running, halt_time))
            if not realtime_preview:
                progress_time = time_running / halt_time

        # Samples/Passes stats
        samples_count = stats.Get('stats.renderengine.pass').GetInt()
        samples_term = 'Pass' if engine in ['BIASPATHCPU', 'BIASPATHOCL'] else 'Samples'
        if halt_samples != 0:
            stats_list.append('%s: %d/%d' % (samples_term, samples_count, halt_samples))
            if not realtime_preview:
                progress_samples = samples_count / halt_samples
        else:
            stats_list.append('%s: %d' % (samples_term, samples_count))

        # Tile stats
        if engine in ['BIASPATHCPU', 'BIASPATHOCL']:
            converged = stats.Get('stats.biaspath.tiles.converged.count').GetInt()
            notconverged = stats.Get('stats.biaspath.tiles.notconverged.count').GetInt()
            pending = stats.Get('stats.biaspath.tiles.pending.count').GetInt()

            tiles_amount = converged + notconverged + pending
            stats_list.append('Tiles: %d/%d Converged' % (converged, tiles_amount))
            progress_tiles = converged / tiles_amount

        # Samples per second
        stats_list.append('Samples/Sec %3.2fM' % (stats.Get('stats.renderengine.total.samplesec').GetFloat() / 1000000))

        # Memory usage
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

        if str.endswith(engine, 'OCL'):
            stats_list.append('Memory: %dM/%dM' % (used_memory, max_memory))

        # Engine and sampler info
        engine_info = engine_dict[engine]
        if not engine in ['BIASPATHCPU', 'BIASPATHOCL']:
            engine_info += ' + ' + sampler_dict[sampler]
        stats_list.append(engine_info)

        # Show remaining time until next film update (final render only)
        if not realtime_preview and time_until_update > 0.0:
            stats_list.append('Next update in %ds' % math.ceil(time_until_update))
        elif time_until_update != -1:
            stats_list.append('Updating preview...')
                
        # Update progressbar (final render only)
        if not realtime_preview:
            progress = max([progress_time, progress_samples, progress_tiles])
            self.update_progress(progress)

        # Pass memory usage information to Blender
        if str.endswith(engine, 'OCL'):
            self.update_memory_stats(used_memory, self.mem_peak)

        return ' | '.join(stats_list)

    def haltConditionMet(self, scene, stats, realtime_preview = False):
        """
        Checks if any halt conditions are met
        """
        if realtime_preview:
            halt_samples = scene.luxcore_realtimesettings.halt_samples
            halt_time = scene.luxcore_realtimesettings.halt_time
        else:
            halt_samples = scene.luxcore_enginesettings.halt_samples
            halt_time = scene.luxcore_enginesettings.halt_time
        
        rendered_samples = stats.Get('stats.renderengine.pass').GetInt()
        rendered_time = stats.Get('stats.renderengine.time').GetFloat()
            
        return (halt_samples != 0 and rendered_samples >= halt_samples) or (
                halt_time != 0 and rendered_time >= halt_time) or (
                stats.Get('stats.renderengine.convergence').GetFloat() == 1.0)

    def normalizeChannel(self, channel_buffer):
        isInf = math.isinf

        # find max value
        maxValue = 0.0
        for elem in channel_buffer:
            if elem > maxValue and not isInf(elem):
                maxValue = elem

        if maxValue > 0.0:
            for i in range(0, len(channel_buffer)):
                channel_buffer[i] = channel_buffer[i] / maxValue

    def convertChannelToImage(self, lcSession, scene, filmWidth, filmHeight, channelType, saveToDisk,
                              normalize = False, buffer_id = -1):
        """
        Convert AOVs to Blender images
        """
        from ..outputs.luxcore_api import pyluxcore

        # Structure: {channelType: [pyluxcoreType, is HDR, arrayDepth]}
        attributes = {
                'RGB': [pyluxcore.FilmOutputType.RGB, True, 3],
                'RGBA': [pyluxcore.FilmOutputType.RGBA, True, 4],
                'RGB_TONEMAPPED': [pyluxcore.FilmOutputType.RGB_TONEMAPPED, False, 3],
                'RGBA_TONEMAPPED': [pyluxcore.FilmOutputType.RGBA_TONEMAPPED, False, 4],
                'ALPHA': [pyluxcore.FilmOutputType.ALPHA, False, 1],
                'DEPTH': [pyluxcore.FilmOutputType.DEPTH, True, 1],
                'POSITION': [pyluxcore.FilmOutputType.POSITION, True, 3],
                'GEOMETRY_NORMAL': [pyluxcore.FilmOutputType.GEOMETRY_NORMAL, True, 3],
                'SHADING_NORMAL': [pyluxcore.FilmOutputType.SHADING_NORMAL, True, 3],
                'MATERIAL_ID': [pyluxcore.FilmOutputType.MATERIAL_ID, False, 1],
                'DIRECT_DIFFUSE': [pyluxcore.FilmOutputType.DIRECT_DIFFUSE, True, 3],
                'DIRECT_GLOSSY': [pyluxcore.FilmOutputType.DIRECT_GLOSSY, True, 3],
                'EMISSION': [pyluxcore.FilmOutputType.EMISSION, True, 3],
                'INDIRECT_DIFFUSE': [pyluxcore.FilmOutputType.INDIRECT_DIFFUSE, True, 3],
                'INDIRECT_GLOSSY': [pyluxcore.FilmOutputType.INDIRECT_GLOSSY, True, 3],
                'INDIRECT_SPECULAR': [pyluxcore.FilmOutputType.INDIRECT_SPECULAR, True, 3],
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
        arrayType = 'I' if channelType == 'MATERIAL_ID' else 'f'
        arrayInitValue = 0 if channelType == 'MATERIAL_ID' else 0.0
        arrayDepth = attributes[channelType][2]

        # show info about imported passes
        message = 'Pass: ' + channelType
        if buffer_id != -1:
            message += ' ID: ' + str(buffer_id)
        self.update_stats('Importing AOV passes into Blender...', message)
        LuxLog(message)

        # raw channel buffer
        channel_buffer = array.array(arrayType, [arrayInitValue] * (filmWidth * filmHeight * arrayDepth))
        # buffer for converted array (to RGBA)
        channel_buffer_converted = []

        if channelType == 'MATERIAL_ID':
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

            # spread value to RGBA format

            if arrayDepth == 1:
                if getattr(pyluxcore, 'ConvertFilmChannelOutput_1xFloat_To_4xFloatList', None) is not None:
                    channel_buffer_converted = pyluxcore.ConvertFilmChannelOutput_1xFloat_To_4xFloatList(filmWidth,
                                                                                                         filmHeight,
                                                                                                         channel_buffer,
                                                                                                         normalize)
                else:
                    # normalize channel_buffer values (map to 0..1 range)
                    if normalize:
                        self.normalizeChannel(channel_buffer)
                    for elem in channel_buffer:
                        channel_buffer_converted.extend([elem, elem, elem, 1.0])

            # UV channel, just add 0.0 for B and 1.0 for A components
            elif arrayDepth == 2:
                if getattr(pyluxcore, 'ConvertFilmChannelOutput_2xFloat_To_4xFloatList', None) is not None:
                    channel_buffer_converted = pyluxcore.ConvertFilmChannelOutput_2xFloat_To_4xFloatList(filmWidth,
                                                                                                         filmHeight,
                                                                                                         channel_buffer,
                                                                                                         normalize)
                else:
                    # normalize channel_buffer values (map to 0..1 range)
                    if normalize:
                        self.normalizeChannel(channel_buffer)
                    i = 0
                    while i < len(channel_buffer):
                        channel_buffer_converted.extend([channel_buffer[i], channel_buffer[i + 1], 0.0, 1.0])
                        i += 2

            # RGB channels: just add 1.0 as alpha component
            elif arrayDepth == 3:
                if getattr(pyluxcore, 'ConvertFilmChannelOutput_3xFloat_To_4xFloatList', None) is not None:
                    channel_buffer_converted = pyluxcore.ConvertFilmChannelOutput_3xFloat_To_4xFloatList(filmWidth,
                                                                                                         filmHeight,
                                                                                                         channel_buffer,
                                                                                                         normalize)
                else:
                    # normalize channel_buffer values (map to 0..1 range)
                    if normalize:
                        self.normalizeChannel(channel_buffer)
                    i = 0
                    while i < len(channel_buffer):
                        channel_buffer_converted.extend(
                            [channel_buffer[i], channel_buffer[i + 1], channel_buffer[i + 2], 1.0])
                        i += 3

            # RGBA channels: just copy the list
            else:
                channel_buffer_converted = channel_buffer

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
            imageWidth, imageHeight = scene.camera.data.luxrender_camera.luxrender_film.resolution(scene)
            
            # construct an empty Blender image
            blenderImage = bpy.data.images.new(imageName, alpha = True, 
                                                width = imageWidth, height = imageHeight, float_buffer = use_hdr)
            
            # copy the buffer content to the right position in the Blender image
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
        
        if saveToDisk:
            blenderImage.save()

    def draw_tiles(self, scene, stats, imageBuffer, filmWidth, filmHeight):
        """
        draws tile outlines directly into the imageBuffer
        
        scene: Blender scene object
        stats: LuxCore stats (from LuxCore session)
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
        count_converged = stats.Get('stats.biaspath.tiles.converged.count').GetInt()
        count_notconverged = stats.Get('stats.biaspath.tiles.notconverged.count').GetInt()
        count_pending = stats.Get('stats.biaspath.tiles.pending.count').GetInt()
        
        if count_converged > 0 and show_converged:
            coords_converged = stats.Get('stats.biaspath.tiles.converged.coords').GetInts()
            color_green = (0.0, 1.0, 0.0, 1.0)
            draw_tile_type(count_converged, coords_converged, color_green)
            
        if count_notconverged > 0 and show_unconverged:
            coords_notconverged = stats.Get('stats.biaspath.tiles.notconverged.coords').GetInts()
            color_red = (1.0, 0.0, 0.0, 1.0)
            draw_tile_type(count_notconverged, coords_notconverged, color_red)
            
        if count_pending > 0 and show_pending:
            coords_pending = stats.Get('stats.biaspath.tiles.pending.coords').GetInts()
            color_yellow = (1.0, 1.0, 0.0, 1.0)
            draw_tile_type(count_pending, coords_pending, color_yellow)

    def luxcore_render(self, scene):
        if self.is_preview:
            self.luxcore_render_preview(scene)
            return

        # LuxCore libs
        if not PYLUXCORE_AVAILABLE:
            LuxLog('ERROR: LuxCore rendering requires pyluxcore')
            self.report({'ERROR'}, 'LuxCore rendering requires pyluxcore')
            return
        from ..outputs.luxcore_api import pyluxcore

        try:
            self.set_export_path_luxcore(scene)
        
            filmWidth, filmHeight = self.get_film_size(scene)

            luxcore_exporter = LuxCoreExporter(scene, self)
            luxcore_config = luxcore_exporter.convert(filmWidth, filmHeight)
            luxcore_session = pyluxcore.RenderSession(luxcore_config)

            # maybe export was cancelled by user, don't start the rendering with an incomplete scene then
            if self.test_break():
                return
            
            imageBufferFloat = array.array('f', [0.0] * (filmWidth * filmHeight * 3))

            # Start the rendering
            luxcore_session.Start()

            # Immediately end the rendering if 'FILESAVER' engine is used
            if scene.luxcore_translatorsettings.use_filesaver:
                luxcore_session.Stop()
                return

            imagepipeline_settings = scene.camera.data.luxrender_camera.luxcore_imagepipeline_settings
            startTime = time.time()
            lastImageDisplay = startTime
            done = False

            # Magic formula to compute optimal display interval (found through testing)
            display_interval = float(filmWidth * filmHeight) / 852272.0 * 1.1
            LuxLog('Recommended minimum display interval: %.1fs' % display_interval)

            while not self.test_break() and not done:
                time.sleep(0.2)

                now = time.time()
                timeSinceDisplay = now - lastImageDisplay
                elapsedTimeSinceStart = now - startTime

                # Use user-definde display interval after the first 15 seconds
                if elapsedTimeSinceStart > 15.0:
                    display_interval = imagepipeline_settings.displayinterval
                    
                # Update statistics
                luxcore_session.UpdateStats()
                stats = luxcore_session.GetStats()
                blender_stats = self.CreateBlenderStats(luxcore_config, stats, scene,
                        time_until_update = display_interval - timeSinceDisplay)
                self.update_stats('Rendering...', blender_stats)

                # check if any halt conditions are met
                done = self.haltConditionMet(scene, stats)

                if timeSinceDisplay > display_interval:
                    #display_start = time.time()

                    # Update the image
                    luxcore_session.GetFilm().GetOutputFloat(pyluxcore.FilmOutputType.RGB_TONEMAPPED, imageBufferFloat)

                    # Here we write the pixel values to the RenderResult
                    result = self.begin_result(0, 0, filmWidth, filmHeight)
                    layer = result.layers[0] if bpy.app.version < (2, 74, 4 ) else result.layers[0].passes[0]

                    if (scene.luxcore_enginesettings.renderengine_type in ['BIASPATHCPU', 'BIASPATHOCL'] and
                            scene.luxcore_tile_highlighting.use_tile_highlighting):
                        # use a temp image because layer.rect does not support list slicing
                        tempImage = pyluxcore.ConvertFilmChannelOutput_3xFloat_To_3xFloatList(filmWidth,
                                                                                              filmHeight,
                                                                                              imageBufferFloat)
                        # draw tile outlines
                        self.draw_tiles(scene, stats, tempImage, filmWidth, filmHeight)
                        layer.rect = tempImage
                    else:
                        layer.rect = pyluxcore.ConvertFilmChannelOutput_3xFloat_To_3xFloatList(filmWidth,
                                                                                               filmHeight,
                                                                                               imageBufferFloat)

                    self.end_result(result)

                    lastImageDisplay = now
                    #LuxLog('Imagebuffer update took %.1fs' % (time.time() - display_start))

            # Update the image
            luxcore_session.GetFilm().GetOutputFloat(pyluxcore.FilmOutputType.RGB_TONEMAPPED, imageBufferFloat)
            # write final render result
            result = self.begin_result(0, 0, filmWidth, filmHeight)
            layer = result.layers[0] if bpy.app.version < (2, 74, 4 ) else result.layers[0].passes[0]
            layer.rect = pyluxcore.ConvertFilmChannelOutput_3xFloat_To_3xFloatList(filmWidth, filmHeight,
                                                                                   imageBufferFloat)
            self.end_result(result)

            luxcore_session.Stop()

            if scene.luxrender_channels.enable_aovs:
                self.import_aov_channels(scene, luxcore_session, filmWidth, filmHeight)

            LuxLog('Done.\n')
        except Exception as exc:
            LuxLog('Rendering aborted: %s' % exc)
            self.report({'ERROR'}, str(exc))
            import traceback

            traceback.print_exc()

    def get_film_size(self, scene):
        filmWidth, filmHeight = scene.camera.data.luxrender_camera.luxrender_film.resolution(scene)

        if scene.render.use_border:
            x_min, x_max, y_min, y_max = [
                scene.render.border_min_x, scene.render.border_max_x,
                scene.render.border_min_y, scene.render.border_max_y
            ]

            filmWidth = int(filmWidth * x_max - filmWidth * x_min)
            filmHeight = int(filmHeight * y_max - filmHeight * y_min)

        return filmWidth, filmHeight

    def import_aov_channels(self, scene, lcSession, filmWidth, filmHeight):
        channelCalcStartTime = time.time()
        LuxLog('Importing AOV channels into Blender...')

        channels = scene.luxrender_channels

        if channels.RGB:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'RGB', channels.saveToDisk)
        if channels.RGBA:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'RGBA', channels.saveToDisk)
        if channels.RGB_TONEMAPPED:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'RGB_TONEMAPPED', channels.saveToDisk)
        if channels.RGBA_TONEMAPPED:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'RGBA_TONEMAPPED', channels.saveToDisk)
        if channels.ALPHA:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'ALPHA', channels.saveToDisk)
        if channels.DEPTH:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'DEPTH', channels.saveToDisk,
                                       normalize = channels.normalize_DEPTH)
        if channels.POSITION:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'POSITION', channels.saveToDisk)
        if channels.GEOMETRY_NORMAL:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'GEOMETRY_NORMAL', channels.saveToDisk)
        if channels.SHADING_NORMAL:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'SHADING_NORMAL', channels.saveToDisk)
        if channels.MATERIAL_ID:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'MATERIAL_ID', channels.saveToDisk)
        if channels.DIRECT_DIFFUSE:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'DIRECT_DIFFUSE', channels.saveToDisk,
                                       normalize = channels.normalize_DIRECT_DIFFUSE)
        if channels.DIRECT_GLOSSY:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'DIRECT_GLOSSY', channels.saveToDisk,
                                       normalize = channels.normalize_DIRECT_GLOSSY)
        if channels.EMISSION:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'EMISSION', channels.saveToDisk)
        if channels.INDIRECT_DIFFUSE:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'INDIRECT_DIFFUSE', channels.saveToDisk,
                                       normalize = channels.normalize_INDIRECT_DIFFUSE)
        if channels.INDIRECT_GLOSSY:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'INDIRECT_GLOSSY', channels.saveToDisk,
                                       normalize = channels.normalize_INDIRECT_GLOSSY)
        if channels.INDIRECT_SPECULAR:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'INDIRECT_SPECULAR', channels.saveToDisk,
                                       normalize = channels.normalize_INDIRECT_SPECULAR)
        if channels.DIRECT_SHADOW_MASK:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'DIRECT_SHADOW_MASK', channels.saveToDisk)
        if channels.INDIRECT_SHADOW_MASK:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'INDIRECT_SHADOW_MASK', channels.saveToDisk)
        if channels.UV:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'UV', channels.saveToDisk)
        if channels.RAYCOUNT:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'RAYCOUNT', channels.saveToDisk,
                                       normalize = channels.normalize_RAYCOUNT)
        if channels.IRRADIANCE:
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'IRRADIANCE', channels.saveToDisk)

        props = lcSession.GetRenderConfig().GetProperties()
        # Convert all MATERIAL_ID_MASK channels
        mask_ids = set()
        for i in props.GetAllUniqueSubNames('film.outputs'):
            if props.Get(i + '.type').GetString() == 'MATERIAL_ID_MASK':
                mask_ids.add(props.Get(i + '.id').GetInt())

        for i in range(len(mask_ids)):
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'MATERIAL_ID_MASK', channels.saveToDisk, buffer_id = i)

        # Convert all BY_MATERIAL_ID channels
        ids = set()
        for i in props.GetAllUniqueSubNames('film.outputs'):
            if props.Get(i + '.type').GetString() == 'BY_MATERIAL_ID':
                ids.add(props.Get(i + '.id').GetInt())

        for i in range(len(ids)):
            self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                       'BY_MATERIAL_ID', channels.saveToDisk, buffer_id = i)

        # Convert all RADIANCE_GROUP channels
        lightgroup_count = lcSession.GetFilm().GetRadianceGroupCount()

        # don't import the standard lightgroup that contains all lights even if no groups are set
        if lightgroup_count > 1:
            for i in range(lightgroup_count):
                self.convertChannelToImage(lcSession, scene, filmWidth, filmHeight,
                                           'RADIANCE_GROUP', channels.saveToDisk, buffer_id = i)

        channelCalcTime = time.time() - channelCalcStartTime
        LuxLog('AOV conversion took %.1f seconds' % channelCalcTime)

    cached_preview_properties = ''

    def determine_preview_settings(self, scene):
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

        # TODO: scene setup based on PREVIEW_TYPE

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
        # LuxCore libs
        if not PYLUXCORE_AVAILABLE:
            LuxLog('ERROR: LuxCore preview rendering requires pyluxcore')
            return
        from ..outputs.luxcore_api import pyluxcore
        from ..export.luxcore.materialpreview import MaterialPreviewExporter

        try:
            def update_result(self, is_thumbnail, luxcore_session, imageBufferFloat, filmWidth, filmHeight):
                # Update the image
                luxcore_session.GetFilm().GetOutputFloat(pyluxcore.FilmOutputType.RGB_TONEMAPPED, imageBufferFloat)

                # Here we write the pixel values to the RenderResult
                result = self.begin_result(0, 0, filmWidth, filmHeight)
                layer = result.layers[0] if bpy.app.version < (2, 74, 4 ) else result.layers[0].passes[0]

                layer.rect = pyluxcore.ConvertFilmChannelOutput_3xFloat_To_3xFloatList(filmWidth, filmHeight,
                                                                                   imageBufferFloat)
                self.end_result(result)

            filmWidth, filmHeight = scene.camera.data.luxrender_camera.luxrender_film.resolution(scene)
            is_thumbnail = filmWidth <= 96
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
            LuxLog('Starting', preview_type, 'preview render', thumbnail_info)
            startTime = time.time()
            luxcore_session.Start()

            if is_thumbnail:
                time.sleep(0.02)
                update_result(self, is_thumbnail, luxcore_session, imageBufferFloat, filmWidth, filmHeight)
            else:
                stopTime = 6.0 if preview_type == 'MATERIAL' else 0.1
                done = False

                while not self.test_break() and time.time() - startTime < stopTime and not done:
                    time.sleep(0.1)

                    # Update statistics
                    luxcore_session.UpdateStats()
                    done = self.haltConditionMet(scene, luxcore_session.GetStats())

                    update_result(self, is_thumbnail, luxcore_session, imageBufferFloat, filmWidth, filmHeight)

            luxcore_session.Stop()
            LuxLog('Preview render done (%.2fs)' % (time.time() - startTime))
        except Exception as exc:
            LuxLog('Rendering aborted: %s' % exc)
            import traceback

            traceback.print_exc()

    ############################################################################
    # Viewport render
    ############################################################################

    luxcore_exporter = None
    viewport_render_active = False
    viewport_render_paused = False
    luxcore_session = None

    viewFilmWidth = -1
    viewFilmHeight = -1
    viewImageBufferFloat = None
    # store renderengine configuration of last update
    lastRenderSettings = ''
    lastVolumeSettings = ''
    lastHaltTime = -1
    lastHaltSamples = -1
    lastCameraSettings = ''
    lastVisibilitySettings = None
    update_counter = 0

    @staticmethod
    def begin_scene_edit():
        if RENDERENGINE_luxrender.viewport_render_active:
            if not RENDERENGINE_luxrender.viewport_render_paused:
                print('pausing viewport render')
                RENDERENGINE_luxrender.viewport_render_paused = True
                RENDERENGINE_luxrender.luxcore_session.BeginSceneEdit()

    @staticmethod
    def end_scene_edit():
        if RENDERENGINE_luxrender.viewport_render_active:
            if RENDERENGINE_luxrender.viewport_render_paused:
                print('resuming viewport render')
                RENDERENGINE_luxrender.viewport_render_paused = False
                RENDERENGINE_luxrender.luxcore_session.EndSceneEdit()

    @staticmethod
    def stop_luxcore_session():
        if RENDERENGINE_luxrender.viewport_render_active:
            print('stopping viewport render')
            RENDERENGINE_luxrender.end_scene_edit()
            RENDERENGINE_luxrender.viewport_render_active = False

            RENDERENGINE_luxrender.luxcore_session.Stop()
            RENDERENGINE_luxrender.luxcore_session = None

    
    def luxcore_view_draw(self, context):
        # LuxCore libs
        if not PYLUXCORE_AVAILABLE:
            LuxLog('ERROR: LuxCore real-time rendering requires pyluxcore')
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
        newCameraSettings = str(self.luxcore_exporter.camera_exporter.properties)

        if self.lastCameraSettings == '':
            self.lastCameraSettings = newCameraSettings
        elif self.lastCameraSettings != newCameraSettings:
            update_changes = UpdateChanges()
            update_changes.set_cause(camera = True)
            self.lastCameraSettings = newCameraSettings
            self.luxcore_view_update(context, update_changes)

        # Update statistics
        if RENDERENGINE_luxrender.viewport_render_active:
            RENDERENGINE_luxrender.luxcore_session.UpdateStats()
            stats = RENDERENGINE_luxrender.luxcore_session.GetStats()

            stop_redraw = (context.scene.luxrender_engine.preview_stop or
                    self.haltConditionMet(context.scene, stats, realtime_preview = True))

            # update statistic display in Blender
            luxcore_config = RENDERENGINE_luxrender.luxcore_session.GetRenderConfig()
            blender_stats = self.CreateBlenderStats(luxcore_config,
                                                    stats,
                                                    context.scene,
                                                    realtime_preview = True)
            if stop_redraw:
                self.update_stats('Paused', blender_stats)
            else:
                self.update_stats('Rendering', blender_stats)

            # Update the image buffer
            RENDERENGINE_luxrender.luxcore_session.GetFilm().GetOutputFloat(pyluxcore.FilmOutputType.RGB_TONEMAPPED,
                                                      self.viewImageBufferFloat)

        # Update the screen
        bufferSize = self.viewFilmWidth * self.viewFilmHeight * 3
        glBuffer = bgl.Buffer(bgl.GL_FLOAT, [bufferSize], self.viewImageBufferFloat)
        bgl.glRasterPos2i(0, 0)
        bgl.glDrawPixels(self.viewFilmWidth, self.viewFilmHeight, bgl.GL_RGB, bgl.GL_FLOAT, glBuffer)

        if stop_redraw:
            # Pause rendering
            RENDERENGINE_luxrender.begin_scene_edit()
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

            if (not RENDERENGINE_luxrender.viewport_render_active or
                    RENDERENGINE_luxrender.luxcore_session is None or
                    self.luxcore_exporter is None):
                update_changes.set_cause(startViewportRender = True)

                # LuxCoreExporter instance for viewport rendering is only created here
                self.luxcore_exporter = LuxCoreExporter(context.scene, self, True, context)

            # check if filmsize has changed
            if (self.viewFilmWidth == -1) or (self.viewFilmHeight == -1) or (
                    self.viewFilmWidth != context.region.width) or (
                    self.viewFilmHeight != context.region.height):
                update_changes.set_cause(config = True)

            if bpy.data.objects.is_updated:
                # check objects for updates
                for ob in bpy.data.objects:
                    if ob == None:
                        continue

                    if ob.is_updated_data:
                        if ob.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT']:
                            update_changes.set_cause(mesh = True)
                            update_changes.changed_objects_mesh.add(ob)
                        elif ob.type in ['LAMP']:
                            update_changes.set_cause(light = True)
                            update_changes.changed_objects_transform.add(ob)
                        elif ob.type in ['CAMERA'] and ob.name == context.scene.camera.name:
                            update_changes.set_cause(camera = True, config = True)

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
                    if mat.is_updated:
                        # only update this material
                        update_changes.changed_materials.add(mat)
                        update_changes.set_cause(materials = True)

            if bpy.data.textures.is_updated:
                for tex in bpy.data.textures:
                    if tex.is_updated:
                        for mat in tex.users_material:
                            update_changes.changed_materials.add(mat)
                            update_changes.set_cause(materials = True)

            self.luxcore_exporter.convert_camera()
            newCameraSettings = str(self.luxcore_exporter.pop_updated_scene_properties())

            if self.lastCameraSettings == '':
                self.lastCameraSettings = newCameraSettings
            elif self.lastCameraSettings != newCameraSettings:
                update_changes.set_cause(camera = True)
                self.lastCameraSettings = newCameraSettings

            # check for changes in volume configuration
            for volume in context.scene.luxrender_volumes.volumes:
                self.luxcore_exporter.convert_volume(volume)

            newVolumeSettings = str(self.luxcore_exporter.pop_updated_scene_properties())

            if self.lastVolumeSettings == '':
                self.lastVolumeSettings = newVolumeSettings
            elif self.lastVolumeSettings != newVolumeSettings:
                update_changes.set_cause(volumes = True)
                self.lastVolumeSettings = newVolumeSettings

            # check for changes in halt conditions
            newHaltTime = context.scene.luxcore_realtimesettings.halt_time
            newHaltSamples = context.scene.luxcore_realtimesettings.halt_samples

            if self.lastHaltTime != -1 and self.lastHaltSamples != -1:
                if newHaltTime > self.lastHaltTime or newHaltSamples > self.lastHaltSamples:
                    update_changes.set_cause(haltconditions = True)

            self.lastHaltTime = newHaltTime
            self.lastHaltSamples = newHaltSamples

            self.luxcore_exporter.convert_config(self.viewFilmWidth, self.viewFilmHeight)
            newRenderSettings = str(self.luxcore_exporter.config_exporter.properties)

            if self.lastRenderSettings == '':
                self.lastRenderSettings = newRenderSettings
            elif self.lastRenderSettings != newRenderSettings:
                # renderengine config has changed
                update_changes.set_cause(config = True)
                # save settings to compare with next update
                self.lastRenderSettings = newRenderSettings
        except Exception as exc:
            LuxLog('Update check failed: %s' % exc)
            self.report({'ERROR'}, str(exc))
            import traceback
            traceback.print_exc()

        return update_changes
    
    def luxcore_view_update(self, context, update_changes = None):
        # LuxCore libs
        if not PYLUXCORE_AVAILABLE:
            LuxLog('ERROR: LuxCore real-time rendering requires pyluxcore')
            return

        if self.test_break() or context.scene.luxrender_engine.preview_stop:
            print("stopping view update")
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
            print('WARNING: Update cause unknown, skipping update')

        elif update_changes.cause_haltconditions:
            pass

        elif update_changes.cause_startViewportRender:
            try:
                RENDERENGINE_luxrender.stop_luxcore_session()

                self.lastRenderSettings = ''
                self.lastVolumeSettings = ''
                self.lastHaltTime = -1
                self.lastHaltSamples = -1
                self.lastCameraSettings = ''
                self.lastVisibilitySettings = None
                self.update_counter = 0

                LuxManager.SetCurrentScene(context.scene)

                self.viewFilmWidth = context.region.width
                self.viewFilmHeight = context.region.height
                self.viewImageBufferFloat = array.array('f', [0.0] * (self.viewFilmWidth * self.viewFilmHeight * 3))

                LuxLog('Starting viewport render')

                # Export the Blender scene
                luxcore_config = self.luxcore_exporter.convert(self.viewFilmWidth, self.viewFilmHeight)
                RENDERENGINE_luxrender.luxcore_session = pyluxcore.RenderSession(luxcore_config)

                RENDERENGINE_luxrender.luxcore_session.Start()
                RENDERENGINE_luxrender.viewport_render_active = True
            except Exception as exc:
                LuxLog('View update aborted: %s' % exc)

                message = str(exc)
                if message == 'An empty DataSet can not be preprocessed':
                    # more user-friendly error message
                    message = 'The scene does not contain any meshes'

                self.update_stats('Error: ', message)

                RENDERENGINE_luxrender.stop_luxcore_session()

                import traceback
                traceback.print_exc()
        else:
            # config update
            if update_changes.cause_config:
                LuxLog('Configuration update')

                self.viewFilmWidth = context.region.width
                self.viewFilmHeight = context.region.height
                self.viewImageBufferFloat = array.array('f', [0.0] * (self.viewFilmWidth * self.viewFilmHeight * 3))

                luxcore_config = RENDERENGINE_luxrender.luxcore_session.GetRenderConfig()
                RENDERENGINE_luxrender.stop_luxcore_session()

                self.luxcore_exporter.convert_config(self.viewFilmWidth, self.viewFilmHeight)

                # change config
                luxcore_config.Parse(self.luxcore_exporter.config_properties)

                RENDERENGINE_luxrender.luxcore_session = pyluxcore.RenderSession(luxcore_config)

                RENDERENGINE_luxrender.luxcore_session.Start()
                RENDERENGINE_luxrender.viewport_render_active = True

            # begin sceneEdit
            luxcore_scene = RENDERENGINE_luxrender.luxcore_session.GetRenderConfig().GetScene()
            RENDERENGINE_luxrender.begin_scene_edit()

            if update_changes.cause_camera:
                LuxLog('Camera update')
                self.luxcore_exporter.convert_camera()

            if update_changes.cause_materials:
                LuxLog('Materials update')
                for material in update_changes.changed_materials:
                    self.luxcore_exporter.convert_material(material)

            if update_changes.cause_mesh:
                for ob in update_changes.changed_objects_mesh:
                    LuxLog('Mesh update: ' + ob.name)
                    self.luxcore_exporter.convert_object(ob, luxcore_scene, update_mesh=True, update_material=False)

            if update_changes.cause_light or update_changes.cause_objectTransform:
                for ob in update_changes.changed_objects_transform:
                    LuxLog('Transformation update: ' + ob.name)

                    self.luxcore_exporter.convert_object(ob, luxcore_scene, update_mesh=False, update_material=False)

            if update_changes.cause_objectsRemoved:
                # TODO: implement this with new interface
                pass

                '''
                def remove_object(ob, exported_object):
                    # loop through object components (split by materials)
                    for exported_object_data in exported_object.luxcore_data:
                        luxcore_name = exported_object_data.lcObjName
                        light_type = exported_object_data.lightType

                        if ob.type == 'LAMP' and light_type != 'AREA':
                            print('removing light %s (luxcore name: %s)' % (ob.name, luxcore_name))
                            luxcore_scene.DeleteLight(luxcore_name)
                        else:
                            print('removing object %s (luxcore name: %s)' % (ob.name, luxcore_name))
                            luxcore_scene.DeleteObject(luxcore_name)

                cache = converter.get_export_cache()

                for ob in update_changes.removed_objects:
                    if cache.has(ob):
                        exported_object = cache.get_exported_object(ob)
                        remove_object(ob, exported_object)

                # Remove particles/duplis
                for ob in update_changes.removed_objects:
                    # Dupliverts/frames/groups etc.
                    if ob.is_duplicator and len(ob.particle_systems) == 0:
                        ob.dupli_list_create(context.scene, settings = 'VIEWPORT')

                        for dupli_ob in ob.dupli_list:
                            dupli_key = (dupli_ob.object, ob)

                            if cache.has(dupli_key):
                                exported_object = cache.get_exported_object(dupli_key)
                                remove_object(ob, exported_object)

                        ob.dupli_list_clear()

                    # Particle systems
                    elif len(ob.particle_systems) > 0:
                        for psys in ob.particle_systems:
                            ob.dupli_list_create(context.scene, settings = 'VIEWPORT')

                            if len(ob.dupli_list) > 0:
                                dupli_ob = ob.dupli_list[0]
                                dupli_key = (dupli_ob.object, psys)

                                if cache.has(dupli_key):
                                    exported_object_list = cache.get_exported_object(dupli_key)

                                    for exported_object in exported_object_list:
                                        remove_object(ob, exported_object)

                            ob.dupli_list_clear()
                '''

            if update_changes.cause_volumes:
                for volume in context.scene.luxrender_volumes.volumes:
                    self.luxcore_exporter.convert_volume(volume)

            updated_properties = self.luxcore_exporter.pop_updated_scene_properties()

            # Debug output
            print('Updated scene properties:')
            print(updated_properties, '\n')

            # parse scene changes and end sceneEdit
            luxcore_scene.Parse(updated_properties)

            RENDERENGINE_luxrender.end_scene_edit()

        # report time it took to update
        view_update_time = int(round(time.time() * 1000)) - view_update_startTime
        LuxLog('Dynamic updates: update took %dms' % view_update_time)
            
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
        self.cause_objectsRemoved = False
        self.cause_volumes = False
        self.cause_haltconditions = False
        
    def set_cause(self,
                  startViewportRender = None, 
                  mesh = None, 
                  light = None, 
                  camera = None, 
                  objectTransform = None, 
                  layers = None,
                  materials = None, 
                  config = None,
                  objectsRemoved = None,
                  volumes = None,
                  haltconditions = None):
        # automatically switch off unkown
        self.cause_unknown = False
        
        if startViewportRender is not None:
            self.cause_startViewportRender = startViewportRender 
        if mesh is not None:
            self.cause_mesh = mesh 
        if light is not None:
            self.cause_light = light 
        if camera is not None:
            self.cause_camera = camera 
        if objectTransform is not None:
            self.cause_objectTransform = objectTransform 
        if layers is not None:
            self.cause_layers = layers
        if materials is not None:
            self.cause_materials = materials 
        if config is not None:
            self.cause_config = config 
        if objectsRemoved is not None:
            self.cause_objectsRemoved = objectsRemoved
        if volumes is not None:
            self.cause_volumes = volumes
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
        if self.cause_objectsRemoved:
            print('objects where removed:')
            for obj in self.removed_objects:
                print('    ' + obj.name)
        if self.cause_volumes:
            print('volumes changed')
        if self.cause_haltconditions:
            print('halt conditions changed')

        print('========================================')


@persistent
def stop_viewport_render(context):
    # Check if there should be an active viewport rendering session
    if bpy.context.screen:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D' and space.viewport_shade == 'RENDERED':
                        return

    # No viewport in "RENDERED" mode found, stop running rendersessions
    RENDERENGINE_luxrender.stop_luxcore_session()


bpy.app.handlers.scene_update_post.append(stop_viewport_render)