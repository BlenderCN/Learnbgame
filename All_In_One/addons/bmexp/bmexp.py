import bpy
import bmesh
import json
from mathutils import Matrix
from mathutils import Vector
from functools import reduce
<<<<<<< HEAD
from operator import attrgetter

d16 = lambda x: x * 16.0
#d16 = lambda x: x

round4 = lambda x: round(x, 4)
mcos = lambda vec: attrgetter('yzx')(vec)

fd = { (0, -1, 0) : 'down', #in MCOS
=======

d16 = lambda x: x * 16.0

def index(li, ele):
	for i, e in enumerate(li):
		if (e[0] == ele[0] and e[1] == ele[1]):
			return i
	raise Exception("Could not find " + str(ele) + " in " + str(li))

fd = { (0, -1, 0) : 'down',
>>>>>>> c5a7e7bbe7c2440dc5ab8306b6b0099097fa371b
		(0, 1, 0) : 'up',
		(-1, 0, 0) : 'west',
		(1, 0, 0) : 'east',
		(0, 0, -1) : 'north',
<<<<<<< HEAD
		(0, 0, 1) : 'south' }	

#vector distance to positive positive positive
#10000 is an arbritary big number which is hopefully big enough
def vecDistToPPP(vec):
	return (vec.co - Vector([10000.0, 10000.0, 10000.0])).length

#vector distance to negative negative
#only used for textures
def vecDistToNN(vec):
	vec = Vector(vec)
	return (vec - Vector([-10000.0, -10000.0])).length


def roundTouple(tu):
	return tuple(map(lambda x: float(int(x)), tu))
=======
		(0, 0, 1) : 'south' }

fsolver = {(0, 2, 1) : (90, False, True),
			(3, 1, 0) : (0, False, False), #1 
			(2, 0, 3) : (90, False, True), #2 
			(1, 3, 2) : (0, False, False), #3 
			(3, 1, 2) : (90, False, True), #4
			(0, 2, 3) : (0, False, False), #0 ff
			(1, 3, 0) : (90, False, True),
			(2, 0, 1) : (0, False, False) } 

