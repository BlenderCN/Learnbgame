__author__ = ['Dzmitry Malyshau']
__bpydoc__ = 'Mesh module of KRI exporter.'

import mathutils
from io_kri.common	import *


def calc_TBN(verts, uvs):
	va = verts[1].co - verts[0].co
	vb = verts[2].co - verts[0].co
	n0 = n1 = va.cross(vb)
	tan,bit,hand = None,None,1.0
	if uvs!=None and n1.length_squared>0.0:
		ta = uvs[1] - uvs[0]
		tb = uvs[2] - uvs[0]
		tan = va*tb.y - vb*ta.y
		if tan.length_squared>0.0:
			bit = vb*ta.x - va*tb.x
			n0 = tan.cross(bit)
			tan.normalize()
			hand = (-1.0,1.0)[n0.dot(n1) > 0.0]
		else:	tan = None
	return (tan, bit, n0, hand, n1)

def calc_quat(normal):
	import math
	#note: constructor is Quaternion(w,x,y,z)
	if normal.z > 0.0:
		d = math.sqrt(2.0 + 2.0*normal.z)
		return mathutils.Quaternion(( 0.5*d, -normal.y/d, normal.x/d, 0.0 ))
	else:
		d = math.sqrt(2.0 - 2.0*normal.z)
		return mathutils.Quaternion(( normal.x/d, 0.0, 0.5*d, normal.y/d ))

def fix_convert(type, valist):
	typeScale = {
		'B': 0xFF,
		'H': 0xFFFF,
		'I': 0xFFFFFFFF
		}
	fun = None
	if type.islower():
		scale = typeScale[type.upper()] + 1
		fun = lambda x: int(min(1,max(-1,x))*0.5*scale-0.5)
	else:
		scale = typeScale[type]
		fun = lambda x: int(min(1,max(0,x))*scale)
	return [fun(x) for x in valist]



class Vertex:
	__slots__= 'face', 'vert','vert2', 'coord', 'tex', 'color', 'normal', 'tangent', 'quat', 'dual'
	def __init__(self, v):
		self.face = None
		self.vert = v
		self.vert2 = None
		self.coord = v.co
		self.tex = None
		self.color = None
		self.normal = v.normal
		self.tangent = None
		self.quat = None
		self.dual = -1


class Face:
	__slots__ = 'v', 'vi', 'no', 'uv', 'color', 'mat', 'ta', 'hand', 'normal', 'wes'
	def __init__(self, face, m, ind = None, uves = None, colors = None):
		if not ind: # clone KRI face
			self.vi		= list(face.vi)
			self.hand	= face.hand
			self.mat	= face.mat
			return
		# this section requires optimization!
		# hint: try 'Recalculate Outside' if getting lighting problems
		self.mat = face.material_index
		self.vi = [ face.vertices[i]	for i in ind   ]
		self.v  = tuple( m.vertices[x]	for x in self.vi )
		self.no = tuple( x.normal		for x in self.v  )
		self.normal = ( face.normal, mathutils.Vector((0,0,0)) )[face.use_smooth]
		xuv		= tuple(tuple( layer[i]	for i in ind ) for layer in uves)
		color	= tuple(tuple( layer[i]	for i in ind ) for layer in colors)
		uv_base = None
		if Settings.fakeQuat != 'Force' and len(xuv)>0:
			uv_base = xuv[0]
		t,b,n,hand,nv = calc_TBN(self.v, uv_base)
		self.wes = tuple( 3 * [0.1+nv.length_squared] )
		self.ta = t
		self.hand = hand
		self.uv	= ([],xuv)			[Settings.putUv]
		self.color	= ([],color)	[Settings.putColor]


###  MESH   ###

class Attribute:
	# fixed enumerant:
	# 0: not fixed, leave as is (e.g. positions)
	# 1: fixed, already converted (e.g. bone weights)
	# 2: fixed, needs conversion (e.g. normals)
	__slots__ = 'name', 'type', 'fixed', 'data', 'interpolate'
	def __init__(self, name, type, fixed=0):
		self.name = name
		self.type = type
		self.fixed = fixed
		self.data = []
		self.interpolate = True

