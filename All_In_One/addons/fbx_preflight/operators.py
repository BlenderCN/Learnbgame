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

import bpy
import os
import re

from . import helpers


class MigratePreflightGroups(bpy.types.Operator):
    bl_idname = "preflight.migrate_groups"
    bl_label = "Migrate Preflight Groups"
    bl_description = "Migrate Preflight Groups from 2.78 to 2.8x"

    def execute(self, context):
        groups = context.scene.preflight_props.fbx_export_groups
        for group_idx, group in enumerate(groups):
            for obj_idx, obj in enumerate(group.obj_names):
                if obj.obj_name and obj.obj_pointer is None:
                    data = bpy.data.objects.get(obj.obj_name)
                    if data is not None:
                        print('Migrating ' + obj.obj_name)
                        obj.obj_pointer = data

        return {'FINISHED'}


class AddSelectionToPreflightGroup(bpy.types.Operator):
    bl_idname = "preflight.add_selection_to_group"
    bl_label = "Add Selection"
    bl_description = "Add Selection to an export group"

    group_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            for idx, obj in enumerate(context.selected_objects):
                group_names = context.scene.preflight_props.fbx_export_groups[
                    self.group_idx].obj_names
                item = group_names.add()
                item.obj_pointer = obj

            helpers.redraw_properties()
        else:
            message = 'Group Index is not Set'
            self.report({'ERROR'}, message)
            raise ValueError(message)

        return {'FINISHED'}


class AddPreflightObjectOperator(bpy.types.Operator):
    bl_idname = "preflight.add_object_to_group"
    bl_label = "Add Object"
    bl_description = "Add an object to this export group."

    group_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            context.scene.preflight_props.fbx_export_groups[
                self.group_idx].obj_names.add()
            helpers.redraw_properties()

        return {'FINISHED'}


class RemovePreflightObjectOperator(bpy.types.Operator):
    bl_idname = "preflight.remove_object_from_group"
    bl_label = "Remove Object"
    bl_description = "Remove object from this export group."

    group_idx = bpy.props.IntProperty()
    object_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None and self.object_idx is not None:
            context.scene.preflight_props.fbx_export_groups[
                self.group_idx].obj_names.remove(self.object_idx)
            helpers.redraw_properties()

        return {'FINISHED'}


class AddPreflightExportGroupOperator(bpy.types.Operator):
    bl_idname = "preflight.add_export_group"
    bl_label = "Add Export Group"
    bl_description = "Add an export group. Each group will be exported to its own .fbx file with all selected objects."

    def execute(self, context):
        groups = context.scene.preflight_props.fbx_export_groups
        new_group = groups.add()
        new_group.name = "Export Group {0}".format(str(len(groups)))
        helpers.redraw_properties()
        return {'FINISHED'}


class RemovePreflightExportGroupOperator(bpy.types.Operator):
    bl_idname = "preflight.remove_export_group"
    bl_label = "Remove Export Group"
    bl_description = "Remove an export group."

    group_idx = bpy.props.IntProperty()

    def execute(self, context):
        if self.group_idx is not None:
            context.scene.preflight_props.fbx_export_groups.remove(
                self.group_idx)
            helpers.redraw_properties()
        return {'FINISHED'}


