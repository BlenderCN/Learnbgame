'''
	SimBlend, a Blender import module for SIMION ion trajectory data

	Copyright (C) 2013 - Physical and Theoretical Chemistry /
	Institute of Pure and Applied Mass Spectrometry
	of the University of Wuppertal, Germany


	This file is part of SimBlend

	SimBlend is free software: You may redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
	------------
	import_script.py

	This is the core of SimBlend.
	The blender plugin system calls the main method of "SimionToAnimation" upon startup

	Original author:  Dominik Sand
	Version: 0.1


	Sources that were used during the program creation:
	http://openbook.galileocomputing.de/
	http://docs.python.org/dev/library/argparse.html
	http://code.blender.org/index.php/2011/05/scripting-%E2%80%93-change-settings-the-fast-way/
	http://www.blender.org/documentation/blender_python_api_2_57_release/bpy.types.Operator.html
	http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Three_ways_to_create_objects
	http://blenderscripting.blogspot.de/2011/05/inspired-by-post-on-ba-it-just-so.html
	http://blenderartists.org/forum/showthread.php?237761-Blender-2-6-Set-keyframes-using-Python-script
	http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Materials_and_textures
	http://www.blender.org/documentation/248PythonDoc/
	http://www.blender.org/documentation/blender_python_api_2_59_0/bpy.types.Operator.html?highlight=invoke#bpy.types.Operator.invoke
	http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Actions_and_drivers
	http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Properties
	http://blenderscripting.blogspot.de/2011/05/blender-25-python-bezier-from-list-of.html
	http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Other_data_types
	http://www.blender.org/documentation/blender_python_api_2_56_5/bpy.ops.object.html
	http://blenderscripting.blogspot.de/2012/03/deleting-objects-from-scene.html
	http://blenderartists.org/forum/showthread.php?258778-How-to-select-object-by-name
	http://www.zoo-logique.org/3D.Blender/scripts_python/BPY/bpy.ops.object.html
	http://www.blender.org/forum/viewtopic.php?p=60837&sid=9cb468ddca11503b11b5089359945b23
	http://stackoverflow.com/questions/3657120/how-to-create-a-simple-mesh-in-blender-2-50-via-the-python-api
	http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Simulations
	http://code.metager.de/source/xref/blender/release/scripts/addons_contrib/io_import_sound_to_anim.py
	http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Materials_and_textures
	http://blenderscripting.blogspot.de/2011/06/vertex-colours.html
'''

import os
import bpy
import simblend.helper
from datetime import datetime
from mathutils import Vector
from math import floor
from .file_io import FileImport
from .ion import *
from .masslist_create import *
from .material_create import *
from .windowed import *

