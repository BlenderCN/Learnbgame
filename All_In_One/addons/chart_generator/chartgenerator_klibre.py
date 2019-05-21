																	 
																	 
																	 
											 
# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	"name": "Chart Graphics Generator",
	"author": "klibre, PKHG, thanks to JesterKing, Oscurart, Carlos Guerrero",
	"version": (0,0,4),
	"blender": (2, 5, 9),
	"api": 40101,
	"category": "Add Curve",
	"location": "View3d > Tools",
	"description": "Tool to build bar graphics from csv databases,",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "http://blenderpython.svn.sourceforge.net/viewvc/blenderpython/259/scripts/addons_extern/chart_generator/",}


#----------------------------------------------------

import bpy
import csv
from math import pi
import mathutils
import random
import sys

#-------------------globals---------------------------------
pid2 = pi * 0.5
sce = bpy.context.scene
obj = bpy.context.object
bc = bpy.context
boo = bpy.ops.object
bot = bpy.ops.transform
suma = 0
chartType = '' #not yet used
negativValueSeen = False
sizesCVSfile = None
colnrPKHG = '-1'
factorescala = 5
cvs_colums = 0
allData = None
sce.frame_start = 0
#sce.frame_end = 500
time = 20
origin = bc.scene.cursor_location

#-------------------end globals---------------------------------

def interuptMe(where,debug = True):
	if debug:
		print(where);
		__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

def getCSV(path):
	global sizesCVSfile, cvs_colums  
	result = False
	try:
		csvfile =  open(path, 'r')
		dialect = csv.Sniffer().sniff(csvfile.read(1024))
		csvfile.seek(0)
#   reader = csv.DictReader(csvfile, dialect=dialect) #no not needed
		reader = csv.reader(csvfile, dialect=dialect)
		csvData = []
		for data in reader:
			csvData.append(data)
		result = csvData
		cvs_rows = len(result)
		cvs_colums = len(result[0])
		sizesCVSfile = [cvs_colums, cvs_rows]
		csvfile.close()
	except:
		print("no good csv file adress given!")
		self.report({'INFO'}, "no good csv file adress given!")
	return result
#
#
#def finalfps():
#   if bpy.ops.screen.keyframe_jump(next=True) == true :
#   
#   bpy.ops.screen.keyframe_jump(next=True)
#   
#   else :
#   
#   return {"FINISHED"}

class ImportadorUI(bpy.types.Panel):
	bl_label = "Generador de Graficas"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'

	def draw(self, context):
		global colnrPKHG, allData, cvs_colums, time
		layout = self.layout		
		col = layout.column(align=1)
		row = layout.row()
		split=row.split()
		col.label("Path of the CSV file:")
		row.operator("lee.ruta",icon="FILE_SCRIPT")
		col = split.column()				
		col.prop(bc.scene,"importPydataPath")
		row = layout.row()
		row.prop(bc.scene,"useColumnNr")
		colnrPKHG = bc.scene.useColumnNr
		path = bc.scene.importPydataPath
		check = getCSV(path)
		
		if colnrPKHG >= cvs_colums:
			print("column ", colnrPKHG," not possible")
		elif check:
			allData = check
			row=layout.row()
			split=row.split()
			colL0 = split.column()
			colL0.label("Graphic Type:")
			row = layout.row()
			row.prop(bc.scene,"scaleFactor")
			factorescala = bc.scene.scaleFactor
			row=layout.row()
			split=row.split()
			colL1 = split.column()  
			colL1.operator("importador.cubos", icon="MESH_CUBE")
			colR1 = split.column()
			colR1.operator("importador.cilindros", icon="MESH_CYLINDER")
			colL3 = split.column()
			colL3.operator("fabricar.quesito", icon="MESH_CIRCLE")
			row=layout.row()
			split=row.split()
			colL5 = split.column()	
			
		if suma <= 1:
			print("build graphic before")			
		elif check:
			allData = check
			colL5.label("Configuration:")
			row=layout.row()
			split=row.split()
			colR2 = split.column()
			colR2.operator("calculo.porcentajes", icon="LINENUMBERS_ON")
			split=row.split()
			colL4 = split.column()
			colL4.operator("align.data", icon="FONTPREVIEW")
			colL5 = split.column()
			colL5.operator("colorear.grafica", icon="MATERIAL")
			row=layout.row()
			split=row.split()
			colL2 = split.column()
			colL2.operator("hard.edges", icon="MOD_EDGESPLIT")


