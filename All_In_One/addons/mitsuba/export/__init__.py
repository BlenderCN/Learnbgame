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

import bpy, os, copy, subprocess, math, mathutils
import string
import collections
from math import radians
from extensions_framework import util as efutil
from ..outputs import MtsLog

class ExportProgressThread(efutil.TimerThread):
	message = '%i%%'
	KICK_PERIOD = 0.2
	total_objects = 0
	exported_objects = 0
	last_update = 0
	def start(self, number_of_meshes):
		self.total_objects = number_of_meshes
		self.exported_objects = 0
		self.last_update = 0
		super().start()
	def kick(self):
		if self.exported_objects != self.last_update:
			self.last_update = self.exported_objects
			pc = int(100 * self.exported_objects/self.total_objects)
			MtsLog(self.message % pc)

class ExportCache(object):
	def __init__(self, name='Cache'):
		self.name = name
		self.cache_keys = set()
		self.cache_items = {}
		self.serial_counter = collections.Counter()
	
	def clear(self):
		self.__init__(name=self.name)
	
	def serial(self, name):
		s = self.serial_counter[name]
		self.serial_counter[name] += 1
		return s
	
	def have(self, ck):
		return ck in self.cache_keys
	
	def add(self, ck, ci):
		self.cache_keys.add(ck)
		self.cache_items[ck] = ci
	
	def get(self, ck):
		if self.have(ck):
			return self.cache_items[ck]
		else:
			raise Exception('Item %s not found in %s!' % (ck, self.name))

class ParamSetItem(list):
	type		= None
	type_name	= None
	name		= None
	value		= None
	
	def __init__(self, *args):
		self.type, self.name, self.value = args
		self.type_name = "%s %s" % (self.type, self.name)
		self.append(self.type_name)
		self.append(self.value)
	
	def export(self, exporter):
		if self.type == "color":
			exporter.parameter('rgb', self.name,
				{ 'value' : "%s %s %s" % (self.value[0], self.value[1], self.value[2])})
		elif self.type == "point" or self.type == "vector":
			exporter.parameter(self.type, self.name,
				{ 'value' : "%s %s %s" % (self.value[0], self.value[1], self.value[2])})
		elif self.type == "integer" or self.type == "float" \
				or self.type == "string" or self.type == "boolean":
			exporter.parameter(self.type, self.name, { 'value' : "%s" % self.value })
	
	def export_ref(self, exporter):
		if self.type == "reference_texture" or self.type == 'reference_medium' or self.type == 'reference_id':
			if self.name != "":
				exporter.element('ref', {'id' : self.value, 'name' : self.name})
			else:
				exporter.element('ref', {'id' : self.value})
		elif self.type == "reference_material":
			exporter.element('ref', {'id' : self.value+'-material', 'name' : self.name})

class ParamSet(list):
	names = []
	
	def update(self, other):
		for p in other:
			self.add(p.type, p.name, p.value)
		return self
	
	def add(self, type, name, value):
		if name in self.names:
			for p in self:
				if p.name == name:
					self.remove(p)
		
		self.append(
			ParamSetItem(type, name, value)
		)
		self.names.append(name)
		return self
	
	def add_float(self, name, value):
		self.add('float', name, value)
		return self
	
	def add_integer(self, name, value):
		self.add('integer', name, value)
		return self
	
	def add_reference(self, type, name, value):
		self.add('reference_%s' % type, name, value)
		return self
	
	def add_bool(self, name, value):
		self.add('boolean', name, str(value).lower())
		return self
	
	def add_string(self, name, value):
		self.add('string', name, str(value))
		return self
	
	def add_vector(self, name, value):
		self.add('vector', name, [i for i in value])
		return self
	
	def add_point(self, name, value):
		self.add('point', name, [p for p in value])
		return self
	
	def add_color(self, name, value):
		self.add('color', name, [c for c in value])
		return self
	
	def export(self, exporter):
		for item in self:
			item.export(exporter)
		for item in self:
			item.export_ref(exporter)

def is_obj_visible(scene, obj, is_dupli=False):
	ov = False
	for lv in [ol and sl and rl for ol,sl,rl in zip(obj.layers, scene.layers, scene.render.layers.active.layers)]:
		ov |= lv
	return (ov or is_dupli) and not obj.hide_render

def get_instance_materials(ob):
	obmats = []
	# Grab materials attached to object instances ...
	if hasattr(ob, 'material_slots'):
		for ms in ob.material_slots:
			obmats.append(ms.material)
	# ... and to the object's mesh data
	if hasattr(ob.data, 'materials'):
		for m in ob.data.materials:
			obmats.append(m)
	return obmats

def resolution(scene):
	'''
	scene		bpy.types.scene
	Calculate the output render resolution
	Returns		tuple(2) (floats)
	'''
	xr = scene.render.resolution_x * scene.render.resolution_percentage / 100.0
	yr = scene.render.resolution_y * scene.render.resolution_percentage / 100.0
	
	return xr, yr

def MtsLaunch(mts_path, path, commandline):
	env = copy.copy(os.environ)
	env['LD_LIBRARY_PATH'] = mts_path
	commandline[0] = os.path.join(mts_path, commandline[0])
	return subprocess.Popen(commandline, env = env, cwd = path)		#, stdout=subprocess.PIPE)
