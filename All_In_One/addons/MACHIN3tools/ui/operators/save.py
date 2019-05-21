import bpy
from bpy.props import StringProperty, BoolProperty
import bmesh
import os
import re
import time
from ... utils.registration import get_prefs, get_addon
from ... utils.append import append_material, append_world
from ... utils.system import add_path_to_recent_files
from ... utils import MACHIN3 as m3



class New(bpy.types.Operator):
    bl_idname = "machin3.new"
    bl_label = "Current file is unsaved. Start a new file anyway?"
    bl_options = {'REGISTER'}


    def execute(self, context):
        bpy.ops.wm.read_homefile(app_template="")

        return {'FINISHED'}

    def invoke(self, context, event):
        if bpy.data.is_dirty:
            return context.window_manager.invoke_confirm(self, event)
        else:
            bpy.ops.wm.read_homefile(app_template="")
            return {'FINISHED'}


# TODO: file size output

class Save(bpy.types.Operator):
    bl_idname = "machin3.save"
    bl_label = "Save"
    bl_description = "Save"
    bl_options = {'REGISTER'}

    def execute(self, context):
        currentblend = bpy.data.filepath

        if currentblend:
            bpy.ops.wm.save_mainfile()

            t = time.time()
            localt = time.strftime('%H:%M:%S', time.localtime(t))

            print("%s | Saved blend: %s" % (localt, currentblend))
        else:
            bpy.ops.wm.save_mainfile('INVOKE_DEFAULT')

        return {'FINISHED'}


class SaveIncremental(bpy.types.Operator):
    bl_idname = "machin3.save_incremental"
    bl_label = "Incremental Save"
    bl_description = "Incremental Save"
    bl_options = {'REGISTER'}


    def execute(self, context):
        currentblend = bpy.data.filepath

        if currentblend:
            save_path = self.get_incremented_path(currentblend)

            # add it to the recent files list
            add_path_to_recent_files(save_path)

            if os.path.exists(save_path):
                self.report({'ERROR'}, "File '%s' exists already!\nBlend has NOT been saved incrementally!" % (save_path))
            else:
                bpy.ops.wm.save_as_mainfile(filepath=save_path)
                print("Saved blend incrementally:", save_path)
        else:
            bpy.ops.wm.save_mainfile('INVOKE_DEFAULT')

        return {'FINISHED'}


    def get_incremented_path(self, currentblend):
        path = os.path.dirname(currentblend)
        filename = os.path.basename(currentblend)

        filenameRegex = re.compile(r"(.+)\.blend\d*$")

        mo = filenameRegex.match(filename)

        if mo:
            name = mo.group(1)
            numberendRegex = re.compile(r"(.*?)(\d+)$")

            mo = numberendRegex.match(name)

            if mo:
                basename = mo.group(1)
                numberstr = mo.group(2)
            else:
                basename = name + "_"
                numberstr = "000"

            number = int(numberstr)

            incr = number + 1
            incrstr = str(incr).zfill(len(numberstr))
            incrname = basename + incrstr + ".blend"

            return os.path.join(path, incrname)


class LoadMostRecent(bpy.types.Operator):
    bl_idname = "machin3.load_most_recent"
    bl_label = "Load Most Recent"
    bl_options = {"REGISTER"}

    def execute(self, context):
        recent_path = bpy.utils.user_resource('CONFIG', "recent-files.txt")

        try:
            with open(recent_path) as file:
                recent_files = file.read().splitlines()
        except (IOError, OSError, FileNotFoundError):
            recent_files = []

        if recent_files:
            most_recent = recent_files[0]

            # load_ui ensures the the viewport location/angle is loaded as well
            bpy.ops.wm.open_mainfile(filepath=most_recent, load_ui=True)

        return {'FINISHED'}


class AppendWorld(bpy.types.Operator):
    bl_idname = "machin3.append_world"
    bl_label = "Append World"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return get_prefs().appendworldpath and get_prefs().appendworldname

    def draw(self, context):
        layout = self.layout

        column = layout.column()

    def execute(self, context):
        path = get_prefs().appendworldpath
        name = get_prefs().appendworldname

        world = append_world(path, name)

        if world:
            bpy.context.scene.world = world
        else:
            self.report({'ERROR'}, "World '%s' could not be appended.\nMake sure a world of that name exists in the world source file." % (name))

        return {'FINISHED'}


