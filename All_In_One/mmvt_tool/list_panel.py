import bpy
from bpy.props import IntProperty, CollectionProperty #, StringProperty
from bpy.types import Panel, UIList


# return name of selected object
def get_activeSceneObject():
    return bpy.context.scene.objects.active.name


# ui list item actions
class Uilist_actions(bpy.types.Operator):
    bl_idname = "custom.list_action"
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
                item_next = scn.custom[idx+1].name
                scn.custom_index += 1
                info = 'Item %d selected' % (scn.custom_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.custom[idx-1].name
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
            item.name = get_activeSceneObject() # assign name of selected object
            scn.custom_index = (len(scn.custom)-1)
            info = '%s added to list' % (item.name)
            self.report({'INFO'}, info)

        return {"FINISHED"}

# -------------------------------------------------------------------
# draw
# -------------------------------------------------------------------

# custom list
class UL_items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(0.3)
        split.label("Index: %d" % (index))
        split.prop(item, "name", text="", emboss=False, translate=False, icon='BORDER_RECT')

    def invoke(self, context, event):
        pass

# draw the panel
class UIListPanelExample(Panel):
    """Creates a Panel in the Object properties window"""
    bl_idname = 'mmvt.OBJECT_PT_my_panel'
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_label = "Custom Object List"

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 2
        row = layout.row()
        row.template_list("UL_items", "", scn, "custom", scn, "custom_index", rows=rows)

        col = row.column(align=True)
        col.operator("custom.list_action", icon='ZOOMIN', text="").action = 'ADD'
        col.operator("custom.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.separator()
        col.operator("custom.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("custom.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'

        row = layout.row()
        col = row.column(align=True)
        col.operator("custom.print_list", icon="WORDWRAP_ON")
        col.operator("custom.select_item", icon="UV_SYNC_SELECT")
        col.operator("custom.clear_list", icon="X")


# print button
class Uilist_printAllItems(bpy.types.Operator):
    bl_idname = "custom.print_list"
    bl_label = "Print List"
    bl_description = "Print all items to the console"

    def execute(self, context):
        scn = context.scene
        for i in scn.custom:
            print (i.name, i.id)
        return{'FINISHED'}

# select button
class Uilist_selectAllItems(bpy.types.Operator):
    bl_idname = "custom.select_item"
    bl_label = "Select List Item"
    bl_description = "Select Item in scene"

    def execute(self, context):
        scn = context.scene
        bpy.ops.object.select_all(action='DESELECT')
        obj = bpy.data.objects[scn.custom[scn.custom_index].name]
        obj.select = True

        return{'FINISHED'}

# clear button
class Uilist_clearAllItems(bpy.types.Operator):
    bl_idname = "custom.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items in the list"

    def execute(self, context):
        scn = context.scene
        lst = scn.custom
        current_index = scn.custom_index

        if len(lst) > 0:
             # reverse range to remove last item first
            for i in range(len(lst)-1,-1,-1):
                scn.custom.remove(i)
            self.report({'INFO'}, "All items removed")

        else:
            self.report({'INFO'}, "Nothing to remove")

        return{'FINISHED'}

# Create custom property group
class CustomProp(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    id = IntProperty()

# -------------------------------------------------------------------
# register
# -------------------------------------------------------------------

def init(addon):
    register()


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.custom = CollectionProperty(type=CustomProp)
    bpy.types.Scene.custom_index = IntProperty()

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index

if __name__ == "__main__":
    register()