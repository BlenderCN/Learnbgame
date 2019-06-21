#====================== BEGIN GPL LICENSE BLOCK ======================
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
#======================= END GPL LICENSE BLOCK ========================

bl_info = {
    "name": "EVERTims, real-time auralization framework",
    "author": "David Poirier-Quinot",
    "version": (0, 1),
    "blender": (2, 7, 8),
    "location": "3D View > Toolbox",
    "description": "A collection of tools to configure your EVERTims environment.",
    "warning": "",
    'tracker_url': "https://evertims.github.io/#contact",
    "wiki_url": "https://evertims.github.io",
    'support': 'COMMUNITY',
    "category": "Learnbgame",
}

if "bpy" in locals():
    import importlib
    importlib.reload(ui)
else:
    import bpy
    import os
    from bpy.props import (
            StringProperty,
            EnumProperty,
            BoolProperty,
            IntProperty,
            FloatProperty,
            PointerProperty
            )
    from bpy.types import (
            PropertyGroup,
            AddonPreferences
            )
    from . import (
            ui,
            operators
            )
import imp

# tag update required when changing mat file
def updateMatFileCallback(self, context):
    evertims = context.scene.evertims
    evertims.mat_list_need_update = True

class EVERTimsSettings(PropertyGroup):

    enable_bge = BoolProperty(
            name="Enable EVERTims",
            description='Activate EVERTims module in BGE',
            default=False,
            )
    enable_edit_mode = BoolProperty(
            name="Enable EVERTims in EDIT mode",
            description='Activate real-time update of the EVERTims client from Blender outside the BGE (in casual edit mode)',
            default=False,
            )
    debug_logs_raytracing = BoolProperty(
            name="Print Raytracing Logs",
            description='Print raytracing client logs in Blender console',
            default=False,
            )
    debug_rays = BoolProperty(
            name="Draw Rays",
            description='Enable visual feedback on EVERTims raytracing in Blender',
            default=True,
            )
    debug_logs = BoolProperty(
            name="Print Logs",
            description='Print logs of the EVERTims python module in Blender console',
            default=False,
            )
    movement_threshold_loc = FloatProperty(
            name="Movement threshold location",
            description="Minimum value a listener / source must move to be updated on EVERTims client",
            default=0.1,
            )
    movement_threshold_rot = FloatProperty(
            name="Movement threshold rotation",
            description="Minimum value a listener / source must rotate to be updated on EVERTims client",
            default=1,
            )
    ip_local = StringProperty(
            name="IP local",
            description="IP of the computer running Blender",
            default="127.0.0.1", maxlen=1024,
            )
    ip_raytracing = StringProperty(
            name="IP EVERTims client",
            description="IP of the computer running the EVERTims raytracing client",
            default="127.0.0.1", maxlen=1024,
            )
    port_write_raytracing = IntProperty(
            name="Port write",
            description="Port used by EVERTims raytracing client to read data sent by the Blender",
            default=3858,
            )
    port_read = IntProperty(
            name="Port read",
            description="Port used by Blender to read data sent by the EVERTims raytracing client",
            default=3862,
            )

    # EVERTims Raytracing client properties
    enable_raytracing_client = BoolProperty(
            name="Launch EVERTims raytracing client",
            description='Launch the EVERTims raytracing client as a subprocess (embedded in Blender)',
            default=False,
            )
    ip_auralization = StringProperty(
            name="IP EVERTims auralization client",
            description="IP of the computer running the EVERTims auralization client",
            default="127.0.0.1", maxlen=1024,
            )
    port_write_auralization = IntProperty(
            name="Port EVERTims auralization client",
            description="Port used by the auralization client to read data sent by the raytracing client",
            default=3860,
            )
    min_reflection_order = IntProperty(
            name="Min reflection order",
            description="Min reflection order passed to the embedded EVERTims client",
            default=1,
            )
    max_reflection_order = IntProperty(
            name="Max reflection order",
            description="Max reflection order passed to the embedded EVERTims client",
            default=2,
            )

    # EVERTims auralization client properties
    enable_auralization_client = BoolProperty(
            name="Launch EVERTims auralization client",
            description='Launch the EVERTims auralization client as a subprocess (embedded in Blender)',
            default=False,
            )

    # EVERTims elements
    room_object = StringProperty(
            name="Room",
            description="Current room selected for auralization",
            default="", maxlen=1024,
            ) 
    listener_object = StringProperty(
            name="Listener",
            description="Current listener selected for auralization",
            default="", maxlen=1024,
            ) 
    source_object = StringProperty(
            name="Source",
            description="Current source selected for auralization",
            default="", maxlen=1024,
            )     
    mat_list = StringProperty(
            name="Material List",
            description="A string of all available materials, displayed in GUI",
            default="", maxlen=0, # unlimited length
            ) 
    mat_list_need_update = BoolProperty(
            name="Check whether mat_list need update of not",
            description='',
            default=True,
            )

class EVERTimsPreferences(AddonPreferences):
    bl_idname = __name__

    raytracing_client_path_to_binary = StringProperty(
            name="EVERTims Raytracing client binary path",
            description="Path to the ims binary that handles EVERTims raytracing",
            default="//", maxlen=1024, subtype="FILE_PATH",
            )
    raytracing_client_path_to_matFile = StringProperty(
            name="EVERTims Raytracing client material path",
            description="Path to the .mat file used by the EVERTims raytracing client",
            default="//", maxlen=1024, subtype="FILE_PATH", update = updateMatFileCallback,
            )
    auralization_client_path_to_binary = StringProperty(
            name="EVERTims auralization client binary path",
            description="Path to the binary that handles EVERTims auralization",
            default="//", maxlen=1024, subtype="FILE_PATH",
            )

# ############################################################
# Un/Registration
# ############################################################

def register():

    bpy.utils.register_class(EVERTimsSettings)
    bpy.utils.register_class(EVERTimsPreferences)

    ui.register()
    operators.register()

    bpy.types.Scene.evertims = PointerProperty(type=EVERTimsSettings)


def unregister():

    bpy.utils.unregister_class(EVERTimsSettings)
    bpy.utils.unregister_class(EVERTimsPreferences)

    ui.unregister()
    operators.unregister()

    del bpy.types.Scene.evertims
