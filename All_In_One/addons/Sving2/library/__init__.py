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
import os


class LibPath:

    def __init__(self, path, root=None):
        self.path = path
        if root:
            self.local_path = path[len(root):]
        else:
            self.local_path = path
        self.name = bpy.path.display_name_from_filepath(path)

    def __lt__(self, other):
        return self.path < other.path


class LibDir(LibPath):

    def __init__(self, path, root=None):
        LibPath.__init__(self, path, root)
        self.files = []
        self.dirs = []

class LibFile(LibPath):

    def add_to_menu(self, layout):
        op = layout.operator("mesh.uv_shape_image_add",
            text=self.name, icon='COLOR')
        op.filepath = self.path


def build_lib(path=None):
    if not path:
        path = lib_dir
    top = LibDir(path)
    path2dir = {path: top}
    for root, dirs, files in os.walk(path):
        dirs.sort()
        files.sort()
        dirobj = path2dir[root]
        for name in dirs:
            subdirobj = LibDir(os.path.join(root, name), top.path)
            path2dir[subdirobj.path] = subdirobj
            dirobj.dirs.append(subdirobj)
        for name in files:
            if name[-4:] == '.png':
                dirobj.files.append(LibFile(os.path.join(root, name), \
                        top.path))
                dirobj.files[-1].local_path = dirobj.files[-1].local_path[:-4]
    return top


def menu_library(self, context):
    if structure.files != [] or structure.dirs != []:
        layout = self.layout
        layout.separator()
        for f in structure.files:
            f.add_to_menu(layout)
        for d in structure.dirs:
            if d.files != [] or d.dirs != []:
                layout.menu("INFO_MT_mesh_add_uvlib_" + d.name,
                    text=d.name)


class INFO_MT_mesh_add_uvlibrary(bpy.types.Menu):
    bl_label = "UVLibrary"
    lib = None

    def draw(self, context):
        if self.lib is not None:
            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            for f in self.lib.files:
                f.add_to_menu(layout)
            for d in self.lib.dirs:
                if d.files != [] or d.dirs != []:
                    m = layout.menu("INFO_MT_mesh_add_uvlib_" + d.name,
                        text=d.name)


structure = build_lib(os.path.dirname(__file__))
classes = []


def register():
    for d in structure.dirs:
        if d.files != [] or d.dirs != []:
            cls = type("INFO_MT_mesh_add_uvlib_" + d.name,
                (INFO_MT_mesh_add_uvlibrary,), {'lib': d})
            bpy.utils.register_class(cls)
            classes.append(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    classes = []
