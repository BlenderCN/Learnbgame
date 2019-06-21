"""
    Some ugly hooks to override behaviour from the ogre exporter.
"""

from collections import defaultdict

import ogredotscene
import ogremeshesexporter
from ogrepkg.base import PathName
import ogrepkg.meshexport
import ogrepkg.materialexport
import uuid
import Blender.Material
from b2rexpkg.tools import uuidexport


obj_export = ogredotscene.ObjectExporter.export
mesh_export = ogremeshesexporter.MeshExporter.export
mat_export = ogrepkg.materialexport.DefaultMaterial.write
tex_export = ogrepkg.materialexport.MaterialManager.registerTextureImage

def my_obj_export(*args):
    obj = args[0]
    bobj = obj.getBlenderObject()
    name = bobj.getName()
    if not 'opensim' in bobj.properties:
        bobj.properties['opensim'] = {}
    if not 'uuid' in bobj.properties['opensim']:
        bobj.properties['opensim']['uuid'] = str(uuid.uuid4())
    uuid_str = bobj.properties['opensim']['uuid']
    uuidexport.uuidexporter.add('objects', 'object', name, uuid_str)
    print " * exporting obj", name, uuid_str, bobj
    sceneExporter = args[1]
    return obj_export(*args)

def my_tex_export(*args):
    materialmanager = args[0]
    bobj = args[1] # blender image
    path = bobj.filename
    texturePath = PathName(path)
    name = texturePath.basename()
    #name = bobj.getName()
    if not 'opensim' in bobj.properties:
        bobj.properties['opensim'] = {}
    if not 'uuid' in bobj.properties['opensim']:
        bobj.properties['opensim']['uuid'] = str(uuid.uuid4())
    uuid_str = bobj.properties['opensim']['uuid']
    uuidexport.uuidexporter.add('textures', 'texture', name, uuid_str)
    print " * exporting tex", name, uuid_str, bobj
    return tex_export(*args)


def my_mat_export(*args):
    obj = args[0]
    try:
	    bobj = obj.material
    except:
	    return mat_export(*args)
    name = obj._createName()
    if not bobj:
        uuid_str = str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
        uuidexport.uuidexporter.add('materials', 'material', name, uuid_str)
        return mat_export(*args)
    if not 'opensim' in bobj.properties:
        bobj.properties['opensim'] = {}
    if not 'uuid' in bobj.properties['opensim']:
        bobj.properties['opensim']['uuid'] = str(uuid.uuid4())
    uuid_str = bobj.properties['opensim']['uuid']
    uuid_str = str(uuid.uuid5(uuid.UUID(uuid_str), name))
    uuidexport.uuidexporter.add('materials', 'material', name, uuid_str)
    print " * exporting material", name, uuid_str, bobj
    sceneExporter = args[1]
    return mat_export(*args)

def my_mesh_export(*args):
    obj = args[0]
    bobj = obj.getObject().getData(0, True)
    name = obj.getName()
    if not 'opensim' in bobj.properties:
        bobj.properties['opensim'] = {}
    if not 'uuid' in bobj.properties['opensim']:
        bobj.properties['opensim']['uuid'] = str(uuid.uuid4())
    uuid_str = bobj.properties['opensim']['uuid']
    uuidexport.uuidexporter.add('meshes' ,'mesh', name, uuid_str)
    print " * exporting mesh", name, uuid_str, bobj
    sceneExporter = args[1]
    return mesh_export(*args)

ogredotscene.ObjectExporter.export = my_obj_export
ogremeshesexporter.MeshExporter.export = my_mesh_export
ogrepkg.materialexport.DefaultMaterial.write = my_mat_export
ogrepkg.materialexport.MaterialManager.registerTextureImage = my_tex_export


