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

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165

bl_info = {
    "name": "MakeHuman Utilities (do NOT enable!)",
    "author": "Thomas Larsson",
    "version": "0.2",
    "blender": (2, 6, 5),
    "api": 40000,
    "location": "None",
    "description": "Utility package for MakeHuman scripts. Don't enable this addon - it is visible only to kill some annoying error messages in the console.",
    "warning": "",
    'wiki_url': "",
    "category": "Learnbgame",
}


if "bpy" in locals():
    print("Reloading mh_utils")
    import imp
    imp.reload(mh)
    imp.reload(utils)
    imp.reload(settings)
    imp.reload(proxy)
    imp.reload(warp)
    imp.reload(import_obj)
    imp.reload(character)
else:
    print("Loading mh_utils")
    import bpy
    from . import mh
    from . import utils
    from . import settings
    from . import proxy
    from . import warp
    from . import import_obj
    from . import character


class VIEW3D_OT_DummyButton(bpy.types.Operator):
    bl_idname = "mh.dummy"
    bl_label = "Dummy"
    
    def execute(self, context):
        return {'FINISHED'}


def init():
    mh.confirm = None
    mh.confirmString = "?"

    settings.init()
    import_obj.init()
    character.init()
  
  
def register():
    bpy.utils.register_module(__name__)
  
def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
  
