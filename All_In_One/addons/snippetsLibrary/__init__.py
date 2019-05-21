'''
Copyright (C) 2017 YOUR NAME
YOUR@MAIL.com

Created by YOUR NAME

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "snippets library",
    "description": "Add a library list to quickly load/save personnal texts snippets from text editor",
    "author": "Samuel Bernou",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "location": "Text editor > toolbar",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }


import bpy
from bpy.props import IntProperty, CollectionProperty #, StringProperty 

# load and reload submodules
##################################

import importlib
from . import developer_utils
#from . import func
#from . import operators
from .operators import *
from .func import *

importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())


### addon preferences panel
 
class snippetsPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    snippets_custom_path : bpy.props.BoolProperty(
        name='Use custom path',
        description="Set a cutom directory for snippets library",
        default=False)
 
    snippets_filepath : bpy.props.StringProperty(
        name="Snippets folder",
        subtype='FILE_PATH',
        )
 
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "snippets_custom_path")
        layout.label(text="Snippets will be saved as invidual files")
        layout.label(text="in a folder named 'snippets' (created at first use)")
        layout.label(text="located aside the addon file (unless you enter a custom path)")
        if self.snippets_custom_path:
            #layout.label(text="Leave the field empty to get default location")#"Custom path to you text load/save folder\n"
            layout.prop(self, "snippets_filepath")
            layout.label(text="May not work if space are in path.")


# register
##################################

classes = (
SNIPPETSLIB_OT_actions,
SNIPPETSLIB_OT_saveSnippet,
SNIPPETSLIB_OT_insertTemplate,
SNIPPETSLIB_OT_reloadItems,
SNIPPETSLIB_OT_OpenSnippetsFolder,
SNIPPETSLIB_sniptoolProp,
SNIPPETSLIB_UL_items,
SNIPPETSLIB_PT_uiList,
snippetsPreferences,
)

import traceback

def register():
    try:
        for cls in classes:
            bpy.utils.register_class(cls)
    except:
        traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    bpy.types.Scene.sniptool = CollectionProperty(type=SNIPPETSLIB_sniptoolProp)
    bpy.types.Scene.sniptool_index = IntProperty()


def unregister():
    try:
        for cls in classes:
            bpy.utils.unregister_class(cls)
    except:
        traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
    del bpy.types.Scene.sniptool
    del bpy.types.Scene.sniptool_index
    

if __name__ == "__main__":
    register()