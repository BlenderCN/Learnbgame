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


bl_info = {
    "name": "Multicam Tools",
    "description": "Change Multicam sources with operators. This is intended for shortcut assignment.",
    "author": "Björn Sonnenschein",
    "version": (0, 1),
    "blender": (2, 64, 0),
    "location": "Sequencer > Tools",
    "warning": "Experimental",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Learnbgame"
}

import bpy, os

############TO DO##########
 
#######Changelog########
##Let's keep track of changes if some people will develop this script independently from each other.

################################
                                     
class s0 (bpy.types.Operator):
    bl_idname = "mt.s0"
    bl_label = "s0"
    bl_description = "Set source to 0"    
    
    def invoke (self, context, event):
        bpy.context.scene.sequence_editor.active_strip.multicam_source = 0
        print("ff")        
        return {'FINISHED'}                          
 
class s1 (bpy.types.Operator):
    bl_idname = "mt.s1"
    bl_label = "s1"
    bl_description = "Set source to 1"    
    
    def invoke (self, context, event):
        bpy.context.scene.sequence_editor.active_strip.multicam_source = 1     
        return {'FINISHED'}        
    
class s2 (bpy.types.Operator):
    bl_idname = "mt.s2"
    bl_label = "s2"
    bl_description = "Set source to 2"    
    
    def invoke (self, context, event):
        bpy.context.scene.sequence_editor.active_strip.multicam_source = 2    
        return {'FINISHED'}  
          
class s3 (bpy.types.Operator):
    bl_idname = "mt.s3"
    bl_label = "s3"
    bl_description = "Set source to 3"    
    
    def invoke (self, context, event):
        bpy.context.scene.sequence_editor.active_strip.multicam_source = 3  
        return {'FINISHED'}                          
 
class s4 (bpy.types.Operator):
    bl_idname = "mt.s4"
    bl_label = "s4"
    bl_description = "Set source to 4"    
    
    def invoke (self, context, event):
        bpy.context.scene.sequence_editor.active_strip.multicam_source = 4     
        return {'FINISHED'}        
    
class s5 (bpy.types.Operator):
    bl_idname = "mt.s5"
    bl_label = "s5"
    bl_description = "Set source to 5"    
    
    def invoke (self, context, event):
        bpy.context.scene.sequence_editor.active_strip.multicam_source = 5     
        return {'FINISHED'}  
    
class s6 (bpy.types.Operator):
    bl_idname = "mt.s6"
    bl_label = "s6"
    bl_description = "Set source to 6"    
    
    def invoke (self, context, event):
        bpy.context.scene.sequence_editor.active_strip.multicam_source = 6    
        return {'FINISHED'}        
    
class s7 (bpy.types.Operator):
    bl_idname = "mt.s7"
    bl_label = "s7"
    bl_description = "Set source to 7"    
    
    def invoke (self, context, event):
        bpy.context.scene.sequence_editor.active_strip.multicam_source = 7     
        return {'FINISHED'}  
    
def register():
    bpy.utils.register_class( s0 )
    bpy.utils.register_class( s1 )
    bpy.utils.register_class( s2 )
    bpy.utils.register_class( s3 )
    bpy.utils.register_class( s4 )
    bpy.utils.register_class( s5 )
    bpy.utils.register_class( s6 )
    bpy.utils.register_class( s7 )
    
def unregister():
    bpy.utils.unregister_class( s0 )
    bpy.utils.unregister_class( s1 )
    bpy.utils.unregister_class( s2 )
    bpy.utils.unregister_class( s3 )
    bpy.utils.unregister_class( s4 )
    bpy.utils.unregister_class( s5 )
    bpy.utils.unregister_class( s6 )
    bpy.utils.unregister_class( s7 )
 
if __name__ == "__main__":
    register()
    
    
    
    




