from struct import pack
import bpy, bmesh
from io import BytesIO as bio

f2i = lambda s, f = {}: sum(leval(x[:10]) if x.startswith('0x') else int(x) if x.isnumeric() else f[x] for x in s.replace(' ', '').split('|'))
b2i = lambda s: int(s) if s.isnumeric() else {'true': 1, 'false': 2}[s.lower()]

def write_atd(filepath, **kwargs):
	assert 'version' in kwargs, 'Did not recieve version string.'
	v = kwargs['version']
	del kwargs['version']
	print('Version:', v)
	if   v == 'MDL2': write_mdl2(filepath, **kwargs)
	#elif v == 'MDL1': write_mdl1(filepath, **kwargs)
	#elif v == 'MDL0': write_mdl0(filepath, **kwargs)
	else: raise AssertionError('Invalid version.')

#Options:
# Vector : Inertia multiplier
# Float  : Sphere bounding box radius
# I4 Bool: Fades at distance
# I4 Bool: Has bounding box
#  If True:
#   Vector: (Corner 1)
#   Vector: (Corner 2)
#   Vector: (Center)
#   Float : (Rotation Y)

def write_mdl2(filepath,
	bounding_radius = 5,
	distance_fades = True,
	use_bounding_box = True,
	matprops = 3, # crashes if 1
):
	meshroots    = []
	bitmap_paths = []
	validroot    = False
	for root in bpy.data.objects:
		if root.type == 'EMPTY' and root.parent == None:
			for detaillevel in root.children:
				if detaillevel.type == 'EMPTY':
					assert detaillevel.children, 'Detail level "%s" has no children.' % detaillevel.name
					meshroots += [[detaillevel, []]]
					validmesh = False
					for rendergroup in detaillevel.children:
						if rendergroup.type == 'MESH':
							assert rendergroup.material_slots, 'Render group "%s" has no material slots; there must be 1.' % rendergroup.name
							bitmap_path = rendergroup.material_slots[0].name
							assert bitmap_path, 'Render group "%s"\'s 1st material slot is unnamed; name it a texture path.' % rendergroup.name
							assert bitmap_path.lower().startswith('game data'), 'Render group "%s"\'s 1st material slot does not start with the game data path "game data".' % rendergroup.name
							validmesh = True
							if bitmap_path not in bitmap_paths: bitmap_paths += [bitmap_path]
							meshroots[-1][1] += [(rendergroup, bitmap_paths.index(bitmap_path))]
						assert validmesh, 'Detail level "%s" has no valid mesh.' % detaillevel.name
	assert meshroots, 'Could not find any valid roots. Import an .md2 to see the required hierarchy.'
	
	f = open(filepath, 'wb')
	
	for chunkname in (b'MDL2', b'GEO1'):
		f.write(chunkname + b'\0\0\0\0')
		chunkstart = f.tell()
		if chunkname == b'MDL2':
			f.write(
				pack('f', 1.5)*3 # inertia multiplier
				+ pack('f', bounding_radius)
				+ pack('I', distance_fades)
				+ pack('I', use_bounding_box)
			)
			if use_bounding_box:
				f.write(
					pack('3f', -2, -2, -2) #min
					+pack('3f', 2, 2, 2) #max
					+pack('3f', 0, 0, 0) #center
					+pack('f', -.0) #rotation y
				)
			f.write(
				pack('4I', 0, 0, 0, 0)
				+ b'\0'*48
			)
			f.write(
				pack('I', len(bitmap_paths))
			)
			for index, path in enumerate(bitmap_paths):
				encodedpath = path.encode('ascii')
				assert len(encodedpath) <= 255, 'The bitmap path "%s" is too long; it must be below 256 characters.' % path
				f.write(
					pack('256s', encodedpath)
					+ pack('I', 0) # type
					+ pack('I', index) # type
				)
			f.write( # matprops
				pack('I', matprops)
			)
			for matprop in range(matprops):
				f.write(
					pack('4f',  0.3764,0.3764,0.3764,0.3764,)
					+pack('4f', 0.5019,0.5019,0.5019,0.5019,)
					+pack('4f', 0.6588,0.6588,0.6588,0.6588,)
					+pack('4f', 0,0,0,0)
					+pack('f', 0)
					+pack('f', 0)
					+pack('I', 0)
					+pack('I', 0)
					+pack('8s', b'RRU') # "anim name" in liblr2, but i think it's unused
				)
		elif chunkname == b'GEO1':
			f.write(pack('I', len(meshroots)))
			detaillevel_id = 0
			for detaillevel, rendergroups in meshroots:
				f.write(
					pack('I', 1) # set in official models, but unused by the game; 1 for normal mesh, 2 for lod, but it determines lod from the detail level definition being first or second
					+ pack('f', 5) # max edge length, unknown purpose
					+ pack('I', len(rendergroups))
					+ b'\0'*8
				)
				
				for rendergroup, bitmap_id in rendergroups:
					dl_mesh = bmesh.new()
					dl_mesh.from_object(rendergroup, bpy.context.scene)
					dl_mesh.faces.ensure_lookup_table()
					dl_mesh.verts.ensure_lookup_table()
					dl_mesh.verts.index_update()
					
					f.write(
						pack('H', len(dl_mesh.faces))
						+ pack('H', len(dl_mesh.verts))
						+ pack('H', 1) # "material"
						+ pack('H', 0) # "effects"
						+ b'\0'*12
					)
					f.write(
						pack('H', 1)
						+ pack('H', 0)
						+ pack('H', 1)
						+ pack('B', 0)
						+ pack('B', 1)
					)
					for texblend in (
						(
							pack('I', 0)
							+ pack('H', bitmap_id)
							+ pack('B', 0)
							+ pack('B', 3) # 3 = tiling enabled, 0 = disabled
						),
						*(b'\xff\xff\xff\xff\xff\xff\x0f\x03',)*3,
					):
						f.write(texblend)
					f.write(
						pack('i', 0) #geo1_vertex_offset_vector  ,\
						+ pack('i', 12) #geo1_vertex_offset_normal  ,\
						+ pack('i', 0) #geo1_vertex_offset_colour  ,\
						+ pack('i', 24) #geo1_vertex_offset_texcoord,\
						+ pack('I', 32) #geo1_vertex_size_vertstruct,\
						+ pack('I', 1) #geo1_vertex_num_texcoords  ,\
						+ pack('H', 0b1011) #geo1_vertex_flags          ,\
						+ pack('H', len(dl_mesh.verts)) #geo1_vertex_vertices       ,\
						+ pack('H', 1) #geo1_vertex_managedbuffer  ,\
						+ pack('H', 0) #geo1_vertex_currentvertex # looks unused, appears as a partially overwritten float in the official files
						+ b'\0'*8
					)
					try: uvlayer = dl_mesh.loops.layers.uv[0]
					except IndexError: raise IndexError('Model does not have a UV map.')
					for vert in dl_mesh.verts:
						uv = ()
						for face in dl_mesh.faces:
							for loop in face.loops:
								if loop.vert.index == vert.index:
									uv = loop[uvlayer].uv
						assert uv, 'Did not find UV for vertex %i.' % vert
						f.write(
							pack('3f', *tuple(vert.co)[::-1])
							+ pack('3f', *tuple(vert.normal)[::-1])
							+ pack('2f', *uv)
						)
						
					f.write(
						pack('I', 1)
						+ pack('I', 0)
						+ pack('I', len(dl_mesh.faces)*3)
					)
					for face in dl_mesh.faces:
						f.write(
							pack('3H', *(v.index for v in face.verts))
						)
				detaillevel_id += 1
		chunkend = f.tell()
		f.seek(chunkstart - 4)
		f.write(pack('I', chunkend - chunkstart))
		f.seek(chunkend)
	
	f.close()
	
def write_mdl1(filepath):
	NotImplemented
def write_mdl0(filepath):
	NotImplemented