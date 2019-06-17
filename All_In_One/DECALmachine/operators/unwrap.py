import bpy
import bmesh
from .. utils.decal import sort_panel_geometry, create_panel_uvs
from .. utils.raycast import shrinkwrap
from .. utils.object import flatten


class Unwrap(bpy.types.Operator):
    bl_idname = "machin3.panel_decal_unwrap"
    bl_label = "MACHIN3: Panel Decal Unwrap"
    bl_description = "Re-Unwraps panel decals\nALT: Shrinkwraps in addtion to Unwrap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        decals = [obj for obj in context.selected_objects if obj.DM.isdecal]
        return decals and all(obj.DM.decaltype == "PANEL" and obj.DM.issliced for obj in decals)

    def invoke(self, context, event):
        for obj in context.selected_objects:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            if event.alt:
                target = obj.DM.slicedon if obj.DM.slicedon else obj.parent if obj.parent else None

                if target:
                    dg = context.evaluated_depsgraph_get()

                    bmt = bmesh.new()
                    bmt.from_mesh(target.evaluated_get(dg).to_mesh())

                    shrinkwrap(bm, bmt)


            # sort faces
            geo = sort_panel_geometry(bm)

            # unwrap
            create_panel_uvs(bm, geo, obj)

            obj.data.update()

        return {'FINISHED'}
