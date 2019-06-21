import bpy
from bpy.props import BoolProperty
import os
import re
from uuid import uuid4
import shutil
from .. utils.registration import get_path, get_prefs, reload_infotextures, reload_infofonts, reload_instant_decals, set_new_decal_index, reload_decal_libraries
from .. utils.append import append_scene, append_material, append_object
from .. utils.math import get_bbox_dimensions
from .. utils.pil import text2img, fix_legacy_normals
from .. utils.system import makedir, get_new_directory_index, abspath
from .. utils.material import get_decal_textures, get_decalgroup_from_decalmat, get_parallaxgroup_from_decalmat
from .. utils.material import get_decalmat, deduplicate_material, remove_decalmat
from .. utils.collection import get_decaltype_collection
from .. utils.scene import setup_surface_snapping
from .. utils.decal import align_decal, set_defaults, apply_decal, set_decalobj_name, set_props_and_node_names_of_library_decal, render_thumbnail, save_uuid, save_blend
from .. utils.modifier import add_nrmtransfer
from .. utils.create import create_decal_blend, pack_textures, create_info_decal_texture, create_decal_textures, create_decal_geometry, get_info_decal_geometry, get_decal_source_objects


class Create(bpy.types.Operator):
    bl_idname = "machin3.create_decal"
    bl_label = "MACHIN3: Create Decal"
    bl_description = "Create your own Decals - from Geometry, Images or Text"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if get_prefs().pil:
            if context.scene.DM.create_decaltype == "INFO":
                if context.scene.DM.create_infotype == "IMAGE":
                    return bpy.types.WindowManager.infotextures[1]['items']

                elif context.scene.DM.create_infotype == "FONT":
                    return bpy.types.WindowManager.infofonts[1]['items'] and context.scene.DM.create_infotext

                elif context.scene.DM.create_infotype == "GEOMETRY":
                    return context.selected_objects

            else:
                return context.active_object in context.selected_objects

    def execute(self, context):
        templatepath = os.path.join(get_path(), "resources", "Templates.blend")
        createpath = os.path.join(get_path(), "assets", "Create")
        instantpath = os.path.join(createpath, "instant")
        infopath = os.path.join(createpath, 'infotextures')
        fontspath = os.path.join(createpath, 'infofonts')

        uuid = str(uuid4())
        index = get_new_directory_index(instantpath)
        decalpath = makedir(os.path.join(instantpath, "%s_%s" % (index, uuid)))

        dm = context.scene.DM
        wm = context.window_manager

        if dm.create_decaltype == 'INFO':
            location = (0, 0, 0)
            width = 0

            if context.scene.DM.create_infotype == "IMAGE":
                texturespath = makedir(os.path.join(decalpath, 'textures'))
                texturename = wm.infotextures
                ext = os.path.splitext(texturename)[1]

                crop = dm.create_infoimg_crop
                padding = dm.create_infoimg_padding

                # copy current info decal texture to decal/textures folder
                srcpath = os.path.join(infopath, texturename)
                destpath = os.path.join(texturespath, "color%s" % (ext))
                shutil.copy(srcpath, destpath)

                # create color alpha map
                packed, decaltype = pack_textures(dm, decalpath, [destpath], crop=crop, padding=padding)

                # set up the decal
                decal, decalmat, size = create_decal_blend(context, templatepath, decalpath, packed, decaltype, uuid=uuid)

                # create thumbnail
                render_thumbnail(context, decalpath, decal, decalmat, tint=dm.create_thumbnail_tint, size=size)

            elif context.scene.DM.create_infotype == "FONT":
                texturespath = makedir(os.path.join(decalpath, 'textures'))
                fontname = wm.infofonts

                font = os.path.join(fontspath, fontname)
                text = dm.create_infotext.replace("\\n", "\n")

                textcolor = dm.create_infotext_color
                bgcolor = dm.create_infotext_bgcolor

                size = dm.create_infotext_size
                padding = dm.create_infotext_padding
                offset = dm.create_infotext_offset

                align = dm.create_infotext_align

                texturename = "%d_%s_%s" % (size, fontname[:-4], text.replace("\n", "") + ".png")
                text2imgpath = os.path.join(texturespath, texturename)

                text2img(text2imgpath, text, font, size, padding=padding, offset=offset, align=align, color=textcolor, bgcolor=bgcolor)

                # create color alpha map
                packed, decaltype = pack_textures(dm, decalpath, [text2imgpath])

                # set up the decal
                decal, decalmat, size = create_decal_blend(context, templatepath, decalpath, packed, decaltype, uuid=uuid)

                # create thumbnail
                render_thumbnail(context, decalpath, decal, decalmat, tint=dm.create_thumbnail_tint, size=size)


            elif context.scene.DM.create_infotype == "GEOMETRY":
                bakepath = makedir(os.path.join(decalpath, "bakes"))
                padding = dm.create_infotext_padding

                sel = [obj for obj in context.selected_objects]

                # get and set create scene
                bakescene = append_scene(templatepath, "Bake")

                # switch to the bakescene
                context.window.scene = bakescene

                # link selected object duplicates to the create scene, also create a bounding box
                source_objs, bbox_coords = get_info_decal_geometry(context, bakescene, sel)

                # get bbox dimensions
                width, depth, height = get_bbox_dimensions(bbox_coords)

                # create decal object and position it slightly above the bbox
                decal, location = create_decal_geometry(context, bakescene, bbox_coords, min((d for d in [width, depth, height] if d != 0)))

                textures, size = create_info_decal_texture(context, dm, templatepath, bakepath, bakescene, decal, source_objs, bbox_coords, width, depth, padding)

                # pack the textures
                packed, decaltype = pack_textures(dm, decalpath, textures, size)

                # set up the decal
                # self.setup_decal(context, templatepath, packed, decaltype, decal, size, uuid)
                decal, decalmat, size = create_decal_blend(context, templatepath, decalpath, packed, decaltype, decal, size, uuid)

                # create thumbnail
                render_thumbnail(context, decalpath, decal, decalmat, tint=dm.create_thumbnail_tint, size=size)


        else:
            bakepath = makedir(os.path.join(decalpath, "bakes"))

            sel = [obj for obj in context.selected_objects if obj.type == "MESH"]
            active = context.active_object

            # get and set create scene
            bakescene = append_scene(templatepath, "Bake")

            # switch to the bakescene
            context.window.scene = bakescene

            # link selected object duplicates to the bake scene, also create a bounding box
            source_objs, active, bbox_coords = get_decal_source_objects(context, bakescene, sel, active, debug=False)

            # get bbox dimensions
            width, depth, height = get_bbox_dimensions(bbox_coords)

            # create decal object and position it slightly above the bbox
            decal, location = create_decal_geometry(context, bakescene, bbox_coords, height)

            # bake and create raw decal textures
            textures, size = create_decal_textures(context, dm, templatepath, bakepath, bakescene, decal, active, source_objs, bbox_coords, width, depth)

            # pack the textures
            packed, decaltype = pack_textures(dm, decalpath, textures, size)

            # create and save decal blend
            decal, decalmat, size = create_decal_blend(context, templatepath, decalpath, packed, decaltype, decal, size, uuid)

            # create thumbnail
            render_thumbnail(context, decalpath, decal, decalmat, tint=dm.create_thumbnail_tint, size=size)

        # reload instant decal library and set new default
        reload_instant_decals(default=os.path.basename(decalpath))

        # bring decal into current scene
        self.insert_decal(context, decalpath, decaltype, location, width)

        # set quickinsert props
        dm.quickinsertdecal = os.path.basename(decalpath)
        dm.quickinsertlibrary = "INSTANT"
        dm.quickinsertisinstant = True

        # setup surface snapping
        setup_surface_snapping(context.scene)

        return {'FINISHED'}

    def insert_decal(self, context, decalpath, decaltype, location, width):
        baked = False if decaltype == "INFO" and context.scene.DM.create_infotype in ['IMAGE', 'FONT'] else True

        decalobj = append_object(os.path.join(decalpath, "decal.blend"), "LIBRARY_DECAL")

        # get collection
        dtcol = get_decaltype_collection(context.scene, decalobj.DM.decaltype)

        dtcol.objects.link(decalobj)

        # align the decal to the source geometry
        if baked:
            decalobj.location = location
            factor = decalobj.dimensions[0] / width
            decalobj.scale /= factor

        # align the decal to the cursor and scale it
        else:
            dg = context.evaluated_depsgraph_get()
            align_decal(decalobj, context.scene, dg, force_cursor_align=True)

        # unselect sll, select decal
        bpy.ops.object.select_all(action='DESELECT')
        decalobj.select_set(True)
        context.view_layer.objects.active = decalobj

        # deduplicate the material
        mat = get_decalmat(decalobj)

        if mat:
            decalmat = deduplicate_material(mat)
            decalobj.active_material = decalmat

        else:
            decalmat = None

        if decalmat:
            # set the props of the decal obj and the as of yet unmatched material
            set_props_and_node_names_of_library_decal("INSTANT", os.path.basename(decalpath), decalobj=decalobj, decalmat=decalmat)

            # set the defaults, just like the props above, it's important to do this before the decal is applied and the material is potentially auto matched
            set_defaults(decalobj=decalobj, decalmat=decalmat)

            if not baked:
                # apply the decal - do a raycast and then set up the custom normals, the parenting, auto match the material according to the result of the cast
                apply_decal(decalobj, raycast=True)

            # set decalobj name, counting up
            set_decalobj_name(decalobj)


