#-*- coding: utf-8 -*-
#
# patwork blender tools addon
# v0.1 - 2016-04-07
# v0.2 - 2017-01-01
# v0.3 - 2017-01-03
# v0.4 - 2017-10-03
#

# ----------------------------------------------------------------------------
bl_info = {
	'name': 'patwork tools',
	'description': 'My tools for Blender',
	'author': 'patwork@gmail.com',
	'version': (0, 4),
	'blender': (2, 79, 0),
	'location': 'Tool Shelf',
	'warning': '',
	'wiki_url': 'https://github.com/patwork/blender-tools',
	"category": "Learnbgame",
}

ui = {
	'panel_category': 'patwork',
	'label_tools': 'Tools',

	'label_world': 'World',
	'id_syncskywithsun': 'patwork.syncskywithsun',
	'txt_syncskywithsun': 'Sync sky',
	'icon_syncskywithsun': 'MAT_SPHERE_SKY',

	'label_mesh': 'Mesh',
	'id_renamemeshes': 'patwork.renamemeshes',
	'txt_renamemeshes': 'Rename meshes',
	'icon_renamemeshes': 'OOPS',
	'id_cleanmeshes': 'patwork.cleanmeshes',
	'txt_cleanmeshes': 'Clean meshes',
	'icon_cleanmeshes': 'WIRE',

	'label_clipboard': 'Clipboard',
	'id_copyrendersettings': 'patwork.rendersettings',
	'txt_copyrendersettings': 'Render settings',
	'icon_copyrendersettings': 'TEXT',

	'label_archicad': 'ArchiCad',
	'id_archicadgroups': 'patwork.archicadgroups',
	'txt_archicadgroups': 'Make groups',
	'icon_archicadgroups': 'SCRIPTWIN'
}

# ----------------------------------------------------------------------------
import bpy
from math import *
from mathutils import *

# ----------------------------------------------------------------------------
class SyncSkyWithSun(bpy.types.Operator):
	'''Synchronize Sky Texture with Sun lamp'''

	bl_idname = ui['id_syncskywithsun']
	bl_label = ui['txt_syncskywithsun']

	# ----------------------------------------------------------------------------
	def my_sync_sky_with_sun(self):

		if 'Sky Texture' in bpy.context.scene.world.node_tree.nodes:
			sky = bpy.context.scene.world.node_tree.nodes['Sky Texture']
		else:
			self.report({'ERROR'}, '%s: cannot find sky texture!' % ui['txt_syncskywithsun'])
			return False

		if 'Sun' in bpy.context.scene.objects:
			sun = bpy.context.scene.objects['Sun']
		else:
			self.report({'ERROR'}, '%s: cannot find sun lamp!' % ui['txt_syncskywithsun'])
			return False

		m = sun.matrix_world
		sky.sun_direction = Vector((m[0][2], m[1][2], m[2][2]))

		print('synchronized %s to %s (%f, %f, %f)' % (sky.name, sun.name, m[0][2], m[1][2], m[2][2]))

		return True

	# ----------------------------------------------------------------------------
	def execute(self, context):

		if self.my_sync_sky_with_sun():
			self.report({'INFO'}, '%s: done.' % ui['txt_syncskywithsun'])

		return {'FINISHED'}

# ----------------------------------------------------------------------------
class RenameMeshes(bpy.types.Operator):
	'''Rename meshes to match parent objects'''

	bl_idname = ui['id_renamemeshes']
	bl_label = ui['txt_renamemeshes']

	# ----------------------------------------------------------------------------
	def my_rename_meshes(self):

		ok = 0
		warn = 0
		err = 0

		for obj in bpy.data.objects:
			if obj.type == 'MESH' and obj.name != obj.data.name:

				if obj.data.users > 1:
					print('shared mesh: %s'% obj.data.name)
					warn = warn + 1
				elif obj.name in bpy.data.meshes:
					print('name collision: %s'% obj.name)
					err = err + 1
				else:
					print('rename %s - %s' % (obj.name, obj.data.name))
					obj.data.name = obj.name
					ok = ok + 1

		msg = '%s: done (%d/%d/%d).' % (ui['txt_archicadgroups'], ok, warn, err)

		if (err):
			self.report({'ERROR'}, msg)
			return False
		elif (warn):
			self.report({'WARNING'}, msg)
			return False

		print(msg)

		return True

	# ----------------------------------------------------------------------------
	def execute(self, context):

		if self.my_rename_meshes():
			self.report({'INFO'}, '%s: done.' % ui['txt_renamemeshes'])

		return {'FINISHED'}

