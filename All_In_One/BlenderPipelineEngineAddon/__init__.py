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

# Contributed to by:
# meta-androcto, Bill Currie, Jorge Hernandez - Melenedez  Jacob Morris, Oscurart  #
# Rebellion, Antonis Karvelas, Eleanor Howick, lijenstina, Daniel Schalla, Domlysz #
# Unnikrishnan(kodemax), Florian Meyer, Omar ahmed, Brian Hinton (Nichod), liero   #
# Atom, Dannyboy, Mano-Wii, Kursad Karatas, teldredge, Phil Cote #

bl_info = {
    "name": "Pipeline Engine Exporter",
    "author": "Nico Forteza",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "description": "Exporter form my personal custom engine",
    "warning": "",
    "category": "Learnbgame",
    }


class ObjectExporter():
    name = ''
    type = 'EMPTY'
    location = (0.0, 0.0, 0.0)
    rotation = (0.0, 0.0, 0.0)
    scale = (1.0, 1.0, 1.0)


import bpy
import os
from math import radians,degrees
from mathutils import Vector, Matrix
import json

ASSETS_RELATIVE_PATH = "data/assets"

class ExporterEnginePathOperator(bpy.types.PropertyGroup):
    path = bpy.props.StringProperty(
        name="Root Engine Directory",
        description="Path to Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

class WrapperObject(bpy.types.PropertyGroup):
     name = bpy.props.StringProperty(name="Test Prop", default="")
     
class AddObjectWaypointOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "exporter.add_waypoint"
    bl_label = "Add waypoint"
    result = {}
    
    def execute(self, context):
        obj = context.active_object
        self.report({'INFO'}, "name: hola")
        if obj.tmp_object_select == None:
            self.report({'INFO'}, "name: None")
        else: 
            self.report({'INFO'}, "name:" + str(obj.is_waypoint))
            not_in = True
            for my_item in obj.waypoint_list:
                if my_item.name == obj.tmp_object_select.name:
                    not_in = False
            if not_in and obj.is_waypoint and obj.tmp_object_select.is_waypoint:
                item = obj.waypoint_list.add()
                item.name = obj.tmp_object_select.name
            obj.tmp_object_select = None
        return {'FINISHED'}
        
class ClearObjectWaypointOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "exporter.clear_waypoint"
    bl_label = "Clear waypoint"
    result = {}
    
    def execute(self, context):
        obj = context.active_object
        obj.waypoint_list.clear()
        return {'FINISHED'}

class Object_UL_matslots_example(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=str(item.name))
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=str(item.name), icon_value=icon)

