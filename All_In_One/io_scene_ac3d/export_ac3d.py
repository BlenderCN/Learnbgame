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

'''
This file is a complete reboot of the AC3D export script that is used to export .ac format file into blender.

Reference to the .ac format is found here:
http://www.inivis.com/ac3d/man/ac3dfileformat.html

Some noted points that are important for consideration:
 - AC3D appears to use Left Handed axes, but with Y oriented "Up". Blender uses Right Handed axes, the export does provide a rotation matrix applied to the world object that corrects this, so "Up" in the blender becomes "Up" in the .AC file - it's configurable, so you can change how it rotates...
 - AC3D supports only one texture per surface. This is a UV texture map, so only blenders texmap is exported
 - Blender's Materials can have multiple textures per material - so a material + texure in AC3D requires a distinct and unique material in blender. The export uses a comparison of material properties to see if a material is the same as another one and then uses that material index for the .ac file.

TODO: Option to define "DefaultWhite" material
TODO: Optionally over-write existing textures
'''

from . import AC3D

import os, bpy
from math import radians
from mathutils import Matrix

def TRACE(message):
	AC3D.TRACE(message)

class ExportConf:
	def __init__(
			self,
			operator,
			context,
			filepath,
			global_matrix,
			use_selection,
			use_render_layers,
			skip_data,
			global_coords,
			mircol_as_emis,
			mircol_as_amb,
			crease_angle,
			):
		# Stuff that needs to be available to the working classes (ha!)
		self.operator = operator
		self.context = context
		self.global_matrix = global_matrix
		self.use_selection = use_selection
		self.use_render_layers = use_render_layers
		self.skip_data = skip_data
		self.global_coords = global_coords
		self.mircol_as_emis = mircol_as_emis
		self.mircol_as_amb = mircol_as_amb
		self.crease_angle = crease_angle

		# used to determine relative file paths
		self.exportdir = os.path.dirname(filepath)
		self.ac_name = os.path.split(filepath)[1]
		TRACE('Exporting to {0}'.format(self.ac_name))

class ExportAC3D:
	def __init__(
			self,
			operator,
			context,
			filepath='',
			global_matrix=None,
			use_selection=False,
			use_render_layers=True,
			skip_data=False,
			global_coords=False,
			mircol_as_emis=True,
			mircol_as_amb=False,
			crease_angle=radians(35.0),
			):

			self.export_conf = ExportConf(
										operator,
										context,
										filepath,
										global_matrix,
										use_selection,
										use_render_layers,
										skip_data,
										global_coords,
										mircol_as_emis,
										mircol_as_amb,
										crease_angle,
										)

			#TRACE("Global: {0}".format(global_matrix))

			self.ac_mats = [AC3D.Material()]
			self.ac_world = None

			# Parsing the tree in a top down manner and check on the way down which
			# objects are to be exported

			self.world = AC3D.World('Blender_export__' + bpy.path.basename(filepath), self.export_conf)
			self.parseLevel(self.world, [ob for ob in bpy.data.objects if ob.parent == None and not ob.library])
			self.world.parse(self.ac_mats)

			# dump the contents of the lists to file
			ac_file = open(filepath, 'w')
			ac_file.write('AC3Db\n')
			for ac_mat in self.ac_mats:
				ac_mat.write(ac_file)

			#self.ac_world.write_ac_output(ac_file)
			self.world.write(ac_file)
			ac_file.close()

	def parseLevel( self,
									parent,
									objects,
									ignore_select = False,
									local_transform = Matrix() ):
		'''
		Parse a level in the object hierarchy
		'''
		for ob in objects:

			ac_ob = None

			# Objects from libraries don't have the select flag set even if their
			# proxy is selected. We therefore consider all objects from libraries as
			# selected, as the only possibility to get them considered is if their
			# proxy should be exported.
			if 		(not self.export_conf.use_render_layers or ob.is_visible(self.export_conf.context.scene))\
				and (not self.export_conf.use_selection or ob.select or ignore_select):

				# We need to check for dupligroups first as every type of object can be
				# converted to a dupligroup without removing the data from the old type.
				if ob.dupli_type == 'GROUP':
					ac_ob = AC3D.Group(ob.name, ob, self.export_conf, local_transform)
					children = [child for child in ob.dupli_group.objects
					                            if not child.parent
					                            or not child.parent.name in ob.dupli_group.objects]
					self.parseLevel(ac_ob, children, True, local_transform * ob.matrix_world)
				elif ob.type in ['MESH', 'LATTICE', 'SURFACE', 'CURVE']:
					ac_ob = AC3D.Poly(ob.name, ob, self.export_conf, local_transform)
				elif ob.type == 'ARMATURE':
					p = parent
					for bone in ob.pose.bones:
						for c in ob.children:
							if c.parent_bone == bone.name:
								ac_child = AC3D.Poly(c.name, c, self.export_conf, local_transform)
								p.addChild(ac_child)
								p = ac_child

								if len(c.children):
									self.parseLevel(p, c.children, ignore_select, local_transform)
					continue
				elif ob.type == 'EMPTY':
					ac_ob = AC3D.Group(ob.name, ob, self.export_conf, local_transform)
				else:
					TRACE('Skipping object {0} (type={1})'.format(ob.name, ob.type))

			if ac_ob:
				parent.addChild(ac_ob)
				next_parent = ac_ob
			else:
				# if link chain is broken (aka one element not exported) the object will
				# be placed in global space (=world)
				next_parent = self.world

			if len(ob.children):
				self.parseLevel(next_parent, ob.children, ignore_select, local_transform)
