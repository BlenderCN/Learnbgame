import bpy
import bmesh
import os
import sys
import platform
import subprocess


def clear():
    os.system("clear")


def get_active():
    return bpy.context.active_object


def make_active(obj):
    bpy.context.view_layer.objects.active = obj
    return obj


def selected_objects():
    return bpy.context.selected_objects


def select_all(string):
    if string == "MESH":
        bpy.ops.mesh.select_all(action='SELECT')
    elif string == "OBJECT":
        bpy.ops.object.select_all(action='SELECT')


def unselect_all(string):
    if string == "MESH":
        bpy.ops.mesh.select_all(action='DESELECT')
    elif string == "OBJECT":
        bpy.ops.object.select_all(action='DESELECT')


def select(objlist):
    for obj in objlist:
        obj.select = True


def hide_all(string):
    if string == "OBJECT":
        select_all(string)
        bpy.ops.object.hide_view_set(unselected=False)
    elif string == "MESH":
        select_all(string)
        bpy.ops.mesh.hide(unselected=False)


def unhide_all(string="OBJECT"):
    if string == "OBJECT":
        for obj in bpy.data.objects:
            obj.hide = False
    elif string == "MESH":
        bpy.ops.mesh.reveal()


def get_mode():
    mode = bpy.context.mode

    if mode == "OBJECT":
        return "OBJECT"
    elif mode == "EDIT_MESH":
        return get_mesh_select_mode()


def get_mesh_select_mode():
    mode = tuple(bpy.context.scene.tool_settings.mesh_select_mode)
    if mode == (True, False, False):
        return "VERT"
    elif mode == (False, True, False):
        return "EDGE"
    elif mode == (False, False, True):
        return "FACE"
    else:
        return None


def set_mode(string, extend=False, expand=False):
    if string == "EDIT":
        bpy.ops.object.mode_set(mode='EDIT')
    elif string == "OBJECT":
        bpy.ops.object.mode_set(mode='OBJECT')
    elif string in ["VERT", "EDGE", "FACE"]:
        bpy.ops.mesh.select_mode(use_extend=extend, use_expand=expand, type=string)



def change_context(string):
    area = bpy.context.area

    print("area:", area)

    old_type = area.type

    print("old type before:", old_type)

    area.type = string

    print("old type after:", old_type)

    return old_type


def change_pivot(string):
    space_data = bpy.context.space_data
    old_type = space_data.pivot_point
    space_data.pivot_point = string
    return old_type


def DM_check():
    return addon_check("DECALmachine")


def MM_check():
    return addon_check("MESHmachine")


def RM_check():
    return addon_check("RIGmachine")


def HOps_check():
    return addon_check("HOps")


def BC_check():
    return addon_check("BoxCutter")


def AM_check():
    return addon_check("asset_management", precise=False)


def GP_check():
    return addon_check("GroupPro")


def addon_check(string, precise=True):
    for addon in bpy.context.preferences.addons.keys():
        if precise:
            if string == addon:
                return True
        else:
            if string.lower() in addon.lower():
                return True
    return False


def move_to_cursor(obj, scene):
    obj.select = True
    make_active(obj)
    obj.location = bpy.context.scene.cursor.location


def lock(obj, location=True, rotation=True, scale=True):
    if location:
        for idx, _ in enumerate(obj.lock_location):
            obj.lock_location[idx] = True

    if rotation:
        for idx, _ in enumerate(obj.lock_rotation):
            obj.lock_rotation[idx] = True

    if scale:
        for idx, _ in enumerate(obj.lock_scale):
            obj.lock_scale[idx] = True


def open_folder(pathstring):

    if platform.system() == "Windows":
        os.startfile(pathstring)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", pathstring])
    else:
        # subprocess.Popen(["xdg-open", pathstring])
        os.system('xdg-open "%s" %s &' % (pathstring, "> /dev/null 2> /dev/null"))  # > sends stdout,  2> sends stderr


def makedir(pathstring):
    if not os.path.exists(pathstring):
        os.makedirs(pathstring)
    return pathstring


def addon_prefs(addonstring):
    return bpy.context.preferences.addons[addonstring].preferences


def DM_prefs():
    return bpy.context.preferences.addons["DECALmachine"].preferences


def MM_prefs():
    return bpy.context.preferences.addons["MESHmachine"].preferences


def RM_prefs():
    return bpy.context.preferences.addons["RIGmachine"].preferences


def M3_prefs():
    return bpy.context.preferences.addons["MACHIN3tools"].preferences


def make_selection(string, idlist):
    mesh = bpy.context.object.data
    set_mode("OBJECT")
    if string == "VERT":
        for v in idlist:
            mesh.vertices[v].select = True
    elif string == "EDGE":
        for e in idlist:
            mesh.edges[e].select = True
    elif string == "FACE":
        for p in idlist:
            mesh.polygons[p].select = True
    set_mode("EDIT")


def get_selection(string):
    active = bpy.context.active_object
    active.update_from_editmode()

    if string == "VERT":
        return [v.index for v in active.data.vertices if v.select]
    if string == "EDGE":
        return [e.index for e in active.data.edges if e.select]
    if string == "FACE":
        return [f.index for f in active.data.polygons if f.select]


def get_selection_history():
    mesh = bpy.context.object.data
    bm = bmesh.from_edit_mesh(mesh)
    vertlist = [elem.index for elem in bm.select_history if isinstance(elem, bmesh.types.BMVert)]
    return vertlist


def get_scene_scale():
    return bpy.context.scene.unit_settings.scale_length


def lerp(value1, value2, amount):
    if 0 <= amount <= 1:
        return (amount * value2) + ((1 - amount) * value1)
