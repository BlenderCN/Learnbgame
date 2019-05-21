# Deeva - Character Generation Platform
# Copyright (C) 2018  Nicolas Erbach, Fabrizio Nunnari
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import bpy
from bpy.path import abspath
from mathutils import Vector

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )


import os
import math


bl_info = {
    "name": "Deeva - Pictures Rendering Tools",
    "description": "Automates import of scripts and generation of pictures from characters for the ManuelbastioniLAB.",
    "author": "Nicolas Erbach",
    "version": (0, 10),
    "blender": (2, 79, 0),
    "location": "Toolbox > ManuelBastioniLAB > Pictures",
    "category": "Characters",
    }

#
# Constants
#
HEAD_CAMERA_ORTHO_SCALE = 1.1
HEAD_CAMERA_ORTHO_DEFAULT = 0.3

#
# Panel
#


class PicturesRenderPanel(bpy.types.Panel):
    # bl_idname = "OBJECT_PT_PictureCreationPanel"
    bl_label = bl_info["name"] + " (v" + (".".join([str(x) for x in bl_info["version"]])) + ")"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = "Deeva"

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        box = row.box()
        box.label(text="Load character files")
        box.prop(context.scene, "conf_path")
        box.operator(LoadScripts.bl_idname)
        
        row = layout.row()
        box = row.box()
        box.label(text="Preview characters")
        box.prop(context.scene, "character_file_list")

        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Camera")
        row.operator(ChangeCamera.bl_idname, text="Head").view = 'head'
        row.operator(ChangeCamera.bl_idname, text="Body").view = 'body'
        
        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Camera Ortho Scale")
        row.prop(context.scene, "check_head_scale")
        row.prop(context.scene, "float_head_scale")

        row = box.row()
        row.alignment = 'EXPAND'
        row.label(text="Face Mask")
        row.prop(context.scene, "check_black_background")
        row.operator(ApplyFaceMaskMaterial.bl_idname)

        row = box.row()
        row.alignment = 'EXPAND'
        row.label(text="Lights")
        row.operator(ReplaceLights.bl_idname, text="Replace Lights")
        
        row = layout.row()
        box = row.box()
        box.label(text="Generate pictures")
        box.prop(context.scene, "check_head_render")
        box.prop(context.scene, "check_body_render")
        box.prop(context.scene, "output_path")

        box.prop(context.scene.render, "resolution_x")
        box.prop(context.scene.render, "resolution_y")

        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.label(text="Render")
        row.operator(CreateOneRender.bl_idname, text="current").file_name = context.scene.character_file_list
        row.operator(CreateAllRender.bl_idname, text="all")
        
        # row = layout.row()
        # box = row.box()
        # box.label(text="Version {}.{}".format(bl_info['version'][0], bl_info['version'][1]))
        

#
# Operators
#


class LoadScripts(bpy.types.Operator):
    """Iterates trough the folder and looks for json files."""
    bl_idname = "mbastauto.load_scripts"
    bl_label = "Load Scripts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        import glob
        
        # clear current list
        del context.scene.character_file_list_items[:]
        
        files = glob.glob(abspath(context.scene.conf_path) + os.path.sep + "*.json")
        # print("List of files: " + str(files))

        # fill list with file names
        for file in files:
            dirname, file = os.path.split(file)
            # print(file)
            # print("enum m", context.scene.character_file_list_items)
            context.scene.character_file_list_items.append((file, file, file))
            
        print("List of retrieved characters: ", context.scene.character_file_list)

        return {'FINISHED'}

    
