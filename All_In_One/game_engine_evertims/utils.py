import json
import bpy

def dict2str(d):
	return json.dumps(d)

def str2dict(s):
	return json.loads(s) 

def loadMatFile(context, force = False):

	evertims = context.scene.evertims

	# discard if already loaded
	if not evertims.mat_list_need_update and not force:
		return evertims.mat_list

	# get material file name
	addon_prefs = context.user_preferences.addons[__package__].preferences
	fileName = bpy.path.abspath(addon_prefs.raytracing_client_path_to_matFile)
		
	# load mat file
	fileObj  = open(fileName, 'r')
	mat = dict()

	# loop over lines (one per material)
	lines = fileObj.readlines()
	for line in lines:
		l = line.lstrip().split(' ')
		absArray = [float(x) for x in l[0:10]]
		diff = l[10]
		name = l[11].rstrip()
		mat[name] = absArray
	
	# update update flag
	evertims.mat_list_need_update = False

	# return material dictionary as string
	return dict2str(mat)