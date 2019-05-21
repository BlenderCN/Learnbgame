
# To do:
# [x] Sort out image names (DIFF only)
# [x] Apply SUB_PARAMS for nav lights
# [ ] Apply SUB_PARAMS for dock paths
# [x] Delete superfluous SUB_PARAMS objects
# [x] "001" for nav lights (Tur_P1Mothership.dae)
# [x] Nav Lights parents
# [x] Merge Goblins
# [ ] Implementation of import options:
#	  - Import mesh only
# [x] Handle spurious materials, for example "default" in Tur_P1Mothership.dae
# [ ] Remove "_ncl1" tags - is this a good idea?
# [x] Handle "-pivot" objects created by 3DSMax
#
#
# [o] = implemented, not confirmed
# [x] = tested, complete
#

import os
import xml.etree.ElementTree
import math
import mathutils
import bpy

ET = xml.etree.ElementTree

###############################################################################
# TEST CASE SUMMARY
###############################################################################

# Gearbox examples
# Kad_Swarmer.dae"              # ok
# Tur_P1Mothership.dae"         # ok
# Kad_Swarmer_local.dae"        # ok
# Kad_FuelPod.DAE"              # ok
# Tai_Interceptor.DAE"          # ok (badge not checked)
# Tai_MultiGunCorvette.DAE"     # ok (badge not checked)
# Hgn_Carrier.dae"              # ok when split normals turned off
# Asteroid_3.dae"               # ok
# Kus_SupportFrigate.dae"       # ok
# planetexample_Light.DAE"      # ok
# Example_light.DAE"            # ok

# RODOH examples
# meg_gehenna_2.dae"            # ok
# hgn_shipyard.dae"             # ok when split normals turned off - flames come in with no parents..
# hgn_battlecruiser.dae         # internal error setting array - subMesh.from_pydata(Verts,[],faceTris)
# hgn_gunturret.dae"            # internal error setting array - subMesh.from_pydata(Verts,[],faceTris)
# hgn_torpedofrigate.dae"       # ok when split normals turned off
# meg_bentus.dae"               # OK
# vgr_carrier.dae"              # ok when split normals turned off
# vgr_mothership.dae"           # ok when split normals turned off

# Blender-generated TRP ships
# trp_marinefrigate.dae"        # ok
# trp_assaultfrigate.dae"       # ok
# trp_ioncannonfrigate.dae"     # ok

# 3DSMax-generated TRP ships
# trp_resourcecollector.DAE"    # ok
# trp_carrier.DAE"              # ok
# trp_assaultcorvette.DAE"      # ok
# trp_probe.DAE"                # ok
# trp_interceptor.DAE"          # ok
# trp_scout.DAE"                # ok
# trp_attackbomber.DAE"         # ok
# trp_sensdisprobe.DAE          # ok
# trp_proximitysensor.DAE       # ok

###############################################################################
###############################################################################
###############################################################################

#############
#DAE Schemas#
#############

#Just defining all the DAE attributes here so the processing functions are more easily readable

#Asset Schemas
DAEUpAxis = "{http://www.collada.org/2005/11/COLLADASchema}up_axis"

#Utility Schemas
DAENode = "{http://www.collada.org/2005/11/COLLADASchema}node"
DAETranslation = "{http://www.collada.org/2005/11/COLLADASchema}translate"
DAEInit = "{http://www.collada.org/2005/11/COLLADASchema}init_from"
DAEInput = "{http://www.collada.org/2005/11/COLLADASchema}input"
DAEFloats = "{http://www.collada.org/2005/11/COLLADASchema}float_array"
DAESource = "{http://www.collada.org/2005/11/COLLADASchema}source"
DAEInstance = "{http://www.collada.org/2005/11/COLLADASchema}instance_geometry"

#Material Schemas
DAELibMaterials = "{http://www.collada.org/2005/11/COLLADASchema}library_materials"
DAEMaterials = "{http://www.collada.org/2005/11/COLLADASchema}material"
DAELibEffects = "{http://www.collada.org/2005/11/COLLADASchema}library_effects"
DAEfx = "{http://www.collada.org/2005/11/COLLADASchema}effect"
DAELibImages = "{http://www.collada.org/2005/11/COLLADASchema}library_images"
DAEimage = "{http://www.collada.org/2005/11/COLLADASchema}image"
DAEDiff = "{http://www.collada.org/2005/11/COLLADASchema}diffuse"
DAETex = "{http://www.collada.org/2005/11/COLLADASchema}texture"
DAEProfile = "{http://www.collada.org/2005/11/COLLADASchema}profile_COMMON"
DAETechnique = "{http://www.collada.org/2005/11/COLLADASchema}technique"
DAEPhong = "{http://www.collada.org/2005/11/COLLADASchema}phong"

