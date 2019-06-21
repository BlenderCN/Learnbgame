import bpy
import os
from bpy.props import StringProperty, EnumProperty
from shutil import rmtree
from ..utils.ui import popup_message, get_icon
from ..utils.registration import get_prefs, get_path, reload_decal_libraries
from ..utils.library import get_lib


class Move(bpy.types.Operator):
    bl_idname = "machin3.move_decal_library"
    bl_label = "MACHIN3: Move Decal Library"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Move library up or down.\nThis controls the position in the DECALmachine pie menu.\nSave prefs to remember"

    direction: EnumProperty(items=[("UP", "Up", ""),
                                   ("DOWN", "Down", "")])

    def execute(self, context):
        idx, libs, _ = get_lib()

        if self.direction == "UP":
            nextidx = max(idx - 1, 0)
        elif self.direction == "DOWN":
            nextidx = min(idx + 1, len(libs) - 1)

        libs.move(idx, nextidx)
        get_prefs().decallibsIDX = nextidx

        return {'FINISHED'}


class Clear(bpy.types.Operator):
    bl_idname = "machin3.clear_decal_libraries"
    bl_label = "MACHIN3: Clear Decal Libraries"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear library prefs, resets them into their original state.\nNo decals will be lost!\nSave prefs and restart Blender to complete the process"

    def execute(self, context):
        get_prefs().decallibsCOL.clear()

        return {'FINISHED'}


class Reload(bpy.types.Operator):
    bl_idname = "machin3.reload_decal_libraries"
    bl_label = "MACHIN3: Reload Decal Libraries"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Reload all libraries. Propagates lock and slice settings.\nSave prefs to complete the process"

    def execute(self, context):
        reload_decal_libraries()

        return {'FINISHED'}


class Rename(bpy.types.Operator):
    bl_idname = "machin3.rename_decal_library"
    bl_label = "Rename Decal Library"
    bl_description = "Rename selected library"

    newlibname: StringProperty(name="New Name")

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.split(factor=0.25)
        row.label(text="Old Name:")
        row.label(text=self.active.name)

        row = column.split(factor=0.25)
        row.label(text="New Name:")
        row.prop(self, "newlibname", text="")

    @classmethod
    def poll(cls, context):
        _, _, active = get_lib()
        return active and not active.islocked

    def invoke(self, context, event):
        _, _, self.active = get_lib()

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        assetspath = get_prefs().assetspath
        oldlibpath = os.path.join(assetspath, self.active.name)
        oldlibname = self.active.name

        newlibname = self.newlibname.strip()

        if newlibname:
            if newlibname != oldlibname:
                newlibpath = os.path.join(assetspath, newlibname)
                if not os.path.exists(newlibpath):
                    os.rename(oldlibpath, newlibpath)
                    reload_decal_libraries()

                    print(" » Renamed library %s to %s" % (oldlibname, newlibname))
                    self.newlibname = ""
                else:
                    popup_message("This library exists already, choose another name!", title="Failed to add library", icon="ERROR")
            else:
                popup_message("The new name needs to be different from the old one.", title="Failed to rename library", icon="ERROR")
        else:
            popup_message("No new name chosen.", title="Failed to rename library", icon="ERROR")

        return {'FINISHED'}


class Remove(bpy.types.Operator):
    bl_idname = "machin3.remove_decal_library"
    bl_label = "Remove Decal Library"
    bl_description = "Removes selected decal library and all its decals"

    def draw(self, context):
        layout = self.layout

        layout.label(text="This removes the decal library '%s' and all its decals!" % self.active.name, icon_value=get_icon("error"))
        layout.label(text="Are you sure? This cannot be undone!")

    @classmethod
    def poll(cls, context):
        _, _, active = get_lib()
        return active and not active.islocked

    def invoke(self, context, event):
        _, libs, self.active = get_lib()

        unlockedlibs = [lib for lib in libs if not lib.islocked]

        if unlockedlibs == [self.active]:
            popup_message("You can't remove the only unlocked library!")
            return {'FINISHED'}
        else:
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=400)


    def execute(self, context):
        assetspath = get_prefs().assetspath

        path = os.path.join(assetspath, self.active.name)

        if os.path.exists(path):
            rmtree(path)
        else:
            popup_message("Have you already removed it manualy, while Blender was running?", title="Library '%s' not found" % self.library, icon="ERROR")

        reload_decal_libraries()

        return {'FINISHED'}


class ResetDecalsLocation(bpy.types.Operator):
    bl_idname = "machin3.reset_decals_location"
    bl_label = "Reset Decals Folder Location"
    bl_description = "Resets Decals Folder Location to DECALmachine/assets/Decals"

    def execute(self, context):
        get_prefs().assetspath = os.path.join(get_path(), "assets", "Decals")

        return {'FINISHED'}
