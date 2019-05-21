bl_info = {
    "name": "Clairvoyance JSON Exporter",
    "author": "Mihai Damian",
    "blender": (2, 5, 8),
    "api": 38019,
    "location": "File > Import-Export",
    "description": "Export to JSON Format",
    "warning": "",
    "wiki_url": "https://github.com/MihaiDamian/Clairvoyance",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Learnbgame"
}

if "bpy" in locals():
    from imp import reload
    if "ClairvoyanceJSON" in locals():
        reload(ClairvoyanceJSON)

import json

import bpy
from bpy.props import BoolProperty
from bpy_extras.io_utils import ExportHelper


class ClairvoyanceJSON:
    string = ""
    prettyprint = False

    def __init__(self, prettyprint):
        self.prettyprint = prettyprint

    def rel_path_from_blender_path(self, path):
        #blender prefixes relative paths with '//'
        return path.strip('/')

    def obj(self, obj_data):
        obj = {}
        obj['name'] = obj_data.name
        obj['location'] = list(obj_data.location)
        
        rotation_mode = obj_data.rotation_mode
        obj_data.rotation_mode = 'QUATERNION'
        #transform from WXYZ to XYZW
        rotation = list(obj_data.rotation_quaternion)[1:4]
        rotation.append(obj_data.rotation_quaternion[0])
        obj['rotation'] = rotation
        obj_data.rotation_mode = rotation_mode
        
        return obj

    def material(self, material_data):
        material = {}
        texture_data = material_data.active_texture
        if texture_data != None and texture_data.type != 'NONE':
            texture = {}
            if texture_data.type == 'IMAGE':
                texture_path = texture_data.image.filepath
                normalized_path = self.rel_path_from_blender_path(texture_path)
                texture['path'] = normalized_path
            material['texture'] = texture
        material['name'] = material_data.name
        return material

    def mesh(self, mesh_data):
        mesh = {}

        materials = []
        for material_data in mesh_data.materials:
            material = self.material(material_data)
            materials.append(material)
        mesh['materials'] = materials

        mesh_is_textured = len(mesh_data.uv_textures) > 0

        faces = []
        if mesh_is_textured:
            uv_texture_layer = mesh_data.uv_textures[0]
        for face_index, face_data in enumerate(mesh_data.faces):
            face = {}
            if mesh_is_textured:
                texture_face = uv_texture_layer.data[face_index]
                face['uv_coords'] = texture_face.uv_raw[:6]
            face['vertex_indices'] = list(face_data.vertices)
            face['material_index'] = face_data.material_index
            faces.append(face)
        mesh['faces'] = faces

        vertices = []
        for vertex in mesh_data.vertices:
            vertices += list(vertex.co)
        mesh['vertices'] = vertices
        
        return mesh

    def camera(self, camera_data):
        camera = {}
        camera['clipStart'] = camera_data.clip_start
        camera['clipEnd'] = camera_data.clip_end
        camera['fov'] = camera_data.angle
        return camera
    
    def create(self):
        data = {}
        data['meshes'] = []
        data['cameras'] = []

        bpy.ops.object.mode_set(mode='OBJECT')

        #TODO: find a way to identify the actual active scene
        active_scene = bpy.data.scenes[0]

        for scene_object in active_scene.objects:
            obj = self.obj(scene_object)
            obj_data = scene_object.data
            if scene_object.type == 'MESH':
                obj.update(self.mesh(obj_data))
                data['meshes'].append(obj)
            elif scene_object.type == 'CAMERA':
                obj.update(self.camera(obj_data))
                data['cameras'].append(obj)
        
        if self.prettyprint:
            self.string = json.dumps(data, sort_keys=True, indent=4)
        else:
            self.string = json.dumps(data, separators=(',', ':'))


class ExportJSON(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.json"
    bl_label = "Export Clairvoyance JSON"

    filename_ext = ".js"

    prettyprint = BoolProperty(name="Prettyprint",
                               description="Nicely indented JSON",
                               default=False)
 
    def execute(self, context):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)
        json = ClairvoyanceJSON(self.prettyprint)
        json.create()
        content = json.string
        self.save_file(filepath, content)
        return {'FINISHED'}

    def save_file(self, filepath, content):
        with open(filepath, 'wb') as file:
            file.write(content.encode('utf-8'))

def menu_func_export(self, context):
    self.layout.operator(ExportJSON.bl_idname, text="Clairvoyance JSON (.js)")
 
def register():
    bpy.utils.register_class(ExportJSON)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
 
def unregister():
    bpy.utils.unregister_class(ExportJSON)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

