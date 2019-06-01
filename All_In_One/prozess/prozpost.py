'''
Create GL friendly data from blender dump.
NOTE: requires pyglet: http://www.pyglet.org/
NOTE: requires python 2.6 or newer (but not python3, due to pyglet)
'''
import sys
import os
import pyglet
import prozscene as proz

def prozpost(path):
	print 'Loading scene: ', path
	scene = proz.Scene(path)
	write_images(scene)
	write_meshes(scene)

def write_images(scene):
	for imgdict in scene.data_images().values():
		imgfile = imgdict['file']
		imgdir = scene.image_dir()
		imgpath = os.path.join(imgdir, imgfile)
		print 'Loading image: ', imgpath
		img = pyglet.image.load(imgpath).get_image_data()
		print 'Image format:', img.format, ' width:', img.width, ' height:', img.height
		pitch = len(img.format) * img.width
		pixels = img.get_data(img.format, pitch)
		rawpath = imgpath + '.raw'
		print 'Writing raw pixels: ', rawpath
		with open(rawpath, 'w') as f:
			f.write(pixels)

def write_meshes(scene):
	for meshdict in scene.data_meshes().values():
		meshname = meshdict['name']
		print 'Loading mesh: ', meshname
		mesh = scene.load_mesh(meshname)
		print 'Mesh indices:', len(mesh.index), ' vertices:', len(mesh.vertex)/6

if __name__ == '__main__':
	prozpost(sys.argv[1])
