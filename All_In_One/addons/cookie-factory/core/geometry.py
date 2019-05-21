# ##### BEGIN LGPL LICENSE BLOCK #####
#
#  Copyright (C) 2018 Nikolai Janakiev
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this library; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END LGPL LICENSE BLOCK #####


import bpy
import bmesh
from mathutils import Vector, Matrix, Color
from mathutils.noise import random_unit_vector
from math import sin, cos, tan, asin, acos, atan2, pi
PI, TAU = pi, 2*pi
import numpy as np
import logging

logger = logging.getLogger(__name__)


def map_range(value, start1, stop1, start2, stop2):
	return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))


def uv_from_vector(vector):
    x, y, z = vector.normalized()
    phi, theta = atan2(y, x), asin(z)
    u, v = (phi + PI)/TAU, (theta + PI/2)/PI

    return u, v


def get_frame(p, as_matrix=False):
    p = Vector(p)
    N = p.normalized()
    B = N.cross((0, 0, -1))
    if(B.length == 0):
        B, T = Vector((1, 0, 0)), Vector((0, 1, 0))
    else:
        B.normalize()
        T = N.cross(B).normalized()

    if as_matrix:
    	return Matrix([T, B, N]).to_4x4().transposed()
    else:
    	return T, N, B


def random_orientation_matrix(size=4):
	if size == 2:
		V = random_unit_vector(2)
		N = Vector((V.y, -V.x))
		return Matrix([V, N])

	N, V = random_unit_vector(), random_unit_vector()
	E1 = N.cross(V).normalized()
	E2 = N.cross(E1).normalized()
	if(N.length == 0 or E1.length == 0 or E2.length == 0):
		return random_orientation_matrix()

	if size == 3:
		return Matrix([E1, E2, N])
	elif size == 4:
		return Matrix([E1, E2, N]).to_4x4()
	else:
		raise ValueError('can only return 2x2, 3x3 or 4x4 matrix')


def icosphere_mesh(bm, location=(0, 0, 0), diameter=1.0, subdivisions=1, material_index=0, smooth=False, matrix=Matrix()):
	M = Matrix.Translation(location) * matrix
	verts = bmesh.ops.create_icosphere(bm, diameter=diameter, subdivisions=subdivisions, matrix=M)['verts']
	if material_index != 0 or smooth == True:
		for vert in verts:
			for face in vert.link_faces:
				face.material_index = material_index
				face.smooth = smooth


def icosphere(location=(0, 0, 0), diameter=1.0, subdivisions=1, matrix=Matrix()):
	# Create an empty mesh and the object
	mesh = bpy.data.meshes.new('Icosphere')
	obj = bpy.data.objects.new('Icosphere', mesh)

	# Add the object to the scene
	bpy.context.scene.objects.link(obj)
	obj.location = location

	# Construct bmesh cube and assign it to blender mesh
	bm = bmesh.new()
	bmesh.ops.create_icosphere(bm, diameter=diameter, matrix=matrix)
	bm.to_mesh(mesh)
	bm.free()

	return obj


def cube_mesh(bm, location=(0, 0, 0), size=1.0, material_index=0, matrix=Matrix()):
	M = Matrix.Translation(location) * matrix
	verts = bmesh.ops.create_cube(bm, size=size, matrix=M)['verts']
	if material_index != 0:
		for vert in verts:
			for face in vert.link_faces:
				face.material_index = material_index


def cube(location=(0, 0, 0), size=1.0, matrix=Matrix()):
	# Create an empty mesh and the object
	mesh = bpy.data.meshes.new('Cube')
	obj = bpy.data.objects.new('Cube', mesh)

	# Add the object to the scene
	bpy.context.scene.objects.link(obj)
	obj.location = location

	# Construct bmesh cube and assign it to blender mesh
	bm = bmesh.new()
	bmesh.ops.create_cube(bm, size=size, matrix=matrix)
	bm.to_mesh(mesh)
	bm.free()

	return obj


def bmesh_to_object(bm, name='Object'):
	mesh = bpy.data.meshes.new(name+'Mesh')
	bm.to_mesh(mesh)
	bm.free()

	obj = bpy.data.objects.new(name, mesh)
	bpy.context.scene.objects.link(obj)
	bpy.context.scene.update()

	return obj


