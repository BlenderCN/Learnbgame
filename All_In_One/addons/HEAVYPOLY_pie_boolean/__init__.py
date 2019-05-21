bl_info = {
	"name": "HP Boolean Pie",
	"description": "",
	"author": "Vaughan Ling // Rombout Versluijs",
	"version": (0, 1, 5 ),
	"blender": (2, 79, 0),
	"location": "",
	"warning": "",
	"wiki_url": "https://github.com/schroef/HeavyPoly-Pie-Boolean/",
	"tracker_url": "https://github.com/schroef/HeavyPoly-Pie-Boolean/issues",
	"category": "Pie Menu"
	}
import bpy
import os
import rna_keymap_ui
from bpy.types import Menu
from bpy.props import StringProperty
from bl_ui.properties_data_modifier import DATA_PT_modifiers

def checkSel():
	obList = [ o for o in bpy.context.scene.objects if o.select ]
	if len(obList) == 0:
	   noSel = False
	else:
	   noSel = True
	return noSel

bpy.types.Scene.noSel = bpy.props.BoolProperty(name="Selection", default=False)
# Boolean Pie
class VIEW3D_PIE_HP_Boolean(Menu):
	bl_idname = "pie.hp_boolean"
	bl_label = "HP Boolean"
	bl_options = {'REGISTER', 'UNDO'}

	def draw(self, context):
		layout = self.layout
		pie = layout.menu_pie()
		split = pie.split()
		col = split.column(align=True)
		#Plain ol Booleans
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		prop = row.operator("view3d.hp_boolean_live", text="Add", icon_value=hp_icons["add-destr"].icon_id)
		prop.bool_operation = 'UNION'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		prop.live = 'NO'
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		prop = row.operator("view3d.hp_boolean_live", text="Intersect", icon_value=hp_icons["intersect-destr"].icon_id)
		prop.bool_operation = 'INTERSECT'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		prop.live = 'NO'
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		prop = row.operator("view3d.hp_boolean_live", text="Subtract", icon_value=hp_icons["subtract-destr"].icon_id)
		prop.bool_operation = 'DIFFERENCE'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		prop.live = 'NO'
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		row.operator("view3d.hp_boolean_slice", text="Slice", icon_value=hp_icons["slice-destr"].icon_id)
		#Live Booleans
		split = pie.split()
		col = split.column(align=True)

		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		prop = row.operator("view3d.hp_boolean_live", text="Live Add", icon_value=hp_icons["add-live"].icon_id)
		prop.bool_operation = 'UNION'
		prop.live = 'YES'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		prop = row.operator("view3d.hp_boolean_live", text="Live Intersect", icon_value=hp_icons["intersect-live"].icon_id)
		prop.bool_operation = 'INTERSECT'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		prop.live = 'YES'
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		prop = row.operator("view3d.hp_boolean_live", text="Live Subtract", icon_value=hp_icons["subtract-live"].icon_id)
		prop.bool_operation = 'DIFFERENCE'
		prop.live = 'YES'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		prop = row.operator("view3d.hp_boolean_live", text="Live Subtract Inset", icon_value=hp_icons["subinset-live"].icon_id)
		prop.bool_operation = 'DIFFERENCE'
		prop.live = 'YES'
		prop.cutline = 'NO'
		prop.insetted = 'YES'
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		prop = row.operator("view3d.hp_boolean_live", text="Live Cutline", icon_value=hp_icons["cutline-live"].icon_id)
		prop.bool_operation = 'DIFFERENCE'
		prop.live = 'YES'
		prop.cutline = 'YES'
		prop.insetted = 'NO'

		split = pie.split()
		col = split.column(align=True)

		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		row.operator("view3d.hp_boolean_apply", text="Apply and Copy").dup = 'YES'
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		row.operator("view3d.hp_boolean_apply", text="Apply").dup = 'NO'

		split = pie.split()
		col = split.column(align=True)
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		#row.operator("view3d.hp_boolean_toggle_bool_solver", text="Toggle Solver")
		row.operator("view3d.hp_boolean_toggle_cutters", text="Toggle Cutters", icon=toggleCutters())
		row = col.row(align=True)
		row.scale_y=1.5
		row.scale_x=1.5
		sub = row
		sub.operator("view3d.hp_settings", text="Bool Settings", icon='PREFERENCES')
		sub.active = checkSel()


	   # Boolean Pie
