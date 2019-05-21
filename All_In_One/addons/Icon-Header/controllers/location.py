import bpy

class CenterPivotMeshObj(bpy.types.Operator):
    """Change the object Pivot to the origin geometry"""
    bl_idname = "object.center_pivot_mesh_obj"
    bl_label = "Simple Object Operator"

    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        i = 0
        while i <3:
            bpy.context.object.location[i] = 0
            i = i +1

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CenterPivotMeshObj)


def unregister():
    bpy.utils.unregister_class(CenterPivotMeshObj)
