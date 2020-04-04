# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	"name": "QuickPie",
	"author": "Johann Schill",
	"version": (0, 1, 1),
	"blender": (2, 7, 2),
	"description": "Quick Pie Menu - Spacebar, Q and X",
	"category": "Learnbgame",
}



import bpy
import bmesh
import time
import math

from bpy.types import Menu
from bpy.props import *
from bpy.app.handlers import persistent
from bpy.types import Operator, AddonPreferences
from bl_ui.properties_paint_common import (
				UnifiedPaintPanel,
				brush_texture_settings,
				brush_texpaint_common,
				brush_mask_texture_settings,
		)



#Radial Clone from Mifth Tools
bpy.mifthTools = dict()

class MFTProperties(bpy.types.PropertyGroup):

	radialClonesAxis = EnumProperty(
		items = (('X', 'X', ''),
			('Y', 'Y', ''),
			('Z', 'Z', '')
			),
		default = 'Z'
	)

	radialClonesAxisType = EnumProperty(
		items = (('Global', 'Global', ''),
			   ('Local', 'Local', '')
			   ),
		default = 'Global'
	)


class MFTRadialClone(bpy.types.Operator):
	bl_idname = "mft.radialclone"
	bl_label = "Radial Clone"
	bl_description = "Radial Clone"
	bl_options = {'REGISTER', 'UNDO'}

	radialClonesAngle = FloatProperty(
		name = "Angle",
		default = 360.0,
		min = -360.0,
		max = 360.0
	)
	clonez = IntProperty(
		name = "Count",
		default = 8,
		min = 2,
		max = 300
	)
	

	def execute(self, context):

		if len(bpy.context.selected_objects) > 0:
			activeObj = bpy.context.scene.objects.active
			selObjects = bpy.context.selected_objects
			mifthTools = bpy.context.scene.mifthTools
			#self.clonez = mifthTools.radialClonesNumber

			activeObjMatrix = activeObj.matrix_world

			for i in range(self.clonez - 1):
				bpy.ops.object.duplicate(linked=True, mode='DUMMY')
				#newObj = bpy.context.selected_objects[0]
				#print(newObj)
				#for obj in bpy.context.selected_objects:
				theAxis = None

				if mifthTools.radialClonesAxis == 'X':
					if mifthTools.radialClonesAxisType == 'Local':
						theAxis = (activeObjMatrix[0][0], activeObjMatrix[1][0], activeObjMatrix[2][0])
					else:
						theAxis = (1, 0, 0)

				elif mifthTools.radialClonesAxis == 'Y':
					if mifthTools.radialClonesAxisType == 'Local':
						theAxis = (activeObjMatrix[0][1], activeObjMatrix[1][1], activeObjMatrix[2][1])
					else:
						theAxis = (0, 1, 0)

				elif mifthTools.radialClonesAxis == 'Z':
					if mifthTools.radialClonesAxisType == 'Local':
						theAxis = (activeObjMatrix[0][2], activeObjMatrix[1][2], activeObjMatrix[2][2])
					else:
						theAxis = (0, 0, 1)
				
				rotateValue = (math.radians(self.radialClonesAngle)/float(self.clonez))
				bpy.ops.transform.rotate(value=rotateValue, axis=theAxis)


			bpy.ops.object.select_all(action='DESELECT')

			for obj in selObjects:
				obj.select = True
			selObjects = None
			bpy.context.scene.objects.active = activeObj
		else:
			self.report({'INFO'}, "Select Objects!")

		return {'FINISHED'}



#Apply Transforms
class ApplyTransformAll(bpy.types.Operator):  
	bl_idname = "apply.transformall"  
	bl_label = "Apply Transform All"  
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None
	
	def execute(self, context):
		bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
		return {'FINISHED'}   
		
		
