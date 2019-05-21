bl_info = {
	"name": "Quake Map Exporter",
	"author": "Xembie, Seeeker",
	"version": (0, 2, 0),
	"blender": (2, 74, 0),
	"location": "File > Import-Export",
	"description": "Export Quake 3 Map",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame"
}
import math,mathutils,struct
def popup(title,msg,icon):
	def draw(self,context):
		self.layout.label(msg)
	bpy.context.window_manager.popup_menu(draw,title=title,icon=icon)
def tri_normal(tri):
	a = mathutils.Vector(tri[1]) - mathutils.Vector(tri[0])
	b = mathutils.Vector(tri[2]) - mathutils.Vector(tri[0])
	a.normalize()
	b.normalize()
	normal = []
	normal.append((a.y * b.z) - (a.z * b.y))
	normal.append((a.z * b.x) - (a.x * b.z))
	normal.append((a.x * b.y) - (a.y * b.x))
	return normal
def tri_fix(tri,normal):
	a = mathutils.Vector(normal)
	b = mathutils.Vector(tri_normal(tri))
	a.normalize()
	b.normalize()
	v = a - b
	if v.length < math.sqrt(2):
		vert = tri[0]
		tri[0] = tri[1]
		tri[1] = vert
import os
overrideproperties = ["noexport","shadows","autoclip","forcemeta","modelname","nomodelent","castshadows","recvshadows","convexbrush","texture","hiddentexture","brushwidth","detailbrush","hiddendetailbrush","animmodel","fps","startframe","numframes","junior","linear","noangle","nogridlight","sun","shader","noimage"]
def obj_prop(obj,name,default):
	try:
		val = obj[name]
		if type(val) == str and len(val) == 0:
			raise Exception("empty prop")
	except:
		val = default
	return val
def str_to_float(instr,default):
	try:
		val = float(instr)
	except:
		val = default
	return val
def str_to_int(instr,default):
	try:
		val = int(instr)
	except:
		val = default
	return val
def shader_append(shaderlist,shader):
	for s in shaderlist:
		if s == shader:
			return
	shaderlist.append(shader)
from . import md3_encode
def save_model(path,obj,scale,precision,basedir,shaderlist):
	objname = basedir + obj_prop(obj,"modelname",obj.name)
	fpath = os.path.dirname(path) + "/" + objname
	try:
		os.makedirs(os.path.dirname(fpath))
	except:
		pass
	if len(obj.material_slots) == 0:
		print("  Missing material for model object: " + obj.name)
		return []
	nobj = obj.to_mesh(bpy.context.scene,True,"PREVIEW")
	matrix = obj.matrix_world.copy()
	matrix[0][3] = 0
	matrix[1][3] = 0
	matrix[2][3] = 0
	propertylist = []
	if obj.animmodel == True:
		print("  Exporting model to " + fpath + ".md3")
		md3 = md3_encode.md3Object()
		md3.ident = md3_encode.MD3_IDENT
		md3.version = md3_encode.MD3_VERSION
		md3.name = obj.name
		startframe = str_to_int(obj_prop(obj,"startframe",0),0)
		md3.numFrames = str_to_int(obj_prop(obj,"numframes",1),1)
		if md3.numFrames < 1:
			md3.numFrames = 1
		nsurface = md3_encode.md3Surface()
		nsurface.name = obj.name
		nsurface.ident = md3_encode.MD3_IDENT
		md3.surfaces.append(nsurface)
		md3.numSurfaces += 1
		vertlist = []
		for matindex in range(0,len(obj.material_slots)):
			image = None
			shader = basedir + obj_prop(obj.material_slots[matindex].material,"shader",obj.material_slots[matindex].material.name).replace(".","")
			try:
				for n in obj.material_slots[matindex].material.node_tree.nodes:
					if n.type == "TEX_IMAGE":
						image = n.image
						break
			except:
				try:
					image = obj.data.uv_textures.active.data[0].image
				except:
					pass
			if len(shader.encode()) > 64:
				print("    Shader \"" + shader + "\" exceeds 64 byte limit of the MD3 format for material in object: " + obj.name)
			nshader = md3_encode.md3Shader()
			nshader.name = shader
			nsurface.shaders.append(nshader)
			nsurface.numShaders += 1
			if obj.material_slots[matindex].material.noimage == False:
				if image == None:
					print("    Missing material image/baked texture of surface for material in object: " + obj.name)
				else:
					scene = bpy.context.scene
					scene.render.image_settings.file_format="JPEG" #"JPEG2000","TARGA","TARGA_RAW"
					image.save_render(os.path.dirname(path) + "/" + shader + ".jpg",scene)
			shader_append(shaderlist,shader.encode())
			for f in nobj.polygons:
				if f.material_index != matindex:
					continue
				if len(f.vertices) != 3:
					print("    Found a nontriangle face in object " + obj.name)
					continue
				ntri = md3_encode.md3Triangle()
				nsurface.triangles.append(ntri)
				nsurface.numTriangles += 1
				for i,l in enumerate(f.loop_indices):
					match = False
					uv = nobj.uv_layers.active.data[l]
					uv_u = round(uv.uv[0],precision)
					uv_v = round(uv.uv[1],precision)
					for i2,vi in enumerate(vertlist):
						if vi != nobj.loops[l].vertex_index or nsurface.uv[i2].u != uv_u or nsurface.uv[i2].v != uv_v:
							continue
						match = True
						ntri.indexes[i] = i2
						break
					if match == False:
						ntri.indexes[i] = len(vertlist)
						vertlist.append(nobj.loops[l].vertex_index)
						ntex = md3_encode.md3TexCoord()
						ntex.u = uv_u
						ntex.v = uv_v
						nsurface.uv.append(ntex)
						nsurface.numVerts += 1
		for child in obj.children:
			if len(child.tagname) > 0:
				md3.numTags += 1
		for frame in range(startframe,startframe + md3.numFrames):
			bpy.context.scene.frame_set(frame)
			fobj = obj.to_mesh(bpy.context.scene,True,'PREVIEW')
			nframe = md3_encode.md3Frame()
			nframe.name = str(frame - startframe)
			md3.frames.append(nframe)
			for vi in vertlist:
				vert = fobj.vertices[vi]
				nvert = md3_encode.md3Vert()
				nvert.normal = nvert.Encode(vert.normal)
				nvert.xyz = matrix * vert.co * scale
				for i in range(0,3):
					nvert.xyz[i] = round(nvert.xyz[i],precision)
					nframe.mins[i] = min(nframe.mins[i],nvert.xyz[i])
					nframe.maxs[i] = max(nframe.maxs[i],nvert.xyz[i])
				minlength = math.sqrt(math.pow(nframe.mins[0],2) + math.pow(nframe.mins[1],2) + math.pow(nframe.mins[2],2))
				maxlength = math.sqrt(math.pow(nframe.maxs[0],2) + math.pow(nframe.maxs[1],2) + math.pow(nframe.maxs[2],2))
				nframe.radius = round(max(minlength,maxlength),5)
				nsurface.verts.append(nvert)
				nsurface.numFrames += 1
			bpy.data.meshes.remove(fobj)
			for child in obj.children:
				if len(child.tagname) > 0:
					ntag = md3_encode.md3Tag()
					ntag.name = child.tagname
					childmatrix = child.matrix_world.copy()
					childmatrix.normalize()
					ntag.origin[0] = round(childmatrix[0][3] * scale,precision)
					ntag.origin[1] = round(childmatrix[1][3] * scale,precision)
					ntag.origin[2] = round(childmatrix[2][3] * scale,precision)
					ntag.axis[0] = round(childmatrix[0][0],precision)
					ntag.axis[1] = round(childmatrix[0][1],precision)
					ntag.axis[2] = round(childmatrix[0][2],precision)
					ntag.axis[3] = round(childmatrix[1][0],precision)
					ntag.axis[4] = round(childmatrix[1][1],precision)
					ntag.axis[5] = round(childmatrix[1][2],precision)
					ntag.axis[6] = round(childmatrix[2][0],precision)
					ntag.axis[7] = round(childmatrix[2][1],precision)
					ntag.axis[8] = round(childmatrix[2][2],precision)
					md3.tags.append(ntag)
		file = open(fpath + ".md3","wb")
		md3.Save(file)
		file.close()
		if obj.nomodelent == False:
			propertylist.append("\"classname\" \"misc_anim_model\"\n")
			fps = obj_prop(obj,"fps",20)
			propertylist.append("\"animation\" \"0 " + str(md3.numFrames) + " " + str(md3.numFrames) + " " + str(fps) + "\"\n")
			propertylist.append("\"model\" \"" + objname + ".md3\"\n")
			if obj.castshadows == True:
				propertylist.append("\"_cs\" \"1\"\n")
			if obj.recvshadows == False:
				propertylist.append("\"_rs\" \"0\"\n")
			for prop in obj.items():
				if type(prop[1]) != str and type(prop[1]) != int and type(prop[1]) != float:
					continue
				if prop[0] in overrideproperties:
					continue
				if prop[0] == "origin" or prop[0] == "classname" or prop[0] == "model" or prop[0] == "_rs" or prop[0] == "animation":
					continue
				propertylist.append("\"" + prop[0] + "\" \"" + str(prop[1]) + "\"\n")
			propertylist.append("\"origin\" \"" +	str(int(round(obj.matrix_world[0][3] * scale,precision))) + " " + \
													str(int(round(obj.matrix_world[1][3] * scale,precision))) + " " + \
													str(int(round(obj.matrix_world[2][3] * scale,precision))) + "\"\n")
	else:
		print("  Exporting model to " + fpath + ".obj")
		vertlist = []
		uvlist = []
		normallist = []
		for v in nobj.vertices:
			v2 = matrix * v.co
			v2 = v2 * scale
			vertlist.append("v " + str(round(v2[0],precision)) + " " + str(round(v2[1],precision)) + " " + str(round(v2[2],precision)) + "\n")
			vn = [None] * 3
			vn[0] = round(v.normal[0],precision)
			vn[1] = round(v.normal[1],precision)
			vn[2] = round(v.normal[2],precision)
			normallist.append("vn " + str(vn[0]) + " " + str(vn[1]) + " " + str(vn[2]) + "\n")
		for uv in nobj.uv_layers.active.data:
			vt = [None] * 2
			vt[0] = round(uv.uv[0],precision)
			vt[1] = round(uv.uv[1],precision)
			uvlist.append("vt " + str(vt[0]) + " " + str(vt[1]) + "\n")
		file = open(fpath + ".obj","wb")
		file.write(b"o " + objname.encode() + b"\n")
		for v in vertlist:
			file.write(v.encode())
		for uv in uvlist:
			file.write(uv.encode())
		for n in normallist:
			file.write(n.encode())
		for matindex in range(0,len(obj.material_slots)):
			image = None
			shader = basedir + obj_prop(obj.material_slots[matindex].material,"shader",obj.material_slots[matindex].material.name).replace(".","")
			try:
				for n in obj.material_slots[matindex].material.node_tree.nodes:
					if n.type == "TEX_IMAGE":
						image = n.image
						break
			except:
				try:
					image = obj.data.uv_textures.active.data[0].image
				except:
					pass
			if obj.material_slots[matindex].material.noimage == False:
				if image == None:
					print("    Missing material image/baked texture of surface for material in object: " + obj.name)
				else:
					scene = bpy.context.scene
					scene.render.image_settings.file_format="JPEG" #"JPEG2000","TARGA","TARGA_RAW"
					image.save_render(os.path.dirname(path) + "/" + shader + ".jpg",scene)
			file.write(b"g " + shader.encode() + b"\n")
			file.write(b"usemtl " + shader.encode() + b"\n")
			shader_append(shaderlist,shader.encode())
			for f in nobj.polygons:
				if f.material_index != matindex:
					continue
				face = "f"
				for l in f.loop_indices:
					face += " " + str(nobj.loops[l].vertex_index + 1) + "/" + str(l + 1) + "/" + str(nobj.loops[l].vertex_index + 1)
				face += "\n"
				file.write(face.encode())
		file.close()
		if obj.nomodelent == False:
			propertylist.append("\"classname\" \"misc_model\"\n")
			propertylist.append("\"model\" \"" + objname + ".obj\"\n")
			if obj.castshadows == True:
				propertylist.append("\"_cs\" \"1\"\n")
			if obj.recvshadows == False:
				propertylist.append("\"_rs\" \"0\"\n")
			for prop in obj.items():
				if type(prop[1]) != str and type(prop[1]) != int and type(prop[1]) != float:
					continue
				if prop[0] in overrideproperties:
					continue
				if prop[0] == "origin" or prop[0] == "classname" or prop[0] == "model" or prop[0] == "_rs":
					continue
				propertylist.append("\"" + prop[0] + "\" \"" + str(prop[1]) + "\"\n")
			propertylist.append("\"origin\" \"" +	str(int(round(obj.matrix_world[0][3] * scale,precision))) + " " + \
													str(int(round(obj.matrix_world[1][3] * scale,precision))) + " " + \
													str(int(round(obj.matrix_world[2][3] * scale,precision))) + "\"\n")
	bpy.data.meshes.remove(nobj)
	print("    Done")
	return propertylist