#Geometry Schemas
DAEGeo = "{http://www.collada.org/2005/11/COLLADASchema}geometry"
DAEMesh = "{http://www.collada.org/2005/11/COLLADASchema}mesh"
DAEVerts = "{http://www.collada.org/2005/11/COLLADASchema}vertices"
DAETris = "{http://www.collada.org/2005/11/COLLADASchema}triangles"
DAEp = "{http://www.collada.org/2005/11/COLLADASchema}p"

#Animation Schemas
DAELibAnims = "{http://www.collada.org/2005/11/COLLADASchema}library_animations"
DAEAnim = "{http://www.collada.org/2005/11/COLLADASchema}animation"
DAEChannel = "{http://www.collada.org/2005/11/COLLADASchema}channel"

###########
#Functions#
###########

def makeTextures(name, DAEPath, path):
	name = name.rstrip("-image")
	# Sort out the image path (it could be absolute, local or relative)
	print("makeTextures()")
	print("************************************************")
	DAEPath = DAEPath + "/"
	print(DAEPath)
	print("Image path from DAE file:")
	print(path)
	if "\\" in DAEPath:
		print("Found \\ in DAEPath!")
		DAEPath = DAEPath.replace("\\","/")
	if "\\" in path:
		print("Found \\ in path!")
		path = path.replace("\\","/")
		print(path)
	if "/" in path:
		if ".." in path:
			print("This is a relative path...")
			DAEPath_elements = DAEPath.split("/")
			print(DAEPath_elements)
			del DAEPath_elements[-1]
			print(DAEPath_elements)
			path_elements = path.split("/")
			print(path_elements)
			for i in path_elements:
				if i == "..":
					del DAEPath_elements[-1]
			image_path = ""
			print("Building full path...")
			print("-----------")
			for j in DAEPath_elements:
				image_path = image_path + j + "/"
				print(image_path)
			for k in path_elements:
				if k != ".." and k != ".":
					print(image_path)
					print(len(image_path))
					if image_path[len(image_path)-1] != "/":
						image_path = image_path + "/" + k
					else:
						image_path = image_path + k
					print(image_path)
			print("-----------")
		else:
			if path.startswith("./"):
				print("This is a local path with ./")
				image_path = DAEPath + path[2:]
			else:
				print("This is an absolute path")
				image_path = path
	else:
		print("This is a file name only")
		image_path = DAEPath + "/" + path
	
	# Now we have an image path ready to load
	print("Processed image path:")
	print(image_path)
	
	# But sometimes it is not the DIFF (e.g. Kad_Swarmer)...
	# So correct the image file name
	if "DIFF" not in image_path:
		print("switching file name to DIFF...")
		image_path = image_path[0:len(image_path)-8] + "DIFF" + ".tga"
		print(image_path)
	print(name)
	# And correct the image name (IMG[xxx_DIFF]_FMT[...)
	if "DIFF" not in name:
		print("switching image name to DIFF...")
		# This is a lazy way of doing it, but it works - may no longer be necessary (Dom2 28-NOV-2016)
		name = name.replace("_DIFX]","_DIFF]")
		name = name.replace("_GLOW]","_DIFF]")
		name = name.replace("_GLOX]","_DIFF]")
		name = name.replace("_NORM]","_DIFF]")
		name = name.replace("_PAIN]","_DIFF]")
		name = name.replace("_REFL]","_DIFF]")
		name = name.replace("_REFX]","_DIFF]")
		name = name.replace("_SPEC]","_DIFF]")
		name = name.replace("_SPEX]","_DIFF]")
		name = name.replace("_STRP]","_DIFF]")
		name = name.replace("_TEAM]","_DIFF]")
		print(name)
	# Now get the image
	bpy.data.textures.new(name, 'IMAGE')	
	bpy.data.textures[name].image = bpy.data.images.load(image_path)
	image_file_name = image_path.split("/")[len(image_path.split("/"))-1]
	print(image_file_name)
	bpy.data.images[image_file_name].name = name
	print("************************************************")
	
