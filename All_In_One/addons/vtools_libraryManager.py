bl_info = {
	"name": "vtools - texture library manager",
	"author": "Antonio Mendozam,Bookyakuno  (2.8Update) ",
	"version": (0, 0, 3),
	"blender": (2, 80, 0),
	"location": "View3D > Property Shelf > Texture libraries panel (sculpt mode)",
	"warning": "",
	"description": "Load and unload image libraries",
	"category": "Learnbgame",
}


import bpy
import os
import sys
import time



from bpy.props import (StringProperty,BoolProperty,IntProperty,FloatProperty,FloatVectorProperty,EnumProperty,PointerProperty)
from bpy.types import (Menu, Panel,Operator,AddonPreferences, PropertyGroup)
from bpy_extras.io_utils import ImportHelper



#---- Definitions -----#

def findImage (p_Name):

	found = False

	for img in bpy.data.textures:
		if img.name == p_Name:
			found = True
			break

	return found

def selectImages (p_fileList):

	file_list = p_fileList
	img_list = [item for item in file_list if item[-3:] == 'png' or item[-3:] == 'jpg' or item[-4:] == 'jpeg' or item[-3:] == 'tga']
	#img_list = [item for item in file_list if item[-3:] == 'jpg' or item[-4:] == 'jpeg']
	return img_list

def image_batchImport(p_dir):


	if os.path.isdir(p_dir):
		file_list = sorted(os.listdir(p_dir))
		img_list = selectImages (file_list)

		imgLimits = 25
		cont = 0
		for img in img_list:
			dirImage = os.path.join(p_dir, img)
			tName = os.path.basename(os.path.splitext(img)[0])

			if findImage(tName) == False:
				nImage = bpy.data.images.load(dirImage)
				nT = bpy.data.textures.new(name=tName,type='IMAGE')
				bpy.data.textures[tName].image = nImage
				#cont += 1

			#if cont >= imgLimits:
			#	break


def image_batchRemove(p_dir):


	if os.path.isdir(p_dir):
		file_list = sorted(os.listdir(p_dir))
		img_list = selectImages (file_list)



		for img in img_list:
			dirImage = os.path.join(p_dir, img)
			tName = os.path.basename(os.path.splitext(img)[0])



			for tex in bpy.data.textures:
				if tex.name == tName:
					if tex.type == 'IMAGE':
						image = tex.image
						imgName = image.name
						tex.user_clear()
						bpy.data.textures.remove(tex)
						bpy.data.images[imgName].user_clear()
						bpy.data.images.remove(bpy.data.images[imgName])


def image_DeleteNonExisting(p_dir):

	if os.path.isdir(p_dir):
		for img in bpy.data.images:
			dirImage = os.path.join(p_dir, img.name)
			if not os.path.isfile(dirImage):
				tName = os.path.basename(os.path.splitext(img.name)[0])

				texID = bpy.data.textures.find(tName)
				if texID != -1:
					tex = bpy.data.textures[texID]
					if tex.type == 'IMAGE':
						image = tex.image
						tex.user_clear()
						bpy.data.textures.remove(tex)
						img.user_clear()
						bpy.data.images.remove(img)


def findUserSysPath():

	userPath = ''

def readLibraryDir():
		dir = ''
		fileDir = os.path.join(bpy.utils.resource_path('USER'), "scripts\\presets\\texture_library.conf")
		if os.path.isfile(fileDir):
			file = open(fileDir, 'r')
			dir = file.read()
			file.close()
		return dir


#-----------------------#



def deleteNonExistingLibraries():

	i = 0
	cont = 0
	while i < len(bpy.context.scene.textureLibrary):
		l = bpy.context.scene.textureLibrary[i]
		if not os.path.isdir(l.dirPath):
			removeLibrary(i)
			i = -1

		i += 1

def findSubLibraries(p_parentLibrary):
	existing = False
	dir = p_parentLibrary

	if os.path.isdir(dir):
		file_list = sorted(os.listdir(dir))
		for item in file_list:
			lib_dir = os.path.join(dir,item)
			if os.path.isdir(lib_dir):
				existing = False
				for l in bpy.context.scene.textureLibrary:
					if l.dirPath == lib_dir:
						existing = True

				if not existing:
					newLibrary = bpy.context.scene.textureLibrary.add()
					newLibrary.name = os.path.basename(os.path.normpath(lib_dir))
					newLibrary.dirPath = lib_dir
					newLibrary.loaded = False
					newLibrary.parent = p_parentLibrary

					sortLibrary(newLibrary, len(bpy.context.scene.textureLibrary)-1)



