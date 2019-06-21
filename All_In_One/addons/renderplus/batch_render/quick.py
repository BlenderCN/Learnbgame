# ------------------------------------------------------------------------------
# LICENSE
# ------------------------------------------------------------------------------
# Render+ - Blender addon
# (c) Copyright Diego Garcia Gangl (januz) - 2014, 2015
# <diego@sinestesia.co>
# ------------------------------------------------------------------------------
# This file is part of Render+
#
# Render+ is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ------------------------------------------------------------------------------

import bpy

from bpy.props import (IntProperty, 
                       StringProperty,
                       BoolProperty,
                       EnumProperty)


from . import color_looks
from .. import ui

# ------------------------------------------------------------------------------
#  LARGE RENDERS
# ------------------------------------------------------------------------------

class RP_OT_Quick_LargeRender(bpy.types.Operator):
    """ Generate render jobs by splitting the render in chunks """

    bl_idname = 'renderplus.batch_quick_large_render'
    bl_label = 'Large Render'
    bl_options = {"UNDO"}

    def execute(self, context):
        
        scene = context.scene
        batch_list = scene.renderplus.batch.jobs
        index = len(batch_list)
        settings = scene.renderplus.batch_ops.quick_batch

        step_x = 1 / settings.tiles_x
        step_y = 1 / settings.tiles_y
        
        current_x = 0
        current_y = 0
                
        for x in range(settings.tiles_x):
            for y in range(settings.tiles_y):
                batch_list.add()
                
                # Name 
                # --------------------------------------------------------------
                name = '{0} - Tile ({1}, {2})'.format(scene.name, x, y)
                batch_list[index].name = name
                
                # Output
                # --------------------------------------------------------------
                output = '{0}_tile_{1}_{2}-'.format(settings.output_path, x, y)
                batch_list[index].output = output
                
                # Scene data 
                # --------------------------------------------------------------
                context.scene.renderplus.batch.index = index
                
                batch_list[index].scene = context.scene.name
                batch_list[index].frame_start = scene.frame_start
                batch_list[index].frame_end = scene.frame_end
                
                
                # Section render settings
                # --------------------------------------------------------------
                batch_list[index].use_section = True     
                batch_list[index].section_x = current_x
                batch_list[index].section_y = current_y
                batch_list[index].section_width = step_x
                batch_list[index].section_height = step_y
                
                current_y += step_y
                index += 1
                
            current_y = 0
            current_x += step_x
        
        ui.mode = 'NORMAL'
        return {'FINISHED'}


# ------------------------------------------------------------------------------
#  COLOR LOOKS
# ------------------------------------------------------------------------------

class RP_OT_Quick_Looks(bpy.types.Operator):
    """ Generate render jobs by using a different look per job """

    bl_idname = 'renderplus.batch_quick_looks'
    bl_label = 'Render jobs by Color Looks'
    bl_options = {"UNDO"}

                    
    def execute(self, context):
        
        scene = context.scene
        settings = scene.renderplus.batch_ops.quick_batch
        batch_settings = scene.renderplus.batch
        batch_list = batch_settings.jobs
        index = len(batch_list)
            
        batch_settings.use_global_size = True
        batch_settings.global_size_x = settings.size_x
        batch_settings.global_size_y = settings.size_y
        
        for look in color_looks.looks:
            batch_list.add()
            batch_list[index].name = look
            
            # SCENE INFO
            # ------------------------------------------------------------------
            context.scene.renderplus.batch.index = index
            batch_list[index].scene = scene.name
            
            # OUTPUT
            # ------------------------------------------------------------------
            batch_list[index].output = '{0} - {1}_'.format(settings.output_path, 
                                                           look)
            
            # CUSTOM OVERRIDES
            # ------------------------------------------------------------------
            batch_list[index].custom_overrides.add()
            
            batch_list[index].custom_overrides[0].name = look
            batch_list[index].custom_overrides[0].path = 'view_settings.look'
            batch_list[index].custom_overrides[0].data = '\'{0}\''.format(look)
            
            index += 1
        
        ui.mode = 'NORMAL'
        return {'FINISHED'}



# ------------------------------------------------------------------------------
#  UI
# ------------------------------------------------------------------------------

class RP_MT_BatchQuick(bpy.types.Menu):

    """ Quick Batch Menu """

    bl_label = 'Quick Batch'
    bl_idname = 'renderplus.menus.batch_quick'

    def draw(self, context):
        layout = self.layout
        
        layout.operator('renderplus.batch_quick_scene', 
        text='Scenes', icon='SCENE_DATA')
        
        layout.operator('renderplus.batch_toggle_mode', text='Markers', 
        icon='MARKER_HLT').mode = 'QUICK_MARKERS'
        
        layout.operator('renderplus.batch_toggle_mode', text='Cameras', 
        icon='CAMERA_DATA').mode = 'QUICK_CAMERAS'
        
        layout.operator('renderplus.batch_toggle_mode', text='Render Layers', 
        icon='RENDERLAYERS').mode = 'QUICK_RLAYERS'
        
        layout.separator()
        
        layout.operator('renderplus.batch_toggle_mode', text='Large Render', 
                        icon='IMGDISPLAY').mode = 'QUICK_LARGE'
        
        layout.operator('renderplus.batch_toggle_mode', text='Color Looks', 
                        icon='COLOR').mode = 'QUICK_COLORS'
        

# ------------------------------------------------------------------------------
#  SCENE
# ------------------------------------------------------------------------------

