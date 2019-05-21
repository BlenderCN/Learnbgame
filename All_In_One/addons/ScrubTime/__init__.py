# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2011: Benjamin Walther-Franks, bwf@tzi.de

bl_info = {
    "name": "ScrubTime",
    "description": "Retime an existing keyframe layout by scrubbing the timeline.",
    "author": "Benjamin Walther-Franks",
    "version": (1, 0),
    "blender": (2, 5, 9),
    "api": 31236,
    "location": "Timeline > Header > ScrubTime Button",
    "warning": '',
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

from .mpathutils import MotionPathProps, MotionPathPanel, MotionPathDrawOperator, MotionPathClearOperator
from .scrubtime import ScrubTimeOperator, ScrubTimeProps
from .timingutils import TimingProps
from bl_ui import space_time
import bpy


def draw(self, context):
    
    if context.active_object and context.active_object.mode in ['OBJECT', 'POSE']:
        layout = self.layout
        layout.separator()
        row = layout.row(align=True)
        row.operator("time.scrub_time", text="ScrubTime")
        row.prop(context.window_manager.scrub_time.timing, "apply_mode", text="")


def register():
    
    # ops
    bpy.utils.register_class(ScrubTimeOperator)
    
    # props
    bpy.utils.register_class(MotionPathProps)
    bpy.utils.register_class(TimingProps)
    bpy.utils.register_class(ScrubTimeProps)    
    bpy.types.WindowManager.scrub_time = bpy.props.PointerProperty(type=ScrubTimeProps)
    
    # gui
    space_time.TIME_HT_header.append(draw)
    
    # motion path setup
    if not hasattr(bpy.context.window_manager, "motion_path"):
        
        bpy.utils.register_class(MotionPathPanel)
        bpy.utils.register_class(MotionPathDrawOperator)
        bpy.utils.register_class(MotionPathClearOperator)
        
        bpy.types.WindowManager.motion_path = bpy.props.PointerProperty(type=MotionPathProps)


def unregister():
    
    bpy.utils.unregister_class(ScrubTimeOperator)
    bpy.utils.unregister_class(ScrubTimeProps)
    bpy.utils.unregister_class(TimingProps)
        
    del bpy.types.WindowManager.scrub_time
    space_time.TIME_HT_header.remove(draw)


if __name__ == "__main__":
    register()
