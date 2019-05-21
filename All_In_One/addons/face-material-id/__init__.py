import bpy
from .face_material_id_ui import *


bl_info = {
    "name": "Face Material Id",
    "description": "Face Material Id",
    "category": "Mesh",
    "author": "Cube"
}


def register():
    bpy.utils.register_class(SaveFaceMaterialIdOperator)
    bpy.utils.register_class(LoadFaceMaterialIdOperator)
    bpy.utils.register_class(FaceMaterialIdPanel)


def unregister():
    bpy.utils.unregister_class(SaveFaceMaterialIdOperator)
    bpy.utils.unregister_class(LoadFaceMaterialIdOperator)
    bpy.utils.unregister_class(FaceMaterialIdPanel)
