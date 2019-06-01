import bpy, bmesh, math
from mathutils import Vector, Matrix
from collections import OrderedDict
from . import utils as ut

ERR_MSG_WRONG_OBJECT = "Selected object not suited for this application"
ERR_MSG_WRONG_LAYER = "Selected object not in active layer"
ERR_MSG_NO_OBJECT_SELECTED = "No object selected"
ERR_MSG_NO_ACTIVE_OBJECT_SELECTED = "No active object selected"
ERR_MSG_OBJECT_NOT_FOUND = "Object not found"

PREF = "_"
PART = "_PART"
TEMP = "_TEMP"
BASE = "_BASE"
SECT = "_SECT"
LOD = "_LOD"
PHYS = "_PHYS"
NUMB = ".000"
BOUNDS = "_BOUNDS"
PROP = "BGE_TOOLS_LOD_SECTIONS"
SCRIPT = "bge_tools_lod_sections"

class LODSections(bpy.types.Operator):
	
	bl_description = "Generates sections with level of detail"
	bl_idname = "bge_tools.lod_sections"
	bl_label = "BGE-Tools: LOD Sections"
	bl_options = {"REGISTER", "UNDO", "PRESET"}
	
	prop_update_or_clear = bpy.props.EnumProperty(
		items=[
			("update", "Update", ""),
			("clear", "Clear", "")
		],
		name="",
		description="Update or clear",
		default="clear"
	)
	prop_number_or_size = bpy.props.EnumProperty(
		items=[
			("generate_by_number", "Generate by number", ""),
			("generate_by_size", "Generate by size", "")
		],
		name="",
		description="Generate by number or size",
		default="generate_by_number"
	)
	prop_number = bpy.props.IntVectorProperty(
		name="",
		description="Number of sections",
		default=(8, 8),
		min=1,
		max=64,
		size=2
	)
	prop_size = bpy.props.FloatVectorProperty(
		name="",
		description="Section size",
		default=(64, 64),
		soft_min=8,
		soft_max=512,
		size=2
	)
	prop_number_mode = bpy.props.EnumProperty(
		items=[
			("use_automatic_numbering", "Use Automatic Numbering", ""),
			("use_even_numbers", "Use Even Numbers", ""),
			("use_odd_numbers", "Use Odd Numbers", "")
		],
		name="",
		description="Mode for numbering",
		default="use_even_numbers"
	)
	prop_use_decimate_dissolve = bpy.props.BoolProperty(
		name="Decimate Dissolve",
		description="Apply planar decimation",
		default=False
	)
	prop_decimate_dissolve_angle_limit = bpy.props.FloatProperty(
		name="",
		description="Decimate Dissolve angle limit",
		default=math.radians(1),
		min=0,
		max=math.pi,
		subtype="ANGLE"
	)
	prop_use_lod = bpy.props.BoolProperty(
		name="Level of detail",
		description="Use level of detail",
		default=True
	)
	prop_lod_number = bpy.props.IntProperty(
		name="",
		description="Number of levels to be added",
		default=3,
		min=1,
		max=8
	)
	prop_lod_factor = bpy.props.FloatProperty(
		name="",
		description="Additive Decimate Collapse factor",
		default=0.5,
		min=0,
		max=1,
		subtype="FACTOR"
	)
	prop_lod_use_distance = bpy.props.BoolProperty(
		name="Distance",
		description="Use custom distance",
		default=False
	)
	prop_lod_distance = bpy.props.FloatProperty(
		name="",
		description="Additive distance of lod levels",
		default=100,
		soft_min=12.5,
		soft_max=800,
		subtype="DISTANCE"
	)
	prop_lod_use_physics = bpy.props.BoolProperty(
		name="Physics",
		description="Use physics",
		default=True
	)
	prop_use_approx = bpy.props.BoolProperty(
		name="Approximate",
		description="Use approximation",
		default=True
	)
	prop_approx_num_digits = bpy.props.IntProperty(
		name="",
		description="Maximum number of digits used with coordinates",
		default=2,
		min=0,
		max=15
	)
	prop_use_custom_prefix = bpy.props.BoolProperty(
		name="Prefix",
		description="Use custom prefix",
		default=False
	)
	prop_custom_prefix = bpy.props.StringProperty(
		name="",
		description="Custom prefix",
		default=PREF
	)
	
	err_msg = ""
	log_msg = ""
	
	def invoke(self, context, event):
		
		if context.object in context.selected_editable_objects:
			if isinstance(context.object.data, bpy.types.Mesh):
				self.scene = context.scene
				self.object = context.object
			else:
				self.err_msg = ERR_MSG_WRONG_OBJECT
		elif context.selected_editable_objects:
			self.err_msg = ERR_MSG_NO_ACTIVE_OBJECT_SELECTED
		elif context.selected_objects:
			self.err_msg = ERR_MSG_WRONG_LAYER
		else:
			self.err_msg = ERR_MSG_NO_OBJECT_SELECTED
			
		system_dpi = bpy.context.user_preferences.system.dpi
		
		return context.window_manager.invoke_props_dialog(self, width=system_dpi*5)
		
	def draw(self, context):
		
		layout = self.layout
		box = layout.box
		row = box().row
		
		if self.log_msg:
			row().label(self.log_msg, icon="INFO")
			return
			
		if self.err_msg:
			row().label(self.err_msg, icon="CANCEL")
			return
			
		if PROP in self.object.game.properties:
			row().prop(self, "prop_update_or_clear")
			return
			
		s = bpy.types.WM_MT_operator_presets
		print(s)
			
		row().prop(self, "prop_number_or_size")
		
		col = row().column
		col_numb = col()
		col_numb.prop(self, "prop_number")
		col_size = col()
		col_size.prop(self, "prop_size")
		col_size.prop(self, "prop_number_mode")
		
		if self.prop_number_or_size == "generate_by_number":
			col_size.active = False
		else:
			col_numb.active = False
			
		col = row().column
		col().prop(self, "prop_use_decimate_dissolve")
		col_deci = col()
		col_deci.prop(self, "prop_decimate_dissolve_angle_limit")
		if not self.prop_use_decimate_dissolve:
			col_deci.active = False
			
		col = row().column
		col().prop(self, "prop_use_lod")
		col_lod = col()
		col_lod.prop(self, "prop_lod_number")

		row_lod = row()
		col = row_lod.column
		col().prop(self, "prop_lod_use_physics", toggle=True)
		col().prop(self, "prop_lod_factor")
		
		row_dist = row()
		col = row_dist.column
		col().prop(self, "prop_lod_use_distance", toggle=True)
		col_dist = col()
		col_dist.prop(self, "prop_lod_distance")
		if not self.prop_lod_use_distance:
			col_dist.active = False
			
		if not self.prop_use_lod:
			col_lod.active = False
			row_dist.active = False
			row_lod.active = False
			
		col = row().column
		col().prop(self, "prop_use_approx")
		col_ndig = col()
		col_ndig.prop(self, "prop_approx_num_digits")
		if not self.prop_use_approx:
			col_ndig.active = False
			
		col = row().column
		col().prop(self, "prop_use_custom_prefix")
		col_pref = col()
		col_pref.prop(self, "prop_custom_prefix")
		if not self.prop_use_custom_prefix:
			col_pref.active = False
			
	def check(self, context):
		
		if self.err_msg:
			return False
		return True
		
	def execute(self, context):
		
		if self.err_msg:
			return {"CANCELLED"}
			
		self.prefix = self.prop_custom_prefix if self.prop_use_custom_prefix else PREF
		
		if PROP in self.object.game.properties:
			sections_name = self.object.game.properties[PROP].value
			
			try:
				sections = self.scene.objects[sections_name]
				
				for i, prop in enumerate(self.object.game.properties):
					if prop.name == PROP:
						bpy.ops.object.game_property_remove(i)
						
				ut.remove_logic_python(self.object, SCRIPT)
				ut.remove_text(SCRIPT)
				
				meshes = set()
				for ob in sections.children:
					meshes.add(ob.data)
					ut.remove(ob, False)
				materials = set()
				for me in meshes:
					for mat in me.materials:
						if not mat.name.startswith(self.prefix):
							continue
						materials.add(mat)
					ut.remove(me)
				for mat in materials:
					ut.remove(mat)
				ut.remove(sections, False)
				
				if self.prop_update_or_clear == "clear":
					
					return {"FINISHED"}
					
			except KeyError:
				self.err_msg = ERR_MSG_OBJECT_NOT_FOUND + ": " + sections_name
				
				return {"CANCELLED"}
				
		print("\nLOD Sections\n------------\n")
		
		def store_initial_state():
			
			bpy.ops.object.mode_set(mode="OBJECT")
			
			self.undo = context.user_preferences.edit.use_global_undo
			context.user_preferences.edit.use_global_undo = False
			
			self.cursor_location = self.scene.cursor_location.copy()
			self.scene.cursor_location = Vector()
			
			self.hide_render = self.object.hide_render
			self.hide = self.object.hide
			
		def collect_data():
			
			self.prof = ut.Profiler()
			
			print(self.prof.timed("Collecting data"))
			
			self.number = Vector()
			self.size = Vector()
			
			dimensions = ut.dimensions(self.object).xy
			
			if self.prop_number_or_size == "generate_by_number":
				self.number.x = self.prop_number[0]
				self.number.y = self.prop_number[1]
				self.size.x = dimensions.x / self.number.x
				self.size.y = dimensions.y / self.number.y
			else:
				self.size.x = self.prop_size[0]
				self.size.y = self.prop_size[1]
				n_x = math.ceil(dimensions.x / self.size.x)
				n_y = math.ceil(dimensions.y / self.size.y)
				
				numb_mode = self.prop_number_mode
				if numb_mode == "use_automatic_numbering":
					self.number.x = n_x
					self.number.y = n_y
				else:
					i = 0 if numb_mode == "use_even_numbers" else 1
					self.number.x = n_x + 1 - i if n_x % 2 else n_x + i
					self.number.y = n_y + 1 - i if n_y % 2 else n_y + i
					
			self.ndigits = len(str(int(self.number.x * self.number.y)))
			self.points = OrderedDict()
			
			n = 1
			for j in range(int(self.number.y)):
				y = 0.5 * self.size.y * (2 * j + 1 - self.number.y)
				for i in range(int(self.number.x)):
					x = 0.5 * self.size.x * (2 * i + 1 - self.number.x)
					id = ut.get_id(n, "", self.ndigits)
					self.points[id] = Vector((x, y, 0))
					n += 1
					
			self.particles = {}
			self.data = {}
			
			bpy.ops.object.empty_add()
			self.sections = self.scene.objects.active
			self.sections.name = self.prefix + self.object.name
			self.sections.select = False
			
		def create_base():
			
			print(self.prof.timed("Creating base"))
			
			self.scene.objects.active = self.object
			self.object.select = True
			bpy.ops.object.duplicate()
			self.object.select = False
			
			self.base = self.scene.objects.active
			self.base.data.name = self.base.name = self.sections.name + BASE
			
			self.base.game.physics_type = "NO_COLLISION"
			self.materials = set(self.base.data.materials)
			
			for mod in self.base.modifiers:
				
				if mod.type == "PARTICLE_SYSTEM":
					bpy.ops.object.modifier_remove(modifier=mod.name)
					continue
					
				print(self.prof.timed("Applying ", mod.name))
				
				bpy.ops.object.modifier_apply(apply_as="DATA", modifier=mod.name)
				
			for vertex_group in list(self.base.vertex_groups):
				self.base.vertex_groups.remove(vertex_group)
				
			bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
			bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
			self.transform = self.base.matrix_world.copy()
			self.base.matrix_world = Matrix()
			
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all()
			bpy.ops.mesh.quads_convert_to_tris()
			bpy.ops.mesh.select_all(action="DESELECT")
			bpy.ops.object.editmode_toggle()
			
		def dissolve():
			
			if not self.prop_use_decimate_dissolve:
				return
				
			print(self.prof.timed("Applying Decimate Dissolve"))
			
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all()
			
			bpy.ops.mesh.dissolve_limited(angle_limit=self.prop_decimate_dissolve_angle_limit, use_dissolve_boundaries=False, delimit={"NORMAL", "MATERIAL", "SEAM", "SHARP", "UV"})
			
			bpy.ops.mesh.quads_convert_to_tris()
			bpy.ops.mesh.beautify_fill()
			
			bpy.ops.mesh.select_all(action="DESELECT")
			bpy.ops.object.editmode_toggle()
			
		def generate_sections():
			
			print(self.prof.timed("Multisecting base"))
			
			self.scene.objects.active = tmps = ut.copy(self.scene, self.base)
			tmps.select = True
			self.base.select = False
			
			tmps.data.name = tmps.name = self.sections.name + TEMP + NUMB
			tmps.vertex_groups.new(BOUNDS)
			tmps.show_all_edges = True
			tmps.show_wire = True
			tmps.game.physics_type = "NO_COLLISION"
			
			bpy.ops.object.editmode_toggle()
			
			bm = bmesh.from_edit_mesh(tmps.data)
			
			for i in range(int(self.number.x) + 1):
				try:
					l = bm.verts[:] + bm.edges[:] + bm.faces[:]
					co = ((i - 0.5 * self.number.x) * self.size.x, 0, 0)
					no = (1, 0, 0)
					d = bmesh.ops.bisect_plane(bm, geom=l, plane_co=co, plane_no=no)
					bmesh.ops.split_edges(bm, edges=[e for e in d["geom_cut"] if isinstance(e, bmesh.types.BMEdge)])
				except RuntimeError:
					continue
					
			for i in range(int(self.number.y) + 1):
				try:
					l = bm.verts[:] + bm.edges[:] + bm.faces[:]
					co = (0, (i - 0.5 * self.number.y) * self.size.y, 0)
					no = (0, 1, 0)
					d = bmesh.ops.bisect_plane(bm, geom=l, plane_co=co, plane_no=no)
					bmesh.ops.split_edges(bm, edges=[e for e in d["geom_cut"] if isinstance(e, bmesh.types.BMEdge)])
				except RuntimeError:
					continue
					
			bmesh.update_edit_mesh(tmps.data)
			
			bpy.ops.object.editmode_toggle()
			
			bm.free()
			del bm
			
			print(self.prof.timed("Separating into sections"))
			
			bpy.ops.mesh.separate(type="LOOSE")
			tmps = context.selected_objects
			bpy.ops.object.select_all(action="DESELECT")
			
			print(self.prof.timed("Organizing sections"))
			
			for tmp in tmps:
				self.scene.objects.active = tmp
				tmp.select = True
				
				bpy.ops.object.editmode_toggle()
				bpy.ops.mesh.select_all()
				bpy.ops.mesh.remove_doubles()
				bpy.ops.mesh.quads_convert_to_tris()
				bpy.ops.mesh.beautify_fill()
				bpy.ops.mesh.region_to_loop()
				bpy.ops.object.vertex_group_assign()
				bpy.ops.mesh.select_all(action="DESELECT")
				bpy.ops.object.editmode_toggle()
				
				bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
				
				inside = False
				for id, v in self.points.items():
					if ut.point_inside_rectangle(tmp.location, (v, self.size * 0.99)):
						tmp.data.name = tmp.name = self.sections.name + SECT + id
						self.scene.cursor_location = v
						bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
						self.data[id] = tmp
						tmp.parent = self.sections
						tmp.select = False
						inside = True
						break
						
				if not inside:
					ut.remove(tmp)
					
			self.scene.cursor_location = Vector()
			
		def generate_lod():
			
			if not self.prop_use_lod:
				return
				
			lod = {id: [sect] for id, sect in self.data.items()}
			id = ut.get_id(0, "", self.ndigits)
			lod_id = ut.get_id(self.prop_lod_number, "_", 1)
			me_name = self.sections.name + SECT + id + LOD + lod_id
			sect_lod_me_linked = bpy.data.meshes.new(me_name)
			
			for i in range(1, self.prop_lod_number + 1):
				
				print(self.prof.timed("Generating LOD ", i, " of ", self.prop_lod_number))
				
				lod_id = ut.get_id(i, "_", 1)
				
				for id, sect in self.data.items():
					sect_lod_name = sect.name + LOD + lod_id
					sect_lod_me_name = sect.data.name + LOD + lod_id
					
					if i == self.prop_lod_number:
						sect_lod = bpy.data.objects.new(sect_lod_name, sect_lod_me_linked)
						sect_lod.game.physics_type = "NO_COLLISION"
						self.scene.objects.link(sect_lod)
					else:
						self.scene.objects.active = sect
						sect.select = True
						bpy.ops.object.duplicate()
						sect.select = False
						
						sect_lod = self.scene.objects.active
						sect_lod.name = sect_lod_name
						sect_lod.data.name = sect_lod_me_name
						
						mod_decimate_collapse = sect_lod.modifiers.new("Decimate Collapse", "DECIMATE")
						mod_decimate_collapse.decimate_type = "COLLAPSE"
						mod_decimate_collapse.ratio = self.prop_lod_factor / i
						mod_decimate_collapse.vertex_group = BOUNDS
						mod_decimate_collapse.invert_vertex_group = True
						#mod_decimate_collapse.use_collapse_triangulate = True
						bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Decimate Collapse")
						
					sect_lod.location = sect.location
					sect_lod.select = False
					sect_lod.parent = self.sections
					
					lod[id].append(sect_lod)
					
			print(self.prof.timed("Configuring LOD"))
			
			if self.prop_lod_use_distance:
				lod_dist = self.prop_lod_distance
			else:
				lod_dist = round(math.pi * math.sqrt(self.size.x * self.size.y) * 0.5)
				
			for id, l in lod.items():
				sect = self.data[id]
				self.scene.objects.active = sect
				sect.select = True
				for i, sect_lod in enumerate(l):
					bpy.ops.object.lod_add()
					lod_level = sect.lod_levels[i + 1]
					lod_level.distance = lod_dist * i
					lod_level.use_material = True
					lod_level.object = sect_lod
				sect.select = False
				
		def convert_particles():
			
			particles = {}
			
			for mod in self.object.modifiers:
				if mod.type == "PARTICLE_SYSTEM":
					
					if not mod.show_viewport:
						continue
						
					settings = mod.particle_system.settings
					
					if not settings.dupli_object:
						continue
						
					print(self.prof.timed("Converting ", mod.name))
					
					self.materials.update(settings.dupli_object.data.materials)
					
					self.scene.objects.active = self.object
					self.object.select = True
					bpy.ops.object.duplicates_make_real()
					self.object.select = False
					bpy.ops.object.make_single_user(type="SELECTED_OBJECTS", obdata=True)
					
					transform_inverted = self.transform.inverted()
					for ob in context.selected_objects:
						ob.matrix_world = transform_inverted * ob.matrix_world
						
						inside = False
						for id, v in self.points.items():
							if ut.point_inside_rectangle(ob.location, (v, self.size)):
								if id not in particles:
									particles[id] = []
								particles[id].append(ob)
								inside = True
								break
								
						if not inside:
							ut.remove(ob)
							
					bpy.ops.object.select_all(action="DESELECT")
					mod.show_viewport = True
					
			for id, objects in particles.items():
				self.particles[id] = p = objects[0]
				p.data.name = p.name = self.sections.name + PART + id
				
				if not objects:
					continue
					
				if len(objects) > 1:
					self.scene.objects.active = p
					meshes = []
					for ob in objects:
						ob.select = True
						if ob == p:
							continue
						meshes.append(ob.data)
					bpy.ops.object.join()
					p.select = False
					for me in meshes:
						ut.remove(me)
						
		def join_particles():
			
			if not self.particles:
				return
				
			for id, sect in self.data.items():
				
				if id not in self.particles:
					continue
					
				v = self.points[id]
				part = self.particles[id]
				part_me = part.data
				
				if self.prop_use_lod:
					
					lod = [ll.object for ll in sect.lod_levels[2:-1]]
					
					for i, sect_lod in enumerate(lod):
						
						self.scene.objects.active = part
						part.select = True
						bpy.ops.object.duplicate()
						part.select = False
						part_lod = self.scene.objects.active
						part_lod_me = part_lod.data
						
						mod_decimate_collapse = part_lod.modifiers.new("Decimate Collapse", "DECIMATE")
						mod_decimate_collapse.decimate_type = "COLLAPSE"
						mod_decimate_collapse.ratio = self.prop_lod_factor / (i + 1)
						mod_decimate_collapse.use_collapse_triangulate = True
						bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Decimate Collapse")
						
						self.scene.objects.active = sect_lod
						sect_lod.select = True
						bpy.ops.object.join()
						self.scene.cursor_location = v
						bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
						sect_lod.select = False
						
						ut.remove(part_lod_me)
						
				self.scene.objects.active = sect
				sect.select = True
				part.select = True
				bpy.ops.object.join()
				self.scene.cursor_location = v
				bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
				sect.select = False
				
				ut.remove(part_me)
				
		def copy_normals():
			
			objects = []
			for sect in self.data.values():
				objects.append(sect)
				if not self.prop_use_lod:
					continue
				for lod_level in sect.lod_levels[2:-1]:
					objects.append(lod_level.object)
					
			for ob in objects:
				self.scene.objects.active = ob
				ob.select = True
				
				ob.data.use_auto_smooth = True
				ob.data.create_normals_split()
				
				mod_copy_cust_norm = ob.modifiers.new(name="Copy Custom Normals", type="DATA_TRANSFER")
				mod_copy_cust_norm.object = self.base
				mod_copy_cust_norm.use_loop_data = True
				mod_copy_cust_norm.data_types_loops = {"CUSTOM_NORMAL"}
				mod_copy_cust_norm.vertex_group = BOUNDS
				
				bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Copy Custom Normals")
				
				ob.select = False
				
			ut.remove(self.base)
			
		def generate_lod_materials():
			
			if not self.prop_use_lod:
				return
				
			print(self.prof.timed("Generating lod materials"))
			
			materials_lod = {}
			
			for mat in self.materials:
				mat_lod = mat.copy()
				mat_lod.name = self.prefix + mat.name
				materials_lod[mat.name] = mat_lod
				
				mat_lod.game_settings.physics = False
				mat_lod.use_cast_shadows = False
				mat_lod.use_shadows = False
				
				mat.game_settings.physics = True
				mat.use_cast_shadows = True
				mat.use_shadows = True
				
			for sect in self.data.values():
				for lod_level in sect.lod_levels[2:-1]:
					sect_lod = lod_level.object
					for i, mat in enumerate(sect_lod.data.materials):
						sect_lod.active_material_index = i
						sect_lod.active_material = materials_lod[mat.name]
						
		def export_normals():
			
			print(self.prof.timed("Exporting custom normals"))
			
			objects = []
			for sect in self.data.values():
				objects.append(sect)
				if not self.prop_use_lod:
					continue
				for lod_level in sect.lod_levels[2:-1]:
					objects.append(lod_level.object)
					
			approx_ndigits = self.prop_approx_num_digits if self.prop_use_approx else -1
			
			custom_normals = {}
			
			for ob in objects:
				self.scene.objects.active = ob
				ob.select = True
				
				bpy.ops.object.editmode_toggle()
				bpy.ops.mesh.select_all(action="DESELECT")
				bpy.ops.object.vertex_group_select()
				bpy.ops.object.editmode_toggle()
				
				custom_normals[ob.name] = ut.get_custom_normals(ob, approx_ndigits, True)
				
				bpy.ops.object.editmode_toggle()
				bpy.ops.mesh.select_all(action="DESELECT")
				bpy.ops.object.editmode_toggle()
				
				ob.vertex_groups.remove(ob.vertex_groups.get(BOUNDS))
				
				ob.select = False
					
			ut.save_txt(custom_normals, PROP, self.object.name)
			
		def generate_physics():
			
			if not (self.prop_use_lod and self.prop_lod_use_physics):
				return
				
			print(self.prof.timed("Generating Physics"))
			
			for sect in self.data.values():
				sect_physics = ut.copy(self.scene, sect, True)
				sect_physics.name = sect.name + PHYS
				
				sect_physics.game.physics_type = "STATIC"
				sect_physics.game.use_collision_bounds = True
				sect_physics.game.collision_bounds_type = "TRIANGLE_MESH"
				sect_physics.select = False
				
				sect_physics.parent = self.sections
				
		def finalize():
			
			print(self.prof.timed("Finalizing sections"))
			
			layer_twenty = [False for i in range(19)] + [True]
			
			sections = self.data.values()
			for ob in self.sections.children:
				ob.layers = layer_twenty
				if ob not in sections:
					ob.hide_render = True
					ob.hide = True
					
			self.sections.layers = layer_twenty
			self.sections.hide_render = True
			self.sections.hide = True
			
		def generate_game_logic():
			
			print(self.prof.timed("Generating game logic"))
			
			self.scene.objects.active = self.object
			self.object.select = True
			
			if PROP not in self.object:
				bpy.ops.object.game_property_new(type="STRING", name=PROP)
			else:
				self.object[PROP].type = "STRING"
			self.object.game.properties[PROP].value = self.sections.name
			
			ut.add_text(self.bl_idname, True, SCRIPT)
			ut.add_logic_python(self.object, SCRIPT, "update", True)
			
		def restore_initial_state():
			
			print(self.prof.timed("Restoring initial state"))
			
			self.object.hide_render = self.hide_render
			self.object.hide = self.hide
			
			self.scene.cursor_location = self.cursor_location
			
			context.user_preferences.edit.use_global_undo = self.undo
			
		def log():
			
			self.log_msg = self.prof.timed("Finished generating ", len(self.data), " (", round(self.size.x, 1), " X ", round(self.size.y, 1), ") sections in")
			
			print(self.log_msg)
			
		store_initial_state()
		collect_data()
		create_base()
		dissolve()
		generate_sections()
		generate_lod()
		convert_particles()
		join_particles()
		copy_normals()
		generate_lod_materials()
		export_normals()
		generate_physics()
		finalize()
		generate_game_logic()
		restore_initial_state()
		log()
		
		return {"FINISHED"}
		
def register():
	bpy.utils.register_class(LODSections)
	
def unregister():
	bpy.utils.unregister_class(LODSections)
	
if __name__ == "__main__":
	register()
	