def makeMaterials(name, textures):
	bpy.data.materials.new(name)
	if len(textures) > 0:	
		bpy.data.materials[name].texture_slots.add()
		texture_name = textures[0]
		if "_DIFF" not in texture_name:
			print("!- makeMaterials() could not find '_DIFF' in texture_name: " + texture_name)
			texture_name = texture_name.replace("_DIFX]","_DIFF]")
			texture_name = texture_name.replace("_GLOW]","_DIFF]")
			texture_name = texture_name.replace("_GLOX]","_DIFF]")
			texture_name = texture_name.replace("_NORM]","_DIFF]")
			texture_name = texture_name.replace("_PAIN]","_DIFF]")
			texture_name = texture_name.replace("_REFL]","_DIFF]")
			texture_name = texture_name.replace("_REFX]","_DIFF]")
			texture_name = texture_name.replace("_SPEC]","_DIFF]")
			texture_name = texture_name.replace("_SPEX]","_DIFF]")
			texture_name = texture_name.replace("_STRP]","_DIFF]")
			texture_name = texture_name.replace("_TEAM]","_DIFF]")
			print("!- makeMaterials() tried to fix it, now using: " + texture_name)
		bpy.data.materials[name].texture_slots[0].texture = bpy.data.textures[texture_name]
	else:
		print("!- makeMaterials() was given an empty list of textures for mat " + name)

def meshBuilder(matName, Verts, Normals, UVCoords, vertOffset, normOffset, UVoffsets, pArray, smooth):
	print("meshBuilder() - Building "+matName)
	print(UVoffsets)
	subMesh = bpy.data.meshes.new(matName)
	ob = bpy.data.objects.new(subMesh.name, subMesh)
	
	#split <p> array to get just the face data
	faceIndices = []
	for i in range(0, len(pArray)):
		faceIndices.append(pArray[i][vertOffset])
	faceTris = [faceIndices[i:i+3] for i in range(0,len(faceIndices),3)]
	subMesh.from_pydata(Verts,[],faceTris)
	if matName is not "None":
		print("meshBuilder() - appending material '" + matName + "' to submesh '" + subMesh.name + "'")
		subMesh.materials.append(bpy.data.materials[matName.lstrip("#")])
	
	if smooth:
		normIndices = []
		for i in range(0, len(pArray)):
			this_norm_index = mathutils.Vector(Normals[pArray[i][normOffset]])
			normIndices.append(this_norm_index) # This line causes problems for some DAEs, not yet traced why (Dom2 28-NOV-2016)
		
		print("Splitting normals...")
		subMesh.normals_split_custom_set(normIndices)
	print("Smoothing mesh...")
	subMesh.use_auto_smooth = True
	
	print("Adding UVs...")
	#Add UVs
	if len(UVCoords) > 0:
		for coords in range(0,len(UVoffsets)):
			subMesh.uv_textures.new()
	
			meshUV = []
			for p in range(0, len(pArray)):
				meshUV.append(UVCoords[coords][pArray[p][UVoffsets[coords]]])
	
			for l in range(0,len(subMesh.uv_layers[coords].data)):
				subMesh.uv_layers[coords].data[l].uv = meshUV[l]
	
	print("Linking objects...")
	bpy.context.scene.objects.link(ob)
	
	return ob

