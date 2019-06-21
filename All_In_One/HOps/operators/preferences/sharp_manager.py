import bpy
import bmesh
from bpy.props import EnumProperty, FloatProperty
from math import radians
from ... utils.blender_ui import get_dpi_factor
from ... utils.context import ExecutionContext

sharp_types = [
    ("CREASE", "Crease", ""),
    ("BWEIGHT", "Bweight", ""),
    ("SEAM", "Seam", ""),
    ("SHARP", "Sharp", "")]

bweight_tabs = [
    ("ALL", "All Values", ""),
    ("DEFINED", "Defined Values", "")]


class HOPS_OT_SharpManager(bpy.types.Operator):
    bl_idname = "hops.sharp_manager"
    bl_label = "Hops Sharp Manager"
    bl_description = "Panel for conversion of marked edges to other types"
    bl_options = {'REGISTER', 'UNDO'}

    take_sharp_from: EnumProperty(name="Take Sharp Types",
                                  options={"ENUM_FLAG"}, items=sharp_types)

    apply_sharp_to: EnumProperty(name="Take Sharp Types",
                                 options={"ENUM_FLAG"}, items=sharp_types)

    remove_sharp: EnumProperty(name="Take Sharp Types",
                               options={"ENUM_FLAG"}, items=sharp_types)

    add_new_sharp: EnumProperty(name="Take Sharp Types",
                                options={"ENUM_FLAG"}, items=sharp_types)

    add_new_angle: FloatProperty(name="Apply To Angle", default=radians(30),
                                 min=0.0, max=radians(180), subtype="ANGLE")

    tab_weight_from: EnumProperty(name="Bweight", default="ALL", items=bweight_tabs)

    tab_weight_value: FloatProperty(name="Bevel Width Amount", description="Bevel Width Amount", default=0, min=0, max=1)

    tab_crease_from: EnumProperty(name="Crease", default="ALL", items=bweight_tabs)

    tab_crease_value: FloatProperty(name="Crease Amount", description="Crease Amount", default=0, min=0, max=1)

    tab_weight_apply: EnumProperty(name="Bweight", default="ALL", items=bweight_tabs)

    tab_weight_apply_value: FloatProperty(name="Bevel Width Amount", description="Bevel Width Amount", default=0, min=0, max=1)

    tab_crease_apply: EnumProperty(name="Crease", default="ALL", items=bweight_tabs)

    tab_crease_apply_value: FloatProperty(name="Crease Amount", description="Crease Amount", default=0, min=0, max=1)

    tab_weight_create: EnumProperty(name="Bweight", default="ALL", items=bweight_tabs)

    tab_weight_create_value: FloatProperty(name="Bevel Width Amount", description="Bevel Width Amount", default=0, min=0, max=1)

    tab_crease_create: EnumProperty(name="Crease", default="ALL", items=bweight_tabs)

    tab_crease_create_value: FloatProperty(name="Crease Amount", description="Crease Amount", default=0, min=0, max=1)

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object is None: return False
        return object.type == "MESH"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400 * get_dpi_factor(force=False))

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        box = layout.box().split(align=True)
        col = box.column(align=True)
        col.label(text="From")
        col.prop(self, "take_sharp_from", expand=True)
        col.prop(self, "tab_weight_from", expand=False)
        if self.tab_weight_from == "DEFINED":
            col.prop(self, "tab_weight_value")
        col.prop(self, "tab_crease_from", expand=False)
        if self.tab_crease_from == "DEFINED":
            col.prop(self, "tab_crease_value")

        col = box.column(align=True)
        col.label(text="Apply To")
        col.prop(self, "apply_sharp_to", expand=True)
        col.prop(self, "tab_weight_apply", expand=False)
        if self.tab_weight_apply == "DEFINED":
            col.prop(self, "tab_weight_apply_value")
        col.prop(self, "tab_crease_apply", expand=False)
        if self.tab_crease_apply == "DEFINED":
            col.prop(self, "tab_crease_apply_value")

        box = layout.box().split(align=True)
        col = box.column(align=True)
        col.label(text="Remove")
        col.prop(self, "remove_sharp", expand=True)

        box = layout.box().split(align=True)
        col = box.column(align=True)
        col.label(text="Apply To Angle")
        col.prop(self, "add_new_sharp", expand=True)
        col.prop(self, "add_new_angle")
        col.prop(self, "tab_weight_create", expand=False)
        if self.tab_weight_create == "DEFINED":
            col.prop(self, "tab_weight_create_value")
        col.prop(self, "tab_crease_create", expand=False)
        if self.tab_crease_create == "DEFINED":
            col.prop(self, "tab_crease_create_value")

    def execute(self, context):

        object = bpy.context.active_object
        with ExecutionContext(mode="EDIT", active_object=object):

            obj = bpy.context.object
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            bw = bm.edges.layers.bevel_weight.verify()
            cr = bm.edges.layers.crease.verify()
            # me.show_edge_bevel_weight = True
            # me.show_edge_crease = True
            # me.show_edge_sharp = True
            # me.show_edge_seams = True

            all_edges = [e for e in bm.edges]
            selected = [e for e in bm.edges if e.select]

            bpy.ops.mesh.select_all(action='DESELECT')

            for option in self.take_sharp_from:
                if option is not None:
                    for e in all_edges:
                        if option == "CREASE":
                            if self.tab_crease_from == "ALL":
                                if e[cr] > 0:
                                    e.select = True
                            elif self.tab_crease_from == "DEFINED":
                                if e[cr] == self.tab_crease_value:
                                    e.select = True
                        if option == "BWEIGHT":
                            if self.tab_weight_from == "ALL":
                                if e[bw] > 0:
                                    e.select = True
                            elif self.tab_weight_from == "DEFINED":
                                if e[bw] == self.tab_weight_value:
                                    e.select = True

                        if option == "SEAM":
                            if e.seam is True:
                                e.select = True
                        if option == "SHARP":
                            if e.smooth is False:
                                e.select = True
                        selected = [e for e in bm.edges if e.select]
                        for option2 in self.apply_sharp_to:
                            edges_values = [1, 1]
                            if self.tab_crease_apply == "DEFINED":
                                edges_values[0] = self.tab_crease_apply_value
                            if self.tab_weight_apply == "DEFINED":
                                edges_values[1] = self.tab_weight_apply_value
                            self.set_sharps(option2, selected, edges_values[0], edges_values[1], True, False)

                        bpy.ops.mesh.select_all(action='DESELECT')

            for option in self.remove_sharp:
                if option is not None:
                    self.set_sharps(option, all_edges, 0, 0, False, True)

            for option in self.add_new_sharp:
                if option is not None:
                    bpy.ops.mesh.edges_select_sharp(sharpness=self.add_new_angle)
                    selected = [e for e in bm.edges if e.select]
                    edges_to_create_values = [1, 1]
                    if self.tab_crease_create == "DEFINED":
                        edges_to_create_values[0] = self.tab_crease_create_value
                    if self.tab_weight_create == "DEFINED":
                        edges_to_create_values[1] = self.tab_weight_create_value
                    self.set_sharps(option, selected, edges_to_create_values[0], edges_to_create_values[1], True, False)

            bmesh.update_edit_mesh(me)

        return {"FINISHED"}

    def set_sharps(self, option, selection, crease, bweight, seam, share):

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bw = bm.edges.layers.bevel_weight.verify()
        cr = bm.edges.layers.crease.verify()
        for e in selection:
            if option == "CREASE":
                e[cr] = crease
            if option == "BWEIGHT":
                e[bw] = bweight
            if option == "SEAM":
                e.seam = seam
            if option == "SHARP":
                e.smooth = share

        return {'FINISHED'}
