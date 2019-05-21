# FleetMaker.py Copyright (C) 2011, Dolf Veenvliet
#
#
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
	"name": "FleetMaker",
	"author": "Dolf Veenvliet + Andrew Porter",
	"version": 1,
	"blender": (2, 5, 6),
	"api": 31847,
	"location": "object > FleetMaker ",
	"description": "Build a Ship for Fleet",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame"
}

"""
Usage:

Launch from "object -> fleetmaker"


Additional links:
	Author Site: http://www.macouno.com
	e-mail: dolf {at} macouno {dot} com
"""


import bpy
import mathutils
import math
import random
import time
import os
import json
from bpy.props import StringProperty, IntProperty


# Make it as a class
class ShipWright():

	# Initialise the class
	def __init__(self, context, seed, limit, percentage, filename):

		random.seed(seed)
		self.startTime = time.time()
		self.markTime = self.startTime
		self.debug = True
		self.partCount = 0
		self.partRefs = []
		self.connectors = []
		self.hitParts = []

		self.scn = bpy.data.scenes[0]
		for ob in self.scn.objects:
			ob.select = False
		self.scn.objects.active = None

		self.mark('START')

		# Get a random starting point!
		basesGroup = bpy.data.groups['hulls']
		partsGroup = bpy.data.groups['parts']

		# Get a nr to select a part

		self.setPart(connector=None, part=None,
		             group=basesGroup, percentage=percentage)

		while self.partCount < limit and len(self.connectors):

			self.setPart(connector=self.getConnector(), part=None, group=partsGroup,percentage=percentage)

		if self.partCount >= limit:
			self.mark('END > reached limit')
		elif not len(self.connectors):
			self.mark('END > no more connectors')
		
		self.mark("start wrapping process")
		for j in range(len(self.partRefs)):
			ref = self.partRefs[j]
			ref.select = True
			self.mark("uv unwrapping part")
			self.scn.objects.active = ref
			self.mark("set active")
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action = 'SELECT')
			bpy.ops.uv.smart_project()
			bpy.ops.mesh.select_all(action = 'DESELECT')
			bpy.ops.object.mode_set(mode = 'OBJECT')
			ref.select = False
			self.scn.objects.active = None
		
		partnames = []
		for j in range(len(self.partRefs)):
			ref = self.partRefs[j]
			ref.select = True
			print(ref.name)
			partnames.append(ref.name)
			
		blend_file_path = bpy.data.filepath
		directory = os.path.dirname(blend_file_path)
		jsonfiledata = { "parts" : partnames, "count": self.partCount }
		target_file_json = os.path.join(directory, filename + "_.json")
		with open(target_file_json, 'w') as outfile:
			json.dump(jsonfiledata, outfile)
		
		bpy.context.scene.layers = [True,False,False,False,False,False,False,False,False,False,False, False,False,False,False,False,False,False,False,False]
		bpy.ops.object.select_all(action='SELECT')
		bpy.context.scene.objects.active = self.partRefs[0]

		target_file = os.path.join(directory, filename)
		bpy.ops.export_scene.obj(filepath=target_file, check_existing=True, axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl", use_selection=True, use_animation=False, use_mesh_modifiers=True, use_edges=True, use_smooth_groups=False, use_smooth_groups_bitflags=False, use_normals=True, use_uvs=True, use_materials=True, use_triangles=False, use_nurbs=False, use_vertex_groups=False, use_blen_objects=True, group_by_object=False, group_by_material=False, keep_vertex_order=False, global_scale=1, path_mode='AUTO')
		return

	def setPart(self, connector=None, part=None, group=None, percentage=None):

		oPart = None
		minArea = 0
		if group is None:
			return

		if part is None:
			part = self.getPart(group)
			oPart = part
			
		self.partRefs.append(part)
		part.select = True
		self.scn.objects.active = part
		bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
		bpy.ops.object.duplicate(linked=True)

		if percentage is not None:
			areas = [i.area for i in part.data.polygons if i.area > 2]
			areas.sort()
			area_index = math.floor(len(areas) * (percentage / 100))
			if len(areas) > 0:
				minArea = areas[area_index]
			self.mark("min area set to " + str(minArea))
		else:
			self.mark("min area not set")

		bpy.ops.object.move_to_layer(layers=(True, False, False, False, False, False, False, False,
		                             False, False, False, False, False, False, False, False, False, False, False, False))

		part = self.scn.objects.active
		if connector is None:
			part.location = (0.0, 0.0, 0.0)
			part.rotation_euler = (0.0, 0.0, 0.0)
			if len(self.connectors) == 0:
				polygons = [i for i in part.data.polygons if i.area > minArea]
				self.mark('looking for polygons to use as connectors')
				self.mark('found connectors ' + str(len(polygons)))
				c = 0
				for poly in polygons:
					if c < 100:
						o = bpy.data.objects.new("poliy_empty" + str(c), None)
						c = c + 1
						bpy.context.scene.objects.link(o)
						co_final = part.matrix_world * poly.center
						o.location = co_final
						o.parent = part
		else:
			self.connectors.remove(connector)
			part.matrix_world = connector.matrix_world

		self.partCount += 1
		
        
		if len(part.children):
			for c in part.children:
				cMat = mathutils.Matrix(c.matrix_world)
				c.parent = None
				self.connectors.append(c)
				c.matrix_world = cMat
				c.select = False
				
		part.select = False
		self.scn.objects.active = None
		
		# mirror all this
		if oPart and not connector is None:
			checkLoc = mathutils.Vector(connector.location)
			for c in self.connectors:
				if round(c.location[1],4) == round(connector.location[1],4) and round(c.location[2],4) == round(connector.location[2],4):
					if random.random() > 0.5:
						self.mark('mirroring')
						self.setPart(connector=c, part=oPart, group=group, percentage=percentage)
		
		return
		
		
	# Select a random connector(child)
	def getConnector(self):
	
		if not len(self.connectors):
			return None
			
		sel = int(math.floor(random.random() * len(self.connectors)))
		self.mark('selecting '+str(sel)+' from connectors')
		
		return self.connectors[sel]
	
		
	# Select a random part
	def getPart(self, group):
	
		if not len(group.objects):
			return None
	
		# Get a nr to select a part
		sel = int(math.floor(random.random() * len(group.objects)))
		self.mark('selecting '+str(sel)+' from '+group.name)
		
		return group.objects[sel]
		
		
		
	# Mark this point in time and print if we want... see how long it takes
	def mark(self,desc):
		if self.debug:
			now = time.time()
			jump = now - self.markTime
			self.markTime = now
			print(desc.rjust(30, ' '),round(jump,5))		
		
		
		

		
		
class FleetMaker_init(bpy.types.Operator):
	'''Build a Fleet'''
	bl_idname = 'object.fleetmaker'
	bl_label = 'Ship Fleet Maker'
	bl_options = {'REGISTER', 'UNDO'}
	
	d = int(random.random()*1000)

	seed = IntProperty(name="Seed", description="Nr to seed your ship with", default=d)
	
	limit = IntProperty(name="Limit", description="Limit the nr of parts", default=50)

	percentage = IntProperty(name="Percentile", description="Size of the auto connect", default=60)

	filename = StringProperty(name="Name", description="Name of exported file.", default="myobject1")

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		bpy.context.scene.layers = [True,True,True,True,True,True,True,True,True,True,True, True,True,True,True,True,True,True,True,True]
		ship = ShipWright(context, self.seed, self.limit, self.percentage, self.filename) 
		bpy.context.scene.layers = [True,False,False,False,False,False,False,False,False,False,False, False,False,False,False,False,False,False,False,False]
		bpy.ops.object.select_all(action='SELECT')

		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(FleetMaker_init.bl_idname, text="FleetMaker")
	
def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
	register()