def tri_append(matrix,v1,v2,v3,scale,normal,br,text,detail):
	af = (matrix * v1) * scale
	bf = (matrix * v2) * scale
	cf = (matrix * v3) * scale
	tri = [[	int(round(bf.x,0)),
				int(round(bf.y,0)),
				int(round(bf.z,0)) ],
			[	int(round(af.x,0)),
				int(round(af.y,0)),
				int(round(af.z,0)) ],
			[	int(round(cf.x,0)),
				int(round(cf.y,0)),
				int(round(cf.z,0)) ]]
	tri_fix(tri,normal)
	flags = 0
	if detail == True:
		flags |= 1 << 27
	br.append(	"( "	+ str(tri[0][0]) + " " + str(tri[0][1]) + " " + str(tri[0][2]) + " ) " + \
				"( "	+ str(tri[1][0]) + " " + str(tri[1][1]) + " " + str(tri[1][2]) + " ) " + \
				"( "	+ str(tri[2][0]) + " " + str(tri[2][1]) + " " + str(tri[2][2]) + " ) " + \
				text + " 0 0 0 1 1 " + str(flags) + " 0 0\n" )
def find_linked_faces(mesh,faces,ignorefaces):
	while True:
		added = False
		for face in mesh.polygons:
			if face in ignorefaces or face in faces:
				continue
			for v in face.vertices:
				done = False
				for f in faces:
					if v in f.vertices:
						faces.append(face)
						added = True
						done = True
						break
				if done == True:
					break
		if added == False:
			break
