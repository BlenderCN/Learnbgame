import bpy
import os
from bpy.app.handlers import persistent

bl_info = {"name": "autoFBX", "category": "Learnbgame"
}

@persistent
def save_fbx(scene):
	#Edit filename to end in .fbx
	newpath = os.path.splitext(bpy.data.filepath)[0] + '-groups/'

	if not os.path.exists(newpath):
		os.makedirs(newpath)

	print('AutoFBX::Exporting to FBX in current directory...')
	bpy.ops.export_scene.fbx(check_existing=False, filepath=newpath, version='BIN7400', mesh_smooth_type='FACE', batch_mode='GROUP', use_batch_own_dir=False, use_selection=False, axis_forward='X', axis_up='-Z', global_scale=100)


def register():
	bpy.app.handlers.save_post.append(save_fbx)
    
def unregister():
    print("AutoFBX Disabled")

