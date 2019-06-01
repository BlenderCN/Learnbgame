#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****



bl_info = {
    "name": "Maxwell MXS Format",
    "author": "al3p (uaraus)",
    "version": (0, 5),
    "blender": (2, 6, 2),
#    "api": 37699,
    "location": "File > Import-Export",
    "description": "Export to MXS file format",
    "warning": "Beta",
    "wiki_url": "https://github.com/al3p/BtoMW",
    "tracker_url": "",
    "category": "Learnbgame",
}

# Release Log
# ============================================================
# 0.5 First Public release 
# ------------
# 0.4 Private release 
# * cleaning
# * update for Blender 2.62 matrix access
# ------------
# 0.3 Private release 
# * added scene to export interface
# * visibility object check
# ------------
# 0.2 Private release 
# * update for Blender 2.61 camera settings
# ------------
# 0.1 Private release 
# * initial release
# ------------



# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    import imp
    if "export_mxs" in locals():
        imp.reload(export_mxs)

import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper, path_reference_mode, axis_conversion






# ===========================================================
# === Definition of new operator ============================
# ===========================================================
class ExportMXS(bpy.types.Operator, ExportHelper):
    '''Save a Maxwell MXS File'''

    bl_idname = "export_scene.mxs"
    bl_label = 'Export MXS'
    bl_options = {'PRESET', 'REGISTER', 'UNDO'}

    filename_ext = ".mxs"
    filter_glob = StringProperty(default="*.mxs", options={'HIDDEN'})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    # context group
    use_selection = BoolProperty(name="Selection Only", description="Export selected objects only", default=True)
    #use_animation = BoolProperty(name="Animation", description="", default=False)

    # object group
    use_apply_modifiers = BoolProperty(name="Apply Modifiers", description="Apply modifiers to mesh before exporting", default=True)
    use_apply_xform = BoolProperty(name="Apply trasformation on neg scale", description="Warning: will modify the file", default=False)

    # extra data group
    use_uvs = BoolProperty(name="UVs", description="", default=True)
    use_materials = BoolProperty(name="Materials", description="", default=True)
    # copy_images = BoolProperty(name="Copy Images", description="", default=False)
    # use_vertex_groups = BoolProperty(name="Polygroups", description="", default=False)

    # grouping group
    # use_blen_objects = BoolProperty(name="Objects as MXS Objects", description="", default=True)

    global_scale = FloatProperty(name="Scale", description="Scale all data", min=0.01, max=1000.0, soft_min=0.01, soft_max=1000.0, default=1.0)

    #axis_forward = EnumProperty(
    #        name="Forward",
    #        items=(('-Z', "-Z Forward", ""),
    #               ('-Y', "-Y Forward", ""),
    #               ('-X', "-X Forward", ""),
    #               ('Z', "Z Forward", ""),
    #               ('Y', "Y Forward", ""),
    #               ('X', "X Forward", ""),
    #               ),
    #        default='-Z',
    #        )

    #axis_up = EnumProperty(
    #        name="Up",
    #        items=(('-Z', "-Z Up", ""),
    #               ('-Y', "-Y Up", ""),
    #               ('-X', "-X Up", ""),
    #               ('Z', "Z Up", ""),
    #               ('Y', "Y Up", ""),
    #               ('X', "X Up", ""),
    #               ),
    #       default='Y',
    #        )

    path_mode = path_reference_mode

    # ===========================================================
    # === Operator execution function ===========================
    # ===========================================================
    def execute(self, context):
        from . import export_mxs #done here, @top level does not work.

        from mathutils import Matrix
        #keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "check_existing", "filter_glob"))

        global_matrix = Matrix()
        global_matrix[0][0] = global_matrix[1][1] = global_matrix[2][2] = self.global_scale
        #global_matrix = global_matrix * axis_conversion(to_forward=self.axis_forward, to_up=self.axis_up).to_4x4()
        #XXX below: passing the whole operator then duplicating the info in it 
        ee = export_mxs.export(self, #the operator 
                               context,
                               None,
                               self.path_mode,
                               self.use_selection,
                               global_matrix,
                               self.global_scale,
                               self.filepath,
                               self.use_uvs,
                               self.use_apply_modifiers,
                               self.use_apply_xform,
                               self.use_materials)
        return ee.save()
    # end execute

# end operator class



# ===========================================================
# === Callback and Registration functions ===================
# ===========================================================

def menu_func_export(self, context):
    self.layout.operator(ExportMXS.bl_idname, text="Maxwell (.mxs)")
# end callback function

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

# end register

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
# end unregister



# ===========================================================
# === Default behavior ======================================
# ===========================================================

if __name__ == "__main__":
    register()










