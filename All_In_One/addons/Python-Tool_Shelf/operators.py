import bpy
import addon_utils
import os
import subprocess
import importlib.util
import threading

blenderAddonPaths = addon_utils.paths()
externalPythonScripts = []
pythonNames = []
vaildPythonLocation = ""

def get_Files_in_Directory(path, onlyPyFiles):
    files = []
    
    if onlyPyFiles:
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(".py")]
    else:
        files = [f for f in os.listdir(path)]
        
    return files


class ExternalPythonThread(threading.Thread):
    running = False
    pathToPy = ""
    nameWithoutExtension = ""
    
    def __init__(self):
        threading.Thread.__init__(self)
        return
    
    def start(self):
        self.running = True
        threading.Thread.start(self)
        
    def stop(self):
        self.running = False
        
    def run(self):
        fileSpec = importlib.util.spec_from_file_location(self.nameWithoutExtension, self.pathToPy)
        userModule = importlib.util.module_from_spec(fileSpec)
        fileSpec.loader.exec_module(userModule)
        
        #Only execute python file once
        return
        
for path in blenderAddonPaths:
    basePath = os.path.join(path, "Python-Tool-Shelf", "scripts")
    exists = os.path.exists(basePath)
    if exists:
        pythonNames = get_Files_in_Directory(basePath, True)
        vaildPythonLocation = basePath

for name in pythonNames:
    class exterPythonFile(bpy.types.Operator):
        bl_idname = ('externalpython.' + name.lower().replace('.',""))
        bl_label = name
        bl_description = name
        pathToPy = os.path.join(vaildPythonLocation, name)
        nameWithoutExtension = os.path.splitext(name)[0]
        timer = None
        thread = None
        
        def modal(self, context, event):
            if event.type == 'TIMER':
                if not self.thread.isAlive():
                    self.report({'INFO'}, "Operator: " + self.bl_label + " Done.")
                    self.thread.join()
                    return {'FINISHED'}
                else:
                    return {'PASS_THROUGH'}
                
            return {'PASS_THROUGH'}
                
        def invoke(self, context, event):
            self.thread = ExternalPythonThread()
            self.thread.pathToPy = self.pathToPy
            self.thread.nameWithoutExtension = self.nameWithoutExtension
            
            self.thread.start()
            self.timer = context.window_manager.event_timer_add(0.05, context.window)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
    
    externalPythonScripts.append(exterPythonFile)
