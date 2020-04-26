# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any laTter version.
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


##########################################################################################################
##########################################################################################################

bl_info = {   
 "name": "GYAZ Game Rigger",   
 "author": "Andras Gyalog",   
 "version": (2, 80, 0),   
 "blender": (2, 80, 0),   
 "location": "",   
 "description": "Rig geared for real-time rendering with linear skinning.",
 "warning": "",   
 "wiki_url": "",   
 "tracker_url": "",   
 "category": "Learnbgame",
 }

import bpy 
from bpy.types import AddonPreferences

class GYAZ_GameRigger_Preferences (AddonPreferences):
    # single-file addon: __name__
    # multi-file addon: __package__
    bl_idname = __name__
                   
    def draw(self, context):
        
        lay = self.layout
        lay.label ('Game Rigger')
        lay.label ('3D View > SHIFT+A > Armature > GYAZ Source Rig or 3D View > Header > Add > Armature > GYAZ Source Rig or 3D View')
        lay.label ('3D View > SPACE > GYAZ Game Rigger: Generate Rig')
        lay.label ('At least one mesh should be parented to the rig and all bones should be inside a mesh.')
        lay.label ('Manuel Bastioni Rig to GYAZ Source Rig')
        lay.label ('3D View > SPACE > Manuel Bastioni Rig to GYAZ Source Rig')
        

# Registration
def register():
    bpy.utils.register_class (GYAZ_GameRigger_Preferences)

def unregister():
    bpy.utils.unregister_class (GYAZ_GameRigger_Preferences)

register()


modulesNames = ['ui', 'generate_rig', 'manuel_bastioni_to_gyaz_source_rig']
 
import sys
import importlib
 
modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()
 
def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()
 
if __name__ == "__main__":
    register()
