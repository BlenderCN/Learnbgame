#TODO
#	* Get Parts list and grouping working (HIGH)
#	* LSynth and "404" handler (MED)

import os
from os import path
import math
import sqlite3
import bpy
from zipfile import ZipFile
#import tempfile
import xml.etree.ElementTree as ET

DEBUG = True

# Part list:
model_bricks = []
grouped_bricks = {}

# Generic function that forwards the file to the appropriate import function
def load_file(self, context):
	src_name, src_ext = os.path.splitext(self.filepath)
	if src_ext == '.ldr' or src_ext == '.dat':
		# If the file is LDraw, send to read_ldraw function
		read_ldraw(self, context, self.filepath)
	elif src_ext == '.lxf':
		# Lego Digital Designer file
		read_ldd(self, context, self.filepath)
# LDraw Line specification:
# 0   1     2  3 4 5 6 7 8 9 10 11 12 13  14
# 1 <color> x -z y a b c d e f  g  h  i <part file> (there is actually only one space between each value)

# LDraw Processing Function
def read_ldraw(self, context, src):
	# Debug: print ldraw file to import
	print(src)

	# Open the ldraw file:
	ldraw_file = open(src, "r")

	# If the file was successfully opened, continue processing:
	if ldraw_file.mode == "r":
		# Since LDraw is a line-based file, read in the whole file as lines:
		file_loc, file_name = os.path.split(src)
		ldraw_lines = ldraw_file.readlines()
		# Part counter:
		part_num = 1

		# Get the path of the parts library:
		addons_paths = bpy.utils.script_paths("addons")
		library_path = "library"
		for path in addons_paths:
			library_path = os.path.join(path, "io_scene_lego_importer/Library")
			if os.path.exists(library_path):
				break

		# Proccess each LDraw line:
		for item in ldraw_lines:
			# 3 unit array to store x, y, z transformations
			transform = [None] * 3

			# Split the data row into a proccessable array:
			col = item.split()

			# Skip any lines other than brick references
			if col[0] != "1":
				continue;

			# Get the part number:
			part, ext = col[14].split('.')

			# Debug: Print the part number
			part = part.lower()
			print("Part: " + part)

			# Transform the origin to the new location:
			transform[0] = float(col[5]) * float(col[2]) + float(col[6]) * float(col[3]) + float(col[7]) * float(col[4])
			transform[1] = float(col[8]) * float(col[2]) + float(col[9]) * float(col[3]) + float(col[10]) * float(col[4])
			transform[2] = float(col[11]) * float(col[2]) + float(col[12]) * float(col[3]) + float(col[13]) * float(col[4])

			# Decompose the transformation matrix to get the rotation:
			rot_x = math.atan2(float(col[12]), float(col[13]))
			rot_y = math.atan2(float(col[8]), float(col[5]))
			rot_z = math.atan2(float(col[11]), math.sqrt(float(col[12]) * float(col[12]) + float(col[13]) * float(col[13])))

			# Transform the origin to the new location in blender:
			pos_x = float(col[2]) * 0.01
			pos_y = float(col[4]) * 0.01
			pos_z = (-float(col[3]) * 0.01)

			# Debug: Print new position and the rotation in degrees:
			if DEBUG:
				print("pos x = " + str(pos_x))
				print("pos y = " + str(pos_y))
				print("pos z = " + str(pos_z))

				print("rot x = " + str(int(round(math.degrees(rot_x)))))
				print("rot y = " + str(int(round(math.degrees(rot_y)))))
				print("rot z = " + str(int(round(math.degrees(rot_z)))))

			# Select the correct resolution from the import settings:
			if self.resolution == "LowRes":
				resolution = "_L"
			else:
				resolution = "_H"

			# Append the brick from the library
			filepath = library_path + "/" + part + ".blend" + "/Object/"
			directory = "/Object/"
			brick = part + resolution
			# Debug: Print the appending variables:
			if DEBUG:
				print("filepath = " + filepath)
				print("directory = " + directory)
				print("filename = " + brick)
				print("\n")

			bpy.ops.object.select_all(action='DESELECT')
			bpy.ops.wm.append(directory=filepath, filename=brick, active_layer=True, autoselect=True)

			# Select brick:
			current_brick = bpy.context.selected_objects[0]

			# Add the Logo to the brick studs:
			if self.logo:
				# Append the Lego Logo to the scene:
				filepath = library_path + "/Logo.blend/Object/"
				directory = "/Object/"
				logo_path = "Logo.Text"
				# 0 is the Logo vertex group id
				vertex_group_id = 0
				global_verts = []
				verticies = [v for v in current_brick.data.vertices if vertex_group_id in [vg.group for vg in v.groups]]
				for vertex in verticies:
					global_verts.append(current_brick.matrix_world * vertex.co)

				for vertex in global_verts:
					# Append the logo the scene:
					bpy.ops.wm.append(directory=filepath, filename=logo_path)
					logo = bpy.data.objects["Logo.Text"]
					if DEBUG:
						print(vertex[0])
						print(vertex[1])
						print(vertex[2])
						print("\n")
					logo.location = (vertex[0], vertex[1], vertex[2])
					# Select the two objects for joining:
					bpy.ops.object.select_all(action="DESELECT")
					logo.select = True
					current_brick.select = True
					bpy.context.scene.objects.active = current_brick
					# Make the brick the active object:
					bpy.ops.object.join()

			# Brick Material:
			if self.create_materials:
				# Convert LDraw color ID to Lego color ID
				if DEBUG:
					print(library_path + '/materials.db') # Debug: Print Material Database location

				# Query the material database to get Lego ID from LDraw ID
				con = sqlite3.connect(library_path + '/materials.db')
				cursor = con.cursor()
				cursor.execute("SELECT LEGO_ID FROM LDRAW_MATERIALS WHERE COLOR_ID = :color_id", {"color_id": col[1]})
				row = cursor.fetchone()
				mat = bpy.data.materials.get("LEGO." + '{0:03d}'.format(row[0]))

				# Append material if not already existing:
				if mat is None:
					filepath = library_path + "/_Materials.blend/Material/"
					new_material = "LEGO." + '{0:03d}'.format(row[0])
					bpy.ops.wm.append(directory=filepath, filename=new_material)
				mat = bpy.data.materials.get("LEGO." + '{0:03d}'.format(row[0]))

				# Assign material
				current_brick.active_material = mat
				con.close()

			# Brick Bevel:
			if self.bevel:
				# Edit the modifier:
				current_brick.modifiers["Bevel"].width = 0.002
				current_brick.modifiers["Bevel"].use_clamp_overlap = True
				current_brick.modifiers["Bevel"].limit_method = "WEIGHT"
				current_brick.modifiers["Bevel"].offset_type = "OFFSET"
				if resolution == "_H":
					current_brick.modifiers["Bevel"].segments = 3
				else:
					current_brick.modifiers["Bevel"].segments = 1
			else:
				# Remove the modifier
				current_brick.modifiers.remove(current_brick.modifiers["Bevel"])

			# UV Map
			if not self.uvmap:
				# Remove UV Map
				bpy.ops.mesh.uv_texture_remove()

			# Add brick to master list
			model_bricks.append(current_brick)

			# Add brick to group list
			if part not in grouped_bricks:
				grouped_bricks[part] = []
			grouped_bricks[part].append(current_brick)

			part_num = len(grouped_bricks[part]) - 1
			# Select the newly added brick and transform it accordingly:
			current_brick.location = (pos_x, pos_y, pos_z)
			current_brick.rotation_euler = (rot_x, rot_y, rot_z)
			current_brick.name = part + '.' + '{0:04d}'.format(part_num)

		if self.root:
			bpy.ops.object.select_all(action="DESELECT")
			bpy.ops.object.empty_add(type='PLAIN_AXES')
			empty = bpy.context.selected_objects[0]
			empty.name = file_name
			for brick in model_bricks:
				brick.select = True
			empty.select = True
			bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
			bpy.ops.object.select_all(action="DESELECT")

		if self.linked_type:
			for group in grouped_bricks:
				bpy.ops.object.select_all(action="DESELECT")
				for brick in group:
					brick.select = True
				bpy.ops.object.make_links_data(type='OBDATA')
			bpy.ops.object.select_all(action="DESELECT")
	else:
		print("Error, file not opened!")
	ldraw_file.close()