class AddDecalToLibrary(bpy.types.Operator):
    bl_idname = "machin3.add_decal_to_library"
    bl_label = "MACHIN3: Add Decal to Library"
    bl_description = "Add Selected Decal(s) to Decal Library"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return any(obj for obj in context.selected_objects if obj.DM.isdecal and not obj.DM.isprojected and not obj.DM.issliced) and context.scene.userdecallibs

    def draw(self, context):
        layout = self.layout
        column = layout.column()

    def execute(self, context):
        # update the index, shouldn't be necessary, unless the users meses with the decal libs, while blender is running, but just to make extra sure
        set_new_decal_index(self, context)

        assetspath = get_prefs().assetspath
        templatepath = os.path.join(get_path(), "resources", "Templates.blend")

        index = context.window_manager.newdecalidx
        library = context.scene.userdecallibs
        name = context.scene.DM.addlibrary_decalname
        dm = context.scene.DM

        decals = [obj for obj in context.selected_objects if obj.DM.isdecal and not obj.DM.isprojected and not obj.DM.issliced]

        for idx, source_decal in enumerate(decals):
            decalidx = str(int(index) + idx).zfill(3)
            decalname = "%s_%s" % (decalidx, name.strip().replace(" ", "_")) if name.strip() else decalidx

            decalpath = makedir(os.path.join(assetspath, library, decalname))

            # duplicate decalobj
            decal = source_decal.copy()
            decal.data = source_decal.data.copy()

            # get old decalmat
            oldmat = source_decal.active_material

            # bring in template material, NOTE: instead of duplicating the old material(and its nodes), we are importing a new template mat, because the material could be matched and the library decal shouldn't be
            decalmat = append_material(templatepath, "TEMPLATE_%s" % oldmat.DM.decaltype, relative=False)
            decal.active_material = decalmat


            # set the parallax value, on the new material, which may have been adjusted by the user
            oldpg = get_parallaxgroup_from_decalmat(oldmat)
            pg = get_parallaxgroup_from_decalmat(decalmat)

            if oldpg and pg:
                pg.inputs['Amount'].default_value = oldpg.inputs['Amount'].default_value

            # create new uuid
            uuid = str(uuid4())

            # get creator from source obj
            creator = source_decal.DM.creator

            # set all props to LIBRARY_DECAL
            set_props_and_node_names_of_library_decal("LIBRARY", "DECAL", decalobj=decal, uuid=uuid, creator=creator)

            decal.name = "LIBRARY_DECAL"
            decal.data.name = decal.name

            # get old and new textures
            oldtextures = get_decal_textures(oldmat)
            textures = get_decal_textures(decalmat)

            # copy textures and set new texture paths
            for textype, img in oldtextures.items():
                if textype != 'HEIGHT':
                    srcpath = abspath(img.filepath)
                    destpath = os.path.join(decalpath, os.path.basename(srcpath))

                    shutil.copy(srcpath, destpath)

                    textures[textype].filepath = destpath

            # link decal to decal asset scene
            decalscene = bpy.data.scenes.new(name="Decal Asset")
            decalscene.collection.objects.link(decal)

            # create uuid file
            save_uuid(decalpath, uuid)

            # save decal blend
            save_blend(decal, decalpath, decalscene)

            # render thumbnail and remove everything
            render_thumbnail(context, decalpath, decal, decalmat, tint=dm.create_thumbnail_tint, removeall=True)


        # reload library that was added to
        reload_decal_libraries(library=library, default=os.path.basename(decalpath))

        # update the index
        set_new_decal_index(self, context)

        return {'FINISHED'}


