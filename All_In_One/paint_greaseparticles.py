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

__bpydoc__ = """\
GreaseParticles - greasepencil draw with particles.


Documentation

First go to User Preferences->Addons and enable the GreaseParticles addon in the Paint category.
Enable and GreaseParticles shows up in the 3Dview properties panel.  Click activate to activate,
click deactivate to stop.
When activated greasepencil strokes will be converted in curves and these in meshes automatically.
You can find these meshcurves as sibling of the GPLAYERNAME_empty object, which is itself a child
of the active object.
You need first to create a ParticleSettings object with the same name as the greasepencil layer
you are drawing on.  These settings will be created and initialized if they dont already exist.
At the end of each stroke particles will be created.
"""


bl_info = {
	"name": "GreaseParticles",
	"author": "Gert De Roost",
	"version": (0, 1, 0),
	"blender": (2, 6, 3),
	"location": "View3D > Properties",
	"description": "Greasepencil draw with particles.",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame",
}

if "bpy" in locals():
	import imp


import bpy


activated = 0
setedit = 0


class GreaseParticlesPanel(bpy.types.Panel):
	bl_label = "GreaseParticles"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw_header(self, context):
		
		if not(activated):
			self.layout.operator("paint.greaseparticles", text="Activate")
		else:
			self.layout.operator("paint.greaseparticles", text="Deactivate")
			
	def draw(self, context):
		
		pass


class GreaseParticles(bpy.types.Operator):
	bl_idname = "paint.greaseparticles"
	bl_label = "GreaseParticles"
	bl_description = "Greasepencil draw with particles"
	bl_options = {"REGISTER"}
	
	def invoke(self, context, event):
		
		global activated, contxt
		
		contxt = bpy.context
		
		if not(activated):
			activated = 1
			self._handle = context.region.callback_add(redraw, (), 'PRE_VIEW')
			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			activated = 0
			context.region.callback_remove(self._handle)
			return {'FINISHED'}

	def modal(self, context, event):

		global mousex, mousey
		
		mousex = event.mouse_region_x
		mousey = event.mouse_region_y
		
		return {'PASS_THROUGH'}
		
		

def register():
	bpy.utils.register_module(__name__)


def unregister():
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()



def redraw():
	
	global setedit
	
	region = contxt.region
	if mousex < 0 or mousex > region.width or mousey < 0 or mousey > region.height:
		return
	obj = contxt.active_object
	pencil = obj.grease_pencil
	if pencil == None:
		return
	layer = obj.grease_pencil.layers.active
	if layer.active_frame.is_edited:
		setedit = 1
		return
	if setedit:
		setedit = 0
		layerempty = bpy.data.objects.get(layer.info + "_empty")
		if layerempty == None:
			bpy.ops.object.add(type='EMPTY', location=obj.location, rotation=obj.rotation_euler)
			contxt.active_object.name = layer.info + "_empty"
			layerempty = contxt.active_object
			obj.select = True
			contxt.scene.objects.active = obj
			bpy.ops.object.parent_set(type='OBJECT')
		psettings = bpy.data.particles.get(layer.info)
		if psettings == None:
			psettings = bpy.data.particles.new(layer.info)
		bpy.ops.gpencil.convert(type="CURVE")
		bpy.ops.object.convert(target='MESH', keep_original=False)
		bpy.ops.object.particle_system_add()
		curve = contxt.active_object
		curve.particle_systems[0].name = curve.name
		curve.particle_systems[0].settings = psettings
		layerempty.select = True
		contxt.scene.objects.active = layerempty
		bpy.ops.object.parent_set(type='OBJECT')
		obj.select = True
		contxt.scene.objects.active = obj
		layer.select = True
		curve.select = False
