# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA

bl_info = {
'name': 'Flippist',
'author': 'Alexey Khlystov',
'version': (1, 3),
'blender': (2, 7, 8),
'location': 'View3D > Spacebar Search > Flippist',
'description': 'Automatically Flip Normals and Make Normals Consistent on multiple objects',
'wiki_url': 'http://alexiy.nl/flippist/',
'tracker_url': 'http://alexiy.nl/feedback/',
"category": "Learnbgame",
}

import bpy

def log(text):
	if bpy.context.user_preferences.addons[__name__].preferences.pref_log:
		print('Flippist: '+text)
	return {'FINISHED'}

class flippist_preferences(bpy.types.AddonPreferences):
	bl_idname = __name__
	pref_log = bpy.props.BoolProperty(
			name = 'Logging',
			description = 'Logging to the console',
			default = False)

	pref_def = bpy.props.EnumProperty(
		items = [('0', 'Flip Normals', 'Flip Normals'),
				('1', 'Make Normals Consistent', 'Make Normals Consistent'),
				('2', 'Make Normals Consistent next Flip Normals', 'Make Normals Consistent next Flip Normals')],
		name = 'Default behavior (after Blender reload)',
		description = 'Default behavior',
		default = '0')

	def draw(self, context):
		self.layout.prop(self, 'pref_def')
		self.layout.prop(self, 'pref_log')

		self.layout.operator('wm.url_open', text='mmm... donuts ;)', icon='MESH_TORUS').url = 'https://www.paypal.me/alekhly'

bpy.utils.register_class(flippist_preferences)

class flippist(bpy.types.Operator):
	bl_idname = 'object.flippist'
	bl_label = 'Flippist'
	bl_context = 'objectmode'
	bl_options = {'REGISTER', 'UNDO'}

	default = '0'
	if __name__ in bpy.context.user_preferences.addons:
		if not(bpy.context.user_preferences.addons[__name__].preferences == None) and bool(bpy.context.user_preferences.addons[__name__].preferences.pref_def):
			default = bpy.context.user_preferences.addons[__name__].preferences.pref_def

	param = bpy.props.EnumProperty(
		items = [('0', 'Flip Normals', 'Flip Normals'),
				('1', 'Make Normals Consistent', 'Make Normals Consistent'),
				('2', 'Make Normals Consistent next Flip Normals', 'Make Normals Consistent next Flip Normals')],
		name = 'Flippist options',
		default = default)

	def execute(self, context):
		objects = bpy.context.selected_objects

		if len(objects) == 0:
			log('no selected objects')
			return {'FINISHED'}

		wm = bpy.context.window_manager
		wm.progress_begin(0, len(objects))
		progress = 0;

		for object in objects:

			if object.type != 'MESH':
				log(object.name+' is not a mesh object')

			else:
				bpy.context.scene.objects.active = object
				bpy.ops.object.mode_set(mode = 'EDIT')
				bpy.ops.mesh.reveal()
				bpy.ops.mesh.select_all(action='SELECT')

				if self.param == '0':
					bpy.ops.mesh.flip_normals()
				elif self.param == '1':
					bpy.ops.mesh.normals_make_consistent()
				elif self.param == '2':
					bpy.ops.mesh.normals_make_consistent()
					bpy.ops.mesh.flip_normals()

				bpy.ops.object.mode_set(mode = 'OBJECT')
				log(object.name+' - hit!')

			progress = progress + 1
			wm.progress_update(progress)

		wm.progress_end()
		return {'FINISHED'}

def register():
	try:
		foo = bool(bpy.types.flippist_preferences)
	except:
		bpy.utils.register_class(flippist_preferences)

	bpy.utils.register_class(flippist)

def unregister():
	bpy.utils.unregister_class(flippist)
	bpy.utils.unregister_class(flippist_preferences)