#If it ain't broke don't fix it. This function written by Dom2
def CreateJoint(jnt_name,jnt_locn,jnt_rotn,jnt_context, dock_seg_type):
	
	if 'navl' not in jnt_name.lower():
		#print("Creating joint" + jnt_name)
		this_jnt = bpy.data.objects.new(jnt_name, None)
		jnt_context.scene.objects.link(this_jnt)
		pi = math.pi
		this_jnt.rotation_euler.x = jnt_rotn[0] * (pi/180.0)
		this_jnt.rotation_euler.y = jnt_rotn[1] * (pi/180.0)
		this_jnt.rotation_euler.z = jnt_rotn[2] * (pi/180.0)
		this_jnt.location.x = float(jnt_locn[0])
		this_jnt.location.y = float(jnt_locn[1])
		this_jnt.location.z = float(jnt_locn[2])
	
		if "dock" in jnt_name.lower():
			if jnt_name.lower() is not "hold_dock":
				jointProps = jnt_name.split("_")
			
				for p in jointProps:
					if "flags" in p.split("[")[0].lower():
						print(p)
						this_jnt["Flags"] = p[6:].rstrip("]")
					if "link" in p.split("[")[0].lower():
						print(p)
						this_jnt["Link"] = p[5:].rstrip("]")
					if "fam" in p.split("[")[0].lower():
						this_jnt["Fam"] = p[4:].rstrip("]")
					if "mad" in p.split("[")[0].lower():
						print(p)
						this_jnt["MAD"] = p.lstrip("MAD[").rstrip("]") 
			
		if "seg" in jnt_name.lower():
			jointProps = jnt_name.split("_")
			this_jnt.empty_draw_type = dock_seg_type
		
			for p in jointProps:
				if "flags" in p.split("[")[0].lower():
					this_jnt["Flags"] = p[6:].rstrip("]")
				if "spd" in p.split("[")[0].lower():
					this_jnt["Speed"] = float(p[4:].rstrip("]"))
				if "tol" in p.split("[")[0].lower():
					this_jnt.empty_draw_size = float(p[4:].rstrip("]"))
	else:
		navl_name = "NAVL[" + jnt_name.split("]")[0].split("[")[1] + "]"
		print("-------------------------------------------")
		print("nav light name = " + navl_name)
		this_lamp = bpy.data.lamps.new(navl_name,'POINT')
		
		this_jnt = bpy.data.objects.new(navl_name,this_lamp)
		jnt_context.scene.objects.link(this_jnt)
		pi = math.pi
		this_jnt.rotation_euler.x = jnt_rotn[0]*(pi/180.0)
		this_jnt.rotation_euler.y = jnt_rotn[1]*(pi/180.0)
		this_jnt.rotation_euler.z = jnt_rotn[2]*(pi/180.0)
		this_jnt.location.x = float(jnt_locn[0])
		this_jnt.location.y = float(jnt_locn[1])
		this_jnt.location.z = float(jnt_locn[2])
		
		this_lamp["name"] = navl_name
		lampProps = jnt_name.split("]_")
		
		if 'type' not in jnt_name.lower():
			this_lamp["Type"] = 'default'
		for p in lampProps:
			p = p + "]"
			print(p)
			if p.split("[")[0].lower() == 'sz':
				this_lamp.energy = float(p[3:].rstrip("]").split("]")[0])
			if p.split("[")[0].lower() == 'ph':
				this_lamp["Phase"] = float(p[3:].rstrip("]").split("]")[0])
			if p.split("[")[0].lower() == 'fr':
				this_lamp["Freq"] = float(p[3:].rstrip("]").split("]")[0])
			if p.split("[")[0].lower() == 'col':
				rgb = p[4:].rstrip("]").split("]")[0].split(',')
				this_lamp.color[0] = float(rgb[0])
				this_lamp.color[1] = float(rgb[1])
				this_lamp.color[2] = float(rgb[2])
			if p.split("[")[0].lower() == 'dist':
				this_lamp.distance = float(p[5:].rstrip("]").split("]")[0])
			if p.split("[")[0].lower() == 'flags':
				this_lamp["Flags"] = p[6:].rstrip("]").split("]")[0]
			if p.split("[")[0].lower() == 'type':
				this_lamp["Type"] = p[5:].rstrip("]").split("]")[0]
		print("-------------------------------------------")
	return this_jnt

def CheckForChildren(node,context,root):
	print("-----------------------------------------------------------------")
	for item in node:
		# If there is a child node...
		if "node" in item.tag:
			print(item.attrib["name"])
			# Nav lights need name modification
			if "NAVL[" in item.attrib["name"]:
				print("Found child nav light:")
				print(bpy.data.objects.get(item.attrib["name"]))
				navlight_name = item.attrib["name"].split("]")[0] + "]"
				print(navlight_name)
				child_navlight = bpy.data.objects.get(navlight_name)
				child = bpy.data.objects[navlight_name]
				parent = bpy.data.objects[node.attrib["name"][0:63]]
				child.parent = parent
				CheckForNavSubParams(item,navlight_name,context) # check for children of nav light (RODOH generates "SUB_PARAMS" as children of the nav light)
			# Node without a name is a mesh(?)
			elif bpy.data.objects.get(item.attrib["name"][0:63]) is None: # Do we need the [0:63]???
				for i in item:
					if "instance_geometry" in i.tag:
						url = i.attrib["url"].lstrip("#")
						for geo in root.iter(DAEGeo):
							if geo.attrib["id"] == url:
								child = bpy.data.objects[geo.attrib["name"]]
								parent = bpy.data.objects[node.attrib["name"][0:63]]
								child.parent = parent
								CheckForChildren(item,context,root)
			# Anything else is a standard joint
			else:
				child = bpy.data.objects[item.attrib["name"][0:63]]
				parent = bpy.data.objects[node.attrib["name"][0:63]]
				child.parent = parent
				CheckForChildren(item,context,root)