class RP_OT_Quick_Scene(bpy.types.Operator):
    """ Generate render jobs from scene properties """

    bl_idname = "renderplus.batch_quick_scene"
    bl_label = "Generate render jobs for each scene"
    bl_options = {"UNDO"}

    def execute(self, context):
        
        scenes = bpy.data.scenes
        batch_list = context.scene.renderplus.batch.jobs
        index = len(batch_list)
        
        for scene in scenes:
            batch_list.add()
            batch_list[index].name = scene.name
            
            # SCENE INFO
            # ------------------------------------------------------------------
            context.scene.renderplus.batch.index = index
            batch_list[index].scene = scene.name
            batch_list[index].frame_start = scene.frame_start
            batch_list[index].frame_end = scene.frame_end
            
            batch_list[index].output = '//{0}'.format(scene.name)
            index += 1
            
        return {'FINISHED'}



# ------------------------------------------------------------------------------
#  OPERATOR
# ------------------------------------------------------------------------------

class RP_OT_QuickBatch(bpy.types.Operator):
    """ Generate render jobs from scene properties """

    bl_idname = "renderplus.batch_quick"
    bl_label = "Generate Render Jobs"
    bl_options = {"UNDO"}

    prop_type = EnumProperty(
        items=(
            ('QUICK_MARKERS', "Markers", ""),
            ('QUICK_CAMERAS', "Cameras", ""),
            ('QUICK_RLAYERS', "Render Layers", ""),
        ),
        name="Property to use",
    )

    def check_props(self, scene):
        """ Check if the scene has any of the selected property """

        if self.prop_type == 'QUICK_MARKERS':
            return True if len(scene.timeline_markers) > 0 else False

        elif self.prop_type == 'QUICK_RLAYERS':
            return True if len(scene.render.layers) > 0 else False

        elif self.prop_type == 'QUICK_CAMERAS':
            return scene.camera

    def generate_from_markers(self, context, scene):
        """ Generate render jobs from markers """

        markers = list(scene.timeline_markers)
        batch_list = context.scene.renderplus.batch.jobs
        settings = context.scene.renderplus.batch_ops.quick_batch

        # Sort markers by their frame
        markers.sort(key=lambda m: m.frame)

        start_index = len(batch_list) - 1
        index = start_index

        frame_start = 0

        for marker in markers:
            batch_list.add()
            index += 1

            batch_list[index].name = marker.name
            batch_list[index].frame_custom = True
            batch_list[index].frame_still = marker.frame

            # special case, don't use animation
            if marker.frame == 0:
                break

            # Move index to the new job
            context.scene.renderplus.batch.index = index
            batch_list[index].scene = scene.name

            batch_list[index].animation = settings.use_animation
            batch_list[index].frame_start = frame_start
            batch_list[index].frame_end = marker.frame

            frame_start = marker.frame
            
            if settings.no_camera:
                batch_list[index].camera = ''
                
        # Remaining of the animation
        if settings.use_animation and not frame_start == scene.frame_end:
            batch_list.add()
            index += 1

            batch_list[index].name = str.format(
                'Remaining for "{0}"',
                scene.name)
            batch_list[index].frame_custom = True
            batch_list[index].frame_still = scene.frame_end

            context.scene.renderplus.batch.index = index
            batch_list[index].scene = scene.name
            
            if settings.no_camera:
                batch_list[index].camera = ''

            batch_list[index].animation = True
            batch_list[index].frame_start = frame_start
            batch_list[index].frame_end = scene.frame_end


    def generate_from_renderlayers(self, context, scene):
        """ Generate render jobs from render layers """

        batch_list = context.scene.renderplus.batch.jobs
        layers = scene.render.layers

        start_index = len(batch_list) - 1
        index = start_index

        for layer in layers:

            # Only enabled layers
            if layer.use:
                batch_list.add()
                index += 1

                context.scene.renderplus.batch.index = index
                batch_list[index].name = layer.name
                batch_list[index].scene = scene.name
                batch_list[index].layer = layer.name

    def generate_from_cameras(self, context, scene):
        """ Generate render jobs from cameras """

        batch_list = context.scene.renderplus.batch.jobs
        cameras = []

        for obj in scene.objects:
            if obj.type == 'CAMERA':
                cameras.append(obj.name)

        start_index = len(batch_list) - 1
        index = start_index

        for cam in cameras:
            batch_list.add()
            index += 1

            context.scene.renderplus.batch.index = index
            batch_list[index].name = cam
            batch_list[index].scene = scene.name
            batch_list[index].camera = cam

    def execute(self, context):
        scenes = []
        settings = context.scene.renderplus.batch_ops.quick_batch

        if settings.all_scenes:
            for scene in bpy.data.scenes:
                scenes.append(scene)
        elif settings.scene == '':
            scenes.append(context.scene)
        else:
            scenes.append(bpy.data.scenes[settings.scene])

        for scene in scenes:
            # Check we have something to use
            if not self.check_props(scene):
                continue

            if self.prop_type == 'QUICK_MARKERS':
                self.generate_from_markers(context, scene)

            elif self.prop_type == 'QUICK_RLAYERS':
                self.generate_from_renderlayers(context, scene)

            elif self.prop_type == 'QUICK_CAMERAS':
                self.generate_from_cameras(context, scene)

            else:
                log.error('Unkown prop type in autogenerate')

                return {'CANCELLED'}

        if context.scene.renderplus.batch.index == -1:
            context.scene.renderplus.batch.index = 1

        ui.mode = 'NORMAL'
        return {'FINISHED'}