class UpdateLegacyDecalLibrary(bpy.types.Operator):
    bl_idname = "machin3.update_legacy_decal_library"
    bl_label = "MACHIN3: Update Legacy Decal Library"
    bl_description = "Update Legacy Decal Library"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.scene.userdecallibs and context.scene.DM.updatelibrarypath and context.scene.DM.updatelibrarypath != "CHOOSE A LEGACY DECAL LIBRARY!":
            return get_prefs().pil if context.scene.DM.update_fix_legacy_normals else True

    def execute(self, context):
        set_new_decal_index(self, context)

        scene = context.scene
        dm = scene.DM

        fixnormals = dm.update_fix_legacy_normals
        storeolduuids = dm.update_store_uuid_with_old_decals
        keepthumbnails = dm.update_keep_old_thumbnails

        assetspath = get_prefs().assetspath
        templatepath = os.path.join(get_path(), "resources", "Templates.blend")

        sourcepath = dm.updatelibrarypath
        librarypath = os.path.join(assetspath, scene.userdecallibs)
        startidx = context.window_manager.newdecalidx

        tint = dm.create_thumbnail_tint

        legacydecals = self.get_legacy_decals(sourcepath)

        if legacydecals:

            for idx, (name, blendpath, iconpath) in enumerate(legacydecals):
                name = name.replace("c_paneling", "c_panel_decal")
                index = str(int(startidx) + idx).zfill(3)

                # append old decal, create new decal from it and save it to new path
                decalname = self.create_new_decal(context, index, name, blendpath, iconpath, templatepath, librarypath, fixnormals, storeolduuids, keepthumbnails, tint)

            # reload decal library
            reload_decal_libraries(library=scene.userdecallibs, default=decalname)

        return {'FINISHED'}

    def create_new_decal(self, context, index, name, blendpath, iconpath, templatepath, librarypath, fixnormals, storeolduuids, keepthumbnails, tint):
        decalscene = bpy.data.scenes.new(name="Decal Asset")
        context.window.scene = decalscene

        # append the legacy decal object
        with bpy.data.libraries.load(blendpath, link=False) as (data_source, data_current):
            if name in data_source.objects:
                data_current.objects.append(name)

        # append decal obj to the decal asset scene
        if data_current.objects:
            decalobj = data_current.objects[0]
            decalscene.collection.objects.link(decalobj)

            # enable auto smooth (for the normal transfer to work)
            decalobj.data.use_auto_smooth = True

            # add data transfer mod
            add_nrmtransfer(decalobj)

            # determine basename and basic props
            decalname = self.get_decal_basename(index, name)
            decaltype = self.get_legacy_decaltype(decalobj)
            creator = get_prefs().decalcreator
            uuid = str(uuid4())

            # get the template material and apply a copy of it, creating a new decalmat
            if decaltype:
                # get the legacy material and its textures
                oldmat = decalobj.active_material
                oldtextures = get_decal_textures(oldmat, legacy=True)

                # bring in the template material
                decalmat = append_material(templatepath, "TEMPLATE_%s" % decaltype, relative=False)
                decalobj.active_material = decalmat

                # set basic decalobj props and name
                decalobj.name = "LIBRARY_DECAL"
                decalobj.data.name = decalobj.name

                decalobj.show_wire = False
                decalobj.DM.isdecal = True

                # get decalmat textures
                textures = get_decal_textures(decalmat)

                # set props and node names
                set_props_and_node_names_of_library_decal("LIBRARY", "DECAL", decalobj, decalmat, list(textures.values()), decaltype, uuid, creator)

                # copy the old textures to their new location and set the new path on the texutures
                decalpath = makedir(os.path.join(librarypath, decalname))

                for textype, oldimg in oldtextures.items():
                    oldpath = abspath(oldimg.filepath)
                    newpath = os.path.join(decalpath, textype.lower() + ".png")

                    shutil.copy(oldpath, newpath)

                    textures[textype].filepath = newpath

                    if fixnormals and textype == "NRM_ALPHA":
                        fix_legacy_normals(newpath)

                # create uuid file
                save_uuid(decalpath, uuid)

                if storeolduuids:
                    save_uuid(blendpath, uuid, legacy=True)

                # write the new blend file
                save_blend(decalobj, decalpath, decalscene)

                # copy old thubnail
                if keepthumbnails:
                    shutil.copy(iconpath, os.path.join(decalpath, "decal.png"))

                    bpy.data.meshes.remove(decalobj.data, do_unlink=True)
                    remove_decalmat(decalmat, remove_textures=True)

                # render thumbnail
                else:
                    render_thumbnail(context, decalpath, decalobj, decalmat, tint=tint, removeall=True)

                # remove old material and textures
                remove_decalmat(oldmat, remove_textures=True, legacy=True)

                return decalname

    def get_legacy_decaltype(self, decalobj):
        # detect the type of the decal via the materials decal group
        decalmat = decalobj.active_material

        if decalmat:
            dg = get_decalgroup_from_decalmat(decalmat)

            if dg:
                treename = dg.node_tree.name

                if any([n in treename for n in["Decal Group", "Decal Subtractor Group"]]):
                    return "SIMPLE"
                elif "Decal Subset Group" in treename:
                    return "SUBSET"
                elif "Decal Info Group" in treename:
                    return "INFO"
                elif "Decal Panel Group" in treename:
                    return "PANEL"

    def get_decal_basename(self, index, decalname):
        # decal01_05 or c_decal01_05
        basenameRegex = re.compile(r"[\w]+_\d\d\w?([\w]*)")
        mo = basenameRegex.match(decalname)

        basename = mo.group(1)

        if basename:
            newbasename = index + "_" + basename
        else:
            newbasename = index

        return newbasename

    def get_legacy_decals(self, librarypath):
        blendspath = os.path.join(librarypath, "blends")
        iconspath = os.path.join(librarypath, "icons")

        legacydecals = []

        for f in sorted(os.listdir(iconspath)):
            if f.endswith(".png"):
                decalname = f[:-4]

                iconpath = os.path.join(iconspath, f)
                blendpath = os.path.join(blendspath, decalname + ".blend")

                if os.path.exists(blendpath):
                    legacydecals.append((decalname, blendpath, iconpath))

        return legacydecals


