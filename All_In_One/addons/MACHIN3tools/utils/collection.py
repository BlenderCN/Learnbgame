import bpy
from . registration import get_addon


def get_groups_collection(scene):
    mcol = scene.collection

    gpcol = bpy.data.collections.get("Groups")

    if gpcol:
        # link Groups collection, if it exists but is not linked to the master collection
        if gpcol.name not in mcol.children:
            mcol.children.link(gpcol)

    # create Groups collection, if it doesn't exist
    else:
        gpcol = bpy.data.collections.new(name="Groups")
        mcol.children.link(gpcol)

    return gpcol


def get_scene_collections(scene, ignore_decals=True):
    decalmachine, _, _, _ = get_addon("DECALmachine")
    mcol = scene.collection

    scenecols = []
    seen = list(mcol.children)

    while seen:
        col = seen.pop(0)
        if col not in scenecols:
            if not (ignore_decals and decalmachine and (col.DM.isdecaltypecol or col.DM.isdecalparentcol)):
                scenecols.append(col)
        seen.extend(list(col.children))

    return scenecols