class ChangeCamera(bpy.types.Operator):
    """Position the camera and set its rendering parameters.
    The position can be the head of the full body of the character"""

    bl_idname = "mbastauto.change_camera"
    bl_label = "Change Camera"

    # Set this at either "head" or "body"
    view = bpy.props.StringProperty()
 
    def execute(self, context):
        scene = context.scene

        if self.view == 'head':
            # get correct skeleton
            # TODO -- take skeleton from selection, not from name.
            skeleton = next(v for k, v in bpy.data.armatures.items() if k.find('skeleton'))
    
            # calculate head position and size
            bone_head_end = skeleton.bones['head'].tail_local
            bone_neck_start = skeleton.bones['neck'].head_local
            head_middle = (bone_head_end + bone_neck_start)/2
            head_length = (bone_head_end - bone_neck_start).length
            
            t = head_middle - Vector([0, 1, 0])  # Moves the camera away from the body
            r = [90, 0, 0]  # the camera must point horizontally
            o = head_length * HEAD_CAMERA_ORTHO_SCALE
            if scene.check_head_scale:
                o = scene.float_head_scale
                
        elif self.view == 'body':
            t = [0, -5, 1.30]
            r = [90, 0, 0]
            o = 2.7
        else:
            assert False
            
        # set camera position (translation)
        scene.camera.location = t
        
        # set camera direction (rotation)
        r = [value * (math.pi/180.0) for value in r]
        scene.camera.rotation_mode = 'XYZ'
        scene.camera.rotation_euler = r
        
        # set camera to ortographic mode and set scale
        scene.camera.data.type = 'ORTHO'
        scene.camera.data.ortho_scale = o
        
        # set render size (to get correct preview)
        # scene.render.resolution_percentage = 100
        
        # render settings
        scene.cycles.samples = 1000
        scene.cycles.sample_clamp_direct = 3
        scene.cycles.sample_clamp_indirect = 3

        return{'FINISHED'}
    
    
class CreateOneRender(bpy.types.Operator):
    """Create render for currently selected character"""
    bl_idname = "mbastauto.create_one_render"
    bl_label = "Render current character"
    bl_options = {'REGISTER'}
    
    file_name = bpy.props.StringProperty()

    def execute(self, context):

        if not context.scene.check_head_render and not context.scene.check_body_render:
            raise Exception("No picture type selected!")
        
        if not context.scene.output_path:
            raise Exception("No output path selected!")
        
        # script_name = context.scene.character_file_list
        script_name = self.file_name
        
        if not self.file_name:
            raise Exception("No character selected!")    
        name = script_name.replace(".json", "")

        # set background transparent
        if context.scene.check_black_background:
            bpy.context.scene.cycles.film_transparent = False
            bpy.context.scene.world.horizon_color = 0, 0, 0
        else:
            bpy.context.scene.cycles.film_transparent = True
            bpy.context.scene.world.horizon_color = 0.050876, 0.050876, 0.050876

            bpy.context.scene.render.alpha_mode = 'TRANSPARENT'

        if context.scene.check_head_render:
            bpy.ops.mbastauto.change_camera(view="head")
            bpy.data.scenes['Scene'].render.filepath = os.path.join(context.scene.output_path,
                                                                    "{}-head.png".format(name))
            bpy.ops.render.render(write_still=True)

        if context.scene.check_body_render:
            bpy.ops.mbastauto.change_camera(view="body")
            bpy.data.scenes['Scene'].render.filepath = os.path.join(context.scene.output_path,
                                                                    "{}-body.png".format(name))
            bpy.ops.render.render(write_still=True)

        return {'FINISHED'}


class CreateAllRender(bpy.types.Operator):
    """Create render for all chracters"""
    bl_idname = "mbastauto.create_all_render"
    bl_label = "Render current character"
    bl_options = {'REGISTER'}
    
    file_name = bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene

        if not context.scene.check_head_render and not context.scene.check_body_render:
            raise Exception("No picture type selected!")
        
        if not context.scene.output_path:
             raise Exception("No output path selected!")
        
        if not bpy.types.Scene.character_file_list_items :
            raise Exception("No characters loaded!") 
           
        print("Rendering all characters...")
        for file_name in bpy.types.Scene.character_file_list_items:
            filepath = os.path.join(context.scene.conf_path, file_name[0])
            filepath = abspath(filepath)
            print("Importing", filepath)
            bpy.ops.mbast.import_character(filepath=filepath)
            print("Rendering", file_name[0])
            bpy.ops.mbastauto.create_one_render(file_name=file_name[0])

        return {'FINISHED'}