class AppendMaterial(bpy.types.Operator):
    bl_idname = "machin3.append_material"
    bl_label = "Append Material"
    bl_description = "Append material, or apply if it's already in the scene.\nSHIFT: Force append material, even if it's already in the scene."
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty(name="Append Name")

    applymaterial: BoolProperty(name="Apply Material to Selection", default=True)


    @classmethod
    def poll(cls, context):
        return get_prefs().appendmatspath

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "applymaterial")

    def invoke(self, context, event):
        path = get_prefs().appendmatspath
        name = self.name

        if name == "ALL":
            all_names = [mat.name for mat in get_prefs().appendmats]

            for name in all_names:
                if name != "---":
                    append_material(path, name)
        else:
            mat = bpy.data.materials.get(name)

            if not mat or event.shift:
                mat = append_material(path, name)

            if mat:
                if self.applymaterial:
                    meshes = [obj for obj in context.selected_objects if obj.type in ["MESH", "SURFACE", "CURVE", "FONT", "META"]]

                    decalmachine, _, _, _ = get_addon("DECALmachine")

                    if decalmachine:
                        meshes = [obj for obj in meshes if not obj.DM.isdecal]

                    for obj in meshes:
                        # append material when there are no slots[creates a new slot automatically, as well as when in edit mode
                        if not obj.material_slots or obj.mode == "EDIT":
                            obj.data.materials.append(mat)
                            idx = len(obj.data.materials) - 1

                            if obj.mode == "EDIT":
                                bm = bmesh.from_edit_mesh(obj.data)
                                bm.normal_update()

                                faces = [f for f in bm.faces if f.select]

                                for face in faces:
                                    face.material_index = idx

                                bmesh.update_edit_mesh(obj.data)


                        # other wise just set the first slot's material
                        else:
                            obj.material_slots[0].material = mat

            else:
                self.report({'ERROR'}, "Material '%s' could not be appended.\nMake sure a material of that name exists in the material source file." % (name))

        return {'FINISHED'}


class LoadWorldSource(bpy.types.Operator):
    bl_idname = "machin3.load_world_source"
    bl_label = "Load World Source"
    bl_description = "Load World Source File"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return get_prefs().appendworldpath


    def execute(self, context):
        appendworldpath = get_prefs().appendworldpath

        if os.path.exists(appendworldpath):
            bpy.ops.wm.open_mainfile(filepath=appendworldpath, load_ui=True)

        return {'FINISHED'}


class LoadMaterialsSource(bpy.types.Operator):
    bl_idname = "machin3.load_materials_source"
    bl_label = "Load Materials Source"
    bl_description = "Load Materials Source File"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return get_prefs().appendmatspath

    def execute(self, context):
        appendmatspath = get_prefs().appendmatspath

        if os.path.exists(appendmatspath):
            bpy.ops.wm.open_mainfile(filepath=appendmatspath, load_ui=True)

        return {'FINISHED'}


class LoadPrevious(bpy.types.Operator):
    bl_idname = "machin3.load_previous"
    bl_label = "Load Previous"
    bl_description = "Load Previous Blend File in Current Folder"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bpy.data.filepath

    def execute(self, context):
        filepath = bpy.data.filepath


        # """

        if filepath:
            currentpath = os.path.dirname(filepath)
            currentblend = os.path.basename(filepath)

            blendfiles = [f for f in sorted(os.listdir(currentpath)) if f.endswith(".blend")]

            index = blendfiles.index(currentblend)

            previousidx = index - 1

            if previousidx >= 0:
                previousblend = blendfiles[previousidx]


                loadpath = os.path.join(currentpath, previousblend)

                # add the path to the recent files list, for some reason it's not done automatically
                add_path_to_recent_files(loadpath)


                print("Loading blend file %d/%d: %s" % (previousidx + 1, len(blendfiles), previousblend))
                bpy.ops.wm.open_mainfile(filepath=loadpath, load_ui=True)
            else:
                self.report({'ERROR'}, "You've reached the first file in the current foler: %s." % (currentpath))



        return {'FINISHED'}


class LoadNext(bpy.types.Operator):
    bl_idname = "machin3.load_next"
    bl_label = "Load Next"
    bl_description = "Load Next Blend File in Current Folder"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bpy.data.filepath

    def execute(self, context):
        filepath = bpy.data.filepath

        if filepath:
            currentpath = os.path.dirname(filepath)
            currentblend = os.path.basename(filepath)

            blendfiles = [f for f in sorted(os.listdir(currentpath)) if f.endswith(".blend")]

            index = blendfiles.index(currentblend)

            nextidx = index + 1

            if nextidx < len(blendfiles):
                nextblend = blendfiles[nextidx]

                loadpath = os.path.join(currentpath, nextblend)

                # add the path to the recent files list, for some reason it's not done automatically
                add_path_to_recent_files(loadpath)

                print("Loading blend file %d/%d: %s" % (nextidx + 1, len(blendfiles), nextblend))
                bpy.ops.wm.open_mainfile(filepath=loadpath, load_ui=True)
            else:
                self.report({'ERROR'}, "You've reached the last file in the current foler: %s." % (currentpath))

        return {'FINISHED'}
