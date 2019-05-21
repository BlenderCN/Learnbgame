import bpy
from bpy.props import EnumProperty, BoolProperty
import bmesh


axisitems = [("X", "X", ""),
             ("Y", "Y", ""),
             ("Z", "Z", "")]

axismap = {"X": 0, "Y": 1, "Z": 2}

typeitems = [("MIN", "Min", ""),
             ("MAX", "Max", ""),
             ("ZERO", "Zero", ""),
             ("AVERAGE", "Average", ""),
             ("CURSOR", "Cursor", "")]


class AlignEditMesh(bpy.types.Operator):
    bl_idname = "machin3.align_editmesh"
    bl_label = "MACHIN3: Align (Edit Mesh)"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Default: Local Align\nAlt + Click: Global Align."

    axis: EnumProperty(name="Axis", items=axisitems, default="X")
    type: EnumProperty(name="Type", items=typeitems, default="MIN")
    local: BoolProperty(name="Local Space", default=True)

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def invoke(self, context, event):
        self.local = not event.alt

        self.align(context, axismap[self.axis], self.type, local=self.local)
        return {'FINISHED'}

    def execute(self, context):
        self.align(context, axismap[self.axis], self.type, local=self.local)
        return {'FINISHED'}

    def align(self, context, axis, type, local=True):
        active = context.active_object
        mx = active.matrix_world

        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]
        axiscoords = [v.co[axis] for v in verts] if local else [(mx @ v.co)[axis] for v in verts]


        # get target value depending on type
        if type == "MIN":
            target = min(axiscoords)

        elif type == "MAX":
            target = max(axiscoords)

        elif type == "ZERO":
            target = 0

        elif type == "AVERAGE":
            target = sum(axiscoords) / len(axiscoords)

        elif type == "CURSOR":
            if local:
                c_world = context.scene.cursor.location
                c_local = mx.inverted() @ c_world
                target = c_local[axis]

            else:
                target = context.scene.cursor.location[axis]


        # set the new coordinates
        for v in verts:
            if local:
                v.co[axis] = target

            else:
                world_co = mx @ v.co
                world_co[axis] = target

                v.co = mx.inverted() @ world_co

        bmesh.update_edit_mesh(active.data)
