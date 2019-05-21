#enables standalone support
if __name__ == "__main__":
    import bpy
    import sys
    from os.path import dirname, join, abspath, basename
    mainPackage = dirname(bpy.data.filepath) #bpy filepath is the blend file
    if not mainPackage in sys.path:
        sys.path.append(mainPackage)
    library = join(mainPackage, "libs")
    if not library in sys.path:
        sys.path.append(library)
        print(library + " appended to sys path")

import bpy
import sys #import system so path can be appended
from bpy.utils import register_class as register_class
from bpy.utils import unregister_class as unregister_class

import io.io_handler #import the custom io handler

refresh_device_list("audio")


class DeviceListInput(bpy.types.Menu): #incomplete. still making menu
    bl_label = "Input Device"
    
    def draw(self, context):
        layout = self.layout
            
    i = 0
    for i, deviceCount:
        name[i] = [
        deviceList[i].get('name'), #device friendly name
        deviceList[i].get('max_input_channels'),
        deviceList[i].get('max_output_channels'),
        deviceList[i].get(


class AudioIOSettingsPanel(bpy.types.Panel):
    """Audio settings and information."""
    bl_label = "Audio IO Settings"
    bl_idname = "Nimbus_SCENE_AIO_panel"
    bl_space_type = "PROPERTIES"
    bl_context = "scene"
    deviceNameInput = "No input selected"
    deviceNameOutput = "No output selected"
    
    def draw(self, context):
        layout = self.layout
        
        scene = context.scene
        
        #text
        layout.label(text = "Select Input")
        
        
        
        
        
        
        
        
#causes blender to register the classes as classes
def register():
    register_class(AudioIOSettingsPanel)
    

def unregister():
    unregister_class(AudioSettingsPanel)
    sys.path.remove('Z:\\PythonWorkspace\\BlenderExtraLibs')