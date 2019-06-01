import bpy
import os
import subprocess
from bpy.app.handlers import persistent




def get_context_override_uv():
	for window in bpy.context.window_manager.windows:
		screen = window.screen
		for area in screen.areas:
			if area.type == 'IMAGE_EDITOR':
				return {'window': window, 'screen': screen, 'area': area}
	return None


blend_call = None

@persistent
def load_handler(dummy):
	global blend_call
	# do the deletes here now everything is properly loaded up
	if blend_call:
		blend_call()
		blend_call = None #Clear Again
bpy.app.handlers.load_post.append(load_handler)


class Op_Test:
	name = ""
	blend = ""
	python = ""
	test = None
	def __init__(self, name, python="", blend="", test=None):
		self.name = name
		self.python = python
		self.blend = blend
		self.test = test

	def run(self):
		print("Run test '{}'".format(self.name))

		# Execute test
		if self.test:
			global blend_call
			blend_call = self.test

		# Open blend file first
		if self.blend:
			self.open_blend()
		else:
			# Execute without Blend file
			if self.test:
				self.test()
		

	def open_python(self):
		# https://stackoverflow.com/questions/281888/open-explorer-on-a-file
		# subprocess.Popen(r'explorer /select,"C:\path\of\folder\file"')
		# subprocess.call("explorer C:\\temp\\yourpath", shell=True)
		print("Open PY File")

	def open_blend(self):
		if self.blend != "":
			path = os.path.join(os.path.dirname(__file__), "blend\\{}.blend".format(self.blend))
			print("Open Blend File {} \n{}".format(self.blend, path))

			bpy.ops.wm.open_mainfile(filepath=path)


		# https://stackoverflow.com/questions/281888/open-explorer-on-a-file
		# subprocess.Popen(r'explorer /select,"C:\path\of\folder\file"')
		# subprocess.call("explorer C:\\temp\\yourpath", shell=True)
		