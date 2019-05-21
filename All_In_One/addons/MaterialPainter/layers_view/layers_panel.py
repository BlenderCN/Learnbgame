"""
    This file contains all the UI components and the action operators linked to the UI elements in the
    Layers Panel.
"""
import bpy
from layers_view.layers_panel_op_actions import LayersPanelOpActions


def get_active_scene_object_name():
    return bpy.context.scene.objects.active.name


# layers_view list item actions
class ActionsOp(bpy.types.Operator):
    bl_idname = "layers.list_action"
    bl_label = "List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.custom_index

        try:
            item = scn.custom[idx]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and idx < len(scn.custom) - 1:
                item_next = scn.custom[idx + 1].name
                scn.custom.move(idx, idx + 1)
                scn.custom_index += 1
                info = 'Item %d selected' % (scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.custom[idx - 1].name
                scn.custom.move(idx, idx - 1)
                scn.custom_index -= 1
                info = 'Item %d selected' % (scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item %s removed from list' % (scn.custom[scn.custom_index].name)
                scn.custom_index -= 1
                self.report({'INFO'}, info)
                scn.custom.remove(idx)

        if self.action == 'ADD':
            item = scn.custom.add()
            item.id = len(scn.custom)
            item.name = get_active_scene_object_name()  # assign name of selected object
            scn.custom_index = (len(scn.custom) - 1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)

        return {"FINISHED"}


# -------------------------------------------------------------------
# draw
# -------------------------------------------------------------------

# draw the list item
class LayersUIListItem(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(0.3)
        split.prop(item, "name", text="", emboss=False, translate=False, icon='LAYER_USED')
        split.label("%d" % (index))

    def invoke(self, context, event):
        pass


# draw the panel
class LayersPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_idname = 'OBJECT_PT_my_panel'
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "Custom Object List"

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 2
        row = layout.row()
        row.template_list("LayersUIListItem", "", scn, "custom", scn, "custom_index", rows=rows)

        col = row.column(align=True)
        col.operator("layers.list_action", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("layers.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("layers.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("layers.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        row = layout.row()
        col = row.column(align=True)
        col.operator("layers.print_list", icon="WORDWRAP_ON")
        col.operator("layers.select_item", icon="UV_SYNC_SELECT")
        col.operator("layers.clear_list", icon="X")


# print button
class PrintAllItemsOp(bpy.types.Operator):
    bl_idname = "layers.print_list"
    bl_label = "Print List"
    bl_description = "Print all items to the console"

    def execute(self, context):
        return LayersPanelOpActions(context, self.report).print_all()


# select button
class SelectAllItemsOp(bpy.types.Operator):
    bl_idname = "layers.select_item"
    bl_label = "Select List Item"
    bl_description = "Select Item in scene"

    def execute(self, context):
        return LayersPanelOpActions(context, self.report).selectAllItems()


# clear button
class ClearAllItemsOp(bpy.types.Operator):
    bl_idname = "layers.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items in the list"

    def execute(self, context):
        return LayersPanelOpActions(context, self.report).clearAllItems()


# Create custom property group
class CustomProp(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    id = bpy.props.IntProperty()


# -------------------------------------------------------------------
# register
# -------------------------------------------------------------------

def register():
    bpy.types.Scene.custom_index = bpy.props.IntProperty()
    bpy.types.Scene.custom = bpy.props.CollectionProperty(type=CustomProp)


def unregister():
    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index


if __name__ == "__main__":
    pass
