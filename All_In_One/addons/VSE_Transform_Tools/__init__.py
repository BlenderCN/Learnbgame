bl_info = {
    "name": "VSE Transform Tools",
    "description": "Quickly manipulate video strips in Blender's Video Sequence Editor",
    "author": "kgeogeo, DoubleZ, doakey3",
    "version": (1, 2, 7),
    "blender": (2, 80, 0),
    "wiki_url": "https://github.com/doakey3/VSE_Transform_Tools",
    "tracker_url": "https://github.com/doakey3/VSE_Transform_Tools/issues",
    "category": "Learnbgame",
}

"""
RegEx Classname
===============
[A-Z][A-Z0-9_]*_{ABBREV}_[A-Za-z0-9_]+

Abbrev
------
Header:   _HT_
Menu:     _MT_
Operator: _OT_
Panel:    _PT_
UIList:   _UL_
"""

import bpy

from .operators import *

handle_2d_cursor = None

from .operators.utils.draw import draw_line


def draw_callback_px_2d_cursor(self, context):
    c2d = context.region.view2d.view_to_region(
        context.scene.seq_cursor2d_loc[0],
        context.scene.seq_cursor2d_loc[1], clip=False)

    v1 = [c2d[0] - 5, c2d[1]]
    v2 = [c2d[0] + 5, c2d[1]]

    draw_line(v1, v2, 2, (1, 0, 0, 1))

    v1 = [c2d[0], c2d[1] - 5]
    v2 = [c2d[0], c2d[1] + 5]

    draw_line(v1, v2, 2, (1, 0, 0, 1))


def Add_Icon_Pivot_Point(self, context):
    layout = self.layout
    layout.prop(
        context.scene, "seq_pivot_type", text='',
        expand=False,  icon_only=True
    )


def update_seq_cursor2d_loc(self, context):
    context.area.tag_redraw()


def update_pivot_point(self, context):
    bpy.ops.vse_transform_tools.initialize_pivot()


class PREV_OT_initialize_pivot(bpy.types.Operator):
    """
    The pivot icon won't show up if blender opens already on pivot type
    2. This operator should be called whenever an action occurs on a
    strip.

    This has to be in the init file because of the global variable
    "handle_2d_cursor"
    """
    bl_idname = "vse_transform_tools.initialize_pivot"
    bl_label = "Make the pivot point appear if pivot styles is currently 2D cursor"

    @classmethod
    def poll(cls, context):
        ret = False
        if (context.scene.sequence_editor and
                context.space_data.type == 'SEQUENCE_EDITOR'):
            return True
        return False

    def execute(self, context):
        global handle_2d_cursor
        scene = context.scene
        args = (self, context)

        if scene.seq_pivot_type == '2' and not handle_2d_cursor:
            handle_2d_cursor = bpy.types.SpaceSequenceEditor.draw_handler_add(
                draw_callback_px_2d_cursor, args, 'PREVIEW', 'POST_PIXEL')
        elif not scene.seq_pivot_type == '2' and handle_2d_cursor:
            bpy.types.SpaceSequenceEditor.draw_handler_remove(
                handle_2d_cursor, 'PREVIEW')
            handle_2d_cursor = None

        return {'FINISHED'}