def quake_map(path,exportselected,scale,precision,texture,basedir,shaderfile,brushwidth,hiddentexture):
	print("Quake Map exporter " + str(bl_info["version"]))
	shaderpath = os.path.dirname(path) + "/" + shaderfile
	try:
		os.makedirs(os.path.dirname(shaderpath))
	except:
		pass
	objectlist = []
	brusheslist = []
	entitylist = []
	shaderlist = []
	try:
		bpy.ops.object.mode_set(mode="OBJECT")
	except:
		pass
	bpy.context.scene.update()
	origframe = bpy.context.scene.frame_current
	expobjs = bpy.data.objects
	if exportselected == True:
		expobjs = bpy.context.selected_objects
	for obj in expobjs:
		if obj.noexport == True:
			continue
		bpy.context.scene.frame_set(origframe)
		if obj.type == "MESH":
			if len(obj.data.uv_layers) > 0:
				propertylist = save_model(path,obj,scale,precision,basedir,shaderlist)
				if len(propertylist) > 0:
					entity = []
					entitylist.append(entity)
					entity.append(propertylist)
				if obj.modelbrush == False:
					continue
			mesh = obj.to_mesh(bpy.context.scene,True,"PREVIEW")
			brush = []
			brusheslist.append(brush)
			propertylist = []
			brush.append(propertylist)
			brushlist = []
			brush.append(brushlist)
			objectlist.append(brush)
			classname = False
			for prop in obj.items():
				if type(prop[1]) != str and type(prop[1]) != int and type(prop[1]) != float:
					continue
				if prop[0] in overrideproperties:
					continue
				if prop[0] == "classname":
					classname = True
				propertylist.append([str(prop[0]),"\"" + prop[0] + "\" \"" + str(prop[1]) + "\"\n"])
			if classname == False:
				propertylist.insert(0,[obj.name,"\"classname\" \"func_group\"\n"])
			matrix = obj.matrix_world
			if obj.convexbrush == True:
				ignorefaces = []
				while True:
					faces = []
					for face in mesh.polygons:
						if face in ignorefaces:
							continue
						faces.append(face)
						break
					if len(faces) == 0:
						break
					find_linked_faces(mesh,faces,ignorefaces)
					ignorefaces += faces
					br = []
					brushlist.append(br)
					for face in faces:
						if len(face.vertices) < 3:
							continue
						objtext = obj_prop(obj,"texture",texture)
						objdetailbrush = obj.detailbrush
						if len(mesh.materials) > face.material_index:
							objtext = obj_prop(mesh.materials[face.material_index],"texture",objtext)
							objdetailbrush = mesh.materials[face.material_index].detailbrush
						localcenter = mathutils.Vector((0,0,0))
						for v in face.vertices:
							localcenter += mesh.vertices[v].co
						localcenter /= len(face.vertices)
						tri_append(matrix,mesh.vertices[face.vertices[0]].co,mesh.vertices[face.vertices[1]].co,localcenter,scale,face.normal,br,objtext,objdetailbrush)
			else:
				for face in mesh.polygons:
					if len(face.vertices) < 3:
						continue
					objtext = obj_prop(obj,"texture",texture)
					objhiddentext = obj_prop(obj,"hiddentexture",hiddentexture)
					objwidth = obj_prop(obj,"brushwidth",brushwidth)
					objdetailbrush = obj.detailbrush
					objhiddendetailbrush = obj.hiddendetailbrush
					if len(mesh.materials) > face.material_index:
						objtext = obj_prop(mesh.materials[face.material_index],"texture",objtext)
						objhiddentext = obj_prop(mesh.materials[face.material_index],"hiddentexture",objhiddentext)
						objwidth = obj_prop(mesh.materials[face.material_index],"brushwidth",objwidth)
						objdetailbrush = mesh.materials[face.material_index].detailbrush
						objhiddendetailbrush = mesh.materials[face.material_index].hiddendetailbrush
					br = []
					brushlist.append(br)
					localcenter = mathutils.Vector((0,0,0))
					for v in face.vertices:
						localcenter += mesh.vertices[v].co
					localcenter /= len(face.vertices)
					tri_append(matrix,mesh.vertices[face.vertices[0]].co,mesh.vertices[face.vertices[1]].co,mesh.vertices[face.vertices[2]].co,scale,face.normal,br,objtext,objdetailbrush)
					localcenter += face.normal * -1 * (str_to_float(objwidth,2.0) / scale)
					for li in face.loop_indices:
						edge = mesh.edges[mesh.loops[li].edge_index]
						tri_append(matrix,mesh.vertices[edge.vertices[1]].co,mesh.vertices[edge.vertices[0]].co,localcenter,scale,face.normal * -1,br,objhiddentext,objhiddendetailbrush)
			print("  Mesh(" + obj.name + ").")
			bpy.data.meshes.remove(mesh)
		elif obj.type == "LAMP":
			if obj.data.type != "POINT" and obj.data.type != "SPOT":
				print("  Skipped lamp object(" + obj.name + "). It is not a POINT or SPOT type.")
				continue
			entity = []
			entitylist.append(entity)
			propertylist = []
			entity.append(propertylist)
			light = obj.data.distance * obj.data.energy * scale
			light = str_to_float(obj_prop(obj,"light",light),light)
			spawnflags = obj_prop(obj,"spawnflags","")
			if obj.junior == True:
				propertylist.append("\"classname\" \"lightjunior\"\n")
			else:
				propertylist.append("\"classname\" \"light\"\n")
			if len(spawnflags) > 0:
				propertylist.append("\"spawnflags\" \"" + spawnflags + "\"\n")
			if obj.data.type == "SPOT":
				target = None
				for constraint in obj.constraints:
					if constraint.type != "TRACK_TO" or constraint.target == None:
						continue
					target = constraint.target
					break
				if target == None or len(target.classname) == 0 or len(target.targetname) == 0:
					print("  Spot Lamp(" + obj.name + ") is missing TRACK_TO constraint with object that has classname and targetname.")
				else:
					distv = obj.location - target.location
					if obj.data.spot_size > 3.14:
						radius = scale * distv.length * 1255
					else:
						radius = scale * distv.length * math.tan(obj.data.spot_size / 2)
					radius -= 16
					radius = str_to_float(obj_prop(obj,"radius",radius),radius)
					propertylist.append("\"radius\" \"" + str(round(radius,precision)) + "\"\n")
					propertylist.append("\"target\" \"" + target.targetname + "\"\n")
					if obj.sun == True:
						propertylist.append("\"_sun\" \"1\"\n")
			propertylist.append("\"light\" \"" + str(round(light,precision)) + "\"\n")
			propertylist.append("\"_color\" \"" +	str(round(obj.data.color[0],precision)) + " " + \
													str(round(obj.data.color[1],precision)) + " " + \
													str(round(obj.data.color[2],precision)) + "\"\n")
			propertylist.append("\"origin\" \"" +	str(int(round(obj.matrix_world[0][3] * scale,0))) + " " + \
													str(int(round(obj.matrix_world[1][3] * scale,0))) + " " + \
													str(int(round(obj.matrix_world[2][3] * scale,0))) + "\"\n")
			print("  Lamp(" + obj.name + ") " + str(len(propertylist)) + " properties.")
		elif obj.type == "EMPTY" or obj.type == "CAMERA":
			entity = []
			entitylist.append(entity)
			propertylist = []
			entity.append(propertylist)
			origin = False
			angles = False
			if hasattr(obj,"classname") == False:
				print("  Missing classname for object: " + obj.name)
				continue
			for prop in obj.items():
				if type(prop[1]) != str and type(prop[1]) != int and type(prop[1]) != float:
					continue
				if prop[0] in overrideproperties:
					continue
				if prop[0] == "origin":
					origin = True
				elif prop[0] == "angles":
					angles = True
				propertylist.append("\"" + prop[0] + "\" \"" + str(prop[1]) + "\"\n")
			if origin == False:
				propertylist.append("\"origin\" \"" +	str(int(round(obj.matrix_world[0][3] * scale,0))) + " " + \
														str(int(round(obj.matrix_world[1][3] * scale,0))) + " " + \
														str(int(round(obj.matrix_world[2][3] * scale,0))) + "\"\n")
			if angles == False:
				up = obj.matrix_world.to_quaternion() * mathutils.Vector((0.0,1.0,0.0))
				right = obj.matrix_world.to_quaternion() * mathutils.Vector((-1.0,0.0,0.0))
				dir = obj.matrix_world.to_quaternion() * mathutils.Vector((0.0,0.0,-1.0))
				yaw = math.atan2(dir[1],dir[0]) * 180 / math.pi
				pitch = -math.atan2(dir[2],math.sqrt(dir[0] * dir[0] + dir[1] * dir[1])) * 180 / math.pi
				roll = math.atan2(right[2],up[2]) * 180 / math.pi
				propertylist.append("\"angles\" \"" +	str(round(pitch,precision)) + " " + \
														str(round(yaw,precision)) + " " + \
														str(round(roll,precision)) + "\"\n")
			print("  Entity(" + obj.name + ") " + str(len(propertylist)) + " properties.")
	f = open(path,"wb")
	#write world with world properties
	f.write(b"// entity 0\n")
	f.write(b"{\n\"classname\" \"worldspawn\"\n")
	for prop in bpy.context.scene.world.items():
		if type(prop[1]) != str and type(prop[1]) != int and type(prop[1]) != float:
			continue
		if prop[0] == "classname":
			continue
		f.write(b"\"" + prop[0].encode() + b"\" \"" + str(prop[1]).encode() + b"\"\n")
	f.write(b"}\n")
	#Write objects
	entitynum = 1
	for o in objectlist:
		f.write(b"// entity " + str(entitynum).encode() + b"\n")
		entitynum += 1
		brushnum = 0
		f.write(b"{\n")
		for prop in o[0]:
			f.write((prop[1]).encode())
		for brush in o[1]:
			f.write(b"// brush " + str(brushnum).encode() + b"\n")
			brushnum += 1
			f.write(b"{\n")
			for br in brush:
				f.write((br).encode())
			f.write(b"}\n")
		f.write(b"}\n")
	#write empties/cameras
	if len(entitylist) > 0:
		for i,entity in enumerate(entitylist):
			f.write(b"// entity " + str(entitynum).encode() + b"\n")
			entitynum += 1
			f.write(b"{\n")
			for prop in entity[0]:
				f.write((prop).encode())
			f.write(b"}\n")
	f.close()
	#write shaders
	with open(shaderpath,"wb") as shaderfile:
		for s in shaderlist:
			shaderfile.write(s + b"\n{\n")
			shaderfile.write(b"\t{\n\t\tmap $lightmap\n\t\trgbGen identity\n\t}\n")
			shaderfile.write(b"\t{\n\t\tmap " + s + b".jpg\n\t\tblendFunc filter\n\t}\n}\n")
		shaderfile.close()
	bpy.context.scene.frame_set(origframe)
	print("Done")
	popup("Quake Map Exporter","Completed. Check console for possible errors.","NONE")
