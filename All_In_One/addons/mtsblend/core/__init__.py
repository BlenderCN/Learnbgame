# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# ***** END GPL LICENSE BLOCK *****

"""Main Mitsuba extension class definition"""

# System libs
import os
import sys
import threading

# Blender libs
import bpy
import bl_ui

# Framework libs
from ..extensions_framework import util as efutil

# Exporter libs
from .. import MitsubaAddon
from ..export import get_output_filename
from ..export.scene import SceneExporter
from ..outputs import MtsManager
from ..outputs import MtsLog

# Exporter Property Groups need to be imported to ensure initialisation
from ..properties import (
    camera, engine, integrator, mesh, node as props_node, object as props_object, particle, sampler
)

# Exporter Nodes need to be imported to ensure initialisation
from ..nodes import (
    sockets, node_output, node_input, node_bsdf, node_subsurface, node_medium,
    node_emitter, node_environment, node_texture, nodetree
)

# Exporter Interface Panels need to be imported to ensure initialisation
from ..ui import (
    properties_render, properties_render_layer, properties_world,
    properties_camera, properties_lamp, properties_mesh, properties_particle,
    properties_material, properties_texture, space_node
)

# Exporter Operators need to be imported to ensure initialisation
from ..operators import misc, material, node as ot_node

from ..core import handlers


def _register_elm(elm, required=False):
    try:
        elm.COMPAT_ENGINES.add('MITSUBA_RENDER')

    except:
        if required:
            MtsLog('Failed to add Mitsuba to ' + elm.__name__)

# Add standard Blender Interface elements
_register_elm(bl_ui.properties_render.RENDER_PT_render, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_dimensions, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_output, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_stamp)

_register_elm(bl_ui.properties_render_layer.RENDERLAYER_PT_layers)

_register_elm(bl_ui.properties_scene.SCENE_PT_scene, required=True)
_register_elm(bl_ui.properties_scene.SCENE_PT_audio)
_register_elm(bl_ui.properties_scene.SCENE_PT_physics)  # This is the gravity panel
_register_elm(bl_ui.properties_scene.SCENE_PT_keying_sets)
_register_elm(bl_ui.properties_scene.SCENE_PT_keying_set_paths)
_register_elm(bl_ui.properties_scene.SCENE_PT_unit)
_register_elm(bl_ui.properties_scene.SCENE_PT_color_management)

_register_elm(bl_ui.properties_scene.SCENE_PT_rigid_body_world)

_register_elm(bl_ui.properties_scene.SCENE_PT_custom_props)

_register_elm(bl_ui.properties_world.WORLD_PT_context_world, required=True)
_register_elm(bl_ui.properties_world.WORLD_PT_preview)

_register_elm(bl_ui.properties_material.MATERIAL_PT_preview)

_register_elm(bl_ui.properties_data_lamp.DATA_PT_context_lamp)


# compatible() copied from blender repository (netrender)
def compatible(mod):
    mod = getattr(bl_ui, mod)

    #for subclass in mod.__dict__.values():
    for member in dir(mod):
        subclass = getattr(mod, member)
        _register_elm(subclass)

    del mod

compatible("properties_data_camera")
compatible("properties_data_mesh")
compatible("properties_data_speaker")
compatible("properties_particle")


