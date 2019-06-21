import bpy
import os
from . registration import get_prefs
from . append import append_material
from . system import abspath


def get_decalmat(obj):
    mat = obj.active_material
    if mat and mat.DM.isdecalmat:
        return mat


def remove_decalmat(decalmat, remove_textures=False, legacy=False, debug=False):
    if debug:
        print("\n%s, users: %d" % (decalmat.name, decalmat.users))

    dg = get_decalgroup_from_decalmat(decalmat)
    pg = get_parallaxgroup_from_decalmat(decalmat)

    if dg:
        if debug:
            print("decalgroup users:", dg.node_tree.users)

        if dg.node_tree.users == 1:
            if debug:
                print("Removing decalgroup '%s'." % (dg.name))

            bpy.data.node_groups.remove(dg.node_tree, do_unlink=True)

    if pg:
        if debug:
            print("parallaxgroup users:", pg.node_tree.users)

        hg = get_heightgroup_from_parallaxgroup(pg)

        if pg.node_tree.users == 1:
            if debug:
                print("Removing heightgroup '%s'." % (hg.name))

            bpy.data.node_groups.remove(hg.node_tree, do_unlink=True)

            if debug:
                print("Removing parallaxgroup '%s'." % (pg.name))

            bpy.data.node_groups.remove(pg.node_tree, do_unlink=True)

    if remove_textures:
        textures = get_decal_textures(decalmat, legacy=legacy)

        for img in textures.values():
            bpy.data.images.remove(img, do_unlink=True)

    if debug:
        print("Removing material '%s'" % (decalmat.name))

    bpy.data.materials.remove(decalmat, do_unlink=True)


# DECAL GROUP

def get_decalgroup_from_decalmat(decalmat):
    output = decalmat.node_tree.nodes.get('Material Output')

    if output:
        links = output.inputs['Surface'].links
        if links:
            nodegroup = links[0].from_node

            return nodegroup


def get_decalgroup_from_decalobj(decalobj):
    decalmat = get_decalmat(decalobj)

    if decalmat:
        return get_decalgroup_from_decalmat(decalmat)


# PARALLAX GROUP

def get_parallaxgroup_from_decalmat(decalmat):
    if decalmat.DM.parallaxnodename:
        nodegroup = decalmat.node_tree.nodes.get(decalmat.DM.parallaxnodename)

        if nodegroup:
            return nodegroup

    for node in decalmat.node_tree.nodes:
        if node.type == "GROUP":
            if node.node_tree:
                if node.node_tree.name.startswith("parallax"):
                    return node


def get_parallaxgroup_from_decalobj(decalobj):
    decalmat = get_decalmat(decalobj)

    if decalmat:
        return get_parallaxgroup_from_decalmat(decalmat)


# HEIGHT GROUP

def get_heightgroup_from_parallaxgroup(parallaxgroup, getall=False):
    tree = parallaxgroup.node_tree

    heightgroups = []

    for node in tree.nodes:
        if node.type == "GROUP":
                heightgroups.append(node)

    heightgroups.sort(key=lambda x: x.name)

    return heightgroups if getall else heightgroups[0] if heightgroups else None


def get_heightgroup_from_decalmat(decalmat, getall=False):
    parallaxgroup = get_parallaxgroup_from_decalmat(decalmat)

    if parallaxgroup:
        return get_heightgroup_from_parallaxgroup(parallaxgroup, getall)


def get_heightgroup_from_decalobj(decalobj, getall=False):
    decalmat = get_decalmat(decalobj)

    if decalmat:
        return get_heightgroup_from_decalmat(decalmat)


# DECAL TEXTURES, NOTE: relies on texture names to determine type, to be compliant with legacy decals, TODO: in future replace with decaltextype prop

def get_decal_textures(decalmat, legacy=False):
    textures = {}

    for node in decalmat.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            cond = node.image if legacy else node.image and node.image.DM.isdecaltex

            if cond:
                if node.image.filepath.endswith("ao_curv_height.png"):
                    textures["AO_CURV_HEIGHT"] = node.image

                elif node.image.filepath.endswith("nrm_alpha.png"):
                    textures["NRM_ALPHA"] = node.image

                elif node.image.filepath.endswith("masks.png") or (legacy and (node.image.filepath.endswith("subset.png") or node.image.filepath.endswith("mat2_alpha.png"))):
                    textures["MASKS"] = node.image

                elif node.image.filepath.endswith("color_alpha.png") or legacy:
                    textures["COLOR_ALPHA"] = node.image


            # TODO, in future do this
            # texturedict[node.image.DM.decaltextype] = node.image

    return textures