from bpy.props import *
import bpy
bpy.types.Scene.exportselected	= BoolProperty(name = "Export selected objects",description = "Only export objects that are selected.",default = False)
bpy.types.Scene.scale			= FloatProperty(name = "Scale",description = "Scale all objects from origin.",default = 64.0)
bpy.types.Scene.precision		= IntProperty(name = "Precision",description = "Rounding of values to decimal place.",default = 5)
bpy.types.Scene.basedir			= StringProperty(name = "Base directory",description = "Prefix for models and material textures",default = "models/")
bpy.types.Scene.shaderfile		= StringProperty(name = "Shader file path",description = "Shader file path",default = "scripts/map.shader")
bpy.types.Scene.texture			= StringProperty(name = "Texture",description = "Specific to some quake formats. This can be overrided per object",maxlen = 1024,default = "common/caulk")
bpy.types.Scene.brushwidth		= FloatProperty(name = "Brush width",description = "Width of brushes. Scale is not applied.",default = 2.0)
bpy.types.Scene.hiddentexture	= StringProperty(name = "Hidden Texture",description = "Used on hidden brush faces.",maxlen = 1024,default = "common/invisible")
class ExportBrushMap(bpy.types.Operator):
	bl_idname		= "export.brushmap"
	bl_label		= "Export brush map"
	filepath		= StringProperty(subtype = "FILE_PATH",name = "File path",description = "Filepath for exporting")
	def draw(self,context):
		scene = context.scene
		self.layout.prop(scene,"exportselected")
		self.layout.prop(scene,"scale")
		self.layout.prop(scene,"precision")
		box = self.layout.box()
		box.label("Model Options")
		box.prop(scene,"basedir")
		box.prop(scene,"shaderfile")
		box = self.layout.box()
		box.label("Brush Defaults")
		box.prop(scene,"texture")
		box.prop(scene,"brushwidth")
		box.prop(scene,"hiddentexture")
	def execute(self,context):
		scene = context.scene
		quake_map(self.filepath,scene.exportselected,scene.scale,scene.precision,scene.texture,scene.basedir,scene.shaderfile,scene.brushwidth,scene.hiddentexture)
		return {"FINISHED"}
	def invoke(self,context,event):
		wm = context.window_manager
		wm.fileselect_add(self)
		return {"RUNNING_MODAL"}
def export(self,context):
	self.layout.operator(ExportBrushMap.bl_idname,text="Quake 3 Map")
bpy.types.Scene.skyboxdir = StringProperty(subtype = "DIR_PATH",name = "Save Directory",description = "Directory where skybox images should be saved.")
bpy.types.Scene.skyboxname = StringProperty(name = "Base Name",description = "Base name or prefix for images.",default = "skybox")
bpy.types.Scene.skyboxresx = IntProperty(name = "Image width",description = "Width of image in pixels.",default = 1024)
bpy.types.Scene.skyboxresy = IntProperty(name = "Image height",description = "Height of image in pixels.",default = 1024)
bpy.types.Scene.bsppath = StringProperty(subtype = "FILE_PATH",name = "BSP File",description = "BSP file to be modified.")
bpy.types.Scene.lightgridscale = FloatProperty(name = "Scale",description = "Scale from Blender to Quake. Use same value used when exporting.",default = 64.0)
bpy.types.Scene.lightgridlightscale = FloatProperty(name = "Light scale",description = "Multiplies the light color.",default = 1.0)
bpy.types.Scene.extractentities = StringProperty(subtype = "FILE_PATH",name = "Output Text",description = "File path used to write entities text.")
bpy.types.Scene.insertentities = StringProperty(subtype = "FILE_PATH",name = "Input Text",description = "File path used to read entities text.")
bpy.types.Scene.extractshaders = StringProperty(subtype = "FILE_PATH",name = "Output Text",description = "File path used to write shader text.")
bpy.types.Scene.insertshaders = StringProperty(subtype = "FILE_PATH",name = "Input Text",description = "File path used to read shader text.")
bpy.types.Scene.convertbsp = StringProperty(subtype = "FILE_PATH",name = "Output BSP",description = "File path used to write converted BSP.")
bpy.types.Scene.convertbspversion = IntProperty(name = "Version",description = "BSP version usually unique to each game.",default = 1,min = 0,max = 0x7FFFFFFF)
class ToolPanel(bpy.types.Panel):
	bl_label = "Quake Map Exporter"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	def draw(self,context):
		scene = context.scene
		box = self.layout.box()
		box.label("Create Skybox Images")
		box.prop(scene,"skyboxdir")
		box.prop(scene,"skyboxname")
		box.prop(scene,"skyboxresx")
		box.prop(scene,"skyboxresy")
		box.operator("quakemap.skybox")
		box = self.layout.box()
		box.label("IBSP/RBSP Operations")
		box.prop(scene,"bsppath")
		box2 = box.box()
		box2.label("Build Light-grid")
		box2.prop(scene,"lightgridscale")
		box2.prop(scene,"lightgridlightscale")
		box2.label("Save before continuing! This may take a very long time.")
		box2.label("May generate poor grid lights near walls.")
		box2.operator("quakemap.lightgrid")
		box2 = box.box()
		box2.label("Remove Directional Light-grid")
		box2.operator("quakemap.lightgridaverage")
		box2 = box.box()
		box2.label("Extract Entities")
		box2.prop(scene,"extractentities")
		box2.operator("quakemap.extractentities")
		box2 = box.box()
		box2.label("Insert Entities")
		box2.prop(scene,"insertentities")
		box2.operator("quakemap.insertentities")
		box2 = box.box()
		box2.label("Extract Shaders")
		box2.prop(scene,"extractshaders")
		box2.operator("quakemap.extractshaders")
		box2 = box.box()
		box2.label("Import Shaders")
		box2.prop(scene,"extractshaders")
		box2.operator("quakemap.insertshaders")
		box2 = box.box()
		box2.label("Convert BSP(IBSP<->RBSP)")
		box2.prop(scene,"convertbsp")
		box2.prop(scene,"convertbspversion")
		box2.operator("quakemap.convertbsp")
def skybox(scene,camobj,dir,name,resx,resy):
	degree2rad = math.pi / 180.0
	camobj.data.angle = 90.0 * degree2rad#FOV
	camobj.rotation_mode = "XYZ"
	camobj.data.type = "PERSP"
	#Save and set up resolutions and image format
	origcamera = scene.camera
	origresx = scene.render.resolution_x
	origresy = scene.render.resolution_y
	origperc = scene.render.resolution_percentage
	origformat = scene.render.image_settings.file_format
	origcolormode = scene.render.image_settings.color_mode
	origfilepath = scene.render.filepath
	origmatrix = camobj.matrix_world.copy()
	origloc = camobj.location.copy()
	origalphamode = scene.render.alpha_mode
	scene.camera = camobj
	scene.render.resolution_x = resx
	scene.render.resolution_y = resy
	scene.render.resolution_percentage = 100
	scene.render.image_settings.file_format = 'TARGA'
	scene.render.image_settings.color_mode = 'RGBA'
	#Set Transparent BG
	origcyclestrans = None
	if scene.render.engine == "CYCLES":
		origcyclestrans = scene.cycles.film_transparent
		scene.cycles.film_transparent = True
	scene.render.alpha_mode = "TRANSPARENT"
	camera_euler_rotations = (
		("bk",180,0),
		("ft",0,0),
		("lf",90,0),
		("rt",-90,0),
		("up",0,-90),
		("dn",0,90))
	up = camobj.matrix_world.to_quaternion() * mathutils.Vector((0.0,1.0,0.0))
	right = camobj.matrix_world.to_quaternion() * mathutils.Vector((-1.0,0.0,0.0))
	for rotation in camera_euler_rotations:
		if rotation[1] != 0.0:
			camobj.matrix_world = mathutils.Matrix.Rotation(rotation[1] * degree2rad,4,up) * origmatrix
		elif rotation[2] != 0.0:
			camobj.matrix_world = mathutils.Matrix.Rotation(rotation[2] * degree2rad,4,right) * origmatrix
		camobj.location = origloc
		scene.render.filepath = os.path.join(dir,name + "_" + rotation[0] + ".tga")
		bpy.ops.render.render(write_still = True)
		camobj.matrix_world = origmatrix
	scene.camera = origcamera
	scene.render.resolution_x = origresx
	scene.render.resolution_y = origresy
	scene.render.resolution_percentage = origperc
	scene.render.image_settings.file_format = origformat
	scene.render.image_settings.color_mode = origcolormode
	scene.render.filepath = origfilepath
	if scene.render.engine == "CYCLES":
		scene.cycles.film_transparent = origcyclestrans
	scene.render.alpha_mode = origalphamode
