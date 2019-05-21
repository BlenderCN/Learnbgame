# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# <pep8 compliant>

import bpy
import re

bl_info = {
    "name" : "LearnBlenderUI",
    "author" : "ChieVFX",
    "description" : "\
        Helps you find python name for the UI elements\
        via fragments of labels or python names.",
    "version": (0, 5),
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "wiki_url": "https://github.com/p2or/blender-viewport-rename",
    "tracker_url": "https://github.com/p2or/blender-viewport-rename/issues",
    "category" : "Development"
}

def get_ui_classes():
    ui = []
    headers = []
    menus = []
    operators = []
    panels = []
    ui_lists = []
    for clsName in dir(bpy.types):
        cls = getattr(bpy.types, clsName)
        # print("{} :: {}".format(clsName, cls))
        id_name = clsName
        if "_HT_" in id_name:
            ui.append(ClassContainer(cls, clsName))
            headers.append(ClassContainer(cls, clsName))
        if "_MT_" in clsName:
            ui.append(ClassContainer(cls, clsName))
            menus.append(ClassContainer(cls, clsName))
        if "_OT_" in clsName:
            ui.append(ClassContainer(cls, clsName))
            operators.append(ClassContainer(cls, clsName))
        if "_PT_" in clsName:
            ui.append(ClassContainer(cls, clsName))
            panels.append(ClassContainer(cls, clsName))
        if "_UL" in clsName:
            ui.append(ClassContainer(cls, clsName))
            ui_lists.append(ClassContainer(cls, clsName))
    
    return ui, headers, menus, operators, panels, ui_lists

class ClassContainer:
    def __init__(self, cls, idname):
        self.cls = cls
        self.label = ""
        if hasattr(cls, "bl_label"):
            self.label = cls.bl_label
        self.idname = idname
        if hasattr(cls, "bl_idname"):
            self.idname = cls.bl_idname
        else:
            class_name : [] = str(cls).replace("<class '", "").replace("'>", "").split('.')
            self.idname = class_name[len(class_name)-1]
        
        self.debug = "{}: {}".format(self.idname, self.label)

def _on_value_updated_redraw(prop : bpy.types.Property, context):
    context.area.tag_redraw()

def _show_data(layout:bpy.types.UILayout, context, data=[]):
    is_overflowing = True
    max_i = 21
    if max_i > len(data):
        max_i = len(data)
        is_overflowing = False
    for i in range(0, max_i):
        layout.label(text=data[i].debug)
    if is_overflowing:
        layout.label(text="...")

class OpGetIdByLabel(bpy.types.Operator):
    bl_idname = "learn_blender_ui.by_label"
    bl_label = "Learn ID by Label fragment"
    bl_description = "\
        By typing in a part of the label's text\
        you will get a list of ids for the ui elements that match"
    bl_options = {'REGISTER'}

    @staticmethod
    def _get_classes_by_label(label_fragment:str):
        result = []
        ui, headers, menus, operators, panels, ui_lists = get_ui_classes()
        label_fragment = label_fragment.lower()
        for class_container in ui:
            if not label_fragment:
                result.append(class_container)
                continue
            
            if label_fragment in class_container.label.lower():
                result.append(class_container)

        return result


    label_fragment : bpy.props.StringProperty(
        name="Label fragment",
        description="Part of the label that the search will be matching against",
        subtype='NONE',
        update=_on_value_updated_redraw
        )

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "label_fragment")

        user_input = self.label_fragment
        classes = OpGetIdByLabel._get_classes_by_label(user_input)

        if not user_input:
            return
        
        _show_data(layout, context, classes)

        

class OpGetIdById(bpy.types.Operator):
    bl_idname = "learn_blender_ui.by_id"
    bl_label = "Learn ID by ID fragment"
    bl_description = "\
        By typing in a part of the bl_idname\
        you will get a list of ids for the ui elements that match"
    bl_options = {'REGISTER'}

    @staticmethod
    def _get_classes_by_id(id_fragment:str):
        result = []
        ui, headers, menus, operators, panels, ui_lists = get_ui_classes()
        id_fragment = id_fragment.lower()
        for class_container in ui:
            if not id_fragment:
                result.append(class_container)
                continue
            
            if id_fragment in class_container.idname.lower():
                result.append(class_container)

        return result


    id_fragment : bpy.props.StringProperty(
        name="Id fragment",
        description="Part of the id that the search will be matching against",
        subtype='NONE',
        update=_on_value_updated_redraw
        )

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "id_fragment")

        user_input = self.id_fragment
        classes = OpGetIdById._get_classes_by_id(user_input)

        if not user_input:
            return

        _show_data(layout, context, classes)


# ------------------------------------------------------------------------
#    register and unregister functions
# ------------------------------------------------------------------------

classes = [
    OpGetIdByLabel,
    OpGetIdById,
]

addon_keymaps = []

def register():
    from bpy.utils import register_class

    addon_keymaps.clear()
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)

if __name__ == "__main__":
    register()