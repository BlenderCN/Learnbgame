import bpy
from os.path import join as j

TOOL_NAME = "bge_tools_uv_scroll"
SCRIPT_NAME = TOOL_NAME + ".py"
MODULE_NAME = TOOL_NAME + ".main"
SCRIPT_PATH = j("bge-tools", "gen", SCRIPT_NAME)

PROP_SPRITES_DEFAULT = (8, 8)
PROP_SEQUENCE_DEFAULT = "0-63"
PROP_SKIP_DEFAULT = 0
PROP_LOOP_DEFAULT = -1
PROP_PINGPONG_DEFAULT = False
PROP_LINKED_DEFAULT = True

ERR_MSG_WRONG_OBJECT = "Selected object not suited for this application"
ERR_MSG_WRONG_LAYER = "Selected object not in active layer"
ERR_MSG_NO_OBJECT_SELECTED = "No object selected"

class UVScroll(bpy.types.Operator):
	
	bl_description = "Manages animation of a sprite sheet for the Blender Game Engine"
	bl_idname = "bge_tools.uv_scroll"
	bl_label = "BGE-Tools: UV Scroll"
	bl_options = {"REGISTER", "UNDO"}
	
	prop_uv_texture_name = bpy.props.StringProperty(name="UV Map", description="UV Map to be scrolled")
	prop_sprites = bpy.props.IntVectorProperty(name="Sprites", description="Number of sprites horizontally (X) and vertically (Y)", min=1, subtype="XYZ", size=2)
	prop_sequence = bpy.props.StringProperty(name="Sequence", description="Animation sequence. Example: \'0*2, 1-5, 7\' gives \'0, 0, 0, 1, 2, 3, 4, 5, 7\'")
	prop_skip = bpy.props.IntProperty(name="Skip", description="Number of logic tics to skip", min=0)
	prop_loop = bpy.props.IntProperty(name="Loop", description="Loop count; -1 infinite", min=-1)
	prop_pingpong = bpy.props.BoolProperty(name="Pingpong", description="Reverse the sequence with every loop")
	prop_linked = bpy.props.BoolProperty(name="Linked", description="Whether the mesh should be unique")
	
	def invoke(self, context, event):
		
		def init():
			self.uv_textures = context.object.data.uv_textures
			self.prop_uv_texture_name = self.uv_textures[0].name if self.uv_textures else ""
			self.obj_props = context.object.game.properties
			self.prop_sprites = [int(s) for s in self.obj_props["sprites"].value.replace(" ", "").split(",")] if "sprites" in self.obj_props else PROP_SPRITES_DEFAULT
			self.prop_sequence = self.obj_props["sequence"].value if "sequence" in self.obj_props else PROP_SEQUENCE_DEFAULT
			sensors = context.object.game.sensors
			self.prop_skip = sensors[TOOL_NAME].tick_skip if TOOL_NAME in sensors else PROP_SKIP_DEFAULT
			self.prop_loop = self.obj_props["loop"].value if "loop" in self.obj_props else PROP_LOOP_DEFAULT
			self.prop_pingpong = self.obj_props["pingpong"].value if "pingpong" in self.obj_props else PROP_PINGPONG_DEFAULT
			self.prop_linked = self.obj_props["linked"].value if "linked" in self.obj_props else PROP_LINKED_DEFAULT
			self.duplicate = context.object.data in [o.data for o in bpy.data.objects if o != context.object]
			self.error = None
			
		if context.object:
			if context.object.data:
				if context.object in context.selected_editable_objects:
					init()
				else:
					self.error = ERR_MSG_WRONG_LAYER
			else:
				self.error = ERR_MSG_WRONG_OBJECT
		else:
			self.error = ERR_MSG_NO_OBJECT_SELECTED
			
		return context.window_manager.invoke_props_dialog(self, width=480)
		
	def draw(self, context):
		layout = self.layout
		box = layout.box()
		
		if self.error:
			box.label(self.error, icon="ERROR")
			return
			
		row = box.row(True)
		row.prop_search(self, "prop_uv_texture_name",  context.object.data, "uv_textures")
		
		row = box.row(True)
		row.prop(self, "prop_sprites")
		
		row = box.row(True)
		row.prop(self, "prop_sequence")
		
		row = box.row(True)
		row.prop(self, "prop_skip")
		row.prop(self, "prop_loop")
		row.prop(self, "prop_pingpong", toggle=True)
		
		if self.duplicate:
			row.prop(self, "prop_linked", toggle=True)
			
		row.operator("bge_tools.uv_scroll_clear", text="", icon="X")
		
	def execute(self, context):
		
		if self.error:
			return {"CANCELLED"}
			
		def add_properties():
			if "sprites" not in self.obj_props:
				bpy.ops.object.game_property_new(type="STRING", name="sprites")
			if "sequence" not in self.obj_props:
				bpy.ops.object.game_property_new(type="STRING", name="sequence")
			if "loop" not in self.obj_props:
				bpy.ops.object.game_property_new(type="INT", name="loop")
			if "pingpong" not in self.obj_props:
				bpy.ops.object.game_property_new(type="BOOL", name="pingpong")
			if "linked" not in self.obj_props:
				bpy.ops.object.game_property_new(type="BOOL", name="linked")
				
		def set_properties():
			self.obj_props["sprites"].value = str(list(self.prop_sprites))[1:-1]
			self.obj_props["sequence"].value = self.prop_sequence
			self.obj_props["loop"].value = self.prop_loop
			self.obj_props["pingpong"].value = self.prop_pingpong
			self.obj_props["linked"].value = self.prop_linked
			
		def add_logic():
			
			if TOOL_NAME not in context.object.game.controllers:
				bpy.ops.logic.controller_add(type="PYTHON", name=TOOL_NAME, object=context.object.name)
				
			if TOOL_NAME not in context.object.game.sensors:
				bpy.ops.logic.sensor_add(type="ALWAYS", name=TOOL_NAME, object=context.object.name)
				
			sens = context.object.game.sensors[TOOL_NAME]
			sens.use_pulse_true_level = True
			sens.tick_skip = self.prop_skip
			cont = context.object.game.controllers[TOOL_NAME]
			cont.mode = "MODULE"
			cont.module = MODULE_NAME
			
			cont.link(sensor=sens)
			
		def add_script_internal():
			
			if SCRIPT_NAME in bpy.data.texts:
				bpy.data.texts.remove(bpy.data.texts[SCRIPT_NAME], do_unlink=True)
				
			addons_paths = bpy.utils.script_paths("addons")
			url = j(addons_paths[0], SCRIPT_PATH)
			text = bpy.ops.text.open(filepath=url, internal=True)
			if text != {"FINISHED"}:
				url = j(addons_paths[1], SCRIPT_PATH)
				bpy.ops.text.open(filepath=url, internal=True)
	
		def set_uv_texture():
			
			if not self.prop_uv_texture_name:
				return
				
			uv_texture = self.uv_textures[self.prop_uv_texture_name]
			uv_texture.active = True
			uv_texture.active_render = True
			bpy.ops.object.mode_set(mode="EDIT")
			bpy.ops.mesh.select_all(action="SELECT")
			area_type = context.area.type
			context.area.type = "IMAGE_EDITOR"
			bpy.ops.uv.reset()
			bpy.ops.uv.select_all(action="SELECT")
			bpy.ops.uv.cursor_set(location=(0.0, 0.0))
			context.space_data.pivot_point = "CURSOR"
			bpy.ops.transform.resize(value=[1/i for i in self.prop_sprites] + [1])
			context.area.type = area_type
			bpy.ops.uv.select_all(action="DESELECT")
			bpy.ops.mesh.select_all(action="DESELECT")
			bpy.ops.object.mode_set(mode="OBJECT")
			
		add_properties()
		set_properties()
		add_logic()
		add_script_internal()
		set_uv_texture()
		
		return {"PASS_THROUGH"}
		
class UVScrollClear(bpy.types.Operator):
	
	bl_description = "Clear"
	bl_idname = "bge_tools.uv_scroll_clear"
	bl_label = "BGE-Tools: UV Scroll Clear"
	bl_options = {"INTERNAL"}
	
	def execute(self, context):
		
		for i in range(len(context.object.game.properties)):
			bpy.ops.object.game_property_remove(i)
			
		bpy.ops.logic.controller_remove(controller=TOOL_NAME, object=context.object.name)
		bpy.ops.logic.sensor_remove(sensor=TOOL_NAME, object=context.object.name)
		
		if SCRIPT_NAME in bpy.data.texts:
			bpy.data.texts.remove(bpy.data.texts[SCRIPT_NAME], do_unlink=True)
			
		return {"FINISHED"}
		
def register():
	bpy.utils.register_class(UVScroll)
	bpy.utils.register_class(UVScrollClear)
	
def unregister():
	bpy.utils.unregister_class(UVScroll)
	bpy.utils.unregister_class(UVScrollClear)
	
if __name__ == "__main__":
	register()
	