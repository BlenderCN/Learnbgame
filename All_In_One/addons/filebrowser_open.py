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
    "name": "File Browser Open Files",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 6, 5),
    "location": "File Browser -> Header -> Open File",
    "description": "Open Files in External Applications",
    "warning": "",
    "category": "Learnbgame",
}

"""Open Files in External Applications from the File Browser Editor"""

import bpy
from bpy.props import StringProperty

def getEditor(filename):
    import os
    file, ext = os.path.splitext(filename)

    if not ext:
        return False
    ext = ext[1:]
    if ext in ('jpg', 'png'):
        return 'xv'
    elif ext in ('rll', 'exr', 'tiff'):
        return 'gruv'
    elif ext in ('obn', 'obj'):
        return 'glix'
    elif ext in ('py', 'txt'):
        import os
        return 'kwrite'
    else:
        return False


class FileOpenInExternalEditor(bpy.types.Operator):
    bl_idname = 'file.open_external'
    bl_label = 'Open Selected'
    bl_description = 'Open Files in External Applications from the File Browser Editor'
    bl_options = {'REGISTER', 'INTERNAL'}
    
    directory = StringProperty()
    filename = StringProperty()
    
    @classmethod
    def poll(cls, context):
        space_data = context.space_data
        filename = space_data.params.filename.strip()
        
        rules = []
        rules.append(space_data.type == 'FILE_BROWSER')
        rules.append(filename)
        rules.append(getEditor(filename))
        
        return all(rules)

    def execute(self, context):
        import os
        import subprocess
        _editor = getEditor(self.filename)
        filepath = os.path.join(self.directory, self.filename)
        subprocess.Popen([_editor, filepath])
        return {'FINISHED'}


def file_browser_open_append_draw(self, context):
    space_data = context.space_data
    params = space_data.params
    oper = self.layout.operator('file.open_external', icon='FILESEL')
    oper.directory = params.directory
    oper.filename = params.filename
    editor = getEditor(params.filename)
    if editor:
        self.layout.label('Selected file opens with {0}'.format(editor))


def register():
    bpy.utils.register_class(FileOpenInExternalEditor)
    bpy.types.FILEBROWSER_HT_header.append(file_browser_open_append_draw)


def unregister():
    bpy.utils.unregister_class(FileOpenInExternalEditor)
    bpy.types.FILEBROWSER_HT_header.remove(file_browser_open_append_draw)


if __name__ == "__main__":
    register()


