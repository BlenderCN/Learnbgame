from struct  import unpack
from sys     import argv
from os.path import split, splitext, join
from io      import BytesIO as bio
import bpy, bmesh

def readnulltermstring(input,skip=False):
	if type(input) in (str, bytes): #else it's a file object
		null = '\0' if type(input)==str else b'\0'
		return input[:input.index(null)] if null in input else input
	if skip:
		while 1:
			c = input.read(1)
			if not c or c == b'\0': return
	buildstring = bytearray()
	while 1:
		c = input.read(1)
		if not c or c == b'\0': return buildstring
		buildstring += c

def open_lr2(filepath, **kwargs):
	first4 = open(filepath,'rb').read(4)
	if   first4 == b'MDL2': return open_mdl2(filepath, **kwargs)
	elif first4 == b'MDL1': return open_mdl2(filepath, **kwargs)
	elif first4 == b'MDL0': return open_mdl0(filepath, **kwargs)
	else: raise AssertionError('Input file is not a supported type; expected signature to be MDL2, MDL1, or MDL0, recieved %s.' % str(first4)[2:-1])

def buildfaces(work_bmesh, mdl0_fill_type, mdl0_polygons, f):
	if mdl0_fill_type == 0:
		for face in range(mdl0_polygons):
			try:
				work_bmesh.faces.new((work_bmesh.verts[x] for x in unpack('3H', f.read(6))))
			except ValueError: # accounts for models of type double, but does not fix the problem
				print('Face %i is two-sided, and this is unsupported.' % face)
	elif mdl0_fill_type == 1:
		vertexbuffer = [*unpack('2H', f.read(4))]
		for face in range(mdl0_polygons):
			print(hex(f.tell()))
			vertexbuffer += [*unpack('H', f.read(2))]
			try:
				work_bmesh.faces.new(work_bmesh.verts[v] for v in vertexbuffer)
			except ValueError:
				print('Face %i is two-sided, and this is unsupported.' % face)
			del vertexbuffer[0]
	else:
		raise AssertionError('Unsupported primitive fill type. (%i)' % mdl0_fill_type)
	