def append_geometry(bm, verts, faceIndicesList, location=(0, 0, 0), smooth=False, material_index=0, matrix=Matrix()):
	if bm is None: bm = bmesh.new()

	vertList = []
	for vert in verts:
		vertList.append(bm.verts.new(matrix * vert + Vector(location)))

	faces = []
	for faceIndices in faceIndicesList:
		face = bm.faces.new(tuple(vertList[i] for i in faceIndices))
		face.smooth = smooth
		face.material_index = material_index
		faces.append(face)

	bmesh.ops.recalc_face_normals(bm, faces=faces)

	return bm


def geometry_to_object(points, faces, location=(0, 0, 0), name='Shape'):
	verts = points
	faces = [tuple(int(value) for value in face) for face in faces]

	# Create mesh and object
	mesh = bpy.data.meshes.new(name+'Mesh')
	obj  = bpy.data.objects.new(name, mesh)
	obj.location = location
	# Link object to scene
	bpy.context.scene.objects.link(obj)
	# Create mesh from given verts and faces
	mesh.from_pydata(verts, [], faces)
	#Update mesh with new data
	mesh.update(calc_edges=True)
	return obj


def circle_path(n, r, v1=(1,0,0), v2=(0,1,0), phi=0):
	points, directions, normals = [], [], []
	v1, v2 = Vector(v1), Vector(v2)

	normal = v1.cross(v2)
	normal.normalize()

	for i in range(n):
		t = float(i)/float(n)
		# Calculate points on circle
		p = r*(v1*cos(TAU*t + phi) + v2*sin(TAU*t + phi))
		points.append(p)

		# Calculate directions (tangents)
		d = -v1*sin(TAU*t + phi) + v2*cos(TAU*t + phi)
		directions.append(d)

		# Calculate the normals
		n0 = normal.cross(d)
		n0.normalize()
		normals.append(n0)

	return points, directions, normals


def random_sphere_points(n, r=1):
	u = np.random.random((n, 1))
	v = np.random.random((n, 1))
	phiList = TAU*u
	thetaList = np.arccos(2*v - 1) + PI/2  # Uniform distribution on sphere

	return [Vector((r*np.cos(theta)*np.cos(phi), \
					r*np.cos(theta)*np.sin(phi), \
					r*np.sin(theta))) \
					for (phi, theta) in zip(phiList, thetaList)]


def parametric_surface_geometry(mapping, n=100, m=100, location=(0, 0, 0), uClosed=False, vClosed=False, quads=True):
	logger.debug('parametric_surface_geometry called')
	verts, faces = [], []

	# Create uniform n by m grid
	for col in range(m):
		for row in range(n):
			u, v = row/n, col/m

			# Create surface
			p = mapping(u, v)
			verts.append(p)

			if(row < (n - (not uClosed)) and col < (m - (not vClosed))):
				# Connect first and last vertices on the u and v axis
				rowNext = (row + 1) % n
				colNext = (col + 1) % m
				if quads:
					faces.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext, (colNext*n) + row))
				else:
					# Indices for first triangle
					faces.append(((col*n) + row, (colNext*n) + rowNext, (colNext*n) + row))
					# Indices for second triangle
					faces.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext))

	#logger.debug('verts : ' + str(len(verts)))
	#logger.debug('faces : ' + str(len(faces)))
	return verts, faces


def parametric_surface(mapping, n, m, location=(0, 0, 0), uClosed=False, vClosed=False, quads=True, smooth=False, name='Surface'):
	logger.debug('parametric_surface called')
	verts, faces = parametric_surface_geometry(mapping, n, m, location, uClosed, vClosed, quads)

	# Create mesh
	mesh = bpy.data.meshes.new(name+'Mesh')
	# Create object
	obj  = bpy.data.objects.new(name, mesh)
	obj.location = location
	# Link object to scene
	bpy.context.scene.objects.link(obj)
	# Create mesh from given verts and faces
	mesh.from_pydata(verts, [], faces)
	#Update mesh with new data
	mesh.update(calc_edges=True)

	# Make mesh smooth
	if smooth:
		for p in mesh.polygons:
			p.use_smooth = smooth

	return obj