class SkyboxButton(bpy.types.Operator):
	bl_idname = "quakemap.skybox"
	bl_label = "Generate Skybox"
	def execute(self,context):
		scene = context.scene
		#Find a camera
		camobj = None
		for obj in bpy.context.selected_objects:
			if obj.type == "CAMERA":
				camobj = obj
				break
		if camobj == None:
			for obj in bpy.data.objects:
				if obj.type == "CAMERA":
					camobj = obj
					break
		if camobj == None:
			popup("Skybox","Missing a camera in selection and scene.","ERROR")
		elif len(scene.skyboxdir) == 0 or len(scene.skyboxname) == 0:
			popup("Skybox","Missing skybox directory or name.","ERROR")
		elif scene.skyboxresx <= 0 or scene.skyboxresy <= 0:
			popup("Skybox","Image width and height must be at least 1.","ERROR")
		else:
			skybox(scene,camobj,scene.skyboxdir,scene.skyboxname,scene.skyboxresx,scene.skyboxresy)
		return{"FINISHED"}
def lightgrid_bake(origin,bounds,gridsize,scale):
	try:
		bpy.ops.object.mode_set(mode="OBJECT")
	except:
		pass
	bpy.ops.mesh.primitive_uv_sphere_add(segments = 8,ring_count = 4,size = 0.5)
	obj = bpy.context.object
	obj.scale = gridsize / scale
	bpy.ops.mesh.uv_texture_add()
	objpositions = []
	pindex = 0
	total = len(obj.data.polygons)
	increment = 1 / total
	for poly in obj.data.polygons:
		center = mathutils.Vector((0,0,0))
		for li,l in enumerate(poly.loop_indices):
			uv = obj.data.uv_layers.active.data[l]
			uv.uv[0] = increment * pindex
			uv.uv[1] = 0
			if li == 1 or li == 2:
				uv.uv[1] = 1
			if li == 2 or li == 3:
				uv.uv[0] += increment
			center += obj.data.vertices[obj.data.loops[l].vertex_index].co
		center /= len(poly.loop_indices)
		center.normalize()
		objpositions.append((center,pindex * 4))
		pindex += 1
	newimage = bpy.data.images.new(name = "Lightmap",width = total,height = 1,alpha = False)
	if bpy.context.scene.render.engine == "CYCLES":
		mat = bpy.data.materials.new("Mat")
		mat.use_nodes = True
		obj.data.materials.append(mat)
		node = mat.node_tree.nodes.new(type = "ShaderNodeTexImage")
		node.image = newimage
	else:
		for uvd in obj.data.uv_textures.active.data:
			uvd.image = newimage
	lightgrid = [None] * (bounds[0] * bounds[1] * bounds[2])
	for x in range(0,bounds[0]):
		for y in range(0,bounds[1]):
			for z in range(0,bounds[2]):
				index = (z * bounds[0] * bounds[1]) + (y * bounds[0]) + x
				xyz = mathutils.Vector((x,y,z))
				for i in range(0,3):
					obj.location[i] = (origin[i] + (xyz[i] * gridsize[i])) / scale
				print("Baking external at location: " + str(obj.location))
				if bpy.context.scene.render.engine == "CYCLES":
					bpy.ops.object.bake(type='COMBINED')
				else:
					bpy.ops.object.bake_image()
				dir = mathutils.Vector((0,0,0))
				ambient = mathutils.Vector((0,0,0))
				for position in objpositions:
					temp = mathutils.Vector((0,0,0))
					for i in range(0,3):
						temp[i] = newimage.pixels[position[1] + i]
						ambient[i] += math.pow(temp[i],2)
					dir += position[0] * temp.length
				ambient /= len(objpositions)#index
				directional = ambient.copy() * dir.length
				dir.normalize()
				dir *= -1
				if dir[0] == 0 and dir[1] == 0:
					if dir[2] > 0:
						longitude = 0
						latitude = 0
					else:
						longitude = 128
						latitude = 0
				else:
					rad2degree = 180.0 / math.pi
					longitude = int(math.acos(dir[2]) * rad2degree * 255.0 / 360.0)
					latitude = int(math.atan2(dir[1],dir[0]) * rad2degree * 255.0 / 360.0)
				lightgrid[index] = (ambient,directional,latitude,longitude)
	bpy.ops.object.mode_set(mode="EDIT")
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.flip_normals()
	bpy.ops.object.mode_set(mode="OBJECT")
	for x in range(0,bounds[0]):
		for y in range(0,bounds[1]):
			for z in range(0,bounds[2]):
				index = (z * bounds[0] * bounds[1]) + (y * bounds[0]) + x
				xyz = mathutils.Vector((x,y,z))
				for i in range(0,3):
					obj.location[i] = (origin[i] + (xyz[i] * gridsize[i])) / scale
				print("Baking internal at location: " + str(obj.location))
				if bpy.context.scene.render.engine == "CYCLES":
					bpy.ops.object.bake(type='COMBINED')
				else:
					bpy.ops.object.bake_image()
				average = mathutils.Vector((0,0,0))
				for pi,pixel in enumerate(newimage.pixels):
					rgbi = pi % 4
					if rgbi == 3:
						continue
					average[rgbi] += math.pow(pixel,2)
				average /= len(objpositions)#index
				ambient = lightgrid[index][0]
				if average.length > ambient.length:
					ambient = (ambient + average) / 2
	bpy.ops.object.delete()
	return lightgrid
def bsp_load(filepath):
	with open(filepath,"rb") as f:
		format = f.read(4)
		if format != b"RBSP" and format != b"IBSP":
			print("Unknown format")
			f.close()
			return None
		version = struct.unpack("<I",f.read(4))[0]
		table = [(0,0)] * 18
		marker = b""
		lumps = [None] * 18
		for i in range(0,18):
			table[i] = (struct.unpack("<I",f.read(4))[0],struct.unpack("<I",f.read(4))[0])
		while 1:
			byte = f.read(1)
			if byte == b"\0":
				break
			marker += byte
		for i in range(0,18):
			if table[i][0] > 0 and table[i][1] > 0:
				f.seek(table[i][0])
				lump = f.read(table[i][1])
				if len(lump) != table[i][1]:
					print("Table points to missing data.")
					f.close()
					return None
				lumps[i] = lump
		f.close()
		return (format,version,table,marker,lumps)
	return None
def bsp_save(filepath,format,version,marker,lumps):
	with open(filepath,"wb") as f:
		table = [(0,0)] * 18
		f.write(format)
		f.write(struct.pack("<I",version))
		f.write(b"\0" * (18 * 4 * 2))
		f.write(marker)
		for i,lump in enumerate(lumps):
			if lump == None:
				continue
			pos = (f.tell() + 3) & ~3
			f.seek(pos)
			table[i] = (pos,len(lump))
			f.write(lump)
		f.seek(8)
		for i in range(0,18):
			f.write(struct.pack("<II",table[i][0],table[i][1]))
		f.close()
		return True
	return False
