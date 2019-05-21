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
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os
import subprocess

from math import radians
from mathutils import Vector


bl_info = {
    'name': 'Unity Exporter',
    'description': 'Export FBX file for use in the Unity Engine',
    'author': 'Lucas (stillwwater)',
    'version': (1, 0),
    'blender': (2, 79, 0),
    'location': 'View3D > Tools > Unity',
    'warning': 'FBXConvert executable required to use all add-on features',
    'wiki_url': 'http://github.com/stillwwater/bl_unity_exporter',
    'tracker_url': 'http://github.com/stillwwater/bl_unity_exporter/issues',
    'category': 'Import-Export'
}


class Transform():
    """Safely handle an object transform"""
    def __init__(self, obj=None):
        self.obj = obj
        self.delta_loc = Vector((0, 0, 0))
        self.delta_scl = Vector((0, 0, 0))
        self.delta_rot = [0, 0, 0]

    def rotation(self, x, y, z):
        self.delta_rot[0] += x - self.obj.rotation_euler[0]
        self.delta_rot[1] += y - self.obj.rotation_euler[1]
        self.delta_rot[2] += z - self.obj.rotation_euler[2]
        self.obj.rotation_euler = (x, y, z)
        return self

    def location(self, x, y, z):
        loc = Vector((x, y, z))
        self.delta_loc += loc - self.obj.location
        self.obj.location = loc
        return self

    def scale(self, x, y, z):
        scl = Vector((x, y, z))
        self.delta_scl += scl - self.obj.scale
        self.obj.scale = scl
        return self

    def revert(self):
        self.obj.location -= self.delta_loc
        self.obj.scale -= self.delta_scl
        self.obj.rotation_euler[0] -= self.delta_rot[0]
        self.obj.rotation_euler[1] -= self.delta_rot[1]
        self.obj.rotation_euler[2] -= self.delta_rot[2]
        return self

    def apply(self, loc=False, rot=True, scl=True):
        bpy.ops.object.transform_apply(
            location=loc, rotation=rot, scale=scl)


class UProperties(bpy.types.PropertyGroup):
    advanced_props = bpy.props.BoolProperty(
        name='advanced_props',
        description='Show advanced propertied',
        default=True
    )

    enable_convert = bpy.props.BoolProperty(
        name='enable_convert',
        description='Enable using FBXConverter (must be installed in $PATH)',
        default=False
    )

    fbx_format = bpy.props.EnumProperty(
        items=[('f201300', 'FBX 7.3 Binary', 'Binary .fbx'),
               ('f201200', 'FBX 7.2 Binary', 'Binary .fbx'),
               ('f201100', 'FBX 7.1 Binary', 'Binary .fbx'),
               ('f201000', 'FBX 6.1 Binary', 'Binary .fbx'),
               ('ascii', 'FBX 7.3 ASCII', 'ASCII .fbx')],
        name='File Format',
        description='Change FBX file format',
        default='f201300'
    )

    patch_rotation = bpy.props.BoolProperty(
        name='patch_rotation',
        description='Fix mesh rotation to identity Rot (Requires FBXConverter)',
        default=True
    )

    patch_scale = bpy.props.BoolProperty(
        name='patch_scale',
        description='Fix mesh scaling to use unit Scl (Requires FBXConverter)',
        default=True
    )

    fbx_convert_path = bpy.props.StringProperty(
        name='fbx_convert_path',
        description='Path location to the FBXConverter executable',
        default='FBXConverter'
    )

    fix_y_up = bpy.props.BoolProperty(
        name='fix_y_up',
        description='Fix mesh rotation by swapping Z axis for Y',
        default=True
    )

    same_dir_export = bpy.props.BoolProperty(
        name='save_dir_export',
        description='Export to the same directory as .blend file',
        default=False
    )

    identity_location = bpy.props.BoolProperty(
        name='identity_location',
        description='Export mesh at location (0, 0, 0)',
        default=True
    )

    export_dir = bpy.props.StringProperty(
        name='export_dir',
        description='Directory name to export to',
        default='Fbx'
    )

    search_dir = bpy.props.StringProperty(
        name='search_dir',
        description='Directory name to limit export search to',
        default='Assets'
    )


