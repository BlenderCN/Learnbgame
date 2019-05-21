'''

  V-Ray/Blender

  http://vray.cgdo.ru

  Author: Andrey M. Izrantsev (aka bdancer)
  E-Mail: izrantsev@cgdo.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *
from vb25.ui import ui


TYPE= 'SETTINGS'
ID=   'RTEngine'

NAME= 'Realtime Engine'
DESC= "V-Ray Realtime Engine"

PARAMS= (
	'enabled',
	'separate_window',
	'trace_depth',
	'use_gi',
	'gi_depth',
	'gi_reflective_caustics',
	'gi_refractive_caustics',
	'bundle_size',
	'samples_per_pixel',
	'coherent_tracing',
	'use_opencl',
	'stereo_mode',
	'stereo_eye_distance',
	'stereo_focus',
	'opencl_texsize',
)

PARAMS_SETTINGS_RT_ENGINE = (
	'trace_depth',
	'use_gi',
	'gi_depth',
	'gi_reflective_caustics',
	'gi_refractive_caustics',
	'bundle_size',
	'samples_per_pixel',
	'coherent_tracing',
	'stereo_mode',
	'stereo_eye_distance',
	'stereo_focus',
	'opencl_texsize',
)


def add_properties(rna_pointer):
	class RTEngine(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(RTEngine)

	rna_pointer.RTEngine= PointerProperty(
		name= NAME,
		type= RTEngine,
		description= "V-Ray Realtime Engine settings"
	)

	# enabled
	RTEngine.enabled= BoolProperty(
		name= "Realtime engine",
		description= "Enable the RT engine",
		default= False
	)

	# separate_window
	RTEngine.separate_window= BoolProperty(
		name= "Separate window",
		description= "True to open a separate window for the RTEngine, and false to use the V-Ray VFB",
		default= False
	)

	# trace_depth
	RTEngine.trace_depth= IntProperty(
		name= "Trace depth",
		description= "Maximum trace depth for reflections/refractions etc",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 5
	)

	# use_gi
	RTEngine.use_gi= BoolProperty(
		name= "Use GI",
		description= "Use global illumination",
		default= True
	)

	# gi_depth
	RTEngine.gi_depth= IntProperty(
		name= "GI depth",
		description= "Maximum trace depth for GI",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 3
	)

	# gi_reflective_caustics
	RTEngine.gi_reflective_caustics= BoolProperty(
		name= "GI reflective caustics",
		description= "Reflective GI caustics",
		default= False
	)

	# gi_refractive_caustics
	RTEngine.gi_refractive_caustics= BoolProperty(
		name= "GI refractive caustics",
		description= "Refractive GI caustics",
		default= True
	)

	# bundle_size
	RTEngine.bundle_size= IntProperty(
		name= "Bundle size",
		description= "Number of samples to transfer over the network",
		min= 0,
		max= 1024,
		soft_min= 0,
		soft_max= 1024,
		default= 128
	)

	# samples_per_pixel
	RTEngine.samples_per_pixel= IntProperty(
		name= "Samples per pixel",
		description= "Number of samples per pixel",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 4
	)

	# coherent_tracing
	RTEngine.coherent_tracing= BoolProperty(
		name= "Coherent tracing",
		description= "Coherent tracing of gi/reflections/refractions etc",
		default= False
	)

	# use_opencl
	RTEngine.use_opencl = EnumProperty(
		name = "Device",
		description = "Computation Device",
		items = (
			('CPU',           "CPU",             ""),
			('CUDA_SINGLE',   "CUDA",            ""),
			('OPENCL_SINGLE', "OpenCL (Single)", ""),
			('OPENCL_MULTI',  "OpenCL (Multi)",  ""),
		),
		default = 'CPU'
	)

	# stereo_mode
	RTEngine.stereo_mode= EnumProperty(
		name= "Stereo mode",
		description= "Enable side-by-side stereo rendering",
		items= (
			('STEREO', "Side-by-side", "Side-by-side stereo rendering"),
			('NONE',   "None",   ""),
		),
		default= 'NONE'
	)

	# stereo_eye_distance
	RTEngine.stereo_eye_distance= FloatProperty(
		name= "Stereo eye distance",
		description= "Distance between the two cameras for stereo mode",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 6.5
	)

	# stereo_focus
	RTEngine.stereo_focus= EnumProperty(
		name= "Stereo focus",
		description= "Focus mode",
		items= (
			('SHEAR', "Shear",    ""),
			('ROT',   "Rotation", ""),
			('NONE',  "None",     ""),
		),
		default= 'NONE'
	)

	# opencl_texsize
	RTEngine.opencl_texsize= IntProperty(
		name= "Texture size",
		description= "OpenCL Single Kernel maximum texture size - bigger textures are scaled to fit this size",
		min= 0,
		max= 100000,
		soft_min= 0,
		soft_max= 2048,
		default= 512
	)

	# Command line options
	RTEngine.rtTimeOut = FloatProperty(
		name        = "Timeout",
		description = "Specifies a timeout in minutes for a frame (0.0 - no limit)",
		unit        = 'TIME',
		min         = 0.0,
		max         = 10000.0,
		soft_min    = 0.0,
		soft_max    = 10.0,
		precision   = 3,
		default     = 0.0
	)

	RTEngine.rtNoise = FloatProperty(
		name        = "Noise",
		description = "Specifies noise threshold for a frame",
		min         = 0.0,
		max         = 1.0,
		soft_min    = 0.0,
		soft_max    = 1.0,
		precision   = 4,
		default     = 0.001
	)

	RTEngine.rtSampleLevel = IntProperty(
		name        = "Sample Level",
		description = "Specifies maximum paths per pixel (0 - no limit)",
		min         = 0,
		default     = 0
	)



def write(bus):
	ofile = bus['files']['scene']
	scene = bus['scene']

	VRayScene = scene.vray
	RTEngine  = VRayScene.RTEngine

	STEREO_MODE = {
		'STEREO': 1,
		'NONE':   0,
	}

	STEREO_FOCUS = {
		'SHEAR': 2,
		'ROT':   1,
		'NONE':  0,
	}

	DEVICE = {
		'CPU'           : 0,
		'OPENCL_SINGLE' : 1,
		'OPENCL_MULTI'  : 2,
		'CUDA_SINGLE'   : 4,
	}

	if RTEngine.enabled:
		# XXX: When exporting this plugin termination params do not work!
		# Write all the params to support previous versions
		# ofile.write("\n%s %s {" % (ID, ID))
		# for param in PARAMS:
		# 	if param == 'stereo_mode':
		# 		value = STEREO_MODE[RTEngine.stereo_mode]
		# 	elif param == 'stereo_focus':
		# 		value = STEREO_FOCUS[RTEngine.stereo_focus]
		# 	elif param == 'use_opencl':
		# 		value = DEVICE[RTEngine.use_opencl]
		# 	else:
		# 		value = getattr(RTEngine, param)
		# 	ofile.write("\n\t%s=%s;"%(param, p(value)))
		# ofile.write("\n}\n")

		ofile.write("\nSettingsRTEngine settingsRT {")
		for param in PARAMS_SETTINGS_RT_ENGINE:
			if param == 'stereo_mode':
				value = STEREO_MODE[RTEngine.stereo_mode]
			elif param == 'stereo_focus':
				value = STEREO_FOCUS[RTEngine.stereo_focus]
			elif param == 'use_opencl':
				# We will set it in command line
				#value = DEVICE[RTEngine.use_opencl]
				continue
			else:
				value = getattr(RTEngine, param)
			ofile.write("\n\t%s=%s;"%(param, p(value)))
		ofile.write("\n}\n")


'''
  GUI
