"""BlenderFDS, temporary object management."""

import bpy

def del_all_tmp_objects(context):
    """Restore all original obs, delete all tmp objects, select original selected_ob or its parent"""
    if context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    sc = context.scene
    for ob in sc.objects:
        # Restore original object
        if ob.bf_has_tmp: ob.bf_has_tmp, ob.hide = False, False
        # Unlink and delete temporary object
        if ob.bf_is_tmp:
            sc.objects.unlink(ob)
            bpy.data.objects.remove(ob)
            continue

def set_tmp_object(context, ob, ob_tmp):
    """Link ob_tmp as temporary object of ob."""
    # Set original object
    ob.bf_has_tmp = True
    ob.hide = True
    # Set temporary object
    ob_tmp.bf_is_tmp = True
    ob_tmp.active_material = ob.active_material
    ob_tmp.layers = ob.layers
    ob_tmp.show_wire = True
    ob_tmp.select = True
    # Set parenting and keep position
    ob_tmp.parent = ob
    ob_tmp.matrix_parent_inverse = ob.matrix_world.inverted()