def lightgrid(filepath,scale,lightscale):
	bsp = bsp_load(filepath)
	if bsp == None:
		print("Could not load bsp " + filepath)
		return
	if bsp[4][7] == None or len(bsp[4][7]) < 40:
		print("Worldspawn model is missing!")
		return
	worldbounds = struct.unpack("<ffffff16x",bsp[4][7])
	mins = (worldbounds[0] - 1,worldbounds[1] - 1,worldbounds[2] - 1)
	maxs = (worldbounds[3] + 1,worldbounds[4] + 1,worldbounds[5] + 1)
	gridsize = (64,64,128)
	entitylines = bsp[4][0].splitlines()
	for line in entitylines:
		linesep = line.split(sep=b"\"")
		if len(linesep) != 5:
			continue
		if linesep[1].lower() == b"gridsize":
			gridsizesplit = linesep[3].split()
			gridsize = (int(gridsizesplit[0]),int(gridsizesplit[1]),int(gridsizesplit[2]))
	origin = [0,0,0]
	bounds = [0,0,0]
	for i in range(0,3):
		origin[i] = gridsize[i] * math.ceil(mins[i] / gridsize[i])
		temp = gridsize[i] * math.floor(maxs[i] / gridsize[i])
		bounds[i] = int((temp - origin[i]) / gridsize[i] + 1)
	grid = lightgrid_bake(mathutils.Vector(origin),bounds,mathutils.Vector(gridsize),scale)
	newgrid = b""
	newarray = b""
	epsilon = 4
	usedgridarray = []
	for gi,g in enumerate(grid):
		if g == None:
			print("None type at index " + str(gi))
			break
		ambient = [int(g[0][0] * lightscale * 255),int(g[0][1] * lightscale * 255),int(g[0][2] * lightscale * 255)]
		for i in range(0,3):
			if ambient[i] > 255:
				ambient[i] = 255
		directional = [int(g[1][0] * lightscale * 255),int(g[1][1] * lightscale * 255),int(g[1][2] * lightscale * 255)]
		for i in range(0,3):
			if directional[i] > 255:
				directional[i] = 255
		lat = 255 if g[2] > 255 else g[2]
		long = 255 if g[3] > 255 else g[3]
		lat = 0 if lat < 0 else lat
		long = 0 if long < 0 else long
		if bsp[0] == b"RBSP":
			gridarray = (ambient[0],ambient[1],ambient[2],directional[0],directional[1],directional[2],lat,long)
			gridfound = False
			for gi2,gridarray2 in enumerate(usedgridarray):
				match = True
				for gi3 in range(0,len(gridarray)):
					if abs(gridarray[gi3] - gridarray2[gi3]) > epsilon:
						match = False
				if match == True:
					gridfound = True
					break
			if gridfound == True:
				newarray += struct.pack("<H",gi2)
			else:
				newgrid += struct.pack("BBB",ambient[0],ambient[1],ambient[2])
				newgrid += b"\0" * 9
				newgrid += struct.pack("BBB",directional[0],directional[1],directional[2])
				newgrid += b"\0" * 9
				newgrid += b"\x00\xff\xff\xff"
				newgrid += struct.pack("BB",lat,long)
				newarray += struct.pack("<H",len(usedgridarray))
				usedgridarray.append(gridarray)
				if len(usedgridarray) > 65535:
					print("Exceeded 65535 unique grids.")
					break
		else:
			newgrid += struct.pack("BBB",ambient[0],ambient[1],ambient[2])
			newgrid += struct.pack("BBB",directional[0],directional[1],directional[2])
			newgrid += struct.pack("BB",lat,long)
	bsp[4][15] = newgrid
	if bsp[0] == b"RBSP":
		bsp[4][17] = newarray
	if bsp_save(filepath,bsp[0],bsp[1],bsp[3],bsp[4]) == False:
		print("Could not save bsp " + filepath)
	print("Done")
	popup("Light-grid","Completed. Check console for possible errors.","NONE")
class LightgridButton(bpy.types.Operator):
	bl_idname = "quakemap.lightgrid"
	bl_label = "Overwrite Light-grid"
	def execute(self,context):
		scene = context.scene
		if len(scene.bsppath) == 0:
			popup("Light-grid","Missing BSP file path.","ERROR")
		elif bpy.context.scene.render.engine != "CYCLES" and bpy.context.scene.render.engine != "BLENDER_RENDER":
			popup("Light-grid","Only works with cycles or blender render","ERROR")
		else:
			lightgrid(scene.bsppath,scene.lightgridscale,scene.lightgridlightscale)
		return{"FINISHED"}
def lightgrid_removedirection(gridpos):
	r = int(math.sqrt((math.pow(gridpos[0],2) + math.pow(gridpos[3],2)) / 2)) & 255
	g = int(math.sqrt((math.pow(gridpos[1],2) + math.pow(gridpos[4],2)) / 2)) & 255
	b = int(math.sqrt((math.pow(gridpos[2],2) + math.pow(gridpos[5],2)) / 2)) & 255
	return (r,g,b,0,0,0,0,0)
class LightgridAverageButton(bpy.types.Operator):
	bl_idname = "quakemap.lightgridaverage"
	bl_label = "Remove"
	def execute(self,context):
		scene = context.scene
		if len(scene.bsppath) == 0:
			popup("Remove Directional Light-grid","Missing BSP file path.","ERROR")
		else:
			bsp = bsp_load(scene.bsppath)
			if bsp == None:
				popup("Remove Directional Light-grid","Could not load bsp " + scene.bsppath,"ERROR")
				return{"CANCELLED"}
			if bsp[0] == b"IBSP":
				newgrid = b""
				grids = [bsp[4][15][i:i + 8] for i in range(0,len(bsp[4][15]),8)]
				for gi,g in enumerate(grids):
					gu = struct.unpack("BBBBBBBB",g)
					gu = lightgrid_removedirection(gu)
					newgrid += struct.pack("BBBBBBBB",gu[0],gu[1],gu[2],gu[3],gu[4],gu[5],gu[6],gu[7])
				bsp[4][15] = newgrid
			else:
				newgrid = b""
				newarray = b""
				epsilon = 4
				usedgridarray = []
				grids = [bsp[4][15][i:i + 30] for i in range(0,len(bsp[4][15]),30)]
				array = [bsp[4][17][i:i + 2] for i in range(0,len(bsp[4][17]),2)]
				for a in array:
					index = struct.unpack("<H",a)[0]
					if index >= len(grids):
						popup("Remove Directional Light-grid","Grid array index out of bounds.","ERROR")
						return{"CANCELLED"}
					gu = struct.unpack("BBB9xBBB13xBB",grids[index])
					gu = lightgrid_removedirection(gu)
					gridfound = False
					for gi,g in enumerate(usedgridarray):
						match = True
						for gi2 in range(0,len(gu)):
							if abs(gu[gi2] - g[gi2]) > epsilon:
								match = False
						if match == True:
							gridfound = True
							break
					if gridfound == True:
						newarray += struct.pack("<H",gi)
					else:
						newgrid += struct.pack("BBB9xBBB9x4sBB",gu[0],gu[1],gu[2],gu[3],gu[4],gu[5],b"\x00\xff\xff\xff",gu[6],gu[7])
						newarray += struct.pack("<H",len(usedgridarray))
						usedgridarray.append(gu)
						if len(usedgridarray) > 65535:
							popup("Remove Directional Light-grid","Exceeded 65535 unique grids.","ERROR")
							return{"CANCELLED"}
				bsp[4][15] = newgrid
				bsp[4][17] = newarray
			if bsp_save(scene.bsppath,bsp[0],bsp[1],bsp[3],bsp[4]) == False:
				popup("Remove Directional Light-grid","Could not save bsp " + scene.bsppath,"ERROR")
				return{"CANCELLED"}
			popup("Remove Directional Light-grid","Completed","NONE")
			return{"FINISHED"}
		return{"CANCELLED"}
class ExtractEntitiesButton(bpy.types.Operator):
	bl_idname = "quakemap.extractentities"
	bl_label = "Extract"
	def execute(self,context):
		scene = context.scene
		if len(scene.bsppath) == 0:
			popup("Extract Entities","Missing BSP file path.","ERROR")
		elif len(scene.extractentities) == 0:
			popup("Extract Entities","Missing extract file path.","ERROR")
		else:
			bsp = bsp_load(scene.bsppath)
			if bsp == None:
				popup("Extract Entities","Could not load bsp " + scene.bsppath,"ERROR")
				return{"CANCELLED"}
			success = False
			with open(scene.extractentities,"wb") as f:
				entities = bsp[4][0]
				if entities[-1:] == b"\0":
					entities = entities[:-1]
				f.write(entities)
				f.close()
				success = True
			if success == False:
				popup("Extract Entities","Could not write to " + scene.extractentities,"ERROR")
				return{"CANCELLED"}
			popup("Extract Entities","Completed","NONE")
			return{"FINISHED"}
		return{"CANCELLED"}