class FileHandler():
    def __init__(self, path):
        self.old_wd = os.getcwd()
        self.wd = path
        self.export_dir = None
        self.path_trace_stack = []
        os.chdir(path)

    @staticmethod
    def from_file_path(file_path):
        return FileHandler(os.path.dirname(file_path))

    def get_export_dir(self, cache_results=True):
        """Finds an appropriate exporting directory

        this method attempts to replicate the file structure
        in the source directory.

        expected directory structure example:

        Models
        +---Blend
        |   +---Directory
        +---Fbx
            +---Directory
        """
        if self.export_dir and cache_results:
            # return cached export path
            return self.export_dir

        if bpy.context.scene.u_prop.same_dir_export:
            self.export_dir = self.wd
            return self.export_dir

        i = 0
        path = self.wd
        search_dir = bpy.context.scene.u_prop.search_dir
        export_dir = bpy.context.scene.u_prop.export_dir
        last_dir = None

        while True:
            # get current directory name
            dir_name = os.path.split(path)[-1]

            if os.path.isdir(os.path.join(path, export_dir)):
                # found the export directory
                break

            if dir_name == search_dir:
                raise FileNotFoundError('Cannot find %s in %s'
                                        % (export_dir, search_dir))

            if last_dir:
                # add this directory to the directory trace
                # this is used to replicate the directory structure
                # in the EXPORT_DIR
                self.path_trace_stack.append(last_dir)

            # move up to next parent
            print(dir_name)
            path = os.path.dirname(path)
            last_dir = dir_name
            i += 1

        # push EXPORT_DIR and base path
        self.path_trace_stack.append(export_dir)
        self.path_trace_stack.append(path)
        # get a real export path
        self.export_dir = os.path.join(*reversed(self.path_trace_stack))
        return self.setup_export_dir()

    def get_export_file(self, file_name):
        return os.path.join(self.get_export_dir(), file_name) + '.fbx'

    def setup_export_dir(self):
        if not os.path.isdir(self.export_dir):
            os.makedirs(self.export_dir)
        return self.export_dir

    def restore(self):
        os.chdir(self.old_wd)
        print('restored working directory')


class UFbx():
    TMP_FILE = 'UFbx__tmp.fbx'

    def __init__(self, path):
        self.path = path

    def bl_export(self):
        """wrapper for blender's fbx exporter"""
        bpy.ops.export_scene.fbx(
            filepath=self.path,
            use_selection=True,
            axis_forward='-Z',
            axis_up='Y',
            global_scale=1)

        return self

    def convert(self, file_format):
        """converts a binary FBX file to ASCII or vice-versa

        blender has an ASCII FBX exporter option, but it is currently
        deprecated, instead we export a regular FBX binary and then
        convert it to ASCII using FBXConverter.
        """
        if not bpy.context.scene.u_prop.enable_convert:
            return self

        converter = bpy.context.scene.u_prop.fbx_convert_path

        if not converter:
            raise Exception('Please define the path to the FBXConverter')

        args = [converter, self.path, UFbx.TMP_FILE, '/f']
        args.append('/' + file_format)

        p = subprocess.Popen(args, shell=False)
        p.wait()

        if p.returncode != 0:
            raise Exception('Failed to execute FBXConverter')

        os.remove(self.path)
        os.rename(UFbx.TMP_FILE, self.path)

        print('converted binary %s to ASCII' % self.path)
        return self

    def patch(self):
        """Patches an ASCII FBX file to use unit scale/rot

        by default blender exports fbx meshes with a rotation of
        (-90, 0, 0) and scale of (100, 100, 100), this should not
        be done since we are already fixing the tranform in this script.

        It's a mild incovenience to have to reset the transform in Unity
        every time, and the only way to fix this is by modifying blender's
        `export_fbx_bin.py` script. To avoid doing that we simply read the
        ASCII file and change it manually. This requires an ASCII Export.
        """
        u_prop = bpy.context.scene.u_prop

        if not (u_prop.enable_convert and
                (u_prop.patch_rotation or u_prop.patch_scale)):
            return self

        if u_prop.fbx_format != 'ascii':
            # convert file to ascii in order to patch it
            self.convert('ascii')

        src = open(self.path, 'r')
        dst = open(UFbx.TMP_FILE, 'w')

        for ln in src.readlines():
            cln = ln.strip()

            if cln.startswith('P: "Lcl Rotation"') and u_prop.patch_rotation:
                # skip Lcl Rotation, this forces rotation of 0, 0, 0
                continue

            if cln.startswith('P: "Lcl Scaling"') and u_prop.patch_scale:
                # skip Lcl Scale, this forces scale of 1, 1, 1
                continue

            if cln.startswith('P: "UnitScaleFactor"') and u_prop.patch_scale:
                # change unit scale factor to 100
                hln = ','.join(ln.split(',')[:-1])
                dst.write(hln + ',100' + ln[-1])
                continue

            # copy line to dst
            dst.write(ln)

        src.close()
        dst.close()
        # swap files
        os.remove(self.path)
        os.rename(UFbx.TMP_FILE, self.path)

        if u_prop.fbx_format != 'ascii':
            # convert file back into binary
            self.convert(u_prop.fbx_format)

        print('patched %s' % self.path)
        return self