#Auto Smooth
class AutoSmooth(bpy.types.Operator): 
	bl_idname = "auto.smooth"  
	bl_label = "Auto Smooth"  
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'OBJECT' and context.active_object.type == 'MESH'
	
	def execute(self, context):
		bpy.context.object.data.use_auto_smooth = True
		bpy.context.object.data.auto_smooth_angle = 0.523598
		bpy.ops.object.shade_smooth()
		#bpy.ops.object.shade_flat()
		return {'FINISHED'}  
	

#Clear All
class ClearAll(bpy.types.Operator):  
	bl_idname = "clear.all"  
	bl_label = "Clear All" 
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None
	
	def execute(self, context):
		selection = bpy.context.selected_objects
		bpy.ops.object.location_clear()
		bpy.ops.object.rotation_clear()
		bpy.ops.object.scale_clear()
		return {'FINISHED'} 
		
		
#Bool Union
class BoolUnion(bpy.types.Operator):  
	bl_idname = "bool.union"  
	bl_label = "Bool Union" 

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'OBJECT' and context.active_object.type == 'MESH'  and 1<len(bpy.context.selected_objects)<=2

	def execute(self, context):
		bpy.ops.btool.boolean_union_direct()
		return {'FINISHED'} 


class BoolDiff(bpy.types.Operator):  
	bl_idname = "bool.diff"  
	bl_label = "Bool Difference" 

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'OBJECT' and context.active_object.type == 'MESH'  and 1<len(bpy.context.selected_objects)<=2

	def execute(self, context): 
		bpy.ops.btool.boolean_diff_direct()
		return {'FINISHED'} 



#Join Object
class JoinObject(bpy.types.Operator):  
	bl_idname = "join.object"  
	bl_label = "Join Object" 

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'OBJECT' and 1<len(bpy.context.selected_objects)

	def execute(self, context):
		bpy.ops.object.join()
		return {'FINISHED'} 



			
#Enable Dyntopo
class EnableDyntopo(bpy.types.Operator):  
	bl_idname = "enable.dyntopo"  
	bl_label = "Enable Dyntopo" 
	
	def execute(self, context):
		bpy.ops.sculpt.dynamic_topology_toggle()
		bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'SUBDIVIDE_COLLAPSE'
		bpy.context.scene.tool_settings.sculpt.detail_type_method = 'CONSTANT'
		bpy.context.scene.tool_settings.sculpt.use_smooth_shading = True
		bpy.context.scene.tool_settings.sculpt.constant_detail = 5
		return {'FINISHED'} 


#Sculpt Symmetrize -X to +X
class SculptSymmetrizeMoinsX(bpy.types.Operator):  
	bl_idname = "sculpt.symmetrizemoinsx"  
	bl_label = "Sculpt Symmetrize - X to + X" 

	@classmethod
	def poll(cls, context):
		return (context.sculpt_object and context.tool_settings.sculpt and context.sculpt_object.use_dynamic_topology_sculpting)
	
	def execute(self, context):
		bpy.ops.sculpt.symmetrize()
		if bpy.context.scene.tool_settings.sculpt.symmetrize_direction ==  'POSITIVE_X' :
			bpy.context.scene.tool_settings.sculpt.symmetrize_direction = 'NEGATIVE_X'
		return {'FINISHED'} 






		
		
		
		
		   