class leeruta (bpy.types.Operator):
	bl_idname = "lee.ruta"
	bl_label = "Leer" 
	 
	def execute(self,context):
		global path
		path = bc.scene.importPydataPath
		return {"FINISHED"}


class formatcurves (bpy.types.Operator):
	'''format data for values'''
	bl_idname = "format.curves"
	bl_label = "format curves" 
	
	def execute(self,context):  
#		boo.convert(target='CURVE', keep_original=False)
		bc.selected_objects[0].data.extrude = 0.01
		bc.selected_objects[0].data.bevel_depth = 0.005
		return {"FINISHED"}


class importadorcubos(bpy.types.Operator):
	"""importa data, fabica  cubos con los datos"""
	bl_idname = "importador.cubos"
	bl_label = "Cubes" 

	def execute(self,context):
		global colnrPKHG, allData, chartType, time, factorescala, origin
		chartType = 'cubos'
		distancia= 0
		iescalado = 0
		factorescala = bc.scene.scaleFactor
	
		for data in allData:
			distancia += 3
			escalado = float(data[colnrPKHG])/factorescala
			bpy.ops.mesh.primitive_cube_add(location=((origin[0] + distancia+1),(origin[1] +1.5), (origin[2] + escalado)))  
			bot.resize(value=(1,1,escalado))
			# [start a simple animation]							  
			boo.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
			boo.transform_apply(scale=True)
			iescalado += escalado + 10
			bpy.ops.anim.change_frame(frame = (iescalado+time))
			bpy.ops.anim.keyframe_insert_menu(type="Scaling")   
			bpy.ops.anim.change_frame(frame = (iescalado))
			bot.resize(value=(1,1,0.01))
			bpy.ops.anim.keyframe_insert_menu(type="Scaling")
			# [end a simple animation]  
			boo.modifier_add(type='BEVEL')
			boo.editmode_toggle()
			bpy.ops.mesh.faces_shade_smooth()   
			boo.editmode_toggle()
			boo.select_all(action='DESELECT')
		bpy.ops.ver.nombres()
		bpy.ops.calculo.total()
#		bpy.ops.ver.valores()
		return {"FINISHED"}


class importadorcilindros (bpy.types.Operator):
	"""importa data, fabica  cilindros y los textcurves con la data"""
	bl_idname = "importador.cilindros"
	bl_label = "Cylinders"
	
	def execute(self,context):
		global colnrPKHG, allData, chartType, origin
		factorescala = bc.scene.scaleFactor
		chartType = 'cylinders'
		distancia= 0
		iescalado = 0
		bpy.ops.ver.nombres()
		bpy.ops.calculo.total()
		for data in allData:
			distancia += 3
			escalado = float(data[colnrPKHG])/factorescala
			if escalado >= 0:
				boo.text_add(location=((origin[0] + distancia),(origin[1]+1.5),(origin[2]+((escalado)*2)+0.2)),rotation=(pid2, 0, 0))
			else:
				boo.text_add(location=((origin[0] + distancia),(origin[1]+1.5),(origin[2] + 0.2)),rotation=(pid2, 0, 0))				
			boo.editmode_toggle()
			bpy.ops.font.delete()
			bpy.ops.font.text_insert(text=data[colnrPKHG], accent=False)
			boo.editmode_toggle()
			bpy.ops.format.curves()
			bpy.ops.mesh.primitive_cylinder_add(location=((origin[0] + distancia+1),(origin[1] +1.5),(origin[2] + escalado))) 
			bot.resize(value=(1,1,escalado))
			# [end a simple animation]  
			boo.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
			boo.transform_apply(scale=True)
			iescalado += escalado + 10
			bpy.ops.anim.change_frame(frame = (iescalado+time))
			bpy.ops.anim.keyframe_insert_menu(type='Scaling')   
			bpy.ops.anim.change_frame(frame = (iescalado))
			bot.resize(value=(1,1,0.01))
			bpy.ops.anim.keyframe_insert_menu(type='Scaling')
			# [end a simple animation]  
			boo.modifier_add(type='BEVEL')
			boo.editmode_toggle()
			bpy.ops.mesh.faces_shade_smooth()   
			boo.editmode_toggle()
			boo.select_all(action='DESELECT')
		return {"FINISHED"}
	

