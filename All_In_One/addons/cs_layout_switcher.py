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
	"name": "Layout Switcher",
	"author": "Cenek Strichel",
	"version": (1, 0, 3),
	"blender": (2, 79, 0),
	"location": "Info header",
	"description": "Switch layout with buttons on Info header",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
from bpy.props import StringProperty
from bpy.types import Header, Panel

import platform


#################
# AUTO IK CHAIN #
#################

class SwitchLatout(bpy.types.Operator):

	'''Change layout'''
	bl_idname = "screen.switch_layout"
	bl_label = "Change layout"
	
	layoutName = StringProperty(name="Layout Name")
	
	
	def execute(self, context):
		
		try:
			bpy.context.window.screen = bpy.data.screens[ self.layoutName ]
			
		except:
		#	bpy.ops.screen.new() # duplicate current
			
			bpy.context.window.screen.name = self.layoutName
		#	bpy.context.window.screen = bpy.data.screens[ self.layoutName ]
			
			# rename old
			'''
			for s in bpy.data.screens:
				bpy.context.window.screen.name = s.name.replace(".001","")
				bpy.context.window.screen.name = s.name.replace(".002","")
				bpy.context.window.screen.name = s.name.replace(".003","")
				bpy.context.window.screen.name = s.name.replace(".004","")
			'''	
			self.report({'WARNING'}, "Current layout was renamed!")
			
		return {'FINISHED'}


def switchLayout(self, context):
	
	layout = self.layout
	row = layout.row(align=True)
	
	totalWidth = 0
	
	for area in bpy.context.screen.areas: # iterate through areas in current screen
		totalWidth = totalWidth + area.width
		
	prefix = ""
	
	# my home station (1 big monitor)
	if "[M1]" in str(bpy.context.window.screen.name):
		prefix = "[M1] "
		
	elif "[M2]" in str(bpy.context.window.screen.name):
		prefix = "[M2] "
		
	elif "[M3]" in str(bpy.context.window.screen.name):
		prefix = "[M3] "
		
	row = layout.row(align=True)
		
	row.operator(SwitchLatout.bl_idname, text = "Generic", icon = "VIEW3D").layoutName = (prefix + "1 Generic")
	row.operator(SwitchLatout.bl_idname, text = "Animation", icon = "IPO").layoutName = (prefix + "2 Animation")
	row.operator(SwitchLatout.bl_idname, text = "Composition", icon = "NODETREE").layoutName = (prefix + "3 Composition")
	row.operator(SwitchLatout.bl_idname, text = "", icon = "TEXT").layoutName = (prefix + "4 Scripting")


################################################################
# register 

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_HT_header.prepend(switchLayout)

	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_HT_header(switchLayout)
	
if __name__ == "__main__":
	register()