@MitsubaAddon.addon_register_class
class RENDERENGINE_mitsuba(bpy.types.RenderEngine):
    '''
    Mitsuba Engine Exporter/Integration class
    '''

    bl_idname = 'MITSUBA_RENDER'
    bl_label = 'Mitsuba'
    bl_use_preview = True

    render_lock = threading.Lock()
    preferences = None

    def render(self, scene):
        '''
        scene:  bpy.types.Scene

        Export the given scene to Mitsuba.
        Choose from one of several methods depending on what needs to be rendered.

        Returns None
        '''

        with RENDERENGINE_mitsuba.render_lock:  # just render one thing at a time
            try:
                self.MtsManager = None
                self.render_update_timer = None
                self.output_dir = efutil.temp_directory()
                self.output_file = 'default.png'
                self.preferences = MitsubaAddon.get_prefs()

                if scene is None:
                    MtsLog('ERROR: Scene to render is not valid')
                    return

                MtsManager.SetRenderEngine(self)

                if self.is_preview:
                    self.render_preview(scene)
                    return

                exported_file = self.export_scene(scene)
                if exported_file is False:
                    return  # Export frame failed, abort rendering

                self.render_start(scene)

            except Exception as err:
                MtsLog('%s' % err)
                self.report({'ERROR'}, '%s' % err)

    def render_preview(self, scene):
        xres, yres = scene.camera.data.mitsuba_camera.mitsuba_film.resolution(scene)
        # Don't render the tiny images
        if xres <= 96:
            raise Exception('Skipping material thumbnail update, image too small (%ix%i)' % (xres, yres))

        if sys.platform == 'darwin':
            self.output_dir = efutil.filesystem_path(bpy.app.tempdir)

        else:
            self.output_dir = efutil.temp_directory()

        if self.output_dir[-1] != '/':
            self.output_dir += '/'

        output_file = os.path.join(self.output_dir, "matpreview.png")
        self.output_file = output_file

        efutil.export_path = self.output_dir

        from ..export import materials as export_materials

        # Iterate through the preview scene, finding objects with materials attached
        objects_mats = {}
        for obj in [ob for ob in scene.objects if ob.is_visible(scene) and not ob.hide_render]:
            for mat in export_materials.get_instance_materials(obj):
                if mat is not None:
                    if not obj.name in objects_mats.keys():
                        objects_mats[obj] = []

                    objects_mats[obj].append(mat)

        # find objects that are likely to be the preview objects
        preview_objects = [o for o in objects_mats.keys() if o.name.startswith('preview')]

        try:
            pobj = preview_objects[0]

        except:
            pobj = None

        # find the materials attached to the likely preview object
        try:
            likely_materials = objects_mats[pobj]

        except:
            likely_materials = None

        try:
            pmat = likely_materials[0]
            MtsLog('Rendering material preview: %s' % pmat.name)

        except:
            pmat = None

        ptex = None

        MM = MtsManager(
            scene.name,
            api_type=self.preferences.preview_export,
        )
        MtsManager.SetCurrentScene(scene)
        MtsManager.SetActive(MM)

        preview_context = MM.export_ctx

        if preview_context.EXPORT_API_TYPE == 'FILE':
            mts_filename = os.path.join(
                self.output_dir,
                'matpreview_materials.xml'
            )
            preview_context.set_filename(scene, mts_filename)

            MtsLog('output_dir: %s' % self.output_dir)
            MtsLog('output_file: %s' % output_file)
            MtsLog('scene_file: %s' % mts_filename)

        try:
            export_materials.ExportedMaterials.clear()
            export_materials.ExportedTextures.clear()

            from ..export import preview_scene

            preview_scene.preview_scene(scene, preview_context, obj=pobj, mat=pmat, tex=ptex)

            preview_context.configure()

            refresh_interval = 2

            MM.create_render_context('INT')  # Try creating an internal render context for preview
            render_ctx = MM.render_ctx

            if render_ctx.RENDER_API_TYPE == 'EXT':  # Internal rendering is not available, set some options for external rendering
                render_ctx.cmd_args.extend(['-b', '16',
                    '-r', '%i' % refresh_interval])

            render_ctx.set_scene(preview_context)
            render_ctx.render_start(output_file)

            MM.start()

            if render_ctx.RENDER_API_TYPE == 'EXT':
                MM.start_framebuffer_thread()

            while render_ctx.is_running() and not render_ctx.test_break():
                self.render_update_timer = threading.Timer(1, self.process_wait_timer)
                self.render_update_timer.start()

                if self.render_update_timer.isAlive():
                    self.render_update_timer.join()

            MM.stop()

        except Exception as exc:
            MtsLog('Preview aborted: %s' % exc)

        preview_context.exit()

        MM.reset()

    def set_export_path(self, scene):
        # replace /tmp/ with the real %temp% folder on Windows
        # OSX also has a special temp location that we should use
        fp = scene.render.filepath
        output_path_split = list(os.path.split(fp))

        if sys.platform in {'win32', 'darwin'} and output_path_split[0] == '/tmp':
            if sys.platform == 'darwin':
                output_path_split[0] = efutil.filesystem_path(bpy.app.tempdir)

            else:
                output_path_split[0] = efutil.temp_directory()

            fp = os.path.join(*output_path_split)

        scene_path = efutil.filesystem_path(fp)

        if os.path.isdir(scene_path):
            self.output_dir = scene_path

        else:
            self.output_dir = os.path.dirname(scene_path)

        if self.output_dir[-1] not in {'/', '\\'}:
            self.output_dir += '/'

        if scene.mitsuba_engine.export_type == 'INT':
            write_files = scene.mitsuba_engine.write_files

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

        # Pre-allocate the MtsManager so that we can set up the network servers before export
        MM = MtsManager(
            scene.name,
            api_type=api_type,
        )
        MtsManager.SetActive(MM)

        output_filename = get_output_filename(scene)

        scene_exporter = SceneExporter()
        scene_exporter.properties.directory = self.output_dir
        scene_exporter.properties.filename = output_filename
        scene_exporter.properties.api_type = api_type           # Set export target
        scene_exporter.properties.write_files = write_files     # Use file write decision from above
        scene_exporter.properties.write_all_files = False       # Use UI file write settings
        scene_exporter.set_scene(scene)

        export_result = scene_exporter.export()

        if 'CANCELLED' in export_result:
            return False

        # Look for an output image to load
        #if scene.camera.data.mitsuba_camera.mitsuba_film.write_png:
        #    self.output_file = efutil.path_relative_to_export(
        #        '%s/%s.png' % (self.output_dir, output_filename)
        #    )
        #elif scene.camera.data.mitsuba_camera.mitsuba_film.write_exr:
        #    self.output_file = efutil.path_relative_to_export(
        #        '%s/%s.exr' % (self.output_dir, output_filename)
        #    )
        self.output_file = '%s/%s.%s' % (self.output_dir, output_filename, scene.camera.data.mitsuba_camera.mitsuba_film.fileExtension)

        return "%s.xml" % output_filename

    def rendering_behaviour(self, scene):
        internal = (scene.mitsuba_engine.export_type == 'INT')
        write_files = scene.mitsuba_engine.write_files and (scene.mitsuba_engine.export_type in {'INT', 'EXT'})
        render = scene.mitsuba_engine.render

        # Handle various option combinations using simplified variable names !
        if internal:
            if write_files:
                if render:
                    start_rendering = True
                    parse = True

                else:
                    start_rendering = False
                    parse = False

            else:
                # will always render
                start_rendering = True
                parse = False

        else:
            # external always writes files
            if render:
                start_rendering = True
                parse = False

            else:
                start_rendering = False
                parse = False

        return internal, start_rendering, parse

    def render_start(self, scene):
        self.MtsManager = MtsManager.GetActive()

        # Remove previous rendering, to prevent loading old data
        # if the update timer fires before the image is written
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

        internal, start_rendering, parse = self.rendering_behaviour(scene)

        # Begin rendering
        if start_rendering:
            MtsLog('Starting Mitsuba')
            self.update_stats('', 'Mitsuba: Preparing Render')

            self.MtsManager.create_render_context(scene.mitsuba_engine.export_type)
            render_ctx = self.MtsManager.render_ctx

            if render_ctx.RENDER_API_TYPE == 'EXT':
                if scene.mitsuba_engine.binary_name == 'mitsuba':
                    render_ctx.cmd_args.extend(['-r', '%i' % scene.mitsuba_engine.refresh_interval])

            render_ctx.set_scene(self.MtsManager.export_ctx)
            render_ctx.render_start(self.output_file.replace('//', '/'))
            self.MtsManager.start()

            if internal or scene.mitsuba_engine.binary_name != 'mtsgui':
                if render_ctx.RENDER_API_TYPE == 'EXT':
                    self.MtsManager.start_framebuffer_thread()

                while render_ctx.is_running() and not render_ctx.test_break():
                    self.render_update_timer = threading.Timer(1, self.process_wait_timer)
                    self.render_update_timer.start()

                    if self.render_update_timer.isAlive():
                        self.render_update_timer.join()

                self.MtsManager.stop()
                self.MtsManager.reset()

    def process_wait_timer(self):
        # Nothing to do here
        pass
