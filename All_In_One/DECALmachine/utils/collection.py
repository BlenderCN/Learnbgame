import bpy


def get_decaltype_collection(scene, decaltype):
    mcol = scene.collection

    decalsname = ".Decals" if scene.DM.hide_decaltype_collections else "Decals"
    typename = ".%s" % (decaltype.capitalize()) if scene.DM.hide_decaltype_collections else decaltype.capitalize()

    dcol = bpy.data.collections.get(decalsname)

    if dcol:
        # link Decals collection, if it exists but is not linked to the master collection
        if dcol.name not in mcol.children:
            mcol.children.link(dcol)

    # create Decals collection, if it doesn't exist
    else:
        dcol = bpy.data.collections.new(name=decalsname)
        mcol.children.link(dcol)
        dcol.DM.isdecaltypecol = True

    dtcol = bpy.data.collections.get(typename)

    if dtcol:
        # link decal type collection, if it exists but is not linked to the Decals collection
        if dtcol.name not in dcol.children:
            dcol.children.link(dtcol)

    # create decal type collection, if it doesn't exist
    else:
        dtcol = bpy.data.collections.new(name=typename)
        dcol.children.link(dtcol)
        dtcol.DM.isdecaltypecol = True

    return dtcol


def get_parent_collections(scene, obj):
    dpcols = []

    if obj.parent:
        cols = [col for col in obj.parent.users_collection if not col.DM.isdecaltypecol]

        for col in cols:
            dpcol = None

            # look for existing decal parent collection in the current col
            for childcol in col.children:
                if childcol.DM.isdecalparentcol:
                    dpcol = childcol
                    break

            # if none is found, create a new one
            if not dpcol:
                dpcol = bpy.data.collections.new("tempdecals")
                col.children.link(dpcol)
                dpcol.DM.isdecalparentcol = True

            # make sure it's named after the col
            dpcol.name = ".%s_Decals" % (col.name) if scene.DM.hide_decalparent_collections else "%s_Decals" % (col.name)

            dpcols.append(dpcol)

    return dpcols


def unlink_object(obj):
    for col in obj.users_collection:
        col.objects.unlink(obj)


def purge_decal_collections(debug=False):
    decalsname = ".Decals" if bpy.context.scene.DM.hide_decaltype_collections else "Decals"

    purge_collections = [col for col in bpy.data.collections if ((col.DM.isdecaltypecol and col.name != decalsname) or col.DM.isdecalparentcol) and (not col.objects and not col.children)]

    for col in purge_collections:
        if debug:
            print("Removing collection: %s" % (col.name))

        bpy.data.collections.remove(col, do_unlink=True)

    dcol = bpy.data.collections.get(decalsname)

    if dcol and dcol.DM.isdecaltypecol and not dcol.objects and not dcol.children:
        if debug:
            print("Removing collection: %s" % (dcol.name))

        bpy.data.collections.remove(dcol, do_unlink=True)


def sort_into_collections(scene, obj, purge=True):
    """
    sort decal object into collections based on scene default props
    """

    decaltype = scene.DM.collection_decaltype
    parent = scene.DM.collection_decalparent
    active = scene.DM.collection_active

    sorted_collections = []

    # LINK to DECAL TYPE COLLECTION

    if decaltype:
        dtcol = get_decaltype_collection(scene, obj.DM.decaltype)
        if obj.name not in dtcol.objects:
            dtcol.objects.link(obj)

        sorted_collections.append(dtcol)


    # LINK to DECAL PARENT COLLECTION

    if parent:
        dpcols = get_parent_collections(scene, obj)

        # link the decal to it
        for dpcol in dpcols:
            if obj.name not in dpcol.objects:
                dpcol.objects.link(obj)

        sorted_collections.extend(dpcols)


    # LINK to ACTIVE COLLECTION

    if active:
        acol = bpy.context.view_layer.active_layer_collection.collection

        if not any([acol.DM.isdecaltypecol, acol.DM.isdecalparentcol]):
            if obj.name not in acol.objects:
                acol.objects.link(obj)

            sorted_collections.append(acol)


    # UNLINK

    unlink_collections = [col for col in obj.users_collection if col not in sorted_collections]

    for col in unlink_collections:
        col.objects.unlink(obj)


    # MASTER COLLECTION FALLBACK

    if not any([decaltype, parent, active]) or not obj.users_collection:
        mcol = scene.collection

        if obj.name not in mcol.objects:
            mcol.objects.link(obj)

        sorted_collections.append(mcol)


    # PURGE
    if purge:
        purge_decal_collections()