def CheckForNavSubParams(navlight,name,context):
	this_lamp = bpy.data.lamps[name]
	# Check each item under the nav light for "SUB_PARAMS"
	for item in navlight:
		if "node" in item.tag:
			if "SUB_PARAMS" in item.attrib["name"]:
				# Check each item under SUB_PARAMS for parameters
				for param in item:
					if "node" in param.tag:
						p = param.attrib["name"]
						if p.split("[")[0].lower() == 'sz':
							this_lamp.energy = float(p[3:].rstrip("]").split("]")[0])
						if p.split("[")[0].lower() == 'ph':
							this_lamp["Phase"] = float(p[3:].rstrip("]").split("]")[0])
						if p.split("[")[0].lower() == 'fr':
							this_lamp["Freq"] = float(p[3:].rstrip("]").split("]")[0])
						if p.split("[")[0].lower() == 'col':
							rgb = p[4:].rstrip("]").split("]")[0].split(',')
							this_lamp.color[0] = float(rgb[0])
							this_lamp.color[1] = float(rgb[1])
							this_lamp.color[2] = float(rgb[2])
						if p.split("[")[0].lower() == 'dist':
							this_lamp.distance = float(p[5:].rstrip("]").split("]")[0])
						if p.split("[")[0].lower() == 'flags':
							this_lamp["Flags"] = p[6:].rstrip("]").split("]")[0]
						if p.split("[")[0].lower() == 'type':
							this_lamp["Type"] = p[5:].rstrip("]").split("]")[0]
			# Delete SUB_PARAMS object and all child objects... (perhaps do this later, as a final step to delete everything that is not a child of the root nodes (e.g. Root Col, Root LOD[0], etc.)
	print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

################
#XML Processing#
################

