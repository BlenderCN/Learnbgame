bl_info = \
{
  "name": "Cal3D format",
  "author": "Jean-Baptiste Lamy (Jiba), " \
            "Chris Montijin, "            \
            "Damien McGinnes, "           \
            "David Young, "               \
            "Alexey Dorokhov, "           \
            "Matthias Ferch, "             \
            "Peter Amstutz",
  "blender": (2, 5, 8),
  "api": 35622,
  "location": "File > Export > Cal3D (.cfg)",
  "description": "Export mesh geometry, armature, "   \
                 "materials and animations to Cal3D",
  "warning": "",
  "wiki_url": "",
  "tracker_url": "",
  "category": "Import-Export"
}

# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "bpy" in locals():
	import imp

	if "mesh_classes" in locals():
		imp.reload(mesh_classes)

	if "export_mesh" in locals():
		imp.reload(export_mesh)


import bpy
from bpy import ops
from bpy import context
from bpy.props import BoolProperty,			\
                      EnumProperty,			\
                      CollectionProperty,	\
                      FloatProperty,		\
                      StringProperty,		\
                      FloatVectorProperty,	\
                      IntProperty


import bpy_extras
from bpy_extras.io_utils import ExportHelper, ImportHelper

import mathutils

import os.path
import sys
import traceback