class ExportMeshGroupsOperator(bpy.types.Operator):
    bl_idname = "preflight.export_groups"
    bl_label = "Export All Groups"
    bl_description = "Export all export groups to the chosen export destination."

    @classmethod
    def poll(cls, context):
        """
        Poll for ability to perform export. Only return
        true if there is at least 1 group, and all objects
        in export groups are set.
        """

        groups = context.scene.preflight_props.fbx_export_groups

        if len(groups) < 1:
            return False

        for group in groups:
            if len(group.obj_names) < 1:
                return False

            for obj in group.obj_names:
                if not obj.obj_pointer:
                    return False

        return True

    def execute(self, context):
        # SANITY CHECK
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "File must be saved before exporting.")
            return {'CANCELLED'}

        # SETUP
        groups = context.scene.preflight_props.fbx_export_groups

        # SAFETY CHECK
        if not helpers.groups_are_unique(groups):
            self.report(
                {'WARNING'}, "Cannot export with duplicate group names.")
            return {'CANCELLED'}

        if len(groups) < 1:
            self.report(
                {'WARNING'}, "Must have at least 1 export group to export files.")
            return {'CANCELLED'}

        # DO GROUP EXPORT
        for group_idx, group in enumerate(groups):
            try:
                self.export_group(group, context)
                self.report({'INFO'}, "Exported Group {0} of {1} Successfully.".format(
                    group_idx+1, len(groups)))
            except Exception as e:
                print(e)
                self.report(
                    {'ERROR'}, "There was an error while exporting: {0}.".format(group.name))
                return {'CANCELLED'}

        # DO ANIMATION EXPORT
        if context.scene.preflight_props.export_options.separate_animations:
            try:
                self.export_animations(context)
            except Exception as e:
                print(e)
                self.report(
                    {'ERROR'}, "There was an error while exporting animations")
                return {'CANCELLED'}

        # FINISH
        self.report(
            {'INFO'}, "Exported {0} Groups Successfully.".format(len(groups)))
        return {'FINISHED'}

    def prepare_objects(self, objects):
        self.select_objects(objects)
        return bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

    def duplicate_objects(self, objects, context):
        duplicates = []

        for src_obj in objects:
            new_obj = src_obj.copy()
            new_obj.data = src_obj.data.copy()
            context.scene.objects.link(new_obj)
            duplicates.append(new_obj)

        return duplicates

    def delete_objects(self, objects):
        self.select_objects(objects)
        return bpy.ops.object.delete()

    def select_objects(self, objects, append_selection=False):
        """
        Select all objects, raise an error if the object
        does not exist.
        """
        if not append_selection:
            bpy.ops.object.select_all(action='DESELECT')

        for obj in objects:
            if obj is not None:
                obj.select = True
            else:
                message = error_message_for_obj_name(obj.name)
                self.report({'ERROR'}, message)
                raise ValueError(message)

        return True

    def export_objects(self, objects, filepath, **kwargs):
        self.select_objects(objects)

        # Do Export
        export_opts = kwargs
        export_opts['filepath'] = filepath

        bpy.ops.export_scene.fbx(**export_opts)

        # Deselect Objects
        bpy.ops.object.select_all(action='DESELECT')

    def export_group(self, group, context):
        """
        Export an export group according to its options and
        included objects.
        """

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Validate that we have objects
        if len(group.obj_names) < 1:
            message = "Must have at least 1 mesh to export group."
            self.report({'WARNING'}, message)
            raise ValueError(message)

        # Validate export path
        export_path = export_path_for_string(group.name, context.scene)

        if not ensure_export_path(export_path):
            raise ValueError("Invalid Export Path")

        # Export files
        original_objects = [context.scene.objects.get(
            obj.obj_pointer.name) for obj in group.obj_names]
        duplicate_objects = self.duplicate_objects(original_objects, context)
        export_options = context.scene.preflight_props.export_options.get_options_dict(
            use_anim=group.include_animations,
            use_mesh_modifiers=group.apply_modifiers
        )

        self.prepare_objects(duplicate_objects)
        self.export_objects(duplicate_objects, export_path, **export_options)
        self.delete_objects(duplicate_objects)

    def export_animations(self, context):
        """
        Export each armature in the current context with all
        animations attached.
        """
        export_options = context.scene.preflight_props.export_options.defaults_for_unity(
            object_types={'ARMATURE'})
        print(export_options)

        for obj in context.scene.objects:
            if obj.type != 'ARMATURE':
                continue
            export_path = export_path_for_string(
                obj.name, context.scene, suffix="@animations")
            if not ensure_export_path(export_path):
                raise ValueError("Invalid Export Path")
            self.export_objects([obj], export_path, **export_options)


class ResetExportOptionsOperator(bpy.types.Operator):
    bl_idname = "preflight.reset_export_options"
    bl_label = "Reset Export Options"
    bl_description = "Reset all export options to default values."

    def execute(self, context):
        export_options = context.scene.preflight_props.export_options
        export_options.reset(export_options.defaults_for_unity().items())
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


def ensure_export_path(export_path):
    try:
        export_dir = os.path.dirname(export_path)
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
    except:
        return False

    return True


def filename_for_string(s, suffix=""):
    """Determine Filename for String"""
    filepath = bpy.data.filepath
    filename = os.path.splitext(os.path.basename(filepath))[0]
    return "{0}-{1}{2}.fbx".format(helpers.to_camelcase(filename), helpers.to_camelcase(s), suffix)


def export_path_for_string(s, scene, suffix=""):
    """Determine the export path for an export group."""
    filename = filename_for_string(s, suffix=suffix)
    directory = bpy.path.abspath(
        scene.preflight_props.export_options.export_location)
    return os.path.join(directory, filename)


def error_message_for_obj_name(obj_name=""):
    """
    Determine the error message for a given object name.

    Keyword arguments:
    obj_name -- name of the object for error message (default "")
    """

    if not obj_name:
        return "Cannot export empty object."
    else:
        return 'Object "{0}" could not be found.'.format(obj_name)
