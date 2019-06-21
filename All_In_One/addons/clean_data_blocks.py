#====================== BEGIN GPL LICENSE BLOCK ======================
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
#======================= END GPL LICENSE BLOCK ========================


bl_info = {
	"name": "Clean Data-Blocks",
	"blender": (2, 80, 0),
	"author": "",
	"location": "View 3d > Object > Clear > Clean Data-Blocks",
	"description": ("Clear data-blocks that have zero users."),
	"category": "Learnbgame",
}


import bpy


#############################################################################################
class VIEW3D_MT_ClearDataIdMenu(bpy.types.Menu):   
	bl_label = "Clean Data-Blocks"   
	bl_idname = "OBJECT_clear_data_id"
	
	def draw(self, context):
		layout = self.layout				
		#Actuator Operators
		
		layout.label(text="Data-Block Type")
		self.layout.separator()
			 
		self.layout.operator("clear.actions_id", text="Actions", icon='ANIM_DATA')#Done 					   
		self.layout.operator("clear.materials_id", text="Materials", icon='MATERIAL_DATA')#Done 
		self.layout.operator("clear.meshes_id", text="Meshes", icon='MESH_DATA')#Done
		self.layout.operator("clear.particles_id", text="Particles", icon='PARTICLES')#Done 	
		self.layout.operator("clear.cameras_id", text="Cameras", icon='CAMERA_DATA')#Done   	
		self.layout.operator("clear.images_id", text="Images", icon='IMAGE_DATA')#Done 
		self.layout.operator("clear.lights_id", text="Lights", icon='LIGHT_DATA')#Done   
		self.layout.operator("clear.sounds_id", text="Sounds", icon='SOUND')#Done   	
		self.layout.operator("clear.scenes_id", text="Scenes", icon='SCENE_DATA')#Done 
		self.layout.operator("clear.textures_id", text="Textures", icon='TEXTURE_DATA')#Done
		self.layout.operator("clear.node_groups_id", text="Node Groups", icon='NODETREE')#Done  	
		self.layout.operator("clear.curves_id", text="Curves", icon='CURVE_DATA')#Done  	
		self.layout.operator("clear.brushes_id", text="Brushes", icon='BRUSH_DATA')#Done	 
		self.layout.operator("clear.metaballs_id", text="Metaballs", icon='META_DATA')#Done 	
		self.layout.operator("clear.armatures_id", text="Armatures", icon='ARMATURE_DATA')#Done 
		self.layout.operator("clear.groups_id", text="Groups", icon='GROUP')#Done     
		self.layout.operator("clear.lattices_id", text="Lattices", icon='LATTICE_DATA')#Done					 
		self.layout.operator("clear.grease_pencil_id", text="Grease Pencil", icon='GREASEPENCIL')#Done 
		self.layout.operator("clear.collections_id", text="Collections", icon='GROUP')#Done  				 
		self.layout.operator("clear.fonts_id", text="Fonts", icon='FILE_FONT')#Done
		self.layout.operator("clear.light_probes_id", text="Light Probes", icon='LIGHTPROBE_CUBEMAP')#Done
		self.layout.operator("clear.worlds_id", text="Worlds", icon='WORLD_DATA')#Done

				  
def OBJECT_ClearDataIdMenu(self, context):
	self.layout.menu(VIEW3D_MT_ClearDataIdMenu.bl_idname) 	   