def parametric_surface_mesh(bm, surfaceMapping, n=10, m=10, location=(0, 0, 0), quads=True, uClosed=False, vClosed=False, smooth=False, material_index=0, matrix=Matrix()):
	location = Vector(location)
	verts, faces, faceIndicesList = [], [], []
	for col in range(m):
		for row in range(n):
			u, v = float(row)/float(n - (not uClosed)), float(col)/float(m - (not vClosed))
			#u, v = float(row)/float(n - 1), float(col)/float(m - 1)
			vert = Vector(surfaceMapping(u, v))
			verts.append(bm.verts.new(matrix*vert + location))

			if row < (n - (not uClosed)) and col < (m - (not vClosed)):
				rowNext = (row + 1) % n
				colNext = (col + 1) % m
				if quads:
					faceIndicesList.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext, (colNext*n) + row))
				else:
					faceIndicesList.append(((col*n) + row, (colNext*n) + rowNext, (colNext*n) + row))
					faceIndicesList.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext))

	for faceIndices in faceIndicesList:
		face = bm.faces.new(tuple(verts[i] for i in faceIndices))
		face.smooth = smooth
		face.material_index = material_index
		faces.append(face)

	bmesh.ops.recalc_face_normals(bm, faces=faces)


def patch_mesh(bm, points, location=(0, 0, 0), quads=True, uClosed=False, vClosed=False, uCap=False, vCap=False, smooth=False, material_index=0, matrix=Matrix()):
	location = Vector(location)
	verts, faces, faceIndicesList = [], [], []
	n, m = np.shape(points)[:2]

	for col in range(m):
		for row in range(n):
			vert = Vector(points[row][col])
			verts.append(bm.verts.new(matrix*vert + location))

			if row < (n - (not uClosed)) and col < (m - (not vClosed)):
				rowNext = (row + 1) % n
				colNext = (col + 1) % m
				if quads:
					faceIndicesList.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext, (colNext*n) + row))
				else:
					faceIndicesList.append(((col*n) + row, (colNext*n) + rowNext, (colNext*n) + row))
					faceIndicesList.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext))

	if uCap:
		faceIndicesList.append(np.arange(0, n*m, n))
		faceIndicesList.append(np.arange(n - 1, n*m, n))
	if vCap:
		faceIndicesList.append(np.arange(n))
		faceIndicesList.append(np.arange(n*(m - 1), n*m))

	for faceIndices in faceIndicesList:
		face = bm.faces.new(tuple(verts[i] for i in faceIndices))
		face.smooth = smooth
		face.material_index = material_index
		faces.append(face)

	bmesh.ops.recalc_face_normals(bm, faces=faces)


def torus_surface(name, location, R0, r0, X):
	logger.debug('torus_surface called')
	verts, faces = [], []
	(n, m) = np.shape(X)

	# Create uniform n by m grid
	for col in range(m):
		for row in range(n):
			u, v = row/n, col/m
			r = r0 + X[row, col]

			# Create surface
			p = ((R0 + r*cos(TAU*v))*cos(TAU*u), \
				 (R0 + r*cos(TAU*v))*sin(TAU*u), \
				 r*sin(TAU*v))
			verts.append(p)

			# Connect first and last vertices on the u and v axis
			rowNext = (row + 1) % n
			colNext = (col + 1) % m
			# Indices for first triangle
			faces.append(((col*n) + row, (colNext*n) + rowNext, (colNext*n) + row))
			# Indices for second triangle
			faces.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext))

	logger.debug('verts : ' + str(len(verts)))
	logger.debug('faces : ' + str(len(faces)))
	# Create mesh and object
	mesh = bpy.data.meshes.new(name+'Mesh')
	obj  = bpy.data.objects.new(name, mesh)
	obj.location = location
	# Link object to scene
	bpy.context.scene.objects.link(obj)
	# Create mesh from given verts and faces
	mesh.from_pydata(verts, [], faces)
	#Update mesh with new data
	mesh.update(calc_edges=True)
	return obj


def torus_mesh(bm, R, r, n=40, m=20, location=(0, 0, 0), smooth=False, material_index=0, matrix=Matrix()):
	def torus(u, v):
		return ((R + r*cos(TAU*v))*cos(TAU*u), \
				(R + r*cos(TAU*v))*sin(TAU*u), \
				r*sin(TAU*v))

	parametric_surface_mesh(bm, torus, n, m, location, uClosed=True, vClosed=True, smooth=smooth, material_index=material_index, matrix=matrix)


