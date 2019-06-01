import os
import bpy
import json
from os import path
from .multifile import register_class, register_function, unregister_function, ReloadStorage
from .envelope_builder import get_armature_filenames
from bpy.app.handlers import persistent


def space(layout, length=5):
    for _ in range(length):
        layout.separator()


def draw_mask_tools(layout, context):
    ob = context.active_object
    layout.label(text="Mask Tools")
    layout.operator("sculpt_tool_kit.mask_extract")
    layout.operator("sculpt_tool_kit.mask_split")
    layout.operator("sculpt_tool_kit.mask_decimate")
    if ob:
        if not ob.get("MASK_RIG"):
            layout.operator("sculpt_tool_kit.mask_deform_add")
        else:
            layout.operator("sculpt_tool_kit.mask_deform_remove")


def draw_remesh_tools(layout, context):
    layout.label(text="Remesh")
    layout.operator("sculpt_tool_kit.voxel_remesh")
    layout.operator("sculpt_tool_kit.decimate")


def draw_booleans(layout, context):
    ob = context.active_object
    layout.label(text="Booleans")
    layout.operator("sculpt_tool_kit.boolean", text="Union", icon="MOD_OPACITY").operation = "UNION"
    layout.operator("sculpt_tool_kit.boolean", text="Difference", icon="MOD_BOOLEAN").operation = "DIFFERENCE"
    layout.operator("sculpt_tool_kit.boolean", text="Intersect", icon="MOD_MASK").operation = "INTERSECT"
    layout.operator("sculpt_tool_kit.slice_boolean", icon="MOD_MIRROR")
    layout.operator("sculpt_tool_kit.slash", icon="GREASEPENCIL")


@register_class
class SCTK_PT_envelope_list(bpy.types.Panel):
    bl_idname = "SCULPT_TOOL_KIT_PT_envelope_list"
    bl_label = "Add Envelope Base"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    def draw(self, context):
        layout = self.layout
        for file, name, path in reversed(list(get_armature_filenames())):
            row = layout.row(align=True)
            row.operator("sculpt_tool_kit.load_envelope_armature", text=name, text_ctxt=path).type = file
            row.operator("sculpt_tool_kit.delete_envelope_armature", text="", text_ctxt=path, icon="CANCEL").name = name


def draw_envelope_builder(layout, context):
    layout.label(text="Envelope Builder")
    layout.popover("SCULPT_TOOL_KIT_PT_envelope_list")
    layout.operator("sculpt_tool_kit.save_envelope_armature")
    layout.operator("sculpt_tool_kit.convert_envelope_armature")


def get_brush_enum_data(self, context):
    data = []
    n = 0
    for brush in bpy.data.brushes:
        if brush.use_paint_sculpt:
            data.append((brush.name, brush.name, brush.name, brush_icon_get(brush), n))
            n += 1
    return data


