import bpy
from bpy.types import (
        Operator,
        Menu,
        Panel,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        FloatVectorProperty,
        )


class IOPS_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "InteractionOps"

    text_color: FloatVectorProperty(
        name="Color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0,
        max=1,
        default=(0.8, 0.8, 0.8, 1.0),
        )
    text_color_key: FloatVectorProperty(
        name="Color key",
        subtype='COLOR_GAMMA',
        size=4,
        min=0,
        max=1,
        default=(1, 0.757, 0, 1.0),
        )

    text_size: IntProperty(
        name="Size",
        description="Modal operators text size",
        default=20,
        soft_min=1,
        soft_max=100
        )

    text_pos_x: IntProperty(
        name="Position X",
        description="Modal operators Text pos X",
        default=60,
        soft_min=1,
        soft_max=10000
        )

    text_pos_y: IntProperty(
        name="Position Y",
        description="Modal operators Text pos Y",
        default=60,
        soft_min=1,
        soft_max=10000
        )

    text_shadow_color: FloatVectorProperty(
        name="Shadow",
        subtype='COLOR_GAMMA',
        size=4,
        min=0,
        max=1,
        default=(0.0, 0.0, 0.0, 1.0),
        )

    text_shadow_toggle: BoolProperty(
        name="ON/OFF",
        description="ON/Off",
        default=False
        )

    text_shadow_blur: EnumProperty(
        name='Blur',
        description='Could be 0,3,5',
        items=[
            ('0', 'None', '', '', 0),
            ('3', 'Mid', '', '', 3),
            ('5', 'High', '', '', 5)],
        default='0',
        )

    text_shadow_pos_x: IntProperty(
        name="Shadow pos X",
        description="Modal operators Text pos X",
        default=2,
        soft_min=-50,
        soft_max=50
        )
    text_shadow_pos_y: IntProperty(
        name="Shadow pos Y",
        description="Modal operators Text pos Y",
        default=-2,
        soft_min=-50,
        soft_max=50
        )

    vo_cage_color: FloatVectorProperty(
        name="Cage color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0,
        max=1,
        default=(0.573, 0.323, 0.15, 1),
        )

    vo_cage_points_color: FloatVectorProperty(
        name="Cage points color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0,
        max=1,
        default=(0.873, 0.623, 0.15, 1),
        )

    vo_cage_ap_color: FloatVectorProperty(
        name="Active point color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0,
        max=1,
        default=(1, 0, 0, 1),
        )

    vo_cage_p_size: IntProperty(
        name="Cage point size",
        description="Visual origin cage point size",
        default=3,
        soft_min=2,
        soft_max=20
        )

    vo_cage_ap_size: IntProperty(
        name="Active point size",
        description="Visual origin active point size",
        default=6,
        soft_min=2,
        soft_max=20
        )

    align_edge_color: FloatVectorProperty(
        name="Edge color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0,
        max=1,
        default=(0, 1, 0, 1),
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row(align=True)
        # we don't want to put anything else on this row other than the 'split' item
        split = row.split(factor=0.65, align=False)
        box_kmp = split.box()
        box_ui = split.box()
        # Keymaps

        box_kmp.label(text='Keymaps:')
        try:
            mainRow = box_kmp.row(align=True)
            mainRow.alignment = 'LEFT'

            colLabels = mainRow.column(align=True)
            colLabels.alignment = 'RIGHT'

            colKeys = mainRow.column(align=True)
            colKeys.alignment = 'EXPAND'

            keymap = context.window_manager.keyconfigs.user.keymaps["Window"]
            colKeys.context_pointer_set("keymap", keymap)  # For the 'wm.keyitem_restore' operator.

            for item in reversed(keymap.keymap_items):
                if item.idname.startswith('iops.'):
                    op = eval("bpy.ops." + item.idname + ".get_rna_type()")
                    colLabels.label(text=op.name)
                    subRow = colKeys.row()
                    subRow.alignment = 'LEFT'
                    subRow.prop(item, 'type', text='', full_event=True)
                    subRow.prop(item, 'shift')
                    subRow.prop(item, 'ctrl')
                    subRow.prop(item, 'alt')
                    if item.is_user_modified:
                        subRow.operator('preferences.keyitem_restore', text='', icon='BACK').item_id = item.id

        except:
            layout.label(text='No keymaps found.', icon='ERROR')

        box_ui.label(text='UI Tweaks:')
        col = box_ui.column(align=True)
        box = box_ui.box()
        col = box.column(align=True)
        col.label(text="Text settings:")
        row = box.row(align=True)
        split = row.split(factor=0.5, align=False)
        col_text = split.column(align=True)
        col_shadow = split.column(align=True)
        row = col_text.row(align=True)
        row.prop(self, "text_color")
        row.prop(self, "text_color_key")
        row = col_text.row(align=True)
        row.prop(self, "text_size")
        row = col_text.row(align=True)
        row.prop(self, "text_pos_x")
        row.prop(self, "text_pos_y")
        # Shadow
        row = col_shadow.row(align=True)
        row.prop(self, "text_shadow_color")
        row.prop(self, "text_shadow_blur")
        row = col_shadow.row(align=True)
        row.prop(self, "text_shadow_toggle", toggle=True)
        row = col_shadow.row(align=True)
        row.prop(self, "text_shadow_pos_x")
        row.prop(self, "text_shadow_pos_y")
        # Align to edge
        box = box_ui.box()
        col = box.column(align=True)
        col.label(text="Align to edge:")
        row = box.row(align=True)
        row.alignment = 'LEFT'
        row.prop(self, "align_edge_color")
        # Visual origin
        box = box_ui.box()
        col = box.column(align=True)
        col.label(text="Visual origin:")
        # row = col.row(align=True)
        # col.alignment = 'LEFT'
        row = box.row(align=True)
        split = row.split(factor=0.5, align=False)
        col_ap = split.column(align=True)
        col_p = split.column(align=True)
        # Active point column
        col = col_p.column(align=True)
        col.label(text="Cage points:")
        col.prop(self, "vo_cage_p_size", text="Size")
        col.prop(self, "vo_cage_points_color", text="")
        # Cage points column
        col = col_ap.column(align=True)
        col.label(text="Active point:")
        col.prop(self, "vo_cage_ap_size", text="Size")
        col.prop(self, "vo_cage_ap_color", text="")
        # Cage color
        col = box.column(align=True)
        col.prop(self, "vo_cage_color")
