# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
	"name": "Rig Switcher",
	"category": "Cenda Tools",
	"author": "Cenek Strichel",
	"description": "Switching between Riggigng modes",
	"location": "Add to Input: wm.call_menu + VIEW3D_MT_rig_switcher_menu & Armature Setting: Rig Switcher Settings",
	"version": (1, 0, 4),
	"blender": (2, 79, 0),
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
}

import bpy
from bpy.props import BoolProperty

################################################################################################################
# MENU #
########
class RigSwitcherMenu(bpy.types.Menu):

	bl_label = ""
	bl_idname = "VIEW3D_MT_rig_switcher_menu"

	def draw(self, context):
		
		pie = self.layout.menu_pie()
		
		# LEFT BOX
		box = pie.split().column()
		row = box.split(align=True)
		
		
		# WIRE / SOLID #########################################################			
		if ( bpy.context.active_object != None and bpy.context.active_object.type == 'ARMATURE' ):
			
			state = bpy.context.object.draw_type
			
			if (state == 'WIRE') :
				current_text = 'Solid Draw Type'
			else:
				current_text = 'Wire Draw Type'
				
		# no icon
		else :
			current_text = "Wire \ Solid Draw Type"
			
		box.scale_y = 1.4
		box.operator("cenda.solid_wire", icon="BONE_DATA", text = current_text )


		# WIRE on SHADED #########################################################
		box.operator("cenda.wire_on_shaded", icon = "WIRE" )
		
		
		# POSE / REST #########################################################
		# checkbox for active Armature
		
		if ( bpy.context.active_object != None and bpy.context.active_object.type == 'ARMATURE' ):
			
			state = bpy.context.object.data.pose_position
			
			if (state == 'POSE') :
				current_text = 'Rest Position'
				current_icon = 'ARMATURE_DATA'
			else:
				current_text = 'Pose Position'
				current_icon = 'POSE_DATA'
				
		# no icon
		else :
			current_text = "Pose \ Rest"
			current_icon = 'BLANK1'
			
		box.operator("cenda.pose_rest_toggle", icon = current_icon, text = current_text )


		# SHAPES #########################################################
		# checkbox for active Armature
		
		if ( bpy.context.active_object != None and bpy.context.active_object.type == 'ARMATURE' ):
			
			state = bpy.context.object.data.show_bone_custom_shapes
			
			if (state) :
				current_icon = 'CHECKBOX_HLT'
			else:
				current_icon = 'CHECKBOX_DEHLT'
				
		# no icon
		else :
			current_icon = "SCULPT_DYNTOPO"
				
		box.operator("cenda.shapes_toggle", icon= current_icon )
		
		
		
		# NAMES #########################################################
		if ( bpy.context.active_object != None and bpy.context.active_object.type == 'ARMATURE' ):
			
			state = bpy.context.object.data.show_names
			
			if (state) :
				current_icon = 'CHECKBOX_HLT'
			else:
				current_icon = 'CHECKBOX_DEHLT'
				
		# no icon
		else :
			current_icon = "SCULPT_DYNTOPO"
			
			
		box.operator("cenda.names_toggle", icon = current_icon )
		

		##########################################################
		# PIE MENU #
		##########################################################
		# RIGHT
		pie.operator("cenda.edit",icon="EDITMODE_HLT")

		# DOWN
		pie.operator("cenda.pose",icon="POSE_HLT")

		# WEIGHT
		pie.operator("cenda.weight",icon="WPAINT_HLT")
		
		# MODE
		pie.separator()
		pie.operator("cenda.object",icon="OBJECT_DATAMODE", text ="Object & Select").selectHierarchy = True
		pie.separator()
	#	pie.operator("cenda.object",icon="OBJECT_DATAMODE").selectHierarchy = False
		pie.operator("cenda.parent",icon="GROUP_BONE")
		
'''		
def ShowBoxButton(boolType, stateTest, text, icon, text1, icon1, text2, icon2):
	
	if ( bpy.context.active_object != None and bpy.context.active_object.type == 'ARMATURE' ):
		
		if (boolType == stateTest) :
			current_text = text1
			current_icon = icon1
		else:
			current_text = text2
			current_icon = icon2
				
	# no icon
	else :
		current_text = text
		current_icon = icon
		
	return(current_text, current_icon) # tuple
'''			
			
## BOX OPTIONS ##############################################################################################################
class PoseRestToggle(bpy.types.Operator):

	"""Pose \ Rest Toggle"""
	bl_idname = "cenda.pose_rest_toggle"
	bl_label = "Pose \ Rest"

	def execute(self, context):
		
		if( not ActiveArmature(self) ):
			return {'FINISHED'}
		
		# switch
		if( bpy.context.object.data.pose_position == 'POSE') :
			bpy.context.object.data.pose_position = 'REST'
			self.report({'INFO'},"REST position")
			
		else :
			bpy.context.object.data.pose_position = 'POSE'
			self.report({'INFO'},"POSE position")
			
		return {'FINISHED'}


