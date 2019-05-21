# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
	"name": "Smooth Settings",
	"author": "Cenek Strichel",
	"version": (1, 0, 2),
	"blender": (2, 79, 0),
	"location": "Only hotkey",
	"description": "Smoothing with Angle toggle",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
import math
from bpy.props import FloatProperty


class SetSmooth(bpy.types.Operator):

	bl_idname = "view3d.set_smooth"
	bl_label = "Smooth"
	bl_options = {'REGISTER', 'UNDO'}
	
	angle = FloatProperty( name = "Angle", default = 120, min = 0, max = 180 )
	
	def execute(self, context):
		
		# Smooth #
	#	if( not bpy.context.object.data.use_auto_smooth ):
			
		bpy.ops.object.shade_smooth()
		
		objs = bpy.context.selected_objects
		
		for o in objs:
			o.data.use_auto_smooth = True
			o.data.auto_smooth_angle = math.radians(self.angle)
		
		bpy.ops.mesh.customdata_custom_splitnormals_clear() # needed for imported FBX
			
		# Flat #
		'''
		else:
			
			bpy.ops.object.shade_flat()
			
			objs = bpy.context.selected_objects
			for o in objs:
				o.data.use_auto_smooth = False
		'''
			
		return {'FINISHED'}



################################################################
# register #
############
def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	
if __name__ == "__main__":
	register()