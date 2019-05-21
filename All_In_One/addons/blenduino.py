import serial
import time
import threading
from multiprocessing import Queue
import bpy

# Meta information.
bl_info = {
	"name": "Blenduino",
	"author": "James",
	"version": (1, 0),
	"blender": (2, 80,0),
	"location": "Tools > Serial",
	"description": "Add Serial",
	"warning": "",
	"support": "TESTING",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Tool"
}

class SerialDataThread(threading.Thread):

	def __init__(self, name='SerialDataThread'):
		print("Starting SDT")
		self._stopevent = threading.Event()

		try:
			self.ser = serial.Serial( # Set Serial params
				port= bpy.context.scene.serial_port,
				baudrate= bpy.context.scene.serial_baud,
				timeout=1		# Timeout after 1 second. Prevents freezing if no data coming in
				# bytesize=serial.SEVENBITS,
				# parity=serial.PARITY_EVEN,
				# stopbits=serial.STOPBITS_ONE
			)
			self.ser.isOpen() # try to open port, if possible print message and proceed with 'while True:'
			print ("port is opened!")

		except IOError: # if port is already opened, close it, open it again and print message
			self.ser.close()
			self.ser.open()
			print ("Port reset.")


		threading.Thread.__init__(self, name=name)
		print("Thread started")
		#thread = threading.Thread(target=self.run, args=())

	def run(self):

		""" main control loop """
		while not self._stopevent.isSet():

			if(bpy.types.Scene.isSerialConnected == True):
				########################
				### Read Serial Here ###
				########################
				
				#If serial closed, open it
				if(self.ser.isOpen() == False):
					print("Opening Serial")
					self.ser.open()
				
				# Parse serial data
				line = str(self.ser.readline())
				line = line.replace("b'", "")   	# Remove byte flag from incoming string
				line = line.replace("\\r\\n'", "")  # Remove end line character
				line = line.rstrip()
				data = line.split(bpy.context.scene.serial_separator)	# Split by the user-defined character


				try:
					data.remove("") #Remove empty data
				except:
					pass

				# Only print/use data if it's the expected length
				if(len(data) == bpy.context.scene.serial_expected_length):
					c = 0
					for element in data:
						bpy.context.scene.serial_data[c] = int(element)
						if(bpy.context.scene.debug_serial): 
							print(bpy.context.scene.serial_data[c], end="\t")
						c = c+1
					if(bpy.context.scene.debug_serial): print()

				#########################
				### Write Serial Here ###
				#########################

				output = str(bpy.context.scene.serial_write_data)

				#Old array code
				# for value in bpy.context.scene.serial_write_data:
				# 	output += str(value) 
				# 	output += bpy.context.scene.serial_separator

				output += '\n'
				output = output.encode('utf-8') # Remove last separator character.

				print("Writing Serial: " + str(output))
				self.ser.write(output)  # Encoding mandated by pySerial docs: https://pythonhosted.org/pyserial/pyserial_api.html?highlight=write#serial.Serial.write
				


			else:

				#If serial open, close
				if(self.ser.isOpen() == True):
					print("Closing Serial")
					self.ser.close()

				print("Waiting to activate Serial")
				self._stopevent.wait(1)
			
		print("Thread has come to an end.")

	def join(self, timeout=2):
		""" Stop the thread. """
		print("Asking thread to stop")
		self._stopevent.set()
		threading.Thread.join(self, timeout)

class DebugSerial(bpy.types.Operator):

	bl_idname = "scene.debug_serial" 
	bl_label = "Debug Serial"
	bl_description = "Debug Serial in the python console"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.context.scene.debug_serial = not bpy.context.scene.debug_serial
		return{'FINISHED'}

class ToggleSerial(bpy.types.Operator):

	bl_idname = "scene.toggle_serial"  
	bl_label = "Toggle Serial"
	bl_description = "Toggle Serial Port"
	bl_options = {'REGISTER', 'UNDO'}



	def execute(self, context):

		# Kill any other Serial threads
		for thread in threading.enumerate():
			if(bpy.context.scene.debug_serial): print("Threads detected")
			if(thread.name == "SerialDataThread"):
				if(bpy.context.scene.debug_serial): print("Existing Thread Found. Exiting.")
				thread.join()

		scn = bpy.types.Scene
		print(">>> Toggling Serial class")
		
		if(scn.isSerialConnected == False):
			print("Beginning thread");
			serialThread = SerialDataThread()
			serialThread.start()	
			scn.isSerialConnected = True
			
		else:
			print("Attempting to kill threads")
			for thread in threading.enumerate():
				print("Threads detected")
				if(thread.name == "SerialDataThread"):
					print("Existing Thread Found. Exiting.")
					thread.join()
			scn.isSerialConnected = False
		
		print(scn.isSerialConnected)
		return {'FINISHED'}

