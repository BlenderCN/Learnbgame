"""** BEGIN GPL LICENSE BLOCK *****

This program is free software; you may redistribute it, and/or
modify it, under the terms of the GNU General Public License
as published by the Free Software Foundation - either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, write to:

  	the Free Software Foundation Inc.
	51 Franklin Street, Fifth Floor
	Boston, MA 02110-1301, USA

or go online at: http://www.gnu.org/licenses/ to view license options.

***** END GPL LICENCE BLOCK **"""

import os
import bpy

from bpy.props import StringProperty
from os.path import join

from collections import OrderedDict


# helper constant strings
split_token = "<--->"
material_locator = "\\Material\\"    
locator_prefix = "//"
path_to_scripts = bpy.utils.script_paths()[0]
path_to_script = join(path_to_scripts, 'addons_contrib', 'io_material_loader')


# helper functions
def import_material(file_name, matname):
    """
    takes input file_name, and the material name located within, and imports into
    current .blend
    """
    file_name += '.blend'
    opath = locator_prefix + file_name + material_locator + matname
    dpath = join(path_to_script, file_name) + material_locator

    bpy.ops.wm.link_append(
            filepath=opath,     # "//filename.blend\\Folder\\"
            filename=matname,   # "material_name
            directory=dpath,    # "fullpath + \\Folder\\
            filemode=1,
            link=False,
            autoselect=False,
            active_layer=True,
            instance_groups=False,
            relative_path=True)


def get_source_files():
    """
    given the predefined place to look for materials, this populates source_files
    with the list of .blends inside the directory pointed at. 
    """
    source_files = []
    source_files.extend(source_list(path_to_script, 
                                    filename_check=lambda f:f.endswith(".blend")))
    return source_files


def source_list(path, filename_check=None):
    """
    generates the iterable used to find all .blend files.
    """
    for dirpath, dirnames, filenames in os.walk(path):
        # skip hidden dirs
        if dirpath.startswith("."):
            continue
        for filename in filenames:
            # skip non .blend
            if not filename.endswith('.blend'):
                continue
            
            # we want these
            filepath = join(dirpath, filename)
            if filename_check is None or filename_check(filepath):
                yield filepath


def get_materials_dict():
    """
    Generates an ordered dictionary to map materials to the blend files that hold them.
    """
    source_files = get_source_files()
    mlist = OrderedDict()
    
    for i, filepath in enumerate(source_files):
        file_name = filepath.split(os.sep)[-1].replace('.blend', '')
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            if data_from.materials:
                materials_in_file = [mat for mat in data_from.materials]
        mlist[file_name] = materials_in_file

    return mlist


class AddMaterial(bpy.types.Operator):
    bl_idname = "scene.add_material_operator"
    bl_label = "Add Material Operator"

    selection = StringProperty()

    def execute(self, context):
        file_name, file_material = self.selection.split(split_token)
        import_material(file_name, file_material)
        print(file_name, file_material)
        return {'FINISHED'}


class CustomMenu(bpy.types.Menu):
    bl_label = "Materials"
    bl_idname = "OBJECT_MT_custom_menu"

    my_mat_dict = get_materials_dict()

    def draw(self, context):
        layout = self.layout
        for key in self.my_mat_dict:
            for material_choice in self.my_mat_dict[key]:
                info = key + split_token + material_choice
                layout.operator(    'scene.add_material_operator', 
                                    text=material_choice).selection = info 
            layout.label(text=key, icon='MATERIAL')


