import os
from .other import Camera,Point,Feature,gen_lines,readlisti,readlistf,getCamNameFromFileName

def read_cam(lines, name):
	""" return Camera(name, focal, k1, k2, rotation, translation) """
	f, kx, ky = readlistf(next(lines))
	R = (readlistf(next(lines)),readlistf(next(lines)),readlistf(next(lines)))
	t = readlistf(next(lines))

	return Camera(name, f, kx, ky, R, t)

def read_point(lines):
	""" return Point(pos, col, ( Feature(camID, key, sx, sy), ... ) ) """
	pos = readlistf(next(lines))
	col=readlistf(next(lines))
	views, *lst = next(lines).split()
	views = int(views) 
	
	view_list = list()
	for i in range(views):
		camId,key,sx,sy,*lst = lst
		view_list.append(Feature(int(camId),int(key),float(sx),float(sy)))

	return (pos, col, view_list)

#	""" cf https://www.cs.cornell.edu/~snavely/bundler/bundler-v0.4-manual.html#S6
#	# Bundle file v0.3
#	<num_cameras> <num_points>   [two integers]
#	<camera1>
#	   ...
#	<cameraN>
#	<point1>
#	   ...
#	<pointM>
#
#	<camera> := <f> <k1> <k2> [the focal length, followed by two radial distortion coeffs]
#	            <R>           [a 3x3 matrix representing the camera rotation]
#	            <t>           [a 3-vector describing the camera translation]
#
#	<point> := <position>   [a 3-vector describing the 3D position of the point]
#	           <color>      [a 3-vector describing the RGB color of the point]
#	           <view list>  [a list of views the point is visible in]
#
#	<view list> := <cameraNum> <key> <x> <y>
#  The pixel positions are floating point numbers in a coordinate system where the origin
#  is the center of the image, the x-axis increases to the right, and the y-axis increases
#  towards the top of the image. 
#	"""

#Example of use (actually not used)
class Bundle:
	def __init__(self,bundlefile,cameraNames=None):
		self.cameras = list()
		self.points  = list()

		camNames = cameraNames
		if not camNames:
			#load the file with the corresponding images name
			dirname =  os.path.dirname(bundlefile)
			listfile_path = os.path.join(dirname, 'listfile.txt')
			with open(listfile_path, 'r') as f:
				listfile = f.readlines()
			listfile = [ l.split()[0] for l in listfile ]
			# and extract camera names from image filename
			#camNames = list(map(getCamNameFromFileName, listfile ) )
			camNames = [ l.strip(' \n\t\r') for l in listfile ]

		with open(bundlefile,'r') as f:
			lines = gen_lines(f)
			(numCam, numPts) = readlisti(next(lines))
			#assert( numCam == len(camNames) ) #disabled to pass a generator
			for i,name in zip(range(numCam),camNames):
				self.cameras.append(read_cam(lines,name))

			for i in range(numPts):
				try:
					self.points.append(read_point((lines)))
				except StopIteration:
					print("WARNING : Corrupted Bundle file !!! Expected Points",numPts,"found",i)
					break

	def camNameFromID(self, camID):
		return self.cameras[camID].name

# vim: set ts=4 sw=4 tw=90 ff=unix noet :
