# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
	"name": "Export Material to .VMT",
	"category": "Learnbgame",
	"author": "lucasvinbr (lucasvinbr@gmail.com)",
	"version": "0.1",
	"location": "Material Properties > Export Material to VMT",
	"description": "Uses a VMT blueprint and replaces its contents to create a new one",
}

import bpy

from bpy.props import (IntProperty,
					   BoolProperty,
					   StringProperty,
					   CollectionProperty,
					   PointerProperty,
					   EnumProperty)

from bpy.types import (Operator,
					   Panel,
					   Menu,
					   PropertyGroup,
					   Scene,
					   UIList)
					   

from bpy_extras.io_utils import ExportHelper

def writeToFile(context, filepath, writeData):
	f = open(filepath, 'w', encoding='utf-8')
	f.write(writeData)
	f.close()

	return {'FINISHED'}
	
def prepareVMTContents(curScene):
	if curScene.baseVMTReferenceFile is None:
		print("VMT content preparation failed: No Blueprint file specified!")
		return ""
	else:
		newFileContents = curScene.baseVMTReferenceFile.as_string()
		if len(curScene.VMTreplacerList) > 0 and curScene.VMTwildcardString.count("") > 0:
			replacerIndex = 0
			for i in range(newFileContents.count(curScene.VMTwildcardString)):
				newFileContents = newFileContents.replace(curScene.VMTwildcardString, curScene.VMTreplacerList[replacerIndex].repl_content, 1)
				replacerIndex += 1
				if replacerIndex >= len(curScene.VMTreplacerList):
					replacerIndex = 0
		return newFileContents
	


class VmtWritePreviewText(Operator):
	"""Clears the Preview text file's contents and then writes the same content that would be written in the final VMT file in it"""
	bl_idname = "material.vmt_preview_operator"
	bl_label = "Write Preview VMT"
	
	def execute(self, context):

		curScene = context.scene
		if curScene.baseVMTReferenceFile is None:
			self.report({"ERROR_INVALID_INPUT"},"Blueprint file not specified")
		elif curScene.previewVMTReferenceFile is None:
			self.report({"ERROR_INVALID_INPUT"},"Preview file not specified")
		else:
			newFileContents = prepareVMTContents(curScene)
			
			curScene.previewVMTReferenceFile.clear()
			curScene.previewVMTReferenceFile.write(newFileContents)
		
		
		return {'FINISHED'}



class VmtExportOp(Operator, ExportHelper):
	"""Opens the export menu for the VMT file"""
	bl_idname = "material.vmt_exportmat_operator"
	bl_label = "Export Replaced Text as VMT"

	# ExportHelper mixin class uses this
	filename_ext = ".vmt"
	
	filename = StringProperty(
			name="File Name",
			description="Name used by the exported file",
			maxlen=255,
			subtype='FILE_NAME',
			)

	def execute(self, context):
		return writeToFile(context, self.filepath, prepareVMTContents(context.scene))
		
	def invoke(self, context, event):
		import os
		if not self.filepath:
			blend_filepath = context.blend_data.filepath
			if not blend_filepath:
				blend_filepath = "untitled"
			else:
				blend_filepath = os.path.splitext(blend_filepath)[0]
				self.filepath = os.path.join(os.path.dirname(blend_filepath), self.filename + self.filename_ext)
		else:
			self.filepath = os.path.join(os.path.dirname(self.filepath), self.filename + self.filename_ext)
		

		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}




