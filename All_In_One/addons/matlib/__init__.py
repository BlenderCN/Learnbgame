# #####BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# #####END GPL LICENSE BLOCK #####

bl_info = {
	"name": "Material Library",
	"author": "Mackraken (mackraken2023@hotmail.com)",
	"version": (0, 5, 3),
	"blender": (2, 5, 8),
	"api": 37702,
	"location": "Properties > Material",
	"description": "Material Library VX",
	"warning": "",
	"wiki_url": "https://sites.google.com/site/aleonserra/home/scripts/matlib-vx",
	"tracker_url": "",
	"category": "Learnbgame",
}


import bpy, os, inspect
from xml.dom import minidom
from xml.dom.minidom import Document

#hey
#do not write a relative path for the material library
#it must be absolute

matlibpath = inspect.getfile(inspect.currentframe())[0:-len("__init__.py")] + "materials.blend"
catspath = inspect.getfile(inspect.currentframe())[0:-len("__init__.py")] + "categories.xml"

#i have to do this for windows, dont know if its going to work on mac or linux
matlibpath = matlibpath.replace("\\", "\\\\")
catspath = catspath.replace("\\", "\\\\")


#matlibpath = bpy.app.binary_path[0:-len("blender.exe")]+"materials.blend"
#catspath = bpy.app.binary_path[0:-len("blender.exe")]+"categories.xml"


class matlibPropGroup(bpy.types.PropertyGroup):
	category = bpy.props.StringProperty(name="Category")
	lastselected = None

bpy.utils.register_class(matlibPropGroup)

bpy.types.Scene.matlib_index = bpy.props.IntProperty(min = -1, default = -1)
bpy.types.Scene.matlib = bpy.props.CollectionProperty(type=matlibPropGroup)
#??? is this needed?
#bpy.props.matlib_link = bpy.props.BoolProperty(name = "matlib_link", default = False)


bpy.types.Scene.matlib_cats_index = bpy.props.IntProperty(min = -1, default = -1)
bpy.types.Scene.matlib_cats = bpy.props.CollectionProperty(type=matlibPropGroup)

def update_index(self, context):
	search = self.matlib_search
	for i, it in enumerate(self.matlib):
		if it.name==search:
			self.matlib_index = i
			break
	
#   matlibvxPanel.draw(matlibPanel, context)
	
bpy.types.Scene.matlib_search = bpy.props.StringProperty(name="matlib_search", update=update_index)

bpy.props.link = False
#bpy.props.relpath = False

#MaterialPropGroup.matname = bpy.props.StringProperty()
#bpy.types.Scene.matlib_search= bpy.props.StringProperty(name="search")
def createDoc(path):
	file = open(path, "w")
	doc = Document()
	wml = doc.createElement("data")
	doc.appendChild(wml)
	file.write(doc.toprettyxml(indent=" "))
	file.close()			
if os.path.exists(catspath)==False:
	createDoc(catspath)

def saveDoc(path, doc):
	file = open(path, "w")
	file.write(doc.toprettyxml(indent="  "))
	file.close()
	
	#clean xml (ugly way but it works)
	file = open(path)
	text = ""
	line = file.readline()
	
	while (line!=""):
		line = file.readline()
		if line.find("<")>-1:
			text+=line
	file.close()
	file = open(path, "w")
	file.write(text)
	file.close()

def deleteNode(c):
	parent = c.parentNode
	parent.removeChild(c)
	
def listmaterials(libpath):
	#print("listing")
	list = []
	with bpy.data.libraries.load(libpath) as (data_from, data_to):
		for mat in data_from.materials:
			list.append(mat)

	return list