class ShapesToggle(bpy.types.Operator):

	"""Shapes Toggle"""
	bl_idname = "cenda.shapes_toggle"
	bl_label = "Shapes"

	def execute(self, context):

		if( not ActiveArmature(self) ):
			return {'FINISHED'}
			
		# switch
		bpy.context.object.data.show_bone_custom_shapes = not bpy.context.object.data.show_bone_custom_shapes
			
		return {'FINISHED'}


class SolidWireToggle(bpy.types.Operator):

	"""Draw Solid or Wire"""
	bl_idname = "cenda.solid_wire"
	bl_label = "Wire \ Solid Bone"

	def execute(self, context):

		if( not ActiveArmature(self) ):
			return {'FINISHED'}
			
		# switch
		if( bpy.context.object.draw_type == 'SOLID'):
			bpy.context.object.draw_type = 'WIRE'
		else:
			bpy.context.object.draw_type = 'SOLID'
			
		return {'FINISHED'}


class NamesToggle(bpy.types.Operator):

	"""Names Toggle"""
	bl_idname = "cenda.names_toggle"
	bl_label = "Names"

	def execute(self, context):

		if( not ActiveArmature(self) ):
			return {'FINISHED'}
			
		# switch
		bpy.context.object.data.show_names = not bpy.context.object.data.show_names
			
		return {'FINISHED'}


################################################################################################################
# OPTIONS #
###########
class ObjectMode(bpy.types.Operator):

	"""Set Object Mode"""
	bl_idname = "cenda.object"
	bl_label = "Object Mode"

	selectHierarchy = BoolProperty(name="SelectHierarchy",default=False)
	
	def execute(self, context):

		if( not ActiveArmature(self) ):
			return {'FINISHED'}
		
		HideLODs(False)
		DeselectableAllMeshes( False ) # mesh is selectable

		obj = context.object
		
		SetArmatureLayer( obj.PoseModeIndexLayer )
		SetBoneSettings( "OCTAHEDRAL", False, False, False, True )	
		
		bpy.ops.object.mode_set(mode='OBJECT')
		
		if(self.selectHierarchy):
			bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
			
		SetModeChild( "OBJECT", True )
		
		return {'FINISHED'}
	
	
class EditMode(bpy.types.Operator):

	"""Change Armature"""
	bl_idname = "cenda.edit"
	bl_label = "Edit Mode"

	def execute(self, context):

		if( not ActiveArmature(self) ):
			return {'FINISHED'}
		
		HideLODs()
		DeselectableAllMeshes()

		SetArmatureLayer(None)
		SetBoneSettings( "OCTAHEDRAL", True, True, False, False )
		
		bpy.ops.object.mode_set(mode='EDIT')
		
		obj = context.object
		
		if(obj.SolidDrawEdit):
			obj.draw_type = 'SOLID'
		else:
			obj.draw_type = 'WIRE'
			
		SetModeChild( "OBJECT", True )
		
		return {'FINISHED'}


class WeightMode(bpy.types.Operator):

	"""Weight Paint Mode for Skinning"""
	bl_idname = "cenda.weight"
	bl_label = "Weight Paint"

	def execute(self, context):
	
		if( not ActiveArmature(self) ):
			return {'FINISHED'}
		
		HideLODs()
		DeselectableAllMeshes(False)

		obj = context.object

		SetArmatureLayer( obj.DefIndexLayer )
		SetBoneSettings( "STICK", True, False, False, False )

		bpy.ops.object.mode_set(mode='POSE')
#		bpy.context.space_data.viewport_shade = 'SOLID'
		
		SetModeChild( "WEIGHT_PAINT", False )
		
		return {'FINISHED'}  
	
	  
class PoseMode(bpy.types.Operator):

	"""Pose Mode for Animation"""
	bl_idname = "cenda.pose"
	bl_label = "Pose Mode"

	def execute(self, context):

		if( not ActiveArmature(self) ):
			return {'FINISHED'}
		
		HideLODs()
		DeselectableAllMeshes( True )

		obj = context.object

		SetArmatureLayer( obj.PoseModeIndexLayer )
		SetBoneSettings( "STICK" if obj.Stick else 'OCTAHEDRAL', obj.XRay, False, False, True )		

		bpy.ops.object.mode_set(mode='POSE')
#		bpy.context.space_data.viewport_shade = 'MATERIAL'
		
		# solid or wire by setting
		if(obj.SolidDraw):
			obj.draw_type = 'SOLID'
		else:
			obj.draw_type = 'WIRE'
			
		# turn off Wire
		for child in bpy.context.active_object.children :
			child.show_all_edges = False
			child.show_wire = False
			
		SetModeChild( "OBJECT", True )	
		
		return {'FINISHED'}