# Menu setting.
class CreateSerialPanel(bpy.types.Panel):
	bl_label = "CREATE Serial"
	bl_idname = "create_serial" # class ID.
	bl_space_type = "VIEW_3D"   # Menu accessible from 3D viewport
	bl_region_type = "TOOLS"	# Menu lives in the left tool shelf.
	bl_category = "Serial"  	# Create new tab for Serial
	bl_context = (("objectmode"))
	 
	# Menu and input:
	def draw(self, context):
		obj = context.object
		scene = context.scene

		layout = self.layout

		row = layout.row()
		row.label("Serial Port")
		row.prop(scene, "serial_port") 

		row = layout.row()
		row.label("Baud Rate")
		row.prop(scene, "serial_baud")

		row = layout.row()
		row.label("Separator")
		row.prop(scene, "serial_separator")

		row = layout.row()
		row.label("Expected Length")
		row.prop(scene, "serial_expected_length")

		txt = "Stop Serial"
		icn = "PAUSE"   
		if bpy.context.scene.isSerialConnected == False:
			txt = "Start Serial"
			icn = "PLAY"

		layout.operator(ToggleSerial.bl_idname, icon=icn, text=txt)
		 
		if bpy.context.scene.debug_serial == False:
			txt = "Turn on serial debugging"
			icn = "LINENUMBERS_ON"
		else:
			txt = "Turn off serial debugging"
			icn = "LINENUMBERS_OFF"  

		layout.operator(DebugSerial.bl_idname, icon=icn, text=txt)

		# Panel to Serial Write data (controllable via drivers)
		row = layout.row()
		row.label("Data to Write")
		row.prop(scene, "serial_write_data")  

		c_read = 0
		for i in bpy.context.scene.serial_data:
			row = layout.row()
			row.label("Serial Data " + str(c_read) + ": " + str(bpy.context.scene.serial_data[c_read]))   
			c_read = c_read+1


			


# Set up scene-wide properties
def initSerialProperties():
	bpy.types.Scene.serial_port = bpy.props.StringProperty(
		name = "Serial Port",
		description = "Set test float",
		default = "COM4"
	)

	bpy.types.Scene.serial_baud =  bpy.props.IntProperty(
		name = "Baud Rate",
		description = "Set Baud Rate",
		default = 115200
	)

	bpy.types.Scene.serial_separator = bpy.props.StringProperty(
		name = "Data Separator",
		description = "What character separates your incoming data?",
		default = ","
	)

	bpy.types.Scene.isSerialConnected = bpy.props.BoolProperty(
		name = "Is Serial Connected",
		description = "Is the serial connected?",
		default = False
	)

	bpy.types.Scene.debug_serial = bpy.props.BoolProperty(
		name = "Serial Debugger",
		description = "Is the serial debugger active?",
		default = True
	)

	bpy.types.Scene.serial_expected_length = bpy.props.IntProperty(
		name = "Expected Data Length",
		description = "Expected length of incoming data",
		default=9
	)

	# Todo rename to serial_read_data
	bpy.types.Scene.serial_data = bpy.props.IntVectorProperty(
		name = "Serial Data Array",
		description = "What character separates your incoming data?",
		default=(0,0,0,0,0,0,0,0),
		size = 8
	)

	bpy.types.Scene.serial_write_data = bpy.props.IntProperty(
		name = "Serial Write Array",
		description = "The outgoing data. For now just 1 int",
		default = 0
	)

# Remove addon data if addon is closed.
def removeSerialProperties():
	scn = bpy.context.scene
	del scn.serial_port
	del scn.serial_baud
	del scn.serial_separator
	del scn.isSerialConnected
	del scn.debug_serial
	del scn.serial_expected_length
	del scn.serial_data
	del scn.serial_write_data

def register():
	initSerialProperties()
	bpy.utils.register_module(__name__)
	print("Blenduino was activated.")

def unregister():
	#Remove addon data
	removeSerialProperties()
	bpy.utils.unregister_module(__name__)
	print("Blenduino was deactivated.")

#For local testing
if __name__ == "__main__":
	register()
	

#########
###END###
#########


#Todo: Update menu window on serial update.

#todo: [Big picture] implement more reliable threading (use queues?)

	#     def run(self):
	#   	while(True):
				# if(self.stop == True):
				#   return

				# if(bpy.types.Scene.isSerialConnected == True):
				#   print ("reading")
				#   time.sleep(.5)
				# else:
				#   print("not reading")
				#   time.sleep(1)



# # Set these values in window?
# def add_driver(
#   	  source, target, prop, dataPath,
#   	  index = -1, negative = False, func = ''
#     ):
#     ''' Add driver to source prop (at index), driven by target dataPath '''

#     if index != -1:
#   	  d = source.driver_add( prop, index ).driver
#     else:
#   	  d = source.driver_add( prop ).driver

#     v = d.variables.new()
#     v.name				 = prop
#     v.targets[0].id   	 = target
#     v.targets[0].data_path = dataPath

#     d.expression = func + "(" + v.name + ")" if func else v.name
#     d.expression = d.expression if not negative else "-1 * " + d.expression




# class ResetSerial(bpy.types.Operator):

#   bl_idname = "scene.reset_serial"  # Access the class by bpy.ops.object.create_serial.
#   bl_label = "Reset Serial"
#   bl_description = "Reset Serial Port"
#   bl_options = {'REGISTER', 'UNDO'}

#   def execute(self,context):

#   	for thread in threading.enumerate():
#   		if(thread.name == "SerialDataThread"):
#   			print("Existing Thread Found. Exiting.")
#   			thread.join()

#   	serialThread = SerialDataThread()
#   	serialThread.start()
#   	return {'FINISHED'}