def sendmat(name):
	print("-----------------------")
	
	nl = "\n"
	tab = " "
	#incluir en el script??
	list = listmaterials(matlibpath)
			
	add = True
	for it in list:
		if it == name:
			add = False
			break
		
	bpy.ops.wm.save_mainfile(check_existing=True)
	thispath = bpy.data.filepath
	thispath = thispath.replace("\\", "\\\\")
	
	if add:
		# Add material
		print("Add material "+name)
		#scriptpath = bpy.app.binary_path[0:-len("blender.exe")]+"sendmat.py"
		scriptpath = inspect.getfile(inspect.currentframe())[0:-len("__init__.py")] + "sendmat.py"

		print("sendmat: Doesnt exists sending material "+name)

		file = open(scriptpath, "w")
		file.write("import bpy"+nl)
		file.write('with bpy.data.libraries.load("'+thispath+'") as (data_from, data_to):'+nl)
		file.write(tab+'data_to.materials = ["'+name+'"]'+nl)
		file.write('mat = bpy.data.materials["'+name+'"]'+nl)
		file.write("mat.use_fake_user=True"+nl)
		file.write('bpy.ops.wm.save_mainfile(filepath="'+matlibpath+'", check_existing=False, compress=True)'+nl)
		file.close()
#		
		bin = bpy.app.binary_path
		com = bin +' "'+matlibpath+'" -b -P "'+scriptpath+'" '
		#print(com)
		os.system(com)
		
	else:
		# overwrite material
		#scriptpath = bpy.app.binary_path[0:-len("blender.exe")]+"overwmat.py"
		scriptpath = inspect.getfile(inspect.currentframe())[0:-len("__init__.py")] + "overwmat.py"
		
		print("sendmat: Exists, Overwriting "+name)
		
		file = open(scriptpath, "w")
		file.write("import bpy"+nl)
		file.write('mat = bpy.data.materials["'+name+'"]'+nl)
		file.write('mat.name = "tmp"'+nl)
		file.write('mat.user_clear()'+nl)
		file.write('with bpy.data.libraries.load("'+thispath+'") as (data_from, data_to):'+nl)
		file.write(tab+'data_to.materials = ["'+name+'"]'+nl)
		file.write('mat = bpy.data.materials["'+name+'"]'+nl)
		file.write("mat.use_fake_user=True"+nl)
		file.write('bpy.ops.wm.save_mainfile(filepath="'+matlibpath+'", check_existing=False, compress=True)'+nl)
		file.close()
		
		bin = bpy.app.binary_path
		com = bin +' "'+matlibpath+'" -b -P "'+scriptpath+'" '
		#print(com)
		os.system(com)
	
	return add
	

def getmat(name, link=False, rel=False):
	with bpy.data.libraries.load(matlibpath, link, rel) as (data_from, data_to):
		data_to.materials = [name]
		if link:
			print(name + " linked.")
		else:
			print(name + " appended.")
		
		#mat = bpy.data.materials[name]
		#mat.use_fake_user = False
	
	#return mat

def removemat(name):
	scriptpath = inspect.getfile(inspect.currentframe())[0:-len("__init__.py")] +"removemat.py" 
	
	thispath = bpy.data.filepath
	
	nl = "\n"
	tab = " "
	
	
	list = listmaterials(matlibpath)
	
	#check if it really exists 
	remove = False
	for it in list:
		print(it)
		if it == name:
			remove = True
			break
	
	if remove:
		
		print("removemat: Existe y me lo cargo "+name)
		
		file = open(scriptpath, "w")
		file.write("import bpy"+nl)
		file.write('mat = bpy.data.materials["'+name+'"]'+nl)
		file.write("mat.use_fake_user=False"+nl)
		file.write("mat.user_clear()"+nl)   
		file.write('bpy.ops.wm.save_mainfile(filepath="'+matlibpath+'", check_existing=False, compress=True)'+nl)
		file.close()
		
		bin = bpy.app.binary_path
		com = bin +' "'+matlibpath+'" -b -P "'+scriptpath+'" '
		#print(com)
		os.system(com)


### Categories Block	

def reloadcats(context):
	if os.path.exists(catspath)==False:
		createDoc(catspath)
	
		
	doc = minidom.parse(catspath)
	wml = doc.firstChild
	
	catstext = []
	for catnode in wml.childNodes:
		if catnode.nodeType!=3:
			catstext.append(catnode.attributes['name'].value)
			#print(node.nodeName)

	catstext.sort()
	catstext.insert(0, "All")
	
	scn = context.scene
	cats = scn.matlib_cats
	
	for it in cats:
		cats.remove(0)
	
	for it in catstext:
		item = cats.add()
		item.name = it
		
