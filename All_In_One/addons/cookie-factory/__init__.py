# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Copyright (C) 2018 Nikolai Janakiev
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
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
import sys
import json
import time
import importlib
import logging
import random

from . import panel
from . import core

if "bpy" in locals():
    importlib.reload(panel)
    importlib.reload(core)

import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.app.handlers import persistent

logging.basicConfig(level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


bl_info = {
    'name': 'Cookie Factory',
    'author': 'Nikolai Janakiev (njanakiev)',
    'version': (0, 1, 0),
    'blender': (2, 78, 0),
    'location': 'View3D > Tool Shelf > Cookie Factory',
    'description': 'Processing-style coding in Blender',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Development'
}


class ImportConfigurations(bpy.types.Operator):
    bl_label = 'Import / Reload'
    bl_idname = 'cookie_factory.import_configuration'
    log = logging.getLogger('bpy.ops.%s' % bl_idname)

    def execute(self, context):
        cf = context.scene.cookie_factory
        self.log.debug('Import configuraton file : {}'.format(
                            cf.config_filepath))

        import_configuration(context.scene, cf.config_filepath)

        return {'FINISHED'}


class CookieFactoryRender(bpy.types.Operator):
    bl_label = 'Render'
    bl_idname = 'cookie_factory.render'
    log = logging.getLogger('bpy.ops.%s' % bl_idname)

    def execute(self, context):
        render(context.scene)
        return {'FINISHED'}


class CookieFactoryAnimation(bpy.types.Operator):
    bl_label = 'Animation'
    bl_idname = 'cookie_factory.animation'
    log = logging.getLogger('bpy.ops.%s' % bl_idname)

    def execute(self, context):
        render(context.scene, animation=True)
        return {'FINISHED'}


def import_configuration(scene, filepath):
    logger.debug('import_configuration called')
    if os.path.splitext(filepath)[1] != '.json':
        raise ValueError('Only JSON files allowed')

    with open(filepath, 'r') as f:
        config = json.load(f)

    cwd = os.path.dirname(__file__)
    sys.path.append(cwd)

    scene_folder = os.path.dirname(filepath)
    if scene_folder not in sys.path:
        sys.path.append(scene_folder)

    scene_names = []
    if 'scene' in config:
        scene_name = config['scene']
        scene_names.append(scene_name)
    else:
        scene_idx = 0
        if 'scene_idx' in config and 'scenes' in config:
            scene_idx = config['scene_idx']
            scene_name = config['scenes'][scene_idx]
            scene_names = config['scenes']
        elif 'scenes' in config:
            scene_name = config['scenes'][0]
            scene_names = config['scenes']
        else:
            raise ValueError('Configuraton not valid')

    # Get cookie_factory configuration
    cf = scene.cookie_factory

    # Set render stamp
    if 'render_stamp' in config:
        title = "Render"
        detailed = False
        foreground, background = (0, 0, 0, 1), (1, 1, 1, 0)
        font_size = 10

        if 'title' in config['render_stamp']:
            title = config['render_stamp']['title']
        if 'detailed' in config['render_stamp']:
            detailed = config['render_stamp']['detailed']
        if 'background' in config['render_stamp']:
            background = tuple(config['render_stamp']['background'])
        if 'foreground' in config['render_stamp']:
            foreground = tuple(config['render_stamp']['foreground'])
        if 'font_size' in config['render_stamp']:
            font_size = config['render_stamp']['font_size']
        core.render_stamp(title, detailed, foreground, background, font_size)
    else:
        scene.render.use_stamp = False

    # Set number of used threads
    if 'threads' in config:
        scene.render.threads_mode = 'FIXED'
        scene.render.threads = config['threads']

    # Set render engine
    if 'cycles' in config:
        if config['cycles']:
            bpy.context.scene.render.engine = 'CYCLES'
        else:
            bpy.context.scene.render.engine = 'BLENDER_RENDER'

    # Set render resolution
    width, height, percentage = 800, 800, 100
    if 'resolution' in config:
        if 'width' in config['resolution']:
            width = config['resolution']['width']
        if 'height' in config['resolution']:
            height = config['resolution']['height']
        if 'percentage' in config['resolution']:
            percentage = config['resolution']['percentage']
    rnd = scene.render
    rnd.resolution_x, rnd.resolution_y = width, height
    rnd.resolution_percentage = percentage

    if 'output_folder' in config:
        cf.output_folder = config['output_folder']
    if 'output_name' in config:
        cf.output_name = config['output_name']
    else:
        cf.output_name = scene_name.split('.')[-1]
    if 'override' in config:
        cf.override = config['override']
    if 'animation' in config:
        frame_start, frame_end = 1, 100
        if 'frames' in config['animation']:
            frame_end = config['animation']['frames']
        if 'frame_start' in config['animation']:
            frame_start = config['animation']['frame_start']
        if 'frame_end' in config['animation']:
            frame_end = config['animation']['frame_end']

        # Set number of frames
        scene.frame_start = frame_start
        scene.frame_current = frame_start
        scene.frame_end = frame_end
        scene.frame_step = 1

    #  Add scenes
    cf.scene_names.clear()
    for name in scene_names:
        item = cf.scene_names.add()
        item.name = name

    # Set scene (this calls the execute function)
    cf.scene_name = scene_name


def render(scene, animation=False):
    logger.debug('render called')

    cf = scene.cookie_factory
    scene_folder = os.path.dirname(cf.config_filepath)

    if animation:
        if cf.override:
            filepath = os.path.join(scene_folder,
                                    cf.output_name, 'frame_')
        else:
            output_folder = lambda idx : \
                os.path.join(os.getcwd(),
                             scene_folder,
                             cf.output_folder,
                             '{}_{:04d}'.format(cf.output_name, idx))
            i = 0
            while(os.path.exists(output_folder(i))): i += 1
            filepath = os.path.join(output_folder(i), 'frame_')
    else:
        if cf.override:
            filepath = os.path.join(scene_folder,
                                    cf.output_folder, 'frame_')
        else:
            output_file = lambda idx : \
                os.path.join(os.getcwd(),
                             scene_folder,
                             cf.output_folder,
                             '{}_{:04d}.png'.format(cf.output_name, idx))
            i = 0
            logger.debug('Filepath : {}'.format(output_file(i)))

            while os.path.exists(output_file(i)):
                logger.debug('exits')
                i = i + 1

            filepath = output_file(i)
            logger.debug('Filepath : {}'.format(filepath))

    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(animation=animation, write_still=True)


@persistent
def run_background(scene):
    logger.debug('run_background called')

    if run_background in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.remove(run_background)

    # Read arguments
    if "--" not in sys.argv:
        argv = []  # as if no args are passed
    else:
        blender_argv = sys.argv[:sys.argv.index('--')]
        argv = sys.argv[sys.argv.index('--') + 1:]  # get args after '--'
        if len(argv) < 1:
            raise ValueError('No filepath to configuration file given')
        filepath = argv[0]

        import_configuration(scene, filepath)

        # Rerun render_pre handlers
        for handler in bpy.app.handlers.render_pre:
            handler(scene)

        if ('-a' in blender_argv) or ('--render-anim' in blender_argv):
            render(scene, animation=True)
            bpy.ops.wm.quit_blender()

        elif ('-f' in blender_argv) or ('--render-frame' in blender_argv):
            render(scene)
            bpy.ops.wm.quit_blender()


def register():
    logger.debug('register called')

    panel.register()
    bpy.utils.register_class(ImportConfigurations)
    bpy.utils.register_class(CookieFactoryRender)
    bpy.utils.register_class(CookieFactoryAnimation)

    # Register handler when Blender is run in background
    if bpy.app.background:
        bpy.app.handlers.render_pre.append(run_background)


def unregister():
    logger.debug('unregister called')

    panel.unregister()
    bpy.utils.unregister_class(ImportConfigurations)
    bpy.utils.unregister_class(CookieFactoryRender)
    bpy.utils.unregister_class(CookieFactoryAnimation)


if __name__ == '__main__':
    register()