class UExport(bpy.types.Operator):
    bl_idname = "u_export.fbx"
    bl_label = "Export Unity FBX"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        fh = FileHandler.from_file_path(bpy.data.filepath)
        buffer = bpy.context.selected_objects
        u_prop = bpy.context.scene.u_prop

        Transform().apply()
        # if `get_export_dir` crashes it'll do so before
        # we start modifying objects
        fh.get_export_dir()

        # deselect all objects, work from local buffer
        bpy.ops.object.select_all(action='DESELECT')

        # thread stack
        threads = []
        self.transforms = []

        for obj in buffer:
            self.export_obj(obj, u_prop, fh)

        fh.restore()
        return {'FINISHED'}

    def export_obj(self, obj, u_prop, fh):
        # select object for exporting
        obj.select = True
        transform = Transform(obj)

        if u_prop.fix_y_up:
            # flip Z to Y up rotation
            transform.rotation(radians(-90), 0, 0).apply()

        if u_prop.identity_location:
            transform.location(0, 0, 0)

        # clean name for safe file name
        cname = bpy.path.clean_name(obj.name)
        cpath = fh.get_export_file(cname)
        # export FBX
        UFbx(cpath).bl_export().convert(u_prop.fbx_format).patch()
        # revert transform
        transform.revert().apply()
        # deselect object
        obj.select = False
        # free resources
        del transform


class UExportUI(bpy.types.Panel):
    """User interface for UExport"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'
    bl_label = 'Unity'

    def draw(self, context):
        props = context.scene.u_prop
        box = self.layout.box()
        box.label(text='Exporter')
        box.operator('u_export.fbx', text='Export FBX', icon='EXPORT')
        box.prop(props, 'advanced_props', text='Advanced')

        if props.advanced_props:
            self.export_settings(box.box(), props)
            self.fbx_settings(box.box(), props)

    def export_settings(self, layout, props):
        """Draw Export Settings panel"""
        layout.label(text='Export Settings')
        layout.prop(props, 'same_dir_export', text='Same Path Export')

        if not props.same_dir_export:
            layout.prop(props, 'export_dir', text='Export')
            layout.prop(props, 'search_dir', text='Search')

        layout.label(text='Mesh:')
        layout.prop(props, 'fix_y_up', text='Fix Rotation')
        layout.prop(props, 'identity_location', 'Identity Location')

    def fbx_settings(self, layout, props):
        """Draw FBX Settings panel"""
        layout.label(text='FBX Settings')
        layout.prop(props, 'enable_convert',
                    text='Enable FBXConverter', icon='ERROR')

        if props.enable_convert:
            layout.prop(props, 'fbx_convert_path', text='', icon='CONSOLE')
            layout.prop(props, 'fbx_format', text='Format')

            col = layout.column(align=True)
            col.label(text='Patch .fbx file:')

            row = layout.row(align=True)
            row.prop(props, 'patch_rotation', text='Rotation')
            row.prop(props, 'patch_scale', text='Scale')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.u_prop = bpy.props.PointerProperty(type=UProperties)


def unregister():
    bpy.utils.unregister_module(__name__)
    # free PointerProperty
    del bpy.types.u_prop


if __name__ == "__main__":
    register()