# =======================
# Keypress SPACE
# =======================
class PieQuick(Menu):
	# label is displayed at the center of the pie menu.
	bl_label = "Select Mode"
	bl_idname = "mesh.quickpie"

	def draw(self, context):
		layout = self.layout
		
		pie = layout.menu_pie()

		if bpy.context.area.type == 'VIEW_3D' and not bpy.context.object:
		

			#4 - LEFT
			pie.operator("apply.transformall", text="Apply All", icon='MANIPUL')
			#6 - RIGHT
			pie.operator("bool.diff", text="Cutout", icon='ZOOMOUT')
			#2 - BOTTOM
			pie.operator("object.origin_set", text="Origin to Geo",icon="ROTATECOLLECTION").type = 'ORIGIN_GEOMETRY'
			#8 - TOP
			pie.operator("screen.redo_last", text="Setting", icon='SETTINGS')
			#7 - TOP - LEFT 
			pie.operator("auto.smooth", text="AutoSmooth", icon='MESH_DATA') 
			#9 - TOP - RIGHT
			pie.operator("bool.union", text="Union", icon='ZOOMIN') 
			#1 - BOTTOM - LEFT
			pie.operator("join.object",icon="GROUP")
			#3 - BOTTOM - RIGHT
			pie.operator("mft.radialclone", text="Radial Clone", icon='CURSOR') 
			
		   
		
		elif bpy.context.area.type == 'VIEW_3D' and bpy.context.object.mode == 'OBJECT':

			#4 - LEFT
			pie.operator("apply.transformall", text="Apply All", icon='MANIPUL')
			#6 - RIGHT
			pie.operator("bool.diff", text="Cutout", icon='ZOOMOUT')
			#2 - BOTTOM
			pie.operator("object.origin_set", text="Origin to Geo",icon="ROTATECOLLECTION").type = 'ORIGIN_GEOMETRY'
			#8 - TOP
			pie.operator("screen.redo_last", text="Setting", icon='SETTINGS')
			#7 - TOP - LEFT 
			pie.operator("auto.smooth", text="AutoSmooth", icon='MESH_DATA')  
			#9 - TOP - RIGHT
			pie.operator("bool.union", text="Union", icon='ZOOMIN') 
			#1 - BOTTOM - LEFT
			pie.operator("join.object",icon="GROUP")
			#3 - BOTTOM - RIGHT
			pie.operator("mft.radialclone", text="Radial Clone", icon='CURSOR')   
			
			
		
		elif bpy.context.object.mode == 'EDIT': 
		

			#4 - LEFT
			pie.operator("mesh.bevel",text="Bevel Vertex",icon='MOD_DISPLACE').vertex_only = True
			#6 - RIGHT
			pie.operator("mesh.select_mode", text="Vertex", icon='VERTEXSEL').type = 'VERT'
			#2 - BOTTOM
			pie.operator("mesh.merge", text="Merge", icon='AUTOMERGE_ON').type='CENTER'
			#8 - TOP
			pie.operator("screen.redo_last", text="Setting", icon='SETTINGS')
			#7 - TOP - LEFT 
			pie.operator("mesh.bevel",text="Bevel Edge", icon='MOD_BEVEL')
			#9 - TOP - RIGHT
			pie.operator("mesh.select_mode", text="Edge", icon='EDGESEL').type = 'EDGE'
			#1 - BOTTOM - LEFT
			pie.operator("mesh.subdivide", text="Subdivide", icon='GRID').smoothness=0
			#3 - BOTTOM - RIGHT  
			pie.operator("mesh.select_mode", text="Face", icon='FACESEL').type = 'FACE'   
			
			   
		
		elif bpy.context.area.type == 'VIEW_3D' and bpy.context.object.mode == 'SCULPT':  
			
			
			#4 - LEFT
			pie.operator("paint.brush_select",text="Grab",icon='BRUSH_SNAKE_HOOK').sculpt_tool='SNAKE_HOOK'
			#6 - RIGHT
			pie.operator("paint.brush_select",text="Strips",icon='BRUSH_CLAY_STRIPS').sculpt_tool='CLAY_STRIPS'
			#2 - BOTTOM
			pie.operator("paint.brush_select",text="Mask",icon='BRUSH_MASK').sculpt_tool='MASK'
			#8 - TOP
			pie.operator("paint.brush_select",text="Pinch",icon='BRUSH_PINCH').sculpt_tool='PINCH'
			#7 - TOP - LEFT 
			pie.operator("paint.brush_select",text="Scrape",icon='BRUSH_SCRAPE').sculpt_tool='SCRAPE'
			#9 - TOP - RIGHT
			pie.operator("paint.brush_select",text="Crease",icon='BRUSH_CREASE').sculpt_tool='CREASE'
			#1 - BOTTOM - LEFT
			invertmask = pie.operator("paint.mask_flood_fill", text="Invert Mask",icon='BRUSH_TEXDRAW')
			invertmask.mode = 'INVERT'
			#3 - BOTTOM - RIGHT
			clearmask = pie.operator("paint.mask_flood_fill", text="Fill Mask",icon='BRUSH_TEXMASK')
			clearmask.mode = 'VALUE'
			clearmask.value = 1

			   








