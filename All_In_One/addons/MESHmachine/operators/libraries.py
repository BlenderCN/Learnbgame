import bpy
import os
from bpy.props import StringProperty, EnumProperty
from shutil import rmtree
from ..utils import MACHIN3 as m3
from ..utils.ui import popup_message
from ..utils.registration import reload_plug_libraries


def get_lib():
    idx = m3.MM_prefs().pluglibsIDX
    libs = m3.MM_prefs().pluglibsCOL
    active = libs[idx]

    return idx, libs, active


class Move(bpy.types.Operator):
    bl_idname = "machin3.move_plug_library"
    bl_label = "MACHIN3: Move Plug Library"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Move library up or down.\nThis controls the position in the MESHmachine Plug Libraries submenu.\nSave prefs to remember"

    direction = EnumProperty(items=[("UP", "Up", ""),
                                    ("DOWN", "Down", "")])

    def execute(self, context):
        idx, libs, _ = get_lib()

        if self.direction == "UP":
            nextidx = max(idx - 1, 0)
        elif self.direction == "DOWN":
            nextidx = min(idx + 1, len(libs) - 1)

        libs.move(idx, nextidx)
        m3.MM_prefs().pluglibsIDX = nextidx

        return {'FINISHED'}


class Clear(bpy.types.Operator):
    bl_idname = "machin3.clear_plug_libraries"
    bl_label = "MACHIN3: Clear Plug Libraries"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear library prefs, resets them into their original state.\nNo plugs will be lost!\nSave prefs and restart Blender to complete the process"

    def execute(self, context):
        m3.MM_prefs().pluglibsCOL.clear()

        return {'FINISHED'}


class Reload(bpy.types.Operator):
    bl_idname = "machin3.reload_plug_libraries"
    bl_label = "MACHIN3: Reload Plug Libraries"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Reload all libraries. Propagates forced lock settings.\nSave prefs to complete the process"

    def execute(self, context):
        reload_plug_libraries()

        return {'FINISHED'}


class Add(bpy.types.Operator):
    bl_idname = "machin3.add_plug_library"
    bl_label = "MACHIN3: Add Plug Library"
    bl_description = "Add a new empty library"

    @classmethod
    def poll(cls, context):
        return m3.MM_prefs().newpluglibraryname

    def execute(self, context):
        assetspath = m3.MM_prefs().assetspath
        name = m3.MM_prefs().newpluglibraryname

        if os.path.exists(os.path.join(assetspath, name)):
            popup_message("This library exists already, choose another name!", title="Failed to add library", icon="ERROR")
        else:
            self.create_new_library(assetspath, name)
            m3.MM_prefs().newpluglibraryname = ""
            reload_plug_libraries()

        return {'FINISHED'}

    def create_new_library(self, assetspath, name):
        blendspath = os.path.join(assetspath, name, "blends")
        iconspath = os.path.join(assetspath, name, "icons")

        m3.makedir(blendspath)
        print(" » Created folder '%s'" % (blendspath))
        m3.makedir(iconspath)
        print(" » Created folder '%s'" % (iconspath))


class Open(bpy.types.Operator):
    bl_idname = "machin3.open_plug_library"
    bl_label = "MACHIN3: Open Plug Library"
    bl_description = "Open selected library in file browser"

    def execute(self, context):
        _, _, self.active = get_lib()
        assetspath = m3.MM_prefs().assetspath
        libpath = os.path.join(assetspath, self.active.name)

        if os.path.exists(libpath):
            m3.open_folder(libpath)
        else:
            popup_message("Library path could not be found, reload libraries or restart Blender.", title="Could not find library path", icon="ERROR")

        return {'FINISHED'}


class Rename(bpy.types.Operator):
    bl_idname = "machin3.rename_plug_library"
    bl_label = "Rename Plug Library"
    bl_description = "Rename selected library"

    newlibname = StringProperty(name="New Name")

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.split(percentage=0.31)
        row.label("Old Name")
        row.label(self.active.name)

        column.prop(self, "newlibname")

    def invoke(self, context, event):
        _, _, self.active = get_lib()

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        assetspath = m3.MM_prefs().assetspath
        oldlibpath = os.path.join(assetspath, self.active.name)
        oldlibname = self.active.name

        if self.newlibname:
            if self.newlibname != oldlibname:
                newlibpath = os.path.join(assetspath, self.newlibname)
                if not os.path.exists(newlibpath):
                    os.rename(oldlibpath, newlibpath)
                    reload_plug_libraries()
                    print(" » Renamed library %s to %s" % (oldlibname, self.newlibname))
                else:
                    popup_message("This library exists already, choose another name!", title="Failed to add library", icon="ERROR")
            else:
                popup_message("The new name needs to be different from the old one.", title="Failed to rename library", icon="ERROR")
        else:
            popup_message("No new name chosen.", title="Failed to rename library", icon="ERROR")

        return {'FINISHED'}

    def rename_library(self, assetspath, name):
        blendspath = os.path.join(assetspath, name, "blends")
        iconspath = os.path.join(assetspath, name, "icons")

        m3.makedir(blendspath)
        print(" » Created folder '%s'" % (blendspath))
        m3.makedir(iconspath)
        print(" » Created folder '%s'" % (iconspath))


class Remove(bpy.types.Operator):
    bl_idname = "machin3.remove_plug_library"
    bl_label = "Remove Plug Library"
    bl_description = "Removes selected plug library and all its plugs"

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        layout.label("This removes the plug library '%s' and all its plugs!" % self.active.name, icon='ERROR')
        layout.label("Are you sure? This cannot be undone!")


    def invoke(self, context, event):
        _, _, self.active = get_lib()

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


    def execute(self, context):
        assetspath = m3.MM_prefs().assetspath

        path = os.path.join(assetspath, self.active.name)

        if os.path.exists(path):
            rmtree(path)
            reload_plug_libraries()
            popup_message("for all plugs lost to eternity :(", title="A moment of silence", icon="INFO")
        else:
            popup_message("Have you already removed it manualy, while Blender was running?", title="Library '%s' not found" % self.library, icon="ERROR")

        return {'FINISHED'}