projectionAxis = {  (0, 0, -1) : ((1.0, 0.0, 0.0), (0.0, -1.0, 0.0)),
					(0, 0, 1) : ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
					(1, 0, 0) :  ((0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
					(-1, 0, 0) :  ((0.0, -1.0, 0.0), (0.0, 0.0, 1.0)),
					(0, -1, 0) :  ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
					(0, 1, 0) :  ((-1.0, 0.0, 0.0), (0.0, 0.0, 1.0)) }

def project(v, normal):
	p1, p2 = projectionAxis[tuple(normal)]
	p1, p2 = Vector(p1), Vector(p2)
	result = (p1.dot(v), p2.dot(v))
	print("res", result, "normal", tuple(normal))

	return result
>>>>>>> c5a7e7bbe7c2440dc5ab8306b6b0099097fa371b

def processFace(f):
	global out, uv_layer
	p = {}
<<<<<<< HEAD
	co = f.verts

=======
	co = sorted(f.verts, key = lambda v: project(v.co.xyz, f.normal.normalized()))	
>>>>>>> c5a7e7bbe7c2440dc5ab8306b6b0099097fa371b
	#test if current face only got 4 vertices (is a quad)
	if (len(co) != 4):
		raise Exception("Found non-quad face")
	#test end

	#test if a single coord is out of bounds
	allCoords = list(map(lambda v: list(v.co.xyz), f.verts))
	test = list(reduce(lambda x, y: x + y, allCoords))
	for x in test:
		if (x > 2 or x < -1):
<<<<<<< HEAD
			raise Exception("Model out of bounds")
	#test end			

	
	face = type('face', (object,), {})()

	fro = co[0]
	to = co[0]
	for v in co: #tiny sort since sorted doesn't work shit
		if (vecDistToPPP(v) > vecDistToPPP(fro)):
			fro = v
		if (vecDistToPPP(v) < vecDistToPPP(to)):						
			to = v
			
	face.fro = fro
	face.to = to
	face.nor = fd[roundTouple(mcos(f.normal.normalized()))]	

	#FIND ROTATION
	uvl = {} #create uv lookup table containing pairs of bmvert : uv-coord as list		
	for loop in f.loops:
		uvl[loop.vert] = list(loop[uv_layer].uv)

	

	### MCOS ROTATIONS
	uvl = {} #create uv lookup table containing pairs of bmvert : uv-coord as list	

	#mirror y coordinate of all uv coordinates
	for loop in f.loops:
		uv = loop[uv_layer].uv		
		uv.y = 1.0 - uv.y		
		uvl[loop.vert] = list(uv)	

	#find smallest (upper left)(closest to 0,0)
	#find biggest (lower right)(furthest away to 0,0)
	uvCoords = list(uvl.values())	
	smallestUV = uvCoords[0]
	biggestUV = uvCoords[0]	
	for uvCoord in uvCoords[1:]:
		if (vecDistToNN(smallestUV) > vecDistToNN(uvCoord)):
			smallestUV = uvCoord
		if (vecDistToNN(biggestUV) < vecDistToNN(uvCoord)):
			biggestUV = uvCoord
	print(smallestUV, biggestUV)
	uv = list(map(d16, smallestUV + biggestUV))
	#uv = list(map(d16, uvl[face.fro] + uvl[face.to]))

	face.uv = uv
	face.rotation = -90
	return face

#face[from vert, to vert, normal, uv[0-3]]
#only use mcos here
=======
			raise Exception("Model out of bounds: " + str(x))
	#test end			
		
	
	face = type('face', (object,), {})()
	face.fro = co[0]
	face.to = co[-1]
	face.nor = f.normal	
	uvl = {} #create uv lookup table containing pairs of bmvert : uv-coord as list
	uli = []
	for loop in f.loops:
		t = list(map(lambda x: round(x, 3), list(loop[uv_layer].uv)))
		uvl[loop.vert] = t
		uli.append(t)	
	xs = list(map(lambda x: x[0], uli))
	ys = list(map(lambda y: y[1], uli))
	t, b, l, r = max(ys), min(ys), min(xs), max(xs)	
	uli = [[l, b], [l, t], [r, t], [r, b]]	#is sorted CW starting from bottom left corner

	uv = list(map(d16, uvl[face.fro] + uvl[face.to]))
	
	froUvIndex = index(uli, uvl[face.fro])
	toUvIndex = index(uli, uvl[face.to])
	testIndex = index(uli, uvl[co[1]])
	fk = sorted(list(fsolver.keys()))
	try:
		print(froUvIndex, toUvIndex, testIndex, ":", fk.index((froUvIndex, toUvIndex, testIndex)))	
	except Exception as e:
		print("from:", face.fro.co.xyz, "to:", face.to.co.xyz)
		raise e

	face.rot, swapx, swapy = fsolver[(froUvIndex, toUvIndex, testIndex)]	
	c0, c1, c2, c3 = 0, 1, 2, 3 #0321
	if (swapx): c0, c2 = 2, 0
	if (swapy): c1, c3 = 3, 1
	face.uv = [uv[c0], 16.0 - uv[c1], uv[c2], 16.0 - uv[c3]]	
	return face

#face[from vert, to vert, normal, uv[0-3]]
>>>>>>> c5a7e7bbe7c2440dc5ab8306b6b0099097fa371b
def export(faces, path):
	out = {}
	out['ambientocclusion'] = False
	out['textures'] = { 'z00' : 'blocks/z00'}
	out['elements'] = []
	for face in faces:
		p = {}
<<<<<<< HEAD
		p['from'] = list(map(round4, list(map(d16, list(mcos(face.fro.co))))))
		p['to'] = list(map(round4, list(map(d16, list(mcos(face.to.co))))))
=======
		p['from'] = list(map(d16, list(face.fro.co.yzx)))
		p['to'] = list(map(d16, list(face.to.co.yzx)))
>>>>>>> c5a7e7bbe7c2440dc5ab8306b6b0099097fa371b
		p['shade'] = False

		#uv face...
		uvf = {}
<<<<<<< HEAD
		sn = face.nor #normal in string form eg. 'UP'
		uvf[sn] = {}
		uvf[sn]['texture'] = '#z00'
		uvf[sn]['cullface'] = True
		uvf[sn]['uv'] = face.uv
		uvf[sn]['rotation'] = face.rotation % 360

		p['faces'] = uvf
		out['elements'].append(p)

=======
		sn = fd[tuple(face.nor.normalized().yzx)] #normal in string form #EDIT THIS XYZ!!!! OR fd
		uvf[sn] = {}
		uvf[sn]['texture'] = '#z00'
		uvf[sn]['cullface'] = True
		uvf[sn]['uv'] = face.uv		
		uvf[sn]['rotation'] = face.rot		
		p['faces'] = uvf
		out['elements'].append(p)	
>>>>>>> c5a7e7bbe7c2440dc5ab8306b6b0099097fa371b

	fi = open(path, 'w')
	fi.write(json.dumps(out, indent=4, separators=(',', ': ')))
	fi.close()

def main():
	global out, uv_layer
<<<<<<< HEAD
	print("[BmExp] Exporting!")
=======
	print("main called")
>>>>>>> c5a7e7bbe7c2440dc5ab8306b6b0099097fa371b

	me = bpy.context.object.data

	bm = bmesh.new()
	bm.from_mesh(me)
	
	bm.verts.ensure_lookup_table()
	bm.faces.ensure_lookup_table()
	uv_layer = bm.loops.layers.uv.active

	processedFaces = []
<<<<<<< HEAD
	for f in bm.faces:
=======
	forder = sorted(list(bm.faces), key = lambda f: f.verts[0].co.x)
	for f in forder:
>>>>>>> c5a7e7bbe7c2440dc5ab8306b6b0099097fa371b
		processedFaces.append(processFace(f))

	#export
	path = 'C:\\Users\\HM\\AppData\\Roaming\\.minecraft\\resourcepacks\\Konv2\\assets\\minecraft\\models\\block\\coal_ore.json'
	export(processedFaces, path)

	bm.free()  # free and prevent further access		

<<<<<<< HEAD
	print("[BmExp] done!")
=======
	print("done")
>>>>>>> c5a7e7bbe7c2440dc5ab8306b6b0099097fa371b
