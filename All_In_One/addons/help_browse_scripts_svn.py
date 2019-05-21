# #####BEGIN GPL LICENSE BLOCK #####
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
# #####END GPL LICENSE BLOCK #####

bl_info = {
	"name": "browse scripts svn",
	"author": "Meta-Androcto",
	"version": (0, 1),
	"blender": (2, 5, 9),
	"api": 40500,
	"location": "Help > Browse Scripts SVN",
	"description": "Contrib & External Script URL Browser",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame"
}
	
import bpy
import urllib
import urllib.request
import webbrowser

class INFO_MT_help_browse_contrib(bpy.types.Menu):
    bl_idname = "INFO_MT_help_browse_contrib"
    bl_label = "Browse Contrib Scripts"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("wm.url_open", text="Contrib Scripts").url = 'https://svn.blender.org/svnroot/bf-extensions/contrib/py/scripts/addons/'
        


class INFO_MT_help_browse_extern(bpy.types.Menu):
    bl_idname = "INFO_MT_help_browse_extern"
    bl_label = "Browse External Scripts"

        ### Contrib Browse ###
    def draw(self, context):		
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("wm.url_open", text="External Scripts").url = 'http://blenderpython.svn.sourceforge.net/viewvc/blenderpython/scripts_library/'
        

class INFO_MT_help_scripts_browser(bpy.types.Menu):
    bl_idname = "INFO_MT_help_scripts_browser"
    bl_label = "Extra Scripts Browser"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
		
        layout.operator("wm.call_menu", text="Browse Contrib").name = "INFO_MT_help_browse_contrib"
        layout.operator("wm.call_menu", text="Browse Extern").name = "INFO_MT_help_browse_extern"

		
    def execute(self, context):
        import webbrowser
        webbrowser.open(self.url)
        return {'FINISHED'}

#### REGISTER ####
def add_object_button(self, context):
    self.layout.menu("INFO_MT_help_scripts_browser", icon="PLUGIN")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_help.append(add_object_button)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_help.remove(add_object_button)


if __name__ == '__main__':
    register()