class ParentMode(bpy.types.Operator):

	"""Parent mode"""
	bl_idname = "cenda.parent"
	bl_label = "Parent Mode"

	def execute(self, context):

		if( not ActiveArmature(self) ):
			return {'FINISHED'}
		
		HideLODs()
		DeselectableAllMeshes( False ) # objs are selectable

		obj = context.object

		SetArmatureLayer( None )
		SetBoneSettings( "OCTAHEDRAL", True, False, False, False )		
		
		bpy.ops.object.mode_set(mode='POSE')
		obj.draw_type = 'SOLID'
	
		# turn off Wire
		for child in bpy.context.active_object.children :
			child.show_all_edges = False
			child.show_wire = False
			
		SetModeChild( "OBJECT", True )
			
		return {'FINISHED'}
	

######################################################################################
# SETUP BONES by Prefix ##############################################################
######################################################################################
class SetupBones(bpy.types.Operator):

	"""Move bones to Layers and set Deform parameter by prefix"""
	bl_idname = "cenda.setup_bones"
	bl_label = "Setup Bones by Prefix"

	def execute(self, context):
		
		ob = bpy.context.object
		
		bpy.ops.object.mode_set(mode='EDIT') # I need switch to edit
		SetArmatureLayer(None) # all layer visible
		
		
		if ob.type == 'ARMATURE':
    
			armature = ob.data
			
			for bone in armature.edit_bones :
				
				# Deformation
				if ( ('DEF-' in bone.name) or ('DEF_' in bone.name) ) :	
					SetBoneLayer( bone, ob.DefIndexLayer )
					bone.use_deform = True

				# Mechanical
				if ( ('MCH-' in bone.name) or ('MCH_' in bone.name) ) :
					SetBoneLayer( bone, ob.MechIndexLayer )
					bone.use_deform = False
					
				# Deform parameter for adding (must be on end)	
				if(bone.use_deform):
					SetBoneLayer( bone, ob.DefIndexLayer, onlyAdd = True )
			
				
		return {'FINISHED'}
	
	
### PANEL SETTING #######################################################################################
class RigSwitcherSettings(bpy.types.Panel):

	bl_label = "Rig Switcher Settings"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(cls, context):
		if not context.armature:
			return False
		return True

	def draw(self, context):

		layout = self.layout
		obj = context.object
		
		box = layout.box()
		box.row().prop( obj, "PoseModeIndexLayer")
		
		box.row().prop( obj, "XRay")
		box.row().prop( obj, "Stick")
		if(not obj.Stick):
			box.row().prop( obj, "SolidDraw")
			
		box = layout.box()
		box.row().prop( obj, "DefIndexLayer")
		box.row().prop( obj, "MechIndexLayer")
		
		box = layout.box()
		box.row().prop( obj, "SolidDrawEdit")
		box.row().operator( "cenda.setup_bones" )


class IntGroup(bpy.types.PropertyGroup):
	
	pose_default = [ True, False, False, False, False, False, False, False, 
False, False, False, False, False, False, False, False, 
False, False, False, False, False, False, False, False, 
False, False, False, False, False, False, False, False ]
	
	def_default = [ False, True, False, False, False, False, False, False, 
False, False, False, False, False, False, False, False, 
False, False, False, False, False, False, False, False, 
False, False, False, False, False, False, False, False ]

	mech_default = [ False, False, True, False, False, False, False, False, 
False, False, False, False, False, False, False, False, 
False, False, False, False, False, False, False, False, 
False, False, False, False, False, False, False, False ]
	
	bpy.types.Object.PoseModeIndexLayer = bpy.props.BoolVectorProperty(name = "Pose", default = pose_default, size = 32, description = "No Prefix", subtype = "LAYER" )
	bpy.types.Object.SolidDraw = bpy.props.BoolProperty( name = "Solid Draw", description = "", default = False )
	bpy.types.Object.XRay = bpy.props.BoolProperty( name = "X-Ray", description = "", default = False )
	bpy.types.Object.Stick = bpy.props.BoolProperty( name = "Stick Bone", description = "", default = False )
	
	bpy.types.Object.DefIndexLayer = bpy.props.BoolVectorProperty(name = "Deform", default = def_default, size = 32, description = "Prefix \"DEF-\"", subtype = "LAYER" )
	bpy.types.Object.MechIndexLayer = bpy.props.BoolVectorProperty(name = "Mechanic", default = mech_default, size = 32, description = "Prefix \"MCH-\"", subtype = "LAYER" )
	
	bpy.types.Object.SolidDrawEdit = bpy.props.BoolProperty( name = "Solid Draw with Edit Mode", description = "", default = False )