class ExportCal3D(bpy.types.Operator, ExportHelper):
	'''Save Cal3d Files'''

	bl_idname = "cal3d_model.cfg"
	bl_label = 'Export Cal3D'
	bl_options = {'PRESET'}

	filename_ext = ".cfg"
	filter_glob = StringProperty(default="*.cfg;*.xsf;*.xaf;*.xmf;*.xrf;*.csf;*.caf;*.cmf;*.crf",
								 options={'HIDDEN'})

	# List of operator properties, the attributes will be assigned
	# to the class instance from the operator settings before calling.

	# context group
	mesh_prefix = StringProperty(name="Mesh Prefix", 
									 default="model_")
									 
	skeleton_prefix = StringProperty(name="Skeleton Prefix", 
									 default="")
									 
	anim_prefix = StringProperty(name="Animation Prefix",
									  default="")
									  
	material_prefix = StringProperty(name="Material Prefix",
									  default="")
	
	imagepath_prefix = StringProperty(name="Image Path Prefix",
									  default="")
									  
	base_rotation = FloatVectorProperty(name="Base Rotation (XYZ)", 
										default = (0.0, 0.0, 0.0),
										subtype="EULER")

	base_scale = FloatProperty(name="Base Scale",
							   default=1.0)
							   
	fps = FloatProperty(name="Frame Rate",
					  default=30.0)

	#path_mode = bpy_extras.io_utils.path_reference_mode
	
	use_groups = BoolProperty(name="Vertex Groups", description="Export the meshes using vertex groups.", default=True)
	#use_envelopes = BoolProperty(name="Envelopes", description="Export the meshes using bone envelopes.", default=True)
	
	skeleton_binary_bool = EnumProperty(
            name="Skeleton Filetype",
            items=(('binary', "Binary (.CSF)", "Export a binary skeleton"),
                   ('xml', "XML (.XSF)", "Export an xml skeleton"),
                   ),
			default='binary'
            )
	mesh_binary_bool = EnumProperty(
            name="Mesh Filetype",
            items=(('binary', "Binary (.CMF)", "Export a binary mesh"),
                   ('xml', "XML (.XMF)", "Export an xml mesh"),
                   ),
			default='binary'
            )
	animation_binary_bool = EnumProperty(
            name="Animation Filetype",
            items=(('binary', "Binary (.CAF)", "Export a binary animation"),
                   ('xml', "XML (.XAF)", "Export an xml animation"),
                   ),
			default='binary'
            )
	material_binary_bool = EnumProperty(
            name="Material Filetype",
            items=(('binary', "Binary (.CRF)", "Export a binary material"),
                   ('xml', "XML (.XRF)", "Export an xml material"),
                   ),
			default='xml'
            )
	
	export_cfg = BoolProperty(name="Export the config file (.CFG)", description="Whether or not to export the .CFG file.", default=False)
	
	def execute(self, context):
		from . import export_mesh
		from . import export_armature
		from . import export_action
		from .export_armature import create_cal3d_skeleton
		from .export_mesh import create_cal3d_materials
		from .export_mesh import create_cal3d_mesh
		from .export_action import create_cal3d_animation

		cal3d_dirname = os.path.dirname(self.filepath)

		cal3d_skeleton = None
		cal3d_materials = []
		cal3d_meshes = []
		cal3d_animations = []
		armature_obj = None

		# base_translation, base_rotation, and base_scale are user adjustments to the export
		base_translation = mathutils.Vector([0.0, 0.0, 0.0])
		base_rotation = mathutils.Euler([self.base_rotation[0],
		                                 self.base_rotation[1],
		                                 self.base_rotation[2]], 'XYZ').to_matrix()
		base_scale = self.base_scale
		fps = self.fps
		
		#visible_objects = [ob for ob in context.scene.objects if ob.is_visible(context.scene)]
		visible_objects = context.selected_objects
		
		# Export armatures
		try:
			for obj in visible_objects:
				if obj.type == "ARMATURE":
					if cal3d_skeleton:
						raise RuntimeError("Only one armature is supported per scene")
					armature_obj = obj
					cal3d_skeleton = create_cal3d_skeleton(obj, obj.data,
					                                       base_rotation.copy(),
					                                       base_translation.copy(),
					                                       base_scale, 900)
		except Exception as e:
			print("###### ERROR DURING ARMATURE EXPORT ######")
			traceback.print_exc()
			return {"FINISHED"}

		# Export meshes and materials
		try:
			cal3d_materials = create_cal3d_materials(cal3d_dirname, self.imagepath_prefix, 900)

			for obj in visible_objects:
				if obj.type == "MESH" and obj.is_visible(context.scene):
					cal3d_meshes.append(create_cal3d_mesh(context.scene, obj, 
														  cal3d_skeleton,
														  cal3d_materials,
														  base_rotation,
														  base_translation,
														  base_scale, 900,
														  self.use_groups, False, armature_obj))
		except RuntimeError as e:
			print("###### ERROR DURING MESH EXPORT ######")
			print(e)
			return {"FINISHED"}


		# Export animations
		try:
			if cal3d_skeleton:
				for action in bpy.data.actions:
					cal3d_animation = create_cal3d_animation(cal3d_skeleton,
					                                         action, fps, 900)
					if cal3d_animation:
						cal3d_animations.append(cal3d_animation)
						
		except RuntimeError as e:
			print("###### ERROR DURING ACTION EXPORT ######")
			print(e)
			return {"FINISHED"}



		if cal3d_skeleton:
			if self.skeleton_binary_bool == 'binary':
				skeleton_filename = self.skeleton_prefix + cal3d_skeleton.name + ".csf"
				skeleton_filepath = os.path.join(cal3d_dirname, skeleton_filename)
				cal3d_skeleton_file = open(skeleton_filepath, "wb")
				cal3d_skeleton.to_cal3d_binary(cal3d_skeleton_file)
			else:
				skeleton_filename = self.skeleton_prefix + cal3d_skeleton.name + ".xsf"
				skeleton_filepath = os.path.join(cal3d_dirname, skeleton_filename)
				cal3d_skeleton_file = open(skeleton_filepath, "wt")
				cal3d_skeleton_file.write(cal3d_skeleton.to_cal3d_xml())
			cal3d_skeleton_file.close()
			print("Wrote skeleton '%s'" % (skeleton_filename))

		i = 0
		for cal3d_material in cal3d_materials:
			if self.material_binary_bool == 'binary':
				material_filename = self.material_prefix + cal3d_material.name + ".crf"
				material_filepath = os.path.join(cal3d_dirname, material_filename)
				cal3d_material_file = open(material_filepath, "wb")
				cal3d_material.to_cal3d_binary(cal3d_material_file)
			else:
				material_filename = self.material_prefix + cal3d_material.name + ".xrf"
				material_filepath = os.path.join(cal3d_dirname, material_filename)
				cal3d_material_file = open(material_filepath, "wt")
				cal3d_material_file.write(cal3d_material.to_cal3d_xml())
			cal3d_material_file.close()
			print("Wrote material '%s' with index %s" % (material_filename, i))
			i += 1


		for cal3d_mesh in cal3d_meshes:
			if self.mesh_binary_bool == 'binary':
				mesh_filename = self.mesh_prefix + cal3d_mesh.name + ".cmf"
				mesh_filepath = os.path.join(cal3d_dirname, mesh_filename)
				cal3d_mesh_file = open(mesh_filepath, "wb")
				cal3d_mesh.to_cal3d_binary(cal3d_mesh_file)
			else:
				mesh_filename = self.mesh_prefix + cal3d_mesh.name + ".xmf"
				mesh_filepath = os.path.join(cal3d_dirname, mesh_filename)
				cal3d_mesh_file = open(mesh_filepath, "wt")
				cal3d_mesh_file.write(cal3d_mesh.to_cal3d_xml())
			cal3d_mesh_file.close()
			print("Wrote mesh '%s' with materials %s" % (mesh_filename, [x.material_id for x in cal3d_mesh.submeshes]))
			
		for cal3d_animation in cal3d_animations:
			if self.animation_binary_bool == 'binary':
				animation_filename = self.anim_prefix + cal3d_animation.name + ".caf"
				animation_filepath = os.path.join(cal3d_dirname, animation_filename)
				cal3d_animation_file = open(animation_filepath, "wb")
				cal3d_animation.to_cal3d_binary(cal3d_animation_file)
			else:
				animation_filename = self.anim_prefix + cal3d_animation.name + ".xaf"
				animation_filepath = os.path.join(cal3d_dirname, animation_filename)
				cal3d_animation_file = open(animation_filepath, "wt")
				cal3d_animation_file.write(cal3d_animation.to_cal3d_xml())
			cal3d_animation_file.close()
			print("Wrote animation '%s'" % (animation_filename))


		if self.export_cfg:
			cal3d_cfg_file = open(self.filepath, "wt")

			# lolwut?
			#cal3d_cfg_file.write("path={0}\n".format("data\\models\\" + os.path.basename(self.filepath[:-4])+ "\\"))
			#cal3d_cfg_file.write("scale=0.01f\n")
			
			if cal3d_skeleton:
				if self.skeleton_binary_bool == 'binary':
					skeleton_filename = self.skeleton_prefix + cal3d_skeleton.name + ".csf"
				else:
					skeleton_filename = self.skeleton_prefix + cal3d_skeleton.name + ".xsf"
				cal3d_cfg_file.write("skeleton={0}\n".format(skeleton_filename))

			for cal3d_animation in cal3d_animations:
				if self.animation_binary_bool == 'binary':
					animation_filename = self.anim_prefix + cal3d_animation.name + ".caf"
				else:
					animation_filename = self.anim_prefix + cal3d_animation.name + ".xaf"
				cal3d_cfg_file.write("animation={0}\n".format(animation_filename))

			for cal3d_material in cal3d_materials:
				if self.material_binary_bool == 'binary':
					material_filename = self.material_prefix + cal3d_material.name + ".crf"
				else:
					material_filename = self.material_prefix + cal3d_material.name + ".xrf"
				cal3d_cfg_file.write("material={0}\n".format(material_filename))

			for cal3d_mesh in cal3d_meshes:
				if self.mesh_binary_bool == 'binary':
					mesh_filename = self.mesh_prefix + cal3d_mesh.name + ".cmf"
				else:
					mesh_filename = self.mesh_prefix + cal3d_mesh.name + ".xmf"
				cal3d_cfg_file.write("mesh={0}\n".format(mesh_filename))

			cal3d_cfg_file.close()

		return {"FINISHED"}

	def draw(self, context):
		layout = self.layout
		
		row = layout.row(align=True)
		row.prop(self, "skeleton_prefix")
		
		row = layout.row(align=True)
		row.prop(self, "mesh_prefix")
		
		row = layout.row(align=True)
		row.prop(self, "anim_prefix")
		
		row = layout.row(align=True)
		row.prop(self, "material_prefix")
		
		row = layout.row(align=True)
		row.prop(self, "imagepath_prefix")
		
		row = layout.row(align=True)
		row.prop(self, "base_rotation")
		
		row = layout.row(align=True)
		row.prop(self, "base_scale")
		
		row = layout.row(align=True)
		row.prop(self, "fps")
		
		#row = layout.row(align=True)
		#row.prop(self, "path_mode")
		
		row = layout.row(align=True)
		row.label(text="Export with:")
		row = layout.row(align=True)
		row.prop(self, "use_groups")
		#row.prop(self, "use_envelopes")
		
		row = layout.row(align=True)
		row.label(text="Skeleton")
		row.prop(self, "skeleton_binary_bool", expand=True)
		row = layout.row(align=True)
		row.label(text="Mesh")
		row.prop(self, "mesh_binary_bool", expand=True)
		row = layout.row(align=True)
		row.label(text="Animation")
		row.prop(self, "animation_binary_bool", expand=True)
		row = layout.row(align=True)
		row.label(text="Material")
		row.prop(self, "material_binary_bool", expand=True)
		
		row = layout.row(align=True)
		row.prop(self, "export_cfg")

	def invoke(self, context, event):
		
		self.fps = context.scene.render.fps
		sc = ""
		if len(bpy.data.scenes) > 1:
			sc = context.scene.name + "_"
		pre = os.path.splitext(os.path.basename(bpy.data.filepath))[0] + "_" + sc
		self.mesh_prefix = pre
		self.skeleton_prefix = pre
		self.anim_prefix = pre
		self.material_prefix = pre
		r = super(ExportCal3D, self).invoke(context, event)
		
		#print(bpy.context.active_operator)
		#preset = bpy.utils.preset_find("default", "operator\\cal3d_model.cfg", display_name=False)
		#print("preset is " + preset)
		#orig = context["active_operator"]
		#try:
		#	bpy.context["active_operator"] = self
		#	bpy.ops.script.execute_preset(context_copy, filepath=preset, menu_idname="WM_MT_operator_presets")
		#finally:
		#	context["active_operator"] = orig
		
		return r

def menu_func_export(self, context):
	self.layout.operator(ExportCal3D.bl_idname, text="Cal3D")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
	register()