class VmtMatExportPanel(bpy.types.Panel):
	"""Creates a Panel in the Material properties window"""
	bl_label = "Text Replacement for VMT"
	bl_idname = "MATERIAL_PT_vmtexport"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "material"
	
	
	@classmethod
	def poll(self, context):
		return context.active_object.active_material!=None

	def draw(self, context):
		layout = self.layout
		mat = context.material
		self.pickedText = None
		
		row = layout.row()
		row.label(text="Resulting VMT name: " + mat.name + ".vmt")
		
		curScene = context.scene
		
		row = layout.row().split(0.33)
		row.label(text="VMT blueprint file")
		row.template_ID(curScene, "baseVMTReferenceFile", new="text.new", unlink="text.unlink", open="text.open")

		layout.separator()
		
		row = layout.row()
		row.prop(curScene, "VMTwildcardString")
		
		row = layout.row()
		row.label(text="Replacer Entries List:")
		
		row = layout.row()
		row.template_list("VmtReplacerListItems", "", curScene, "VMTreplacerList", curScene, "VMTreplacerListIndex", rows=2)

		col = row.column(align=True)
		col.operator("vmtMatExp.list_action", icon='ZOOMIN', text="").action = 'ADD'
		col.operator("vmtMatExp.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
		col.separator()
		col.operator("vmtMatExp.list_action", icon='TRIA_UP', text="").action = 'UP'
		col.operator("vmtMatExp.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
		
		layout.separator()
		
		row = layout.row().split(0.33)
		row.label(text="VMT preview file")
		row.template_ID(curScene, "previewVMTReferenceFile", new="text.new", unlink="text.unlink", open="text.open")
		
		layout.separator()
		
		row = layout.row()
		row.operator(VmtWritePreviewText.bl_idname, "Preview VMT Contents (Will Overwrite Preview File!)")
		
		layout.separator()
		
		row = layout.row()
		row.operator(VmtExportOp.bl_idname, VmtExportOp.bl_label).filename = mat.name

#---------------------
#REPLACERS LIST STUFF
#---------------------
#most of it found in: https://gist.github.com/p2or/d6dfd47366b2f14816f57d2067dcb6a9
#--------

class VmtReplacerStringsColl(PropertyGroup):
	repl_content = StringProperty(name="Content", description="The content that will be written over the replacement marker string in the preview file, following the order of replacers (the ones that come before this one will replace earlier occurrences)")
	repl_id = IntProperty()

class VmtReplacerListItems(UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		split = layout.split(0.2)
		split.label("Order: %d" % (index + 1))
		split.prop(item, "repl_content")

	def invoke(self, context, event):
		pass   

class VmtReplacerListOps(Operator):
	"""Move items up and down, add and remove"""
	bl_idname = "vmtmatexp.list_action"
	bl_label = "Replacer List Actions"
	bl_description = "Move items up and down, add and remove"
	bl_options = {'REGISTER'}

	action = bpy.props.EnumProperty(
		items=(
			('UP', "Up", ""),
			('DOWN', "Down", ""),
			('REMOVE', "Remove", ""),
			('ADD', "Add", "")))

	def invoke(self, context, event):
		curScene = context.scene
		idx = curScene.VMTreplacerListIndex

		try:
			item = curScene.VMTreplacerList[idx]
		except IndexError:
			pass
		else:
			if self.action == 'DOWN' and idx < len(curScene.VMTreplacerList) - 1:
				item_next = curScene.VMTreplacerList[idx+1].name
				curScene.VMTreplacerList.move(idx, idx+1)
				curScene.VMTreplacerListIndex += 1
				

			elif self.action == 'UP' and idx >= 1:
				item_prev = curScene.VMTreplacerList[idx-1].name
				curScene.VMTreplacerList.move(idx, idx-1)
				curScene.VMTreplacerListIndex -= 1
				

			elif self.action == 'REMOVE':
				curScene.VMTreplacerListIndex -= 1
				curScene.VMTreplacerList.remove(idx)

		if self.action == 'ADD':
			item = curScene.VMTreplacerList.add()
			item.repl_id = len(curScene.VMTreplacerList)
			curScene.VMTreplacerListIndex = len(curScene.VMTreplacerList)-1


		return {"FINISHED"}



#--------------
#REGISTER\UNREGISTER
#--------------

classes = (
	VmtWritePreviewText,
	VmtExportOp,
	VmtReplacerListItems,
	VmtReplacerListOps,
	VmtReplacerStringsColl,
	VmtMatExportPanel
)

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)
		
	
	Scene.baseVMTReferenceFile = PointerProperty(type=bpy.types.Text, name="baseVMTReferenceFile", description="File used as blueprint for VMT export")
	Scene.previewVMTReferenceFile = PointerProperty(type=bpy.types.Text, name="previewVMTReferenceFile", description="File used as preview for VMT export")
	
	Scene.VMTwildcardString = StringProperty(name="Replacement Marker String", description="Each occurrence of this string in the blueprint file will be replaced by one of the specified replacer entries in the preview\\destination file. If there are less replacers than replacement markers, the replacers will be looped over (0,1,2,0,1 for example)", maxlen=255)
	
	Scene.VMTreplacerList = CollectionProperty(type=VmtReplacerStringsColl)
	Scene.VMTreplacerListIndex = IntProperty()


def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):
		unregister_class(cls)
		
	del Scene.previewVMTReferenceFile
	del Scene.baseVMTReferenceFile
	del Scene.VMTwildcardString
	del Scene.VMTreplacerList
	del Scene.VMTreplacerListIndex

if __name__ == "__main__":
	register()