class Mesh:
	__slots__ = 'nv', 'ni', 'attribs', 'index'
	def __init__(self):
		self.nv = self.ni = 0
		self.attribs = []
		self.index = None


def save_mesh(out, ob, log): # -> (Mesh, bounds, faces_per_mat)
	# ready...
	print("\t", 'Exporting Mesh', ob.data.name)
	log.logu(0, 'Mesh %s' % (ob.data.name))
	arm = None
	if ob.parent and ob.parent.type == 'ARMATURE':
		arm = ob.parent.data
	# steady...
	(km, bounds, face_num) = collect_attributes(ob.data, arm, ob.vertex_groups, False, log)
	if km == None:
		return (None, None, [])
	# go!
	out.begin('mesh')
	totalFm = ''.join(a.type for a in km.attribs)
	assert len(totalFm) == 2*len(km.attribs)
	stride = out.size_of(totalFm)
	log.logu(1, 'Format: %s, Stride: %d' % (totalFm,stride))
	out.text(ob.data.name);
	out.pack('L', km.nv)
	out.text('3')	# topology
	# vertices
	out.begin('buffer')
	out.pack('B', stride)
	out.text(totalFm)
	seqStart = out.tell()
	for vats in zip(*(a.data for a in km.attribs)):
		for a,d in zip( km.attribs, vats ):
			tip = a.type[1]
			size = out.size_of(a.type)
			if (size&3) != 0:
				log.log(2, 'w', 'Attrib %d has has non-aligned type: %d' % (a.name,tip))
			d2 = (d if a.fixed<=1 else fix_convert(tip,d))
			out.array(tip, d2)
	assert out.tell() == seqStart + km.nv*stride
	# extra info per attribute
	for a in km.attribs:
		out.text(a.name)
		flag = 0
		if a.fixed: flag |= 1
		if a.interpolate: flag |= 2
		out.pack('B', flag)
	out.end()
	# indices
	if km.index:
		out.begin('index')
		stype = km.index.type[0];
		stride = out.size_of(stype)
		out.pack('Lc', km.ni, bytes(stype, 'utf-8'))
		seqStart = out.tell()
		for d in km.index.data:
			out.array(stype, d)
		assert out.tell() == seqStart + km.ni*stride
		out.end()
	# done
	out.end()	#mesh
	return (km, bounds, face_num)

def compute_bounds_2d(vectors):
	x, y = zip(*vectors)
	vmin = (min(x), min(y))
	vmax = (max(x), max(y))
	return (vmin, vmax)

def compute_bounds_3d(vectors):
	x, y, z = zip(*vectors)
	vmin = (min(x), min(y), min(z))
	vmax = (max(x), max(y), max(z))
	return (vmin, vmax)