class VIEW3D_Menu_HP_Boolean(Menu):
	bl_idname = "menu.hp_boolean"
	bl_label = "HP Boolean"
	bl_options = {'REGISTER', 'UNDO'}

	def draw(self, context):
		layout = self.layout
		row = layout.column(align=True)
		prop = row.operator("view3d.hp_boolean_live", text="Add", icon_value=hp_icons["add-destr"].icon_id)
		prop.bool_operation = 'UNION'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		prop.live = 'NO'
		prop = row.operator("view3d.hp_boolean_live", text="Intersect", icon_value=hp_icons["intersect-destr"].icon_id)
		prop.bool_operation = 'INTERSECT'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		prop.live = 'NO'
		prop = row.operator("view3d.hp_boolean_live", text="Subtract", icon_value=hp_icons["subtract-destr"].icon_id)
		prop.bool_operation = 'DIFFERENCE'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		prop.live = 'NO'
		row.operator("view3d.hp_boolean_slice", text="Slice", icon_value=hp_icons["slice-destr"].icon_id)

		#Live Booleans
		row.separator()
		prop = row.operator("view3d.hp_boolean_live", text="Live Add", icon_value=hp_icons["add-live"].icon_id)
		prop.bool_operation = 'UNION'
		prop.live = 'YES'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		prop = row.operator("view3d.hp_boolean_live", text="Live Intersect", icon_value=hp_icons["intersect-live"].icon_id)
		prop.bool_operation = 'INTERSECT'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		prop.live = 'YES'
		prop = row.operator("view3d.hp_boolean_live", text="Live Subtract", icon_value=hp_icons["subtract-live"].icon_id)
		prop.bool_operation = 'DIFFERENCE'
		prop.live = 'YES'
		prop.cutline = 'NO'
		prop.insetted = 'NO'
		prop = row.operator("view3d.hp_boolean_live", text="Live Subtract Inset", icon_value=hp_icons["subinset-live"].icon_id)
		prop.bool_operation = 'DIFFERENCE'
		prop.live = 'YES'
		prop.cutline = 'NO'
		prop.insetted = 'YES'
		prop = row.operator("view3d.hp_boolean_live", text="Live Cutline", icon_value=hp_icons["cutline-live"].icon_id)
		prop.bool_operation = 'DIFFERENCE'
		prop.live = 'YES'
		prop.cutline = 'YES'
		prop.insetted = 'NO'

		# Toggle Slice
		row.separator()
		row.operator("view3d.hp_boolean_apply", text="Apply and Copy").dup = 'YES'
		row.operator("view3d.hp_boolean_apply", text="Apply").dup = 'NO'

		# Toggle Slice
		row.separator()
		#row.operator("view3d.hp_boolean_toggle_bool_solver", text="Toggle Solver")
		prop = row.operator("view3d.hp_boolean_toggle_cutters", text="Toggle Cutters", icon=toggleCutters())
		if checkSel():
			prop = row.menu(HPoptionsPanel.bl_idname, icon='PREFERENCES')

def toggleCutters():
	icon ='NONE'
	for ob in bpy.context.scene.objects:
		if ob.type == 'MESH' and ob.name.startswith("Bool_Cutter"):
			if ob.hide == False:
				icon = 'VISIBLE_IPO_ON'
			elif ob.hide == True:
				icon = 'VISIBLE_IPO_OFF'
	return icon

class HP_Boolean_Toggle_Cutters(bpy.types.Operator):
	bl_idname = "view3d.hp_boolean_toggle_cutters"
	bl_label = "hp_boolean_toggle_cutters"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		for ob in bpy.context.scene.objects:
			if ob.type == 'MESH' and ob.name.startswith("Bool_Cutter"):
				if ob.hide == False:
					ob.hide = True
				elif ob.hide == True:
					ob.hide = False
		return {'FINISHED'}