@register_class
class BrushSet(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.brush_set"
    bl_label = "Brush Set"
    bl_description = ""
    bl_options = {"REGISTER", "INTERNAL"}

    brush: bpy.props.EnumProperty(
        name="Brush",
        items=get_brush_enum_data
    )

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.mode == "SCULPT"

    def execute(self, context):
        if self.brush in bpy.data.brushes.keys():
            context.tool_settings.sculpt.brush = bpy.data.brushes[self.brush]
        return {"FINISHED"}


def brush_icon_get(brush):
    tool = brush.sculpt_tool
    if tool == "DRAW":
        return "BRUSH_SCULPT_DRAW"
    else:
        return "BRUSH_" + tool


@register_class
class SCKT_PT_brushes_list(bpy.types.Panel):
    bl_idname = "SCULPT_TOOL_KIT_PT_brushes_list"
    bl_label = "Brushes List"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sculpt ToolKit"

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.mode == "SCULPT"

    def draw(self, context):
        layout = self.layout
        layout.operator("sculpt_tool_kit.number_row_listener",
                        text="Disable number row" if NumberRowListener.running_get() else "Enable number row")
        layout.operator("sculpt_tool_kit.key_num_save")
        if NumberRowListener.running_get():
            layout.label(text="Number row now changes brushes")
        draw_brushes_list(layout, context)


def draw_brushes_list(layout, context):
    col = layout.column(align=True)
    for brush in bpy.data.brushes:
        row = col.row(align=True)
        if brush.use_paint_sculpt:
            split = row.split(factor=0.8, align=True)
            split.operator(
                "sculpt_tool_kit.brush_set", text=brush.name,
                icon=brush_icon_get(brush),
            ).brush = brush.name
            split.prop(brush, "sckt_key_num", text="")


# I am lazy XD
@register_class
class SCTK_PT_brush_panel(bpy.types.Panel):
    bl_idname = "SCULPT_TOOL_KIT_PT_brush_panel"
    bl_label = "Brush"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    def __getattribute__(self, item):
        if item == "is_popover":
            return False
        else:
            return super().__getattribute__(item)

    def paint_settings(self, context):
        settings = bpy.types.VIEW3D_PT_tools_brush.paint_settings(context)
        return settings

    def draw(self, context):
        bpy.types.VIEW3D_PT_tools_brush.draw(self, context)


def draw_sculpt_panels(layout, context):
    brush = context.tool_settings.sculpt.brush
    layout.popover("SCULPT_TOOL_KIT_PT_brushes_list",
                   text=brush.name,
                   icon=brush_icon_get(brush))
    col = layout.column(align=True)
    col.popover("SCULPT_TOOL_KIT_PT_brush_panel")
    col.popover("VIEW3D_PT_tools_brush_options", text="Brush Options")
    col.popover("VIEW3D_PT_tools_brush_texture")
    col.popover("VIEW3D_PT_tools_brush_stroke")
    col.popover("VIEW3D_PT_tools_brush_falloff")
    col.popover("VIEW3D_PT_sculpt_options")
    col.popover("VIEW3D_PT_sculpt_dyntopo")
    col.popover("VIEW3D_PT_sculpt_symmetry")


def draw_symmetry(layout, context):
    ob = context.active_object
    sculpt = context.scene.tool_settings.sculpt

    if ob and ob.mode == "SCULPT":
        layout.label(text="Symmetry")
        row = layout.row(align=True)
        row.prop(sculpt, "use_symmetry_x", text="X")
        row.prop(sculpt, "use_symmetry_y", text="Y")
        row.prop(sculpt, "use_symmetry_z", text="Z")

    layout.label(text="Symmetrize")
    identifiers = [sign + axis for sign in ("POSITIVE_", "NEGATIVE_") for axis in "XYZ"]
    texts = [sign + axis for sign in ("+ ", "- ") for axis in "XYZ"]
    row = layout.row()
    for i in range(6):
        if i % 3 == 0:
            col = row.column()
        col.operator("sculpt_tool_kit.symmetrize", text=texts[i]).axis = identifiers[i]


@register_class
class Close(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.close_menu"
    bl_label = "Close Menu"
    bl_description = "Close Menu"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {"FINISHED"}


@register_class
class SCTK_MT_sculpt_menu(bpy.types.Menu):
    bl_idname = "SCULPT_TOOL_KIT_MT_sculpt_menu"
    bl_label = "Sculpt"
    bl_region_type = "WINDOW"

    def draw(self, context):
        pie = self.layout.menu_pie()

        row = pie.row()
        col = row.column()
        box = col.box()
        draw_mask_tools(box, context)
        col = row.column()
        box = col.box()
        draw_remesh_tools(box, context)
        box = col.box()
        draw_symmetry(box, context)

        row = pie.row()
        box = row.box()
        draw_sculpt_panels(box, context)

        if context.active_object and not context.active_object.type == "ARMATURE":
            pie.operator("object.mode_set", text="Object Mode").mode = "OBJECT"
        else:
            pie.separator()

        pie.operator("sculpt_tool_kit.close_menu")


@register_class
class SCTK_MT_object_menu(bpy.types.Menu):
    bl_idname = "SCULPT_TOOL_KIT_MT_object_menu"
    bl_label = "Sculpt Toolkit Object menu"
    bl_region_type = "WINDOW"

    def draw(self, context):
        pie = self.layout.menu_pie()

        row = pie.row()
        col = row.column()
        box = col.box()
        draw_booleans(box, context)
        box = col.box()
        draw_remesh_tools(box, context)
        col = row.column()
        box = col.box()
        draw_mask_tools(box, context)
        box = col.box()
        draw_symmetry(box, context)

        # box = pie.box()
        # draw_symmetry(box, context)

        box = pie.box()
        draw_envelope_builder(box, context)

        if context.active_object and not context.active_object.type == "ARMATURE":
            pie.operator("object.mode_set", text="Sculpt Mode").mode = "SCULPT"
        else:
            pie.separator()

        pie.operator("sculpt_tool_kit.close_menu")


class SCKT_PT_panel_factory(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sculpt ToolKit"

    drw_func = lambda layout, context: None

    @classmethod
    def create_panel(cls, label, draw_function, poll_function=None):
        class SCKT_PT_panel(cls):
            bl_idname = "_PT_".join(["SCULPT_TOOL_KIT", label.replace(" ", "_").lower()])
            bl_label = label

            @classmethod
            def poll(cls, context):
                if poll_function:
                    return poll_function(cls, context)
                return True

            def draw(self, context):
                layout = self.layout
                draw_function(layout, context)

        return SCKT_PT_panel


@register_class
class NumberRowListener(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.number_row_listener"
    bl_label = "Number Row Listener"
    bl_description = "Toggles number row shortcuts for brushes."
    bl_options = {"REGISTER"}

    _timer = None
    _running = False

    @classmethod
    def running_set(cls, tag):
        cls._running = tag

    @classmethod
    def running_get(cls):
        return cls._running

    numbers = {"ZERO": 0,
               "ONE": 1,
               "TWO": 2,
               "THREE": 3,
               "FOUR": 4,
               "FIVE": 5,
               "SIX": 6,
               "SEVEN": 7,
               "EIGHT": 8,
               "NINE": 9}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        print(self.running_get())

        if not self.running_get():
            context.window_manager.modal_handler_add(self)
            self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
            self.running_set(True)
        else:
            self.running_set(False)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        if not self.running_get():
            context.window_manager.event_timer_remove(self._timer)
            return {"FINISHED"}

        if context.active_object:
            if context.active_object.mode == "SCULPT" and event.value == "PRESS":
                print("SCULPT")
                if str(event.type) in self.numbers:
                    n = self.numbers[event.type]
                    matching_brushes = []
                    for brush in bpy.data.brushes:
                        if brush.use_paint_sculpt:
                            if brush.sckt_key_num == n:
                                matching_brushes.append(brush)
                    if len(matching_brushes) == 1:
                        bpy.ops.sculpt_tool_kit.brush_set(brush=matching_brushes[0].name)

                    elif len(matching_brushes) > 1:
                        def draw(self, context):
                            pie = self.layout.menu_pie()
                            for brush in matching_brushes:
                                pie.operator("sculpt_tool_kit.brush_set").brush = brush.name

                        context.window_manager.popup_menu_pie(event, draw, title="Pick Brush")

        return {"PASS_THROUGH"}


register_class(SCKT_PT_panel_factory.create_panel("Booleans", draw_booleans))
register_class(SCKT_PT_panel_factory.create_panel("Envelope Builder", draw_envelope_builder))
register_class(SCKT_PT_panel_factory.create_panel("Mask Tools", draw_mask_tools))
register_class(SCKT_PT_panel_factory.create_panel("Remesh", draw_remesh_tools))
register_class(SCKT_PT_panel_factory.create_panel("Symmetry", draw_symmetry))

settings_file = path.join(path.dirname(path.realpath(__file__)), "brush_nums.json")


@persistent
def key_num_load(scene):
    if not path.isfile(settings_file):
        return False
    with open(settings_file, "r") as file:
        data = json.load(file)
    for name, number in data:
        if name in bpy.data.brushes.keys():
            bpy.data.brushes[name].sckt_key_num = number


def key_num_save(scene):
    data = []
    for brush in bpy.data.brushes:
        if brush.use_paint_sculpt:
            data.append((brush.name, brush.sckt_key_num))
    data = json.dumps(data)
    with open(settings_file, "w") as f:
        f.write(data)


@register_class
class KeyNumSave(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.key_num_save"
    bl_label = "Save Number Mapping."
    bl_description = "Saves current number row mapping to brushes as default"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        key_num_save(context.scene)
        return {"FINISHED"}


addon_keymaps = ReloadStorage.get("keymaps")


@register_function
def register():
    bpy.types.Brush.sckt_key_num = bpy.props.IntProperty(
        name="Draw Index",
        description="The key pressed in order to activate the brush if number row selection is active",
        min=-1,
        max=9
    )

    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='Sculpt', space_type="EMPTY")
        kmi = km.keymap_items.new("wm.call_menu_pie", type="W", alt=True, value="PRESS")
        kmi.properties.name = "SCULPT_TOOL_KIT_MT_sculpt_menu"
        addon_keymaps.append((km, kmi))

        km = kcfg.keymaps.new(name='Object Mode', space_type="EMPTY")
        kmi = km.keymap_items.new("wm.call_menu_pie", type="W", alt=True, value="PRESS")
        kmi.properties.name = "SCULPT_TOOL_KIT_MT_object_menu"
        addon_keymaps.append((km, kmi))

    bpy.app.handlers.load_post.append(key_num_load)


@unregister_function
def unregister():
    del bpy.types.Brush.sckt_key_num

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    bpy.app.handlers.load_post.remove(key_num_load)
    addon_keymaps.clear()
