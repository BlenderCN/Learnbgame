# BEGIN GPL LICENSE BLOCK #####
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
# END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Manage File Paths",
    "description": ":)",
    "author": "Greg Zaal",
    "version": (0, 2),
    "blender": (2, 74, 0),
    "location": "Properties Editor > Scene > File Paths panel",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
import os
from shutil import copy2 as copyfile

'''
TODOs:
    Don't fetch image list or check for existance on every redraw, make refresh button (and maybe refresh automatically every so often with modal timer?)
    Find and replace individually
    Only if file doesn't exist
    Somehow automatically try fix paths based on history (stored in config)
    Reload images
'''

class MFPProps(bpy.types.PropertyGroup):
    source = bpy.props.StringProperty(
        name="Source",
        default="",
        description="source")

    target = bpy.props.StringProperty(
        name="Target",
        default="",
        description="target")


def get_images():
    images = []
    for i in bpy.data.images:
        if i.source == 'FILE':
            if not i.library:  # ignore linked images since we cannot modify them
                images.append(i)
    return images

def file_exists(path):
    if path.startswith('//'):  # os.path.exists only works with absolute paths
        path = bpy.path.abspath(path)

    return os.path.exists(path)

def all_rel_to_abs():
    images = get_images()
    for img in images:
        if img.filepath.startswith('//'):
            img.filepath = bpy.path.abspath(img.filepath)

class MFPFindReplace(bpy.types.Operator):
    """Tooltip"""  # TODO
    bl_idname = "mfp.find_replace"
    bl_label = "Replace Source with Target"

    def execute(self, context):
        all_rel_to_abs()
        props = context.scene.mip_props
        images = get_images()

        for img in images:
            img.filepath = img.filepath.replace(props.source, props.target)
        return {'FINISHED'}

class MFPCopy(bpy.types.Operator):
    """Tooltip"""  # TODO
    bl_idname = "mfp.copy"
    bl_label = "Copy Source to Target"

    def execute(self, context):
        all_rel_to_abs()
        props = context.scene.mip_props
        images = get_images()

        for img in images:
            old_path = img.filepath
            if props.source in old_path:
                new_path = old_path.replace(props.source, props.target)
                new_path_root = os.sep.join(new_path.split(os.sep)[:-1])
                if not os.path.exists(new_path_root):
                    os.makedirs(new_path_root)
                img.filepath = new_path
                copyfile (old_path, new_path)
        return {'FINISHED'}

class MFPImagePathsPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "File Paths"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        images = get_images()
        caches = bpy.data.cache_files
        props = context.scene.mip_props

        col = layout.column(align=True)
        col.prop(props, 'source')
        col.prop(props, 'target')
        col.separator()
        col.operator('mfp.find_replace')
        col.operator('mfp.copy')

        col = layout.column()
        for img in images:
            row = col.row(align=True)
            row.prop(img, 'filepath', text=img.name)
            i = 'FILE_TICK' if file_exists(img.filepath) else 'ERROR'
            row.label(text='', icon=i)

        if caches:
            col = layout.column()
            for c in caches:
                row = col.row(align=True)
                row.prop(c, 'filepath', text=c.name)
                i = 'FILE_TICK' if file_exists(c.filepath) else 'ERROR'
                row.label(text='', icon=i)


def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.mip_props = bpy.props.PointerProperty(type=MFPProps)

def unregister():
    del bpy.types.Scene.mip_props

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
