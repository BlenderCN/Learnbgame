from struct  import unpack
from sys     import argv
from os.path import split, splitext, join
from io      import BytesIO as bio
from ast     import literal_eval as leval
import bpy, bmesh
	
VERTEX_HAS_VECTOR = 0b0001 # invariable
VERTEX_HAS_NORMAL = 0b0010 # invariable
VERTEX_HAS_COLOR  = 0b0100 # only set in a few models
VERTEX_HAS_UV     = 0b1000 # invariable

BUFFERACCESSFLAGS = {
	1: 'READ' ,
	2: 'WRITE',
}

i2b = lambda i: 'false' if not i else 'true' if i == 1 else str(i)
i2f = lambda i, f = {}: '0' if not i else ' | '.join(f[i & (1 << b)] if i & (1 << b) in f else '0x' + ('%x' % (i & (1 << b))).upper() for b in range(i.bit_length()) if i & (1 << b))
i2x = lambda i: '0x' + ('%x' % i).upper()

def readnulltermstring(input, skip=False):
	if type(input) in (str, bytes): # else it's a file object
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

def open_atd(filepath, **kwargs):
	first4 = open(filepath,'rb').read(4)
	if   first4 == b'MDL0': return open_mdl0(filepath, **kwargs)
	elif first4 == b'MDL1': return open_mdl1(filepath, **kwargs)
	elif first4 == b'MDL2': return open_mdl2(filepath, **kwargs)
	elif first4 == b'MDL3': return open_mdl3(filepath, **kwargs)
	else: raise AssertionError('Input file is not a supported type; expected signature to be MDL2, MDL1, or MDL0, recieved "%s".' % str(first4)[2:-1])

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

#def buildbitmaplist(f, head_bitmap_count):
#	bitmaps = [None]*head_bitmap_count
#	print('\tBitmaps:', head_bitmap_count)
#	for bitmap_id in range(head_bitmap_count):
#		bitmap_path = readnulltermstring(f.read(256)).decode('utf8')
#		(
#			bitmap_type ,
#			bitmap_index,
#		) = unpack('2I', f.read(8))
#		print(('\t\t %s ' % bitmap_index) + bitmap_path)
#		bitmaps[bitmap_index] = (bitmap_path, bitmap_type)
#	assert None not in bitmaps and len(bitmaps) == head_bitmap_count, 'There was an error in sorting the bitmaps.'
#	return bitmaps
	
def buildbitmaplist(f, head_bitmap_count):
	bitmaps = []
	print('Bitmaps:', head_bitmap_count)
	for bitmap_id in range(head_bitmap_count):
		bitmap_path = readnulltermstring(f.read(256)).decode('utf8')
		(
			bitmap_type ,
			bitmap_index,
		) = unpack('2I', f.read(8))
		print(('\t %s ' % bitmap_index) + bitmap_path)
		bitmaps += [(bitmap_path, bitmap_type, bitmap_index)]
	return bitmaps
		
def openbitmaps(filepath, bitmaps): # only works on lego racers 2's .mip (renamed .tga)
	try: rootpath = filepath[:filepath.lower().index('game data')]
	except ValueError: print('Could not trace back to root directory "GAME DATA".')
	else:
		for bitmap in bitmaps:
			mip = splitext(bitmap[0])[0] + '.mip'
			try: bpy.ops.image.open(filepath = join(rootpath, mip))
			except RuntimeError: print('Failed to open image "%s".' % mip)

