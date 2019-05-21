# ##### BEGIN GPL LICENSE BLOCK #####
#
#  io_export_unityraw.py
#  Export image as Unity raw (plain 16bit greyscale array)
#  Copyright (C) 2017 Quentin Wenger
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



bl_info = {"name": "Export Unity .raw",
           "description": "Export image as Unity raw (plain 16bits greyscale array)",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 0),
           "blender": (2, 78, 0),
           "location": "File Menu -> Export -> Unity 16bit RAW (.raw)",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "Import-Export"
           }

import struct

import bpy


def saveRaw(output_path, image_name, mode, report=print):
    # test for other extension?
    if not output_path.endswith(".raw"):
        output_path += ".raw"
    
    image = bpy.data.images[image_name]
    if image.channels == 0:
        report({'ERROR'}, "Image has no channels.")
    elif mode == 'GREY':
        if image.channels == 1:
            mode == 'FIRST'
        elif image.channels == 2:
            report(
                {'ERROR'},
                "Image does not have enough channels to be greyscaled.")

    # raw is left-right, from top to bottom
    # (Blender: bottom to top)
    pixels = reversed([
        [
            image.pixels[
                (j*image.size[0] + i)*image.channels:
                (j*image.size[0] + i + 1)*image.channels]
            for i in range(0, image.size[0])]
        for j in range(0, image.size[1])])

    with open(output_path, "wb") as f:
        if mode == 'ALL':
            for row in pixels:
                for pixel_grp in row:
                    for pixel in pixel_grp:
                        f.write(struct.pack("<H", int(pixel*65535)))
        else:
            for row in pixels:
                for pixel_grp in row:
                    if mode == 'GREY':
                        v = (
                            0.2126*pixel_grp[0] +
                            0.7152*pixel_grp[1] +
                            0.0722*pixel_grp[2])
                    elif mode == 'FIRST':
                        v = pixel_grp[0]
                    f.write(struct.pack("<H", int(v*65535)))
    report({'INFO'}, "Image successfully exported.")


from bpy.props import *

class ExportUnityRaw(bpy.types.Operator):
    bl_idname = "image.export_unity_raw"
    bl_label = "Unity 16bit RAW (.raw)"
    bl_options = {'REGISTER'}

    filepath = StringProperty(
        subtype='FILE_PATH'
        )
    image = StringProperty(name="Image")
    mode = EnumProperty(
        items=[
            ('FIRST', "First", "Export first channel only"),
            ('GREY', "Greyscale", "Export greyscaled data"),
            ('ALL', "All", "Export all channels")],
        name="Mode",
        description="Export mode",
        default='FIRST')

    def execute(self, context):
        if not self.image:
            self.report({'ERROR'}, "No image selected.")
            return {'CANCELLED'}
        saveRaw(self.filepath, self.image, self.mode, self.report)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop_search(self, "image", bpy.data, "images")
        col.prop(self, "mode")



def menu_func(self, context):
    self.layout.operator(ExportUnityRaw.bl_idname)


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(menu_func)


if __name__ == "__main__":
    register()
