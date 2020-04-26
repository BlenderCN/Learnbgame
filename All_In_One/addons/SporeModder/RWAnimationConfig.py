import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       CollectionProperty
                       )



class RW4AnimProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Action.rw4 = PointerProperty(type=RW4AnimProperties)

        cls.is_morph_handle = BoolProperty(
            name="Is morph handle",
            description="Check if you want this animation to be a morph handle and not a normal animation",
            default=False
        )
        cls.initial_pos = FloatVectorProperty(
            name="Initial position",
            subtype='XYZ',
            precision=3,
            description="Handle initial position"
        )
        cls.final_pos = FloatVectorProperty(
            name="Final position",
            subtype='XYZ',
            precision=3,
            description="Handle final position"
        )
        cls.default_frame = IntProperty(
            name="Default frame",
            default=0,
            min=0
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Action.rw4

class RW4AnimUIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.name, icon=custom_icon)  # bpy.data.actions[item.Index]

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(item.name, icon=custom_icon)


class AnimPanel(bpy.types.Panel):

    bl_label = "RenderWare4 Animation Config"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        lay = self.layout

        row = lay.row()
        row.template_list("RW4AnimUIList", "The_List", bpy.data, "actions", context.scene, "rw4ListIndex")

        if len(bpy.data.actions) > 0:
            item = bpy.data.actions[context.scene.rw4ListIndex].rw4

            row = lay.row()
            row.prop(item, 'is_morph_handle')

            if item.is_morph_handle:
                row = lay.row()
                row.prop(item, 'initial_pos')

                row = lay.row()
                row.prop(item, 'final_pos')

                row = lay.row()
                row.prop(item, 'default_frame')
        

def register():
    bpy.utils.register_class(RW4AnimProperties)
    bpy.types.Scene.rw4ListIndex = IntProperty(name="Index for rw4_list", default=0)  # , update=update_action_list)


def unregister():
    bpy.utils.unregister_class(RW4AnimProperties)

    del bpy.types.Scene.rw4ListIndex