def open_mdl2(filepath, usebitmaps = True, usetext = True):
	f = open(filepath,'rb')
	fn = splitext(split(filepath)[1])[0]
	bpy.ops.object.empty_add()
	obj_root = bpy.context.scene.objects[0]
	obj_root.name = fn
	
	if usetext:
		text = bpy.data.texts.new(fn)
		text.write(
			'# Model configuration file for Lego Racers 2\n'
			'# Keep this file named the same as your root to export with its settings.\n\n'
		)
	
	chunk_name = f.read(4)
	chunk_size = unpack('I', f.read(4))
	head_inertiamulti   = unpack('3f', f.read(12))
	head_boundingradius = unpack('f',  f.read(4))
	(
		head_distancefades , # boolean, 0 for map landmarks, 1 for small objects
		head_hasboundingbox, # always 1
	) = unpack('2I', f.read(8))
	
	if usetext: ###########################
		text.write(
			'InertiaTensor  = %.06f, %.06f, %.06f\n' % head_inertiamulti        +
			'BoundingRadius = %.06f\n'               % head_boundingradius      +
			'DistanceFades  = %s\n'                  % i2b(head_distancefades)  +
			'HasBoundingBox = %s\n\n'                % i2b(head_hasboundingbox)
		)
		
	if head_hasboundingbox:
		head_boundingboxmin    = unpack('3f', f.read(12))
		head_boundingboxmax    = unpack('3f', f.read(12))
		head_boundingboxcenter = unpack('3f', f.read(12))
		head_boundingboxroty   = unpack('f',  f.read(4))
	
		if usetext: ##########################
			text.write(
				'BoundingBoxMin    = %.06f, %.06f, %.06f\n' % head_boundingboxmin    +
				'BoundingBoxMax    = %.06f, %.06f, %.06f\n' % head_boundingboxmax    +
				'BoundingBoxCenter = %.06f, %.06f, %.06f\n' % head_boundingboxcenter +
				'BoundingBoxYaw    = %.06f\n\n'             % head_boundingboxroty
			)
		
	( # all these fields appear unused and always 0
		head_useuniquematerials,
		head_useuniquetextures ,
		head_usegenericgeometry,
		head_vertexbufferflags ,
	) = unpack('4I', f.read(16))
	
	if usetext: ##########################
		text.write(
			'# Weird stuff, might not actually do anything.\n'
			'UseUniqueMaterials = %s\n'   % i2b(head_useuniquematerials) +
			'UseUniqueTextures  = %s\n'   % i2b(head_useuniquetextures ) +
			'UseGenericGeometry = %s\n'   % i2b(head_usegenericgeometry) +
			'VertexBufferFlags  = %s\n\n' % i2x(head_vertexbufferflags )
		)
	
	f.seek(48, 1)
	head_bitmap_count = unpack('I', f.read(4))[0]
	bitmaps = buildbitmaplist(f, head_bitmap_count)
	materials = [bpy.data.materials.new(x[0]) for x in bitmaps]
	
	head_matprop_count = unpack('I', f.read(4))[0]
	matprops = []
	print('MatProps: %i' % head_matprop_count)
	for matprop_id in range(head_matprop_count):
		head_matprop_ambient  = unpack('4f', f.read(16))
		head_matprop_diffuse  = unpack('4f', f.read(16))
		head_matprop_specular = unpack('4f', f.read(16))
		head_matprop_emissive = unpack('4f', f.read(16))
		(
			head_matprop_shine    ,
			head_matprop_alpha    ,
			head_matprop_alphatype,
			head_matprop_bitfield ,
		) = unpack('2f2I', f.read(16))
		head_matprop_animname  = readnulltermstring(f.read(8))
		
		if usetext: ##########################
			text.write(
				'# Shaders\n'                                                                  +
				'MatPropAmbient   = %.06f, %.06f, %.06f, %.06f\n' % head_matprop_ambient       +
				'MatPropDiffuse   = %.06f, %.06f, %.06f, %.06f\n' % head_matprop_diffuse       +
				'MatPropSpecular  = %.06f, %.06f, %.06f, %.06f\n' % head_matprop_specular      +
				'MatPropEmissive  = %.06f, %.06f, %.06f, %.06f\n' % head_matprop_emissive      +
				'MatPropShine     = %.06f\n'                      % head_matprop_shine         +
				'MatPropAlpha     = %.06f\n'                      % head_matprop_alpha         +
				'MatPropAlphaType = %i\n'                         % head_matprop_alphatype     +
				'MatPropFlags     = %s\n'                         % i2x(head_matprop_bitfield) +
				'MatPropName      = %s\n\n'                       % str(head_matprop_animname)
			)
		
		matprops += [(
			head_matprop_ambient  ,
			head_matprop_diffuse  ,
			head_matprop_specular ,
			head_matprop_emissive ,
			head_matprop_shine    ,
			head_matprop_alpha    ,
			head_matprop_alphatype,
			head_matprop_bitfield ,
			head_matprop_animname ,
		)]
	
	offset = f.tell()
	while 1:
		chunk_name = f.read(4)
		if chunk_name == b'\0\0\0\0' or not len(chunk_name) == 4: break
		chunk_size = unpack('I', f.read(4))[0]
		
		print('%s: %s' % (chunk_name.decode('ascii'), hex(chunk_size)))
		
		if chunk_name == b'GEO1':
			geo1_detaillevels = unpack('I', f.read(4))[0]
			
			detaillevel_string = 'Detail level %%0%ii' % len(str(geo1_detaillevels))
			for detaillevel_id in range(geo1_detaillevels):
				bpy.ops.object.empty_add()
				dl_root = bpy.context.scene.objects[0]
				dl_root.name = detaillevel_string % detaillevel_id
				dl_root.parent = obj_root
				(
					geo1_detaillevel_type         , # 0 for base mesh, 1 for distant mesh (model type distant)
					geo1_detaillevel_maxedgelength, # unknown purpose, is the distance between the two most distant connected vertices
					geo1_rendergroups             , # detail level is split into submeshes as textures are applied per submesh
				) = unpack('IfI', f.read(12))
				f.seek(8, 1)
				rendergroup_string = 'Rendergroup %%0%ii (Material %%0%ii)' % (len(str(geo1_rendergroups)), len(str(len(bitmaps))))
				for rendergroup_id in range(geo1_rendergroups):
					work_bmesh = bmesh.new()
					(
						geo1_rendergroup_polygons, #
						geo1_rendergroup_vertices, #
						geo1_rendergroup_material, #
						geo1_rendergroup_effects , # 512 in rgeffects models, else 0
					) = unpack('4H', f.read(8))
					f.seek(12, 1)
					(
						geo1_texblend_effectmask     , # variable as 3, 9, 17, or 513 in effects models, else 0
						geo1_texblend_renderreference, # always 0
						geo1_texblend_effects        , # 2 in effects models, else always 1
						geo1_texblend_custom         , # always 0
						geo1_texblend_coordinates    , # 2 in flow models, else always 1
					) = unpack('3H2B', f.read(8))
					geo1_texblend_blends = tuple(unpack('IH2B', f.read(8)) for x in range(4))
					# I effect         
					# H textureindex    # the bitmap used on the rendergroup
					# B coordinateindex
					# B tilinginfo      # 0x3 = tiling enabled, 0 = disabled
					
					(
						geo1_vertex_offset_vector  , # always 0
						geo1_vertex_offset_normal  , # always 12
						geo1_vertex_offset_colour  , # variable (trash memory if not geo1_vertex_flags & VERTEX_HAS_COLOR)
						geo1_vertex_offset_texcoord, # variable on account of previous int
						geo1_vertex_size_vertstruct, # variable on account of previous ints
						geo1_vertex_num_texcoords  , # either 1, or 2 (rare)
						geo1_vertex_flags          , # see VERTEX_HAS_VECTOR and its following flags
						geo1_vertex_vertices       , # identical to geo1_rendergroup_vertices
						geo1_vertex_managedbuffer  , # always 1
						geo1_vertex_currentvertex  , # either 15998, 16256, or 0
					) = unpack('4I2I4H', f.read(32))
					f.seek(8, 1)
					
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
					(
						geo1_fill_selectableprimblocks, # always 1
						geo1_fill_type                , # always 0
						geo1_fill_indices             , # always equal to (geo1_rendergroup_polygons*3)
					) = unpack('3I', f.read(12))
					
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
	if usebitmaps: openbitmaps(filepath, bitmaps)
			