def collect_attributes(mesh, armature, groups, no_output,log):
	# 0: compute bounds
	bounds = compute_bounds_3d(tuple(v.co) for v in mesh.vertices)

	# 1: convert Mesh to Triangle Mesh
	for layer in mesh.uv_textures:
		if not len(layer.data):
			log.log(1,'e','UV layer is locked by the user')
			return (None, bounds, [])
	hasUv		= len(mesh.uv_textures)>0
	hasTangent	= Settings.putTangent and hasUv
	hasQuatUv	= Settings.putQuat and hasUv
	hasQuat		= Settings.putQuat and (Settings.fakeQuat != 'Never' or hasUv)
	ar_face = []
	for i, face in enumerate(mesh.polygons):
		uves, colors = [], []
		loop_end = face.loop_start + face.loop_total
		for layer in mesh.uv_layers:
			storage = layer.data[face.loop_start : loop_end]
			cur = tuple(mathutils.Vector(x.uv) for x in storage)
			uves.append(cur)
		for layer in mesh.vertex_colors:
			storage = layer.data[face.loop_start : loop_end]
			cur = tuple(mathutils.Vector(x.color) for x in storage)
			colors.append(cur)
		for i in range(2, face.loop_total):
			ar_face.append(Face(face, mesh, (0,i-1,i), uves, colors))
	#else: log.logu(1,'converted to tri-mesh')
	if not 'ClearNonUV':
		n_bad_face =	len(ar_face)
		ar_face = list(filter( lambda f: f.ta!=None, ar_face ))
		n_bad_face -=	len(ar_face)
		if n_bad_face:
			log.log(1, 'w', '%d pure faces detected' % (n_bad_face))
	if not len(ar_face):
		log.log(1, 'e', 'object has no faces')
		return (None, bounds, [])

	# 1.5: face indices
	ar_face.sort(key = lambda x: x.mat)
	face_num = (len(mesh.materials)+1) * [0]
	for face in ar_face:
		face_num[face.mat] += 1

	if no_output:
		return (None, bounds, face_num)

	# 2: fill sparsed vertex array
	avg,set_vert,set_surf = 0.0,{},{}
	for face in ar_face:
		avg += face.hand
		nor = face.normal
		for i in range(3):
			v = Vertex( face.v[i] )
			v.normal = (face.no[i],nor)[nor.length_squared>0.1]
			v.tex	= [layer[i] for layer in face.uv]
			v.color	= [layer[i] for layer in face.color]
			v.face = face
			vs = str((v.coord,v.tex,v.color,v.normal,face.hand))
			if not vs in set_vert:
				set_vert[vs] = []
			set_vert[vs].append(v)
			vs = str((v.coord,v.normal,face.hand))
			if not vs in set_surf:
				set_surf[vs] = []
			set_surf[vs].append(v)
	log.log(1,'i', '%.2f avg handness' % (avg / len(ar_face)))

	# 3: compute tangents
	avg,bad_vert = 0.0,0
	for vgrup in set_surf.values():
		tan,lensum = mathutils.Vector((0,0,0)),0.0
		for v in vgrup:
			assert v.quat == None
			f = v.face
			if f.ta:
				lensum += f.ta.length
				tan += f.ta
		quat = vgrup[0].quat
		no = vgrup[0].normal.normalized()
		if Settings.fakeQuat=='Force' or (Settings.fakeQuat=='Auto' and not hasQuatUv):
			quat = calc_quat(no)
		if lensum>0.0:
			avg += tan.length / lensum
			tan.normalize()		# mean tangent
			if hasQuatUv and quat==None:
				bit = no.cross(tan) * vgrup[0].face.hand	# using handness
				tan = bit.cross(no)	# handness will be applied in shader
				tbn = mathutils.Matrix((tan,bit,no))	# tbn is orthonormal, right-handed
				quat = tbn.to_quaternion().normalized()
		if None in (quat,tan):
			bad_vert += 1
			quat = mathutils.Quaternion((0,0,0,1))
			tan = mathutils.Vector((1,0,0))
		for v in vgrup:
			v.quat = quat
			v.tangent = tan
	if bad_vert:
		log.log(1,'w','%d pure vertices detected' % (bad_vert))
	if hasQuatUv and avg!=0.0:
		log.log(1,'i','%.2f avg tangent accuracy' % (avg / len(set_vert)))
	del set_surf
	del bad_vert
	del avg

	# 4: update triangle indexes
	ar_vert = []
	for i,vgrup in enumerate(set_vert.values()):
		v = vgrup[0]
		for v2 in vgrup:
			f = v2.face
			ind = f.v.index(v2.vert)
			f.vi[ind] = i
		ar_vert.append(v)
	del set_vert

	# 5: unlock quaternions to make all the faces QI-friendly
	def qi_check(f):	# check Quaternion Interpolation friendliness
		qx = tuple( ar_vert[x].quat for x in f.vi )
		assert qx[0].dot(qx[1]) >= 0 and qx[0].dot(qx[2]) >= 0
	def mark_used(ind):	# mark quaternion as used
		v = ar_vert[ind]
		if v.dual < 0: v.dual = ind
	n_dup,ex_face = 0,[]
	for f in ([],ar_face)[hasQuat and Settings.doQuatInt]:
		vx,cs,pos,n_neg = (1,2,0),[0,0,0],0,0
		def isGood(j):
			ind = f.vi[j]
			vi = ar_vert[ind]
			if vi.dual == ind: return False	# used, no clone
			if vi.dual < 0: vi.quat.negate()	# not used
			else:   f.vi[j] = vi.dual	# clone exists
			return True
		def duplicate():
			src = ar_vert[ f.vi[pos] ]
			dst = Vertex(src.vert)
			dst.face = f
			dst.tex = tuple( layer.copy() for layer in src.tex )
			dst.quat = src.quat.copy()
			dst.quat.negate()
			dst.dual = f.vi[pos]
			f.vi[pos] = src.dual = len(ar_vert)
			ar_vert.append(dst)
			return 1
		for j in range(3):
			qx = tuple( ar_vert[f.vi[x]].quat for x in (vx[j],vx[vx[j]]) )
			cs[j] = qx[0].dot(qx[1])
			if cs[j] > cs[pos]: pos = j
			if(cs[j] < 0): n_neg += 1
		#print ("\t %d: %.1f, %.1f, %.1f" % (pos,cs[0],cs[1],cs[2]))
		if n_neg == 2 and not isGood(pos):   # classic duplication case
			n_dup += duplicate()
		if n_neg == 3:  # extremely rare case
			pos = next((j for j in range(3) if isGood(j)), -1)
			if pos < 0:
				pos = 1
				n_dup += duplicate()
			cs[vx[pos]] *= -1
			cs[vx[vx[pos]]] *= -1
			n_neg -= 2
		if n_neg == 1: # that's a bad case
			pos = min((x,j) for j,x in enumerate(cs))[1]
			# prepare
			ia,ib = vx[pos],vx[vx[pos]]
			va = ar_vert[ f.vi[ia] ]
			vb = ar_vert[ f.vi[ib] ]
			vc = ar_vert[ f.vi[pos] ]
			# create mean vertex
			v = Vertex( vc.vert )
			v.vert = va.vert
			v.vert2 = vb.vert
			n_dup += 1
			v.face = f
			v.coord = 0.5 * (va.coord + vb.coord)
			v.quat = (va.quat + vb.quat).normalized()
			if va.tex and vb.tex:
				v.tex = tuple( 0.5*(a[0]+a[1]) for a in zip(va.tex,vb.tex) )
			# create additional face
			f2 = Face( f, mesh )
			mark_used( f.vi[ia] )	# caution: easy to miss case
			v.dual = f.vi[ia] = f2.vi[ib] = len(ar_vert)
			# it's mathematically proven that both faces are QI friendly now!
			ar_vert.append(v)
			ex_face.append(f2)
		# mark as used
		for ind in f.vi: mark_used(ind)

	if Settings.doQuatInt and hasQuat:
		log.log(1,'i', 'extra %d vertices, %d faces' % (n_dup,len(ex_face)))
		ar_face += ex_face
		# run a check
		for f in ar_face: qi_check(f)
	del ex_face

	# 6: stats and output
	log.logu(1, 'total: %d vertices, %d faces' % (len(ar_vert),len(ar_face)))
	avg_vu = 3.0 * len(ar_face) / len(ar_vert)
	log.log(1,'i', '%.2f avg vertex usage' % (avg_vu))

	km = Mesh()

	if 'putVertex':
		vat = Attribute('Position', '3f', 0)
		km.attribs.append(vat)
		for v in ar_vert:
			vat.data.append( v.coord.to_3d() )

	if Settings.putNormal:
		#vat = Attribute('Normal', '3f', 0)
		vat = Attribute('Normal', '4h', 2)
		# WebGL only accept multiples of 4 for the attribute size
		km.attribs.append(vat)
		for v in ar_vert:
			vat.data.append( v.normal.to_4d() )

	if hasTangent:
		vat = Attribute('Tangent', '4b', 2)
		km.attribs.append(vat)
		for v in ar_vert:
			vat.data.append( [v.tangent.x, v.tangent.y, v.tangent.z, v.face.hand] )

	if hasQuat:
		vat2 = Attribute('Handedness', '1f')	# has to be aligned
		vat1 = Attribute('Quaternion', '4h', 2)
		vat1.interpolate = vat2.interpolate = Settings.doQuatInt
		km.attribs.extend([ vat2,vat1 ])
		for v in ar_vert:
			vat1.data.append([ v.quat.x, v.quat.y, v.quat.z, v.quat.w ])
			vat2.data.append([ int(v.face.hand) ])

	if Settings.putUv:
		all = mesh.uv_textures
		log.log(1,'i', 'UV layers: %d' % (len(all)))
		for i, layer in enumerate(all):
			name = 'Tex%d' % i
			vat = Attribute(name, '2f', 0)
			if Settings.compressUv:
				vmin, vmax = compute_bounds_2d(v.tex[i] for v in ar_vert)
				lo, hi, threshold = min(vmin), max(vmax), 0.01
				if lo > -threshold and hi < 1.0 + threshold:
					vat = Attribute(name, '2H', 2)
				elif lo > -1-threshold and hi < 1.0 + threshold:
					vat = Attribute(name, '2h', 2)
				log.log(2,'i', 'UV[%d] bounds: [%.1f,%.1f], format: %s' % (i, lo, hi, vat.type))
			km.attribs.append(vat)
			for v in ar_vert:
				assert i<len(v.tex)
				tc = v.tex[i]
				vat.data.append(tc.to_2d())

	if Settings.putColor:
		all = mesh.vertex_colors
		log.log(1,'i', 'Color layers: %d' % (len(all)))
		for i,layer in enumerate(all):
			vat = Attribute('Color%d' % i, '4B', 2)
			km.attribs.append(vat)
			for v in ar_vert:
				assert i<len(v.color)
				tc = v.color[i];
				vat.data.append(tc)

	if not 'putSticky':
		all = mesh.sticky
		log.log(1,'i', 'Sticky layers: %d' % (len(all)))
		for i in range(len(all)):
			for v in ar_vert:
				pass

	if 'index':
		km.ni = len(ar_face) * 3
		nv = len(ar_vert)
		stype = 'I'
		if nv<0x100:		stype = 'B'
		elif nv<0x10000:	stype = 'H'
		log.log(1,'i', 'Index format: %s' % (stype))
		km.index = vat = Attribute('', stype, 0)
		for face in ar_face:
			vat.data.append(face.vi)

	# 8: bone weights
	if armature:
		vat1 = Attribute('BoneIndex', '4B', 0)
		vat2 = Attribute('BoneWeight', '4B', 1)
		km.attribs.extend([ vat1,vat2 ])
		nempty, avg = 0, 0.0
		for v in ar_vert:
			nw = len(v.vert.groups)
			avg += nw
			if not nw:
				nempty += 1
				vat1.data.append([ 0,0,0,0 ]);
				vat2.data.append([ 255,0,0,0 ]);
				continue
			r_ids = []
			r_weights = []
			bone = sorted(v.vert.groups, key=lambda x: x.weight, reverse=True) [:min(4,nw)]
			left, total = 255, sum(b.weight for b in bone)
			for i in range(4):
				bid,weight = 0,0
				if i < len(bone):
					name = groups[ bone[i].group ].name
					bid = armature.bones.keys().index(name) + 1
					weight = int(255.0 * bone[i].weight / total + 0.5)
				if i==3: weight = left
				else: weight = min(left,weight)
				left -= weight
				assert weight>=0 and weight<256
				r_ids.append(bid)
				r_weights.append(weight)
			vat1.data.append(r_ids)
			vat2.data.append(r_weights)
		avg /= len(ar_vert)
		log.logu(1, 'bone weights: %d empty, %.1f avg' % (nempty,avg))

	# 9: the end!
	km.nv = len(ar_vert)
	return (km, bounds, face_num)