'''
class VRAY_RP_RTEngine(ui.VRayRenderPanel, bpy.types.Panel):
	bl_label       = "Realtime engine"
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		scene= context.scene
		rd=    scene.render
		if not hasattr(scene.vray, ID):
			return False
		use=   scene.vray.RTEngine.enabled
		return (use and ui.engine_poll(__class__, context))

	def draw(self, context):
		wide_ui= context.region.width > ui.narrowui
		layout= self.layout

		VRayScene= context.scene.vray

		RTEngine= getattr(VRayScene, ID)

		split= layout.split()
		col= split.column()
		col.prop(RTEngine, 'use_gi')
		if RTEngine.use_gi:
			col.prop(RTEngine, 'gi_depth', text="Depth")
			col.prop(RTEngine, 'gi_reflective_caustics', text="Reflective caustics")
			col.prop(RTEngine, 'gi_refractive_caustics', text="Refractive caustics")
		if wide_ui:
			col= split.column()
		col.prop(RTEngine, 'coherent_tracing')
		col.prop(RTEngine, 'trace_depth')
		col.prop(RTEngine, 'bundle_size')
		col.prop(RTEngine, 'samples_per_pixel')
		col.prop(RTEngine, 'opencl_texsize')

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(RTEngine, 'stereo_mode')
		if RTEngine.stereo_mode != 'NONE':
			split= layout.split()
			col= split.column()
			col.prop(RTEngine, 'stereo_focus', text="Focus")
			if wide_ui:
				col= split.column()
			col.prop(RTEngine, 'stereo_eye_distance', text="Eye distance")

		layout.separator()

		split = layout.split()
		col = split.column()
		col.prop(RTEngine, 'rtSampleLevel')
		split = layout.split()
		col = split.column()
		col.prop(RTEngine, 'rtNoise')
		if wide_ui:
			col= split.column()
		col.prop(RTEngine, 'rtTimeOut')

		layout.separator()
		layout.prop(RTEngine, 'use_opencl')


def GetRegClasses():
	return (
		VRAY_RP_RTEngine,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
