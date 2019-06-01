#
#
#
#

bl_info = {
	"name": "Lineyka",
	"description": "Production manager: tasks , assets , outsource",
	"author": "Volodya Renderberg",
	"version": (1, 0),
	"blender": (2, 78, 0),
	"location": "View3d tools, ui panels",
	"warning": "", # used for warning icon and text in addons panel
	"category": "Learnbgame",
}

if "bpy" in locals():
    import importlib
    #importlib.reload(tmp_armature_create)
    #importlib.reload(face_rig_create)
    importlib.reload(blender_ui)
else:
    #from . import tmp_armature_create
    #from . import face_rig_create
    from . import blender_ui

import bpy


##### REGISTER #####

def register():
	#bpy.utils.register_module(__name__)
    #tmp_armature_create.register()
    blender_ui.register()
	
def unregister():
	#tmp_armature_create.unregister()
	blender_ui.unregister()
	#bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
    register()

