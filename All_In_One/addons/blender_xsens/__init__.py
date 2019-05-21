bl_info = {
    "name": "XSens Mocap",
    "author": "Benjamin Brieber",
    "version": (1, 0),
    "blender": (2, 71, 0),
    "location": "File > Import-Export > Mocap",
    "description": "Import-Export STL files",
    "warning": "",
    "category": "Rigging",
}
 

import bpy

from blender_xsens.xsens_blender_ui import XSensPanel, OBJECT_OT_RecordButton

def register():
    bpy.utils.register_class(XSensPanel)
    bpy.utils.register_class(OBJECT_OT_RecordButton)
    print("registered")
  
def unregister():
    print("unregistered")
    bpy.utils.unregister_class(XSensPanel)
    bpy.utils.unregister_class(OBJECT_OT_RecordButton)