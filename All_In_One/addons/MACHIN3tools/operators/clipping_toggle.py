import bpy
from bpy.props import FloatProperty, BoolProperty, EnumProperty
from .. utils.property import step_enum


state_items = [("MIN", "Minimum", ""),
               ("MED", "Medium", ""),
               ("MAX", "Maximum", "")]


class ClippingToggle(bpy.types.Operator):
    bl_idname = "machin3.clipping_toggle"
    bl_label = "MACHIN3: Clipping Toggle"
    bl_options = {'REGISTER', 'UNDO'}

    def update_clip_start_maximum(self, context):
        if self.avoid_item_update:
            self.avoid_item_update = False
            return

        bpy.context.space_data.clip_start = self.maximum
        self.avoid_state_update = True
        self.state = "MAX"
        self.avoid_execute = True

    def update_clip_start_medium(self, context):
        if self.avoid_item_update:
            self.avoid_item_update = False
            return

        bpy.context.space_data.clip_start = self.medium
        self.avoid_state_update = True
        self.state = "MED"
        self.avoid_execute = True

    def update_clip_start_minimum(self, context):
        if self.avoid_item_update:
            self.avoid_item_update = False
            return

        bpy.context.space_data.clip_start = self.minimum
        self.avoid_state_update = True
        self.state = "MIN"
        self.avoid_execute = True

    def update_state(self, context):
        if self.avoid_execute:
            self.avoid_execute = False
            return

        if self.avoid_state_update:
            self.avoid_state_update = False
            return

        view = bpy.context.space_data

        if self.state == "MIN":
            view.clip_start = self.minimum

        elif self.state == "MED":
            view.clip_start = self.medium

        elif self.state == "MAX":
            view.clip_start = self.maximum

        self.avoid_execute = True

    def update_reset(self, context):
        if not self.reset:
            return

        self.avoid_item_update = True
        self.maximum = 1
        self.avoid_item_update = True
        self.medium = 0.1
        self.avoid_item_update = True
        self.minimum = 0.001

        view = bpy.context.space_data

        if self.state == "MIN":
            view.clip_start = self.minimum

        elif self.state == "MED":
            view.clip_start = self.medium

        elif self.state == "MAX":
            view.clip_start = self.maximum

        self.reset = False
        self.avoid_execute = True

    maximum: FloatProperty(name="Maximum", default=1, min=0, precision=2, step=10, update=update_clip_start_maximum)
    medium: FloatProperty(name="Medium", default=0.1, min=0, precision=3, step=1, update=update_clip_start_medium)
    minimum: FloatProperty(name="Minimum", default=0.001, min=0, precision=5, step=0.001, update=update_clip_start_minimum)

    state: EnumProperty(name="Current State", items=state_items, default="MED", update=update_state)
    reset: BoolProperty(default=False, update=update_reset)

    avoid_execute: BoolProperty(default=False)
    avoid_state_update: BoolProperty(default=False)
    avoid_item_update: BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        view = bpy.context.space_data

        row = col.row(align=True)
        row.prop(self, "state", expand=True)
        row.prop(self, "reset", text="", icon="BLANK1", emboss=False)

        row = col.row(align=True)
        row.prop(self, "minimum", text="")
        row.prop(self, "medium", text="")
        row.prop(self, "maximum", text="")
        row.prop(self, "reset", text="", icon="LOOP_BACK")

        row = col.row(align=True)
        row.label(text="Current")
        row.label(text=str(round(view.clip_start, 6)))

    def execute(self, context):
        if self.avoid_execute:
            self.avoid_execute = False

        else:
            self.avoid_execute = True
            self.state = step_enum(self.state, state_items, 1, loop=True)

            view = bpy.context.space_data

            if self.state == "MIN":
                view.clip_start = self.minimum

            elif self.state == "MED":
                view.clip_start = self.medium

            elif self.state == "MAX":
                view.clip_start = self.maximum

        return {'FINISHED'}
