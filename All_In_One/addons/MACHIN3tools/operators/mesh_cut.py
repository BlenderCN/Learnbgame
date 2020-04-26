import bpy
from .. utils.mesh import unhide, unselect
from .. utils.object import flatten, add_facemap, add_vgroup


class MeshCut(bpy.types.Operator):
    bl_idname = "machin3.mesh_cut"
    bl_label = "MACHIN3: Mesh Cut"
    bl_description = "Knife Intersect a mesh, using another object.\nALT: flatten target object's modifier stack\nSHIFT: Mark Seam"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 2 and context.active_object and context.active_object in context.selected_objects

    def invoke(self, context, event):
        target = context.active_object
        cutter = [obj for obj in context.selected_objects if obj != target][0]

        # unhide both
        unhide(target.data)
        unhide(cutter.data)

        # unselect both
        unselect(target.data)
        unselect(cutter.data)

        # flatten the cutter
        flatten(cutter)

        # flatten the target
        if event.alt:
            flatten(target)

        # check for active cutter material
        mat = cutter.active_material

        # clear cutter materials
        if mat:
            cutter.data.materials.clear()

        add_facemap(cutter, name="mesh_cut", ids=[f.index for f in cutter.data.polygons])
        add_facemap(target, name="mesh_cut")

        # join
        bpy.ops.object.join()

        # select cutter mesh
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.face_map_select()

        # knife intersect
        if event.shift:
            bpy.ops.mesh.intersect(separate_mode='ALL')
        else:
            bpy.ops.mesh.intersect(separate_mode='CUT')

        # select cutter mesh
        bpy.ops.object.face_map_select()

        # remove cutter mesh
        bpy.ops.mesh.delete(type='FACE')

        # mark non-manifold edges
        if event.shift:
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.region_to_loop()

            bpy.ops.mesh.mark_seam(clear=False)
            bpy.ops.mesh.remove_doubles()

        # remove mesh_cut fmap
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.face_map_remove()

        return {'FINISHED'}