def reloadlib(context):
	#print("reloading library")
	
	matlib = context.scene.matlib
	matlib_cats = context.scene.matlib_cats
	list = listmaterials(matlibpath)
	reloadcats(context)
	
	index =context.scene.matlib_index
	
	context.scene.matlib_index = -1
	for it in matlib:
		matlib.remove(0)
	
	doc = minidom.parse(catspath)
	wml = doc.firstChild
	
	
	list.sort()
	print("--------------")
	for it in list:
		
		cat=""
		
		for xmlcat in wml.childNodes:
			if xmlcat.nodeType!=3:
				for xmlmat in xmlcat.childNodes:
					if xmlmat.nodeType!=3:
						#print(it, cat.nodeName, xmlcat.nodeName)
						matname = xmlmat.attributes['name'].value
						if matname==it:
							cat = xmlcat.attributes['name'].value
							#matcat = xmlcat.nodeName
							break
	
		item = matlib.add()
		item.name = it
		item.category = cat
	
	if len(list)>index:
		context.scene.matlib_index=index
		
	#reload categories
	
	return "Reloading libary"


class matlibDialogOperator(bpy.types.Operator):
	bl_idname = "matlib.cats_dialog"
	bl_label = "Add Category"

	#my_float = bpy.props.FloatProperty(name="Some Floating Point")
	#my_bool = bpy.props.BoolProperty(name="Toggle Option")
	my_string = bpy.props.StringProperty(name="Name")

	def execute(self, context):
		print(self.my_string)
		msg=""
		msgtype="ERROR"
		print("--------------------")
		tmpname = self.my_string
		
		#remove initial spaces
		
		for car in tmpname:
			if car==" ":
				tmpname=tmpname[1::]
			else:
				break
			
		#pretty cat
		name = tmpname.capitalize()
		#print(name)
		
		doc = minidom.parse(catspath)
		wml = doc.firstChild
		
		
		doname = 1
		for catnode in wml.childNodes:
			if catnode.nodeType!=3:
				catname = catnode.attributes['name'].value
				if catname == name:
					doname=0
					break

		if doname:
			node = doc.createElement("category")
			node.setAttribute("name", name)
			wml.appendChild(node)
			saveDoc(catspath, doc)
			reloadcats(context)
		else:
			print(name +" already exists")

		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

	
class matlibcatsAddRemoveOperator(bpy.types.Operator):
	'''Categories operators'''
	bl_idname = "matlib.cats_add_operator"
	bl_label = "Add/Remove Categories"
	
	add = bpy.props.StringProperty()
	
	
	@classmethod
	def poll(cls, context):
		return context.active_object != None

	def draw(self, context):
		print(self.add)
		
	def execute(self, context):
		add=self.add
		if add=="ADD":
			print("adding")
			bpy.ops.matlib.cats_dialog('INVOKE_DEFAULT')
		elif add=="REMOVE":
			print("removing")
			
			scn = context.scene
			cats = scn.matlib_cats
			index = scn.matlib_cats_index
			
			
			if index>0: #any than "All"
				
				name =cats[index].name
				
				doc = minidom.parse(catspath)
				wml = doc.firstChild
				
				for cat in wml.childNodes:
					if cat.nodeType!=3:
						catname=cat.attributes['name'].value
						if catname==name:
							deleteNode(cat)
							saveDoc(catspath, doc)
							scn.matlib_cats_index -=1
							cats.remove(index)
							break
					
			
		elif add == "SET":
			#set categories
			#mat = context.active_object.active_material
			scn = context.scene
			matlib = scn.matlib
			matindex = scn.matlib_index
			
			cats = scn.matlib_cats
			index = scn.matlib_cats_index
			
			if index>0:
				catname = cats[index].name
				matlib[matindex].category= catname
				matname = matlib[matindex].name
				
				#save xml
				doc = minidom.parse(catspath)
				wml = doc.firstChild
				
				for xmlcat in wml.childNodes:
					if xmlcat.nodeType!=3:
						xmlcatname=xmlcat.attributes['name'].value
						for xmlmat in xmlcat.childNodes:
							if xmlmat.nodeType!=3:
								xmlmatname = xmlmat.attributes['name'].value
								if xmlmatname==matname:
									deleteNode(xmlmat)
									
						if xmlcatname==catname:
							newmat=doc.createElement("material")
							newmat.setAttribute("name", matname)
							xmlcat.appendChild(newmat)
						
				saveDoc(catspath, doc)
	
		elif add == "FILTER":
			
			scn = context.scene
			
			cats = scn.matlib_cats
			index = scn.matlib_cats_index
			scn.matlib_search=""
			matlib = scn.matlib
			matindex = scn.matlib_index
			reloadlib(context)
				
			if index>0:
				#print("---------------------")			  
				scn.matlib_index=-1
				
				catname = cats[index].name
				items = []
				for i, it in enumerate(matlib):

					if it.category==catname:
						print(it.name)
						items.append([it.name, it.category])

				for it in matlib:
					matlib.remove(0)
					
				for it in items:
					item = matlib.add()
					item.name = it[0]
					item.category=it[1]
						
				#print("Show  "+ catname)
				
				
		return {'FINISHED'}

