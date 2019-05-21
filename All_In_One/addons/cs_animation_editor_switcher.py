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
	"name": "Animation Editor Switcher",
	"author": "Cenek Strichel",
	"version": (1, 0, 0),
	"blender": (2, 79, 0),
	"location": "Animation Editor's headbar",
	"description": "Fast switch for Animation Editors",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}
	
	
import bpy
from bpy.types import Header, Panel
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import AddonPreferences, Operator
        	

###################################	
# Animation Header #
###################################
def AnimEditor_Switcher(self, context):
	

	user_preferences = context.user_preferences
	addon_prefs = user_preferences.addons[__name__].preferences

	layout = self.layout
	
	# Filter by editor #
	if( not addon_prefs.boolTimeline and context.area.type == "TIMELINE" ):
		return {'FINISHED'}
	
	if( not (addon_prefs.boolGraph or addon_prefs.boolDrivers) and context.area.type == "GRAPH_EDITOR" ):
		return {'FINISHED'}
	
	if( not (addon_prefs.boolDopesheet or addon_prefs.boolAction) and context.area.type == "DOPESHEET_EDITOR" ):
		return {'FINISHED'}
	
	if( not addon_prefs.boolNLA and context.area.type == "NLA_EDITOR" ):
		return {'FINISHED'}
	
	
	# TIMELINE #
	if( addon_prefs.boolTimeline ):

		row = layout.row(align=True)
		row.operator("scene.animation_editor_switcher", text = "", icon = "TIME").editorType = "TIMELINE"
	
	
	# GRAPH #
	if( addon_prefs.boolGraph or addon_prefs.boolDrivers ):
		
		row = layout.row(align=True)
		
		if( addon_prefs.boolGraph ):
			row.operator("scene.animation_editor_switcher", text = "", icon = "IPO").editorType = "GRAPH_EDITOR"
			
		if( addon_prefs.boolDrivers ):
			row.operator("scene.animation_editor_switcher", text = "", icon = "DRIVER").editorType = "GRAPH_EDITOR_DRIVERS"
		
		
	# DOPE #	
	if( addon_prefs.boolDopesheet or addon_prefs.boolAction ):
		
		row = layout.row(align=True)
		
		if( addon_prefs.boolDopesheet ):	
			row.operator("scene.animation_editor_switcher", text = "", icon = "OOPS").editorType = "DOPESHEET_EDITOR"
			
		if( addon_prefs.boolAction ):	
			row.operator("scene.animation_editor_switcher", text = "", icon = "OBJECT_DATAMODE").editorType = "DOPESHEET_EDITOR_ACTION"
		
		
	# NLA #	
	if( addon_prefs.boolNLA ):
		
		row = layout.row(align=True)
		row.operator("scene.animation_editor_switcher", text = "", icon = "NLA").editorType = "NLA_EDITOR"
	
	
class AnimationEditorSwitcher(bpy.types.Operator):

	'''Switch Animation Editor'''
	bl_idname = "scene.animation_editor_switcher"
	bl_label = "Switch Editor"
	
	editorType = StringProperty( name = "EditorType", description = "" )
	
	def execute(self, context):
		
		if(self.editorType == "DOPESHEET_EDITOR"):
			bpy.context.area.type = "DOPESHEET_EDITOR"
			bpy.context.space_data.mode = 'DOPESHEET'
			
		elif(self.editorType == "DOPESHEET_EDITOR_ACTION"):
			bpy.context.area.type = "DOPESHEET_EDITOR"
			bpy.context.space_data.mode = 'ACTION'
			
		elif(self.editorType == "GRAPH_EDITOR"):
			bpy.context.area.type = "GRAPH_EDITOR"
			bpy.context.space_data.mode = 'FCURVES'
			
		elif(self.editorType == "GRAPH_EDITOR_DRIVERS"):
			bpy.context.area.type = "GRAPH_EDITOR"
			bpy.context.space_data.mode = 'DRIVERS'	
			
		else:
			bpy.context.area.type = self.editorType
			
		return {'FINISHED'}
	
	
class AnimEditSwitcherAddonPreferences(AddonPreferences):

	bl_idname = __name__

	boolTimeline = BoolProperty( name="Timeline",default=False )
	boolGraph = BoolProperty( name="Graph Editor",default=True )
	boolDrivers = BoolProperty( name="Drivers Editor",default=False )
	boolDopesheet= BoolProperty( name="Dopesheet",default=True )
	boolAction= BoolProperty( name="Action Editor",default=True )
	boolNLA= BoolProperty( name="NLA",default=True )
	
	def draw(self, context):
	
		layout = self.layout
		layout.prop(self, "boolTimeline")
		layout.prop(self, "boolGraph")
		layout.prop(self, "boolDrivers")
		layout.prop(self, "boolDopesheet")
		layout.prop(self, "boolAction")
		layout.prop(self, "boolNLA")

	
################################################################
# register #

def register():
	bpy.utils.register_module(__name__)
	
	bpy.types.TIME_HT_header.prepend(AnimEditor_Switcher)
	bpy.types.GRAPH_HT_header.prepend(AnimEditor_Switcher)
	bpy.types.DOPESHEET_HT_header.prepend(AnimEditor_Switcher)
	bpy.types.NLA_HT_header.prepend(AnimEditor_Switcher)
	
	
def unregister():
	bpy.utils.unregister_module(__name__)
	
	bpy.types.TIME_HT_header(AnimEditor_Switcher)
	bpy.types.GRAPH_HT_header(AnimEditor_Switcher)
	bpy.types.DOPESHEET_HT_header(AnimEditor_Switcher)
	bpy.types.NLA_HT_header(AnimEditor_Switcher)
	
	
if __name__ == "__main__":
	register()