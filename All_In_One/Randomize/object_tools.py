import bpy

class ChildSeparateLoose(bpy.types.Operator):
    bl_idname = "object.child_separate_loose"
    bl_label = "Separate Child by Loose Parts"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object:
            if len(bpy.context.active_object.children) > 0:
                return True
        return False

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')          # Ensure we're in object mode first
        randomize_obj = bpy.context.active_object
        
        for child in randomize_obj.children:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_name(name=child.name)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_name(name=randomize_obj.name)

        return {'FINISHED'}

class ChildOriginToGeometry(bpy.types.Operator):
    bl_idname = "object.child_origin_to_geometry"
    bl_label = "Set Child Origins to Geometry"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if bpy.context.active_object:
            if len(bpy.context.active_object.children) > 0:
                return True
        return False

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')          # Ensure we're in object mode first
        randomize_obj = bpy.context.active_object
        
        for child in randomize_obj.children:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_name(name=child.name)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_name(name=randomize_obj.name)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(ChildSeparateLoose)
    bpy.utils.register_class(ChildOriginToGeometry)

def unregister():
    bpy.utils.unregister_class(ChildSeparateLoose)
    bpy.utils.unregister_class(ChildOriginToGeometry)
