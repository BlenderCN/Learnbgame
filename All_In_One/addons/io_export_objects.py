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

bl_info = {
    "name": "Objects exporter (obj)",
    "description": "Export all (selected objects) as obj's.",
    "author": "jasperge",
    "version": (0, 8),
    "blender": (2, 6, 3),
    "location": "File > Export",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ExportHelper
from math import degrees
from os import path
from time import time


def check_exporters():
    # Check if .obj exporter is enabled or try to enable it.
    try:
        bpy.ops.export_scene.obj.poll()
    except:
        try:
            bpy.ops.wm.addon_enable(module="io_scene_obj")
            print("*******\n.obj export enabled...\n*******")
        except:
            raise RuntimeError("Could not enable .obj export...")


def solo_select_object(ob):
    """
    Only select obj and make it the active object
    """
    print(ob)
    for obj in bpy.data.objects:
        obj.select = False
    ob.select = True
    bpy.context.scene.objects.active = ob


def write_transforms(objects, obj_dir):

    def get_transforms(objects):
        transform_dict = {}

        for obj in objects:
            matrix_world = obj.matrix_world
            loc = tuple(matrix_world.to_translation())
            loc = (loc[0], loc[2], -loc[1])
            rot = tuple(matrix_world.to_euler())
            rot = (degrees(rot[0]), degrees(rot[2]), -degrees(rot[1]))
            scale = tuple(matrix_world.to_scale())
            scale = (scale[0], scale[2], scale[1])
            transform_dict[obj.name] = (loc, rot, scale)

        return transform_dict

    def write_transforms_file(transform_file, transforms):
        transform_dict = transforms
        with open(transform_file, 'w') as f:
            f.write(str(transform_dict))

    filename = "transforms.txt"
    f = path.join(obj_dir, filename)
    write_transforms_file(f, get_transforms(objects))
    print("Exported the transforms to {f}".format(f=f))


def export_object(**kwargs):

    # Pull out the variables.
    ob = kwargs.setdefault("obj", bpy.context.active_object)
    objdir = kwargs.setdefault("objdir", bpy.path.abspath("//"))
    export_mats = kwargs.setdefault("export_mats", False)
    apply_modifiers = kwargs.setdefault("apply_modifiers", True)
    is_write_transforms = kwargs.setdefault("is_write_transforms", False)

    # Select only this object.
    solo_select_object(ob)

    # Get the name of the object to use in the filename.
    name = bpy.path.clean_name(ob.name)

    if is_write_transforms:
        print("Resetting transforms!")
        # Unparent object if write_transforms is enabled
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        # Reset transforms if write_transforms is enabled
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()
        bpy.ops.object.scale_clear()

    # Export obj.
    filepath = path.join(objdir, "%s.obj" % name)
    bpy.ops.export_scene.obj(
            filepath=filepath,
            check_existing=True,
            use_selection=True,
            use_animation=False,
            use_mesh_modifiers=apply_modifiers,
            use_edges=True,
            use_normals=True,
            use_uvs=True,
            use_materials=export_mats,
            use_triangles=False,
            use_nurbs=False,
            use_vertex_groups=False,
            use_blen_objects=True,
            use_smooth_groups=True,
            use_smooth_groups_bitflags=True,
            group_by_object=False,
            group_by_material=False,
            keep_vertex_order=True,
            global_scale=1,
            axis_forward='-Z',
            axis_up='Y',
            path_mode='AUTO',
            )


class ExportObjs(Operator, ExportHelper):
    """Exports all objects as .obj's."""

    bl_idname = "export_scene.objdir"
    bl_label = "Export scene (OBJ)"
    bl_options = {'PRESET'}

    filename_ext = ".obj"
    filter_glob = StringProperty(
        default="*.obj;*.mtl",
        options={'HIDDEN'},
        )

    use_selection = BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=True,
        )
    apply_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Apply the modifiers",
        default=True,
        )
    export_mats = BoolProperty(
        name="Materials",
        description="Also export the materials",
        default=False,
        )
    is_write_transforms = BoolProperty(
        name="Write transformations",
        description="Write the transformations to a file, reset all transforms before exporting to obj",
        default=False)

    def execute(self, context):

        time1 = time()
        apply_modifiers = self.apply_modifiers
        export_mats = self.export_mats
        is_write_transforms = self.is_write_transforms

        # Check for needed exporters:
        check_exporters()

        # Get a list with all the mesh objects.
        if self.use_selection:
            objects_to_export = [ob for ob in bpy.context.selected_objects]
        else:
            objects_to_export = [ob for ob in bpy.data.objects
                    if ob.type in ('MESH', 'CURVE')]

        # Get the folder.
        dirpath = path.dirname(self.filepath)

        if is_write_transforms:
            # Write transforms file
            write_transforms(objects_to_export, dirpath)

        for ob in objects_to_export:
            print("\n*** processing object %s (%d of %d)...\n" % (
                ob.name,
                objects_to_export.index(ob) + 1,
                len(objects_to_export)),
                )

            export_object(
                obj=ob,
                objdir=dirpath,
                apply_modifiers=apply_modifiers,
                export_mats=export_mats,
                is_write_transforms=is_write_transforms
                )

        process_time = time() - time1
        minutes, seconds = divmod(process_time, 60)
        if minutes == 1:
            print("\n*** Objects export finished in %d minute and %d seconds"\
                    "...\n" % (int(minutes), int(seconds)))
        else:
            print("\n*** Objects export finished in %d minutes and %d seconds"\
                    "...\n" % (int(minutes), int(seconds)))

        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(ExportObjs.bl_idname, text="Export Objects (.obj)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()