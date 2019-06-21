import bpy, os, time, numpy, pickle
from mathutils import Vector
from collections import OrderedDict

# path constants

ADDONS_PATHS = bpy.utils.script_paths("addons")
GEN_PATH = os.path.join("bge-tools", "gen")
BGE_TOOLS_OT = "BGE_TOOLS_OT_"

# profiling utils

class Profiler:
	
	def __init__(self):
		self.start = time.clock()
		
	def time(self):
		return round(time.clock() - self.start, 1)
		
	def timed(self, *args):
		s = ""
		for arg in args:
			s += str(arg)
		for i in range(60 - len(s)):
			s += "."
		s += str(self.time()) + " s"
		return s
		
# string utils

def get_id(o, suffix=".", num_digits=4):
	if not isinstance(o, (list, Vector)):
		if isinstance(o, (int, float)):
			s = suffix
			d = str(o)
			for i in range(num_digits - len(d)):
				s += "0"
			s += d
			return s
		raise ValueError(o.__class__.__name__, "not suited for this application")
		
	f = 10 ** num_digits
	s = str(int(f * round(o[0], num_digits)))
	s += suffix + str(int(f * round(o[1], num_digits)))
	try:
		s += suffix + str(int(f * round(o[2], num_digits)))
	except KeyError:
		pass
		
	return s
	
# math utils

def get_sign(f):
	return numpy.sign(int(f))
	
def point_inside_rectangle(pnt, rect):
	cen, dim = rect
	crn = Vector((cen.x - dim.x * 0.5, cen.y - dim.y * 0.5))
	return (crn.x <= pnt.x <= crn.x + dim.x and crn.y <= pnt.y <= crn.y + dim.y)
	
# text utils

def add_text(name, intern=True, new_name="", ext=".py"):
	text_name = name + ext
	if text_name not in bpy.data.texts:
		text_path = os.path.join(ADDONS_PATHS[0], GEN_PATH, text_name)
		if bpy.ops.text.open(filepath=text_path, internal=intern) != {"FINISHED"}:
			text_path = os.path.join(ADDONS_PATHS[1], GEN_PATH, text_name)
			bpy.ops.text.open(filepath=text_path, internal=intern)
			if intern:
				text = bpy.data.texts[text_name]
				s = text.as_string()
				bpy.data.texts.remove(text, do_unlink=True)
				if new_name:
					text_name = new_name + ext
				text = bpy.data.texts.new(text_name)
				text.from_string(s)
				
	return bpy.data.texts[text_name]
	
def remove_text(name, all_users=False, ext=".py"):
	text_name = name + ext
	if text_name not in bpy.data.texts:
		return False
	text = bpy.data.texts[text_name]
	if not all_users and text.users_logic:
		return False
	bpy.data.texts.remove(bpy.data.texts[text_name], do_unlink=True)
	return True
	
# object utils

def add_logic_python(ob, script_name, module_name="", use_pulse_true_level=False):
	if script_name not in ob.game.sensors:
		bpy.ops.logic.sensor_add(type="ALWAYS", name=script_name, object=ob.name)
		
	if script_name not in ob.game.controllers:
		bpy.ops.logic.controller_add(type="PYTHON", name=script_name, object=ob.name)
		
	sens = ob.game.sensors[script_name]
	sens.use_pulse_true_level = use_pulse_true_level
	
	cont = ob.game.controllers[script_name]
	text = bpy.data.texts[script_name + ".py"]
	if module_name:
		text.use_module = True
		cont.mode = "MODULE"
		cont.module = script_name + "." + module_name
	else:
		cont.mode = "SCRIPT"
		cont.text = text
	cont.link(sensor=sens)
	
def remove_logic_python(ob, brick_name):
	for sens in ob.game.sensors:
		if sens.name == brick_name:
			bpy.ops.logic.sensor_remove(sensor=brick_name, object=ob.name)
	for cont in ob.game.controllers:
		if cont.name == brick_name:
			bpy.ops.logic.controller_remove(controller=brick_name, object=ob.name)
	for actu in ob.game.actuators:
		if actu.name == brick_name:
			bpy.ops.logic.controller_remove(actuator=brick_name, object=ob.name)
			
def copy(sc, ob, link=False, suffix="", apply_modifiers=False, modifier_settings="RENDER"):
	if link:
		ob_copy = bpy.data.objects.new(ob.name + suffix, ob.data)
	else:
		me_copy = ob.to_mesh(sc, apply_modifiers, modifier_settings)
		me_copy.name = ob.data.name + suffix
		ob_copy = bpy.data.objects.new(ob.name + suffix, me_copy)
	ob_copy.matrix_world = ob.matrix_world
	sc.objects.link(ob_copy)
	return ob_copy
	
def remove(o, remove_mesh=True):
	if isinstance(o, bpy.types.Material):
		bpy.data.materials.remove(o)
	elif isinstance(o, bpy.types.Mesh):
		bpy.data.meshes.remove(o)
	elif isinstance(o, bpy.types.Object):
		if remove_mesh:
			me = o.data
			bpy.data.objects.remove(o)
			bpy.data.meshes.remove(me)
		else:
			bpy.data.objects.remove(o)
	else:
		del o
		
def dimensions(*objects, include_transform=False):
	bb_crns = []
	for ob in objects:
		if include_transform:
			bb_crns += [ob.matrix_world * Vector(corner) for corner in ob.bound_box]
		else:
			bb_crns += [Vector(corner) for corner in ob.bound_box]
	n = len(bb_crns)
	dim_x = max(bb_crns[i][0] for i in range(n)) - min(bb_crns[i][0] for i in range(n))
	dim_y = max(bb_crns[i][1] for i in range(n)) - min(bb_crns[i][1] for i in range(n))
	dim_z = max(bb_crns[i][2] for i in range(n)) - min(bb_crns[i][2] for i in range(n))
	return Vector((dim_x, dim_y, dim_z))
	
def get_custom_normals(ob, approx_ndigits=-1, from_selected=False):
	
	def triform(loop_indices):
		indices = list(loop_indices)
		if len(indices) < 4:
			return indices
		return [indices[i] for i in (0, 1, 2, 2, 3, 0)]
		
	mesh = ob.data
	mesh.calc_normals_split()
	
	clnors = [0.0] * 3 * len(mesh.loops)
	mesh.loops.foreach_get("normal", clnors)
	loop_vert = {l.index: l.vertex_index for l in mesh.loops}
	
	normals = {}
	
	for poly in mesh.polygons:
		
		for li in triform(poly.loop_indices):
			vert = mesh.vertices[loop_vert[li]]
			
			if from_selected and not vert.select:
				continue
				
			vert_normal = [clnors[li*3], clnors[li*3+1], clnors[li*3+2]]
			if approx_ndigits != -1:
				vert_normal = [round(f, approx_ndigits) for f in vert_normal]
				
			id = str([round(f) for f in vert.co.xy])
			normals[id] = vert_normal
			
	return normals
	
# file utils

def load_txt(*args):
	data = OrderedDict()
	dir = os.path.join(bpy.path.abspath("//"), *args[:-1])
	if not os.path.exists(dir):
		os.mkdir(dir)
	file_path = os.path.join(dir, args[-1] + ".txt")
	with open(file_path, "rb") as f:
		return pickle.load(f)
		
def save_txt(data, *args):
	dir = os.path.join(bpy.path.abspath("//"), *args[:-1])
	if not os.path.exists(dir):
		os.mkdir(dir)
	file_path = os.path.join(dir, args[-1] + ".txt")
	with open(file_path, "wb") as f:
		pickle.dump(data, f)
		