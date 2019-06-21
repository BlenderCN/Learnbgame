"""
Classes managing the ogre tools from blender 2.5
"""

import os
import uuid
import io_export_ogreDotScene as addon_ogreDotScene
from b2rexpkg.tools import uuidexport

ogre_mesh_entity_helper = addon_ogreDotScene.INFO_OT_createOgreExport._node_export
ogre_material_export = addon_ogreDotScene.INFO_OT_createOgreExport.gen_dot_material

def get_uuid_str(ob):
    if not ob.opensim.uuid:
        ob.opensim.uuid = str(uuid.uuid4())
    return str(ob.opensim.uuid)

def image_tagger(im):
    uuid_str = get_uuid_str(im)
    name = os.path.basename(im.filepath)
    uuidexport.uuidexporter.add('textures', 'texture', name, uuid_str)

def meshobj_tagger(self, ob, *args, **kwargs):
    print(" * object: "+ob.name)
    uuid_str = get_uuid_str(ob)
    uuidexport.uuidexporter.add('objects', 'object', ob.name, uuid_str)
    if ob.type == 'MESH' and ob.data:
        mesh = ob.data
        uuid_str = get_uuid_str(mesh)
        uuidexport.uuidexporter.add('meshes', 'mesh', ob.name, uuid_str)
        for uv_layer in mesh.uv_textures:
            for face in uv_layer.data:
                if face.image:
                    image_tagger(face.image)
    return ogre_mesh_entity_helper(self, ob, *args, **kwargs)

def material_tagger(self, mat, path='/tmp', convert_textures=False):
    print(" * material:"+mat.name)
    uuid_str = get_uuid_str(mat)
    uuidexport.uuidexporter.add('materials', 'material', mat.name, uuid_str)
    for slot in mat.texture_slots:
        if slot and slot.texture and slot.texture.type == 'IMAGE' and slot.texture.image:
            image_tagger(slot.texture.image)
    return ogre_material_export(mat, path=path, convert_textures=convert_textures)

addon_ogreDotScene.INFO_OT_createOgreExport._node_export = meshobj_tagger
addon_ogreDotScene.INFO_OT_createOgreExport.gen_dot_material = material_tagger