#class HP_Boolean_Toggle_Solver(bpy.types.Operator):
#    bl_idname = "view3d.hp_boolean_toggle_bool_solver"
#    bl_label = "hp_boolean_toggle_cutters"
#    bl_options = {'REGISTER', 'UNDO'}
#    def execute(self, context):
#        sel = bpy.context.selected_objects
#        scene = bpy.context.scene
#        bases = [base for base in scene.objects if not base.name.startswith("Bool_Cutter") and base.type == 'MESH']
#        for ob in sel:
#            #Get Cutters in Sel
#            if ob.name.startswith('Bool_Cutter'):
#                cutter = ob
#                for base in bases:
#                    for mod in base.modifiers:
#                        if mod.name == cutter.name:
#                            if mod.solver == 'BMESH':
#                                mod.solver = 'CARVE'
#                            else:
#                                mod.solver = 'BMESH'
#            else:
#                base = ob
#                for mod in base.modifiers:
#                    if mod.name.startswith ('Bool_Cutter'):
#                        if mod.solver == 'BMESH':
#                            mod.solver = 'CARVE'
#                        else:
#                            mod.solver = 'BMESH'
#        return {'FINISHED'}
class HP_Boolean_Live(bpy.types.Operator):
	bl_idname = "view3d.hp_boolean_live"
	bl_label = ""
	bl_options = {'REGISTER', 'UNDO'}
	cutline = bpy.props.StringProperty(name='Cutline',default='NO')
	cutlineThick = bpy.props.FloatProperty(name="Thickness Solver", min=0, max=5, precision=3, default=0.02)
	cutlineEven = bpy.props.BoolProperty(name="Even Thickness", default=True)
	cutlineNormals = bpy.props.BoolProperty(name="High Quality Normals", default=True)
	live = bpy.props.StringProperty(name='Live',default='NO')
	insetted = bpy.props.StringProperty(name='Insetted',default='NO')
	drawtype = bpy.props.StringProperty(name="Draw Type",default='BOUNDS')
	bool_operation = bpy.props.StringProperty(name="Boolean Operation")
	bool_solver = bpy.props.StringProperty(name="Boolean Solver",default='BMESH')

	def execute(self, context):
		sel = bpy.context.selected_objects
		base = bpy.context.active_object
		scene = bpy.context.scene
		isedit = False
		if context.active_object.mode != 'OBJECT' and self.live == 'NO':
			bpy.ops.mesh.select_linked(delimit={'NORMAL'})
			bpy.ops.mesh.intersect_boolean(operation=self.bool_operation)
			return {'FINISHED'}
		def create_cutter(drawtype, insetted):
			bpy.context.scene.objects.active = cutter
			cutter.name = "Bool_Cutter"
			scene_cutters = [obj for obj in scene.objects if obj.name.startswith("Bool_Cutter")]
			for x in scene_cutters:
				if x != cutter:
					bpy.ops.object.modifier_apply(apply_as='DATA', modifier=x.name)
			cutter.name = "Bool_Cutter_" + str(len(scene_cutters))
			if self.cutline == 'YES':
				cutter.modifiers.new('Cutline', "SOLIDIFY")
				bpy.context.object.modifiers['Cutline'].thickness = self.cutlineThick
				bpy.context.object.modifiers['Cutline'].use_even_offset = self.cutlineEven
				bpy.context.object.modifiers['Cutline'].use_quality_normals = self.cutlineNormals
			if self.insetted == 'YES':
				base.select = False
				cutter.select = True
				for x in scene_cutters:
					bpy.ops.object.modifier_apply(apply_as='DATA', modifier = x.name)
				bpy.ops.object.duplicate()
				bpy.context.scene.objects.active.name = "Bool_Inset"
				inset = bpy.context.active_object
				bpy.ops.object.editmode_toggle()
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
				bpy.ops.transform.resize(value=(0.92, 0.92, 0.92), constraint_axis=(False, False, False), mirror=False, proportional='DISABLED')
				bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
				bpy.ops.object.editmode_toggle()
				bpy.context.scene.objects.active = cutter
				bpy.ops.object.constraint_add(type='COPY_TRANSFORMS')
				bpy.context.object.constraints["Copy Transforms"].target = inset
				inset.select = True
				bpy.context.scene.objects.active = inset
			cutter.draw_type = drawtype
			cutter.hide_render = True
			cutter.cycles_visibility.camera = False
			cutter.cycles_visibility.diffuse = False
			cutter.cycles_visibility.glossy = False
			cutter.cycles_visibility.shadow = False
			cutter.cycles_visibility.scatter = False
			cutter.cycles_visibility.transmission = False
			cutter.select = False
		def create_bool(bool_operation, live):
			Bool = base.modifiers.new(cutter.name, "BOOLEAN")
			Bool.object = cutter
			Bool.operation = bool_operation
			#Bool.solver = bool_solver
			base.select = True
			bpy.context.scene.objects.active = base
			bpy.ops.object.modifier_move_down(modifier="Mirror Base")
			if self.live == 'NO':
				if context.active_object.mode != 'OBJECT':
					bpy.ops.object.editmode_toggle()
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier=cutter.name)
				base.select = False
				cutter.select = True
				bpy.ops.object.delete(use_global=False)
				base.select = True
				i = base.data.vertex_colors.active_index
				base.data.vertex_colors.active_index = i + 1
				bpy.ops.mesh.vertex_color_remove()

		if context.active_object.mode != 'OBJECT':
			isedit = True
			bpy.ops.mesh.select_linked()
			bpy.ops.mesh.normals_make_consistent(inside=False)
			bpy.ops.mesh.separate(type='SELECTED')
			bpy.ops.object.editmode_toggle()
			sel = bpy.context.selected_objects
		for cutter in sel:
			if cutter != base:
				create_cutter(self.drawtype, self.insetted)
				create_bool(self.bool_operation, self.live)
		if isedit == True and self.live == 'NO':
			bpy.ops.object.editmode_toggle()
		if self.insetted == 'YES':
			base.select = False
			for x in bpy.context.selected_objects:
				bpy.context.scene.objects.active = x
		return {'FINISHED'}



