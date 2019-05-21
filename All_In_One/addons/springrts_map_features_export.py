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

# <pep8-80 compliant>

bl_info = {
    "name": "SpringRTS Feature Placement Exporter",
    "author": "Samuel Nicholas",
    "version": (0,1),
    "blender": (2, 6, 3),
    "location": "File > Import-Export",
    "description": "export selected objects to features file"
                   "",
    "warning": "",
    "wiki_url": "https://github.com/enetheru/springrts-blender-tools"
                "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy

def write_some_data(context, filepath, x,z, mult_x, mult_z ):
    print("running write_some_data...")
    f = open(filepath, 'w', encoding='utf-8')

    for obj in bpy.context.selected_objects:
        print(
                "{ name = '" + obj.data.name + "', x =",
                int( obj.location.x * mult_x * 512 ),
                ", z =", int( obj.location.y * mult_z * -512 ),
                ", rot = \"" + str(int((obj.rotation_euler.z / 6.141592) * 65536)) + "\"},",
                file=f
                )

    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import Operator


class ExportSomeData(Operator, ExportHelper):
    """Save feature positions to text file"""
    bl_idname = "export_springrts.map_features"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Some Data"

    # ExportHelper mixin class uses this
    filename_ext = ".lua"

    filter_glob = StringProperty(
            default="*.*",
            options={'HIDDEN'},
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    size_x = bpy.props.IntProperty(
            name="Map Width(x)",
            description="The Width of the map in SpringRTS map units",
            min=2, max=128,
            soft_min=4, soft_max=32,
            step=2,
            default=2,
            )

    size_z = bpy.props.IntProperty(
            name="Map Length(z)",
            description="The Length of the map in SpringRTS map units",
            min=2, max=128,
            soft_min=4, soft_max=32,
            step=2,
            default=2,
            )

    mult_x = bpy.props.FloatProperty(
            name="unit multiplier",
            description="how many spring map units a blender map unit is",
            min=0, max=100,
            soft_min=0.125, soft_max=32,
            step=0.125,
            default=1,
            )

    mult_z = bpy.props.FloatProperty(
            name="unit multiplier",
            description="how many spring map units a blender map unit is",
            min=0, max=100,
            soft_min=0.125, soft_max=32,
            step=0.125,
            default=1,
            )

    def execute(self, context):
        return write_some_data(context, self.filepath, self.size_x, self.size_z, self.mult_z, self.mult_z)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text="SpringRTS Map Features")


def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