class InsertEntitiesButton(bpy.types.Operator):
	bl_idname = "quakemap.insertentities"
	bl_label = "Insert"
	def execute(self,context):
		scene = context.scene
		if len(scene.bsppath) == 0:
			popup("Insert Entities","Missing BSP file path.","ERROR")
		elif len(scene.insertentities) == 0:
			popup("Insert Entities","Missing insert file path.","ERROR")
		else:
			bsp = bsp_load(scene.bsppath)
			if bsp == None:
				popup("Insert Entities","Could not load bsp " + scene.bsppath,"ERROR")
				return{"CANCELLED"}
			success = False
			with open(scene.insertentities,"rb") as f:
				contents = f.read()
				contents.replace(b"\r\n",b"\n")
				contents.replace(b"\r",b"\n")
				bsp[4][0] = contents + b"\0"
				f.close()
				success = True
			if success == False:
				popup("Insert Entities","Could not read from " + scene.insertentities,"ERROR")
				return{"CANCELLED"}
			if bsp_save(scene.bsppath,bsp[0],bsp[1],bsp[3],bsp[4]) == False:
				popup("Insert Entities","Could not save bsp " + scene.bsppath,"ERROR")
				return{"CANCELLED"}
			popup("Insert Entities","Completed","NONE")
			return{"FINISHED"}
		return{"CANCELLED"}
def shader_parse(shaders):
	shadersarray = [shaders[i:i + 72] for i in range(0,len(shaders),72)]
	shaderarray = []
	for s in shadersarray:
		shader = struct.unpack("<64sII",s)
		shaderarray.append((shader[0].rstrip(b"\0"),shader[1],shader[2]))
	return shaderarray
def shader_string(shaderarray):
	shaderstring = b""
	for s in shaderarray:
		shaderstring += struct.pack("<64sII",s[0],s[1],s[2])
	return shaderstring
class ExtractShadersButton(bpy.types.Operator):
	bl_idname = "quakemap.extractshaders"
	bl_label = "Extract"
	def execute(self,context):
		scene = context.scene
		if len(scene.bsppath) == 0:
			popup("Extract Shaders","Missing BSP file path.","ERROR")
		elif len(scene.extractshaders) == 0:
			popup("Extract Shaders","Missing extract file path.","ERROR")
		else:
			bsp = bsp_load(scene.bsppath)
			if bsp == None:
				popup("Extract Shaders","Could not load bsp " + scene.bsppath,"ERROR")
				return{"CANCELLED"}
			shaderarray = shader_parse(bsp[4][1])
			success = False
			with open(scene.extractshaders,"wb") as f:
				for shader in shaderarray:
					f.write(b"\"" + shader[0] + b"\",\"" + str(shader[1]).encode() + b"\",\"" + str(shader[2]).encode() + b"\"\n")
				f.close()
				success = True
			if success == False:
				popup("Extract Shaders","Could not write to " + scene.extractshaders,"ERROR")
				return{"CANCELLED"}
			popup("Extract Shaders","Completed","NONE")
			return{"FINISHED"}
		return{"CANCELLED"}
class InsertShadersButton(bpy.types.Operator):
	bl_idname = "quakemap.insertshaders"
	bl_label = "Insert"
	def execute(self,context):
		scene = context.scene
		if len(scene.bsppath) == 0:
			popup("Insert Shaders","Missing BSP file path.","ERROR")
		elif len(scene.insertshaders) == 0:
			popup("Insert Shaders","Missing insert file path.","ERROR")
		else:
			bsp = bsp_load(scene.bsppath)
			if bsp == None:
				popup("Insert Shaders","Could not load bsp " + scene.bsppath,"ERROR")
				return{"CANCELLED"}
			shaderarray = shader_parse(bsp[4][1])
			success = False
			with open(scene.insertshaders,"rb") as f:
				contents = f.read()
				contents = contents.splitlines()
				readarray = []
				for line in contents:
					if len(line) == 0:
						continue
					shader = line.split(sep = b"\"")
					if len(shader) != 7:
						popup("Insert Shaders","Invalid line: \"" + line.decode() + "\"","ERROR")
						f.close()
						return{"CANCELLED"}
					if len(shader[0]) > 64:
						popup("Insert Shaders","Shader exceeds 64 bytes: \"" + shader[1].decode() + "\"","ERROR")
						f.close()
						return{"CANCELLED"}
					try:
						readarray.append((shader[1],int(shader[3]),int(shader[5])))
					except:
						popup("Insert Shaders","Shader's second or third integer values are not valid: \"" + shader[1].decode() + "\"","ERROR")
						f.close()
						return{"CANCELLED"}
				f.close()
				if len(readarray) != len(shaderarray):
					popup("Insert Shaders","The number of shaders in " + scene.extractshaders + " does not match the BSP","ERROR")
					return{"CANCELLED"}
				bsp[4][1] = shader_string(readarray)
				success = True
			if success == False:
				popup("Insert Shaders","Could not read from " + scene.insertshaders,"ERROR")
				return{"CANCELLED"}
			if bsp_save(scene.bsppath,bsp[0],bsp[1],bsp[3],bsp[4]) == False:
				popup("Insert Shaders","Could not save bsp " + scene.bsppath,"ERROR")
				return{"CANCELLED"}
			popup("Insert Shaders","Completed","NONE")
			return{"FINISHED"}
		return{"CANCELLED"}
class ConvertBSPButton(bpy.types.Operator):
	bl_idname = "quakemap.convertbsp"
	bl_label = "Convert"
	def execute(self,context):
		scene = context.scene
		if len(scene.bsppath) == 0:
			popup("Convert BSP","Missing BSP file path.","ERROR")
		elif len(scene.convertbsp) == 0:
			popup("Convert BSP","Missing output BSP file path.","ERROR")
		else:
			bsp = bsp_load(scene.bsppath)
			if bsp == None:
				popup("Convert BSP","Could not load bsp " + scene.bsppath,"ERROR")
				return{"CANCELLED"}
			format = bsp[0]
			version = bsp[1]
			try:
				version = int(scene.convertbspversion)
			except:
				pass
			if bsp[0] == b"IBSP":
				format = b"RBSP"
				newgrid = b""
				newarray = b""
				epsilon = 4
				usedgridarray = []
				grids = [bsp[4][15][i:i + 8] for i in range(0,len(bsp[4][15]),8)]
				for gi,g in enumerate(grids):
					gu = struct.unpack("BBBBBBBB",g)
					gridfound = False
					for gi2,g2 in enumerate(usedgridarray):
						match = True
						for gi3 in range(0,len(gu)):
							if abs(gu[gi3] - g2[gi3]) > epsilon:
								match = False
						if match == True:
							gridfound = True
							break
					if gridfound == True:
						newarray += struct.pack("<H",gi2)
					else:
						newgrid += struct.pack("BBB9xBBB9x4sBB",gu[0],gu[1],gu[2],gu[3],gu[4],gu[5],b"\x00\xff\xff\xff",gu[6],gu[7])
						newarray += struct.pack("<H",len(usedgridarray))
						usedgridarray.append(gu)
						if len(usedgridarray) > 65535:
							popup("Convert BSP","Exceeded 65535 unique grids.","ERROR")
							return{"CANCELLED"}
				bsp[4][15] = newgrid
				bsp[4][17] = newarray
			else:
				format = b"IBSP"
				newgrid = b""
				grids = [bsp[4][15][i:i + 30] for i in range(0,len(bsp[4][15]),30)]
				array = [bsp[4][17][i:i + 2] for i in range(0,len(bsp[4][17]),2)]
				for a in array:
					index = struct.unpack("<H",a)[0]
					if index >= len(grids):
						popup("Convert BSP","Grid array index out of bounds.","ERROR")
						return{"CANCELLED"}
					gu = struct.unpack("BBB9xBBB13xBB",grids[index])
					newgrid += struct.pack("BBBBBBBB",gu[0],gu[1],gu[2],gu[3],gu[4],gu[5],gu[6],gu[7])
				bsp[4][15] = newgrid
				bsp[4][17] = b""
			if bsp_save(scene.convertbsp,format,version,bsp[3],bsp[4]) == False:
				popup("Convert BSP","Could not save bsp " + scene.convertbsp,"ERROR")
				return{"CANCELLED"}
			popup("Convert BSP","Completed conversion to " + format.decode(),"NONE")
			return{"FINISHED"}
		return{"CANCELLED"}
