""" This python script reads the md5 config files of the hudguns associated with a specific playermodel,
    to import their models and adjusted animations. It also sets up a camera for you so you get a preview
	of how the hudgun would look like in the game. However it does **not** correctly parse cube script.
	It assumes line based commands and greedily parses them and will fail otherwise. Only a selection of
	commands is parsed and the rest is ignored.

	After a few tests this seems to be sufficient to get the job done.
	Invoke this script from the commandline:

	blender --python import_hudguns.py -- playermodel

	where playermodel is an integer in the range 0..3
	0 - mrfixit
	1 - snoutx10k
	2 - inky
	3 - captaincannon
"""

import re
import os
import bpy
import math
from mathutils import Vector
from .io_md5mesh import read_md5mesh
from .io_md5anim import read_md5anim
from .dualquat import BoneAdjustment, adjust_animation

# -------------------------------------------------------------------------------

class LineParser:
	def __init__(self, tokens, mask=0):
		self.tokens = tokens
		self.length = len(self.tokens)
		self.mask = mask
		self.n = 0
		self.line = None
		self.pos = 0
		self.result = None
		self.status = 0

	def feed(self, line):
		self.n = 0
		self.line = line
		self.pos = 0
		self.result = []
		self.status = 0

	def get_default(self, tk):
		if   tk is t_Int:   return 0
		elif tk is t_Float: return 0.0
		elif tk is t_Word:  return ""
		else:               return None

	def convert_match_string(self, tk, ms):
		if   tk is t_Int:   return int(ms)
		elif tk is t_Float: return float(ms)

		if tk is t_Word:
			if ms.startswith('"') and ms.endswith('"'):
				ms = ms[1:-1]
		return ms

	def consume(self, tk, is_optional):
		mobj = tk.match(self.line, self.pos)
		if mobj is None:
			if not is_optional:
				self.status = -1
				return None
			else:
				return self.get_default(tk)

		self.pos = mobj.end()
		ms = mobj.group()

		return self.convert_match_string(tk, ms)

	def advance(self):
		self.consume(t_Sep, True)

		tk = self.tokens[self.n]
		is_optional = self.mask & (1 << self.length - 1 - self.n)
		mobj = self.consume(tk, is_optional)

		self.n += 1
		if tk in (t_Int, t_Float, t_Word):
			self.result.append(mobj)

		if self.n == self.length:
			self.status = 1

	def match(self, line):
		self.feed(line)

		while self.status == 0:
			self.advance()

		if self.status == 1:
			return self.result
		else:
			return None

t_Int   = re.compile(r"-?\d+")
t_Float = re.compile(r"-?\d+(?:\.\d+)?")
t_Word  = re.compile(r'(?:"[^"]*")|\S+')
t_Sep   = re.compile(r"\s+")

def t_literal(s):
	return re.compile(s)

lt_exec      = LineParser([t_literal("exec"), t_Word])
lt_md5dir    = LineParser([t_literal("md5dir"), t_Word])
lt_md5load   = LineParser([t_literal("md5load"), t_Word])
lt_md5anim   = LineParser([t_literal("md5anim"), t_Word, t_Word, t_Int], 0b0001)
lt_md5adjust = LineParser([t_literal("md5adjust"), t_Word, t_Float, t_Float, t_Float, t_Float, t_Float, t_Float], 0b00111111)
lt_md5tag    = LineParser([t_literal("md5tag"), t_Word, t_Word])
lt_md5link   = LineParser([t_literal("md5link"), t_Int, t_Int, t_Word, t_Float, t_Float, t_Float], 0b0000111)
lt_md5skin   = LineParser([t_literal("md5skin"), t_Word, t_Word, t_Word])
lt_mdlscale  = LineParser([t_literal("mdlscale"), t_Int])
lt_mdltrans  = LineParser([t_literal("mdltrans"), t_Float, t_Float, t_Float], 0b0111)

class MD5Part:
	def __init__(self):
		self.filepath = ""
		self.skins = []
		self.adjustments = []
		self.animations = []
		self.tags = {}
		self.bobj = None

