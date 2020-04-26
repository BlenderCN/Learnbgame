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
    "name": "AFM mesh",
    "author": "zeffii stanton",
    "version": (0,4),
    "blender": (2, 6, 3),
    "location": "File > Import/Export > Ascii AFM data",
    "description": "Import ASCII data from AFM (.txt format)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    if "import_afm" in locals():
        imp.reload(import_afm)
    if "create_map" in locals():
        imp.reload(create_map)
else:
    import bpy

from bpy.props import StringProperty, BoolProperty


class AFMImporter(bpy.types.Operator):
    '''Load AFM triangle mesh data'''
    bl_idname = "import_afm.txt"
    bl_label = "Import AFM"

    filepath = StringProperty(   name="File Path",
                                 description="Filepath used for importing the AFM file",
                                 maxlen=1024, default="", subtype='FILE_PATH')

    filter_glob = StringProperty(default="*.txt", options={'HIDDEN'})

    make_color_map = BoolProperty(
        name="Make Colour Map",
        description="This maps z-height to vertex colour (Warning, may be slow)",
        default=True,
        )

    def execute(self, context):
        from . import import_afm
        import_afm.startASCIIimport(self.filepath)

        if self.make_color_map:
            from . import create_map
            create_map.create_vertex_color_map()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}



def menu_import(self, context):
    self.layout.operator(AFMImporter.bl_idname, text="Ascii AFM (.txt)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)

if __name__ == "__main__":
    register()