def loadLibrary(p_filePath):


	existing = False
	loaded = False
	deleteNonExistingLibraries()

	for l in bpy.context.scene.textureLibrary:
		if l.dirPath == p_filePath:
			existing = True

	if not existing:

		if os.path.isfile(p_filePath):
			fileName = os.path.basename(os.path.normpath(p_filePath))
			p_filePath = p_filePath.replace(fileName,"")


		if os.path.isdir(p_filePath):
			newLibrary = bpy.context.scene.textureLibrary.add()
			newLibrary.name = os.path.basename(os.path.normpath(p_filePath))
			newLibrary.dirPath = p_filePath
			newLibrary.loaded = False
			newLibrary.parent = "None"

			findSubLibraries(p_filePath)
			loaded = True

	return loaded

def removeLibrary(p_Id):

	idSelected = p_Id
	numItems = len(bpy.context.scene.textureLibrary)

	if numItems > 0 and idSelected != -1:
		library = bpy.context.scene.textureLibrary[idSelected]

		if library.parent == "None" :
			i = 0
			while i < len(bpy.context.scene.textureLibrary):
				l = bpy.context.scene.textureLibrary[i]
				if l.parent != "None" and l.parent == library.dirPath:
					bpy.context.scene.textureLibrary[i].loaded = False
					bpy.context.scene.textureLibrary.remove(i)
					i = 0

				i += 1


		if idSelected == (len(bpy.context.scene.textureLibrary)-1):
				bpy.context.scene.textureLibrary_ID_index = bpy.context.scene.textureLibrary_ID_index - 1

		bpy.context.scene.textureLibrary[idSelected].loaded = False
		bpy.context.scene.textureLibrary.remove(idSelected)


def sortLibrary(p_library, p_id):

	idCont = p_id
	if p_library.parent != "None":
		while idCont > 0:
			prevLib = bpy.context.scene.textureLibrary[idCont - 1]
			if prevLib.parent != p_library.parent and prevLib.dirPath != p_library.parent:
				bpy.context.scene.textureLibrary.move(idCont, idCont - 1)
				idCont = idCont - 1
				p_library = bpy.context.scene.textureLibrary[idCont]
			else:
				idCont = -100
				break




#-------- library collection operator ----------------------- #


class VTOOLS_OP_addLibrary(bpy.types.Operator, ImportHelper):
	bl_idname = "vtools.addlibrary"
	bl_label = "add new library"
	bl_description = "add a new library and every folder within it"

	def addLibrary(self, context, p_filePath):
		loaded = loadLibrary(p_filePath)
		if loaded == False:
			self.report({'WARNING', 'INFO'}, "No valid directory path. Keep filename slot empty")
		return {'FINISHED'}

	def execute(self,context):
		return self.addLibrary(context, self.filepath)

class VTOOLS_OP_removeLibrary(bpy.types.Operator):
	bl_idname = "vtools.removelibrary"
	bl_label = "remove library"
	bl_description = "remove the selected library from the list"

	def execute(self,context):

		removeLibrary(bpy.context.scene.textureLibrary_ID_index)
		return {'FINISHED'}



class VTOOLS_OP_cleanLibraries(bpy.types.Operator):
	bl_idname = "vtools.cleanlibraries"
	bl_label = "clean libraries"
	bl_description = "remove every library"

	def execute(self,context):


		while len(bpy.context.scene.textureLibrary) > 0:
			lib = bpy.context.scene.textureLibrary[0]

			if os.path.isdir(lib.dirPath):
				image_batchRemove(lib.dirPath)
			bpy.context.scene.textureLibrary.remove(0)

		return {'FINISHED'}