class HP_Boolean_Slice(bpy.types.Operator):
	"""slice"""
	bl_idname = "view3d.hp_boolean_slice"
	bl_label = ""
	bl_options = {'REGISTER', 'UNDO'}
	def execute(self, context):
		if bpy.context.mode=='OBJECT':
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.object.vertex_group_add()
			bpy.ops.object.vertex_group_assign()
			bpy.ops.object.editmode_toggle()
			bpy.ops.object.join()
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.object.vertex_group_select()
			bpy.ops.mesh.select_all(action='INVERT')
			bpy.ops.object.vertex_group_remove()
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
		bpy.ops.mesh.select_linked(delimit=set())
		bpy.ops.mesh.normals_make_consistent(inside=False)
		bpy.ops.object.vertex_group_add()
		bpy.ops.object.vertex_group_assign()
		bpy.ops.mesh.intersect()
		bpy.ops.object.vertex_group_add()
		bpy.ops.object.vertex_group_assign()
		i = bpy.context.active_object.vertex_groups.active_index
		i = i-1
		bpy.context.active_object.vertex_groups.active_index = i
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.vertex_group_select()
		bpy.ops.mesh.select_linked(delimit=set())
		bpy.ops.mesh.delete(type='VERT')
		bpy.ops.object.vertex_group_remove()
		bpy.ops.object.vertex_group_select()
		bpy.ops.object.vertex_group_remove()
		return {'FINISHED'}

class HP_Boolean_Apply(bpy.types.Operator):
	bl_idname = "view3d.hp_boolean_apply"
	bl_label = ""
	bl_options = {'REGISTER', 'UNDO'}
	name = StringProperty(name="Name")
	dup = bpy.props.StringProperty(name='Duplicate')
	def execute(self, context):
		def apply(dup):
			sel = bpy.context.selected_objects
			scene = bpy.context.scene
			scene_cutters = [obj for obj in scene.objects if obj.name.startswith("Bool_Cutter")]
			for ob in sel:
				if ob.name.startswith('Bool_Cutter'):
					iscutter = True
					cutter = ob
					for base in scene.objects:
						for mod in base.modifiers:
							bpy.context.scene.objects.active = base
							bpy.ops.object.modifier_apply(apply_as='DATA', modifier=cutter.name)
					cutter.select = True
				else:
					base = ob
					if self.dup == 'YES':
						bpy.ops.object.duplicate()
						clone = bpy.context.active_object
						base.hide = True
					for mod in base.modifiers:
						cutter = bpy.context.scene.objects[mod.name]
						bpy.ops.object.modifier_apply(apply_as='DATA', modifier=cutter.name)
						if self.dup == 'YES':
							cutter.hide = True
							continue
						cutter.select = True
						base.select = False
						bpy.ops.object.delete()
						base.select = True
			try:
				if iscutter == True:
					bpy.ops.object.delete()
					bpy.context.active_object.select = True
					sel = bpy.context.selected_objects
			except:
				pass
		apply(self.dup)
		return {'FINISHED'}

class HPoptionsPanel(bpy.types.Menu):
	bl_label = "HP Options"
	bl_idname = "hp.options"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout.column(1)
		active_object = context.active_object
		layout.operator("view3d.hp_settings", text="Bool Settings")
		layout.separator()


class CutlinePopup(bpy.types.Operator):
	bl_idname = "view3d.hp_settings"
	bl_label = "HP Bool Settings"
	bl_options = {'REGISTER', 'UNDO'}

	name = StringProperty(name="Name")

	def execute(self, context):
		return {'FINISHED'}

	def check(self, context):
		return True

	def invoke(self, context, event):
		object = bpy.context.active_object