def get_decal_texture_nodes(decalmat, legacy=False, height=False):
    nodes = {}

    for node in decalmat.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            cond = node.image if legacy else node.image and node.image.DM.isdecaltex

            if cond:
                if node.image.filepath.endswith("ao_curv_height.png"):
                    nodes["AO_CURV_HEIGHT"] = node

                elif node.image.filepath.endswith("nrm_alpha.png"):
                    nodes["NRM_ALPHA"] = node

                elif node.image.filepath.endswith("masks.png"):
                    nodes["MASKS"] = node

                elif node.image.filepath.endswith("color_alpha.png"):
                    nodes["COLOR_ALPHA"] = node

    if height:
        heightgroup = get_heightgroup_from_decalmat(decalmat)

        if heightgroup:
            for node in heightgroup.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    nodes["HEIGHT"] = node
                    break
    return nodes


def set_decal_textures(decalmat, textures, height=False):
    for node in decalmat.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            if node.image:
                if node.image.filepath.endswith("ao_curv_height.png"):
                    decaltextype = "AO_CURV_HEIGHT"

                elif node.image.filepath.endswith("nrm_alpha.png"):
                    decaltextype = "NRM_ALPHA"

                elif node.image.filepath.endswith("masks.png"):
                    decaltextype = "MASKS"

                elif node.image.filepath.endswith("color_alpha.png"):
                    decaltextype = "COLOR_ALPHA"

                bpy.data.images.remove(node.image, do_unlink=True)

                node.image = textures[decaltextype]


    if height:
        heightgroup = get_heightgroup_from_decalmat(decalmat)

        if heightgroup:
            for node in heightgroup.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    node.image = textures["AO_CURV_HEIGHT"]
                    break


# PBR NODE

def get_pbrnode_from_mat(mat):
    output = mat.node_tree.nodes.get('Material Output')

    if output:
        links = output.inputs['Surface'].links

        if links:
            lastnode = links[0].from_node


            if lastnode.type == "BSDF_PRINCIPLED":
                return lastnode

            elif lastnode.type == "GROUP":
                return get_pbrnode_from_group(lastnode)


def get_pbrnode_from_group(group):
    output = group.node_tree.nodes.get('Group Output')

    if output:
        bsdf = output.inputs.get('BSDF')

        if bsdf and bsdf.links:
            lastnode = bsdf.links[0].from_node

            if lastnode.type == "BSDF_PRINCIPLED":
                return lastnode


# DEDUPLICATION

