import bpy
from bpy.props import IntProperty, CollectionProperty
from bpy.types import Panel, UIList

# #########################################
# TreeView 
# #########################################

def object_deselection():
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
    except:
        pass

def get_activeSceneObject():
    return bpy.context.scene.objects.active.name

class Uilist_actions_faces(bpy.types.Operator):
    bl_idname = "customfaces.list_action"
    bl_label = "List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('DISABLE', "DISABLE", ""),
            ('ENABLE', "ENABLE", "")
        )
    )

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.custom_faces_index

        try:
            item = scn.custom_faces[idx]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and idx < len(scn.custom_faces) - 1:
                item_next = scn.custom_faces[idx+1].name
                scn.custom_faces_index += 1
                info = 'Item %d selected' % (scn.custom_faces_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = scn.custom_faces[idx-1].name
                scn.custom_faces_index -= 1
                info = 'Item %d selected' % (scn.custom_faces_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item %s removed from list' % (scn.custom_faces[scn.custom_faces_index].name)
                object_deselection()
                # bpy.data.objects[scn.custom_faces[scn.custom_faces_index].name].select = True
                # scn.objects.active = bpy.data.objects[scn.custom_faces[scn.custom_faces_index].name]
                # bpy.ops.object.delete()
                scn.custom_faces_index -= 1
                self.report({'INFO'}, info)
                scn.custom_faces.remove(idx)
            elif self.action == 'DISABLE':
                scn.custom_faces[scn.custom_faces_index].enabled = False
            elif self.action == 'ENABLE':
                scn.custom_faces[scn.custom_faces_index].enabled = True
        return {"FINISHED"}

# #########################################
# Draw Panels and Button
# #########################################

def primitive_name_update(self, context):
    scn = context.scene
    idx = scn.custom_faces_index

    # print(idx,"  NEW NAME: ",scn.custom_faces[idx].name,"  OLD NAME: ",scn.custom_faces[idx].prev_name)
    if scn.custom_faces[idx].prev_name == "":
        scn.custom_faces[idx].prev_name = scn.custom_faces[idx].name
    else:
        bpy.data.objects[scn.custom_faces[idx].prev_name].name = scn.custom_faces[idx].name
        scn.custom_faces[idx].prev_name = scn.custom_faces[idx].name

class UL_items_faces(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(0.1)
        split.label("%d" % (index))
        split.prop(item, "name", text="%s" % (item.enabled), emboss=False, translate=True, icon='BORDER_RECT')

    def invoke(self, context, event):
        pass   

class UIListPanelExample_faces(Panel):
    """Creates a Panel in the Object properties window"""
    bl_idname = 'OBJECT_PT_my_panel_faces'
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "3D Faces"

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 5
        row = layout.row()
        row.template_list("UL_items_faces", "", scn, "custom_faces", scn, "custom_faces_index", rows=rows)

        col = row.column(align=True)
        col.operator("customfaces.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("customfaces.select_item", icon="UV_SYNC_SELECT")
        col.operator("customfaces.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        col.separator()
        col.operator("customfaces.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.operator("customfaces.list_action", icon='VISIBLE_IPO_ON', text="").action = 'ENABLE'
        col.operator("customfaces.list_action", icon='VISIBLE_IPO_OFF', text="").action = 'DISABLE'

        row = layout.row()
        col = row.column(align=True)
        col.operator("customfaces.clear_list", icon="X")

class Uilist_selectAllItems_faces(bpy.types.Operator):
    bl_idname = "customfaces.select_item"
    bl_label = ""
    bl_description = "Edit Primitive"

    def __init__(self):
        self._ob_select = None

    def execute(self, context):
        scn = context.scene
        idx = scn.custom_faces_index
        object_deselection()

        try:
            item = scn.custom_faces[idx]
        except IndexError:
            pass

        else:
            self._ob_select = bpy.data.objects[scn.custom_faces[scn.custom_faces_index].name]
            scn.objects.active = self._ob_select
            self._ob_select.select = True
            scn.ignit_panel.vp_model_types = self._ob_select["vp_model_types"]

        return{'FINISHED'}

class Uilist_clearAllItems_faces(bpy.types.Operator):
    bl_idname = "customfaces.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items in the list"

    def execute(self, context):
        scn = context.scene
        lst = scn.custom_faces
        object_deselection()

        if len(lst) > 0:
            for i in range(len(lst)-1,-1,-1):
                scn.custom_faces_index -= 1
                scn.custom_faces.remove(i)
            scn.custom_faces_index += 1
            self.report({'INFO'}, "All items removed")

        else:
            self.report({'INFO'}, "Nothing to remove")   

        return{'FINISHED'}

class CustomProp_faces(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(update=primitive_name_update)
    prev_name = bpy.props.StringProperty()
    enabled = bpy.props.BoolProperty()

# #########################################
# Register
# #########################################

classes = (
    CustomProp_faces,
    Uilist_actions_faces,
    Uilist_clearAllItems_faces,
    Uilist_selectAllItems_faces,
    UIListPanelExample_faces,
    UL_items_faces
)

if __name__ == "__main__":
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
