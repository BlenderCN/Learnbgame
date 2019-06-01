import bpy
import sys #import system stuff so path can be appended
#import numpy #util for working with numbers

sys.path.append('Z:\\PythonWorkspace\\BlenderExtraLibs')

#library for working with realtime audio. command shortcut is sd.{command}
import sounddevice as sd
import mido as midi
import python-osc as osc

def refresh_devices():
    """Refreshes deviceList and recomputes parameters."""
    
    deviceList = sd.query_devices()
    
    #this is a bad but functional way of getting length
    deviceCount = deviceList.index(deviceList[-1])
    return deviceCount


refresh_devices()


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
    bpy.utils.register_class(AudioIOSettingsPanel)
    

def unregister():
    bpy.utils.unregister_class(AudioSettingsPanel)

#enables standalone support    
if __name__ == "__main__":
    register()