def deduplicate_material(decalmat):
    # find existing materials of the same type
    existingmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat and mat != decalmat and mat.DM.uuid == decalmat.DM.uuid]

    if existingmats:
        unmatched = [mat for mat in existingmats if not mat.DM.ismatched]
        matched = [mat for mat in existingmats if mat.DM.ismatched]

        # if there is an unmatched material among the existing ones, apply that and remove the new decal material, its node trees and its textures
        if unmatched:
            existingmat = sorted(unmatched, key=lambda x: x.name)[0]

            # remove all the imported, now duplicate texture images
            for img in get_decal_textures(decalmat).values():
                bpy.data.images.remove(img, do_unlink=True)

            # remove the decalmats node tree's
            decalgroup = get_decalgroup_from_decalmat(decalmat)
            if decalgroup:
                bpy.data.node_groups.remove(decalgroup.node_tree, do_unlink=True)

            # if decalobj.DM.decaltype in ["SIMPLE", "SUBSET"]:
            if decalmat.DM.decaltype in ["SIMPLE", "SUBSET"]:
                heightgroup = get_heightgroup_from_decalmat(decalmat)

                if heightgroup:
                    bpy.data.node_groups.remove(heightgroup.node_tree, do_unlink=True)

                parallaxgroup = get_parallaxgroup_from_decalmat(decalmat)
                if parallaxgroup:
                    bpy.data.node_groups.remove(parallaxgroup.node_tree, do_unlink=True)

            # remove the imported, duplicate material
            bpy.data.materials.remove(decalmat, do_unlink=True)

            return existingmat


        # if there are only matched ones, keep the decalmat, but replace and remove it's node trees and textures
        elif matched:
            existingmat = sorted(matched, key=lambda x: x.name)[0]

            textures = get_decal_textures(existingmat)

            # set textures, no need for height, as we will replace the entire parallax tree instead
            if textures:
                set_decal_textures(decalmat, textures, height=False)

            # replace the decal node tree and remove the old one
            existingdecalgroup = get_decalgroup_from_decalmat(existingmat)
            newdecalgroup = get_decalgroup_from_decalmat(decalmat)

            if existingdecalgroup and newdecalgroup:
                # NOTE, removing the old tree first, would disconnect the node group
                decal_tree = newdecalgroup.node_tree
                newdecalgroup.node_tree = existingdecalgroup.node_tree
                bpy.data.node_groups.remove(decal_tree, do_unlink=True)


            # for the parallax and height trees, first get and remove the height group tree
            # if decalobj.DM.decaltype in ["SIMPLE", "SUBSET"]:
            if decalmat.DM.decaltype in ["SIMPLE", "SUBSET"]:
                heightgroup = get_heightgroup_from_decalmat(decalmat)
                if heightgroup:
                    bpy.data.node_groups.remove(heightgroup.node_tree, do_unlink=True)

                # then replace the parallax group tree and remove the new one
                existingparallaxgroup = get_parallaxgroup_from_decalmat(existingmat)
                newparallaxgroup = get_parallaxgroup_from_decalmat(decalmat)

                if existingparallaxgroup and newparallaxgroup:
                    parallax_tree = newparallaxgroup.node_tree
                    newparallaxgroup.node_tree = existingparallaxgroup.node_tree
                    bpy.data.node_groups.remove(parallax_tree, do_unlink=True)

    # without any existing materials, the decalmat is kept, but the texture paths will be made absolute
    else:
        for textype, img in get_decal_textures(decalmat).items():
            img.filepath = abspath(img.filepath)

    return decalmat


# PANEL DECAL MATERIAL

def get_panel_material(uuid):
    panelmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat and mat.DM.uuid == uuid and not mat.DM.ismatched]

    # apply unmatched material of "current panel decal", if one can be found
    if panelmats:
        mat = panelmats[0]

        return mat, False, None, None

    # otherwise determine the path and append the material from the "current panel decal"
    else:
        # NOTE. this could be done using the decaluuids dict in context.winow_mananger, and it would be more compact as well
        # ####: however, I think it's better to keep this self-contained and just use the paneldecals enum items. timing seems to be identical
        paneldecalitems = bpy.types.WindowManager.paneldecals[1]['items']

        for puuid, name, library in paneldecalitems:
            if uuid == puuid:
                mat = append_material(os.path.join(get_prefs().assetspath, library, name, "decal.blend"), "LIBRARY_DECAL")

                if mat:
                    # dedublicate, even though we know this is the only unmatched material, we still want to re-use any existing node trees and images
                    mat = deduplicate_material(mat)

                    return mat, True, library, name

    return None, None, None, None


# DICTIONARY RERESENTATION

def get_pbrnode_as_dict(node):
    d = {}

    for i in node.inputs:
        # NOTE: temporary fix for https://developer.blender.org/rB8f71a84496a95528303fbe0bb7c1406060353425, which breaks material matching
        # TODO: restructure all decal assets to use Alpha and Emission directly instead of using the Transparent shader
        if i.name in ['Alpha', 'Emission']:
            continue

        if i.type == "VECTOR" and "Subsurface" not in i.name:
            continue

        if i.type in ["RGBA", "VECTOR"]:
            value = [round(v, 3) for v in i.default_value]

        else:
            value = round(i.default_value, 3)

        d[i.name] = value

    return d


