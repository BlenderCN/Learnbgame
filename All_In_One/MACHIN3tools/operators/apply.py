import bpy
from bpy.props import BoolProperty
import bmesh
from mathutils import Vector, Quaternion
from .. utils.registration import get_addon
from .. utils.math import flatten_matrix, get_loc_matrix, get_rot_matrix, get_sca_matrix


# TODO: updare child parent inverse mx?


class Apply(bpy.types.Operator):
    bl_idname = "machin3.apply_transformations"
    bl_label = "MACHIN3: Apply Transformations"
    bl_description = "Apply Transformations while keeping the bevel width as well as the child transformations unchanged."
    bl_options = {'REGISTER', 'UNDO'}

    scale: BoolProperty(name="Scale", default=True)
    rotation: BoolProperty(name="Rotation", default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row(align=True)
        row.prop(self, "scale", toggle=True)
        row.prop(self, "rotation", toggle=True)

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        if any([self.rotation, self.scale]):
            decalmachine, _, _, _ = get_addon("DECALmachine")

            # only apply the scale to objects, that arent't parented themselves
            apply_objs = [obj for obj in context.selected_objects if not obj.parent]

            for obj in apply_objs:

                # fetch children and their current world mx
                children = [(child, child.matrix_world) for child in obj.children]

                mx = obj.matrix_world
                loc, rot, sca = mx.decompose()

                # apply the current transformations on the mesh level
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                bm.normal_update()
                bm.verts.ensure_lookup_table()

                if self.rotation and self.scale:
                    bmmx = get_rot_matrix(rot) @ get_sca_matrix(sca)
                elif self.rotation:
                    bmmx = get_rot_matrix(rot)
                elif self.scale:
                    bmmx = get_sca_matrix(sca)

                bmesh.ops.transform(bm, matrix=bmmx, verts=bm.verts)

                bm.to_mesh(obj.data)
                bm.clear()

                # zero out the transformations on the object level
                if self.rotation and self.scale:
                    applymx = get_loc_matrix(loc) @ get_rot_matrix(Quaternion()) @ get_sca_matrix(Vector.Fill(3, 1))
                elif self.rotation:
                    applymx = get_loc_matrix(loc) @ get_rot_matrix(Quaternion()) @ get_sca_matrix(sca)
                elif self.scale:
                    applymx = get_loc_matrix(loc) @ get_rot_matrix(rot) @ get_sca_matrix(Vector.Fill(3, 1))

                obj.matrix_world = applymx


                # adjust the bevel width values accordingly
                if self.scale:
                    mods = [mod for mod in obj.modifiers if mod.type == "BEVEL"]

                    for mod in mods:
                        vwidth = get_sca_matrix(sca) @ Vector((0, 0, mod.width))
                        mod.width = vwidth[2]


                # reset the children to their original state again
                for obj, mxw in children:
                    obj.matrix_world = mxw

                    # update decal backups's backup matrices as well, we can just reuse the bmesh mx here
                    if decalmachine and obj.DM.decalbackup:
                        backup = obj.DM.decalbackup
                        backup.DM.backupmx = flatten_matrix(bmmx @ backup.DM.backupmx)

        return {'FINISHED'}