class VIEW3D_OT_ClearMaterials(bpy.types.Operator):
	"""Clear all materials that have zero users"""    
	bl_idname = "clear.materials_id"
	bl_label = "Materials"
	
	
	def execute(self, context):
		
		for material in bpy.data.materials:
			if material.users == 0:
				material.user_clear()
				bpy.data.materials.remove(material)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearMeshes(bpy.types.Operator):
	"""Clear all meshes that have zero users"""    
	bl_idname = "clear.meshes_id"
	bl_label = "Meshes"
	
	
	def execute(self, context):
		
		for meshes in bpy.data.meshes:
			if meshes.users == 0:
				meshes.user_clear()
				bpy.data.meshes.remove(meshes)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearParticles(bpy.types.Operator):
	"""Clear all particles that have zero users"""    
	bl_idname = "clear.particles_id"
	bl_label = "Particles"
	
	
	def execute(self, context):
		
		for particles in bpy.data.particles:
			if particles.users == 0:
				particles.user_clear()
				bpy.data.particles.remove(particles)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearCameras(bpy.types.Operator):
	"""Clear all cameras that have zero users"""	
	bl_idname = "clear.cameras_id"
	bl_label = "Cameras"
	
	
	def execute(self, context):
		
		for cameras in bpy.data.cameras:
			if cameras.users == 0:
				cameras.user_clear()
				bpy.data.cameras.remove(cameras)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearImages(bpy.types.Operator):
	"""Clear all images that have zero users"""    
	bl_idname = "clear.images_id"
	bl_label = "Images"
	
	
	def execute(self, context):
		
		for images in bpy.data.images:
			if images.users == 0:
				images.user_clear()
				bpy.data.images.remove(images)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearLights(bpy.types.Operator):
	"""Clear all lights that have zero users"""    
	bl_idname = "clear.lights_id"
	bl_label = "Lights"
	
	
	def execute(self, context):
		
		for lights in bpy.data.lights:
			if lights.users == 0:
				lights.user_clear()
				bpy.data.lights.remove(lights)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearSounds(bpy.types.Operator):
	"""Clear all sounds that have zero users"""    
	bl_idname = "clear.sounds_id"
	bl_label = "Sounds"
	
	
	def execute(self, context):
		
		for sounds in bpy.data.sounds:
			if sounds.users == 0:
				sounds.user_clear()
				bpy.data.sounds.remove(sounds)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearScenes(bpy.types.Operator):
	"""Clear all scenes that have zero users"""    
	bl_idname = "clear.scenes_id"
	bl_label = "Scenes"
	
	
	def execute(self, context):
		
		for scenes in bpy.data.scenes:
			if scenes.users == 0:
				scenes.user_clear()
				bpy.data.scenes.remove(scenes)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearTextures(bpy.types.Operator):
	"""Clear all textures that have zero users"""    
	bl_idname = "clear.textures_id"
	bl_label = "Textures"
	
	
	def execute(self, context):
		
		for textures in bpy.data.textures:
			if textures.users == 0:
				textures.user_clear()
				bpy.data.textures.remove(textures)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearNodeGroups(bpy.types.Operator):
	"""Clear all node groups that have zero users"""	
	bl_idname = "clear.node_groups_id"
	bl_label = "Node Groups"
	
	
	def execute(self, context):
		
		for node_groups in bpy.data.node_groups:
			if node_groups.users == 0:
				node_groups.user_clear()
				bpy.data.node_groups.remove(node_groups)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearCurves(bpy.types.Operator):
	"""Clear all curves that have zero users"""    
	bl_idname = "clear.curves_id"
	bl_label = "Curves"
	
	
	def execute(self, context):
		
		for curves in bpy.data.curves:
			if curves.users == 0:
				curves.user_clear()
				bpy.data.curves.remove(curves)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearBrushes(bpy.types.Operator):
	"""Clear all curves that have zero users"""    
	bl_idname = "clear.brushes_id"
	bl_label = "Brushes"
	
	
	def execute(self, context):
		
		for brushes in bpy.data.brushes:
			if brushes.users == 0:
				brushes.user_clear()
				bpy.data.brushes.remove(brushes)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearMetaballs(bpy.types.Operator):
	"""Clear all metaballs that have zero users"""    
	bl_idname = "clear.metaballs_id"
	bl_label = "Metaballs"
	
	
	def execute(self, context):
		
		for metaballs in bpy.data.metaballs:
			if metaballs.users == 0:
				metaballs.user_clear()
				bpy.data.metaballs.remove(metaballs)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearArmatures(bpy.types.Operator):
	"""Clear all armatures that have zero users"""    
	bl_idname = "clear.armatures_id"
	bl_label = "Armatures"
	
	
	def execute(self, context):
		
		for armatures in bpy.data.armatures:
			if armatures.users == 0:
				armatures.user_clear()
				bpy.data.armatures.remove(armatures)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearGreasePencil(bpy.types.Operator):
	"""Clear all grease pencil that have zero users"""    
	bl_idname = "clear.grease_pencil_id"
	bl_label = "Grease Pencil"
	
	
	def execute(self, context):
		
		for grease_pencil in bpy.data.grease_pencil:
			if grease_pencil.users == 0:
				grease_pencil.user_clear()
				bpy.data.grease_pencil.remove(grease_pencil)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearActions(bpy.types.Operator):
	"""Clear all actions that have zero users"""	
	bl_idname = "clear.actions_id"
	bl_label = "Actions"
	
	
	def execute(self, context):
		
		for actions in bpy.data.actions:
			if actions.users == 0:
				actions.user_clear()
				bpy.data.actions.remove(actions)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearGroups(bpy.types.Operator):
	"""Clear all groups that have zero users"""    
	bl_idname = "clear.groups_id"
	bl_label = "Groups"
	
	
	def execute(self, context):
		
		for groups in bpy.data.groups:
			if groups.users == 0:
				groups.user_clear()
				bpy.data.groups.remove(groups)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearLattices(bpy.types.Operator):
	"""Clear all lattices that have zero users"""    
	bl_idname = "clear.lattices_id"
	bl_label = "Lattices"
	
	
	def execute(self, context):
		
		for lattices in bpy.data.lattices:
			if lattices.users == 0:
				lattices.user_clear()
				bpy.data.lattices.remove(lattices)

		return {'FINISHED'}

