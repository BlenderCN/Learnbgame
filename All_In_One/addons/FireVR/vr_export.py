import os
import io
import shutil
from contextlib import redirect_stdout

import bpy
from mathutils import Vector, Quaternion

from .html import Tag
from . import ipfs

# boolean to string
def b2s(b):
	return str(b).lower()

# float to string
def f2s(f):
	return "{0:.6f}".format(f)

# vector to string
def v2s(v):
	return " ".join("{0:.6f}".format(c) for c in v)

# position to string
def p2s(v):
	v = [v[0],v[2],-v[1]]
	return v2s(v)

# "light" position to string
# used in cases where inversing the Z would be an awful idea
def lp2s(v):
	v = [v[0],v[2],v[1]]
	return v2s(v)

# rotation to string
def r2s(m):
	return v2s(list(m*Vector([-1,0,0,0]))[:3])

# rotation to string, room fwd edition
def r2sr(m):
	return v2s(list(m*Vector([0,0,-1,0]))[:3])

# Insert rotation
# Moved here from the original code in the MESH handler
# Used for links based on placeholder planes.
# Notably, I assume Euler X 90 YZ 0 is a standing link.
# (Later) this turned to be somewhat wrong, fixing it now.
# Code still here in case this setup is useful for something.
#def ir(attr, m):
#	rot = [" ".join([str(f) for f in list(v.xyz)]) for v in m.normalized()]
#	attr += [("xdir", rot[0]), ("ydir", rot[1]), ("zdir", rot[2]),]

# Yes, it's probably inefficient, but I already tried messing around
#  with the function seen in ir, and it was painful.
# This one's used for text and links.
def mt2(attr, m):
	m = m.normalized()
	attr += [("xdir", p2s(list(m*Vector([1,0,0,0]))[:3]))]
	attr += [("ydir", p2s(list(m*Vector([0,1,0,0]))[:3]))]
	attr += [("zdir", p2s(list(m*Vector([0,0,1,0]))[:3]))]

# Here's one that's used for models.
def mtm(attr, m):
	m = m.normalized()
	attr += [("xdir", p2s(list(m*Vector([-1,0,0,0]))[:3]))]
	attr += [("ydir", p2s(list(m*Vector([0,0,1,0]))[:3]))]
	attr += [("zdir", p2s(list(m*Vector([0,-1,0,0]))[:3]))]