def parametric_heightmap(X, extent=[-10,10,-10,10], location=(0, 0, 0), uClosed=False, vClosed=False, name='Shape'):
	logger.debug('parametric_heightmap called')
	verts = list()
	faces = list()

	# Create uniform n by m grid
	n, m = X.shape
	for row in range(n):
		for col in range(m):
			u = map_range(col/(m - 1), 0, 1, extent[0], extent[1])
			v = map_range(row/(n - 1), 0, 1, extent[2], extent[3])

			# Get vertices
			p = (u, v, X[row,col])
			verts.append(p)

			if(row < (n - (not uClosed)) and col < (m - (not vClosed))):
				# Connect first and last vertices on the u and v axis
				rowNext = (row + 1) % n
				colNext = (col + 1) % m
				# Indices for first triangle
				faces.append(((col*n) + row, (colNext*n) + rowNext, (colNext*n) + row))
				# Indices for second triangle
				faces.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext))

	logger.debug('verts : ' + str(len(verts)))
	logger.debug('faces : ' + str(len(faces)))

	# Create mesh and object
	mesh = bpy.data.meshes.new(name+'Mesh')
	obj  = bpy.data.objects.new(name, mesh)
	obj.location = location
	# Link object to scene
	bpy.context.scene.objects.link(obj)
	# Create mesh from given verts and faces
	mesh.from_pydata(verts, [], faces)
	#Update mesh with new data
	mesh.update(calc_edges=True)
	return obj


def disc_geometry(location, n, r, h, v1=(1,0,0), v2=(0,1,0), phi=0):
	v1, v2 = Vector(v1), Vector(v2)
	normal = v1.cross(v2)
	normal.normalize()

	points, faces = [], []

	h0 = location - h*normal
	h1 = location + h*normal
	points.append(h0)
	points.append(h1)

	for i in range(n):
		t = float(i)/float(n)
		p0 = h0 + r*(v1*cos(TAU*t + phi) + v2*sin(TAU*t + phi))
		p1 = h1 + r*(v1*cos(TAU*t + phi) + v2*sin(TAU*t + phi))
		points.append(p0)
		points.append(p1)

		idx0 = 2*i + 2
		idx1 = 2*i + 3
		iNext0 = (idx0 % (2*n)) + 2
		iNext1 = (idx1 % (2*n)) + 2

		faces.append((idx0, 0, iNext0))
		faces.append((1, idx1, iNext1))
		faces.append((idx1, idx0, iNext0, iNext1))

	return points, faces


def disc_mesh(bm, n, r, h, location=(0,0,0), e0=(1,0,0), e1=(0,1,0), normal=None, phi=0, smooth=False, material_index=0, matrix=Matrix()):
	location, e0, e1 = Vector(location), Vector(e0), Vector(e1)
	verts, faces, faceIndicesList = [], [], []

	if normal is None:
		normal = e0.cross(e1)
		normal.normalize()
	else:
		normal = Vector(normal)

	h0 = -h*normal
	h1 = +h*normal
	verts.append(bm.verts.new(matrix*h0 + location))
	verts.append(bm.verts.new(matrix*h1 + location))

	for i in range(n):
		t = float(i)/float(n)
		p0 = h0 + r*(e0*cos(TAU*t + phi) + e1*sin(TAU*t + phi))
		p1 = h1 + r*(e0*cos(TAU*t + phi) + e1*sin(TAU*t + phi))
		verts.append(bm.verts.new(matrix*p0 + location))
		verts.append(bm.verts.new(matrix*p1 + location))

		idx0 = 2*i + 2
		idx1 = 2*i + 3
		iNext0 = (idx0 % (2*n)) + 2
		iNext1 = (idx1 % (2*n)) + 2

		faceIndicesList.append((idx0, 0, iNext0))
		faceIndicesList.append((1, idx1, iNext1))
		faceIndicesList.append((idx1, idx0, iNext0, iNext1))

	for faceIndices in faceIndicesList:
		face = bm.faces.new(tuple(verts[i] for i in faceIndices))
		face.smooth = smooth
		face.material_index = material_index
		faces.append(face)

	bmesh.ops.recalc_face_normals(bm, faces=faces)


