import bpy
from perfect_shape.properties import PerfectShape


class PerfectShapePanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Perfect Shape"
    bl_context = "mesh_edit"
    bl_label = "Perfect Shape"

    def draw(self, context):
        wm = context.window_manager
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)
        col.operator("mesh.perfect_shape")
        if wm.operators:
            operator = wm.operators[-1]
            if operator.bl_idname == "MESH_OT_perfect_shape" and operator.shape == "OBJECT":
                if operator.target in bpy.data.objects:
                    col.operator("mesh.perfect_shape", text="Edit Shape Object")
        col = layout.column(align=True)
        if len(scene.perfect_shape.patterns) > 0:
            pattern = scene.perfect_shape.patterns[int(scene.perfect_shape.active_pattern)]
            col.label("Active Pattern ({} Verts):".format(len(pattern.verts)))
            col.template_icon_view(scene.perfect_shape, "active_pattern", show_labels=True)
            col = layout.column(align=True)
            col.prop(pattern, "name", text="")
            col.operator("mesh.perfect_pattern_remove")
            col = layout.column(align=True)
            col.operator("mesh.perfect_pattern_add", text="Mark New Pattern")
        else:
            col.operator("mesh.perfect_pattern_add")


class PerfectShapeUI(PerfectShape):
    def draw(self, context):
        layout = self.layout

        split = layout.split(align=True)
        col = split.column(align=True)
        col.template_icon_view(self, "shape", show_labels=True)
        col = split.column(align=True)
        sub = col.column()
        # sub.enabled = False
        sub.label("Mode:")
        sub.prop(self, "mode", text="")
        row = col.row()
        row.label("Fill Type:")
        row = col.row(align=True)
        row.prop(self, "fill_type", text="")
        row.prop(self, "fill_flatten", toggle=True)
        row = col.row(align=True)
        row.label("Influence:")
        row.label("Offset:")
        row = col.row(align=True)
        row.prop(self, "factor", text="")
        row.prop(self, "offset", text="")
        col = layout.column(align=True)
        row = col.row()
        if self.shape == "CIRCLE":
            row.label("Circle:")
            row = col.row(align=True)
            row.prop(self, "span")

        if self.shape == "RECTANGLE":
            row.label("Rectangle Sides Ratio:")
            row = col.row(align=True)
            row.prop(self, "ratio_a", text="")
            row.prop(self, "ratio_b", text="")
            row.prop(self, "is_square", toggle=True)
        elif self.shape == "OBJECT":
            row.label("Object:")
            split = col.split(percentage=0.68, align=True)
            split.prop_search(self, "target", context.scene.perfect_shape, "objects", icon="OBJECT_DATAMODE", text="")
            if self.target:
                split.operator("mesh.perfect_shape", text="Edit")
            else:
                split.operator("mesh.perfect_shape", text="Create")
        col.separator()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "active_tab", expand=True)
        box = col.box()

        if self.active_tab == "POSITIONING":
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(self, "shape_translation", text="")

            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(self, "rotation")
            row.prop(self, "shift")
            row.prop(self, "loop_rotation", text="Loop", toggle=True)
            row.prop(self, "shape_rotation", text="Shape", toggle=True)

            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(self, "projection", expand=True)
            row = col.row(align=True)
            row.prop(self, "invert_projection", toggle=True)
            row.prop(self, "use_ray_cast", toggle=True)

        elif self.active_tab == "SHAPING":
            col = box.column(align=True)

            col.prop(self, "extrude", text="Extrude Value")
            col = box.column(align=True)
            if self.extrude == 0:
                col.enabled = False

            col.prop(self, "side_inset", text="Side Faces Inset")
            col.prop(self, "cuts_rings")
            col.prop(self, "cuts")
            row = col.row(align=True)
            if self.cuts == 0:
                row.enabled = False
            row.prop(self, "cuts_shift", text="Shift")
            row.prop(self, "cuts_len", text="Length")
            row.prop(self, "cuts_repeat", text="Repeats")

            col = box.column(align=True)
            col.prop(self, "inset")
            col.prop(self, "outset")

        if context.space_data and (self.pivot_point != context.space_data.pivot_point or
                                   self.transform_orientation != context.space_data.transform_orientation):
            col = layout.column()
            col.operator("mesh.perfect_pattern_update")


def perfect_shape_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator("mesh.perfect_shape")
    layout.operator("mesh.perfect_pattern_add")


def register():
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(perfect_shape_menu)
    bpy.utils.register_class(PerfectShapePanel)


def unregister():
    bpy.utils.unregister_class(PerfectShapePanel)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(perfect_shape_menu)