# =======================
# Keypress Q
# =======================
class PieQuickSecondary(Menu):
	# label is displayed at the center of the pie menu.
	bl_label = "Select Mode"
	bl_idname = "mesh.quickpie_secondary"

	def draw(self, context):
		layout = self.layout
		
		pie = layout.menu_pie()


		if bpy.context.area.type == 'VIEW_3D' and not bpy.context.object:

			#4 - LEFT
			pie.operator("object.lamp_add", text="Point", icon='LAMP_POINT').type = 'POINT'
			#6 - RIGHT
			pie.operator("mesh.primitive_plane_add", text="Plane", icon='MESH_PLANE')
			#2 - BOTTOM
			pie.operator("mesh.primitive_monkey_add", text="Monkey", icon='MESH_MONKEY')
			#8 - TOP
			pie.operator("screen.redo_last", text="Setting", icon='SETTINGS')
			#7 - TOP - LEFT 
			pie.operator("object.lamp_add", text="Sun", icon='LAMP_SUN').type = 'SUN'
			#9 - TOP - RIGHT
			pie.operator("mesh.primitive_cube_add", text="Cube", icon='MESH_CUBE')
			#1 - BOTTOM - LEFT
			pie.operator("object.camera_add", icon='OUTLINER_OB_CAMERA')
			#3 - BOTTOM - RIGHT
			pie.operator("mesh.primitive_circle_add", text="Circle", icon='MESH_CIRCLE')
	  
	  
		elif bpy.context.area.type == 'VIEW_3D' and bpy.context.object.mode == 'OBJECT':

			#4 - LEFT
			pie.operator("object.lamp_add", text="Point", icon='LAMP_POINT').type = 'POINT'
			#6 - RIGHT
			pie.operator("mesh.primitive_plane_add", text="Plane", icon='MESH_PLANE')
			#2 - BOTTOM
			pie.operator("mesh.primitive_monkey_add", text="Monkey", icon='MESH_MONKEY')
			#8 - TOP
			pie.operator("screen.redo_last", text="Setting", icon='SETTINGS')
			#7 - TOP - LEFT 
			pie.operator("object.lamp_add", text="Sun", icon='LAMP_SUN').type = 'SUN'
			#9 - TOP - RIGHT
			pie.operator("mesh.primitive_cube_add", text="Cube", icon='MESH_CUBE')
			#1 - BOTTOM - LEFT
			pie.operator("object.camera_add", icon='OUTLINER_OB_CAMERA')
			#3 - BOTTOM - RIGHT
			pie.operator("mesh.primitive_circle_add", text="Circle", icon='MESH_CIRCLE')			
			
			
		elif bpy.context.object.mode == 'EDIT':


			#4 - LEFT
			pie.operator("gpencil.surfsk_add_surface", 'Add BSurface', icon='OUTLINER_OB_SURFACE')
			#6 - RIGHT
			pie.operator("mesh.looptools_relax",text="Relax", icon='PARTICLE_PATH')
			#2 - BOTTOM
			pie.operator("mesh.looptools_flatten",text="Flatten",icon='FACESEL')
			#8 - TOP
			pie.operator("screen.redo_last", text="Setting", icon='SETTINGS')
			#7 - TOP - LEFT 
			pie.operator("mesh.solidify",text="Solidify",icon='MOD_SOLIDIFY')
			#9 - TOP - RIGHT
			pie.operator("mesh.looptools_circle",text="Circle", icon='MESH_CIRCLE')
			#1 - BOTTOM - LEFT
			pie.operator("mesh.select_all", text="Inverse", icon='RESTRICT_SELECT_ON').action = 'INVERT'
			#3 - BOTTOM - RIGHT   
			pie.operator("mesh.looptools_space",text="Space",icon='PARTICLE_POINT')
			


		elif bpy.context.area.type == 'VIEW_3D' and bpy.context.object.mode == 'SCULPT': 
	
			
			#4 - LEFT
			pie.operator("brush.curve_preset", icon='SMOOTHCURVE', text="Smooth").shape = 'SMOOTH'
			#6 - RIGHT
			pie.operator("brush.curve_preset", icon='NOCURVE', text="Max").shape = 'MAX'
			#2 - BOTTOM
			pie.operator("sculpt.optimize",icon='GROUP_VERTEX')
			
			#8 - TOP
			pie.operator("brush.curve_preset", icon='SHARPCURVE', text="Sharp").shape = 'SHARP'
			#7 - TOP - LEFT 
			pie.operator("brush.curve_preset", icon='SPHERECURVE', text="Round").shape = 'ROUND'
			#9 - TOP - RIGHT
			pie.operator("brush.curve_preset", icon='LINCURVE', text="Line").shape = 'LINE'
			#1 - BOTTOM - LEFT
			if context.sculpt_object.use_dynamic_topology_sculpting:
				pie.operator("sculpt.dynamic_topology_toggle", icon='X', text="Disable Dyntopo")
			else:
				pie.operator("enable.dyntopo", icon='MESH_DATA', text="Enable Dyntopo")
			#3 - BOTTOM - RIGHT
			pie.operator("sculpt.symmetrizemoinsx", text="Mirror", icon='MOD_MIRROR')
			
			


