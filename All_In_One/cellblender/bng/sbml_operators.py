import bpy
import os

from . import sbml2blender




    
#from . import sbml2json
#from . import sbml2json
# We use per module class registration/unregistration

filePath = ''

def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)




def execute_sbml2mcell(filepath,context):
    mcell = context.scene.mcell
    execute_externally(filepath,context)
    #TODO: If isTransformed is false a window should be shown that the model failed to load
    return{'FINISHED'}

def execute_externally(filepath,context):
    import subprocess
    import shutil
    mcell = context.scene.mcell
    if mcell.cellblender_preferences.python_binary_valid:
        python_path = mcell.cellblender_preferences.python_binary
    else:
        python_path = shutil.which("python", mode=os.X_OK)
    destpath = os.path.dirname(__file__)
    subprocess.call([python_path,destpath + '{0}sbml2json.py'.format(os.sep),'-i',filepath])
   
def execute_sbml2blender(filepath,context,addObjects=True):
    mcell = context.scene.mcell
    sbml2blender.sbml2blender(filepath,addObjects)