# ----------------------------------------------------------------------------
class CleanMeshes(bpy.types.Operator):
	'''Clean selected meshes by removing doubles and converting tris to quads'''
	'''https://blenderartists.org/forum/showthread.php?376273-Remove-Doubles-and-Tris-to-Quads-for-all-imported-meshes-at-once'''

	bl_idname = ui['id_cleanmeshes']
	bl_label = ui['txt_cleanmeshes']

	# ----------------------------------------------------------------------------
	def my_clean_meshes(self):

		if len(bpy.context.selected_objects) == 0:
			self.report({'WARNING'}, 'nothing is selected')
			return False

		bpy.context.tool_settings.mesh_select_mode = (True, False, False)

		for ob in bpy.context.selected_objects:
			if ob.type == 'MESH':
				print('cleaning %s' % ob.name)
				bpy.context.scene.objects.active = ob #set active object
				bpy.ops.object.mode_set(mode='EDIT') #switch to edit mode
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.remove_doubles() #remove doubles
				bpy.ops.mesh.tris_convert_to_quads() #tris to quads
				bpy.ops.object.mode_set(mode='OBJECT') #switch to object mode

		return True

	# ----------------------------------------------------------------------------
	def execute(self, context):

		if self.my_clean_meshes():
			self.report({'INFO'}, '%s: done.' % ui['txt_cleanmeshes'])

		return {'FINISHED'}

# ----------------------------------------------------------------------------
class CopyRenderSettings(bpy.types.Operator):
	'''Copy render settings to clipboard'''

	bl_idname = ui['id_copyrendersettings']
	bl_label = ui['txt_copyrendersettings']

	# ----------------------------------------------------------------------------
	def my_get_attrs(self, object_source, object_name):

		txt = ''

		for key in dir(object_source):
			if hasattr(object_source, key) and key != 'name' and not key.startswith('__') and not key.startswith('debug_'):
				val = getattr(object_source, key)

				if (isinstance(val, (int, float, bool))):
					txt = txt + ('%s.%s = %s\n' % (object_name, key, val))
				elif (isinstance(val, (str))):
					txt = txt + ('%s.%s = "%s"\n' % (object_name, key, val))
				else:
					print('ignoring %s.%s = %s' % (object_name, key, val))

		return txt

	# ----------------------------------------------------------------------------
	def my_copy_render_settings(self):

		scene = bpy.context.scene

		txt = '# %s (Blender %s %s)\n' % (scene.name, bpy.app.version_string, bpy.app.version_cycle);
		txt = txt + self.my_get_attrs(scene.render, 'S.render')
		txt = txt + self.my_get_attrs(scene.cycles, 'S.cycles')
		txt = txt + self.my_get_attrs(scene.view_settings, 'S.view_settings')
		txt = txt + self.my_get_attrs(scene.world.light_settings, 'S.world.light_settings')
		txt = txt + self.my_get_attrs(scene.world.cycles, 'S.world.cycles')
		txt = txt + '# ---\n'

		bpy.context.window_manager.clipboard = txt

		return True

	# ----------------------------------------------------------------------------
	def execute(self, context):

		if self.my_copy_render_settings():
			self.report({'INFO'}, '%s: done.' % ui['txt_copyrendersettings'])

		return {'FINISHED'}