## HELPERS ########################################################################################
def SetModeChild( modeType, previousActive = True):

	previousSaved = bpy.context.active_object

	# set weight
	for child in bpy.context.active_object.children :	
	
		bpy.context.scene.objects.active = child
		bpy.ops.object.mode_set( mode=modeType )
		
	if(previousActive):
		bpy.context.scene.objects.active = previousSaved
			
			
def SetBoneSettings( drawType = "OCTAHEDRAL", show_x_ray = False, show_axes = False, show_names = False, show_bone_custom_shapes = False ):
	
	bpy.context.object.data.draw_type = drawType
	bpy.context.object.show_x_ray = show_x_ray
	bpy.context.object.data.show_axes = show_axes
	bpy.context.object.data.show_names = show_names
	bpy.context.object.data.show_bone_custom_shapes = show_bone_custom_shapes
	
	
def DeselectableAllMeshes( state = True ):	
	
	SelectableRecursive( bpy.context.active_object, state )
		
			
def SelectableRecursive(ob, state):
	
    # armature is active
	for child in ob.children :
	
		####################################
		child.hide_select = state
		
		# deselect all child meshes
		if(state):
			child.select = False # deselect object
			
		# for recursive		
		SelectableRecursive(child, state) 


def HideLODs( state = True ):
	
	for child in bpy.context.active_object.children :
		if( 
		child.name.endswith("_LOD1") or 
		child.name.endswith("_LOD2") or 
		child.name.endswith("_LOD3") or 
		child.name.endswith("_LOD4") or 
		child.name.endswith("_LOD5")
		):
			if(state):
				
				child.hide = True
				
				try:
					# decimate first
					child.modifiers["Decimate"].show_viewport = False
					child.modifiers["Armature"].show_viewport = False
					
				except:
					pass

			else:
				
				child.hide = False
				
				try:
					# decimate first
					child.modifiers["Decimate"].show_viewport = True
					child.modifiers["Armature"].show_viewport = True
					
				except:
					pass


class WireAllMeshes(bpy.types.Operator):

	"""Set selected object to Wire mode"""
	bl_idname = "cenda.wire_on_shaded"
	bl_label = "Wire on Shaded"
	
	def execute(self, context):
		
		# mesh is active
		if(bpy.context.object.type == "MESH"):
			bpy.context.object.show_wire = not bpy.context.object.show_wire
			bpy.context.object.show_all_edges = not bpy.context.object.show_all_edges
			
		# armature is active	
		else:

			childMeshes = bpy.context.active_object.children
			
			# no children mesh
			if( len(childMeshes) == 0 ):
				
				firstMesh = False
				
				for obj in bpy.data.objects :
					if(obj.type == "MESH"):
						
						if(not firstMesh):
							state = obj.show_wire # by first mesh
							firstMesh = True
							
						obj.show_all_edges = not state
						obj.show_wire = not state
					
			# set all child meshes		
			else:	
				
				state = childMeshes[0].show_wire # by first mesh
				
				for child in childMeshes :		
					child.show_all_edges = not state
					child.show_wire = not state
		
			
		return {'FINISHED'}	

	
# check or find working armature		
def ActiveArmature(self):
	
	# Hidden is selected
	if( bpy.context.active_object != None ) :
		
		# Armature is selected
		if ( bpy.context.active_object.type == 'ARMATURE' ):
			return True
		
		# Armature is parent (Mesh is selected)
		elif ( bpy.context.active_object.parent == 'ARMATURE' ):
			bpy.context.scene.objects.active = bpy.context.active_object.parent
			return True
			
		# Finding Armature
		else :
			for ob in bpy.context.scene.objects:
				if ob.type == 'ARMATURE' :
					# hidden is skipped
					if ob.hide == True :
						continue
					
					else:
						bpy.context.scene.objects.active = bpy.data.objects[ob.name]
						return True
				
	# no armature in scene			
	self.report({'ERROR'}, "No armature found (must be visible)")
		
	return False


# default show all, set layer visibility
def SetArmatureLayer( indexLayer ):

	obj = bpy.context.object
	
	# show all
	if( indexLayer == None ):
		for i in range(32):
			bpy.context.object.data.layers[i] = True
			
	# show only something		
	else:
		# first true
		for i in range(32):	
			# show by index
			if(indexLayer[i] == True) :
				obj.data.layers[i] = True
				
		# then false
		for i in range(32):	
			# show by index
			if(indexLayer[i] == False) :
				obj.data.layers[i] = False
		
					
def SetBoneLayer( bone, indexLayer, onlyAdd = False ):

	# first true
	for i in range(32):
		if(indexLayer[i] == True) :
			bone.layers[i] = True
			
	# then false		
	if(not onlyAdd):		
		for i in range(32):
			if(indexLayer[i] == False) :
				bone.layers[i] = False


					
#######################################################
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()