def open_mdl1(filepath, usebitmaps = True):
	f = open(filepath,'rb')
	fn = splitext(split(filepath)[1])[0]
	bpy.ops.object.empty_add()
	obj_root = bpy.context.scene.objects[0]
	obj_root.name = fn
	
	chunk_name = f.read(4)
	chunk_size = unpack('I', f.read(4))
	(
		head_inertiamulti  , # variable
		head_boundingradius, # variable
		head_distancefades , # boolean, 0 for map landmarks, 1 for small objects
		head_hasboundingbox, # always 1
	) = unpack('3ff2I', f.read(24))
	if head_hasboundingbox:
		(
			head_boundingboxmin   ,
			head_boundingboxmax   ,
			head_boundingboxcenter,
			head_boundingboxroty  ,
		) = unpack('3f3f3ff', f.read(40))
	( # all these fields appear unused
		head_useuniquematerials, # always 0
		head_useuniquetextures , # always 0
		head_usegenericgeometry, # always 0
		head_vertexbufferflags , # always 0
	) = unpack('4I', f.read(16))
	f.seek(48, 1)
	
	head_bitmap_count = unpack('I', f.read(4))[0]
	bitmaps = buildbitmaplist(f, head_bitmap_count)
	materials = [bpy.data.materials.new(x[0]) for x in bitmaps]
	
	head_matprop_count = unpack('I', f.read(4))[0]
	matprops = []
	for matprop_id in range(head_matprop_count):
		(
			head_int0  ,
			head_float0,
			head_float1,
			head_float2,
			head_float3,
			head_float4,
			head_float5,
		) = unpack('I6f', f.read(28))
		matprops += [(
			head_int0  ,
			head_float0,
			head_float1,
			head_float2,
			head_float3,
			head_float4,
			head_float5,
		)]
	
	offset = f.tell()
	while 1:
		chunk_name = f.read(4)
		if chunk_name == b'\0\0\0\0' or not len(chunk_name) == 4: break
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
				(
					geo1_detaillevel_type         , # variable; 0 for base mesh, 1 for distant mesh (model type distant)
					geo1_detaillevel_maxedgelength, # variable, unknown purpose, is the distance between the two most distant connected vertices
					geo1_rendergroups             , # variable, detail level is split into submeshes as textures are applied per submesh
				) = unpack('IfI', f.read(12))
				f.seek(8, 1)
				rendergroup_string = 'Rendergroup %%0%ii (Material %%0%ii)' % (len(str(geo1_rendergroups)), len(str(len(bitmaps))))
				for rendergroup_id in range(geo1_rendergroups):
					work_bmesh = bmesh.new()
					(
						geo1_rendergroup_polygons, # variable
						geo1_rendergroup_vertices, # variable
						geo1_rendergroup_material, # variable
						geo1_rendergroup_effects , # 512 in rgeffects models, else 0
					) = unpack('4H', f.read(8))
					f.seek(12, 1)
					(
						geo1_texblend_effectmask     , # variable as 3, 9, 17, or 513 in effects models, else 0
						geo1_texblend_renderreference, # always 0
						geo1_texblend_effects        , # 2 in effects models, else always 1
						geo1_texblend_custom         , # always 0
						geo1_texblend_coordinates    , # 2 in flow models, else always 1
					) = unpack('3H2B', f.read(8))
					geo1_texblend_blends = tuple(unpack('IH2B', f.read(8)) for x in range(4))
					# I effect         
					# H textureindex    # the bitmap used on the rendergroup
					# B coordinateindex
					# B tilinginfo      # 0x3 = tiling enabled, 0 = disabled
					
					(
						geo1_vertex_offset_vector  , # always 0
						geo1_vertex_offset_normal  , # always 12
						geo1_vertex_offset_colour  , # variable (trash memory if not geo1_vertex_flags & VERTEX_HAS_COLOR)
						geo1_vertex_offset_texcoord, # variable on account of previous int
						geo1_vertex_size_vertstruct, # variable on account of previous ints
						geo1_vertex_num_texcoords  , # either 1, or 2 (rare)
						geo1_vertex_flags          , # see VERTEX_HAS_VECTOR and its following flags
						geo1_vertex_vertices       , # identical to geo1_rendergroup_vertices
						geo1_vertex_managedbuffer  , # always 1
						geo1_vertex_currentvertex  , # either 15998, 16256, or 0
					) = unpack('4I2I4H', f.read(32))
					f.seek(8, 1)
					
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
					(
						geo1_fill_selectableprimblocks, # always 1
						geo1_fill_type                , # always 0
						geo1_fill_indices             , # always equal to (geo1_rendergroup_polygons*3)
					) = unpack('3I', f.read(12))
					
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
	if usebitmaps: openbitmaps(filepath, bitmaps)
			
