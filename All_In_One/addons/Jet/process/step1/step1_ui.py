import bpy
from ... common_utils import get_hotkey, apply_to_selected
from . step1_utils import flat_smooth


#Panel
class VIEW3D_PT_jet_step1(bpy.types.Panel):
    bl_label = "1. Retopology"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Jet"
    #bl_options = {'HIDE_HEADER'}
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def snap(self, context, layout):
        obj = context.active_object
        toolsettings = context.tool_settings

        col = layout.column(align=True)
        row = col.row(align=True)

        text = "Snap" if toolsettings.use_snap else "No Snap - 'Ctrl to snap'"
        row.prop(toolsettings, "use_snap", text=text)

        row = col.row(align=True)
        row.prop(context.scene.Jet.snap, "face", "Snap to face", toggle=True)
        row.prop(context.scene.Jet.snap, "vertex", "Snap to vertex", toggle=True)

        # Snap original
        row_orig = layout.row()
        show_snap = (obj is None) or (obj.mode not in {'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT'})
        row_orig.enabled = show_snap
        snap_element = toolsettings.snap_element
        row = row_orig.row(align=True)
        row.prop(toolsettings, "snap_element", icon_only=True)
        if snap_element == 'INCREMENT':
            row.prop(toolsettings, "use_snap_grid_absolute", text="")
        else:
            row.prop(toolsettings, "snap_target", text="")
            if obj:
                if obj.mode == 'EDIT':
                    row.prop(toolsettings, "use_snap_self", text="")
                if obj.mode in {'OBJECT', 'POSE', 'EDIT'} and snap_element != 'VOLUME':
                    row.prop(toolsettings, "use_snap_align_rotation", text="")

        if snap_element == 'VOLUME':
            row.prop(toolsettings, "use_snap_peel_object", text="")
        elif snap_element == 'FACE':
            row.prop(toolsettings, "use_snap_project", text="")

        # AutoMerge editing
        # if obj:
        #   if obj.mode == 'EDIT' and obj.type == 'MESH':
        #       row_orig.prop(toolsettings, "use_mesh_automerge", text="", icon='AUTOMERGE_ON')

    def ice_tools(self, layout, context):
        box = layout.box()
        row_sw = box.row(align=True)
        row_sw.alignment = 'EXPAND'
        row_sw.operator("setup.retopo", "Set Up Retopo Mesh")
        row_sw = box.row(align=True)
        row_sw.alignment = 'EXPAND'
        row_sw.operator("shrink.update", "Shrinkwrap Update")

        row_fv = box.row(align=True)
        row_fv.alignment = 'EXPAND'
        row_fv.operator("freeze_verts.retopo", "Freeze")
        row_fv.operator("thaw_freeze_verts.retopo", "Thaw")
        row_fv.operator("show_freeze_verts.retopo", "Show")

        if context.active_object is not None:
            col = box.column(align=True)
            #col.alignment = 'EXPAND'
            col.prop(context.object, "show_wire", toggle=False)
            col.prop(context.object, "show_x_ray", toggle=False)
            col.prop(context.space_data, "show_occlude_wire", toggle=False)

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.Jet.info, "retopology", text="", icon="INFO")


    def draw(self, context):
        layout = self.layout
        box = layout.box()
        self.snap(context, box)

        row = layout.row(align=True)
        row.operator("jet_flat_smooth.btn", text="Flat").smooth=False
        row.operator("jet_flat_smooth.btn", text="Smooth").smooth=True

        col = layout.column(align=True)
        self.ice_tools(col, context)

        col = layout.column(align=True)
        col.operator("mesh.dupli_extrude_cursor", text="Extrude to Mouse - " + get_hotkey(context, "mesh.dupli_extrude_cursor"))
        col.operator("mesh.f2", text="MakeEdge/Face - " + get_hotkey(context, "mesh.f2"))
        col.operator("mesh.loopcut_slide", text="LoopCut and Slide - " + get_hotkey(context, "mesh.loopcut_slide"))
        col.operator("mesh.knife_tool", text="Knife - " + get_hotkey(context, "mesh.knife_tool"))
        col.operator("mesh.rip_edge_move", text="Extend Vertices - " + get_hotkey(context, "mesh.rip_edge_move"))
        col.operator("mesh.rip_move", text="Rip - " + get_hotkey(context, "mesh.rip_move"))
        col.operator("mesh.rip_move_fill", text="Rip Fill - " + get_hotkey(context, "mesh.rip_move_fill"))

#Operators
class VIEW3D_OT_jet_flat_smooth(bpy.types.Operator):
    bl_idname = "jet_flat_smooth.btn"
    bl_label = "Flat/Smooth"
    bl_description = "Flat/Smooth"

    smooth = bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        apply_to_selected(context, flat_smooth, value=self.smooth)
        return {'FINISHED'}