#
# MASKING
BLACK_DULL_MATERIAL_PREFIX = "BlackDull"


class ApplyFaceMaskMaterial(bpy.types.Operator):
    """Create a new Dull Black material (if needed) and apply it to all the polygons
    covering the face. The list of polygons is taken from the list of vertices saved in a json file."""
    bl_idname = "mbastauto.apply_face_mask_material"
    bl_label = "Apply Face Mask Material"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        ao = context.active_object
        if ao is not None:
            if ao.type == 'MESH':
                return True

        return False

    def execute(self, context):
        import json

        from deeva import DEEVA_DATA_DIR

        mesh_obj = context.active_object  # type: bpy.types.Object
        mesh = mesh_obj.data  # type: bpy.types.Mesh

        #
        # Load vertices list
        with open(os.path.join(DEEVA_DATA_DIR, "face_mask_vertices.json"), "r") as vertex_list_file:
            vertices = json.load(vertex_list_file)

        print("Loaded {} vertices".format(len(vertices)))

        #
        # Create a black dull material, if not already existing
        black_dull_material = None
        for m in bpy.data.materials:
            if m.name.startswith(BLACK_DULL_MATERIAL_PREFIX):
                black_dull_material = m
                break

        if black_dull_material is None:
            black_dull_material = bpy.data.materials.new(BLACK_DULL_MATERIAL_PREFIX)
            black_dull_material.use_shadeless = True
            black_dull_material.diffuse_color = 0, 0, 0
            print("Generated Material '{}'".format(m.name))
            mesh.materials.append(black_dull_material)

        black_dull_material_index = mesh_obj.material_slots.find(BLACK_DULL_MATERIAL_PREFIX)
        assert black_dull_material != -1

        #
        # For each polygon, check if all vertices belong to the vertex list
        for p in mesh.polygons:  # type: bpy.types.MeshPolygon
            polygon_is_mask = True  # optimistic approach
            for v in p.vertices:
                if v not in vertices:
                    polygon_is_mask = False
                    break

            # If so, apply the dull material
            if polygon_is_mask:
                p.material_index = black_dull_material_index

        return {'FINISHED'}


class ReplaceLights(bpy.types.Operator):
    """Replace all the lights in the scene with optimal lights for face/body rendering."""
    bl_idname = "mbastauto.replace_lights"
    bl_label = "Replace Lights"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        #
        # Remove all lamps in current scene
        for c in bpy.data.lamps:
            print(c.name)
            bpy.data.lamps.remove(c, do_unlink=True)

        #
        # Add lamps
        
        # Create new lamp datablock
        bpy.ops.object.lamp_add(type='SUN')
        sun = bpy.data.lamps["Sun"]  # type: bpy.types.Lamp
        sun.shadow_soft_size = 5
        sun.node_tree.nodes["Emission"].inputs[1].default_value = 5.0
        # sun.location = (-1.96, 1.59, 1.39)
        sun_object = bpy.data.objects['Sun']  # type: bpy.types.Object
        sun_object.rotation_euler = math.radians(30), 0, math.radians(-45)
        
        """
        lamp_data = bpy.data.lamps.new(name="Lamp Back", type='SUN')

        # Create new object with our lamp datablock
        lamp_object = bpy.data.objects.new(name="Lamp Back", object_data=lamp_data)

        # Link lamp object to the scene so it'll appear in this scene
        scene.objects.link(lamp_object)

        # Place lamp to a specified location
        lamp_object.location = (-1.96, 1.59, 1.39)
        lamp_data.energy=15
        
        r = [42, 37, 558]
        r = [value * (pi/180.0) for value in r]
        lamp_object.rotation_mode = 'XYZ'
        lamp_object.rotation_euler = r

        # And finally select it make active
        lamp_object.select = True
        scene.objects.active = lamp_object
        
        bpy.data.scenes['Scene'].render.engine = 'CYCLES'
        bpy.data.worlds['World'].use_nodes = True
        """

        # Create new lamp datablock
        lamp_data = bpy.data.lamps.new(name="Lamp Front", type='HEMI')

        # Create new object with our lamp data block
        lamp_object = bpy.data.objects.new(name="Lamp Front", object_data=lamp_data)

        # Link lamp object to the scene so it'll appear in this scene
        scene.objects.link(lamp_object)

        # Place lamp to a specified location
        lamp_object.location = (0.72, -1.6, 0.86)
        lamp_data.energy = 15
        
        r = [108, 66, 38]
        r = [value * (math.pi/180.0) for value in r]
        lamp_object.rotation_mode = 'XYZ'
        lamp_object.rotation_euler = r

        # And finally select it make active
        lamp_object.select = True
        scene.objects.active = lamp_object

        return {'FINISHED'}


