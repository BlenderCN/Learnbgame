'''
Created on Feb 14, 2017

@author: Patrick
'''
import bpy

class CUTMESH_OT_join_strokes(bpy.types.Operator):
    """Join all polytrim stokes into single object"""
    bl_idname = "cut_mesh.polytrim_join_strokes"
    bl_label = "Join Polytrim Strokes"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    @classmethod
    def poll(cls, context):
        if context.mode == "OBJECT":
            return True
        else:
            return False
        
    def execute(self, context):
        
        obs = [ob for ob in context.scene.objects if 'polyknife' in ob.name and 'join' not in ob.name]
        bpy.ops.object.select_all(action = 'DESELECT')
        
        for ob in obs:
            ob.hide = False
            ob.select = True
            
        context.scene.objects.active = ob
        
        bpy.ops.object.join()
        context.obejct.name = 'polyknife_joined'
        return {'FINISHED'}
    
class CUTMESH_OT_hide_strokes(bpy.types.Operator):
    """Hide all polytrim stokes to get them out of the way"""
    bl_idname = "cut_mesh.polytrim_hide_strokes"
    bl_label = "Hide Polytrim Strokes"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    @classmethod
    def poll(cls, context):
        if context.mode == "OBJECT":
            return True
        else:
            return False
        
    def execute(self, context):
        
        obs = [ob for ob in context.scene.objects if 'polyknife' in ob.name]
        for ob in obs:
            ob.hide = True
            
        return {'FINISHED'}
    
class CUTMESH_OT_delete_strokes(bpy.types.Operator):
    """Delete all polytrim stokes if they are not needed"""
    bl_idname = "cut_mesh.polytrim_strokes_delete"
    bl_label = "Delete Polytrim Strokes"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    @classmethod
    def poll(cls, context):
        if context.mode == "OBJECT":
            return True
        else:
            return False
        
    def execute(self, context):
        
        obs = [ob for ob in context.scene.objects if 'polyknife' in ob.name and 'join' not in ob.name]
        bpy.ops.object.select_all(action = 'DESELECT')
        
        for ob in obs:
            ob.hide = False
            ob.select = True
            
        context.scene.objects.active = ob
        
        bpy.ops.object.delete(use_global = True)
        return {'FINISHED'}