class VTOOLS_OP_refreshLibraries(bpy.types.Operator):

	bl_idname = "vtools.refreshlibraries"
	bl_label = "refresh libraries"
	bl_description = "refresh existing libraries"

	def execute(self,context):

		deleteNonExistingLibraries()
		for l in bpy.context.scene.textureLibrary:


			#reload images
			if l.loaded == True:
				image_DeleteNonExisting(l.dirPath)
				image_batchImport(l.dirPath)

			#reload folders
			if l.parent == "None":
				dir = l.dirPath
				findSubLibraries(dir)

		return {'FINISHED'}




#------------ CALLBACKS -------------#

def activeSelected(p_name):

	cont = 0
	for item in bpy.context.scene.textureLibrary:
		if item.name == p_name:
			bpy.context.scene.textureLibrary_ID_index = cont
			break

		cont += 1


def callback_loadLibrary(self, value):
	library = self

	if self.loaded:
		#load library

		image_batchImport(self.dirPath)
		if self.parent == "None":
			for l in bpy.context.scene.textureLibrary:
				if l.parent == self.dirPath:
					l.loaded = True

	else:
		#unload library
		if self.parent == "None":
			for l in bpy.context.scene.textureLibrary:
				if l.parent == self.dirPath:
					l.loaded = False


		image_batchRemove(self.dirPath)

	activeSelected(library.name)

#--------------------------------------#

#----------- UI libraries --------------------#

class VTOOLS_UIL_textureLibraryUI(bpy.types.UIList):

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

		row = layout.row(align = True)

		if item.parent == "None":

			if item.loaded == True:
				row.prop(item, "loaded", text="",emboss = False, icon='HIDE_OFF' )

			else:
				row.prop(item, "loaded", text="",emboss = False, icon='HIDE_ON')

			row.label(text="",icon="SHORTDISPLAY")
			row.label(item.name.upper())
		else:
			subLibraryName = " " + item.name
			row.scale_x = 0.5

			for i in range(0, 7):
				row.separator()


			if item.loaded == True:
				row.prop(item, "loaded", text="",emboss = False, icon='HIDE_OFF' )

			else:
				row.prop(item, "loaded", text="",emboss = False, icon='HIDE_ON')

			row.label(subLibraryName)

class VTOOLS_CC_textureLibrary(bpy.types.PropertyGroup):

	ID = IntProperty()
	name = StringProperty(default="")
	parent = StringProperty(default="None")
	loaded = BoolProperty(default=False, update=callback_loadLibrary)
	dirPath = StringProperty(default="")




#-------------------------------#


class LBM_PN_LibraryManager(bpy.types.Panel):
	bl_label = "Texture library"
	#bl_category = "LibraryManager"
	#bl_context = 'sculptmode'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Tools'
	bl_options = {'DEFAULT_CLOSED'}



	@classmethod
	def poll(cls, context):
		return (context.sculpt_object or context.vertex_paint_object or context.vertex_paint_object or context.image_paint_object)

	def draw(self,context):

		layout = self.layout
		row = layout.row()

		col = row.column()
		col.template_list('VTOOLS_UIL_textureLibraryUI', "ID", bpy.context.scene, "textureLibrary", bpy.context.scene, "textureLibrary_ID_index", rows=5, type='DEFAULT')

		col = row.column(align=True)
		col.operator(VTOOLS_OP_addLibrary.bl_idname, text = "", icon = "ADD")
		col.operator(VTOOLS_OP_removeLibrary.bl_idname, text = "", icon = "REMOVE")
		col.operator(VTOOLS_OP_refreshLibraries.bl_idname, text = "", icon = "FILE_REFRESH")
		col.operator(VTOOLS_OP_cleanLibraries.bl_idname, text = "", icon = "X")




classes = {
VTOOLS_OP_addLibrary,
VTOOLS_OP_removeLibrary,
VTOOLS_OP_cleanLibraries,
VTOOLS_OP_refreshLibraries,
VTOOLS_UIL_textureLibraryUI,
VTOOLS_CC_textureLibrary,
LBM_PN_LibraryManager,

}


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


	bpy.types.Scene.textureLibrary = bpy.props.CollectionProperty(type=VTOOLS_CC_textureLibrary)
	bpy.types.Scene.textureLibrary_ID_index = bpy.props.IntProperty()



def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

	del bpy.types.Scene.textureLibrary
	del bpy.types.Scene.textureLibrary_ID_index



if __name__ == "__main__":
	register()
