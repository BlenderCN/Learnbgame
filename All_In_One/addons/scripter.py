# Copyright (c) 2019 ywabygl@gmail.com
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

bl_info = {
    "name": "scripter",
    "author": "ywaby",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "description": "make script easier",
    "warning": "",
    "wiki_url": "http://github.com"
                "Scripts/Add_Mesh/Planes_from_Images",
    "tracker_url": "http://github.com",
    "support": "TESTING",
    "category": "Learnbgame",
}


import os
import sys
import subprocess
import bpy
#from bpy_extras.io_utils import ImportHelper
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    IntProperty,
    FloatProperty,
    CollectionProperty,
    BoolVectorProperty,
    PointerProperty
)
from bpy.types import (
    Operator,
    AddonPreferences,
    Panel,
    PropertyGroup
)



class DebugExt(Operator):
    """Establish remote debug"""
    bl_label = 'Establish remote debug'
    bl_idname = 'scripter.establish_remote_debug'

    def execute(self, context):
        import ptvsd
        ptvsd.enable_attach("my_secret", address=('127.0.0.1', 3000))
        ptvsd.wait_for_attach()
        return {'FINISHED'}


class ReopenBlend(Operator):
    """Repoen current blend file"""
    bl_label = "Reopen current Blend file"
    bl_idname = "scripter.reopen"

    def execute(self, context):
        subprocess.Popen([bpy.app.binary_path, bpy.data.filepath])
        bpy.ops.wm.quit_blender()
        return {"FINISHED"}


class PyPathItem(PropertyGroup):
    path: StringProperty(name="Path", default="", subtype='DIR_PATH')
    enable: BoolProperty(name="Enable", default=True)


class AddPyExPath(Operator):
    bl_label = "Add A Python Path"
    bl_idname = "scripter.add_py_ex_path"
    @classmethod
    def poll(cls, context):
        return (
            context.area.type == 'PREFERENCES'
        )
    def execute(self, context):
        context.preferences.addons[__name__].preferences.py_extra_paths.add()
        return {'FINISHED'}


class RemovePyExPath(Operator):
    bl_label = "Remove A Python Path"
    bl_idname = "scripter.rm_py_ex_path"
    idx: IntProperty(description='remove index')
    @classmethod
    def poll(cls, context):
        return (
            context.area.type == 'PREFERENCES'
        )
    def execute(self, context):
        context.preferences.addons[__name__].preferences.py_extra_paths.remove(
            self.idx)
        return {'FINISHED'}


class AddExAddon(Operator):
    bl_label = "Add A Addon"
    bl_idname = "scripter.add_py_ex_addon"

    def execute(self, context):
        context.preferences.addons[__name__].preferences.py_extra_paths.add()
        return {'FINISHED'}


class RemoveExAddon(Operator):
    bl_label = "Remove A Addon"
    bl_idname = "scripter.rm_py_ex_path"
    idx: IntProperty(description='remove index')

    def execute(self, context):
        context.preferences.addons[__name__].preferences.py_extra_paths.remove(
            self.idx)
        return {'FINISHED'}

class OpenTextWithExternalEditor(Operator):
    bl_label = "Open Text With external Editor"
    bl_idname = "scripter.open_with_external"
    
    @classmethod
    def poll(cls, context):
        return (
            context.area.type == 'TEXT_EDITOR' and
            context.edit_text and
            context.edit_text.filepath and
            context.preferences.addons[__name__].preferences.external_text_editor!=''
        )

    def execute(self, context): #TODO support 空格
        text = context.edit_text
        if text.filepath:
            import subprocess
            real_path=bpy.path.abspath(text.filepath)
            editor = context.preferences.addons[__name__].preferences.external_text_editor
            editor=editor.format(filepath=real_path)
            editor = editor.split()
            subprocess.Popen(editor)
        else:# TODO open as tmp text
            tmp_path=os.path.join('/tmp',text.name)
            text.as_string()
        return {'FINISHED'}




class SCRIPTER_PT_tools(Panel):
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Scripter"
    bl_category = 'Scripter'

    def draw(self, context):
        layout = self.layout
        st = context.space_data
        layout.operator(ReopenBlend.bl_idname, icon="BLENDER")
        layout.operator(OpenTextWithExternalEditor.bl_idname, icon="TEXT")


class Preference(AddonPreferences):
    bl_idname = __name__
    py_extra_paths: CollectionProperty(
        type=PyPathItem)  # TODO update when value change
    extra_addon_path: CollectionProperty(type=PyPathItem)
    py_extra_paths_enable: BoolProperty(name='Python Extra Paths',
                                        default=False)
    extra_addon_enable: BoolProperty(name='Extra Addons', default=False)
    external_text_editor: StringProperty(name='External Text Editor', default='',
                                         description='for example "code {filepath}"',
                                         )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'external_text_editor')
        row = layout.row()
        row.prop(self, "py_extra_paths_enable")
        row.operator("scripter.add_py_ex_path",
                     icon='ADD', text='', emboss=False)
        # Python Extra Paths
        box = layout.box()
        box.active = self.py_extra_paths_enable
        for i, path in enumerate(self.py_extra_paths):
            row = box.row()
            row = box.row()
            row.prop(path, "enable", text="")
            row.prop(path, "path", text="")
            row.operator("scripter.rm_py_ex_path", text="",
                         icon='X', emboss=False).idx = i
        # TODO extra addons when support
        # row = layout.row()
        # row.prop(self, "extra_addon_enable")
        # row.operator("scripter.add_py_ex_path",
        #              icon='ADD', text='', emboss=False)
        # box = layout.box()  # Python Extra Path
        # box.active = self.extra_addon_enable


classes = [PyPathItem,
           Preference,
           AddPyExPath,
           RemovePyExPath,
           DebugExt,
           ReopenBlend,
           SCRIPTER_PT_tools,
           OpenTextWithExternalEditor
           ]


def init():
    preference = bpy.context.preferences.addons[__name__].preferences
    if preference.py_extra_paths_enable:
        for path in preference.py_extra_paths:
            if path.enable:
                sys.path.append(path.path)


def register():
    import sys
    for cls in classes:
        bpy.utils.register_class(cls)
    init()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