#More Dom2 code here
def ImportDAE(DAEfullpath, smoothing_opt, dock_opt, goblins_opt):
	tree = ET.parse(DAEfullpath)
	root = tree.getroot()

	DAE_file_path = os.path.dirname(DAEfullpath)
	
	# if up axis = Y and ROOT_LOD[0] has no X rotation, need to rotate about X by 90...
	y_up = False
	for axis in root.iter(DAEUpAxis): # find all <up_axis> in the file
		if axis.text == "Y_UP":
			for n in root.iter(DAENode): # find all <node> in the file
				if "ROOT_LOD[0]" in n.attrib["name"]:
					for par in n:
						if "rotate" in par.tag:
							if "sid" in par.attrib: # sometimes there are "dummy" <rotate> tags with no "sid"... (-pivot, from 3DSMax)
								if "rotateX" in par.attrib["sid"]:
									if float(par.text.split()[3]) < 89:
										print("This is probably a RODOH dae - Y axis = up and there is no x rotation on ROOT_LOD[0]")
										y_up = True
	
	print(" ")
	print("CREATING JOINTS")
	print(" ")

	# Create joints
	for joint in root.iter(DAENode): # find all <node> in the file
		# Joint name
		joint_name = joint.attrib["name"]
		print(joint_name)
		# Joint location
		joint_location = joint.find(DAETranslation)
		if joint_location == None:
			joint_location = ['0','0','0'] # If there is no translation specified, default to 0,0,0
		else:
			joint_location = joint_location.text.split()
		# Joint rotation
		joint_rotationX = 0 # \
		joint_rotationY = 0 #      |-- If there is no rotation specified, default to 0
		joint_rotationZ = 0 #     /
		for rot in joint:
			if "rotate" in rot.tag:
				if "sid" in rot.attrib: # sometimes there are "dummy" <rotate> tags with no "sid"... (-pivot, from 3DSMax)
					if "rotateX" in rot.attrib["sid"]:
						if y_up and "ROOT" in joint_name:
							#joint_rotationX = (math.pi/2.0) + float(rot.text.split()[3]) # if "y up", rotate everything by +90deg
							joint_rotationX = float(rot.text.split()[3])
						else:
							joint_rotationX = float(rot.text.split()[3])
					elif "rotateY" in rot.attrib["sid"]:
						joint_rotationY = float(rot.text.split()[3])
					elif "rotateZ" in rot.attrib["sid"]:
						joint_rotationZ = float(rot.text.split()[3])
		joint_rotation = [joint_rotationX,joint_rotationY,joint_rotationZ]
		# Joint or mesh?
		is_joint = True
		for item in joint:
			if "instance_geometry" in item.tag:
				print("this is a mesh:" + item.attrib["url"])
				is_joint = False
		# If this is a joint, make it!
		if is_joint:
			CreateJoint(joint_name, joint_location,joint_rotation,bpy.context, dock_opt)
			
	#My code starts here - DL

	#find textures and create them
	for img in root.find(DAELibImages):
		# We use attrib["id]" here because RODOH DAEs have "name"s that do not match their "id"s
		#  this means we will lose the _FMT[] tag but we will have to live with that for now...
		#
		# Example (to solve we would need to add the _FMT[] tag back on at the <texture> stage:
		# <image id="IMG[Hgn_MarineFrigate_Front_DIFF]-image" name="IMG[Hgn_MarineFrigate_Front_DIFF]_FMT[DXT5]">
		# <texture texture="IMG[Hgn_MarineFrigate_Front_DIFF]-image">
		#
		# Let's have a warning message just to let the user know:
		if img.attrib["id"].rstrip("-image") != img.attrib["name"]:
			print("This appears to be a RODOH DAE. _FMT[] tags will be lost from textures - sorry!")
		makeTextures(img.attrib["id"],DAE_file_path,img.find(DAEInit).text.lstrip("file://"))

	#Make materials based on the Effects library
	for fx in root.find(DAELibEffects).iter(DAEfx):
		matname = fx.attrib["name"]
		matTextures = []
		
		# Just look for the <diffuse> tag - don't care about the other image files
		for d in fx.iter(DAEDiff):
			t = d.find(DAETex)
			print(d)
			print(d.tag)
			if t is not None:
				matTextures.append(t.attrib["texture"].rstrip("-image"))
			# !- may not need to do replacing "DIFF" now... -!
		
		makeMaterials(matname, matTextures)

	#Find the mesh data and split the coords into 2D arrays

	for geo in root.iter(DAEGeo):
		meshName = geo.attrib["name"]
		mesh = geo.find(DAEMesh)
		
		blankMesh = bpy.data.meshes.new(meshName)
		ob = bpy.data.objects.new(meshName, blankMesh)
		bpy.context.scene.objects.link(ob)
		
		print(meshName)	
		
		UVs = []
		
		for source in mesh.iter(DAESource):
			if "position" in source.attrib["id"].lower():
				rawVerts = [float(i) for i in source.find(DAEFloats).text.split()]
			
			if "normal" in source.attrib["id"].lower():
				rawNormals = [float(i) for i in source.find(DAEFloats).text.split()]
			
			if "uv" in source.attrib["id"].lower():
				rawUVs = [float(i) for i in source.find(DAEFloats).text.split()]
				coords = [rawUVs[i:i+2] for i in range(0, len(rawUVs),2)]
				UVs.append(coords)
					
		vertPositions = [rawVerts[i:i+3] for i in range(0, len(rawVerts),3)]
		meshNormals = [rawNormals[i:i+3] for i in range(0, len(rawNormals),3)]
		
		subMeshes = []
		
		for tris in mesh.iter(DAETris):
			if "material" in tris.attrib:
				material = tris.attrib["material"]
				print("Found <triangles> with material " + material)
			else:
				material = "None"
				
			maxOffset = 0
			UVOffsets = []
			vertOffset = 0
			normOffset = 0
			for inp in tris.iter(DAEInput):
				if int(inp.attrib["offset"]) > maxOffset:
					maxOffset = int(inp.attrib["offset"])
				if inp.attrib["semantic"].lower() == "texcoord":
					UVOffsets.append(int(inp.attrib["offset"]))
				if inp.attrib["semantic"].lower() == "vertex":
					vertOffset = int(inp.attrib["offset"])
				if inp.attrib["semantic"].lower() == "normal":
					normOffset =  int(inp.attrib["offset"])
			if tris.find(DAEp).text is not None:
				splitPsoup = [int(i) for i in tris.find(DAEp).text.split()]
				pArray = [splitPsoup[i:i+(maxOffset+1)] for i in range(0, len(splitPsoup),(maxOffset+1))]
				# Only build the submesh if it actually has triangles
				subMeshes.append(meshBuilder(material, vertPositions, meshNormals, UVs, vertOffset, normOffset, UVOffsets, pArray, smoothing_opt))
		
		#Combines the material submeshes into one mesh
		for obs in subMeshes:
			obs.select = True
		
		ob.select = True
		bpy.context.scene.objects.active = ob
		bpy.ops.object.join()
		ob.data.use_auto_smooth = True
		bpy.ops.object.editmode_toggle()
		bpy.ops.mesh.remove_doubles()
		bpy.ops.object.editmode_toggle()
		ob.select = False
		
	# Sort out hierarchy
	for child in root:
		if "library_visual_scenes" in child.tag:
			for grandchild in child:
				if "visual_scene" in grandchild.tag:
					for node in grandchild:
						if "node" in node.tag:
							CheckForChildren(node,bpy.context,root)

	###############################
	#							 #
	###############################

	#Animations	
	animLib = root.find(DAELibAnims)
	for anim in animLib.iter(DAEAnim):
		#print(animLib.getchildren().index(anim))
		if anim.find(DAESource):
			frames = []
			locs = []
			#bpy.data.objects[animLib[(animLib.getchildren().index(anim)-1)].attrib["name"]].select = True
			for source in anim.iter(DAESource):
				# print(source.attrib["id"])
				if "input" in source.attrib["id"].lower():
					frames = [float(i) for i in source.find(DAEFloats).text.split()]
					#print(frames)
				elif "output" in source.attrib["id"].lower():
					locs = [float(i) for i in source.find(DAEFloats).text.split()]
					#print(locs)
			#bpy.data.objects[(anim.find(DAEChannel).attrib["target"].split("/")[0])].select = True
			channel = anim.find(DAEChannel).attrib["target"].split("/")[1]
			anim_target = anim.find(DAEChannel).attrib["target"].split("/")[0]
			if anim_target in bpy.data.objects:
				object = bpy.data.objects[anim_target]
				for f in range(0, len(frames)):
					currentFrame = (frames[f]*bpy.context.scene.render.fps)
					if "translate" in channel.lower():
						if "x" in channel.lower():
							object.location.x =  locs[f]
							object.keyframe_insert(data_path = 'location',index = 0, frame = currentFrame)
						elif "y" in channel.lower():
							object.location.y =  locs[f]
							object.keyframe_insert(data_path = 'location',index = 1, frame = currentFrame)
						elif "z" in channel.lower():
							object.location.z =  locs[f]
							object.keyframe_insert(data_path = 'location',index = 2, frame = currentFrame)
					elif "rotatex" in channel.lower():
						object.rotation_euler.x = locs[f]*(math.pi/180)
						object.keyframe_insert(data_path = 'rotation_euler',index = 0, frame = currentFrame)
					elif "rotatey" in channel.lower():
						object.rotation_euler.y = locs[f]*(math.pi/180)
						object.keyframe_insert(data_path = 'rotation_euler',index = 1, frame = currentFrame)
					elif "rotatez" in channel.lower():
						object.rotation_euler.z = locs[f]*(math.pi/180)
						object.keyframe_insert(data_path = 'rotation_euler',index = 2, frame = currentFrame)
			else:
				print("!- Warning: could not find " + anim_target + " for creating animations...")
	
	###############################
	# Check for Goblins and merge #
	###############################
	
	if goblins_opt:
		print("CHECKING FOR GOBLINS")
		
		goblins_present = False
		
		bpy.ops.object.select_all(action='DESELECT')
		
		for x in bpy.data.objects:
			if x.name.startswith("GOBG["):
				goblins_present = True
				print(x.name + " is a goblin mesh")
				x.select = True
			elif x.name.startswith("MULT[") and "LOD[0]" in x.name:
				print(x.name + " is the LOD[0] mesh I will use to combine Goblins...")
				LOD0 = x

		if goblins_present:
			print("Merging goblins...")
			LOD0.select = True
			bpy.context.scene.objects.active = LOD0
			bpy.ops.object.join()
	
	# Last thing, delete any HODOR param objects lying around
	#  and correct joint names for SEG[] and DOCK[]
	
	print("CHECKING FOR HODOR PARAMS")
	
	bpy.ops.object.select_all(action='DESELECT')
	
	naughty_words = ["SUB_PARAMS",
					"Ph[",
					"Sz[",
					"Fr[",
					"Flags[",
					"Dist[",
					"Col[",
					"Sect["
					]
	
	for x in bpy.data.objects:
		# SUB_PARAM objects need deleting
		if x.parent == None:
			for w in naughty_words:
				if x.name.startswith(w):
					print(x.name + " is a HODOR SUB_PARAM and will be deleted...")
					x.select = True
					bpy.ops.object.delete()
		# SEG[] and DOCK[] names need parameters stripping
		if x.name.startswith("SEG["):
			x.name = "SEG[" + x.name.split("]")[0].split("[")[1] + "]"
		elif x.name.startswith("DOCK["):
			x.name = "DOCK[" + x.name.split("]")[0].split("[")[1] + "]"
	
	# If y up, need to rotate all root jnts by +90deg
	bpy.ops.object.select_all(action='DESELECT')
	if y_up:
		for y in bpy.data.objects:
			if "ROOT_" in y.name:
				y.select = True
				bpy.ops.transform.rotate(value=(math.pi/2.0), axis=(1, 0, 0))
				bpy.ops.object.select_all(action='DESELECT')
	
	print("DAE file successfully imported!")


