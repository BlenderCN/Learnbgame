import bpy
from . material import get_parallaxgroup_from_decalmat, get_decal_texture_nodes, get_decalgroup_from_decalmat


def toggle_visibility(state, types, debug=False):
    for type in types:

        # hide
        if state:
            if not type.name.startswith("."):
                if debug:
                    print("Hiding %s." % (type.name))
                type.name = ".%s" % type.name

        # unhide
        else:
            if type.name.startswith("."):
                if debug:
                    print("Unhiding %s." % (type.name))
                type.name = type.name[1:]


def toggle_material_visibility(state, debug=False):
    decalmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat]

    toggle_visibility(state, decalmats, debug=debug)


def toggle_texture_visibility(state, debug=False):
    decaltextures = [img for img in bpy.data.images if img.DM.isdecaltex]

    toggle_visibility(state, decaltextures, debug=debug)


def toggle_decaltype_collection_visibility(state, debug=False):
    cols = [col for col in bpy.data.collections if col.DM.isdecaltypecol]

    toggle_visibility(state, cols, debug=debug)


def toggle_decalparent_collection_visibility(state, debug=False):
    cols = [col for col in bpy.data.collections if col.DM.isdecalparentcol]

    toggle_visibility(state, cols, debug=debug)


def toggle_glossyrays(state, debug=False):
    decals = [obj for obj in bpy.data.objects if obj.DM.isdecal]

    for decal in decals:
        if debug:
            print(decal)

        decal.cycles_visibility.glossy = state
        decal.data.update()


def toggle_parallax(state, debug=False):
    decalmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat and mat.DM.decaltype in ["SIMPLE", "SUBSET"]]

    for mat in decalmats:
        if debug:
            print(mat)

        parallaxgroup = get_parallaxgroup_from_decalmat(mat)

        if debug:
            print(parallaxgroup)

        if parallaxgroup:
            parallaxgroup.mute = not state


def toggle_normaltransfer_render(state, debug=False):
    mods = [obj.modifiers.get("NormalTransfer") for obj in bpy.data.objects if obj.DM.isdecal and "NormalTransfer" in obj.modifiers]

    for mod in mods:
        if debug:
            print(mods)

        mod.show_render = state

    bpy.context.evaluated_depsgraph_get()


def toggle_normaltransfer_viewport(state, debug=False):
    mods = [obj.modifiers.get("NormalTransfer") for obj in bpy.data.objects if obj.DM.isdecal and "NormalTransfer" in obj.modifiers]

    for mod in mods:
        if debug:
            print(mods)

        mod.show_viewport = state

    bpy.context.evaluated_depsgraph_get()


def switch_normalinterpolation(state, debug=False):
    decalmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat and mat.DM.decaltype in ["SIMPLE", "SUBSET", "PANEL"]]

    for mat in decalmats:
        if debug:
            print(mat)

        nrmnode = get_decal_texture_nodes(mat)["NRM_ALPHA"]

        if nrmnode:
            nrmnode.interpolation = state


def switch_colorinterpolation(state, debug=False):
    decalmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat and mat.DM.decaltype in ["INFO"]]

    for mat in decalmats:
        if debug:
            print(mat)

        colornode = get_decal_texture_nodes(mat)["COLOR_ALPHA"]

        if colornode:
            colornode.interpolation = state


def switch_alpha_blendmode(state, debug=False):
    decalmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat]

    for mat in decalmats:
        if debug:
            print(mat)

        mat.blend_method = state


def change_ao_strength(state, debug=False):
    decalmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat and mat.DM.decaltype in ["SIMPLE", "SUBSET", "PANEL"]]

    for mat in decalmats:
        if debug:
            print(mat)

        decalgroup = get_decalgroup_from_decalmat(mat)

        if decalgroup:
            ao = decalgroup.inputs["AO Strength"]

            if ao:
                ao.default_value = state


def invert_infodecals(state, debug=False):
    decalmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat and mat.DM.decaltype == "INFO"]

    for mat in decalmats:
        if debug:
            print(mat)

        decalgroup = get_decalgroup_from_decalmat(mat)

        if decalgroup:
            invert = decalgroup.inputs["Invert"]

            if invert:
                invert.default_value = int(state)


def switch_edge_highlights(state, debug=False):
    decalmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat and mat.DM.decaltype in ["SIMPLE", "SUBSET", "PANEL"]]

    for mat in decalmats:
        if debug:
            print(mat)

        decalgroup = get_decalgroup_from_decalmat(mat)

        if decalgroup:
            highlights = decalgroup.inputs["Edge Highlights"]

            if highlights:
                highlights.default_value = float(state)