def cone_geometry(c0, c1, r, n, v0=None, v1=None):
	c0, c1 = Vector(c0), Vector(c1)
	verts, faces = [], []
	verts.append(c0)
	verts.append(c1)
	if v0 is None and v1 is None:
		N = c0 - c1
		N.normalize()
		v0 = N.cross((0,0,1))
		if(v0.length == 0):
			v0, v1 = Vector((1, 0, 0)), Vector((0, 1, 0))
		else:
			v0.normalize()
			v1 = N.cross(v0)
			v1.normalize()
	else:
		v0, v1 = Vector(v0), Vector(v1)

	for i in range(n):
		t = float(i) / float(n)
		vert = c1 + r*(v0*cos(TAU*t) + v1*sin(TAU*t))
		#vert = (c0 + c1)/2 + r*(v0*cos(TAU*t) + v1*sin(TAU*t))
		verts.append(vert)

		iNext = (i + 1) % n
		faces.append((2+i, 0, 2+iNext))
		faces.append((1, 2+i, 2+iNext))

	return verts, faces


def cone_mesh(bm, c0, c1, r, n=6, v0=None, v1=None, location=(0, 0, 0), material_index=0, smooth=False, matrix=Matrix()):
	if bm is None: bm = bmesh.new()

	verts, faces = cone_geometry(c0, c1, r, n, v0, v1)
	append_geometry(bm, verts, faces, location=location, smooth=smooth, material_index=material_index, matrix=matrix)

	return bm


def pipe_geometry(A, B, n, r0, r1, closed=False, phi=0):
	points, faces = [], []
	A, B = Vector(A), Vector(B)

	# Setup of vectors
	N = B - A
	N.normalize()
	F = N.cross((0,0,1))
	if(F.length == 0):
		F, E = Vector((1, 0, 0)), Vector((0, 1, 0))
	else:
		F.normalize()
		E = N.cross(F)
		E.normalize()

	if(closed):
		points.append(A)
		points.append(B)

	for i in range(n):
		t = float(i)/float(n)
		p0 = A + r0*(F*cos(TAU*t + phi) + E*sin(TAU*t + phi))
		p1 = B + r1*(F*cos(TAU*t + phi) + E*sin(TAU*t + phi))
		points.append(p0)
		points.append(p1)

		if(closed):
			idx0, idx1 = 2*i + 2, 2*i + 3
			iNext0, iNext1 = (idx0 % (2*n)) + 2, (idx1 % (2*n)) + 2
			faces.append((idx0, 0, iNext0))
			faces.append((1, idx1, iNext1))
			faces.append((idx1, idx0, iNext0, iNext1))
		else:
			idx0, idx1 = 2*i, 2*i + 1
			iNext0, iNext1 = (idx0 + 2) % (2*n), (idx1 + 2) % (2*n)
			faces.append((idx1, idx0, iNext0, iNext1))

	return points, faces


