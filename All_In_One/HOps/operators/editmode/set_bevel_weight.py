import bpy
import bmesh
from bpy.props import BoolProperty
from ... preferences import get_preferences


class HOPS_OT_SetEditSharpen(bpy.types.Operator):
    bl_idname = "hops.set_edit_sharpen"
    bl_label = "Hops Set Sharpen"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Mark Ssharp / Unmark Toggle"

    dont_affect_bevel: BoolProperty(name="Don't affect bevel weight",
                                    description="Don't affect bevel weight that was set manually",
                                    default=False)

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return(object.type == 'MESH' and context.mode == 'EDIT_MESH')

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "dont_affect_bevel")

    def execute(self, context):

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bw = bm.edges.layers.bevel_weight.verify()
        cr = bm.edges.layers.crease.verify()

        selected = [e for e in bm.edges if e.select]

        if not selected:
            print("auto_smooth_angle")
            for e in bm.edges:
                if e.calc_face_angle(0) >= get_preferences().sharpness:
                    if get_preferences().sharp_use_crease:
                        e[cr] = 1
                    if get_preferences().sharp_use_sharp:
                        e.smooth = False
                    if get_preferences().sharp_use_seam:
                        e.seam = True
                    if get_preferences().sharp_use_bweight:
                        if e[bw] == 0:
                            e[bw] = 1
        else:
            if any(e[bw] == 1 for e in selected):
                for e in selected:
                    if self.dont_affect_bevel:
                        if e[bw] == 1:
                            e[bw] = 0
                        if get_preferences().sharp_use_crease:
                            e[cr] = 0
                        if get_preferences().sharp_use_sharp:
                            e.smooth = True
                        if get_preferences().sharp_use_seam:
                            e.seam = False

                    else:
                        e[bw] = 0
                        if get_preferences().sharp_use_crease:
                            e[cr] = 0
                        if get_preferences().sharp_use_sharp:
                            e.smooth = True
                        if get_preferences().sharp_use_seam:
                            e.seam = False
            else:
                for e in selected:
                    if self.dont_affect_bevel:
                        if e[bw] == 0:
                            e[bw] = 1
                        if get_preferences().sharp_use_crease:
                            e[cr] = 1
                        if get_preferences().sharp_use_sharp:
                            e.smooth = False
                        if get_preferences().sharp_use_seam:
                            e.seam = True
                    else:
                        e[bw] = 1
                        if get_preferences().sharp_use_crease:
                            e[cr] = 1
                        if get_preferences().sharp_use_sharp:
                            e.smooth = False
                        if get_preferences().sharp_use_seam:
                            e.seam = True

        bmesh.update_edit_mesh(me)

        return {'FINISHED'}
