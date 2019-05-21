'''
Author :  Dominik Sand 
Date : 23.04.2013

Simionoptions panel for the Blender UI
sources : http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Interface
'''
import bpy

#Property Menu Options
bpy.types.Scene.obj_size = bpy.props.FloatProperty( name = "Size", default = 0.1 , min = 0 , max = 1)
bpy.types.Scene.obj_distance = bpy.props.FloatProperty( name = "Distance Scale Factor", default = 1 , min = 0 , max = 5)
bpy.types.Scene.frame_num = bpy.props.IntProperty( name = "Number of Frames", default = 250 , min = 0 , max = 500000)
bpy.types.Scene.animation_type = bpy.props.EnumProperty(items = [("path_id","Path","animates data as path"),("sphere_id","Spheres","animates data as spheres"),("particle_id","Particle","animates data as particles")],default="path_id",name = "Animation Type",description="Animation Properties")
bpy.types.Scene.number_pathverts = bpy.props.IntProperty( name = "Path verticles", default = 8 , min = 1 , max = 64)
bpy.types.Scene.number_merge = bpy.props.IntProperty( name = "Number of paths to merge", default = 1 , min = 1 , max = 50)
bpy.types.Scene.ion_splat = bpy.props.BoolProperty( name = "Mark Ion Splat " ,  default = False)
bpy.types.Scene.ion_tube_mod = bpy.props.BoolProperty( name = "Material Tube Modifier" ,  default = False)


#panel class
class options_panel(bpy.types.Panel) :
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context ="scene"
	bl_label = "Simion to Animation"
	def draw(self, context):
		scn = bpy.context.scene
		layout = self.layout
		column  = layout.row()
		column.prop(scn,"obj_size")
		column = layout.row()
		column.prop(scn,"obj_distance")
		column = layout.row()
		column.prop(scn,"frame_num")
		column = layout.row()
		column.prop(scn,"number_pathverts")
		column = layout.row()
		column.prop(scn,"number_merge")
		column = layout.row()
		column.prop(scn,"ion_splat")
		column = layout.row()
		column.prop(scn,"ion_tube_mod")
		column = layout.row()
		column.prop(scn,"animation_type")
		
		