class matlibcatsSelectOperator(bpy.types.Operator):
	'''Categories'''
	bl_idname = "matlib.cats_select_operator"
	bl_label = "Select Category"

	name = bpy.props.StringProperty()
	add = bpy.props.IntProperty(default=-1, min=-1)
	@classmethod
	def poll(cls, context):
		return context.active_object != None

	def execute(self, context):
		
		scn = context.scene
		scn.matlib_cats_index=self.add
		
		cats = scn.matlib_cats
		catname = cats[self.add].name
		
#	   matlib = scn.matlib
		if self.add==0:
			reloadlib(context)
			
		print(self.add, catname)

			
		
		return {'FINISHED'}

class matlibcatsMenu(bpy.types.Menu):
	bl_idname = "matlib.cats_menu"
	bl_label = "Categories Menu"

	def draw(self, context):
		scn = context.scene
		
		layout = self.layout
		cats = scn.matlib_cats
		catindex = scn.matlib_cats_index
		for i, cat in enumerate(cats):
			layout.operator("matlib.cats_select_operator", text=cat.name).add=i
			
	
class matlibvxOperator(bpy.types.Operator):
	bl_label = "matlib operators"
	bl_idname = "matlib.add_remove_matlib"
	__doc__ = "Add, Remove, Reload, Apply, Preview, Clean Material"
	
	#add = bpy.props.BoolProperty(default = True)
	add = bpy.props.StringProperty()
	
	def invoke(self, context, event):
		add = self.add
		
		scn = context.scene

		mat = context.active_object.active_material  
		matlib = scn.matlib
		index = scn.matlib_index
		msg = ""
		msgtype = "INFO"
		
		#check files
		if os.path.exists(matlibpath)==False:
			add = -1
			msg = matlibpath+" doesnt exists!. Please create materials.blend at that path."
			msgtype="ERROR"
		
		if add=="ADD":
			### Add material
			print("Creating " + mat.name)
			
			send = sendmat(mat.name)
			if send:
				item = matlib.add()
				item.name = mat.name
				

		elif add=="REMOVE":
			### remove items
			
			if len(matlib)>0:
				print("Removing "+matlib[index].name)
				removemat(matlib[index].name)
				matlib.remove(index)
		
		elif add == "RELOAD":	
			### reload library
			msg = reloadlib(context)
			
		elif add=="APPLY":
			### apply material
			
			if len(matlib)>0 and index>-1:
				matl = matlib[index].name
				#print("---------------------")
				#print(matl)
				#no lo apliques al dummy
				if context.object.name=="Material_Preview" and bpy.types.matlibPropGroup.lastselected==None:
					msg = "Apply is disabled for Material Preview Object"
					
				else:
						
					
					#tengo que traerlo?
					#ver si esta linkado
					mat = None
					#search into current libraries 
					for lib in bpy.data.libraries:
						if bpy.path.abspath(lib.filepath) == matlibpath:
							for id in lib.users_id:
								if id.bl_rna.identifier=="Material" and id.name==matl:
									#print(id)
									mat = id
									break
				
					if mat==None:
						#print(matl+" no linkado")
						#trae y aplica el material
									
						nmats = len(bpy.data.materials)
						getmat(matl)
						
						#print(nmats,len(bpy.data.materials))
						
						if nmats == len(bpy.data.materials):
							#print("El material no esta en la db")
							msg = matl+" doesnt exists at Library."
							msgtype="ERROR"
								
						else:
							#y si coje de otra libreria?
							#arreglado porque pilla el ultimo material creado
							#que no este linkado
							for mat in reversed(bpy.data.materials):
								if mat.library==None and mat.name[0:len(matl)]==matl:
									break
							
							
							#print("importado correctamente ", mat, mat.use_fake_user)	
							
							#aplica el material al objeto
							
							
							obj = bpy.context.object
							
							if obj.name=="Material_Preview":
								
								obj = bpy.types.matlibPropGroup.lastselected
								scn.objects.active = obj
								#bpy.types.matlibPropGroup.lastselected=None
								obj.select=True
							matindex = obj.active_material_index
							mat.use_fake_user=False #this line has to be duplicated
							obj.material_slots[matindex].material=None	
							
							obj.material_slots[matindex].material = mat
							
							mat.use_fake_user=False
							
							bpy.ops.object.make_single_user(type='SELECTED_OBJECTS',
													object=False,
													obdata=False,
													material=True,
													texture=True,
													animation=False)
													
							print("importado correctamente ", mat, mat.use_fake_user)
					else:
						#print(matl+" esta linkado")
					
						
						#aplica el material al objeto
						obj = bpy.context.object
						#print("aplicando a", obj)
						if obj.name=="Material_Preview":
							obj.select = False
							
							obj = bpy.types.matlibPropGroup.lastselected
							scn.objects.active = obj
							obj.select=True
							
						matindex = obj.active_material_index
						mat.use_fake_user=False #this line has to be duplicated
						obj.material_slots[matindex].material=None	
						
						obj.material_slots[matindex].material = mat
						
						mat.use_fake_user=False
						
						#quitar el link
						bpy.ops.object.make_local(type="SELECTED_OBJECTS_DATA")
					
	
						
						
						#print("importado correctamente ", mat, mat.use_fake_user)
					
		
		elif add == "PREVIEW":
			### preview material
			if len(matlib)>0 and index>-1:
				matl = matlib[index].name
				print("------------------")
				print("preview material " +matl)
				
				unlinked = True
				#identificar si ya esta linkado
				for mat in bpy.data.materials:
					if mat.name==matl and mat.library!=None and bpy.path.abspath(mat.library.filepath)==matlibpath:
						unlinked=False
						print("si esta linkado")
						break
	
				dopreview = True
	
				if unlinked:
					print("no esta linkado")
					#check if it exists at lib
					list = listmaterials(matlibpath)
			
					exists = False
					for it in list:
						if it == matl:
							exists= True
							break
	
					if exists:
						print("existe en lib")	  
						#link the material
						getmat(matl, True)
						
						for mat in bpy.data.materials:
							if mat.library!=None and bpy.path.abspath(mat.library.filepath)==matlibpath and mat.name==matl:
								break
							
						#add a matlib_remover
					else:
						dopreview=False
						msg = matl +" does'nt exists at library."
						msgtype = "ERROR"
					
				if dopreview:
					#create/get preview object
					try:
						obj = bpy.data.objects['Material_Preview']
					except:
						try:
							me = bpy.data.meshes['Material_Preview_Mesh']
						except:
							me = bpy.data.meshes.new('Material_Preview_Mesh')
						obj = bpy.data.objects.new('Material_Preview', me)
						scn.objects.link(obj)
						
					obj.hide_render = True
					#obj.hide = True
					mat.use_fake_user=False
					
					if len(obj.material_slots)==0:
						obj.data.materials.append(mat)
					else:
						print("previewing "+ mat.name)
						obj.material_slots[0].material = mat
						obj.active_material_index = 0
					
					if scn.objects.active!=obj:
						bpy.types.matlibPropGroup.lastselected = scn.objects.active 
					#cuidado con el context
					obj.select = True
					context.object.select = False
					
					scn.objects.active = obj
	
		elif add == "CLEAN":
			#remove preview material
			try:
				obj = context.scene.objects['Material_Preview']
			except:
				obj=None
			
			if scn.objects.active==obj!=None:
				if bpy.types.matlibPropGroup.lastselected!=None:	
					scn.objects.active = bpy.types.matlibPropGroup.lastselected
					scn.objects.active.select = True
					obj.select = False
			
			if obj:
				
				for i, mat in enumerate(obj.data.materials):
					if mat!=None: mat.use_fake_user=False
					obj.material_slots[i].material=None
				
			### clean unusued materials and textures
			#links should be remove
			for mat in bpy.data.materials:
				mat.use_fake_user=False
				if mat.users==0:
					bpy.data.materials.remove(mat)
			
			for tex in bpy.data.textures:
				tex.use_fake_user=False
				if tex.users==0:
					if tex.type=="IMAGE":
						tex.image=None
					if tex.type=="ENVIRONMENT_MAP" and tex.environment_map.source=="IMAGE_FILE":
						tex.image=None
						
					bpy.data.textures.remove(tex)

			for img in bpy.data.images:
				img.use_fake_user=False
				if img.users==0:
					bpy.data.images.remove(img)		
			
		if msg!="":
			self.report(msgtype, msg)
				
		return {'FINISHED'}


			