# =======================
# Keypress X
# =======================
class PieQuickDel(Menu):
	# label is displayed at the center of the pie menu.
	bl_label = "Select Mode"
	bl_idname = "mesh.quickpie_del"

	def draw(self, context):
		layout = self.layout
		
		pie = layout.menu_pie()
		


		if bpy.context.area.type == 'VIEW_3D' and not bpy.context.object:

			#4 - LEFT
			pie.operator("clear.all", text="Clear Transformations", icon='EMPTY_DATA')
			#6 - RIGHT
			pie.operator("object.delete", text="Delete Object", icon='X')
			#2 - BOTTOM
			pie.operator("object.parent_clear", text="Clear Parent", icon='POSE_DATA').type = 'CLEAR_KEEP_TRANSFORM'
			#8 - TOP
			pie.operator("group.objects_remove_all", text="Remove from Group", icon='GROUP')
			#7 - TOP - LEFT 
			#9 - TOP - RIGHT
			#1 - BOTTOM - LEFT
			#3 - BOTTOM - RIGHT  
	  
	  
		elif bpy.context.area.type == 'VIEW_3D' and bpy.context.object.mode == 'OBJECT':

			#4 - LEFT
			pie.operator("clear.all", text="Clear Transformations", icon='EMPTY_DATA')
			#6 - RIGHT
			pie.operator("object.delete", text="Delete Object", icon='X')
			#2 - BOTTOM
			pie.operator("object.parent_clear", text="Clear Parent", icon='POSE_DATA').type = 'CLEAR_KEEP_TRANSFORM'
			#8 - TOP
			pie.operator("group.objects_remove_all", text="Remove from Group", icon='GROUP')
			#7 - TOP - LEFT 
			#9 - TOP - RIGHT
			#1 - BOTTOM - LEFT
			#3 - BOTTOM - RIGHT  
			
			
		elif bpy.context.object.mode == 'EDIT':


			#4 - LEFT
			pie.operator("mesh.dissolve_verts",text="Dissolve Verts",icon='VERTEXSEL')
			#6 - RIGHT
			pie.operator("mesh.delete", text="Delete Verts",icon='VERTEXSEL').type = 'VERT'
			#2 - BOTTOM
			pie.operator("mesh.delete_edgeloop", text="Delete Edge Loops",icon='LOOPSEL')
			#8 - TOP
			pie.operator("mesh.dissolve_limited",text="Clean Up",icon='LAYER_ACTIVE')
			#7 - TOP - LEFT 
			pie.operator("mesh.dissolve_edges",text="Dissolve Edges",icon='EDGESEL')
			#9 - TOP - RIGHT
			pie.operator("mesh.delete", text="Delete Edges",icon='EDGESEL').type = 'EDGE'
			#1 - BOTTOM - LEFT
			pie.operator("mesh.dissolve_faces",text="Dissolve Faces",icon='FACESEL')
			#3 - BOTTOM - RIGHT   
			pie.operator("mesh.delete", text="Delete Faces",icon='FACESEL').type = 'FACE'
			


		elif bpy.context.area.type == 'VIEW_3D' and bpy.context.object.mode == 'SCULPT': 
	
			
			#4 - LEFT
			showmask = pie.operator("paint.hide_show", text="Show Masked",icon='SOLID')
			showmask.action ='SHOW'
			showmask.area = 'MASKED'
			#6 - RIGHT
			hidemask = pie.operator("paint.hide_show", text="Hide Mask",icon='BRUSH_TEXMASK')
			hidemask.action = 'HIDE'
			hidemask.area = 'MASKED'
			#2 - BOTTOM
			clearmask = pie.operator("paint.mask_flood_fill", text="Clear Mask",icon='BRUSH_TEXFILL')
			clearmask.mode = 'VALUE'
			clearmask.value = 0
			#8 - TOP
			#7 - TOP - LEFT 
			#9 - TOP - RIGHT
			#1 - BOTTOM - LEFT
			#3 - BOTTOM - RIGHT












