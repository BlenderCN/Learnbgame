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
  "name": "CSV PointCloud reader (.csv)",
  "author": "David Ortley (lutra)",
  "version": (0, 4, 2),
  "blender": (2, 67, 0),
  "location": "File > Import-Export > CSV PointCloud (.csv) ",
  "description": "Import CSV Point Cloud as single mesh.",
  "warning": "",
  "wiki_url": "",
  "category": "Import-Export"
}

if "bpy" in locals():
    import imp
    if "readCSV" in locals():
        imp.reload(readCSV)
else:
    import bpy

from bpy.props import (StringProperty,
                       EnumProperty,
                       FloatProperty,
                       )
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 axis_conversion,
                                 )

class CsvImporter(bpy.types.Operator, ImportHelper):
    """Load CSV Point Cloud"""
    bl_idname  = "import_mesh.csv"
    bl_label   = "Import CSV"
    bl_options = {'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH', )
    filter_glob = StringProperty(default="*.csv", options={'HIDDEN'})
    directory = StringProperty(subtype='DIR_PATH', )

    X = StringProperty(name="X",default="x")
    Y = StringProperty(name="Y",default="y")
    Z = StringProperty(name="Z",default="z")
    T = EnumProperty(name="Point Type",
                     items=( ("points", "Points", "Pts"),
                             ("cubes", "Cubes", "Cbs"),
                             ("icospheres1", "Ico Spheres (subdiv 1)", "IcoSpheres (Subdivide 1)"),
                             ("icospheres2", "Ico Spheres (subdiv 2)", "IcoSpheres (Subdivied 2)") )
                     )
    DELIM = StringProperty(name="Delimiter",default=",")
    SCALE = FloatProperty(name="Scale",default=1.0,min=0.00001,max=1000.0)

    def execute(self, context):
        from . import readCSV
        readCSV.read(self.directory,self.filepath,
                     self.X, self.Y, self.Z, self.T,
                     "%s" % (self.DELIM,),
                     self.SCALE)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        engine=context.scene.render.engine
        layout=self.layout

        box=layout.box()
        box.label("Column Header Names")
        box.prop(self, "X")
        box.prop(self, "Y")
        box.prop(self, "Z")

        box=layout.box()
        box.prop(self, "DELIM")

        box=layout.box()
        box.label("Display Type ('points' are fastest)")
        box.prop(self, "T")
        box.prop(self, "SCALE")


def menu_import(self, context):
    self.layout.operator(CsvImporter.bl_idname, text="CSV Files (.csv)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()