# ----------------------------------------------------------------------------
class ArchicadGroups(bpy.types.Operator):
	'''Clean mess from ArchiCad'''

	bl_idname = ui['id_archicadgroups']
	bl_label = ui['txt_archicadgroups']

	my_empty = '_ARCHICAD'

	# ----------------------------------------------------------------------------
	def my_create_empty(self, object_name, object_parent):

		if object_name in bpy.data.objects:
			return bpy.data.objects[object_name]

		print('creating empty %s' % object_name)

		bpy.ops.object.add(type = 'EMPTY')
		object_new = bpy.context.active_object

		if object_new is None:
			self.report({'ERROR'}, '%s: cannot create empty %s!' % ui['txt_archicadgroups'], object_name)
			return None

		object_new.name = object_name
		object_new.rotation_euler = Euler((0.0, 0.0, 0.0))
		object_new.location = Vector((0.0, 0.0, 0.0))
		object_new.scale = Vector((1.0, 1.0, 1.0))

		if object_parent:
			object_new.parent = object_parent

		return object_new

	# ----------------------------------------------------------------------------
	def my_archicad_groups(self):

		if self.my_empty in bpy.data.objects:
			self.report({'WARNING'}, '%s: there can be only one!' % ui['txt_archicadgroups'])
			return False

		top = self.my_create_empty(self.my_empty, None)
		if not top:
			return False

		groups = {}

		for loop in [ 0, 1 ]:
			for obj in bpy.data.objects:
				if obj.type == 'MESH' and obj.parent is None:
					arr = obj.name.strip().split()
					if len(arr) > 1:
						pre = arr[0].upper()

						if loop == 0:
							if pre in groups:
								groups[pre] = groups[pre] + 1
							else:
								groups[pre] = 1

						else:
							if pre in groups and groups[pre] > 1:
								obj.parent = self.my_create_empty('_' + pre, top)
								if not obj.parent:
									return False
							else:
								obj.parent = top

		return True

	# ----------------------------------------------------------------------------
	def execute(self, context):

		if self.my_archicad_groups():
			self.report({'INFO'}, '%s: done.' % ui['txt_archicadgroups'])

		return {'FINISHED'}

# ----------------------------------------------------------------------------
class ToolsPanel(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = 'objectmode'
	bl_category = ui['panel_category']
	bl_label = ui['label_tools']

	# ----------------------------------------------------------------------------
	def draw(self, context):
		col = self.layout.column(align = True)

		col.label(ui['label_world'])
		col.operator(ui['id_syncskywithsun'], text = ui['txt_syncskywithsun'], icon = ui['icon_syncskywithsun'])

		col.label(ui['label_mesh'])
		col.operator(ui['id_renamemeshes'], text = ui['txt_renamemeshes'], icon = ui['icon_renamemeshes'])
		col.separator()
		col.operator(ui['id_cleanmeshes'], text = ui['txt_cleanmeshes'], icon = ui['icon_cleanmeshes'])

		col.label(ui['label_clipboard'])
		col.operator(ui['id_copyrendersettings'], text = ui['txt_copyrendersettings'], icon = ui['icon_copyrendersettings'])

		col.label(ui['label_archicad'])
		col.operator(ui['id_archicadgroups'], text = ui['txt_archicadgroups'], icon = ui['icon_archicadgroups'])

# ----------------------------------------------------------------------------
def register():
	print('register: %s (%d.%d)' % (bl_info['name'], bl_info['version'][0], bl_info['version'][1]))
	bpy.utils.register_class(SyncSkyWithSun)
	bpy.utils.register_class(RenameMeshes)
	bpy.utils.register_class(CleanMeshes)
	bpy.utils.register_class(CopyRenderSettings)
	bpy.utils.register_class(ArchicadGroups)
	bpy.utils.register_class(ToolsPanel)

# ----------------------------------------------------------------------------
def unregister():
	print('unregister: %s (%d.%d)' % (bl_info['name'], bl_info['version'][0], bl_info['version'][1]))
	bpy.utils.unregister_class(SyncSkyWithSun)
	bpy.utils.unregister_class(RenameMeshes)
	bpy.utils.unregister_class(CleanMeshes)
	bpy.utils.unregister_class(CopyRenderSettings)
	bpy.utils.unregister_class(ArchicadGroups)
	bpy.utils.unregister_class(ToolsPanel)

# ----------------------------------------------------------------------------
if __name__ == '__main__':
	register()

# EoF
# vim: noexpandtab tabstop=4 softtabstop=4 shiftwidth=4
