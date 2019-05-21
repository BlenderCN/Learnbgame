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
    "name": "Make Face (experimental)",
    "author": "Thomas Larsson",
    "version": "0.1",
    "blender": (2, 6, 4),
    "location": "View3D > Properties > Make Face",
    "description": "Make MakeHuman Face. Experimental tool, not recommended for end-users.",
    "warning": "",
    'wiki_url': "http://www.makehuman.org/node/223",
    "category": "Learnbgame"
}

if "bpy" in locals():
    print("Reloading makeface")
    import imp    
    imp.reload(mh_utils)
    imp.reload(mh)
    imp.reload(utils)
    imp.reload(settings)
    imp.reload(proxy)
    imp.reload(warp)
    imp.reload(import_obj)
    imp.reload(character)
    
    imp.reload(makeface)
else:
    print("Loading makeface")
    import bpy
    import os
    from bpy.props import *
    from bpy_extras.io_utils import ImportHelper, ExportHelper

    import mh_utils
    from mh_utils import mh
    from mh_utils import utils
    from mh_utils import settings
    from mh_utils import proxy
    from mh_utils import warp
    from mh_utils import import_obj
    from mh_utils import character
    
    from . import makeface
            
#----------------------------------------------------------
#   class MakeFacePanel(bpy.types.Panel):
#----------------------------------------------------------

class MakeFacePanel(bpy.types.Panel):
    bl_label = "Make Face"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        if not utils.drawConfirm(layout, scn):
            return
        settings.drawDirectories(layout, scn)

        layout.label("Base Character")
        character.drawItems(layout, scn)
        layout.operator("mh.create_base_character")

        layout.separator()
        layout.label("Mask")
        layout.operator("mh.generate_mask")
        #layout.operator("mh.make_mask")    
        #layout.operator("mh.shapekey_mask")    
        layout.separator()

        if not utils.checkForNumpy(layout, "MakeFace"):
            return

        layout.label("Face")
        layout.operator("mh.generate_face")
        #layout.prop(scn, "MhStiffness")
        #layout.prop(scn, "MhLambda")
        #layout.prop(scn, "MhIterations")

        ob = context.object
        if ob and ob.MhMaskFilePath:
            layout.operator("mh.save_face")
        layout.operator("mh.save_face_as")


#----------------------------------------------------------
#   Settings buttons
#----------------------------------------------------------

class OBJECT_OT_FactorySettingsButton(bpy.types.Operator):
    bl_idname = "mh.factory_settings"
    bl_label = "Restore Factory Settings"

    def execute(self, context):
        settings.restoreFactorySettings(context)
        return{'FINISHED'}    


class OBJECT_OT_SaveSettingsButton(bpy.types.Operator):
    bl_idname = "mh.save_settings"
    bl_label = "Save Settings"

    def execute(self, context):
        settings.saveDefaultSettings(context)
        return{'FINISHED'}    


class OBJECT_OT_ReadSettingsButton(bpy.types.Operator):
    bl_idname = "mh.read_settings"
    bl_label = "Read Settings"

    def execute(self, context):
        settings.readDefaultSettings(context)
        return{'FINISHED'}    

#----------------------------------------------------------
#   Register
#----------------------------------------------------------

def register():
    mh_utils.init()
    warp.init()
    makeface.init()
    bpy.utils.register_module(__name__)
  
def unregister():
    bpy.utils.unregister_module(__name__)
 
if __name__ == "__main__":
    register()
