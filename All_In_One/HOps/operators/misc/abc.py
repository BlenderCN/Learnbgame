import bpy


class HOPS_OT_changeName(bpy.types.Operator):
    bl_idname = "hops.namefix"
    bl_label = "triangulate ngons"
    bl_description = "name fix"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        replace = "PowerStructure01"

        for obj in context.view_layer.objects:
            if obj.type == 'MESH':
                obj.name = obj.name.replace(replace, "")
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.cube_project(cube_size=0)
                bpy.ops.object.mode_set(mode='OBJECT')

        for mat in bpy.data.materials:
            mat.name = mat.name.replace(replace, "")

        return {"FINISHED"}
