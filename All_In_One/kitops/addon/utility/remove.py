import bpy

def object(object, data=False):
    if data:
        object_data(object)

    try:
        bpy.data.objects.remove(object, do_unlink=True, do_id_user=True, do_ui_user=True)
    except: pass

def object_data(object):
    try:
        if object.data:
            if object.type == 'MESH':
                bpy.data.meshes.remove(object.data, do_unlink=True, do_id_user=True, do_ui_user=True)
            elif object.type not in {'FONT', 'META', 'SURFACE', 'CURVE'}:
                getattr(bpy.data, '{}s'.format(object.type.lower())).remove(object.data, do_unlink=True, do_id_user=True, do_ui_user=True)

            elif object.type in {'FONT', 'SURFACE', 'CURVE'}:
                bpy.data.curves.remove(object.data, do_unlink=True, do_id_user=True, do_ui_user=True)

            else:
                bpy.data.metaballs.remove(object.data, do_unlink=True, do_id_user=True, do_ui_user=True)
    except: pass
