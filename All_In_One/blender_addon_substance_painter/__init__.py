# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
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
        "name": "Substance Painter",
        "description": "Substance Painter Tools",
        "author": "Digiography.Studio",
        "version": (1, 5, 0),
        "blender": (2, 80, 0),
        "location": "Info Toolbar, File -> Import, File -> Export",
        "wiki_url":    "https://github.com/Digiography/blender_addon_substance_painter/wiki",
        "tracker_url": "https://github.com/Digiography/blender_addon_substance_painter/issues",
        "category": "Learnbgame",
}

import bpy

from . import ds_sp

class ds_sp_addon_prefs(bpy.types.AddonPreferences):

        bl_idname = __package__
 
        option_sp_exe : bpy.props.StringProperty(
                name="Substance Executable",
                subtype='FILE_PATH',
                default="C:\Program Files\Allegorithmic\Substance Painter\Substance Painter.exe",
        )
        option_export_folder : bpy.props.StringProperty(
                name="Export Folder Name",
                default="eXport",
        )     
        option_textures_folder : bpy.props.StringProperty(
                name="Textures Folder Name",
                default="Textures",
        )      
        option_save_before_export : bpy.props.BoolProperty(
                name="Save Before Export",
                default=True,
        )     
        option_display_type : bpy.props.EnumProperty(
                items=[('Buttons', "Buttons", "Buttons"),('Menu', "Menu", "Menu"),('Hide', "Hide", "Hide"),],
                name="Display Type",
                default='Buttons',
        )
        option_export_type : bpy.props.EnumProperty(
                items=[('obj', "obj", "obj"),('fbx', "fbx", "fbx"),],
                name="Export Type",
                default='obj',
        )    
        option_import_ext : bpy.props.EnumProperty(
                items=[('png', "png", "png"),('jpeg', "jpeg", "jpeg"),('tiff', "tiff", "tiff"),],
                name="Import Extension",
                default='png',
        )
        option_show_sp_toggle : bpy.props.BoolProperty(
                name="SP Toggle",
                default=True,
        )
        option_show_sp_toggle_state : bpy.props.BoolProperty(
                name="SP Toggle Button State",
                default=False,
        )
        option_relative : bpy.props.BoolProperty(
                name="Relative Paths",
                description="Use Relative Paths for images.",
                default = True
        )  
        option_no_new : bpy.props.BoolProperty(
                name="2018.0.1+ Project File Fix",
                description="Exclude from path for SP 2018.0.1-2018.3.0 to avoid it being added to the textures path.",
                default = False
        )                  
        def draw(self, context):

                layout = self.layout

                box=layout.box()
                box.prop(self, 'option_display_type')
                box.prop(self, 'option_sp_exe')
                box.prop(self, 'option_export_type')
                box.prop(self, 'option_import_ext')
                box=layout.box()
                box.prop(self, 'option_export_folder')
                box.prop(self, 'option_textures_folder')
                box.label(text='Automatically created as a sub folder relative to the saved .blend file. * Do NOT include any "\\".',icon='INFO')
                box.prop(self, 'option_relative')
                box.prop(self, 'option_no_new')
                box.prop(self, 'option_save_before_export')

class ds_sp_prefs_open(bpy.types.Operator):

    bl_idname = "ds_sp.prefs_open"
    bl_label = "Open Preferences"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
 
    def execute(self, context):
        
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')

        return {'FINISHED'}

def register():

        from bpy.utils import register_class

        register_class(ds_sp_addon_prefs)
        register_class(ds_sp_prefs_open)

        ds_sp.register()

def unregister():

        from bpy.utils import unregister_class

        ds_sp.unregister()

        unregister_class(ds_sp_addon_prefs)
        unregister_class(ds_sp_prefs_open)

if __name__ == "__main__":

	register()