bpy.types.Object.noexport = BoolProperty(name = "Do Not Export",description = "Object will not be exported.",default = False)
bpy.types.Object.shadows = BoolProperty(name = "Cast Shadows",description = "Model shader name will have \"_RMG_BSP\" appended instead of \"_BSP\"",default = False)
bpy.types.Object.autoclip = BoolProperty(name = "Auto-clip",description = "Generate a solid brush for model.",default = False)
bpy.types.Object.forcemeta = BoolProperty(name = "Force meta",description = "Allows model to have a lightmap.",default = False)
bpy.types.Object.modelbrush = BoolProperty(name = "Model Brush",description = "Allows model to have a brush set as well. Makes auto-clip redundant.",default = False)
bpy.types.Object.modelname = StringProperty(name = "Model Name",description = "For obj path, shader, and jpg texture paths.")
bpy.types.Object.animmodel = BoolProperty(name = "Animation",description = "Model will be exported as an MD3. Make sure mesh is triangulated.",default = False)
bpy.types.Object.fps = StringProperty(name = "FPS",description = "Frames per second. Default is 20.")
bpy.types.Object.startframe = StringProperty(name = "Start Frame",description = "Start frame number.")
bpy.types.Object.numframes = StringProperty(name = "Number of Frames",description = "Number of frames after start frame to export.")
bpy.types.Object.tagname = StringProperty(name = "MD3 Tag Name",description = "Set on objects parented to an Animation model object.",maxlen = 64)
bpy.types.Object.nomodelent = BoolProperty(name = "No Model Entity",description = "No misc_model or misc_anim_model entity is added for the model.",default = False)
bpy.types.Object.castshadows = BoolProperty(name = "Cast Shadows",description = "Model will cast shadows during light stage.",default = False)
bpy.types.Object.recvshadows = BoolProperty(name = "Receive Shadows",description = "Model will receive shadows during light stage.",default = False)
bpy.types.Object.convexbrush = BoolProperty(name = "Convex Brushes",description = "Each linked mesh of the object becomes a single brush.",default = False)
bpy.types.Object.detailbrush = BoolProperty(name = "Detail Brushes",description = "Brush faces will not be included in vis calculation. Can be overrided per material.",default = False)
bpy.types.Object.hiddendetailbrush = BoolProperty(name = "Hidden Detail Brushes",description = "Hidden Brush faces will not be included in vis calculation. Can be overrided per material.",default = False)
bpy.types.Object.texture = StringProperty(name = "Texture",description = "Texture for visible brush faces or models. Can be overrided per material.")
bpy.types.Object.hiddentexture = StringProperty(name = "Hidden Texture",description = "Texture for hidden(generated) brush faces. Can be overrided per material.")
bpy.types.Object.brushwidth = StringProperty(name = "Brush Width",description = "Thickness of each face. Default is 2.0.")
bpy.types.Object.classname = StringProperty(name = "Classname",description = "Entity or brush group classname.")
bpy.types.Object.targetname = StringProperty(name = "Target Name",description = "Entity or brush group targetname.")
bpy.types.Object.target = StringProperty(name = "Target",description = "Entity or brush group target.")
bpy.types.Object.origin = StringProperty(name = "Origin",description = "Overrides entity origin.")
bpy.types.Object.angles = StringProperty(name = "Angles",description = "Overrides entity angles.")
bpy.types.Object.junior = BoolProperty(name = "Junior",description = "Light source will only affect entities.",default = False)
bpy.types.Object.light = StringProperty(name = "Light",description = "Overrides calculated light intensity.")
bpy.types.Object.fade = StringProperty(name = "Fade",description = "Light attenuation for linear lights. Default is 1.0.")
bpy.types.Object.radius = StringProperty(name = "Radius",description = "Radius by distance. Default is 64.")
bpy.types.Object.sun = BoolProperty(name = "Sun",description = "Turns light into sun emitter. Default is off.",default = False)
bpy.types.Object.linear = BoolProperty(name = "Linear",description = "Light source will have a linear falloff(attenuation) with distance. Spot lights only have non-linear angled attenuation with fade of 1.",default = False)
bpy.types.Object.noangle = BoolProperty(name = "No Angle",description = "Light source will not have attenuation.",default = False)
bpy.types.Object.nogridlight = BoolProperty(name = "No grid light",description = "Light source will not have dynamic entity lighting.",default = False)
bpy.types.Material.shader = StringProperty(name = "Shader",description = "Shader name for model surface material. Defaults to material name.")
bpy.types.Material.noimage = BoolProperty(name = "No Image",description = "Don't export image texture for material.")
bpy.types.Material.detailbrush = BoolProperty(name = "Detail Brush",description = "Brush faces will not be included in vis calculation. Overrides object's detail brush value.",default = False)
bpy.types.Material.hiddendetailbrush = BoolProperty(name = "Hidden Detail Brush",description = "Hidden Brush faces will not be included in vis calculation. Overrides object's hidden detail brush value.",default = False)
bpy.types.Material.texture = StringProperty(name = "Texture",description = "Texture for visible brush faces or models. Overrides object's texture value.")
bpy.types.Material.hiddentexture = StringProperty(name = "Hidden Texture",description = "Texture for hidden(generated) brush faces. Overrides object's hiddentexture value.")
bpy.types.Material.brushwidth = StringProperty(name = "Brush Width",description = "Thickness of each face. Default is 2.0")
class ObjectPanel(bpy.types.Panel):
	bl_label = "Quake Map Options"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"
	def draw(self,context):
		if context.object:
			self.layout.prop(context.object,"noexport")
			box = self.layout.box()
			box.label("Model Options(Object must have UV map)")
			box.prop(context.object,"modelbrush")
			box.prop(context.object,"modelname")
			box.prop(context.object,"nomodelent")
			box.prop(context.object,"castshadows")
			box.prop(context.object,"recvshadows")
			box2 = box.box()
			box2.label("Model Spawnflags(Not for Animation)")
			box2.prop(context.object,"shadows")
			box2.prop(context.object,"autoclip")
			box2.prop(context.object,"forcemeta")
			box2.operator("quakemap.spawnflags")
			box.prop(context.object,"animmodel")
			box2 = box.box()
			box2.label("Model Animation Options")
			box2.prop(context.object,"fps")
			box2.prop(context.object,"startframe")
			box2.prop(context.object,"numframes")
			box2.prop(context.object,"tagname")
			box = self.layout.box()
			box.label("Brush Options")
			box.prop(context.object,"convexbrush")
			box.prop(context.object,"detailbrush")
			box.prop(context.object,"hiddendetailbrush")
			box = box.box()
			box.label("Brush Overrides")
			box.prop(context.object,"texture")
			box.prop(context.object,"hiddentexture")
			box.prop(context.object,"brushwidth")
			box = self.layout.box()
			box.label("Entity Properties")
			box.prop(context.object,"classname")
			box.prop(context.object,"targetname")
			box.prop(context.object,"target")
			box.prop(context.object,"origin")
			box.prop(context.object,"angles")
			box = self.layout.box()
			box.label("Light Properties")
			box.prop(context.object,"junior")
			box.prop(context.object,"light")
			box.prop(context.object,"fade")
			box2 = box.box()
			box2.label("Spot Light Properties")
			box2.prop(context.object,"radius")
			box2.prop(context.object,"sun")
			box2 = box.box()
			box2.label("Light Spawnflags")
			box2.prop(context.object,"linear")
			box2.prop(context.object,"noangle")
			box2.prop(context.object,"nogridlight")
			box2.operator("quakemap.lightspawnflags")
class Spawnflags(bpy.types.Operator):
	bl_idname = "quakemap.spawnflags"
	bl_label = "Set Spawnflags"
	def execute(self,context):
		val = 0
		if context.object.shadows:
			val |= 1
		if context.object.autoclip:
			val |= 2
		if context.object.forcemeta:
			val |= 4
		context.object["spawnflags"] = val
		return{'FINISHED'}
class LightSpawnflags(bpy.types.Operator):
	bl_idname = "quakemap.lightspawnflags"
	bl_label = "Set Spawnflags"
	def execute(self,context):
		val = 0
		if context.object.linear:
			val |= 1
		if context.object.noangle:
			val |= 2
		if context.object.nogridlight:
			val |= 16
		context.object["spawnflags"] = val
		return{'FINISHED'}
class MaterialPanel(bpy.types.Panel):
	bl_label = "Quake Map Options"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "material"
	def draw(self,context):
		if context.material:
			box = self.layout.box()
			box.label("Model Options")
			box.prop(context.material,"shader")
			box.prop(context.material,"noimage")
			box = self.layout.box()
			box.label("Brush Options")
			box.prop(context.material,"detailbrush")
			box.prop(context.material,"hiddendetailbrush")
			box = box.box()
			box.label("Brush Overrides")
			box.prop(context.material,"texture")
			box.prop(context.material,"hiddentexture")
			box.prop(context.material,"brushwidth")
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(export)
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(export)
if __name__ == "__main__":
  register()
