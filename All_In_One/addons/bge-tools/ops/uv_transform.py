import bpy
from os.path import join as j

TOOL_NAME = "bge_tools_uv_transform"
SCRIPT_NAME = TOOL_NAME + ".py"
MODULE_NAME = TOOL_NAME + ".main"
SCRIPT_PATH = j("bge-tools", "gen", SCRIPT_NAME)

PROP_REF_OBJ_NAME_DEFAULT = ""
PROP_LIN_VEL_X_DEFAULT = 0
PROP_LIN_VEL_Y_DEFAULT = 0
PROP_ANGULAR_SPEED_DEFAULT = 0
PROP_ORIGIN_X_DEFAULT = 0.5
PROP_ORIGIN_Y_DEFAULT = 0.5
PROP_SKIP_DEFAULT = 0
PROP_UNLINK_DEFAULT = True

ERR_MSG_WRONG_OBJECT = "Selected object not suited for this application"
ERR_MSG_WRONG_LAYER = "Selected object not in active layer"
ERR_MSG_NO_OBJECT_SELECTED = "No object selected"

class UVTransform(bpy.types.Operator):
	
	bl_description = "Manages animation of a texture for the Blender Game Engine"
	bl_idname = "bge_tools.uv_transform"
	bl_label = "BGE-Tools: UV Transform"
	bl_options = {"REGISTER", "UNDO"}
	
	prop_uv_texture_name = bpy.props.StringProperty(name="UV Map", description="UV Map to be transformed")
	prop_ref_obj_name = bpy.props.StringProperty(name="Reference Object", description="Child object to influence the transform")
	prop_lin_vel = bpy.props.FloatVectorProperty(name="Linear Velocity", description="Linear velocity in units per second", subtype="VELOCITY", size=2)
	prop_ang_speed = bpy.props.FloatProperty(name="", description="Angular speed in degrees per second", subtype="ANGLE")
	prop_origin = bpy.props.FloatVectorProperty(name="", description="Normalized origin", min=0, max=1, default=(0.5, 0.5), subtype="XYZ", size=2)
	prop_skip = bpy.props.IntProperty(name="Skip", description="Number of logic tics to skip", min=0)
	prop_linked = bpy.props.BoolProperty(name="Linked", description="Give the object a unique mesh in game")
	
	def invoke(self, context, event):
		
		def init():
			self.uv_textures = context.object.data.uv_textures
			self.prop_uv_texture_name = self.uv_textures[0].name if self.uv_textures else ""
			self.obj_props = context.object.game.properties
			self.prop_ref_obj_name = self.obj_props["ref_obj_name"].value if "ref_obj_name" in self.obj_props else PROP_REF_OBJ_NAME_DEFAULT
			self.prop_lin_vel.x = self.obj_props["lin_vel_x"].value if "lin_vel_x" in self.obj_props else PROP_LIN_VEL_X_DEFAULT
			self.prop_lin_vel.y = self.obj_props["lin_vel_y"].value if "lin_vel_y" in self.obj_props else PROP_LIN_VEL_Y_DEFAULT
			self.prop_ang_speed = self.obj_props["ang_speed"].value if "ang_speed" in self.obj_props else PROP_ANGULAR_SPEED_DEFAULT
			self.prop_origin.x = self.obj_props["origin_x"].value if "origin_x" in self.obj_props else PROP_ORIGIN_X_DEFAULT
			self.prop_origin.y = self.obj_props["origin_y"].value if "origin_y" in self.obj_props else PROP_ORIGIN_Y_DEFAULT
			sensors = context.object.game.sensors
			self.prop_skip = sensors[TOOL_NAME].tick_skip if TOOL_NAME in sensors else PROP_SKIP_DEFAULT
			self.prop_linked = self.obj_props["linked"].value if "linked" in self.obj_props else PROP_UNLINK_DEFAULT
			self.duplicate = context.object.data in [o.data for o in bpy.data.objects if o != context.object]
			self.error = None
			
		if context.object:
			context.object.data = context.object.data
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
		row.prop_search(self, "prop_ref_obj_name",  context.scene, "objects")
		
		row = box.row()
		col = row.column(True)
		col.label("Angular Speed:")
		col.prop(self, "prop_ang_speed")
		col.prop(self, "prop_lin_vel")
		
		col = row.column(True)
		col.label("Origin:")
		col.prop(self, "prop_origin")
		
		col.label("")
		row = col.row(True)
		row.prop(self, "prop_skip")
		
		if self.duplicate:
			row.prop(self, "prop_linked", toggle=True)
			
		row.operator("bge_tools.uv_transform_clear", text="", icon="X")
		
	def execute(self, context):
		
		if self.error:
			return {"CANCELLED"}
			
		def add_properties():
			if "ref_obj_name" not in self.obj_props:
				bpy.ops.object.game_property_new(type="STRING", name="ref_obj_name")
			if "lin_vel_x" not in self.obj_props:
				bpy.ops.object.game_property_new(type="FLOAT", name="lin_vel_x")
			if "lin_vel_y" not in self.obj_props:
				bpy.ops.object.game_property_new(type="FLOAT", name="lin_vel_y")
			if "ang_speed" not in self.obj_props:
				bpy.ops.object.game_property_new(type="FLOAT", name="ang_speed")
			if "origin_x" not in self.obj_props:
				bpy.ops.object.game_property_new(type="FLOAT", name="origin_x")
			if "origin_y" not in self.obj_props:
				bpy.ops.object.game_property_new(type="FLOAT", name="origin_y")
			if "linked" not in self.obj_props:
				bpy.ops.object.game_property_new(type="BOOL", name="linked")
				
		def set_properties():
			self.obj_props["ref_obj_name"].value = self.prop_ref_obj_name
			self.obj_props["lin_vel_x"].value = self.prop_lin_vel.x
			self.obj_props["lin_vel_y"].value = self.prop_lin_vel.y
			self.obj_props["ang_speed"].value = self.prop_ang_speed
			self.obj_props["origin_x"].value = self.prop_origin.x
			self.obj_props["origin_y"].value = self.prop_origin.y
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
				
		add_properties()
		set_properties()
		add_logic()
		add_script_internal()
		
		return {"PASS_THROUGH"}
		
class UVTransformClear(bpy.types.Operator):
	
	bl_description = "Clear"
	bl_idname = "bge_tools.uv_transform_clear"
	bl_label = "BGE-Tools: UV Transform Clear"
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
	bpy.utils.register_class(UVTransform)
	bpy.utils.register_class(UVTransformClear)
	
def unregister():
	bpy.utils.unregister_class(UVTransform)
	bpy.utils.unregister_class(UVTransformClear)
	
if __name__ == "__main__":
	register()
	