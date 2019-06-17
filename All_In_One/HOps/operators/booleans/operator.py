import bpy
from ... utils.objects import set_active, get_current_selected_status
from ... material import assign_material
from ... preferences import get_preferences
from ... utility import collections, modifier
from ... utility.renderer import cycles


def boolean(context, boolean_method='DIFFERENCE', collection='Cutters'):
    active_object, other_objects, other_object = get_current_selected_status()
    if not other_objects:
        assign_material(context, other_object)

    if get_preferences().workflow == "NONDESTRUCTIVE":
        for obj in other_objects:
            for f in obj.data.polygons:
                f.use_smooth = True

    for obj in other_objects:
        assign_material(context, obj)
        obj.display_type = 'WIRE'
        obj.hops.status = "BOOLSHAPE"

        data = obj.data
        data.use_customdata_edge_bevel = True

        collections.unlink_obj(context, obj)
        collections.link_obj(context, obj, collection)

        obj.hide_render = True
        cycles.hide_preview(context, obj)

        boolean = active_object.modifiers.new("Boolean", "BOOLEAN")
        boolean.operation = boolean_method
        boolean.show_expanded = False
        boolean.object = obj

    if get_preferences().workflow == "DESTRUCTIVE":
        set_active(active_object, select=True, only_select=True)
        modifier.apply(active_object, type=["BOOLEAN"])
        for obj in other_objects:
            bpy.data.objects.remove(obj, do_unlink=True)

    elif get_preferences().workflow == "NONDESTRUCTIVE":
        # if active_object.hops.status != "CSTEP":
        modifier.sort(context, active_object)
        set_active(other_objects[0], select=True, only_select=True)
