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
# Uso Instrucciones: avisa si la escena esta siendo usada por otro artista. 
# check if the de blend file is being used by other artist.

bl_info = {
    "name": "Scene User",
    "author": "Eugenio Pignataro (Oscurart)",
    "version": (1, 0),
    "blender": (2, 76, 0),
    "location": "",
    "description": "Warns if the scene is being used by another user.",
    "warning": "",
    "wiki_url": "",
    "category": "User Interface",
    }

import bpy
import os
from bpy.app.handlers import persistent
import atexit
import platform

status = False # estado de la escena, si fue abierta o no protegida

class sceneUserWarning(bpy.types.Menu):
    bl_label = "WARNING"
    bl_idname = "OBJECT_MT_warning_scene_user"
    def draw(self, context):
        layout = self.layout
        with open(bpy.data.filepath.replace(".blend",".lock"), "r") as file:
            a = file.read()
        layout.label("Current scene is used by: %s" % (a), icon="ERROR")
        layout.operator("scene.user_scene_force_remove", text="remove lock")


class SceneUserForceRemove(bpy.types.Operator):
    bl_idname = "scene.user_scene_force_remove"
    bl_label = "Scene User Force Remove"

    def execute(self, context):
        global status 
        status = False
        SavePre("dummy")
        return {'FINISHED'}


@persistent
def LoadPost(dummy):
    global status
    if os.path.exists(bpy.data.filepath.replace(".blend",".lock")) == False:
        with open(bpy.data.filepath.replace(".blend",".lock"), "w") as file:
            file.write("%s" % (platform.node()))    
        status = False   
    else:
        if bpy.app.background == False:
            bpy.ops.wm.call_menu(name=sceneUserWarning.bl_idname)
        else:
            print("Scene in Backround")    
        status = True        
    
@persistent                  
def LoadPre(dummy):
    global status
    try:
        if os.path.exists(bpy.data.filepath.replace(".blend",".lock")):
            if status == False:            
                os.remove(bpy.data.filepath.replace(".blend",".lock")) 
    except:
        pass       

@persistent                  
def SavePre(dummy):
    global status
    try:
        if os.path.exists(bpy.data.filepath.replace(".blend",".lock")):
            if status == False:            
                os.remove(bpy.data.filepath.replace(".blend",".lock")) 
    except:
        pass  


@persistent
def SavePost(dummy):
    global status
    if os.path.exists(bpy.data.filepath.replace(".blend",".lock")) == False:
        with open(bpy.data.filepath.replace(".blend",".lock"), "w") as file:
            file.write("%s" % (platform.node()))    
        status = False   



bpy.app.handlers.load_pre.append(LoadPre)
bpy.app.handlers.load_post.append(LoadPost)
bpy.app.handlers.save_pre.append(SavePre)
bpy.app.handlers.save_post.append(SavePost)

## funcion borra salida
def my_cleanup_code():
    if status == False:
        os.remove(bpy.data.filepath.replace(".blend",".lock")) 

# registro salida
atexit.register(my_cleanup_code)

def register():
    bpy.utils.register_module(__name__)
def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
