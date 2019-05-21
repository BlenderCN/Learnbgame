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

bl_info = {
    "name": "Decompile Game Engine Runtime",
    "author": "Quentin Wenger (Matpi)",
    "version": (1, 0),
    "blender": (2, 74, 0),
    "location": "File > Import",
    "description": "Retrieve a .blend file from a bundled BlenderPlayer runtime, "
                   "even from another platform.",
    "warning": "",
    "wiki_url": "",
    "category": "Game Engine",
}

import bpy
import os
import sys
import tempfile


def OpenBlend(input_path, use_temp_dir, load_file, to_clipboard, report=print):
    import struct

    # Check the path
    if not os.path.isfile(input_path):
        report({'ERROR'}, "The executable file could not be found! .blend file not retrieved.")
        return
    
    # Get the binary file
    file = open(input_path, 'rb')
    input_d = file.read()
    file.close()

    # Check the end of the data to find "BRUNTIME"
    if not input_d[-8:] == b"BRUNTIME":
        report({'ERROR'}, "Could not retrieve the data, file format not correct!")
        return
    
    # Create a new file for the .blend
    if use_temp_dir:
        temp_fd, blend_path = tempfile.mkstemp(suffix=".blend")
        output = open(temp_fd, "wb")
    else:
        blend_path = os.path.splitext(input_path)[0] + ".blend"
        output = open(blend_path, "wb")
    
    
    # Retrieve the offset
    offset_raw = struct.unpack("4B", input_d[-12:-8])
    offset = sum(v<<(24, 16, 8, 0)[i] for i, v in enumerate(offset_raw))
    
    # Write the blend data from the runtime
    print("Writing .blend...", end=" ")
    output.write(input_d[offset:-12])
    
    output.close()
    
    print("done")

    if to_clipboard:
        bpy.data.window_managers['WinMan'].clipboard = blend_path

    if load_file:
        bpy.ops.wm.open_mainfile(filepath=blend_path)

    else:
        report({'INFO'}, ".blend file saved at %s." % blend_path)
    

from bpy.props import *


class RetrieveFromRuntime(bpy.types.Operator):
    bl_idname = "wm.retrieve_from_runtime"
    bl_label = "Retrieve .blend from Game Engine Runtime"
    bl_options = {'REGISTER'}

    # it should even be possible to use runtimes from other platforms!
    #ext = '.app' if sys.platform == 'darwin' else os.path.splitext(bpy.app.binary_path)[-1]
    #filter_glob = StringProperty(default="*%s" % ext, options={'HIDDEN'})
    
    filepath = StringProperty(
        subtype='FILE_PATH'
        )
    tempdir = BoolProperty(
        name="Use temporary location",
        description="Places the created .blend file in a temporary location "
                    "rather than in the same folder as the runtime",
        default=False
        )
    loadfile = BoolProperty(
        name="Load file",
        description="Loads the created .blend file in the current Blender session; "
                    "This is not recommended if the runtime has been created with a previous version of Blender",
        default=False
        )
    toclipboard = BoolProperty(
        name="Copy path to clipboard",
        description="Copies the path of the created .blend file to the clipboard",
        default=False
        )

    def execute(self, context):
        import time
        start_time = time.clock()
        print("Retrieving .blend from %r" % self.filepath)
        OpenBlend(self.filepath,
                  self.tempdir,
                  self.loadfile,
                  self.toclipboard,
                  self.report
                  )
        print("Finished in %.4fs" % (time.clock()-start_time))
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator(RetrieveFromRuntime.bl_idname)


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()