class matlibvxPanel(bpy.types.Panel):
	bl_label = "Material Library VX"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "material"

	@classmethod
	def poll(self, context):
		return context.active_object.active_material!=None

	def draw(self, context):
		layout = self.layout

		scn = context.scene

		row = layout.row(align=True)
		#row.alignment="LEFT"
		row.prop_search(scn, "matlib_search", scn, "matlib", text="", icon="VIEWZOOM")
		
		entry = ""
		nmats = len(scn.matlib)
		index = scn.matlib_index
		if nmats >0:
			
			if index<nmats:
				entry = scn.matlib[scn.matlib_index].category
		row.alignment="LEFT"
		row.label(entry)
		row = layout.row()
		row.template_list(scn, "matlib", scn, "matlib_index")
		col = row.column(align=True)
		
		col.operator("matlib.add_remove_matlib", icon="ZOOMIN", text="").add = "ADD"
		col.operator("matlib.add_remove_matlib", icon="ZOOMOUT", text="").add = "REMOVE"
		col.operator("matlib.add_remove_matlib", icon="FILE_REFRESH", text="").add = "RELOAD"
		col.operator("matlib.add_remove_matlib", icon="MATERIAL", text="").add = "APPLY"
		col.operator("matlib.add_remove_matlib", icon="COLOR", text="").add = "PREVIEW"
		col.operator("matlib.add_remove_matlib", icon="GHOST_DISABLED", text="").add = "CLEAN"
		row = layout.row(align=True)
		
		cats = scn.matlib_cats
		catindex = scn.matlib_cats_index
		if catindex==-1 or len(cats)<=1:
			name="Categories"
			#scn.matlib_cats_index=-1
		else:
			name = cats[catindex].name
			
		row.menu("matlib.cats_menu",text=name)
		row.operator("matlib.cats_add_operator", icon="FILTER", text="").add="FILTER"
		row.operator("matlib.cats_add_operator", icon="FILE_PARENT", text="").add="SET"
		
		row.operator("matlib.cats_add_operator", icon="ZOOMIN", text="").add="ADD"
		row.operator("matlib.cats_add_operator", icon="ZOOMOUT", text="").add="REMOVE"
		


classes = [matlibcatsMenu, matlibcatsAddRemoveOperator, 
			matlibcatsSelectOperator, matlibDialogOperator,		 
			matlibvxOperator, matlibvxPanel]
	
def register():
	for c in classes:
		bpy.utils.register_class(c)


def unregister():
	for c in classes:
		bpy.utils.unregister_class(c)


if __name__ == "__main__":
	register()