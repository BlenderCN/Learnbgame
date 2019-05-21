import bpy
from . import preferences as P

LM_MASTER_COLLECTION = "Master Collection"
LM_ASSET_COLLECTION = "Assets_Collection"
LM_COMPATIBLE_MESH_FORMAT = {".fbx":(bpy.ops.import_scene.fbx, {'filter_glob':'*.fbx;', 'axis_forward':'-Z', 'axis_up':'Y'}),
								".obj":(bpy.ops.import_scene.obj, {'filter_glob':'*.obj;*.mtl', 'axis_forward':'-Z', 'axis_up':'Y'})}
LM_COMPATIBLE_TEXTURE_FORMAT = {".png":(),
									".tga":()}

LM_CHANNELS = [] if P.get_prefs() is None else [P.get_prefs().textureSet_albedo_keyword,
												P.get_prefs().textureSet_normal_keyword,
												P.get_prefs().textureSet_roughness_keyword,
												P.get_prefs().textureSet_metalic_keyword]

LM_NAMING_CONVENTION_KEYWORDS_COMMON = {'project':[],
										'team':[],
										'category':[],
										'incr':[],
										'gender':['m', 'f', 'mf', 'u']}

LM_NAMING_CONVENTION_KEYWORDS_MESH = {'plugname':[]}
LM_NAMING_CONVENTION_KEYWORDS_TEXTURE = {'tincr':[],
										'matid':[],
										'channel':LM_CHANNELS}

LM_NAMING_CONVENTION_KEYWORDS = {}

LM_NAMING_CONVENTION_KEYWORDS.update(LM_NAMING_CONVENTION_KEYWORDS_COMMON)
LM_NAMING_CONVENTION_KEYWORDS.update(LM_NAMING_CONVENTION_KEYWORDS_MESH)
LM_NAMING_CONVENTION_KEYWORDS.update(LM_NAMING_CONVENTION_KEYWORDS_TEXTURE)
LM_NAMING_CONVENTION_KEYWORDS.update({'assetname':[]})


class GetParam(object):
	def  __init__(self, scn):
		param = {}
		for p in dir(scn):
			if 'lm_' == p[0:3]:
				param.update({p:getattr(scn, p)})

		self.param = param