bl_info = {
    "name": "Remove unused Vertex Groups",
    "author": "CoDEmanX",
    "version": (1, 0),
    "blender": (2, 70, 0),
    "location": "Properties Editor > Object data > Vertex Groups > Specials menu",
    "description": "Delete Vertex Groups with no assigned weight of active object",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame"
}


import bpy
from bpy.types import Operator


class OBJECT_OT_vertex_group_remove_unused(Operator):
    bl_idname = "object.vertex_group_remove_unused"
    bl_label = "Remove unused Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def execute(self, context):

        ob = context.object
        ob.update_from_editmode()

        vgroup_used = {i: False for i, k in enumerate(ob.vertex_groups)}

        for v in ob.data.vertices:
            for g in v.groups:
                if g.weight > 0.0:
                    vgroup_used[g.group] = True

        for i, used in sorted(vgroup_used.items(), reverse=True):
            if not used:
                ob.vertex_groups.remove(ob.vertex_groups[i])

        return {'FINISHED'}


def draw_func(self, context):
    self.layout.operator(
        OBJECT_OT_vertex_group_remove_unused.bl_idname,
        icon='X'
    )


def register():
    bpy.utils.register_module(__name__)
    bpy.types.MESH_MT_vertex_group_specials.prepend(draw_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.MESH_MT_vertex_group_specials.remove(draw_func)

if __name__ == "__main__":
    register()

