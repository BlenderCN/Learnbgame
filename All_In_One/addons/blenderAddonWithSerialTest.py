import serial
import time
import threading
import bpy
from random import randint


bl_info = {
	"name": "Create Cubez",
	"category": "Object",
}

class CreateCubes(bpy.types.Operator):
	"""My Object Moving Script"""      # blender will use this as a tooltip for menu items and buttons.
	bl_idname = "object.create_cubes"        # unique identifier for buttons and menu items to reference.
	bl_label = "Create ten cubes"         # display name in the interface.
	bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

	count = bpy.props.IntProperty(name="Steps", default=10, min=1, max=100)

	port = bpy.props.StringProperty(name="Port", default="COM4")
	ser = serial.Serial("COM4", 9600)

	def execute(self, context):        # execute() is called by blender when running the operator.
		
		# The original script
		for c in range(0, self.count):
			x = c*2.5
			y = 0
			z = 0
			bpy.ops.mesh.primitive_cube_add(location=(x,y,z))

		return {'FINISHED'}            # this lets blender know the operator finished successfully.


def menu_func(self, context):
    self.layout.operator(CreateCubes.bl_idname)
     self.layout.operator(CreateCubes.bl_idname)

def register():
	bpy.types.INFO_MT_add.append(menu_func)
	bpy.utils.register_class(CreateCubes)


def unregister():
	bpy.utils.unregister_class(CreateCubes)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
	register()


print("-----")


"""
# Serial code below. Saved for l8r

ser = serial.Serial("COM4", 9600)

def readSerialData():
	while True:
		line = str(ser.readline())
		line = line.replace("b'", "")
		line = line.replace("\\r\\n'", "")
		print(type(line))
		d = line.split(':')
		print(d)
		

		for i in range (0, len(d)-1):
			if(d[i] == "1"):
				bpy.data.objects[i].scale = (1, 10, 1)
			else:
				bpy.data.objects[i].scale = (1, 1, 1)

def doOtherStuff():
	txt = input("INPUT: ")
	if(txt == "0"):
		exit()

threading.Thread(target=readSerialData).start()
#threading.Thread(target=doOtherStuff).start()
"""