class SEQUENCER_PT_track_transform_ui(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_label = "VSE_Transform_Tools"
    bl_options = {"DEFAULT_CLOSED"}
    bl_category = "Tools"

    @classmethod
    def poll(cls, context):
        return context.space_data.view_type == 'SEQUENCER'

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        # TRANSFORM FROM 2D TRACK
        box = layout.box()
        row = box.row()
        row.label(text="Transform from 2D Track")
        row = box.row()
        row.prop(scene, "vse_transform_tools_use_rotation", text="Rotation")
        row.prop(scene, "vse_transform_tools_use_scale", text="Scale")

        row = box.row()
        row.prop(scene, "vse_transform_tools_tracker_1")
        row = box.row()
        row.prop(scene, "vse_transform_tools_tracker_2")
        if scene.vse_transform_tools_use_rotation or scene.vse_transform_tools_use_scale:
            row.enabled = True
        else:
            row.enabled = False

        row = box.row()
        row.operator("vse_transform_tools.track_transform")


def get_tracker_list(self, context):
    tracks = [("None", "None", "")]
    for movieclip in bpy.data.movieclips:
        for track in movieclip.tracking.tracks:
            tracks.append((track.name, track.name, ""))
    return tracks


def init_properties():
    bpy.types.Scene.seq_cursor2d_loc = bpy.props.IntVectorProperty(
        name="Scales",
        description="location of the cursor2d",
        subtype='XYZ',
        default=(50, 50),
        size=2,
        step=1,
        update=update_seq_cursor2d_loc
    )

    item_pivot_point = (
        ('0', 'Median Point', '', 'PIVOT_MEDIAN', 0),
        ('1', 'Individual Origins', '', 'PIVOT_BOUNDBOX', 1),
        ('2', '2D Cursor', '', 'PIVOT_CURSOR', 2),
        ('3', 'Active Strip', '', 'PIVOT_ACTIVE', 3)
    )
    bpy.types.Scene.seq_pivot_type = bpy.props.EnumProperty(
        name="Pivot Point",
        default="1",
        items=item_pivot_point,
        update=update_pivot_point
    )

    bpy.types.SEQUENCER_HT_header.append(Add_Icon_Pivot_Point)

    bpy.types.Scene.vse_transform_tools_use_rotation = bpy.props.BoolProperty(
        name="Rotation",
        default=True
    )

    bpy.types.Scene.vse_transform_tools_use_scale = bpy.props.BoolProperty(
        name="Scale",
        default=True
    )

    bpy.types.Scene.vse_transform_tools_tracker_1 = bpy.props.EnumProperty(
        name="Tracker 1",
        items=get_tracker_list
        )

    bpy.types.Scene.vse_transform_tools_tracker_2 = bpy.props.EnumProperty(
        name="Tracker 2",
        items=get_tracker_list
        )

classes = [
    PREV_OT_initialize_pivot,
    PREV_OT_set_cursor_2d,
    PREV_OT_add_transform,
    PREV_OT_select,
    PREV_OT_grab,
    PREV_OT_scale,
    PREV_OT_rotate,
    PREV_OT_autocrop,
    PREV_OT_delete,
    PREV_OT_duplicate,
    PREV_OT_group,
    PREV_OT_meta_toggle,
    PREV_OT_adjust_alpha,
    PREV_OT_call_menu,
    PREV_OT_insert_keyframe,
    PREV_MT_menu_insert_keyframe,
    PREV_OT_pixelate,
    PREV_OT_mouse_track,
    PREV_OT_crop,
    SEQUENCER_OT_track_transform,
    SEQUENCER_PT_track_transform_ui
]

addon_keymaps = []

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    init_properties()

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="SequencerPreview", space_type="SEQUENCE_EDITOR", region_type="WINDOW")

    kmi = km.keymap_items.new("vse_transform_tools.add_transform", 'T', 'PRESS')

    kmi = km.keymap_items.new("vse_transform_tools.grab", 'G', 'PRESS')
    kmi = km.keymap_items.new("vse_transform_tools.grab", 'G', 'PRESS', alt=True, shift=False)

    kmi = km.keymap_items.new("vse_transform_tools.scale", 'S', 'PRESS')
    kmi = km.keymap_items.new("vse_transform_tools.scale", 'S', 'PRESS', alt=True)

    kmi = km.keymap_items.new("vse_transform_tools.rotate", 'R', 'PRESS')
    kmi = km.keymap_items.new("vse_transform_tools.rotate", 'R', 'PRESS', alt=True)

    kmi = km.keymap_items.new("vse_transform_tools.autocrop", 'C', 'PRESS', shift=True)

    kmi = km.keymap_items.new("vse_transform_tools.crop", 'C', 'PRESS')
    kmi = km.keymap_items.new("vse_transform_tools.crop", 'C', 'PRESS', alt=True)

    kmi = km.keymap_items.new("vse_transform_tools.delete", "DEL", "PRESS")
    kmi = km.keymap_items.new("vse_transform_tools.delete", "DEL", "PRESS", shift=True)

    kmi = km.keymap_items.new("vse_transform_tools.duplicate", "D", 'PRESS', shift=True)

    kmi = km.keymap_items.new("vse_transform_tools.group", 'G', 'PRESS', ctrl=True)
    kmi = km.keymap_items.new("vse_transform_tools.group", 'G', 'PRESS', ctrl=False, alt=True, shift=True)

    kmi = km.keymap_items.new("vse_transform_tools.meta_toggle", "TAB", "PRESS")

    kmi = km.keymap_items.new("vse_transform_tools.adjust_alpha", 'Q', 'PRESS')
    kmi = km.keymap_items.new("vse_transform_tools.adjust_alpha", 'Q', 'PRESS', alt=True)

    kmi = km.keymap_items.new("vse_transform_tools.call_menu", 'I', 'PRESS')

    kmi = km.keymap_items.new("vse_transform_tools.pixelate", 'P', 'PRESS')

    kmi = km.keymap_items.new("vse_transform_tools.mouse_track", 'M', 'PRESS')

    #smb = bpy.data.window_managers["WinMan"].keyconfigs.active.preferences.select_mouse
    #smb = bpy.context.user_preferences.inputs.select_mouse

    smb = "RIGHT"
    kmi = km.keymap_items.new("vse_transform_tools.select", smb + 'MOUSE', 'PRESS')
    kmi = km.keymap_items.new("vse_transform_tools.select", smb + 'MOUSE', 'PRESS', shift=True)
    kmi = km.keymap_items.new("vse_transform_tools.select", 'A', 'PRESS')

    omb = "LEFT"
    kmi = km.keymap_items.new("vse_transform_tools.set_cursor2d", omb + 'MOUSE', 'PRESS')
    kmi = km.keymap_items.new("vse_transform_tools.set_cursor2d", omb + 'MOUSE', 'PRESS', ctrl=True)

    addon_keymaps.append(km)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
