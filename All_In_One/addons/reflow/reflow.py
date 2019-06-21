'''
Copyright (C) 2015 Diego Gangl
diego@sinestesia.co

Created by Diego Gangl

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
import bpy.props as prop
import re


def render_button(self, context):
    """ Op Button for dimensions panel """

    row = self.layout.row()
    row.operator("keys.reflow")
    


class RF_OT_Reflow(bpy.types.Operator):
    bl_idname = "keys.reflow"
    bl_label = "Change fps for animations"
    bl_description = "Recalculate animations for a different fps"
    bl_options = {"REGISTER", "UNDO"}
    

    # Settings
    # -------------------------------------------------------------------------

    fps_source = prop.IntProperty(
                                   name = "Source FPS",
                                   min = 1,
                                   default = 24,
                                   description = "Original FPS to convert from"
                                 )
    

    fps_dest = prop.IntProperty(
                                 name = "Destination FPS",
                                 min = 1,
                                 default = 60,
                                 description = "Final FPS to convert to"
                               )

    do_actions = prop.BoolProperty(
                                    name = "Change actions",
                                    description = "Move keyframes in actions",
                                    default = True,
                                  )
    
    do_nla = prop.BoolProperty(
                                name = "Fix NLA Tracks",
                                description = ("Change Start and End frames"
                                               " For NLA Tracks"),
                                default = True,
                              )
    
    do_markers = prop.BoolProperty(
                                   name = "Change Markers",
                                   description = "Move markers' frames",
                                   default = True,
                                  )
    

    do_markers_name = prop.BoolProperty(
                                        name = "Change Marker Names",
                                        description = ("Try to change markers"
                                                       " default names"),
                                        default = True,
                                       )

    
    do_fix_endframe = prop.BoolProperty(
                                        name = "Change end frame",
                                        description = ("Change scene's end" 
                                                       " end frame"),
                                        default = True,
                                       )
    



    # Loop Methods
    # -------------------------------------------------------------------------

    def keyframe_resample(self, curve):
        """ Resample every keyframe in a curve """
        
        for keyframe in curve.keyframe_points:
            frame_original = keyframe.co[0]

            if frame_original != 0:
                keyframe.co[0] = frame_original // self.diff



    def fix_nla_length(self, track):
        """ Fix start and end frames for NLA tracks """

        for strip in track.strips:
            strip.action_frame_start //= self.diff
            strip.action_frame_end //= self.diff




    # Main Methods
    # -------------------------------------------------------------------------

    @classmethod
    def poll(cls, context):
        return len(bpy.data.actions) > 0



    def invoke(self, context, event):
        """ Show settings dialog """
        
        # Set default FPS from current FPS
        self.fps_source = context.scene.render.fps
        
        return context.window_manager.invoke_props_dialog(self)
    

    def draw(self, context):
        """ Draw settings dialog """

        self.layout.separator()
        row = self.layout.row()
        
        row.prop(self, "fps_source")
        row.label("", icon="FORWARD")
        row.prop(self, "fps_dest")

        self.layout.separator()
        row = self.layout.row()
        row.label("Settings", icon="SCRIPTWIN")

        row = self.layout.row()
        row.prop(self, "do_nla")
        
        row = self.layout.row()
        row.prop(self, "do_actions")
        
        row = self.layout.row()
        row.prop(self, "do_markers")
        
        row = self.layout.row()
        row.prop(self, "do_markers_name")
        
        row = self.layout.row()
        row.prop(self, "do_fix_endframe")

        self.layout.separator()



    def execute(self, context):
        """ Resample animation data """

        # Init
        # ---------------------------------------------------------------------
        render = context.scene.render
        actions = bpy.data.actions
        markers = context.scene.timeline_markers
        objects = bpy.data.objects

        self.diff = self.fps_source / self.fps_dest

        if self.diff == 1:
            self.report({"WARNING"},"Source and Destination FPS are the same.")
            return {"CANCELLED"}


        # Set new FPS in scene properties
        render.fps = self.fps_dest


        # Fix endframe
        # ---------------------------------------------------------------------
        if self.do_fix_endframe:
            scene.frame_end = scene.frame_end // self.diff

       
        # Fix actions
        # ---------------------------------------------------------------------
        if self.do_actions:
            for action in actions:
                for curve in action.fcurves:
                    self.keyframe_resample(curve)    


        # Fix NLA tracks
        # ---------------------------------------------------------------------
        if self.do_nla:
            for obj in objects:
                if obj.animation_data and obj.animation_data.use_nla:
                    for track in obj.animation_data.nla_tracks:
                        self.fix_nla_length(track)


        # Fix Markers
        # ---------------------------------------------------------------------
        if self.do_markers:
            for mark in markers:
                if mark.frame != 0:
                    new_frame = mark.frame // self.diff
                    mark.frame = new_frame

                    if self.do_markers_name:
                        regex = re.match('^F_[0-9]*$', mark.name)

                        if regex:
                            mark.name = 'F_{0}'.format(new_frame)


        return {'FINISHED'}