class SimionToAnimation(bpy.types.Operator):
	#Blender specific Information for display
	bl_idname = "simion.animation"
	bl_label = "Simion to Animation"
	#change properties to Filepath. Required for File Selectorcall
	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
	
	#call invoke  to set a file and point it to the attribute self.filepath
	def invoke(self,context,event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	#call execute after invoke
	def execute(self,context):
		path = os.getcwd()
		#self filepath contains information about selected file during invoke
		main(self.filepath)
		#expected return value for Execute function
		return{'FINISHED'}



def main(file):
	'''
	This is the main method of SimBlend

	Overview of calls:
	1. Create a list of Ions from the import file specified in the class call using the file_io.py
	2. Create a list of all different ion masses, contained in the Ionlist. For details see masslist_create.py
	3. Create a material for each existing ion mass in order to group the ions by mass and add a color for ions that have the corresponding masses. For details see material_create.py
	4. Calculate Maximum time of flight and Kinectic Energy which is in the Ionlist datastructure
	5. Create the windowed list from the Ionlist. For details see windowed.py
	6. Insert mesh and animation data for the selected animationtype using the windowed list
	7. Group created meshes using the material assigned. This causes a grouping by mass
	'''


	#select current scene and get variables for Size ,Frames and distance scale Factor
	scn = bpy.context.scene
	bpy.context.scene.frame_end = scn.frame_num
	size_fac = scn.obj_size
	dist_fac = scn.obj_distance
	tof_fac_max = 0
	KE_max = 0
	print("Start processing data:")
	print(datetime.now())
	print("File :", file)
	#function for getting data from Ionlist
	def get_xyz_mass(list,item,i):
		x = dist_fac*float(list[item].GetXYZ(i)[0])
		y = dist_fac*float(list[item].GetXYZ(i)[1])
		z = dist_fac*float(list[item].GetXYZ(i)[2])
		Ion_mass = str(list[item].GetMass(i))
		return (x,y,z,Ion_mass)
	Ionlist={}
	#create List : Masslist for Ionsurface material
	Masslist=[]
	f_src = open(file,'r')
	#turns  filedata to a processable List of Ions
	Ionlist = FileImport(f_src)
	#create a list of available Ionmass to create additional materials
	Masslist = masslist_create(Ionlist)
	#create new materials according to Masslist
	material_create(Masslist)
	#curvelist for Pathrendering operation
	curvelist=[]
	#calclate correct animation interpolation factor so that the data of the time of flight can be addressed to a frame
	for item in Ionlist:
		for i in range(0,Ionlist[item].datacount):
			if tof_fac_max < float(Ionlist[item].GetToF(i)):
				tof_fac_max = float(Ionlist[item].GetToF(i))
	#calculate maximum KE for visuals of pipes so that the vertex color operator calculates reasonable results
	for item in Ionlist:
		if(Ionlist[item].kinetic_energy):
			for i in range(0,Ionlist[item].datacount):
				if KE_max < float(Ionlist[item].GetKinetic_Energy(i)):
					KE_max = float(Ionlist[item].GetKinetic_Energy(i))
	#Timescaling factor = frame_num / tof_fac_max
	tof_fac_max = scn.frame_num / tof_fac_max
	#dependend on number of merges is also the number of points.Therefore a merged Ionlist is created
	windowed_list = windowedMeans(Ionlist, bpy.context.scene.number_merge)
	#create spheres if animation_type == 'sphere_id'
	if bpy.context.scene.animation_type == 'sphere_id':
		n = 0
		for item in Ionlist:
			xyz_mat_data = get_xyz_mass(windowed_list,item,0)
			bpy.ops.mesh.primitive_uv_sphere_add(size = size_fac,location = (xyz_mat_data[0],xyz_mat_data[1],xyz_mat_data[2]))
			#select created object
			ob = bpy.context.object
			ob.name = "Ion "+str(windowed_list[item].GetIonN())+" Sphere"
			me = ob.data
			#add material to Ion
			me.materials.append(bpy.data.materials.get(xyz_mat_data[3]))
			#add movement data to spheres 
			for i in range(0,windowed_list[item].datacount):
				xyz_mat_data = get_xyz_mass(windowed_list,item,i)
				time_coordinate = float(windowed_list[item].GetToF(i)) * tof_fac_max
				#add sphere at designated XYZ coordinate with "Timestamp"
				ob.location = (xyz_mat_data[0],xyz_mat_data[1],xyz_mat_data[2])
				#check if marker splat is active and let sphere fade and create a new one at the spot of the splat
				if(bpy.context.scene.ion_splat == True and windowed_list[item].events):
					if((int(windowed_list[item].GetEvent(i)) & 4) == 4):
						#shrink and create new object
						bpy.ops.transform.resize(value =(0,0,0))
						ob.keyframe_insert(data_path = "scale",frame = time_coordinate)
						#create new object on splat point and make it visable at splat
						bpy.ops.mesh.primitive_uv_sphere_add(size = size_fac,location = (xyz_mat_data[0],xyz_mat_data[1],xyz_mat_data[2]))
						splat = bpy.context.object
						splat.name = "Ion "+str(windowed_list[item].GetIonN())+" Sphere Splat"
						splat_me = splat.data
						splat_me.materials.append(bpy.data.materials.get(xyz_mat_data[3] + " red_splat"))
						bpy.ops.transform.resize(value =(0.001,0.001,0.001))
						splat.keyframe_insert(data_path = "scale",frame = 0 )
						splat.keyframe_insert(data_path = "scale",frame = time_coordinate-1)
						bpy.ops.transform.resize(value =(1000,1000,1000))
						splat.keyframe_insert(data_path = "scale",frame = time_coordinate )
					else:
						#keep size
						ob.keyframe_insert(data_path = "scale",frame = time_coordinate )
				#in order to shorten runtime , it needs to be checked if the data needs really to be written. The keyframe_insert is an expensive operation
				if(i < windowed_list[item].datacount - 1):
					if(floor(time_coordinate) != floor(float(windowed_list[item].GetToF(i+1))* tof_fac_max)):
						ob.keyframe_insert(data_path="location",frame = time_coordinate )
						n = n +1
		#note if processed file does not contain events and splat marker is active:
		if((bpy.context.scene.ion_splat == True) and not(windowed_list[item].events)):
			print("No Events parsed")
		print("Number of Insert Keyframe operations: ",n)
	#create path if animation_type == 'path_id'
	if bpy.context.scene.animation_type == 'path_id':
		for item in windowed_list:
			xyz_mat_data = get_xyz_mass(windowed_list,item,0)
			#create a curve at given x,y,z coordinates
			curvedata = bpy.data.curves.new(name= "Ion "+str(windowed_list[item].GetIonN())+" Path", type='CURVE')  
			curvedata.dimensions = '3D'
			objectdata = bpy.data.objects.new("Ion "+str(windowed_list[item].GetIonN())+" Path", curvedata)
			#curve origin , origin ist required so that data is not moved relative
			objectdata.location = (0,0,0)
			curvedata.materials.append(bpy.data.materials.get(xyz_mat_data[3]))
			#add texture to object if Tube modifier is active, therefore need to add a specific material and texture for each object
			bpy.context.scene.objects.link(objectdata)
			polyline = curvedata.splines.new('POLY')
			polyline.points.add(windowed_list[item].datacount-1)
			#create Bevel_object for the curve
			bpy.ops.mesh.primitive_circle_add(vertices=bpy.context.scene.number_pathverts)
			bpy.ops.object.convert( target = 'CURVE')
			bpy.ops.transform.resize(value = (size_fac,size_fac,size_fac))
			bev_obj = bpy.context.active_object
			#adjust size of the object
			curvedata.bevel_object = bev_obj
			curvelist.append(curvedata)
			#mandantory so that bevel object is not converted to Mesh and corrupts data
			bpy.ops.object.select_all(action = "DESELECT")
			for i in range(0,windowed_list[item].datacount):
				xyz_mat_data = get_xyz_mass(windowed_list,item,i)
				polyline.points[i].co = (xyz_mat_data[0],xyz_mat_data[1],xyz_mat_data[2],1)
			#converts curve to actual Mesh , therefore object needs to be selected and the context needs to be set to objectso operator can work
			ob = bpy.data.objects.get("Ion "+str(windowed_list[item].GetIonN())+" Path")
			ob.select = True
			bpy.context.scene.objects.active = ob
			bpy.ops.object.convert( target = 'MESH')
			#now that object is a mesh vertex can be painted
			if(bpy.context.scene.ion_tube_mod == True and KE_max != 0):
				vertice_window = 4 * bpy.context.scene.number_pathverts
				bpy.ops.mesh.vertex_color_add()
				for i in range(0, len(ob.data.vertex_colors['Col'].data),vertice_window):
					index_window = int(i / vertice_window)
					for j in range(i,i+ vertice_window):
						ob.data.vertex_colors['Col'].data[j].color[0] = 10*float(windowed_list[item].GetKinetic_Energy(index_window))/KE_max
						ob.data.vertex_colors['Col'].data[j].color[1] = 10*float(windowed_list[item].GetKinetic_Energy(index_window))/KE_max
						ob.data.vertex_colors['Col'].data[j].color[2] = 10*float(windowed_list[item].GetKinetic_Energy(index_window))/KE_max
			bpy.ops.object.select_all(action = "DESELECT")
			#remove Bevel Object, because its not needed anymore
			bev_obj.select = True
			bpy.ops.object.delete()
		if(bpy.context.scene.ion_tube_mod == True and KE_max == 0):
			print("No Kinetic energy parsed, so KE can not be displayed")
	if bpy.context.scene.animation_type == 'particle_id':
		for item in windowed_list:
			xyz_mat_data = get_xyz_mass(windowed_list,item,0)
			#create primitive verticle
			name = str("Ion "+windowed_list[item].GetIonN())+" Particle"
			me = bpy.data.meshes.new(name)
			#add start coordinates via the "data import method of mesh"
			me.from_pydata([(xyz_mat_data[0],xyz_mat_data[1],xyz_mat_data[2])],[],[])
			#add material  with the name defined
			me.materials.append(bpy.data.materials.get(xyz_mat_data[3]+ "Halo"))
			objectdata = bpy.data.objects.new(name,me)
			bpy.context.scene.objects.link(objectdata)
			#select mesh to add particle system
			ob = bpy.data.objects.get("Ion "+str(windowed_list[item].GetIonN())+" Particle")
			#set object center to origin
			ob.data.vertices[0].co = ([0,0,0])
			ob.select = True
			bpy.context.scene.objects.active = ob
			ob.keyframe_insert(data_path="location",frame = int(windowed_list[item].GetToF(0)))
			bpy.ops.object.particle_system_add()
			emitter = bpy.context.object
			particle = emitter.particle_systems[-1].settings
			#particle system setup
			particle.use_emit_random = False
			particle.emit_from = 'VERT'
			particle.normal_factor = 0
			#setup effectors for the particle system
			effect = particle.effector_weights
			effect.gravity = 0.0
			for i in range(0,windowed_list[item].datacount):
				xyz_mat_data = get_xyz_mass(windowed_list,item,i)
				time_coordinate = float(windowed_list[item].GetToF(i)) * tof_fac_max
				#add sphere at designated XYZ coordinate with "Timestamp"
				ob.location = (xyz_mat_data[0],xyz_mat_data[1],xyz_mat_data[2])
				ob.keyframe_insert(data_path="location",frame = time_coordinate)
	#final grouping of objects using same material
	#walk meshlist
	#check for material used
	# use this information to assign to new group
	# if no group present create new group
	for item in bpy.data.objects:
		bpy.ops.object.select_all(action = "DESELECT")
		current_mat = item.active_material
		if(current_mat != None):
			group_name = current_mat.name
			bpy.context.scene.objects.active = item
			item.select = True
			if bpy.data.groups.find(group_name) != -1:
				bpy.ops.object.group_link(group = str(group_name))
			else:
				bpy.ops.group.create( name = group_name)
	print ("Finished")
	print (datetime.now())