class MD5Config:
	def __init__(self, sb_dir, cwd):
		self.sb_dir = sb_dir
		self.parts = []
		self.links = []
		self.scale = 300
		self.translation = 0.0, 0.0, 0.0
		self.cwd = cwd

	def current_part(self):
		return self.parts[-1]

	def readline(self, line):
		lt2meth = (
			(lt_exec,      MD5Config.on_exec),
			(lt_md5dir,    MD5Config.on_md5dir),
			(lt_md5load,   MD5Config.on_md5load),
			(lt_md5anim,   MD5Config.on_md5anim),
			(lt_md5adjust, MD5Config.on_md5adjust),
			(lt_md5tag,    MD5Config.on_md5tag),
			(lt_md5link,   MD5Config.on_md5link),
			(lt_md5skin,   MD5Config.on_md5skin),
			(lt_mdlscale,  MD5Config.on_mdlscale),
			(lt_mdltrans,  MD5Config.on_mdltrans))

		for lt, method in lt2meth:
			result = lt.match(line)
			if result is not None:
				method(self, result)
				break

	def read_cfg_file(self, filepath):
		with open(filepath) as fobj:
			content = fobj.read()

		for line in content.splitlines():
			self.readline(line)

	def on_exec(self, result):
		self.read_cfg_file(os.path.join(self.sb_dir, result[0]))

	def on_md5dir(self, result):
		self.cwd = os.path.join(self.sb_dir, "packages/models", result[0])

	def on_md5load(self, result):
		part = MD5Part()
		part.filepath = os.path.join(self.cwd, result[0])
		self.parts.append(part)

	def on_md5anim(self, result):
		result[1] = os.path.join(self.cwd, result[1])
		part = self.current_part().animations.append(result)

	def on_md5adjust(self, result):
		bone_name = result[0]
		yaw, pitch, roll = result[1:4]
		translation = result[4:7]

		ba = BoneAdjustment(bone_name, yaw, pitch, roll, translation)
		p = self.current_part()
		p.adjustments.append(ba)

		if p.animations:
			print("WARNING! - read bone adjustment after animation")

	def on_md5tag(self, result):
		self.current_part().tags[result[1]] = result[0]

	def on_md5skin(self, result):
		for i in range(1, 3):
			if result[i].startswith("<dds>"):
				result[i] = result[i][5:]
			result[i] = os.path.join(self.cwd, result[i])

		self.current_part().skins.append(result)

	def on_md5link(self, result):
		self.links.append(result)

	def on_mdlscale(self, result):
		self.scale = result[0]
		self.scale = self.scale / 400

	def on_mdltrans(self, result):
		self.translation = result

# -------------------------------------------------------------------------------

def get_child(obj, child_name):
	for child in obj.children:
		if child.name.rsplit(".")[0] == child_name:
			return child

def set_texture(parent, child_name, texture_path):
	child = get_child(parent, child_name)
	img = bpy.data.images.load(texture_path, check_existing=True)

	for mtp in child.data.uv_textures[0].data:
		mtp.image = img

	mat = child.data.materials[0]
	if mat.texture_slots[0] is not None:
		return

	tex = bpy.data.textures.new(child_name, "IMAGE")
	tex.image = img
	slot = mat.texture_slots.add()
	slot.texture = tex

def set_scene_layer(scene, layers):
	for i in range(20):
		scene.layers[i] = scene.layers[i] or layers[i]

	for i in range(20):
		scene.layers[i] = layers[i]

def layer_mask(n):
	return tuple(i == n for i in range(20))

def set_transform(action, translation, scale):
	fcu_loc   = create_fcurves(action, "location", 3, "ObjectTransform")
	fcu_scale = create_fcurves(action, "scale", 3, "ObjectTransform")

	loc = Vector(translation)
	loc.y = -loc.y
	loc *= scale

	set_kf(fcu_loc,   0.0, loc)
	set_kf(fcu_scale, 0.0, (scale, scale, scale))