def get_defaultwhite_as_dict():
    d = {}

    d["Base Color"] = [0.8, 0.8, 0.8, 1]
    d["Subsurface"] = 0
    d["Subsurface Radius"] = [1, 0.2, 0.1]
    d["Subsurface Color"] = [0.8, 0.8, 0.8, 1]
    d["Metallic"] = 0
    d["Specular"] = 0.5
    d["Specular Tint"] = 0
    d["Roughness"] = 0.25
    d["Anisotropic"] = 0
    d["Anisotropic Rotation"] = 0
    d["Sheen"] = 0
    d["Sheen Tint"] = 0.5
    d["Clearcoat"] = 0
    d["Clearcoat Roughness"] = 0.03
    d["IOR"] = 1.45
    d["Transmission"] = 0
    d["Transmission Roughness"] = 0

    return d


def get_decalgroup_as_dict(node):
    material = {}
    material2 = {}
    subset = {}

    # TODO: extradict for edgehighlghts, ao strength, future emission stuff etc?

    for i in node.inputs:
        if any([i.name.startswith(string) for string in ["Material ", "Subset "]]):
            if i.type in ["RGBA", "VECTOR"]:
                value = [round(v, 3) for v in i.default_value]

            else:
                value = round(i.default_value, 3)

            if i.name.startswith("Material 2 "):
                material2[i.name.replace("Material 2 ", "")] = value

            elif i.name.startswith("Material "):
                material[i.name.replace("Material ", "")] = value

            elif i.name.startswith("Subset "):
                subset[i.name.replace("Subset ", "")] = value

    return material, material2, subset


def get_dict_from_matname(matname):
    if matname is None:
        return {}, None

    elif matname in ["DEFAULTWHITE", "None"]:
        return get_defaultwhite_as_dict(), None

    else:
        mat = bpy.data.materials.get(matname)
        if mat:
            pbrnode = get_pbrnode_from_mat(mat)

            if pbrnode:
                return get_pbrnode_as_dict(pbrnode), mat

            else:
                return {}, None


def get_dict_from_faceidx(matchobj, face_idx, debug=False):
    matchmat, matchpbrnode = get_match_material_from_faceidx(matchobj, face_idx)

    # get default white parameters
    if matchmat == "DEFAULTWHITE":
        if debug:
            print("Matching to Default White Material")

        return get_defaultwhite_as_dict(), None

    # get match material parameters
    elif matchmat:
        if debug:
            print("Matching to %s" % (matchmat.name))

        return get_pbrnode_as_dict(matchpbrnode), matchmat

    # not a matchable material
    else:
        return None, None


# MATERIAL MATCHING

def get_material_from_faceidx(matchobj, face_idx):
    idx = matchobj.data.polygons[face_idx].material_index

    mats = [mat for mat in matchobj.data.materials]

    if mats:
        matchmat = mats[idx] if idx < len(mats) else None

        # the material could be None, if it is passed in as data.materials[index] or material_slot.material
        if matchmat:
            return matchmat

    return "DEFAULTWHITE"


def set_decalgroup_from_dict(nodegroup, material=None, material2=None, subset=None):
    if material:
        for i in material:
            nodegroup.inputs["Material %s" % i].default_value = material[i]

    if material2:
        for i in material2:
            nodegroup.inputs["Material 2 %s" % i].default_value = material2[i]

    if subset:
        for i in subset:
            nodegroup.inputs["Subset %s" % i].default_value = subset[i]


def auto_match_material(decalobj, decalmat, matchobj=None, face_idx=None, matchmatname=None, debug=False):
    # if a matchmatname is passed in for auto match, it means its matched from the matchmaterial enum
    if matchmatname:
        if debug:
            print("Auto-matching material to selected material '%s' from matchmaterial enum." % (matchmatname))

    # otherwise, the default behavior is matching based on raycast results
    elif matchobj and face_idx is not None:
        if debug:
            print("Auto-matching material based on obj and face index.")

        matchmat = get_material_from_faceidx(matchobj, face_idx)
        matchmatname = matchmat.name if isinstance(matchmat, bpy.types.Material) else matchmat if matchmat else None

    # invalid arguments
    else:
        if debug:
            print("Existing auto match material, insufficient arguments.")
        return

    if matchmatname:
        matchmat2name = matchmatname if decalmat.DM.decaltype == "PANEL" else None
        matchsubname = None

        match_material(decalobj, decalmat, matchmatname=matchmatname, matchmat2name=matchmat2name, matchsubname=matchsubname, debug=debug)