class LoadImages(bpy.types.Operator):
    bl_idname = "machin3.load_images"
    bl_label = "MACHIN3: Load Images"
    bl_description = "Load Images to Create Info Decals from"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.window_manager

        wm.collectinfotextures = True

        # poulate collection prop with all existing image names
        for img in bpy.data.images:
            i = wm.excludeimages.add()
            i.name = img.name

        # load new image(s)
        bpy.ops.image.open('INVOKE_DEFAULT', display_type='THUMBNAIL', use_sequence_detection=False)

        # NOTE: the actual work is then done in the draw() function of PanelDecalCreation() as well as the update_infoimages handler

        return {'FINISHED'}


class ClearImages(bpy.types.Operator):
    bl_idname = "machin3.clear_images"
    bl_label = "MACHIN3: Clear Images"
    bl_description = "Clear Images to be used for Info Decals"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        createpath = os.path.join(get_path(), "assets", "Create")
        infotexturespath = os.path.join(createpath, "infotextures")

        images = [os.path.join(infotexturespath, f) for f in os.listdir(infotexturespath) if f != ".gitignore"]

        for img in images:
            os.unlink(img)

        reload_infotextures()

        return {'FINISHED'}


class LoadFonts(bpy.types.Operator):
    bl_idname = "machin3.load_fonts"
    bl_label = "MACHIN3: Load Fonts"
    bl_description = "Load Fonts to be used for Info Decals"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.window_manager

        wm.collectinfofonts = True

        # poulate collection prop with all existing font names
        for font in bpy.data.fonts:
            f = wm.excludefonts.add()
            f.name = font.name

        # load new image(s)
        bpy.ops.font.open('INVOKE_DEFAULT', display_type='THUMBNAIL')
        # NOTE. unlike the image op, this font op only supports loading one font at a time


        # NOTE: the actual work is then done in the draw() function of PanelDecalCreation() as well as the update_infoimages handler

        return {'FINISHED'}


class ClearFonts(bpy.types.Operator):
    bl_idname = "machin3.clear_fonts"
    bl_label = "MACHIN3: Clear Fonts"
    bl_description = "Clear Fonts to be used for Info Decals"
    bl_options = {'REGISTER', 'UNDO'}

    keepubuntu: BoolProperty(name="Keep Ubuntu Font", default=True)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "keepubuntu")

    def execute(self, context):
        createpath = os.path.join(get_path(), "assets", "Create")
        infofontspath = os.path.join(createpath, "infofonts")

        fonts = [os.path.join(infofontspath, f) for f in os.listdir(infofontspath) if f != ".gitignore"]

        for font in fonts:
            if self.keepubuntu and os.path.basename(font) == "ubuntu.ttf":
                continue
            os.unlink(font)

        reload_infofonts()

        return {'FINISHED'}
