import bpy
import bmesh


class HOPS_OT_StarConnect(bpy.types.Operator):
    bl_idname = "hops.star_connect"
    bl_label = "Hops Star Connect"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Allows an edge to be created between more than 2 points"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return(object.type == 'MESH' and context.mode == 'EDIT_MESH')

    def execute(self, context):

        # bmesh version of MACHIN3's star connect

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        # check if at least 2 verts are selected
        selected = [v.index for v in bm.verts if v.select]
        if len(selected) < 2:
            return {'FINISHED'}

        bpy.ops.mesh.select_mode(type="VERT")

        # uses active vert from history (should be faster) or last selected if it doesn't exist
        try:
            av = bm.select_history.active
            av.select_set(0)
        except:
            lastvert = selected[-1]
            av = bm.verts[lastvert]
            av.select_set(0)

        verts = []

        # conects all selected verts to active one
        for v in bm.verts:
            if v.select:
                verts.append(v)
                verts.append(av)
                bm.select_history.add(av)
                bmesh.ops.connect_verts(bm, verts=verts)
                verts[:] = []

        av.select_set(1)

        bmesh.update_edit_mesh(me)

        return {'FINISHED'}
