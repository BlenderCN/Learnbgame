import bpy


class IOPS_OP_ToFaces(bpy.types.Operator):
    """Convert Vertex/Edge selection to face selection"""
    bl_idname = "iops.to_faces"
    bl_label = "Convert vertex/edge selection to face selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sm = context.tool_settings.mesh_select_mode[:]
        return (context.mode == 'EDIT_MESH' and
                (sm == (True, False, False) or
                 sm == (False, True, False)))

    def execute(self, context):
        bpy.ops.mesh.select_mode(use_expand=True, type='FACE')
        context.tool_settings.mesh_select_mode = (False, False, True)
        return {'FINISHED'}


class IOPS_OP_ToEdges(bpy.types.Operator):
    """Convert Vertex/Face selection to edge selection"""
    bl_idname = "iops.to_edges"
    bl_label = "Convert vertex/face selection to edge selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sm = context.tool_settings.mesh_select_mode[:]
        return (context.mode == 'EDIT_MESH' and
                (sm == (True, False, False) or
                 sm == (False, False, True)))

    def execute(self, context):
        exp = False
        if context.tool_settings.mesh_select_mode[0]:
            exp = True
        bpy.ops.mesh.select_mode(use_expand=exp, type='EDGE')
        context.tool_settings.mesh_select_mode = (False, True, False)
        return {'FINISHED'}


class IOPS_OP_ToVerts(bpy.types.Operator):
    """ Convert Edge/Face selection to vertex selection """
    bl_idname = "iops.to_verts"
    bl_label = "Convert edge/face selection to vertex selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sm = context.tool_settings.mesh_select_mode[:]
        return (context.mode == 'EDIT_MESH' and
                (sm == (False, True, False) or
                 sm == (False, False, True)))

    def execute(self, context):
        bpy.ops.mesh.select_mode(use_extend=True, type='VERT')
        context.tool_settings.mesh_select_mode = (True, False, False)
        return {'FINISHED'}