addon_keymaps = []
def register():
	
			
	bpy.utils.register_class(PieQuick)
	bpy.utils.register_class(PieQuickSecondary)
	bpy.utils.register_class(PieQuickDel)
	#Objects
	bpy.utils.register_class(AutoSmooth)
	bpy.utils.register_class(ApplyTransformAll)
	bpy.utils.register_class(ClearAll)
	bpy.utils.register_class(EnableDyntopo)
	bpy.utils.register_class(SculptSymmetrizeMoinsX) 
	bpy.utils.register_class(JoinObject) 
	bpy.utils.register_class(BoolUnion)
	bpy.utils.register_class(BoolDiff)
	
	bpy.mifthTools = dict()
		
	bpy.utils.register_module(__name__) 

	bpy.types.Scene.mifthTools = PointerProperty(
		name="Mifth Tools Variables",
		type=MFTProperties,
		description="Mifth Tools Properties"
	)
		
	wm = bpy.context.window_manager
	
	if wm.keyconfigs.addon:
			
		# Key SPACEBAR
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new("wm.call_menu_pie","NUMPAD_1","PRESS", alt=True)
		kmi.properties.name ="mesh.quickpie"
		
		# Key Q
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new("wm.call_menu_pie","NUMPAD_2","PRESS", alt=True)
		kmi.properties.name ="mesh.quickpie_secondary"  
		
		# Key X
		km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
		kmi = km.keymap_items.new("wm.call_menu_pie","NUMPAD_3","PRESS", alt=True)
		kmi.properties.name ="mesh.quickpie_del" 
		
		
			  
		  

def unregister():
	bpy.utils.unregister_module(__name__)
	
	bpy.utils.unregister_class(PieQuick)
	bpy.utils.unregister_class(PieQuickSecondary)
	bpy.utils.unregister_class(PieQuickDel)
	#Objects
	bpy.utils.unregister_class(AutoSmooth)
	bpy.utils.unregister_class(ApplyTransformAll)
	bpy.utils.unregister_class(ClearAll)
	bpy.utils.unregister_class(EnableDyntopo)
	bpy.utils.unregister_class(SculptSymmetrizeMoinsX)
	bpy.utils.unregister_class(JoinObject) 
	bpy.utils.unregister_class(BoolUnion)
	bpy.utils.unregister_class(BoolDiff)


if __name__ == "__main__":
	register()