def match_material(decalobj, decalmat, matchmatname=None, matchmat2name=None, matchsubname=None, debug=False):
    if debug:
        print("matching", decalmat.name, "to", matchmatname, matchmat2name, matchsubname)

    # get dictionaries for material, material2 and subset from target material names
    materialdict, material = get_dict_from_matname(matchmatname)
    material2dict, material2 = get_dict_from_matname(matchmat2name)
    subsetdict, subset = get_dict_from_matname(matchsubname)

    # abort, if all dicts are empty, as can happen when automatching invalid materials
    if not any([materialdict, material2dict, subsetdict]):
        if debug:
            print("Aborting, all material dictionaries are empty!")
        return None, None

    # contruct the tuple of dictionaries representing the matching decal material
    # note that, in a subset decal for instance, if the subset is not matched, that means the subsetdict needs to be retrieved from the decalmat
    dg = get_decalgroup_from_decalmat(decalmat)
    decal_materialdict, decal_material2dict, decal_subsetdict = get_decalgroup_as_dict(dg)

    match_materialdict = materialdict if materialdict else decal_materialdict
    match_material2dict = material2dict if material2dict else decal_material2dict
    match_subsetdict = subsetdict if subsetdict else decal_subsetdict

    match_tuple = (match_materialdict, match_material2dict, match_subsetdict)


    # look for existing decal material, that matches already
    existingmatchedmats = [mat for mat in bpy.data.materials if mat.DM.isdecalmat and mat.DM.uuid == decalmat.DM.uuid and mat.DM.ismatched]

    for candidate in existingmatchedmats:
        # get decal material parameters
        candidate_dg = get_decalgroup_from_decalmat(candidate)
        candidate_tuple = get_decalgroup_as_dict(candidate_dg)

        if match_tuple == candidate_tuple:
            if debug:
                print("Found existing matching material %s" % (candidate.name))

            decalobj.active_material = candidate
            return candidate, "EXISTING"

    if debug:
        print("Creating new matched decal material")

    decalmatmatched = decalmat.copy()
    decalmatmatched.DM.ismatched = True
    decalobj.active_material = decalmatmatched

    decalnodegroup = get_decalgroup_from_decalmat(decalmatmatched)

    set_decalgroup_from_dict(decalnodegroup, material=materialdict, material2=material2dict, subset=subsetdict)

    # NOTE: causes error: ID user decrement error: MAplastic.red (from '[Main]'): 0 <= 0, but still seems to work, Blender bug?
    # TODO: try to recreate error without DECALmachine activated, if necessary, create  mini script to register the prop, then report it, if the bug is fixed, reenable

    if materialdict:
        decalmatmatched.DM.matchedmaterialto = material

    if material2dict:
        decalmatmatched.DM.matchedmaterial2to = material2

    if subsetdict:
        decalmatmatched.DM.matchedsubsetto = subset

    return decalmatmatched, "MATCHED"


def set_match_material_enum(debug=False):
    wm = bpy.context.window_manager
    default = wm.matchmaterial

    mats = [mat for mat in bpy.data.materials if not mat.DM.isdecalmat and mat.use_nodes and get_pbrnode_from_mat(mat)]

    matchable = []

    if mats:
        if debug:
            print("Matchable materials:", [mat.name for mat in mats])

        for mat in sorted(mats, key=lambda x: x.name, reverse=True):
            matchable.append((mat.name, mat.name, "", mat.preview.icon_id, mat.preview.icon_id))
            # matchable.append((mat.name, mat.name, ""))

    # always have the "None" Material in the list, which is the DEFAULTWHITE material
    matchable.append(("None", "None", "", 0, 0))

    # check if the previously set matchmaterial is still among the items in the updated list, if not set a new default
    if default not in [item[0] for item in matchable]:
        default=matchable[0][0]

    bpy.types.WindowManager.matchmaterial = bpy.props.EnumProperty(name="Materials, that can be matched", items=matchable)

    # manually setting the new default, because it seems to fail sometimes, using the default argument
    bpy.context.window_manager.matchmaterial = default

    return sorted(mats, key=lambda x: x.name)