def write_html(scene, filepath, path_mode):

	stdout = io.StringIO()

	world = scene.world

	doc = Tag("!DOCTYPE html", single=True)

	html = Tag("html")
	doc(html)

	head = Tag("head")
	head(Tag("meta", attr=[("charset","utf-8")], single=True))
	html(head)

	body = Tag("body")
	html(body)

	fire = Tag("FireBoxRoom")
	assets = Tag("Assets")

	attr=[
		("gravity", f2s(scene.janus_room_gravity)),
		("walk_speed", f2s(scene.janus_room_walkspeed)),
		("run_speed", f2s(scene.janus_room_runspeed)),
		("jump_velocity", f2s(scene.janus_room_jump)),
		("near_dist", f2s(scene.janus_room_clipplane[0])),
		("far_dist", f2s(scene.janus_room_clipplane[1])),
		("teleport_min_dist", f2s(scene.janus_room_teleport[0])),
		("teleport_max_dist", f2s(scene.janus_room_teleport[1])),
		("default_sounds", b2s(scene.janus_room_defaultsounds)),
		("cursor_visible", b2s(scene.janus_room_cursorvisible)),
		("fog", b2s(scene.janus_room_fog)),
		("fog_mode", scene.janus_room_fog_mode),
		("fog_density", f2s(scene.janus_room_fog_density)),
		("fog_start", f2s(scene.janus_room_fog_start)),
		("fog_end", f2s(scene.janus_room_fog_end)),
		("fog_col", v2s(scene.janus_room_fog_col)),
		("locked", b2s(scene.janus_room_locked)),
		]

	if scene.janus_server_default!=True:
		attr += [
		("server",scene.janus_server),
		("port",scene.janus_server_port),
		]

	if scene.camera:
		attr += [
		("pos", p2s(scene.camera.location)),
		("fwd", r2sr(scene.camera.matrix_local)),
		]

	if scene.janus_room!="None":
		attr += [
		("use_local_asset",scene.janus_room),
		("visible",b2s(scene.janus_room_visible)),
		("col",v2s(scene.janus_room_color)),
		]

	if scene.janus_room_skybox_active:
		attr += [
		("skybox_left_id","sky_left"),
		("skybox_right_id","sky_right"),
		("skybox_front_id","sky_front"),
		("skybox_back_id","sky_back"),
		("skybox_up_id","sky_up"),
		("skybox_down_id","sky_down"),
		]

		sky_image = [(scene.janus_room_skybox_left,"sky_left"),(scene.janus_room_skybox_right,"sky_right"),(scene.janus_room_skybox_front,"sky_front"),(scene.janus_room_skybox_back,"sky_back"),(scene.janus_room_skybox_up,"sky_up"),(scene.janus_room_skybox_down,"sky_down")]

		for sky in sky_image:
			skyname = os.path.basename(sky[0])
			assetimage = Tag("AssetImage", attr=[("id",sky[1]), ("src",skyname)])
			if not assetimage in assets:
				assets(assetimage)
				shutil.copyfile(src=bpy.path.abspath(sky[0]), dst=os.path.join(filepath, skyname))

	if scene.janus_room_script_active:
		script_list = [scene.janus_room_script1,scene.janus_room_script2,scene.janus_room_script3,scene.janus_room_script4]
		for script_entry in script_list:
			if script_entry != "":
				scriptname = os.path.basename(script_entry)
				assetscript = Tag("AssetScript", attr=[("src",scriptname)])
				if not assetscript in assets:
					assets(assetscript)
					shutil.copyfile(src=bpy.path.abspath(script_entry), dst=os.path.join(filepath, scriptname))

	if scene.janus_room_shader_active:
		if scene.janus_room_shader_frag != "":
			fragname = os.path.basename(scene.janus_room_shader_frag)
		if scene.janus_room_shader_vert != "":
			vertname = os.path.basename(scene.janus_room_shader_vert)
		else:
			vertname = ""
		if fragname:
			attr += [("shader_id", fragname)]
		assetshader = Tag("AssetShader", attr=[("id",fragname),("src",fragname),("vertex_src",vertname)])
		if not assetshader in assets:
			assets(assetshader)
			if fragname:
				shutil.copyfile(src=bpy.path.abspath(scene.janus_room_shader_frag), dst=os.path.join(filepath, fragname))
			if vertname:
				shutil.copyfile(src=bpy.path.abspath(scene.janus_room_shader_vert), dst=os.path.join(filepath, vertname))

	room = Tag("Room", attr)

	useractive = scene.objects.active
	userselect = bpy.context.selected_objects[:]

	exportedmeshes = []
	exportedsurfaces = []

	if  scene.janus_unpack:
		bpy.ops.file.make_paths_relative()
		bpy.ops.file.unpack_all(method='USE_LOCAL')
		bpy.ops.file.make_paths_absolute()

	for o in bpy.data.objects:
		if o.type=="MESH":
			if o.janus_object_objtype == "JOT_OBJECT":
				# A mesh. If the user really wants us to, apply things to it.
				scene.objects.active = o
				for so in bpy.context.selected_objects:
					so.select = False
				o.select = True

				if scene.janus_apply_rot:
					try:
						with redirect_stdout(stdout):
							bpy.ops.object.transform_apply(rotation=True)
					except:
						pass
				if scene.janus_apply_scale:
					try:
						with redirect_stdout(stdout):
							bpy.ops.object.transform_apply(scale=True)
					except:
						pass
				if scene.janus_apply_pos:
					try:
						with redirect_stdout(stdout):
							bpy.ops.object.transform_apply(position=True)
					except:
						pass
				loc = o.location.copy()
				o.location = [0, 0, 0]

				oldrotmode = o.rotation_mode
				oldrotquat = o.rotation_quaternion.copy()
				oldroteu = o.rotation_euler.copy()
				oldrotax = [x for x in o.rotation_axis_angle]

				# note: scale may or may not actually be reverted, depends on what testing finds. It's 1:27 AM, so please don't bug me about it.
				# if NOT applying rotation/scale, then stop the exporters from doing annoying things like preserving rotation (which they do)
				# if applying rotation/scale, then the exporters can do whatever, since it's all meant to be baked into the file
				# it seems the local matrix disappears after this and doesn't come back when the parameters return, so grab it now
				rotmatrix = o.matrix_local.copy()
				if not scene.janus_apply_rot:
					o.rotation_mode = "QUATERNION"
					o.rotation_quaternion = Quaternion([1.0, 0.0, 0.0, 0.0])

				oldscale = o.scale.copy()
				if not scene.janus_apply_scale:
					o.scale = Vector([1, 1, 1])

				#bpy.ops.object.select_pattern(pattern=o.name, extend=False) # This apparently doesn't work on 2.78?
				# Things to hardcode in the name of accident prevention:
				# 1. Force export_scene.obj to use -Z Forward, Y Up, if it's currently using user defaults instead. [done]
				# 2. Figure out what's up with the COLLADA exporter (and force coordinate-related settings)

				if not o.data.name in exportedmeshes:
					epath = os.path.join(filepath, o.data.name+scene.janus_object_export)
					if scene.janus_object_export==".obj":
						with redirect_stdout(stdout):
							bpy.ops.export_scene.obj(filepath=epath, use_selection=True, use_smooth_groups_bitflags=True, use_uvs=True, use_materials=True, use_mesh_modifiers=True,use_triangles=True, check_existing=False, use_normals=True, path_mode="COPY", axis_forward='-Z', axis_up='Y')
					else:
						with redirect_stdout(stdout):
							bpy.ops.wm.collada_export(filepath=epath, selected=True, check_existing=False, include_uv_textures=True, include_material_textures=True)
							# TODO differentiate between per-object and per-mesh properties
					ob = Tag("AssetObject", attr=[("id", o.data.name), ("src",o.data.name+scene.janus_object_export), ("mtl",o.data.name+".mtl")])
					exportedmeshes.append(o.data.name)
					assets(ob)

				if not scene.janus_apply_rot:
					o.rotation_mode = oldrotmode
					o.rotation_axis_angle = oldrotax
					o.rotation_euler = oldroteu
					o.rotation_quaternion = oldrotquat

				if not scene.janus_apply_scale:
					o.scale = oldscale

				attr = [("id", o.data.name), ("locked", b2s(o.janus_object_locked)), ("cull_face", o.janus_object_cullface), ("visible", str(o.janus_object_visible).lower()),("col",v2s(o.janus_object_color) if o.janus_object_color_active else "1 1 1"), ("lighting", b2s(o.janus_object_lighting)),("collision_id", o.data.name if o.janus_object_collision else ""), ("pos", p2s(loc))]

				# The key is, *the model is already rotated, as far as I can tell, by the OBJ and Collada backends.*
				# Hence, the model has to be un-rotated first. That's why the dance above exists.
				if not scene.janus_apply_scale:
					attr += [("scale", lp2s(o.scale))]

				if not scene.janus_apply_rot:
					mtm(attr, rotmatrix)

				if o.janus_object_jsid:
					attr += [("js_id",o.janus_object_jsid)]

					if o.janus_object_websurface and o.janus_object_websurface_url:
						if not o.janus_object_websurface_url in exportedsurfaces:
								assets(Tag("AssetWebSurface", attr=[("id", o.janus_object_websurface_url), ("src", o.janus_object_websurface_url), ("width", o.janus_object_websurface_size[0]), ("height", o.janus_object_websurface_size[1])]))
								exportedsurfaces.append(o.janus_object_websurface_url)
						attr += [("websurface_id", o.janus_object_websurface_url)]

				if o.janus_object_shader_active:
					if o.janus_object_shader_frag != "":
						fragname = os.path.basename(o.janus_object_shader_frag)
					if o.janus_object_shader_vert != "":
						vertname = os.path.basename(o.janus_object_shader_vert)
					else:
						vertname = ""
					if fragname:
						assetshader = Tag("AssetShader", attr=[("id",fragname),("src",fragname),("vertex_src",vertname)])
						if not assetshader in assets:
								assets(assetshader)
								shutil.copyfile(src=bpy.path.abspath(o.janus_object_shader_frag), dst=os.path.join(filepath, fragname))
								if vertname != "":
									shutil.copyfile(src=bpy.path.abspath(o.janus_object_shader_vert), dst=os.path.join(filepath, vertname))
						attr += [("shader_id", fragname)]

				room(Tag("Object", single=False, attr=attr))
				o.location = loc
			elif o.janus_object_objtype == "JOT_LINK":
				# Link is a separate object type now, allowing plane placeholders to allow some semblance of visual editing.
				# portalaccounting deals with the fact Janus portals are centred at their bottom middle, not the centre like a plane placeholder
				portalaccounting = (o.matrix_local.normalized() * Vector([0.0, -o.scale.y, -0.1, 0.0])).xyz
				# leave an Empty marker for debug?
				# for now just ruin state
				# Scaling:
				# ideal input is 1.58, 1.77
				# ideal output is 3.06, 3.35, 1 approx???
				# note; actual ratios used are post-portal position adjustments.
				#
				attr = [("pos",p2s(o.location+portalaccounting)), ("url",o.janus_object_link_url), ("title",o.janus_object_link_name), ("col", v2s(o.color[:3]))]
				attr += [("scale",v2s(Vector([o.scale.x * 1.93, o.scale.y * 2.00, 1.0])))]
				mt2(attr, o.matrix_local)
				if o.janus_object_jsid:
					attr += [("js_id",o.janus_object_jsid)]
				if not o.janus_object_active:
					attr += [("active","false")]
				room(Tag("Link", attr=attr))

		elif o.type=="FONT":

			if o.data.body.startswith("http://") or o.data.body.startswith("https://"):
				# kept to make commit-splitting easier
				room(Tag("Link", attr=[("pos",p2s(o.location)), ("scale","1.8 3.2 1"), ("url",o.data.body), ("title",o.name), ("col", v2s(o.color[:3]))]))
			else:
				texttype = "Text" if o.data.body.find("\n")==-1 else "Paragraph"
				attr = [("pos",p2s(o.location)), ("scale","1.8 3.2 1"), ("title",o.name)]
				#attr += [("fwd", r2s(o.matrix_local))] # in case of emergency. Note that r2s is the wrong way around. Good luck!
				mt2(attr, o.matrix_local)
				text = Tag(texttype, attr=attr)
				text.sub.append(o.data.body)
				room(text)

		elif o.type=="SPEAKER":

			if o.janus_object_sound:
				name = os.path.basename(o.janus_object_sound)
				assetsound = Tag("AssetSound", attr=[("id", name), ("src",name)])
				if not assetsound in assets:
					assets(assetsound)
					shutil.copyfile(src=bpy.path.abspath(o.janus_object_sound), dst=os.path.join(filepath, name))
				sound = Tag("Sound", attr=[("id", name), ("js_id", o.janus_object_jsid), ("pos", p2s(o.location)), ("dist", f2s(o.janus_object_sound_dist)), ("rect", v2s(list(o.janus_object_sound_xy1)+list(o.janus_object_sound_xy2))), ("loop", b2s(o.janus_object_sound_loop)), ("play_once", b2s(o.janus_object_sound_once))])
				room(sound)

	for so in bpy.context.selected_objects:
		so.select = False
	for so in userselect:
		so.select = True
	scene.objects.active = useractive

	fire(assets)
	fire(room)
	body(fire)
	file = open(os.path.join(filepath,"index.html"), mode="w", encoding="utf8", newline="\n")
	fw = file.write
	doc.write(fw, indent="")
	file.close()

def save(operator, context, filepath="", path_mode="AUTO", relpath=""):
	write_html(context.scene, filepath, path_mode)