def ImportLOD0(DAEfullpath, smoothing_opt):
	tree = ET.parse(DAEfullpath)
	root = tree.getroot()
	
	if "\\" in DAEfullpath:
		LOD0Name_ent = DAEfullpath.rstrip("dae").rstrip("DAE").rstrip(".").split("\\")
	else:
		LOD0Name_ent = DAEfullpath.rstrip("dae").rstrip("DAE").rstrip(".").split("\\")
	LOD0Name = LOD0Name_ent[len(LOD0Name_ent)-1]
	
	print("Importing LOD[0] mesh(es) only...")
	print(LOD0Name)
	
	#Find the mesh data and split the coords into 2D arrays
	
	LOD0_mesh = 0
		
	for geo in root.iter(DAEGeo):
		if "MULT[" in geo.attrib["name"] and "_LOD[0]" in geo.attrib["name"]:
			LOD0_mesh = LOD0_mesh + 1
			meshName = LOD0Name + "-" + str(LOD0_mesh)
			mesh = geo.find(DAEMesh)
			
			blankMesh = bpy.data.meshes.new(meshName)
			ob = bpy.data.objects.new(meshName, blankMesh)
			bpy.context.scene.objects.link(ob)
			
			print("Importing " + geo.attrib["name"] + " as: " + meshName)
			
			UVs = []
			
			for source in mesh.iter(DAESource):
				if "position" in source.attrib["id"].lower():
					rawVerts = [float(i) for i in source.find(DAEFloats).text.split()]
				
				if "normal" in source.attrib["id"].lower():
					rawNormals = [float(i) for i in source.find(DAEFloats).text.split()]
				
				if "uv" in source.attrib["id"].lower():
					rawUVs = [float(i) for i in source.find(DAEFloats).text.split()]
					coords = [rawUVs[i:i+2] for i in range(0, len(rawUVs),2)]
					UVs.append(coords)
						
			vertPositions = [rawVerts[i:i+3] for i in range(0, len(rawVerts),3)]
			meshNormals = [rawNormals[i:i+3] for i in range(0, len(rawNormals),3)]
			
			subMeshes = []
			
			for tris in mesh.iter(DAETris):
				# For LOD[0] visual mesh, no materials needed
				material = "None"
					
				maxOffset = 0
				UVOffsets = []
				vertOffset = 0
				normOffset = 0
				for inp in tris.iter(DAEInput):
					if int(inp.attrib["offset"]) > maxOffset:
						maxOffset = int(inp.attrib["offset"])
					if inp.attrib["semantic"].lower() == "texcoord":
						UVOffsets.append(int(inp.attrib["offset"]))
					if inp.attrib["semantic"].lower() == "vertex":
						vertOffset = int(inp.attrib["offset"])
					if inp.attrib["semantic"].lower() == "normal":
						normOffset =  int(inp.attrib["offset"])
				if tris.find(DAEp).text is not None:
					splitPsoup = [int(i) for i in tris.find(DAEp).text.split()]
					pArray = [splitPsoup[i:i+(maxOffset+1)] for i in range(0, len(splitPsoup),(maxOffset+1))]
					# Only build the submesh if it actually has triangles
					subMeshes.append(meshBuilder(material, vertPositions, meshNormals, UVs, vertOffset, normOffset, UVOffsets, pArray, smoothing_opt))
			
			#Combines the material submeshes into one mesh
			for obs in subMeshes:
				obs.select = True
			
			ob.select = True
			bpy.context.scene.objects.active = ob
			bpy.ops.object.join()
			ob.data.use_auto_smooth = True
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.remove_doubles()
			bpy.ops.object.editmode_toggle()
			ob.select = False
#
# end