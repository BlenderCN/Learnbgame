'''
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
    "name": "Scene Lighting Presets",
    "author": "meta-androcto",
    "version": (0,1),
    "blender": (2, 6, 3),
    "location": "View3D > Tool Shelf > Scene Lighting Presets",
    "description": "Creates Scenes with Lighting presets",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/",
    "tracker_url": "",
    "category": "Learnbgame",
}
'''	
import bpy, mathutils, math
from math import pi
from bpy.props import *
from mathutils import Vector

class add_scene(bpy.types.Operator):
    bl_idname = "objects_ao.add_scene"
    bl_label = "Create test scene"
    bl_description = "AO Scene with Objects"
    bl_register = True
    bl_undo = True
    
    def execute(self, context):
        blend_data = context.blend_data
        ob = bpy.context.active_object
	
# add new scene
        bpy.ops.scene.new(type="NEW")
        scene = bpy.context.scene
        scene.name = "scene_objects_ao"
# render settings
        render = scene.render
        render.resolution_x = 1920
        render.resolution_y = 1080
        render.resolution_percentage = 50
# add new world
        world = bpy.data.worlds.new("AO_World")
        scene.world = world
        world.use_sky_blend = True
        world.use_sky_paper = True
        world.horizon_color = (0.004393,0.02121,0.050)
        world.zenith_color = (0.03335,0.227,0.359)
        world.light_settings.use_ambient_occlusion = True
        world.light_settings.ao_factor = 1.00
# add camera
        bpy.ops.object.camera_add(location = (7.48113,-6.50764,5.34367), rotation = (1.109319,0.010817,0.814928))
        cam = bpy.context.active_object.data
        cam.lens = 35
        cam.draw_size = 0.1
        
# add cube
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.subdivide(number_cuts=2)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.modifier_add(type='BEVEL')
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.ops.object.shade_smooth()


        cube = bpy.context.active_object
# add new material

        cubeMaterial = blend_data.materials.new("Cube_Material")
        bpy.ops.object.material_slot_add()
        cube.material_slots[0].material = cubeMaterial

            
#Material settings
# Diffuse
        cubeMaterial.preview_render_type = "CUBE"
        cubeMaterial.diffuse_color = (1.000, 0.373, 0.00)
        cubeMaterial.diffuse_shader  = 'OREN_NAYAR' 
        cubeMaterial.diffuse_intensity = 1.0
        cubeMaterial.roughness = 0.09002
# Specular
        cubeMaterial.specular_color = (1.000, 0.800, 0.136)
        cubeMaterial.specular_shader = "PHONG"
        cubeMaterial.specular_intensity = 1.0
        cubeMaterial.specular_hardness = 511.0
# Shading
        cubeMaterial.ambient = 1.00
        cubeMaterial.use_cubic = False
# Transparency
        cubeMaterial.use_transparency = False
        cubeMaterial.alpha = 0
# Mirror
        cubeMaterial.raytrace_mirror.use = True
        cubeMaterial.mirror_color = (1.000, 0.793, 0.0)
        cubeMaterial.raytrace_mirror.reflect_factor = 0.394
        cubeMaterial.raytrace_mirror.fresnel = 2.0
        cubeMaterial.raytrace_mirror.fresnel_factor = 1.641
        cubeMaterial.raytrace_mirror.fade_to = "FADE_TO_SKY"
        cubeMaterial.raytrace_mirror.gloss_anisotropic = 1.0
# Shadow
        cubeMaterial.use_transparent_shadows = True
		
# Add a texture
        cubetex = blend_data.textures.new("CloudTex", type='CLOUDS')
        cubetex.noise_type = 'SOFT_NOISE'
        cubetex.noise_scale = 0.25
        mtex = cubeMaterial.texture_slots.add()
        mtex.texture = cubetex
        mtex.texture_coords = 'ORCO'
        mtex.scale = (0.800, 0.800, 0.800)
        mtex.use_map_mirror = True
        mtex.mirror_factor = 0.156
        mtex.use_map_color_diffuse = True
        mtex.diffuse_color_factor = 0.156
        mtex.use_map_normal = True
        mtex.normal_factor = 0.010
        mtex.blend_type = "ADD"
        mtex.use_rgb_to_intensity = True
        mtex.color = (1.000, 0.207, 0.000)
#add monkey #
        bpy.ops.mesh.primitive_monkey_add(location = (-0.32639,0.08901,1.49976))
        bpy.ops.transform.rotate(value=(1.15019,), axis=(0, 0, 1))
        bpy.ops.transform.rotate(value=(-0.683882,), axis=(0, 1, 0))
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.ops.object.shade_smooth()
        monkey = bpy.context.active_object
# add new material

        monkeyMaterial = blend_data.materials.new("Monkey_Material")
        bpy.ops.object.material_slot_add()
        monkey.material_slots[0].material = monkeyMaterial

#Material settings
        monkeyMaterial.preview_render_type = "MONKEY"
        monkeyMaterial.diffuse_color = (0.239, 0.288, 0.288)
        monkeyMaterial.specular_color = (0.604, 0.465, 0.136)
        monkeyMaterial.diffuse_shader    = 'LAMBERT' 
        monkeyMaterial.diffuse_intensity = 1.0 
        monkeyMaterial.specular_intensity = 0.3
        monkeyMaterial.ambient = 0
        monkeyMaterial.type = 'SURFACE'
        monkeyMaterial.use_cubic = True
        monkeyMaterial.use_transparency = False
        monkeyMaterial.alpha = 0
        monkeyMaterial.use_transparent_shadows = True
        monkeyMaterial.raytrace_mirror.use = True
        monkeyMaterial.raytrace_mirror.reflect_factor = 0.65
        monkeyMaterial.raytrace_mirror.fade_to = "FADE_TO_MATERIAL"
# add plane

        bpy.ops.mesh.primitive_plane_add(location = (0.0,0.0,-1.0))
        bpy.ops.transform.rotate(value=(-0.820305,), axis=(0, 0, 1))
        bpy.ops.transform.resize(value=(22.0, 22.0, 0.0))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        plane = bpy.context.active_object
# add new material

        planeMaterial = blend_data.materials.new("Plane_Material")
        bpy.ops.object.material_slot_add()
        plane.material_slots[0].material = planeMaterial

            
#Material settings
        planeMaterial.preview_render_type = "CUBE"
        planeMaterial.diffuse_color = (0.2, 0.2, 0.2)
        planeMaterial.specular_color = (0.604, 0.465, 0.136)
        planeMaterial.specular_intensity = 0.3
        planeMaterial.ambient = 0
        planeMaterial.use_cubic = True
        planeMaterial.use_transparency = False
        planeMaterial.alpha = 0
        planeMaterial.use_transparent_shadows = True
        return {"FINISHED"}

class INFO_MT_add_scenesetup(bpy.types.Menu):
    bl_idname = "INFO_MT_objects_ao.add_scene"
    bl_label = "Lighting Setups"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator("objects_ao.add_scene",
            text="Add scene")

#### REGISTER ####
def menu_func(self, context):
    self.layout.menu("INFO_MT_objects_ao.add_scene", icon="PLUGIN")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_add.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_add.remove(menu_func)


if __name__ == '__main__':
    register()