class VIEW3D_OT_ClearCollections(bpy.types.Operator):
	"""Clear all collections that have zero users"""	
	bl_idname = "clear.collections_id"
	bl_label = "Collections"
	
	
	def execute(self, context):
		
		for collections in bpy.data.collections:
			if collections.users == 0:
				collections.user_clear()
				bpy.data.collections.remove(collections)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearFonts(bpy.types.Operator):
	"""Clear all fonts that have zero users"""    
	bl_idname = "clear.fonts_id"
	bl_label = "Fonts"
	
	
	def execute(self, context):
		
		for fonts in bpy.data.fonts:
			if fonts.users == 0:
				fonts.user_clear()
				bpy.data.fonts.remove(fonts)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearLightProbes(bpy.types.Operator):
	"""Clear all light probes that have zero users"""    
	bl_idname = "clear.light_probes_id"
	bl_label = "Light Probes"
	
	
	def execute(self, context):
		
		for lightprobes in bpy.data.light_probes:
			if lightprobes.users == 0:
				lightprobes.user_clear()
				bpy.data.light_probes.remove(lightprobes)

		return {'FINISHED'} 	  

class VIEW3D_OT_ClearWorlds(bpy.types.Operator):
	"""Clear all worlds that have zero users"""    
	bl_idname = "clear.worlds_id"
	bl_label = "Worlds"
	
	
	def execute(self, context):
		
		for worlds in bpy.data.worlds:
			if worlds.users == 0:
				worlds.user_clear()
				bpy.data.worlds.remove(worlds)

		return {'FINISHED'} 	  


classes = (
	VIEW3D_OT_ClearMaterials,
	VIEW3D_OT_ClearMeshes,
	VIEW3D_OT_ClearParticles,
	VIEW3D_OT_ClearCameras,
	VIEW3D_OT_ClearImages,
	VIEW3D_OT_ClearLights,
	VIEW3D_OT_ClearSounds,
	VIEW3D_OT_ClearScenes,
	VIEW3D_OT_ClearTextures,
	VIEW3D_OT_ClearNodeGroups,
	VIEW3D_OT_ClearCurves,
	VIEW3D_OT_ClearBrushes,
	VIEW3D_OT_ClearMetaballs,
	VIEW3D_OT_ClearArmatures,
	VIEW3D_OT_ClearGreasePencil,
	VIEW3D_OT_ClearActions,
	VIEW3D_OT_ClearGroups,
	VIEW3D_OT_ClearLattices,
	VIEW3D_OT_ClearCollections,
	VIEW3D_OT_ClearFonts,
	VIEW3D_OT_ClearLightProbes,
	VIEW3D_OT_ClearWorlds,

	VIEW3D_MT_ClearDataIdMenu,  				 
)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls) 

	bpy.types.VIEW3D_MT_object_clear.append(OBJECT_ClearDataIdMenu)
	
def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):    
		unregister_class(cls)

	bpy.types.VIEW3D_MT_object_clear.remove(OBJECT_ClearDataIdMenu)
	
if __name__ == "__main__":
	register()  					