class calculototal (bpy.types.Operator):
	"""muestra la suma total de los elementos"""
	bl_idname = "calculo.total"
	bl_label = "Total" 
	
	def execute(self,context):
		global colnrPKHG, allData, suma , negativValueSeen, factorescala, origin
		negativValueSeen = False #assume OK at start
		suma = 0
		for data in allData:
			tmp = float(data[colnrPKHG])
			if tmp < 0:
				negativValueSeen = True
				self.report({'WARNING'}, "negative value occured")
				print("error: not meaningfull with negativ values")
				return {"CANCELLED"}
			suma += tmp
			sumados ="total:" + str(suma)

		boo.text_add(location=((origin[0]-1.5),origin[1],(origin[2] + 3)),rotation=(pid2, 0, 0))
		boo.editmode_toggle()
		bpy.ops.font.delete()
		bpy.ops.font.text_insert(text=(sumados), accent=False)
		boo.editmode_toggle()
		bpy.ops.format.curves()
		sce.frame_end = suma + 30
		boo.select_all(action='DESELECT')
		return {"FINISHED"}
	
class calculoporcentajes (bpy.types.Operator):
	bl_idname = "calculo.porcentajes"
	bl_label = "percentages" 
	
	def execute(self,context):
		global colnrPKHG, allData, suma, negativValueSeen, factorescala, origin
		distancia= 0
		bpy.ops.calculo.total()
		print("\n?????? negativValueSeen", negativValueSeen)
		if negativValueSeen:
			self.report({'WARNING'}, "negative value occured")
			return {'CANCELLED'}
		for data in allData:
			distancia += 3 
			sumando = float(data[colnrPKHG])
			if sumando >= 0:
				porciento = '{:.2%}.'.format(sumando/suma)
				escalado = float(data[colnrPKHG])/factorescala
				boo.text_add(location=((origin[0] + distancia),(origin[1]+1.5),(origin[2] + (escalado*2)+1.1)),rotation=(pid2, 0, 0))  
				boo.editmode_toggle()
				bpy.ops.font.delete()
				bpy.ops.font.text_insert(text=(porciento), accent=False)
				boo.editmode_toggle()
				bpy.ops.format.curves()
				boo.select_all(action='DESELECT')
			else:
				print("negativ value for percentage not meaningful+ ")
		return {"FINISHED"}



class vernombres (bpy.types.Operator):
	"""importa data, fabica  cilindros y los textcurves con la data"""
	bl_idname = "ver.nombres"
	bl_label = "Names" 

	def execute(self,context):
		global factorescala, origin 
		path = bc.scene.importPydataPath
		reader = csv.reader(open(path, 'r'))
		distancia= 0			
		#separacion de las cajitas
		for data in reader:
			distancia += 3  
			data[0]=data[0].replace(' ', '\n')
			boo.text_add(location=((origin[0] + distancia),origin[1],(origin[2]+0.3)),rotation=(pid2, 0, 0))
			boo.editmode_toggle()
			bpy.ops.font.delete()
			bpy.ops.font.text_insert(text=data[0], accent=False)
			boo.editmode_toggle()
			bot.resize(value=(0.6,0.6,0.6))
			bpy.ops.format.curves()
			boo.select_all(action='DESELECT')
		return {"FINISHED"}
			

#   Material by http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Materials_and_textures
class coloreargrafica (bpy.types.Operator):
	"""asigna un material a la grafica azar"""
	bl_idname = "colorear.grafica"
	bl_label = "Paint it!" 

	def execute(self,context):
		
		for ob in bpy.data.objects:
			if ob.type == 'CURVE' or ob.type == 'MESH':
				boo.material_slot_remove() #TODO PKHG??? i think for apply a second time
				x = random.uniform(0.05, 0.95)
				y = random.uniform(0.05, 0.95)
				z = random.uniform(0.05, 0.95)
				colordifuso = bpy.data.materials.new('RandomColor')
				colordifuso.diffuse_color = (x,y,z)
				colordifuso.specular_color = ((x+0.4),(y+0.4),(z+0.4))
				colordifuso.specular_intensity = (0.7)
				boo.select_all(action='DESELECT')
				boo.select_by_type(extend=False, type='MESH')
#   boo.join()
				bc.object.data.materials.append(colordifuso)
				boo.select_all(action='DESELECT')   
			else:
				self.report({'INFO'}, "Please. select any object before")   
		return{'FINISHED'}  

		
