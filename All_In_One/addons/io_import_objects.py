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

# Todo:
#   - only preserve selected modifiers

bl_info = {
    "name": "Import object(s)",
    "author": "Jasper van Nieuwenhuizen",
    "version": (0, 1),
    "blender": (2, 6, 6),
    "location": "File > Import > Import object(s)",
    "description": "Import object(s) for use with pointcache importer",
    "warning": "wip",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Learnbgame"
}


import bpy
from bpy.props import (StringProperty,
                       CollectionProperty,
                       EnumProperty,
                       BoolProperty)
from bpy_extras.io_utils import ImportHelper
import addon_utils
import sys
from os import path, devnull
from glob import glob
import time


# Actual import operator.
class ImportObs(bpy.types.Operator, ImportHelper):

    '''Import object(s)'''
    bl_idname = "import_scene.obs"
    bl_label = "Import object(s)"
    bl_options = {'PRESET', 'UNDO'}

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    directory = StringProperty(
            maxlen=1024,
            subtype='DIR_PATH',
            options={'HIDDEN', 'SKIP_SAVE'})
    files = CollectionProperty(
            type=bpy.types.OperatorFileListElement,
            options={'HIDDEN', 'SKIP_SAVE'})

    filename_ext = ".obj"
    filter_glob = StringProperty(default="*.obj", options={'HIDDEN'})
    replace_existing = BoolProperty(
            name="Replace objects",
            description="Replace objects already present in the scene",
            default=True)
    copy_location = BoolProperty(
            name="Location",
            description="Copy the location from the old to the new object",
            default=True)
    copy_rotation = BoolProperty(
            name="Rotation",
            description="Copy the rotation from the old to the new object",
            default=True)
    copy_scale = BoolProperty(
            name="Scale",
            description="Copy the scale from the old to the new object",
            default=True)
    copy_modifiers_options = BoolProperty(
            name="Preserve modifiers",
            description="Copy the modifiers from the replaced object to the "\
                        "newly imported one",
            default=True)
    material_options = EnumProperty(
            name="Materials",
            items=[("scene",
                    "Scene",
                    "Use the materials that are now assigned to the objects "\
                    "(if they already exist), else don't assign materials"),
                   ("obj",
                    "From file",
                    "Use the materials from the OBJ"),
                   ("ignore",
                    "No Materials",
                    "Don't assign materials")],
            description="Select which materials to use for the imported models",
            default='scene')
    is_apply_rotation = BoolProperty(
            name="Apply rotation",
            description="Apply rotation after import",
            default=False)


    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.separator()
        col.prop(self, "is_apply_rotation")
        col.prop(self, "replace_existing")
        if self.replace_existing:
            box = col.box()
            subcol = box.column()
            subcol.label("Preserve transforms")
            row = subcol.row(align=True)
            row.prop(self, "copy_location", toggle=True)
            row.prop(self, "copy_rotation", toggle=True)
            row.prop(self, "copy_scale", toggle=True)
            subcol.separator()
            subcol.label("Preserve modifiers")
            subcol.prop(self, "copy_modifiers_options", text="All", toggle=True)
        col.separator()
        col.label("Materials")
        col.row().prop(self, "material_options", expand=True)

    def execute(self, context):
        start_time = time.time()
        print()
        d = self.properties.directory
        fils = self.properties.files
        if not fils[0].name:
            # No files selected, getting all obj's in the directory.
            import_files = glob(path.join(d, "*.[oO][bB][jJ]"))
        else:
            # Get the full path names for the files.
            import_files = [path.join(d, f.name) for f in fils]
        if import_files:
            # Import the objects and append them to "imported_list".
            imported_objects = []
            for progress, f in enumerate(import_files):
                obj = self.import_file(f)
                if obj:
                    imported_objects.append(obj)
                    if self.material_options == 'ignore':
                        self.remove_materials(obj)
                self.print_progress(progress, maximum=len(import_files) - 1)
            # Select all imported objects and make the last one the active object.
            # The obj importer already deselects previously selected objects.
            bpy.ops.object.select_all(action='DESELECT')
            for obj_name in imported_objects:
                bpy.context.scene.objects[obj_name].select = True
            context.scene.objects.active = bpy.context.scene.objects[imported_objects[-1]]

        print("\nFiles imported in {s:.2f} seconds".format(s=time.time() - start_time))

        return {'FINISHED'}

    # Helper functions
    def import_file(self, f):
        '''
        Imports an obj file and returns the name of the object
        '''

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        dvnull = open(devnull, 'w')
        sys.stdout = sys.stderr = dvnull

        # Check if obj importer is enabled
        if not addon_utils.check("io_scene_obj")[1]:
            # Enable it
            if not addon_utils.enable("io_scene_obj"):
                self.report({'ERROR'}, "could not load obj importer, aborting...")
        # try:
        bpy.ops.import_scene.obj(
            filepath=f,
            axis_forward='-Z',
            axis_up='Y',
            use_edges=True,
            use_smooth_groups=True,
            use_split_objects=False,
            use_split_groups=False,
            use_groups_as_vgroups=False,
            use_image_search=True,
            split_mode='OFF',
            global_clamp_size=0)
        # except AttributeError:
        #     self.report({'ERROR'}, "obj importer not loaded, aborting...")
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        return self.rename_object(f)

    def rename_object(self, f):
        '''
        Renames the object according to the file name and returns the name
        '''
        name = self.get_object_name(f)
        imported_object = bpy.context.selected_objects[0]
        if imported_object:
            if self.is_apply_rotation:
                self.apply_rotation(imported_object)
            if self.is_replace_object(name, imported_object):
                self.replace_object(self.get_object_name(f), imported_object)
            imported_object.name = imported_object.data.name = name
        else:
            print("File: {f} appears to be empty...".format(f=f))
        
        return name

    def is_replace_object(self, name, imported_object):
        '''
        Returns True if the imported object replaces an already existing one
        '''
        if name in bpy.context.scene.objects and self.replace_existing:
            if bpy.context.scene.objects[name] != imported_object:
                return True
        return False

    def get_object_name(self, f):
        '''
        Determines the object name from the file name
        '''
        return path.splitext(path.split(f)[1])[0]

    def replace_object(self, obj_name, obj_new):
        '''
        Replace existing object with new object and copy materials if wanted
        '''
        obj_old = bpy.context.scene.objects[obj_name]
        if self.material_options == 'scene':
            self.copy_materials(obj_new, obj_old)
        if self.copy_location:
            self.copy_transforms(obj_new, obj_old, 'location')
        if self.copy_rotation:
            self.copy_transforms(obj_new, obj_old, 'rotation')
        if self.copy_scale:
            self.copy_transforms(obj_new, obj_old, 'scale')
        if self.copy_modifiers_options:
            self.copy_modifiers(obj_new, obj_old)
        bpy.context.scene.objects.unlink(obj_old)

    def copy_materials(self, obj_copy_to, obj_copy_from):
        '''
        Copy materials from obj_copy_from to obj_copy_to
        '''
        bpy.ops.object.select_all(action='DESELECT')
        obj_copy_to.select = obj_copy_from.select = True
        bpy.context.scene.objects.active = obj_copy_from
        bpy.ops.object.make_links_data(type='MATERIAL')
        if len(obj_copy_to.data.polygons) > len(obj_copy_from.data.polygons):
            obj_iter = obj_copy_from
        else:
            obj_iter = obj_copy_to
        for p in obj_iter.data.polygons:
            pi = p.index
            mi = obj_copy_from.data.polygons[pi].material_index
            obj_copy_to.data.polygons[pi].material_index = mi

    def remove_materials(self, obj_name):
        '''
        Remove all materials from object with name obj_name
        '''
        obj = bpy.context.scene.objects[obj_name]
        bpy.context.scene.objects.active = obj
        for _ in obj.material_slots:
            bpy.ops.object.material_slot_remove()

    def copy_transforms(self, obj_new, obj_old, transform):
        '''
        Copy the given transformation from the old to the new object
        '''
        if transform == 'location':
            obj_new.location = obj_old.location
        if transform == 'rotation':
            obj_new.rotation_mode = obj_old.rotation_mode
            if obj_old.rotation_mode == 'AXIS_ANGLE':
                obj_new.rotation_axis_angle[0] = obj_old.rotation_axis_angle[0]
                obj_new.rotation_axis_angle[1] = obj_old.rotation_axis_angle[1]
                obj_new.rotation_axis_angle[2] = obj_old.rotation_axis_angle[2]
                obj_new.rotation_axis_angle[3] = obj_old.rotation_axis_angle[3]
            if obj_old.rotation_mode == 'QUATERNION':
                obj_new.rotation_quaternion = obj_old.rotation_quaternion
            else:
                obj_new.rotation_euler = obj_old.rotation_euler
        if transform == 'scale':
            obj_new.scale = obj_old.scale

    def copy_modifiers(self, obj_new, obj_old, modifiers='all'):
        '''
        Copy the specified modifiers from obj_old to obj_new
        '''
        print("*** Copying modifiers to {obj_new}...".format(obj_new=obj_new))
        bpy.ops.object.select_all(action='DESELECT')
        obj_new.select = obj_old.select = True
        bpy.context.scene.objects.active = obj_old
        if modifiers == 'all':
            bpy.ops.object.make_links_data(type='MODIFIERS')

    def apply_rotation(self, obj):
        '''
        Apply the object's rotation to its data
        '''
        bpy.context.scene.objects.active = obj
        bpy.ops.object.transform_apply(rotation=True)

    def print_progress(self, progress, minimum=0, maximum=100, barlen=50):
        if maximum <= minimum:
            return
        total_len = maximum - minimum
        bar_progress = int((progress - minimum) * barlen / total_len) * "="
        bar_empty = (barlen - int((progress - minimum) * barlen / total_len)) * " "
        percentage = "".join((str(int((progress - minimum) / total_len * 100)), "%"))
        print("".join(("[", bar_progress, bar_empty, "]", " ", percentage)), end="\r")


def menu_func_import(self, context):
    self.layout.operator(ImportObs.bl_idname, text="Import object(s)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
