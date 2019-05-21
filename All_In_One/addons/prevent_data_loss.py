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
    "name": "Prevent Data Loss On Switching Files",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 6, 5),
    "location": "bpy.app.handlers.load_pre",
    "description": "Prevent accidental losing of data by saving modified data",
    "warning": "",
    "category": "Learnbgame"
}

"""Prevent accidental losing of data by automatically saving session files"""

import bpy
from bpy.app.handlers import persistent

@persistent
def prevent_data_loss(context):
    data = bpy.data
    if not data.is_saved and data.is_dirty:
        print ("File was not saved and contains modified data")
        import os
        filepath = os.path.join(os.getcwd(), 'unsaved.blend')
        print ("Saving data in file {0}".format(filepath))
        bpy.ops.wm.save_mainfile(filepath=filepath, compress=True, relative_remap=True)
    elif data.is_saved and data.is_dirty:
        print ("File exists on disk but was modified in memory")
        print ("Saving modified data {0}".format(bpy.data.filepath))
        bpy.ops.wm.save_mainfile(compress=True, relative_remap=True)
    else:
        print ("All is well")

@persistent
def another_load_pre(context):
    print ("Updating database....")

def register():
    bpy.app.handlers.load_pre.insert(0, prevent_data_loss)
    bpy.app.handlers.load_pre.append(another_load_pre)
    
def unregister():
    bpy.app.handlers.load_pre.remove(prevent_data_loss)
    bpy.app.handlers.load_pre.remove(another_load_pre)

if __name__ == '__main__':
    register()

