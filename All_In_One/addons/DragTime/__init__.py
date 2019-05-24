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
# Contributor: Florian Biermann

bl_info = {
    "name": "DragTime",
    "description": "Drag a feature along its motion path in the 3D view to navigate time or retime an animation.",
    "author": "Benjamin Walther-Franks",
    "version": (1, 0),
    "blender": (2, 5, 9),
    "api": 31236,
    "location": "3D View > Tool Shelf > DragTime Panel",
    "warning": '',
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

from .dragtime import DragTimeOperator, DragTimePanel, DragTimeProps
from .mpathutils import MotionPathProps, MotionPathPanel, MotionPathDrawOperator, MotionPathClearOperator
from .timingutils import TimingProps
import bpy


def register():
    
    # ops
    bpy.utils.register_class(DragTimeOperator)
    
    # props
    bpy.utils.register_class(MotionPathProps)
    bpy.utils.register_class(TimingProps)
    bpy.utils.register_class(DragTimeProps)
    bpy.types.WindowManager.drag_time = bpy.props.PointerProperty(type=DragTimeProps)
    
    # gui
    bpy.utils.register_class(DragTimePanel)    
    
    # motion path setup
    if not hasattr(bpy.context.window_manager, "motion_path"):
        
        bpy.utils.register_class(MotionPathPanel)
        bpy.utils.register_class(MotionPathDrawOperator)
        bpy.utils.register_class(MotionPathClearOperator)
        
        bpy.types.WindowManager.motion_path = bpy.props.PointerProperty(type=MotionPathProps)
    

def unregister():
    
    bpy.utils.unregister_class(DragTimeOperator)
    bpy.utils.unregister_class(DragTimePanel)
    bpy.utils.unregister_class(DragTimeProps)
    bpy.utils.unregister_class(TimingProps)
    
    del bpy.types.WindowManager.drag_time


if __name__ == "__main__":
    register()
