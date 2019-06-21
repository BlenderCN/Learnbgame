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

# <pep8-80 compliant>

#----------------------------------------------------------
# File make_solid_helpers.py
# Helper functions, to be used by MakeSolid class .
#----------------------------------------------------------

import bpy
import bmesh


def prepare_meshes():
	bpy.ops.object.make_single_user(object=True, obdata=True)
	bpy.ops.object.convert()
	bpy.ops.object.join()

	bpy.ops.object.mode_set(mode='EDIT')

	# selection dance for proper results
	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.context.tool_settings.mesh_select_mode = (True, True, True)

	bpy.ops.mesh.normals_make_consistent(inside=False)
	bpy.ops.mesh.separate(type='LOOSE')
	bpy.ops.object.mode_set(mode='OBJECT')


def prepare_mesh(obj, select_action):
	scene = bpy.context.scene

	active_object = bpy.context.active_object
	scene.objects.active = obj
	bpy.ops.object.mode_set(mode='EDIT')

	# reveal hidden vertices in mesh
	bpy.ops.mesh.reveal()

	# mesh cleanup
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.separate(type='LOOSE')
	bpy.ops.mesh.delete_loose()

	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.remove_doubles(threshold=0.0001)

	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.fill_holes(sides=0)

	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.quads_convert_to_tris()

	# back to previous settings
	bpy.ops.mesh.select_all(action=select_action)
	bpy.ops.object.mode_set(mode='OBJECT')
	scene.objects.active = active_object


def cleanup_mesh(obj):
	mesh = obj.data
	bm = bmesh.new()
	bm.from_mesh(mesh)
	bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
	bm.to_mesh(mesh)
	bm.free()


def add_modifier(active, selected):
	bool_modifier = active.modifiers.new('Boolean', 'BOOLEAN')
	bool_modifier.object = selected
	bool_modifier.show_viewport = False
	bool_modifier.show_render = False
	bool_modifier.operation = 'UNION'
	try:
		bool_modifier.solver = 'CARVE'
	except:
		pass

	bpy.ops.object.modifier_apply(modifier='Boolean')

	bpy.context.scene.objects.unlink(selected)
	bpy.data.objects.remove(selected)


def make_solid_batch():
	active = bpy.context.active_object
	selected = bpy.context.selected_objects
	selected.remove(active)

	prepare_mesh(active, 'DESELECT')

	for sel in selected:
		prepare_mesh(sel, 'SELECT')
		add_modifier(active, sel)
		cleanup_mesh(active)


def is_manifold(self):
	mesh = bpy.context.active_object.data
	bm = bmesh.new()
	bm.from_mesh(mesh)

	for edge in bm.edges:
		if not edge.is_manifold:
			bm.free()
			self.report({'ERROR'}, 'Boolean operation result is non-manifold')
			return False

	bm.free()
	return True