def read_ldd(self, context, src):
	# Get the path of the parts library:
	addons_paths = bpy.utils.script_paths("addons")
	library_path = "library"
	for path in addons_paths:
		library_path = os.path.join(path, "io_scene_lego_importer/Library")
		if os.path.exists(library_path):
			break
	# Unzip
	ldd_zip = ZipFile(file=src, mode="r")
	# Process
	ldd_tree = ET.fromstring(ldd_zip.open('IMAGE100.LXFML').read())
	ldd_bricks = ldd_tree.findall('Bricks/Brick')
	for ldd_brick in ldd_bricks:
		part = ldd_brick.get(key='designID')
		matrix_string = ldd_brick.find('Part/Bone').get(key='transformation')
		matrix = matrix_string.split(',')
		# Transform the origin to the new location:
		transform = [None] * 3
		transform[0] = float(matrix[3]) * float(matrix[0]) + float(matrix[4]) * float(matrix[1]) + float(matrix[5]) * float(matrix[2])
		transform[1] = float(matrix[6]) * float(matrix[0]) + float(matrix[7]) * float(matrix[1]) + float(matrix[8]) * float(matrix[2])
		transform[2] = float(matrix[9]) * float(matrix[0]) + float(matrix[10]) * float(matrix[1]) + float(matrix[11]) * float(matrix[2])

		# Decompose the transformation matrix to get the rotation:
		rot_x = math.atan2(float(matrix[10]), float(matrix[11]))
		rot_y = math.atan2(float(matrix[6]), float(matrix[3]))
		rot_z = math.atan2(float(matrix[9]), math.sqrt(float(matrix[10]) * float(matrix[10]) + float(matrix[11]) * float(matrix[11])))

		# Debug:
		if DEBUG:
			print("pos x = " + str(transform[0]))
			print("pos y = " + str(transform[1]))
			print("pos z = " + str(transform[2]))

			print("rot x = " + str(int(round(math.degrees(rot_x)))))
			print("rot y = " + str(int(round(math.degrees(rot_y)))))
			print("rot z = " + str(int(round(math.degrees(rot_z)))))


		if self.resolution == "LowRes":
			resolution = "_L"
		else:
			resolution = "_H"

		# Append the brick from the library
		filepath = library_path + "/" + part + ".blend" + "/Object/"
		directory = "/Object/"
		brick = part + resolution
		# Debug: Print the appending variables:
		print("filepath = " + filepath)
		print("directory = " + directory)
		print("filename = " + brick)
		print("\n")
		bpy.ops.object.select_all(action='DESELECT')
		bpy.ops.wm.append(directory=filepath, filename=brick, active_layer=True, autoselect=True)

		# Select brick:
		current_brick = bpy.context.selected_objects[0]

		# Add the Logo to the brick studs:
		if self.logo:
			# Append the Lego Logo to the scene:
			print("Adding Logo")
			filepath = library_path + "/Logo.blend/Object/"
			directory = "/Object/"
			logo_path = "Logo.Text"
			# 0 is the Logo vertex group id
			vertex_group_id = 0
			global_verts = []
			verticies = [v for v in current_brick.data.vertices if vertex_group_id in [vg.group for vg in v.groups]]
			for vertex in verticies:
				global_verts.append(current_brick.matrix_world * vertex.co)

			for vertex in global_verts:
				# Append the logo the scene:
				bpy.ops.wm.append(directory=filepath, filename=logo_path)
				logo = bpy.data.objects["Logo.Text"]
				print(vertex[0])
				print(vertex[1])
				print(vertex[2])
				print("\n")
				logo.location = (vertex[0], vertex[1], vertex[2])
				# Select the two objects for joining:
				bpy.ops.object.select_all(action="DESELECT")
				logo.select = True
				current_brick.select = True
				bpy.context.scene.objects.active = current_brick
				# Make the brick the active object:
				bpy.ops.object.join()

		# Brick Material:
		if self.create_materials:
			mat_num = int(ldd_brick.find('Part').get(key='materials').split(',')[0])
			mat = bpy.data.materials.get("LEGO." + '{0:03d}'.format(mat_num))
			# Append material if not already existing:
			if mat is None:
				filepath = library_path + "/_Materials.blend/Material/"
				new_material = "LEGO." + '{0:03d}'.format(mat_num)
				bpy.ops.wm.append(directory=filepath, filename=new_material)
			mat = bpy.data.materials.get("LEGO." + '{0:03d}'.format(mat_num))
			# Assign material
			current_brick.active_material = mat

		# Brick Bevel:
		if self.bevel:
			# Edit the modifier:
			current_brick.modifiers["Bevel"].width = 0.002
			current_brick.modifiers["Bevel"].use_clamp_overlap = True
			current_brick.modifiers["Bevel"].limit_method = "WEIGHT"
			current_brick.modifiers["Bevel"].offset_type = "OFFSET"
			if resolution == "_H":
				current_brick.modifiers["Bevel"].segments = 3
			else:
				current_brick.modifiers["Bevel"].segments = 1
		else:
			# Remove the modifier
			current_brick.modifiers.remove(current_brick.modifiers["Bevel"])

		# UV Map
		if not self.uvmap:
			# Remove UV Map
			bpy.ops.mesh.uv_texture_remove()

		# Add brick to master list
		model_bricks.append(current_brick)

		# Add brick to group list
		if part not in grouped_bricks:
			grouped_bricks[part] = []
		grouped_bricks[part].append(current_brick)

		part_num = len(grouped_bricks[part]) - 1
		# Select the newly added brick and transform it accordingly:
		current_brick.location = (transform[0], transform[1], transform[2])
		current_brick.rotation_euler = (rot_x, rot_y, rot_z)
		current_brick.name = part + '.' + '{0:04d}'.format(part_num)

"""
	Documentation:

	LDraw Coordinate system:

	| -y
	|
	|_______x
   /
  /
 z

	LeoCAD:
		Program coordinate system:
		| +z
		|
		|_______ +y
	   /
	  /
	 +x

	 	Test 2:
		piece at (10, 30, 24)

	Dimensions of a 1x1 brick:
		Blender:
			Brick height: 0.24
			Stud Hight: 0.04
			Brick length: 0.2
			Stud Radius: 0.06
		LDraw:
			Brick Height: 24
			Stud Height: 4
			Brick Length: 20
			Stud Radius: 6

	Bevel Modifier:
		Width: 0.002
		Segments: 3 for H, 1 for L

    Blender Mesh Bevel (Not Modifier)
	    Amount: 0.007
	    Segments: 6 for High
	              3 for Low

	Hard Surface notes:
		Stud bevel size (when scaled): 0.007
		Stud base bevel (when scaled): 0.001
"""