#        if object is not None:
#            if object.type == "MESH":
#                self.status = object.hops.status
#        self.tab = get_preferences().helper_tab
#		wm = context.window_manager
#		return wm.invoke_popup(self, width=300)
		return context.window_manager.invoke_props_dialog(self, width=300, height=200)

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		object = bpy.context.active_object
		if not checkSel():
			colrow = col.row(align=True)
			colrow.alignment = "CENTER"
			colrow.label("No active object", icon="INFO")
			return

		layout.operator_menu_enum("object.modifier_add", "type")
		modifiers_panel = DATA_PT_modifiers(bpy.context)
		for modifier in object.modifiers:
			box = layout.template_modifier(modifier)
			if box:
				getattr(modifiers_panel, modifier.type)(box, object, modifier)

def Keymap_Heavypoly():
	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon

	km = kc.keymaps.new('Window', space_type='EMPTY', region_type='WINDOW', modal=False)
	kmi = km.keymap_items.new('wm.call_menu_pie', 'B', 'PRESS',oskey=True).properties.name="pie.hp_boolean"
	kmi = km.keymap_items.new('wm.call_menu', 'B', 'PRESS',alt=True, oskey=True).properties.name="menu.hp_boolean"

def get_hotkey_entry_item(km, kmi_name, properties): #kmi_value, properties):
	try:
		for i, km_item in enumerate(km.keymap_items):
			if km.keymap_items.keys()[i] == kmi_name:
				if km.keymap_items[i].properties.name == properties:
					return km_item
		return None
	except:
		pass

#def get_hotkey_entry_item(km, kmi_name): #kmi_value, properties):
#	for i, km_item in enumerate(km.keymap_items):
#		if km.keymap_items.keys()[i] == kmi_name:
#			return km_item
#	return None


def get_addon_name():
	return os.path.basename(os.path.dirname(os.path.realpath(__file__)))


addon_files=[("wm.call_menu_pie", "wm.call_menu_pie","pie.hp_boolean"),\
			("wm.call_menu", "wm.call_menu","menu.hp_boolean")]

class AdvanceUIPreferences(bpy.types.AddonPreferences):
	bl_idname = get_addon_name()

	def draw(self, context):
		layout = self.layout
		box=layout.box()
		split = box.split()
		col = split.column()
		col.label('Hotkeys:')
		col.label('Do NOT remove hotkeys, disable them instead!')
		col.separator()

		wm = bpy.context.window_manager
		kc = wm.keyconfigs.user
		for addon in addon_files:
			km = kc.keymaps['Window']
			kmi = get_hotkey_entry_item(km, addon[1], addon[2])
			if kmi:
#				row = col.row()
#				row = col.split(percentage=0.25)
#				row.label(addon[3])
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
			else:
				row.label("restore hotkeys from interface tab")



def LoadIcons():
	# importing icons
	import bpy.utils.previews
	global hp_icons
	hp_icons = bpy.utils.previews.new()

	# path to the folder where the icon is
	# the path is calculated relative to this py file inside the addon folder
	icons_dir = os.path.join(os.path.dirname(__file__), "icons")

	# load a preview thumbnail of a file and store in the previews collection
	hp_icons.load("add-destr", os.path.join(icons_dir, "add-destr.png"), 'IMAGE')
	hp_icons.load("intersect-destr", os.path.join(icons_dir, "intersect-destr.png"), 'IMAGE')
	hp_icons.load("subtract-destr", os.path.join(icons_dir, "subtract-destr.png"), 'IMAGE')
	hp_icons.load("slice-destr", os.path.join(icons_dir, "slice-destr.png"), 'IMAGE')
	hp_icons.load("add-live", os.path.join(icons_dir, "add-live.png"), 'IMAGE')
	hp_icons.load("intersect-live", os.path.join(icons_dir, "intersect-live.png"), 'IMAGE')
	hp_icons.load("subtract-live", os.path.join(icons_dir, "subtract-live.png"), 'IMAGE')
	hp_icons.load("subinset-live", os.path.join(icons_dir, "subinset-live.png"), 'IMAGE')
	hp_icons.load("cutline-live", os.path.join(icons_dir, "cutline-live.png"), 'IMAGE')


# global variable to store icons in
hp_icons = None

LoadIcons()

def register():
	bpy.utils.register_module(__name__)
	Keymap_Heavypoly()

	global hp_icons

def unregister():
	bpy.utils.unregister_module(__name__)
	Keymap_Heavypoly()

if __name__ == "__main__":
	register()
