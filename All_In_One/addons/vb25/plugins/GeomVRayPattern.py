#
# V-Ray/Blender
#
# http://vray.cgdo.ru
#
# Author: Andrey M. Izrantsev (aka bdancer)
# E-Mail: izrantsev@cgdo.ru
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#

# Blender modules
import bpy
import mathutils

# V-Ray/Blender modules
import vb25


TYPE = 'OBJECT'
ID   = 'GeomVRayPattern'

NAME = 'VRayPattern'
DESC = "VRayPattern plugin settings"

PARAMS = (
	'use',
	'node_name',
	'base_name',
	'pattern_name',
	'render_pattern_object',
	'render_base_object',

	'geometry_bias',
	'crop_size',
	'height',
	'shift',
	'map_channel',
	'use_real_world',
	'tiling_u',
	'tiling_v',
	'polygon_id_from',
	'polygon_id_to',
	'random_segment_u',
	'random_segment_v',
	'random_segment_seed',
)


def add_properties(rna_pointer):
	class GeomVRayPattern(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(GeomVRayPattern)

	rna_pointer.GeomVRayPattern = bpy.props.PointerProperty(
		name        = ID,
		type        = GeomVRayPattern,
		description = DESC
	)

	GeomVRayPattern.use = bpy.props.BoolProperty(
		name        = "Use",
		description = "Override geometry with VRayPattern plugin",
		default     = False
	)

	GeomVRayPattern.pattern_object = bpy.props.StringProperty(
		name        = "Pattern Object",
		description = "Pattern object",
		default     = ""
	)

	GeomVRayPattern.render_pattern_object = bpy.props.BoolProperty(
		name        = "Render Pattern Object",
		description = "Render original pattern object",
		default     = False
	)

	GeomVRayPattern.render_base_object = bpy.props.BoolProperty(
		name        = "Render Base Object",
		description = "Render base object",
		default     = True
	)

	GeomVRayPattern.geometry_bias = bpy.props.FloatProperty(
		name        = "Geometry Bias",
		description = "Minimum passage distance of the ray after reflection from the geometry, within which all other ray intersections with the geometry are ignored. If this parameter is 0, the object will cast shadows on itself and will get covered with spots",
		min         = 0.0,
		max         = 1.0,
		soft_min    = 0.0,
		soft_max    = 0.1,
		precision   = 4,
		default     = 0.01
	)

	GeomVRayPattern.crop_size = bpy.props.FloatVectorProperty(
		name        = "Crop Size",
		description = "Size of the crop box of propagated geometry. All objects outside of the box – are ignored. Crop box also defines the repeating period of the geometry",
		subtype     = 'TRANSLATION',
		min         = 0.0,
		max         = 1024.0,
		soft_min    = 0.0,
		soft_max    = 10.0,
		precision   = 4,
		default     = (1.0, 1.0, 1.0)
	)

	GeomVRayPattern.height = bpy.props.FloatProperty(
		name        = "Height",
		description = "Height multiplier of the propagated geometry",
		subtype	    = 'PERCENTAGE',
		min         = 0.0,
		max         = 500.0,
		soft_min    = 0.0,
		soft_max    = 200.0,
		precision   = 4,
		default     = 100.0
	)

	GeomVRayPattern.shift = bpy.props.FloatProperty(
		name        = "Shift",
		description = "Displacement of the geometry against surface normal",
		min         = 0.0,
		max         = 1.0,
		soft_min    = 0.0,
		soft_max    = 0.1,
		precision   = 4,
		default     = 0.0
	)

	GeomVRayPattern.map_channel = bpy.props.IntProperty(
		name        = "Mapping Channel",
		description = "Mapping UV channel ID",
		min         = 0,
		max         = 1024,
		default     = 1
	)

	GeomVRayPattern.use_real_world = bpy.props.BoolProperty(
		name        = "Real World Scale",
		description = "Work in real world scale",
		default     = False
	)

	GeomVRayPattern.tiling_u = bpy.props.FloatProperty(
		name        = "Tiling U",
		description = "Mapping multiplier in U axis",
		min         = 0.001,
		soft_max    = 2.0,
		precision   = 4,
		default     = 1.0
	)

	GeomVRayPattern.tiling_v = bpy.props.FloatProperty(
		name        = "Tiling V",
		description = "Mapping multiplier in V axis",
		min         = 0.001,
		soft_max    = 2.0,
		precision   = 4,
		default     = 1.0
	)

	GeomVRayPattern.polygon_id_from = bpy.props.IntProperty(
		name        = "Polygon ID From",
		description = "Polygon ID low value",
		min         = 0,
		max         = 1024,
		default     = 1
	)

	GeomVRayPattern.polygon_id_to = bpy.props.IntProperty(
		name        = "Polygon ID From",
		description = "Polygon ID high value",
		min         = 0,
		max         = 1024,
		default     = 100
	)

	GeomVRayPattern.random_segment_u = bpy.props.IntProperty(
		name        = "Random Segment U",
		description = "Random segment count in U axis",
		min         = 0,
		max         = 1024,
		default     = 1
	)

	GeomVRayPattern.random_segment_v = bpy.props.IntProperty(
		name        = "Random Segment V",
		description = "Random segment count in V axis",
		min         = 0,
		max         = 1024,
		default     = 1
	)

	GeomVRayPattern.random_segment_seed = bpy.props.IntProperty(
		name        = "Seed",
		description = "Random seed",
		min         = 0,
		max         = 1024,
		default     = 42
	)


class VRAY_OT_pattern_fix(bpy.types.Operator):
	bl_idname      = 'vray.pattern_fit'
	bl_label       = "Fit Crop Size"
	bl_description = "Fit Crop Size"

	def execute(self, context):
		ob = context.object
		pattern_ob = None

		VRayObject = ob.vray
		GeomVRayPattern = VRayObject.GeomVRayPattern

		if GeomVRayPattern.pattern_object in context.scene.objects:
			pattern_ob = context.scene.objects[GeomVRayPattern.pattern_object]

		if pattern_ob is None:
			return {'FINISHED'}

		GeomVRayPattern.crop_size = pattern_ob.dimensions

		return {'FINISHED'}

bpy.utils.register_class(VRAY_OT_pattern_fix)


def write(bus):
	# Basically, any file that goes after 'nodes'. Improve this.
	#
	ofile = bus['files']['lights']

	scene = bus['scene']

	ob      = bus['node']['object']
	ob_name = bus['node']['name']
	me      = bus['node']['geometry']

	VRayScene    = scene.vray
	VRayExporter = VRayScene.exporter

	VRayObject = ob.vray
	GeomVRayPattern = VRayObject.GeomVRayPattern

	plug_name = "VRayPattern%s" % (ob_name)
	ofile.write("\nVRayPattern %s {" % (plug_name))
	for param in PARAMS:
		if param == 'node_name':
			value = '"%s"' % ('VRayPattern'+vb25.utils.get_name(ob, prefix='OB'))
		elif param == 'base_name':
			value = '"%s"' % (vb25.utils.get_name(ob, prefix='OB'))
		elif param == 'crop_size':
			crop_size = GeomVRayPattern.crop_size
			value = mathutils.Vector((crop_size.x, crop_size.z, crop_size.y))
		elif param == 'pattern_name':
			pattern_name = GeomVRayPattern.pattern_object
			if pattern_name in scene.objects:
				pattern_object = scene.objects[pattern_name]
				value = '"%s"' % (vb25.utils.get_name(pattern_object, prefix='OB'))
			else:
				value = '""'
		else:
			value = getattr(GeomVRayPattern, param)
		ofile.write("\n\t%s=%s;" % (param, vb25.utils.a(scene, value)))
	ofile.write("\n\tuse_base_map_channel=0;")
	ofile.write("\n}\n")

	return None
