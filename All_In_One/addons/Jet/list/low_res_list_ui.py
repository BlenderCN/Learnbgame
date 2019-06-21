import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator, UIList
from .list_utils import add_objs, check_selected_objs, remove_obj, clear_objs, select_objs, hide_objs


class DATA_UL_jet_low_res_list(UIList):
    """
    List to contain objects (only meshes)
    """
    bl_idname = "DATA_UL_jet_list_low_res"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.object is not None:
            layout.alignment = 'EXPAND'
            # The name of the object will be displayed when is added to the list
            row = layout.row()
            split = row.split(percentage=0.15)
            split.prop(item.object, "hide", emboss=False, text="")
            split = split.split(percentage=0.15)
            icon_select = 'RADIOBUT_ON' if item.object.select else 'RADIOBUT_OFF'
            split.prop(item.object, "select", text="", emboss=False, icon=icon_select)
            split = split.split()
            split.prop(item.object, "name", text="", emboss=False, icon_value=icon)


class DATA_OT_jet_low_res_list_add(Operator):
    """
    Operator to add objects to the list
    """
    bl_idname = "low_res_obj_list_add.btn"
    bl_label = "Add Object(s)"
    bl_description = "Add selected object(s) to the list"

    @classmethod
    def poll(cls, context):
        return check_selected_objs(context)

    def execute(self, context):
        prop = context.scene.Jet.list_low_res
        add_objs(prop, context)
        return {'FINISHED'}


class DATA_OT_jet_low_res_list_remove(Operator):
    """
    Operator to remove objects from the list
    """
    bl_idname = "low_res_obj_list_remove.btn"
    bl_label = "Remove Object"
    bl_description = "Remove object from the list"

    @classmethod
    def poll(cls, context):
        prop = context.scene.Jet.list_low_res
        return len(prop.obj_list)>0

    def execute(self, context):
        low_res = context.scene.Jet.list_low_res
        idx = low_res.obj_list_index
        high_res = low_res.obj_list[idx].list_high_res
        high_res.obj_list_index = 0
        high_res.obj_list.clear()

        remove_obj(low_res)
        return {'FINISHED'}


class DATA_OT_jet_low_res_list_clear(Operator):
    """
    Operator to remove all the objects from the list
    """
    bl_idname = "low_res_obj_list_clear.btn"
    bl_label = "Clear list"
    bl_description = "Remove all objects from the list"

    @classmethod
    def poll(cls, context):
        prop = context.scene.Jet.list_low_res
        return len(prop.obj_list)>0

    def execute(self, context):
        prop = context.scene.Jet.list_low_res
        clear_objs(prop)
        return {'FINISHED'}


class DATA_OT_jet_low_res_list_select(Operator):
    """
    Operator to select/deselect objects from the list
    """
    bl_idname = "low_res_obj_list_select.btn"
    bl_label = "Select/Deselect Objects"
    bl_description = "Select/Deselect all objects in the list"

    select = BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        prop = context.scene.Jet.list_low_res
        return len(prop.obj_list)>0

    def execute(self, context):
        prop = context.scene.Jet.list_low_res
        select_objs(prop, self.select)
        return {'FINISHED'}


class DATA_OT_jet_low_res_list_hide(Operator):
    """
    Operator to show/hide objects from the list
    """
    bl_idname = "low_res_obj_list_hide.btn"
    bl_label = "Show/Hide Objects"
    bl_description = "Show/Hide Objects all object from the list"

    hide = BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        prop = context.scene.Jet.list_low_res
        return len(prop.obj_list)>0

    def execute(self, context):
        prop = context.scene.Jet.list_low_res
        hide_objs(prop, self.hide)
        return {'FINISHED'}