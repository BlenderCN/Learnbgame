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
    "name": "SketchTime",
    "description": "Retime an existing keyframe layout by sketching a timing path in the 3D view.",
    "author": "Benjamin Walther-Franks",
    "version": (1, 0),
    "blender": (2, 5, 9),
    "api": 31236,
    "location": "3D View > Tool Shelf > SketchTime Panel",
    "warning": '',
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

from .mpathutils import MotionPathProps, MotionPathPanel, MotionPathDrawOperator, MotionPathClearOperator
from .sketchtime import SketchTime, SketchTimeEdit, SketchTimeClear, SketchTimeApply, SketchTimePanel, SketchTimeProps
from .timingutils import TimingProps
import bpy


def register():
    
    # ops
    bpy.utils.register_class(SketchTime)
    bpy.utils.register_class(SketchTimeEdit)
    bpy.utils.register_class(SketchTimeClear)
    bpy.utils.register_class(SketchTimeApply)
    
    # props
    bpy.utils.register_class(MotionPathProps)
    bpy.utils.register_class(TimingProps)
    bpy.utils.register_class(SketchTimeProps)
    bpy.types.WindowManager.sketch_time = bpy.props.PointerProperty(type=SketchTimeProps)
    
    # gui
    bpy.utils.register_class(SketchTimePanel)
    
    # motion path setup
    if not hasattr(bpy.context.window_manager, "motion_path"):
        
        bpy.utils.register_class(MotionPathPanel)
        bpy.utils.register_class(MotionPathDrawOperator)
        bpy.utils.register_class(MotionPathClearOperator)
        
        bpy.types.WindowManager.motion_path = bpy.props.PointerProperty(type=MotionPathProps)


def unregister():
    
    bpy.utils.unregister_class(SketchTime)
    bpy.utils.unregister_class(SketchTimeEdit)
    bpy.utils.unregister_class(SketchTimeClear)
    bpy.utils.unregister_class(SketchTimeApply)
    bpy.utils.unregister_class(SketchTimePanel)
    bpy.utils.unregister_class(SketchTimeProps)
    bpy.utils.unregister_class(TimingProps)
    
    del bpy.types.WindowManager.sketch_time


if __name__ == "__main__":
    register()