def create_fcurves(action, data_path, size, group=""):
	return [action.fcurves.new(data_path, i, group) for i in range(size)]

def set_kf(fcurves, time, values, interpolation="CONSTANT"):
	for fcu, val in zip(fcurves, values):
		kf = fcu.keyframe_points.insert(time, val, {'FAST'})
		kf.interpolation = interpolation

# -------------------------------------------------------------------------------

def import_from_config(sb_dir, cfg_filepath, dn):
	md5config = MD5Config(sb_dir, os.path.dirname(cfg_filepath))
	md5config.read_cfg_file(cfg_filepath)

	for i, p in enumerate(md5config.parts):
		arm_obj = read_md5mesh(p.filepath)
		arm_obj.data.draw_type = "WIRE"
		p.bobj = arm_obj

		for skin in p.skins:
			set_texture(arm_obj, skin[0], skin[1])

		for anm in p.animations:
			action = read_md5anim(anm[1])
			action.use_fake_user = True
			action.name = ("hands_"  + dn + "_idle"  if i == 0 and anm[0] == "gun idle"  else
						   "hands_"  + dn + "_shoot" if i == 0 and anm[0] == "gun shoot" else
						   "weapon_" + dn + "_idle"  if i == 1 and anm[0] == "gun idle"  else
						   "weapon_" + dn + "_shoot" if i == 1 and anm[0] == "gun shoot" else
							anm[0]) 

			adjust_animation(arm_obj, p.adjustments)
			anm[1] = action

	for l in md5config.links:
		parent = md5config.parts[l[0]]
		child  = md5config.parts[l[1]]
		tag_name = l[2]
		offset = l[3:6]

		bone_name = parent.tags[tag_name]

		child = child.bobj
		child.scale *= md5config.scale
		child.location = md5config.scale * Vector(offset)
		child.location.y = -child.location.y

		con = child.constraints.new("CHILD_OF")
		con.use_scale_x = False
		con.use_scale_y = False
		con.use_scale_z = False
		con.target = parent.bobj
		con.subtarget = bone_name

	for anm in md5config.parts[0].animations:
		set_transform(anm[1], md5config.translation, md5config.scale)

	md5config.parts[0].bobj.name = "Armature_Hands_" + dn
	md5config.parts[1].bobj.name = "Armature_" + dn

# ------------------------------------------------------------------------------

def setup_cam(scene, fov, width, height):
	cam = bpy.data.objects.get("Camera")
	if cam is None:
		cam_data = bpy.data.cameras.new("Camera")
		cam = bpy.data.objects.new("Camera", cam_data)
		scene.objects.link(cam)

	scene.render.resolution_x = width
	scene.render.resolution_y = height
	scene.camera = cam

	angle = math.radians(65)
	aspect = width / height
	t = math.tan(angle * 0.5)
	hpi = math.pi * 0.5

	cam.location = 0.0, 0.0, 0.0
	cam.rotation_euler = hpi, 0.0, -hpi

	cam_data = cam.data
	cam_data.angle = 2.0 * math.atan(aspect * t)

# ------------------------------------------------------------------------------

if __name__ == "__main__":
	fmt_cfg =  "packages/models/{playermodel:s}/hudguns/{weapon:s}/md5.cfg"
	sb_dir = os.path.expanduser("~/Downloads/Games/sauerbraten_2013/sauerbraten")
	playermodels = "mrfixit", "snoutx10k", "inky", "captaincannon"
	scene = bpy.context.scene

	import sys
	i = int(sys.argv[-1])
	pm = playermodels[i]

	setup_cam(scene, 65, 1280, 1024)

	for i, dn in enumerate(("shotg", "chaing", "rocket", "rifle", "gl", "pistol")):
		scene.update()

		cfg_filepath = os.path.join(sb_dir, fmt_cfg.format(playermodel=pm, weapon=dn))
		print(cfg_filepath)
		set_scene_layer(scene, layer_mask(i))
		import_from_config(sb_dir, cfg_filepath, dn)

	scene.frame_set(0)

	for img in bpy.data.images:
		img.pack()
		img.filepath = ""