VERTEX_HAS_VECTOR = 0b0001 # invariable
VERTEX_HAS_NORMAL = 0b0010 # invariable
VERTEX_HAS_COLOR  = 0b0100 # only set in a few models
VERTEX_HAS_UV     = 0b1000 # invariable
def open_mdl2(filepath, open_bitmaps = True):
	f = open(filepath,'rb')
	
	if open_bitmaps:
		try: rootpath = filepath[:filepath.lower().index('game data')]
		except ValueError:
			open_bitmaps = False
			print('Could not trace back to root directory "GAME DATA".')
		
	bpy.ops.object.empty_add()
	obj_root = bpy.context.scene.objects[0]
	obj_root.name = splitext(split(filepath)[1])[0]
	
	bitmaps  = []
	matprops = []
	objects  = []
	
	chunk_name = f.read(4)
	chunk_size = unpack('I', f.read(4))
	if chunk_name == b'MDL2':
		# variable
		# variable
		# variable, 0 for map landmarks, 1 for small objects
		# always 1
		mdl2_inertiamulti   = unpack('3f', f.read(12))
		mdl2_boundingradius,\
		mdl2_distancefades ,\
		mdl2_hasboundingbox = unpack('f2I', f.read(12))
		
		if mdl2_hasboundingbox:
			mdl2_boundingboxmin    = unpack('3f', f.read(12))
			mdl2_boundingboxmax    = unpack('3f', f.read(12))
			mdl2_boundingboxcenter = unpack('3f', f.read(12))
			mdl2_boundingboxroty   = unpack('f', f.read(4))
			
		# always 0
		# always 0
		# always 0
		# always 0
		mdl2_useuniquematerials,\
		mdl2_useuniquetextures ,\
		mdl2_usegenericgeometry,\
		mdl2_vertexbufferflags  = unpack('4I', f.read(16)) # all these fields appear unused
		f.seek(f.tell() + 48)
		
		# variable
		mdl2_bitmap_count = unpack('I', f.read(4))[0]
		print('	Textures:', mdl2_bitmap_count)
		for bitmap_id in range(mdl2_bitmap_count):
			bitmap_path  = readnulltermstring(f.read(256)).decode('utf8')
			bitmap_type  ,\
			bitmap_index = unpack('2I', f.read(8))
			print('		' + bitmap_path)
			bitmaps += [(bitmap_path, bitmap_type, bitmap_index)]
		materials = [bpy.data.materials.new(x[0]) for x in bitmaps]
		
		# variable
		mdl2_matprop_count = unpack('I', f.read(4))[0]
		for matprop_id in range(mdl2_matprop_count):
			mdl2_matprop_ambient   = unpack('4f', f.read(16))
			mdl2_matprop_diffuse   = unpack('4f', f.read(16))
			mdl2_matprop_specular  = unpack('4f', f.read(16))
			mdl2_matprop_emissive  = unpack('4f', f.read(16))
			mdl2_matprop_shine     ,\
			mdl2_matprop_alpha     ,\
			mdl2_matprop_alphatype ,\
			mdl2_matprop_bitfield  = unpack('2f2I', f.read(16))
			mdl2_matprop_animname  = readnulltermstring(f.read(8))
			matprops += [(
				mdl2_matprop_ambient  ,
				mdl2_matprop_diffuse  ,
				mdl2_matprop_specular ,
				mdl2_matprop_emissive ,
				mdl2_matprop_shine    ,
				mdl2_matprop_alpha    ,
				mdl2_matprop_alphatype,
				mdl2_matprop_bitfield ,
				mdl2_matprop_animname ,
			)]
	elif chunk_name == b'MDL1':
		# variable
		# variable
		# variable, 0 for map landmarks, 1 for small objects
		# always 1
		mdl2_inertiamulti   = unpack('3f', f.read(12))
		mdl2_boundingradius,\
		mdl2_distancefades ,\
		mdl2_hasboundingbox = unpack('f2I', f.read(12))
		
		if mdl2_hasboundingbox:
			mdl2_boundingboxmin    = unpack('3f', f.read(12))
			mdl2_boundingboxmax    = unpack('3f', f.read(12))
			mdl2_boundingboxcenter = unpack('3f', f.read(12))
			mdl2_boundingboxroty   = unpack('f', f.read(4))
			
		# always 0
		# always 0
		# always 0
		# always 0
		mdl2_useuniquematerials,\
		mdl2_useuniquetextures ,\
		mdl2_usegenericgeometry,\
		mdl2_vertexbufferflags  = unpack('4I', f.read(16)) # all these fields appear unused
		f.seek(f.tell() + 48)
		
		# variable
		mdl2_bitmap_count = unpack('I', f.read(4))[0]
		print('	Textures:', mdl2_bitmap_count)
		for bitmap_id in range(mdl2_bitmap_count):
			bitmap_path  = readnulltermstring(f.read(256)).decode('utf8')
			bitmap_type  ,\
			bitmap_index = unpack('2I', f.read(8))
			print('		' + bitmap_path)
			bitmaps += [(bitmap_path, bitmap_type, bitmap_index)]
		materials = [bpy.data.materials.new(x[0]) for x in bitmaps]
		
		# variable
		mdl2_matprop_count = unpack('I', f.read(4))[0]
		for matprop_id in range(mdl2_matprop_count):
			mdl2_int0  ,\
			mdl2_float0,\
			mdl2_float1,\
			mdl2_float2,\
			mdl2_float3,\
			mdl2_float4,\
			mdl2_float5 = unpack('I6f', f.read(28))
			matprops += [(
				mdl2_int0  ,
				mdl2_float0,
				mdl2_float1,
				mdl2_float2,
				mdl2_float3,
				mdl2_float4,
				mdl2_float5,
			)]
	else: return
			
	
	offset = f.tell()
	while 1:
		chunk_name = f.read(4)
		if chunk_name == b'\0\0\0\0' or not chunk_name: break
		chunk_size = unpack('I', f.read(4))[0]
		
		print('%s: %s' % (chunk_name.decode('ascii'), hex(chunk_size)))
		
		if chunk_name == b'GEO1':
			#variable
			geo1_detaillevels = unpack('I', f.read(4))[0]
			
			detaillevel_string = 'Detail level %%0%ii' % len(str(geo1_detaillevels))
			for detaillevel_id in range(geo1_detaillevels):
				bpy.ops.object.empty_add()
				dl_root = bpy.context.scene.objects[0]
				dl_root.name = detaillevel_string % detaillevel_id
				dl_root.parent = obj_root
				
				# variable; 0 for base mesh, 1 for distant mesh (model type distant)
				# variable, unknown purpose, is the distance between the two most distant connected vertices
				# variable, detail level is split into submeshes as textures are applied per submesh
				geo1_detaillevel_type         ,\
				geo1_detaillevel_maxedgelength,\
				geo1_rendergroups       = unpack('IfI', f.read(12))
				f.seek(f.tell() + 8)
				
				rendergroup_string = 'Rendergroup %%0%ii (Material %%0%ii)' % (len(str(geo1_rendergroups)), len(str(len(bitmaps))))
				for rendergroup_id in range(geo1_rendergroups):
					# variable
					# variable
					# variable
					# 512 in rgeffects models, else 0
					work_bmesh = bmesh.new()
					geo1_rendergroup_polygons,\
					geo1_rendergroup_vertices,\
					geo1_rendergroup_material,\
					geo1_rendergroup_effects  = unpack('4H', f.read(8))
					f.seek(f.tell() + 12)
					
					# variable as 3, 9, 17, or 513 in effects models, else 0
					# always 0
					# 2 in effects models, else always 1
					# always 0
					# 2 in flow models, else always 1
					geo1_texblend_effectmask     ,\
					geo1_texblend_renderreference,\
					geo1_texblend_effects        ,\
					geo1_texblend_custom         ,\
					geo1_texblend_coordinates     = unpack('3H2B', f.read(8))
					geo1_texblend_blends          = tuple(unpack('IH2B', f.read(8)) for x in range(4))
					# I effect         
					# H textureindex    # the bitmap used on the rendergroup
					# B coordinateindex
					# B tilinginfo      # 0x3 = tiling enabled, 0 = disabled
					
					# always 0
					# always 12
					# variable (trash memory if not geo1_vertex_flags & VERTEX_HAS_COLOR)
					# variable on account of previous int
                    # variable on account of previous ints
					# either 1, or 2 (rare)
					# see VERTEX_HAS_VECTOR and related
					# identical to geo1_rendergroup_vertices
					# always 1
					# either 15998, 16256, or 0
					geo1_vertex_offset_vector  ,\
					geo1_vertex_offset_normal  ,\
					geo1_vertex_offset_colour  ,\
					geo1_vertex_offset_texcoord,\
					geo1_vertex_size_vertstruct,\
					geo1_vertex_num_texcoords  ,\
					geo1_vertex_flags          ,\
					geo1_vertex_vertices       ,\
					geo1_vertex_managedbuffer  ,\
					geo1_vertex_currentvertex   = unpack('4I2I4H', f.read(32))
					f.seek(f.tell() + 8)
					
					for vertex in range(geo1_vertex_vertices): work_bmesh.verts.new()
					work_bmesh.verts.ensure_lookup_table()
					
					uvs = []
					normals = []
					for vertex in range(geo1_vertex_vertices):
						vstruct = bio(f.read(geo1_vertex_size_vertstruct))
						vertex_xyz    = unpack('3f', vstruct.read(12))[::-1]
						vertex_normal = unpack('3f', vstruct.read(12))[::-1]
						if geo1_vertex_flags & VERTEX_HAS_COLOR:
							vertex_color = unpack('4f', vstruct.read(16))
						for texcoord_id in range(geo1_vertex_num_texcoords):
							vertex_uv     = unpack('2f', vstruct.read(8))
						work_bmesh.verts[vertex].co = vertex_xyz
						normals += [vertex_normal]
						uvs += [vertex_uv]
					
					# always 1
					# always 0
					# always equal to (geo1_rendergroup_polygons*3)
					geo1_fill_selectableprimblocks,\
					geo1_fill_type                ,\
					geo1_fill_indices              = unpack('3I', f.read(12))
					
					buildfaces(work_bmesh, geo1_fill_type, geo1_rendergroup_polygons, f)
					
					### uv
					work_bmesh.faces.ensure_lookup_table()
					work_bmesh.verts.index_update()
					uv_layer = work_bmesh.loops.layers.uv.new()
					for face in work_bmesh.faces:
						for loop in face.loops: loop[uv_layer].uv = uvs[loop.vert.index]
					### uv
					
					work_mesh = bpy.data.meshes.new(rendergroup_string % (rendergroup_id, geo1_texblend_blends[0][1]))
					work_bmesh.to_mesh(work_mesh)
					
					#### normal test
					work_mesh.normals_split_custom_set_from_vertices(normals)
					work_mesh.use_auto_smooth = True
					#### normal test
					
					work_obj = bpy.data.objects.new(rendergroup_string % (rendergroup_id, geo1_texblend_blends[0][1]), work_mesh)
					work_obj.data.materials.append(materials[geo1_texblend_blends[0][1]])
					work_obj.parent = dl_root
					bpy.context.scene.objects.link(work_obj)
		
		offset += 8 + chunk_size
		f.seek(offset)
	f.close()
	
	obj_root.rotation_euler = (__import__('math').pi / 2, 0, 0)
	
	if open_bitmaps:
		for bitmap in bitmaps:
			try:
				bpy.ops.image.open(filepath = join(rootpath, splitext(bitmap[0])[0] + '.mip'))
			except RuntimeError:
				print('Failed to open image %s' % (splitext(bitmap[0])[0] + '.mip'))