def open_mdl0(filepath, usebitmaps = True):
	f = open(filepath,'rb')
	fn = splitext(split(filepath)[1])[0]
	work_bmesh = bmesh.new()
	(
		mdl0_signature,
		mdl0_int      ,
		mdl0_int      ,
		mdl0_int      ,
		mdl0_float    ,
		mdl0_bitmaps  ,
	) = unpack('4s3IfI', f.read(24))
	
	for bitmap_id in range(mdl0_bitmaps):
		bitmaps += [readnulltermstring(f.read(256)).decode('utf8')]
	materials = [bpy.data.materials.new(x) for x in bitmaps]
	
	(
		mdl0_int     ,
		mdl0_int     ,
		mdl0_int     ,
		mdl0_int     ,
		mdl0_int     ,
		mdl0_int     ,
		mdl0_int     ,
		mdl0_int     ,
		mdl0_float   ,
		mdl0_int     ,
		mdl0_int     ,
		mdl0_int     ,
		mdl0_polygons,
		mdl0_vertices,
		mdl0_int     ,
		mdl0_int     ,
		mdl0_int     ,
		mdl0_int     ,
	) = unpack('8If3I2H4I', f.read(68))
	
	(
		mdl0_texblend_effectmask     ,
		mdl0_texblend_renderreference,
		mdl0_texblend_effects        ,
		mdl0_texblend_custom         ,
		mdl0_texblend_coordinates    ,
	) = unpack('3H2B', f.read(8))
	mdl0_texblend_blends = tuple(unpack('IH2B', f.read(8)) for x in range(4))
	# I effect         
	# H textureindex    # the bitmap used on the rendergroup
	# B coordinateindex
	# B tilinginfo      # 0x3 = tiling enabled, 0 = disabled
	
	(
		mdl0_vertex_offset_vector  , # always 0
		mdl0_vertex_offset_normal  , # always 12
		mdl0_vertex_offset_colour  , # variable (trash memory if not geo1_vertex_flags & VERTEX_HAS_COLOR)
		mdl0_vertex_offset_texcoord, # variable on account of previous int
		mdl0_vertex_size_vertstruct, # variable on account of previous ints
		mdl0_vertex_num_texcoords  , # either 1, or 2 (rare)
		mdl0_vertex_flags          , # see VERTEX_HAS_VECTOR and its following flags
		mdl0_vertex_vertices       , # identical to geo1_rendergroup_vertices
		mdl0_vertex_managedbuffer  , # always 1
		mdl0_vertex_currentvertex  , # either 15998, 16256, or 0
	) = unpack('4I2I4H', f.read(32))
	f.seek(8, 1)
	
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
	
	work_obj = bpy.data.objects.new(fn, work_mesh)
	work_obj.data.materials.append(materials[0])
	bpy.context.scene.objects.link(work_obj)
	
	f.close()
	work_obj.rotation_euler = (__import__('math').pi / 2, 0, 0)
	if usebitmaps: openbitmaps(filepath, bitmaps)