import bpy


def meshes_in_selection():
    return [o for o in bpy.context.selected_objects if o.type == 'MESH']


def meshes_without_uv():
    objects_list = meshes_in_selection()
    objects_without_uv = []
    for obj in objects_list:
        if obj.data.uv_textures:
            continue
        if not obj.data.uv_textures:
            objects_without_uv.append(obj)
    return objects_without_uv


def meshes_with_materials():
    objects_list = meshes_in_selection()
    objects_with_mtl = []
    for obj in objects_list:
        if not obj.data.materials:
            continue
        objects_with_mtl.append(obj)
    return objects_with_mtl


def meshes_without_materials():
    objects_list = meshes_in_selection()
    objects_without_mtl = []
    for obj in objects_list:
        if not obj.data.materials:
            objects_without_mtl.append(obj)
    return objects_without_mtl


def make_object_active(self, context):
    context.scene.objects.active = bpy.data.objects[str(self.mesh_to_select)]
    return{'FINISHED'}
