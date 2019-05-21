import bpy
import os
import json
from distutils.version import LooseVersion
from .. import M3utils as m3
from .. operators.update_decal_nodes import update_decal_node
from .. utils.asset_loader import match_to_base_material


def get_selection():
    selection = m3.selected_objects()

    if len(selection) >= 2:
        target = m3.get_active()
        selection.remove(target)
        projectors = selection
        return target, projectors
    else:
        return None


def intersect():
    target, sel = get_selection()
    operator = sel[0]

    booleanmod = target.modifiers.new(name="Intersect", type="BOOLEAN")
    booleanmod.object = operator
    booleanmod.operation = "INTERSECT"

    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=booleanmod.name)

    bpy.data.objects.remove(operator, do_unlink=True)


def hide_meshes(silent=True):
        selection = bpy.context.selected_objects
        activeobj = bpy.context.scene.objects.active

        # hide geo
        for obj in selection:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.hide(unselected=False)
            if not silent:
                print("%s geometry hidden." % (obj.name))
            bpy.ops.object.mode_set(mode='OBJECT')

        # reset the active object, to what it was
        bpy.context.scene.objects.active = activeobj
        return activeobj.name


def unlink_render_result():
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            try:  # if it's already None, image.type will throw an exception
                if area.spaces.active.image.type == 'RENDER_RESULT':
                    area.spaces.active.image = None
            except:
                pass


def unlink_any_image():
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            try:
                area.spaces.active.image = None
            except:
                pass


def append_paneling_material(panelingname):
    if panelingname.startswith("c_"):
        path = bpy.context.user_preferences.addons['DECALmachine'].preferences.customassetpath
    else:
        path = bpy.context.user_preferences.addons['DECALmachine'].preferences.assetpath

    panelpath = "paneling01/blends/%s/Material" % (panelingname + ".blend")
    fullpath = os.path.join(path, panelpath)
    bpy.ops.wm.append(directory=fullpath, filename=panelingname)

    decalmat = bpy.data.materials.get(panelingname)

    # update old decal node group to support the principled pbr shader
    if bpy.app.version >= (2, 79, 0):
        lastnode = decalmat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node
        update_decal_node(decalmat, lastnode)

    if m3.DM_prefs().autobasematerial:
        decalgroup = decalmat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node
        match_to_base_material(decalgroup)

    return decalmat


def load_json(pathstring):
    with open(pathstring, 'r') as f:
        jsondict = json.load(f)
    return jsondict


def save_json(jsondict, pathstring):
    try:
        with open(pathstring, 'w') as f:
            json.dump(jsondict, f, indent=4)
    except PermissionError:
        import traceback
        print()
        traceback.print_exc()

        print(80 * "-")
        print()
        print(" ! FOLLOW THE INSTALLATION INSTRUCTIONS ! ")
        print()
        print("You are not supposed to put DECALmachine into C:\Program Files\Blender Foundation\... etc.")
        print()
        print("https://machin3.io/DECALmachine/docs/installation/")
        print()
        print(80 * "-")


def makedir(pathstring):
    if not os.path.exists(pathstring):
        os.makedirs(pathstring)
    return pathstring


def delete_all(silent=True, keep=None):
    m3.show_all_layers()
    m3.unselect_all("OBJECT")
    m3.unhide_all()

    for obj in bpy.data.objects:
        if keep is None:
            obj.select = True
        else:
            if obj not in keep:
                obj.select = True

    bpy.ops.object.delete(use_global=False)
    if not silent:
        print("Removed all objects.")

    for group in bpy.data.groups:
        bpy.data.groups.remove(group, do_unlink=True)

    if not silent:
        print("Removed all groups.")

    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat, do_unlink=True)

    if not silent:
        print("Removed all materials.")

    for group in bpy.data.node_groups:
        bpy.data.node_groups.remove(group, do_unlink=True)

    if not silent:
        print("Removed all node groups.")

    for img in bpy.data.images:
        bpy.data.images.remove(img, do_unlink=True)

    if not silent:
        print("Removed all images.")