#
# Register & Unregister ###
#

def register():
    # panels
    bpy.utils.register_class(PicturesRenderPanel)
    
    # operators
    bpy.utils.register_class(LoadScripts)
    bpy.utils.register_class(ChangeCamera)
    bpy.utils.register_class(CreateOneRender)
    bpy.utils.register_class(CreateAllRender)
    bpy.utils.register_class(ApplyFaceMaskMaterial)
    bpy.utils.register_class(ReplaceLights)
    
    #
    # variables/props
    bpy.types.Scene.conf_path = bpy.props.StringProperty(
          name="Scripts Path",
          default="",
          description="Define the path where the scripts are located",
          subtype='DIR_PATH'
      )
      
    bpy.types.Scene.character_file_list_items = []
    
    def fill_items(self, context):
        return bpy.types.Scene.character_file_list_items
    
    def change_preview(self, context):
        filepath = os.path.join(context.scene.conf_path, context.scene.character_file_list)
        filepath = abspath(filepath)
        print("Loading MBLab character definitions from {}".format(filepath))
        bpy.ops.mbast.import_character(filepath=filepath)
    
    bpy.types.Scene.character_file_list = bpy.props.EnumProperty(
            items=fill_items,
            name="Character",
            update=change_preview,
        )
        
    bpy.types.Scene.check_head_scale = bpy.props.BoolProperty(name="Manual")
    bpy.types.Scene.float_head_scale = bpy.props.FloatProperty(name="Scale",
                                                               default=HEAD_CAMERA_ORTHO_DEFAULT)
    bpy.types.Scene.check_head_render = bpy.props.BoolProperty(name="head")
    bpy.types.Scene.check_body_render = bpy.props.BoolProperty(name="body")

    bpy.types.Scene.check_black_background = bpy.props.BoolProperty(name="Black Background")

    bpy.types.Scene.output_path = bpy.props.StringProperty(
          name="Images Path",
          default="",
          description="Define the path where the rendered images should be written",
          subtype='DIR_PATH'
      )


def unregister():
    bpy.utils.unregister_class(PicturesRenderPanel)
    bpy.utils.unregister_class(LoadScripts)
    bpy.utils.unregister_class(ChangeCamera)
    bpy.utils.unregister_class(CreateOneRender)
    bpy.utils.unregister_class(CreateAllRender)
    bpy.utils.unregister_class(ApplyFaceMaskMaterial)
    bpy.utils.unregister_class(ReplaceLights)
    del bpy.types.Scene.conf_path
    del bpy.types.Scene.character_file_list 
    del bpy.types.Scene.character_file_list_items
    del bpy.types.Scene.check_head_scale
    del bpy.types.Scene.float_head_scale
    del bpy.types.Scene.check_head_render
    del bpy.types.Scene.check_body_render
    del bpy.types.Scene.check_black_background
    del bpy.types.Scene.output_path


#
# Invoke register if started from editor
if __name__ == "__main__":
    register()
