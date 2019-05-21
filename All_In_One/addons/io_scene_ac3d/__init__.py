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

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper,
    path_reference_mode,
    axis_conversion,
)
from bpy.props import (
    BoolProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
)
from math import radians
import mathutils
import bpy
import datetime
import time
bl_info = {
    "name": "AC3D (.ac) format",
    "description": "Import-Export AC3D",
    "author": "Chris Marr, Petar Jedvaj",
    "version": (2, 1),
    "blender": (2, 80, 0),
    "api": 41098,
    "location": "File > Import-Export",
    "category": "Learnbgame",
    "warning": ""}

if "bpy" in locals():
    import importlib
    if "import_obj" in locals():
        importlib.reload(import_ac3d)
    if "export_obj" in locals():
        importlib.reload(export_ac3d)


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ImportAC3D_MT_Operator(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_scene.import_ac3d'
    bl_label = 'Import AC3D'
    bl_options = {'PRESET'}

    filename_ext = '.ac'
    filter_glob: StringProperty(
        default='*.ac',
        options={'HIDDEN'}
    )

    axis_forward = EnumProperty(
        name="Forward",
        items=(('X', "X Forward", ""),
               ('Y', "Y Forward", ""),
               ('Z', "Z Forward", ""),
               ('-X', "-X Forward", ""),
               ('-Y', "-Y Forward", ""),
               ('-Z', "-Z Forward", ""),
               ),
        default='-Z',
    )

    axis_up = EnumProperty(
        name="Up",
        items=(('X', "X Up", ""),
               ('Y', "Y Up", ""),
               ('Z', "Z Up", ""),
               ('-X', "-X Up", ""),
               ('-Y', "-Y Up", ""),
               ('-Z', "-Z Up", ""),
               ),
        default='Y',
    )

    use_transparency: BoolProperty(
        name="Use Transparency",
        description="Enable transparency for rendering if material alpha < 1.0",
        default=True,
    )

    transparency_method: EnumProperty(
        name="Transparency Method",
        items=(('MASK', "Mask", ""),
               ('Z_TRANSPARENCY', "Z_Transp", ""),
               ('RAYTRACE', "RayTrace", ""),
               ),
        default='Z_TRANSPARENCY',
    )

    use_auto_smooth: BoolProperty(
        name="Auto Smooth",
        description="Use object auto smooth if normal angles are beneath Crease angle",
        default=True,
    )

    use_emis_as_mircol: BoolProperty(
        name="Use Emis as Mirror colour",
        description="Use Emission colour as Mirror colour",
        default=True,
    )

    use_amb_as_mircol: BoolProperty(
        name="Use Amb as Mirror colour",
        description="Use Ambient colour as Mirror colour",
        default=False,
    )

    display_transparency: BoolProperty(
        name="Display Transparency",
        description="Display transparency in main display",
        default=True,
    )

    display_textured_solid: BoolProperty(
        name="Display textured solid",
        description="Show main window with textures applied (transparency works in only in normal direction)",
        default=False,
    )

    def execute(self, context):
        from . import import_ac3d
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()

        keywords["global_matrix"] = global_matrix

        t = time.mktime(datetime.datetime.now().timetuple())
        import_ac3d.ImportAC3D(self, context, **keywords)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished importing in', t, 'seconds')

        return {'FINISHED'}


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ExportAC3D_MT_Operator(bpy.types.Operator, ExportHelper):
    bl_idname = 'export_scene.export_ac3d'
    bl_label = 'Export AC3D'
    bl_options = {'PRESET'}

    filename_ext = '.ac'

    filter_glob: StringProperty(
        default='*.ac',
        options={'HIDDEN'}
    )

    use_render_layers: BoolProperty(
        name="Only Render Layers",
        description="Only export from selected render layers",
        default=True,
    )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )

    mircol_as_emis: BoolProperty(
        name="Mirror col as Emis",
        description="export mirror colour as emissive colour",
        default=True,
    )

    mircol_as_amb: BoolProperty(
        name="Mirror col as Amb",
        description="export mirror colour as ambient colour",
        default=False,
    )

    crease_angle: FloatProperty(
        name="Default Crease Angle",
        description="Default crease angle for exported .ac faces",
        default=radians(35.0),
        options={"ANIMATABLE"},
        unit="ROTATION",
        subtype="ANGLE",
    )

    def execute(self, context):
        from . import export_ac3d
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))

        global_matrix = axis_conversion(to_forward=self.axis_forward,
                                        to_up=self.axis_up,
                                        ).to_4x4()

        keywords["global_matrix"] = global_matrix
        t = time.mktime(datetime.datetime.now().timetuple())
        export_ac3d.ExportAC3D(self, context, **keywords)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished exporting in', t, 'seconds')

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportAC3D_MT_Operator.bl_idname, text='AC3D (.ac)')


def menu_func_export(self, context):
    self.layout.operator(ExportAC3D_MT_Operator.bl_idname, text='AC3D (.ac)')


classes = (
    ImportAC3D_MT_Operator,
    ExportAC3D_MT_Operator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