def open_mdl0(filepath, open_bitmaps = True):
	f = open(filepath,'rb')
	
	if open_bitmaps:
		try: rootpath = filepath[:filepath.lower().index('game data')]
		except ValueError:
			open_bitmaps = False
			print('Could not trace back to root directory "GAME DATA".')
		
	work_bmesh = bmesh.new()
	
	offset   = 0
	bitmaps  = []
	matprops = []
	objects  = []
	
	mdl0_signature,\
	mdl0_int      ,\
	mdl0_int      ,\
	mdl0_int      ,\
	mdl0_float    ,\
	mdl0_bitmaps   = unpack('4s3IfI', f.read(24))
	
	for bitmap_id in range(mdl0_bitmaps):
		bitmaps += [readnulltermstring(f.read(256)).decode('utf8')]
	materials = [bpy.data.materials.new(x) for x in bitmaps]
	
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_float   ,\
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_polygons,\
	mdl0_vertices,\
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_int     ,\
	mdl0_int      = unpack('8If3I2H4I', f.read(68))
	
	mdl0_texblend_effectmask     ,\
	mdl0_texblend_renderreference,\
	mdl0_texblend_effects        ,\
	mdl0_texblend_custom         ,\
	mdl0_texblend_coordinates     = unpack('3H2B', f.read(8))
	mdl0_texblend_blends          = tuple(unpack('IH2B', f.read(8)) for x in range(4))
	# I effect         
	# H textureindex    # the bitmap used on the rendergroup
	# B coordinateindex
	# B tilinginfo      # 0x3 = tiling enabled, 0 = disabled

	# always 0
	# always 12
	# variable (trash memory if not geo1_vertex_flags & VERTEX_HAS_COLOR)
	# variable on account of previous int
    # variable on account of previous ints
	# either 1, or 2 (rare)
	# see VERTEX_HAS_VECTOR and related
	# identical to geo1_rendergroup_vertices
	# always 1
	# either 15998, 16256, or 0
	mdl0_vertex_offset_vector  ,\
	mdl0_vertex_offset_normal  ,\
	mdl0_vertex_offset_colour  ,\
	mdl0_vertex_offset_texcoord,\
	mdl0_vertex_size_vertstruct,\
	mdl0_vertex_num_texcoords  ,\
	mdl0_vertex_flags          ,\
	mdl0_vertex_vertices       ,\
	mdl0_vertex_managedbuffer  ,\
	mdl0_vertex_currentvertex   = unpack('4I2I4H', f.read(32))
	f.seek(f.tell() + 8)
	
	uvs = []
	normals = []
	for vertex in range(mdl0_vertices):
		vstruct = bio(f.read(mdl0_vertex_size_vertstruct))
		vertex_xyz    = unpack('3f', vstruct.read(12))[::-1]
		vertex_normal = unpack('3f', vstruct.read(12))[::-1]
		if mdl0_vertex_flags & VERTEX_HAS_COLOR:
			vertex_color = unpack('4f', vstruct.read(16))
		for texcoord_id in range(mdl0_vertex_num_texcoords):
			vertex_uv     = unpack('2f', vstruct.read(8))
		work_bmesh.verts.new(vertex_xyz)
		normals += [vertex_normal]
		uvs += [vertex_uv]
	work_bmesh.verts.ensure_lookup_table()
	work_bmesh.verts.index_update()
	
	mdl0_fill_type = unpack('I', f.read(4))[0]
	
	buildfaces(work_bmesh, mdl0_fill_type, mdl0_polygons, f)
	
	### uv
	work_bmesh.faces.ensure_lookup_table()
	uv_layer = work_bmesh.loops.layers.uv.new()
	for face in work_bmesh.faces:
		for loop in face.loops: loop[uv_layer].uv = uvs[loop.vert.index]
	### uv
	
	work_mesh = bpy.data.meshes.new('MDL0 mesh')
	work_bmesh.to_mesh(work_mesh)
	
	#### normal test
	work_mesh.normals_split_custom_set_from_vertices(normals)
	work_mesh.use_auto_smooth = True
	#### normal test
	
	work_obj = bpy.data.objects.new(splitext(split(filepath)[1])[0], work_mesh)
	work_obj.data.materials.append(materials[0])
	bpy.context.scene.objects.link(work_obj)
	
	f.close()
	
	work_obj.rotation_euler = (__import__('math').pi / 2, 0, 0)
	
	if open_bitmaps:
		for bitmap in bitmaps:
			try:
				bpy.ops.image.open(filepath = join(rootpath, splitext(bitmap[0])[0] + '.mip'))
			except RuntimeError:
				print('Failed to open image "%s"' % (splitext(bitmap[0])[0] + '.mip'))