def pipe_mesh(bm, A, B, r0, r1=None, n=6, closed=False, phi=0, location=(0, 0, 0), smooth=False, material_index=0, matrix=Matrix()):
	location = Vector(location)
	if r1 is None: r1 = r0

	verts = []
	A, B = Vector(A), Vector(B)
	r0, r1, n = float(r0), float(r1), int(n)

	# Setup of vectors
	N = B - A
	N.normalize()
	F = N.cross((0,0,1))
	if(F.length == 0):
		F, E = Vector((1, 0, 0)), Vector((0, 1, 0))
	else:
		F.normalize()
		E = N.cross(F)
		E.normalize()

	if(closed):
		verts.append(bm.verts.new(matrix*A + location))
		verts.append(bm.verts.new(matrix*B + location))

	for i in range(n):
		t = float(i)/float(n)
		p0 = A + r0*(F*cos(TAU*t + phi) + E*sin(TAU*t + phi))
		p1 = B + r1*(F*cos(TAU*t + phi) + E*sin(TAU*t + phi))
		verts.append(bm.verts.new(matrix*p0 + location))
		verts.append(bm.verts.new(matrix*p1 + location))

	faces = []
	for i in range(n):
		if(closed):
			idx0, idx1 = 2*i + 2, 2*i + 3
			iNext0, iNext1 = (idx0 % (2*n)) + 2, (idx1 % (2*n)) + 2
			vA, vB, v0, v1 = verts[0], verts[1], verts[idx0], verts[idx1]
			vNext0, vNext1 = verts[iNext0], verts[iNext1]

			for faceInidces in [(v0, vA, vNext0), (vB, v1, vNext1), (v1, v0, vNext0, vNext1)]:
				face = bm.faces.new(faceInidces)
				face.material_index = material_index
				face.smooth = smooth
				faces.append(face)
		else:
			idx0, idx1 = 2*i, 2*i + 1
			iNext0, iNext1 = (idx0 + 2) % (2*n), (idx1 + 2) % (2*n)
			v0, v1 = verts[idx0], verts[idx1]
			vNext0, vNext1 = verts[iNext0], verts[iNext1]

			face = bm.faces.new((v1, v0, vNext0, vNext1))
			face.material_index = material_index
			face.smooth = smooth
			faces.append(face)

	bmesh.ops.recalc_face_normals(bm, faces=faces)


def tube_mesh(bm, points, r=1, n=6, location=(0, 0, 0), quads=True, closed=False, smooth=False, material_index=0, matrix=Matrix()):
	location = Vector(location)
	verts, faces, faceIndicesList = [], [], []
	m = len(points)

	for col in range(m):
		for row in range(n):
			u = float(row)/float(n)

			if(closed or (0 < col and col < (m - 1))):
				tangent = Vector(points[(col + 1) % m]) - Vector(points[col - 1])
				tangent.normalize()
			else:
				if(col == 0):
					tangent = Vector(points[col + 1]) - Vector(points[col])
					tangent.normalize()
				elif(col == (m - 1)):
					tangent = Vector(points[col]) - Vector(points[col - 1])
					tangent.normalize()

			p  = Vector(points[col])
			e0 = Vector((tangent.y, -tangent.x, 0))
			e0.normalize()
			e1 = e0.cross(tangent)
			point = p + r*(e0*cos(TAU*u) + e1*sin(TAU*u))

			verts.append(bm.verts.new(matrix*point + location))
			if(col < (m - (not closed))):
				rowNext = (row + 1) % n
				colNext = (col + 1) % m
				if(quads):
					faceIndicesList.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext, (colNext*n) + row))
				else:
					faceIndicesList.append(((col*n) + row, (colNext*n) + rowNext, (colNext*n) + row))
					faceIndicesList.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext))

	for faceIndices in faceIndicesList:
		face = bm.faces.new(tuple(verts[i] for i in faceIndices))
		face.smooth = smooth
		face.material_index = material_index
		faces.append(face)

	bmesh.ops.recalc_face_normals(bm, faces=faces)


def parametric_heightmap_mesh(bm, X, extent=[-10,10,-10,10], location=(0, 0, 0), quads=True, smooth=False, uClosed=False, vClosed=False, material_index=0, matrix=Matrix()):
	location = Vector(location)
	verts, faces, faceIndicesList = [], [], []

	n, m = X.shape
	for col in range(m):
		for row in range(n):
			u = map_range(col/(m - 1), 0, 1, extent[0], extent[1])
			v = map_range(row/(n - 1), 0, 1, extent[2], extent[3])

			point = Vector((u, v, X[row,col]))
			verts.append(bm.verts.new(matrix*point + location))

			if(row < (n - (not uClosed)) and col < (m - (not vClosed))):
				rowNext = (row + 1) % n
				colNext = (col + 1) % m
				if(quads):
					faceIndicesList.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext, (colNext*n) + row))
				else:
					faceIndicesList.append(((col*n) + row, (colNext*n) + rowNext, (colNext*n) + row))
					faceIndicesList.append(((col*n) + row, (col*n) + rowNext, (colNext*n) + rowNext))

	for faceIndices in faceIndicesList:
		face = bm.faces.new(tuple(verts[i] for i in faceIndices))
		face.smooth = smooth
		face.material_index = material_index
		faces.append(face)

	bmesh.ops.recalc_face_normals(bm, faces=faces)