class fabricarquesito (bpy.types.Operator):
	"""Viva la arepa"""
	bl_idname = "fabricar.quesito"
	bl_label = "Arepas" 

	def execute(self,context):
			global colnrPKHG, allData, chartType, suma
			chartType = 'arepas'
			tmp = [ float(el[colnrPKHG]) for el in allData if float(el[colnrPKHG]) > 0]
			suma = sum(tmp)
			if suma == 0:
				self.report({'WARNING'}, "not one positive value given")
				print("\n***error*** a pie-chart needs at least ONE positive value!")
				return {'CANCELLED'}
			origin = bpy.context.scene.cursor_location
			distancia= 0
			desfase = 1.1
			objList = []
			counter = 0
			for data in allData:
				counter += 1
				sumando = float(data[colnrPKHG])
				if sumando <= 0:
	#PKHG zero and negative not handled, not meaningful in pie-charts
					message = "not strict positiv value seen: " + str(sumando) + " at row " + str(counter)
					self.report({'WARNING'}, message) #only two parameters allowed!
	#   print({'WARNING'}, "not strict positiv value seen: ", sumando," not used")
					continue
				porciento = sumando/suma
				porciento2 = porciento * pi * 2   
				bpy.ops.curve.primitive_bezier_curve_add( location=(origin[0],origin[1],origin[2])) 
				bot.translate(value=(desfase,0,0))  
				boo.editmode_toggle()   
				bot.translate(value=(1,0,0))
				bot.resize(value=(1,0,0))   
				boo.editmode_toggle()	
				boo.modifier_add(type='SCREW')
				obj = bc.selected_objects[0] 
				obj.modifiers['Screw'].angle = 0
				print(sumando, suma, porciento, porciento2)
				obj.keyframe_insert(data_path='modifiers["Screw"].angle', frame = sumando)
				obj.modifiers['Screw'].angle = porciento2
				boo.select_all(action='TOGGLE')
				boo.select_all(action='TOGGLE')
				bot.rotate(value=(-porciento2,), axis=(0,0,1), constraint_orientation='GLOBAL')
				obj.keyframe_insert(data_path='modifiers["Screw"].angle', frame = (sumando+time))
				boo.modifier_add(type='SOLIDIFY')
				obj.modifiers['Solidify'].thickness = 0.7
				boo.modifier_add(type='EDGE_SPLIT')
				porciento3 = '{:.2%}.'.format(sumando/suma)   
				objList.append(bc.active_object)
				boo.text_add(location=((origin[0]),(origin[1]),(origin[2]+0.3)),rotation=(pi/2, 0, porciento2/2))
				objList.append(bc.active_object)
				boo.editmode_toggle()
				bpy.ops.font.delete()
				bpy.ops.font.text_insert(text=("	 "+porciento3), accent=False)
				boo.editmode_toggle()
				bot.rotate(value=(-porciento2,), axis=(0,0,1), constraint_orientation='GLOBAL')
				bot.resize(value=(0.5,0.5,0.5))			
				bot.translate(value=(4, 0, 0), constraint_axis=(True,False,False), constraint_orientation='NORMAL')
				bpy.ops.format.curves()
				
			for el in objList:
				el.location = origin
				
			bpy.ops.calculo.total()	
			return{'FINISHED'}
	
	
class aligncurvestocamera (bpy.types.Operator):
	"""Align data to camera"""
	bl_idname = "align.data"
	bl_label = "Align data" 

	def execute(self,context):
		
		boo.select_by_type(type='FONT')

		if  bc.selected_objects[0].type == 'FONT':
			boo.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
			boo.visual_transform_apply()
			bot.select_orientation(orientation='VIEW')
			bot.transform(mode='ALIGN', constraint_orientation='VIEW')				
#	
#		else:
#			message = "You have to build data before"
#			self.report({'WARNING'}, message)
#		
	
		return{'FINISHED'}


class hardedges (bpy.types.Operator):
	"""hARD EDGES gracias Soliman"""
	bl_idname = "hard.edges"
	bl_label = "Hard Edges" 
	global allData
	

	def execute(self,context):


		boo.modifier_add(type='EDGE_SPLIT')

		return{'FINISHED'}


#-----REGISTROS------------------------
def register():
	## CREO DATA FILEPATH
	bpy.types.Scene.importPydataPath=bpy.props.StringProperty(default="ruta.csv")
	bpy.types.Scene.useColumnNr=bpy.props.IntProperty(name = "Nr. of column to use",min = 1, max = 100, soft_max = 5, default = 1)
	bpy.types.Scene.scaleFactor=bpy.props.IntProperty(name = "Scale factor",min = 1, max = 1000, soft_max = 100, default = 10)

	## REGISTRA CLASSES
	burc = bpy.utils.register_class


def unregister():
	## DESREGISTRA CLASSES
	burc = bpy.utils.unregister_class

if __name__ == "__main__":
	register()


#   bye bye register one to one
bpy.utils.register_module(__name__)