class UIListPanelExample(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Next Waypoints"
    bl_idname = "OBJECT_PT_ui_list_example"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        
        row = layout.row()
        row.prop(obj, "is_waypoint")
        
        row = layout.row()
        row.prop(obj, "tmp_object_select")
        row.operator('exporter.add_waypoint')
        
        # template_list now takes two new args.
        # The first one is the identifier of the registered UIList to use (if you want only the default list,
        # with no custom draw code, use "UI_UL_list").
        layout.template_list("Object_UL_matslots_example", "", obj, "waypoint_list", obj, "active_waypoint")
        
        row = layout.row()
        row.operator('exporter.clear_waypoint')



class ExporterExportOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "exporter.export"
    bl_label = "Export"
    result = {}

    def execute(self, context):
        scene = context.scene
        self.result = {"scene": context.scene.exporter_scene_name, "directory": ASSETS_RELATIVE_PATH + '/', "geometries": [],
                       "shaders": [{"name": "phong", "vertex": "data/shaders/phong.vert", "fragment": "data/shaders/phong.frag"}],
                       "textures": [], "materials": [], "lights": [{"name": "Light 1","position": [100,100,100],"color": [0.2,0.1,0.4]},
                       {"name": "Light 2","position": [-100,100,-100],"color": [0.2,0.1,0.4]},
                       {"name": "Light 3","position": [10,100,10],"color": [0.5, 0.5, 0.5]}], "waypoints":[],"entities": []}
        entity_objs = [obj for obj in scene.objects if obj.type == 'MESH']
        root_path = os.path.join(context.scene.exporter_root_path.path, ASSETS_RELATIVE_PATH)
        if not os.path.exists(root_path):
            os.makedirs(root_path)

        mesh_path = os.path.join(root_path, 'mesh')
        if not os.path.exists(mesh_path):
            os.makedirs(mesh_path)
        existent_textures = {}
        for entity in entity_objs:
            ent = {}
            ent['name'] = entity.name
            formated_name = entity.name.replace(' ', '_').replace('.', '-')
            # --Export  Transform
            ent['transform'] = {}
            re_loc = entity.location
            re_rot = entity.rotation_euler.copy()
            # re_rot.rotate_axis('X', radians(90))
            ent['transform']['translate'] = [re_loc.x, re_loc.y, re_loc.z]
            ent['transform']['rotate'] = [degrees(re_rot.x), 
                                          degrees(re_rot.y), 
                                          degrees(re_rot.z)]
            ent['transform']['scale'] = [abs(entity.scale.x), abs(entity.scale.y), abs(entity.scale.z)]

            # --Export mesh
            tmp_scale = [entity.scale.x, entity.scale.y, entity.scale.z]
            tmp_rot = [entity.rotation_euler.x, entity.rotation_euler.y, entity.rotation_euler.z]
            tmp_loc = [entity.location.x, entity.location.y, entity.location.z]
            entity.location = [0,0,0]
            entity.rotation_euler = [0,0,0]
            entity.scale = [1, 1, 1]
            bpy.ops.object.select_all(action='DESELECT')
            entity.select_set(True)
            mesh_path = f'mesh/{formated_name}.obj'
            bpy.ops.export_scene.obj(filepath=os.path.join(root_path, mesh_path), use_selection=True, axis_forward='X', axis_up='Z',
                                     use_triangles=True, use_mesh_modifiers=True, use_materials=False, path_mode='ABSOLUTE')
            
            entity.location = tmp_loc
            entity.rotation_euler = tmp_rot
            entity.scale = tmp_scale
            mesh_name = f'{formated_name}-mesh'
            self.result['geometries'].append({"name": mesh_name, "file": mesh_path})
            ent['geometry'] = mesh_name

            # --Export texture
            if not entity.engine_tga:
                entity.engine_tga = scene.exporter_default_tga
            if existent_textures.get(entity.engine_tga, False):
                ent['material'] = existent_textures[entity.engine_tga]
            else:
                material_name = '-'.join(entity.engine_tga.split('.')[:-1])
                self.result['textures'].append({"name": material_name, "file": f'texture/{entity.engine_tga}'})
                self.result['materials'].append({"name": material_name, "shader": "phong", "diffuse_texture": material_name})
                ent['material'] = material_name
                existent_textures[entity.engine_tga] = material_name

           
            ## export Collider
            existing_colliders = [obj_child for obj_child in scene.objects if
                                  obj_child.parent == entity and obj_child.is_collider]
            collider_exists = len(existing_colliders) > 0
            if collider_exists:
                mwi = entity.matrix_world.inverted()
                ent['collider'] = {}
                ent['collider']['type'] = 'Box'
                local_location = mwi @ existing_colliders[0].matrix_world.translation # existing_colliders[0].location #existing_colliders[0].matrix_world @ 
                local_scale = mwi @ existing_colliders[0].matrix_world.to_scale()
                center_collider = [local_location.x, local_location.y, local_location.z]
                ent['collider']['center'] = center_collider
                ent['collider']['halfwidth'] = [abs(local_scale.x),
                                                abs(local_scale.y),
                                                abs(local_scale.z)]

            self.report({'INFO'}, "name:" + str(ent))
            # Add entity
            self.result['entities'].append(ent)
            
        waypoints_objs = [obj for obj in scene.objects if obj.type == 'EMPTY' and obj.is_waypoint]
        waypoints_result = []
        waypont_to_index = {}
        for obj in waypoints_objs:
            waypoints_result.append({"name": obj.name, "position": [obj.location.x, obj.location.y, obj.location.z],"next" : []})
            waypont_to_index[obj.name] = len(waypoints_result) - 1
        for obj in waypoints_objs:
            tmp = waypoints_result[waypont_to_index[obj.name]]
            lis = []
            for my_item in obj.waypoint_list:
                lis.append(waypont_to_index[my_item.name])
            tmp["next"]= lis
            waypoints_result[waypont_to_index[obj.name]] = tmp
        self.result['waypoints'] = waypoints_result
        with open(os.path.join(root_path, f'{self.result["scene"]}.json'), 'w') as fp:
            json.dump(self.result, fp)

        self.report({'INFO'}, "name:" + str(context.scene.exporter_root_path.path))
        return {'FINISHED'}


class CreateColliderOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "exporter.add_collider"
    bl_label = "Add or reasign collider"

    def adjust(self, parent, collider, context):
        bbox = [Vector(v) for v in parent.bound_box]
        collider.location = [bbox[0].x + ((bbox[4].x - bbox[0].x) / 2.0), bbox[0].y + ((bbox[3].y - bbox[0].y) / 2.0),
                             bbox[0].z + ((bbox[1].z - bbox[0].z) / 2.0)]
        collider.scale = [(bbox[4].x - bbox[0].x) / 2.0, (bbox[3].y - bbox[0].y) / 2.0, (bbox[1].z - bbox[0].z) / 2.0]

        self.report({'INFO'}, str([collider.matrix_world @ Vector(v) for v in collider.bound_box]) + " bound")
        self.report({'INFO'}, str([parent.matrix_world @ Vector(v) for v in parent.bound_box]) + " bound")

    def execute(self, context):
        for obj in context.selected_objects:
            existing_colliders = [obj_child for obj_child in context.scene.objects if
                                  obj_child.parent == obj and obj_child.is_collider]
            self.report({'INFO'}, str(existing_colliders) + "already has a child collider")
            already_exists = len(existing_colliders) > 0
            if already_exists:
                self.adjust(obj, existing_colliders[0], context)
                self.report({'WARNING'}, obj.name + " already has a child collider")
                continue
            if obj.type != 'MESH':
                self.report({'ERROR'}, "Only valid mesh objects")
                continue
            bpy.ops.object.empty_add(type='CUBE', location=[0, 0, 0])
            bpy.context.active_object.is_collider = True
            bpy.context.active_object.parent = obj
            bpy.context.active_object.name = "Collider_" + obj.name
            self.adjust(obj, bpy.context.active_object, context)

        return {'FINISHED'}


class ObjectPropertiesPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Custom Properties Engine!"
    bl_idname = "OBJECT_PT_engine_custom"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        row = layout.row()
        row.prop(obj, "engine_tga")

        row = layout.row()
        row.operator('exporter.add_collider')


class ExporterPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Exporter Custom Engine!"
    bl_idname = "SCENE_PT_exporter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        row = layout.row()
        row.prop(scene.exporter_root_path, "path", text="")

        row = layout.row()
        row.prop(scene, "exporter_scene_name")

        row = layout.row()
        row.prop(scene, "exporter_default_tga")

        row = layout.row()
        row.operator('exporter.export')


def register():
    bpy.utils.register_class(Object_UL_matslots_example)
    bpy.utils.register_class(UIListPanelExample)
    bpy.utils.register_class(WrapperObject)
    bpy.utils.register_class(ClearObjectWaypointOperator)
    bpy.utils.register_class(ExporterEnginePathOperator)
    bpy.utils.register_class(ExporterExportOperator)
    bpy.utils.register_class(AddObjectWaypointOperator)
    bpy.utils.register_class(CreateColliderOperator)
    bpy.utils.register_class(ExporterPanel)
    bpy.utils.register_class(ObjectPropertiesPanel)
    bpy.types.Scene.exporter_root_path = bpy.props.PointerProperty(type=ExporterEnginePathOperator)
    bpy.types.Scene.exporter_scene_name = bpy.props.StringProperty(name="Scene name", description="My description",
                                                                   default="myScene")
    bpy.types.Scene.exporter_default_tga = bpy.props.StringProperty(name="Default tga name", description="My description", default="default.tga")
                                                                    
    bpy.types.Object.tmp_object_select = bpy.props.PointerProperty(name="Selectd", type=bpy.types.Object, description="My description")
    bpy.types.Object.active_waypoint = bpy.props.IntProperty(name="index", default=-1)                          
    bpy.types.Object.waypoint_list =  bpy.props.CollectionProperty(type=WrapperObject)                               
    bpy.types.Object.engine_tga = bpy.props.StringProperty(name="Tga name", description="My description",
                                                           default="")
    bpy.types.Object.is_waypoint = bpy.props.BoolProperty(name="Is waypoint", description="My description",
                                                          default=False)
    bpy.types.Object.is_collider = bpy.props.BoolProperty(name="Is collider", description="My description",
                                                          default=False)


def unregister():
    
    bpy.utils.unregister_class(Object_UL_matslots_example)
    bpy.utils.unregister_class(UIListPanelExample)
    bpy.utils.unregister_class(AddObjectWaypointOperator)
    bpy.utils.unregister_class(WrapperObject)
    bpy.utils.unregister_class(ExporterExportOperator)
    bpy.utils.unregister_class(ExporterPanel)
    bpy.utils.unregister_class(ObjectPropertiesPanel)
    bpy.utils.unregister_class(CreateColliderOperator)
    bpy.utils.unregister_class(ExporterEnginePathOperator)
    del bpy.types.Scene.exporter_scene_name
    del bpy.types.Scene.exporter_root_path
    del bpy.types.Scene.exporter_default_tga
    del bpy.types.Object.engine_tga
    del bpy.types.Object.is_collider
    del bpy.types.Object.is_waypoint
    del bpy.types.Object.tmp_object                                                       
    del bpy.types.Object.waypoint_list 


if __name__ == "__main__":
    register()


