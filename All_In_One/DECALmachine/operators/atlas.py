import bpy
from bpy.props import StringProperty, BoolProperty

try:
    from PIL import Image
except ImportError as e:
    import traceback
    print()
    traceback.print_exc()

    if str(e) == "cannot import name '_imaging'":
        print(80 * "-")
        print()
        print(" ! FOLLOW THE INSTALLATION INSTRUCTIONS ! ")
        print()
        print("You have either chosen the wrong PIL for your operating system,")
        print("or you need to install Microsoft Visual C++ Redistributable 2015.")
        print()
        print("https://machin3.io/DECALmachine/docs/installation/")
        print()
        print(80 * "-")

    elif str(e) == "No module named 'PIL'":
        print(80 * "-")
        print()
        print(" ! FOLLOW THE INSTALLATION INSTRUCTIONS ! ")
        print()
        print("You have skipped installing the PIL module.")
        print()
        print("https://machin3.io/DECALmachine/docs/installation/")
        print()
        print(80 * "-")

import os
from random import randint
from math import sqrt
import re
from . export import ResetExportGroup
from .. utils.operators import load_json, save_json, makedir
from .. import M3utils as m3


# TODO: how would you deal with multiple objects and multiple atlases in one scene?

# TODO: all at once solution that skips the repacking stage and exports whatever res Atlasing comes up with?
# TODO: option to split atlas(= make multiple ones) and dropdow to choose max resolution?
# TODO: Atlasing.view_atlas() - available once DM_atlas group's ["json"] is True?


class ResetAtlasSolution(bpy.types.Operator):
    bl_idname = "machin3.decal_export_reset_atlas"
    bl_label = "MACHIN3: Reset Atlas Solution"
    bl_options = {'REGISTER', 'UNDO'}

    atlastype = StringProperty()

    def execute(self, context):
        atlasgroup = bpy.data.groups['DM_atlas_' + self.atlastype]

        # rest atlasgroup json value, which indicated the presense of the atlas json file
        # once it is False, you can create a new atlas solution
        atlasgroup["json"] = False

        # resetting the maptypes list back the full list found in the decals dict(ao, nrm, curv,etc)
        atlasgroup['maptypes'] = bpy.data.groups['DM_atlas_' + self.atlastype]['decals']['maptypes']

        # reset exportgroups,that match the current atlastype(that have decals of the current atlastype)
        for group in bpy.data.groups:
            if group.name.startswith("DM_export_"):
                if self.atlastype in group["atlastype"]:
                    ResetExportGroup(group.name)

        m3.unselect_all("OBJECT")

        # remove atlas preview materials
        if self.atlastype == "decal":
            decalmat = bpy.data.materials.get("decals")
            panelmat = bpy.data.materials.get("panel_decals")
            if decalmat:
                bpy.data.materials.remove(decalmat, do_unlink=True)
            if panelmat:
                bpy.data.materials.remove(panelmat, do_unlink=True)
        elif self.atlastype == "info":
            infomat = bpy.data.materials.get("info_decals")
            if infomat:
                bpy.data.materials.remove(infomat, do_unlink=True)

        # remove unused atlas textures
        bpy.ops.machin3.cleanout_decal_texture_duplicates()

        # automatically initate a new atlas
        if bpy.context.scene.decals.autoinitiateafterreset:
            bpy.ops.machin3.decal_export_atlas(atlastype=self.atlastype, repack=False)

        return {'FINISHED'}


class AtlasGroup(bpy.types.Operator):
    bl_idname = "machin3.decal_export_atlas_group"
    bl_label = "MACHIN3: Atlas Group"
    bl_options = {'REGISTER', 'UNDO'}

    # TODO: terminal output, espc if an item is already in the group (in case of updating the atlas group)

    def execute(self, context):
        selection = m3.selected_objects()

        # create/update atlasgroups based on selection and iniate their id properties
        # atlasgroups, createdecalgroup, createinfogroup = self.initiate_atlas_groups(selection)
        atlasgroups = self.initiate_atlas_groups(selection)

        # fill out the id properties
        for atlasgroup in atlasgroups:
            self.add_texture_data_to_group(atlasgroup)

        return {'FINISHED'}

    def initiate_atlas_groups(self, selection):
        m3.unselect_all("OBJECT")

        # organize decals in selection by the four decal types
        decals = {}
        decals["decal01"] = []
        decals["decal02"] = []
        decals["info01"] = []
        decals["paneling01"] = []

        # based on those 4 types, put decals into one of two atlas types
        createdecalgroup = False
        createinfogroup = False
        for obj in selection:
            if obj.type == "MESH":
                try:
                    mat = obj.material_slots[0].material
                except:
                    mat = None
                if mat:
                    if "decal01" in mat.name:
                        decals["decal01"].append(obj)
                        createdecalgroup = True
                    if "decal02" in mat.name:
                        decals["decal02"].append(obj)
                        createdecalgroup = True
                    if "paneling01" in mat.name:
                        decals["paneling01"].append(obj)
                        createdecalgroup = True
                    if "info01" in mat.name:
                        decals["info01"].append(obj)
                        createinfogroup = True

        # create decal group and add id properties
        if createdecalgroup:
            if "DM_atlas_decal" not in bpy.data.groups:
                # create new DM_atlas_decal group
                decalgroup = bpy.data.groups.new("DM_atlas_decal")
            else:
                # decal group exists already
                decalgroup = bpy.data.groups["DM_atlas_decal"]

                # unlink all existing objects of the group, this is so you can actually downsize and take out decals from atlas groups, not just add to them
                for obj in decalgroup.objects:
                    decalgroup.objects.unlink(obj)

            # state whether atlas json file is present for this group
            decalgroup["json"] = False
            # this dict will carry all the unique materials and their specific texture types and paths
            decalgroup["decals"] = dict()
            # this list will track the maptypes that need to be atlased (based on an existing solution), ao, curv, nrm, etc
            decalgroup["maptypes"] = list()

        # create info group and add id properties
        if createinfogroup:
            if "DM_atlas_info" not in bpy.data.groups:
                # create new DM_atlas_info group
                infogroup = bpy.data.groups.new("DM_atlas_info")
            else:
                # info group exists already
                infogroup = bpy.data.groups["DM_atlas_info"]

                # unlink all existing objects of the group, this is so you can actually downsize and take out decals from atlas groups, not just add to them
                for obj in infogroup.objects:
                    infogroup.objects.unlink(obj)

            # state whether atlas json file is present for this group
            infogroup["json"] = False
            # this dict will carry all the unique materials and their specific texture types and paths
            infogroup["decals"] = dict()
            # this list will track the maptypes that need to be atlased (based on an existing solution), color
            infogroup["maptypes"] = list()

        # assign objects to the groups accordingly
        for dtype in decals:
            for obj in decals[dtype]:
                if createdecalgroup:
                    if dtype in ["decal01", "decal02", "paneling01"]:
                        if obj.name not in decalgroup.objects:
                            decalgroup.objects.link(obj)
                if createinfogroup:
                    if dtype == "info01":
                        if obj.name not in infogroup.objects:
                            infogroup.objects.link(obj)

        if createdecalgroup and createinfogroup:
            return [decalgroup, infogroup]
        elif createdecalgroup:
            return [decalgroup]
        elif createinfogroup:
            return [infogroup]
        else:
            return []

    def add_texture_data_to_group(self, atlasgroup):
        decalmaps = {}
        maptypes = decalmaps["maptypes"] = []
        for obj in atlasgroup.objects:
            mat = obj.material_slots[0].material
            decalmaps[mat.name] = {}
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    path = os.path.abspath(bpy.path.abspath(node.image.filepath))
                    if "ao_curv_height.png" in path:
                        decalmaps[mat.name]["ao_curv_height"] = path
                        if "ao_curv_height" not in maptypes:
                            maptypes.append("ao_curv_height")
                    if "nrm_alpha.png" in path:
                        decalmaps[mat.name]["nrm_alpha"] = path
                        if "nrm_alpha" not in maptypes:
                            maptypes.append("nrm_alpha")
                    if "subset.png" in path:
                        decalmaps[mat.name]["subset"] = path
                        if "subset" not in maptypes:
                            maptypes.append("subset")
                    if "info01" in path:
                        decalmaps[mat.name]["color"] = path
                        if "color" not in maptypes:
                            maptypes.append("color")

        # remove duplicates values in the decalmaps dict, caused by material matching: somedecal and somedecal.001 etc
        # first, create key, value tuple list
        t = sorted([(mat, decalmaps[mat]) for mat in decalmaps])

        # reset dict
        decalmaps = {}

        # populate it with unique values only
        for k, v in t:
            if v not in decalmaps.values():
                decalmaps[k] = v

        # assign the decalmaps dict and the maptypes list as id properties to the DM_atlas_group
        atlasgroup["decals"] = decalmaps
        atlasgroup["maptypes"] = sorted(maptypes)


class UseExistingAtlasSolution(bpy.types.Operator):
    bl_idname = "machin3.decal_export_use_existing_atlas"
    bl_label = "MACHIN3: Use Existing Atlas Solution"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        blendfile = os.path.basename(bpy.data.filepath)[:-6]
        exportpath = makedir(os.path.join(bpy.context.user_preferences.addons['DECALmachine'].preferences.DMexportpath, blendfile))

        print("Using existing atlas solution!")
        print("Put your existing atlas json's and atlas png's in the export folder:")
        print(exportpath)

        foundatlasgroup = False
        for group in bpy.data.groups:
            if "DM_atlas_" in group.name:
                group['json'] = True
                foundatlasgroup = True

        if bpy.context.scene.decals.autoopenfolderforexistingatlas:
            if foundatlasgroup:
                m3.open_folder(exportpath)

        return {'FINISHED'}


class AcceptAtlasSolution(bpy.types.Operator):
    bl_idname = "machin3.decal_export_accept_atlas"
    bl_label = "MACHIN3: Accept Atlas Solution"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # fetch atlastype and maptype of the current DECALatlas scene
        atlastype = bpy.context.scene.decals.atlastype
        maptype = bpy.context.scene.decals.maptype

        # remove all the atlasmats and all the objects in the DECALatlas scene
        for obj in bpy.context.scene.objects:
            try:
                mat = obj.material_slots[0].material
            except:
                mat = None
            if mat:
                bpy.data.materials.remove(mat, do_unlink=True)
            bpy.data.objects.remove(obj, do_unlink=True)

        # remove atlas scene
        bpy.data.scenes.remove(bpy.context.scene, do_unlink=True)

        # set the export_alas group ["json"] parameter
        bpy.data.groups["DM_atlas_" + atlastype]["json"] = True

        # remove maptype from maptypes list in the DM_atlas group
        # NOTE for packs based on existing atlas solutions, the same is done directly in the atlas class
        maptypes = bpy.data.groups['DM_atlas_' + atlastype]['maptypes']
        maptypes.remove(maptype)
        bpy.data.groups['DM_atlas_' + atlastype]['maptypes'] = maptypes
        print("%s Atlas - '%s' pack completed." % (atlastype.upper(), maptype))
        print(" --- ")

        # pack other maps if there are any
        for maptype in maptypes:
            # print(maptype)
            bpy.ops.machin3.decal_export_atlas(atlastype=atlastype, repack=False)

        return {'FINISHED'}


class AtlasOp(bpy.types.Operator):
    bl_idname = "machin3.decal_export_atlas"
    bl_label = "MACHIN3: Atlas"
    bl_options = {'REGISTER', 'UNDO'}

    atlastype = StringProperty()
    repack = BoolProperty()

    def execute(self, context):
        blendfile = os.path.basename(bpy.data.filepath)[:-6]
        self.exportpath = makedir(os.path.join(bpy.context.user_preferences.addons['DECALmachine'].preferences.DMexportpath, blendfile))

        # There are 3 ways to pack:
        # 1. The Initial Pack, to find the best solution based on the decals selected, this saves out a json
        # 2. A Re-Pack/Re-Atlasing where a new best solution is found based on changes made to the decal texture sizes in the DECALatlas scene
        # 3. A pack based on an Existing Solution, but for a different map type. No actual packing is figured out here, all image positions and scales are read straight from the json
        # the values of atlasjson(None or dictionary) and repack(True or False) determine the way to pack

        # load atlasjson, if it can be found
        atlasjson = self.get_atlas_json()

        # prepare repack
        if self.repack:
            self.prepare_repack(atlasjson)

        # get the map type from the DM_atlas group's ["maptypes"] parameter
        maptype = bpy.data.groups["DM_atlas_" + self.atlastype]["maptypes"][0]

        # get textures of that maptype from the DM_atlas groups decals dict id property
        textures = self.get_textures(maptype)

        # create Atlas
        A = Atlas(textures, maptype, self.atlastype, self.exportpath, atlasjson=atlasjson, repack=self.repack)

        # visualize the packing, when it is an initial pack or a re-pack
        # but not when it is a pack based on an existing solution
        if atlasjson is None or self.repack is True:
            A.layout_atlas()

        return {'FINISHED'}

    def get_textures(self, maptypestring, silent=True):
        decalsdict = bpy.data.groups['DM_atlas_' + self.atlastype]["decals"]

        textures = []
        for d in decalsdict:
            if d != "maptypes":
                for texture in decalsdict[d]:
                    if texture == maptypestring:
                        filename = decalsdict[d][texture]
                        textures.append(filename)

        if not silent:
            print("Textures to pack:")
            for f in sorted(textures):
                print(" > " + os.path.basename(f))
            print()

        return sorted(textures)

    def get_atlas_json(self):
        # only check for a json file when the DM_atlas group has been set to True(1)
        # or if we are in a DECALatlas scene already
        scene = bpy.context.scene
        if bpy.data.groups["DM_atlas_" + self.atlastype]["json"] or scene.name == "DECALatlas":
            try:
                # json found, it's gonna be a pack based on an existing solution or a repack
                atlasjson = load_json(os.path.join(self.exportpath, "atlas_" + self.atlastype + ".json"))
            except:
                # no json found, it's gonna be an initial pack
                atlasjson = None
        else:
            atlasjson = None

        return atlasjson

    def prepare_repack(self, atlasjson):
        # update the packing solution with new per decal scale values
        # which will then be used for re-packing and visualized via Atlas.layout_atlas()
        # also, while at it, collect the atlas materials applied to the decaltexture planes and all the objects in the DECALatlasscene
        DECALatlasmats = []
        DECALatlasobjs = []
        for obj in bpy.context.scene.objects:
            DECALatlasobjs.append(obj)
            try:
                path = obj["filepath"]
                atlasjson["fullboxes"][path][4] = obj.scale[0]
                atlasjson["fullboxes"][path][5] = obj.scale[1]
                mat = obj.material_slots[0].material
                DECALatlasmats.append(mat)
            except:
                pass

        # also update the downsample and padding settings, according to the current DECALatlas scene setting
        atlasjson["downsample"] = bpy.context.scene.decals.atlasdownsample
        atlasjson["padding"] = bpy.context.scene.decals.atlaspadding

        # save atlas json
        save_json(atlasjson, os.path.join(self.exportpath, "atlas_" + self.atlastype + ".json"))

        # remove all the atlasmats, otherwise numerous duplicates will accumulate with each re-pack
        for mat in DECALatlasmats:
            bpy.data.materials.remove(mat, do_unlink=True)

        # remove all objects in the DECALatlas scene, otherwise numerous duplicates will accumulate with each re-pack
        for obj in DECALatlasobjs:
            bpy.data.objects.remove(obj, do_unlink=True)

        # remove DECALatlas scene
        bpy.data.scenes.remove(bpy.context.scene, do_unlink=True)


class Atlas():
    def __init__(self, files, maptype, atlastype, exportpath, atlasjson=None, repack=False):
        self.maptype = maptype
        self.atlastype = atlastype
        self.atlasjson = atlasjson
        self.repack = repack

        if atlasjson:
            self.padding = atlasjson["padding"]
        else:
            if bpy.context.scene.decals.atlaspadding == -1:  # grab default value from prefs
                bpy.context.scene.decals.atlaspadding = m3.DM_prefs().atlaspadding
            self.padding = bpy.context.scene.decals.atlaspadding

        if self.maptype == "ao_curv_height":
            self.bgcolor = (255, 128, 128)
        elif self.maptype == "nrm_alpha":
            # self.bgcolor = (128, 128, 255)
            self.bgcolor = (128, 128, 255, 0)
        elif self.maptype == "color":
            self.bgcolor = (0, 0, 0, 0)
        elif self.maptype == "subset":
            self.bgcolor = (0, 0, 0)

        # create_atlas() returns a list of 9 solutions, sorted from best to worst, based on least free space
        atlases = self.create_atlas(files)

        for idx, atlas in enumerate(atlases):
            atlasimg = atlas[0]
            if self.atlasjson is None or self.repack is True:
                # for new packs and for re-packs take the json from the previous packing solution
                atlasjson = atlas[1]
            else:
                # for packs based on an existing solution take the json thats passed in
                atlasjson = self.atlasjson

            freespace = str(atlasjson["free"])
            atlasw, atlash = atlasjson["size"]
            pack = atlasjson["pack"]
            sortby = atlasjson["sortby"]

            if atlasjson["downsample"]:
                downatlasw, downatlash = atlasjson["downsamplesize"]
                downsamplestring = "(downsampled to %ix%i)" % (downatlasw, downatlash)
            else:
                downsamplestring = ""

            atlaspath = os.path.join(exportpath, "atlas_" + self.maptype + ".png")
            jsonpath = os.path.join(exportpath, "atlas_" + self.atlastype + ".json")

            if idx == 0:
                if self.atlasjson is None or self.repack is True:
                    print("BEST SOLUTION: %ix%i%s with %s%% free space. %s algorithm, sorted by %s." % (atlasw, atlash, downsamplestring, freespace, pack, sortby))
                    save_json(atlasjson, jsonpath)
                else:
                    print("EXISTING SOLUTION: %ix%i%s with %s%% free space. %s algorithm, sorted by %s." % (atlasw, atlash, downsamplestring, freespace, pack, sortby))

                    # if it's a pack using an existing solution, remove the current maptype from the DM_atlas group ["maptypes"] list
                    # for intial packs and re-packs this is done in the AcceptAtlasSolution operator
                    maptypes = bpy.data.groups['DM_atlas_' + self.atlastype]['maptypes']
                    maptypes.remove(self.maptype)
                    bpy.data.groups['DM_atlas_' + self.atlastype]['maptypes'] = maptypes
                    print("%s Atlas - '%s' pack completed." % (self.atlastype.upper(), self.maptype))
                    print(" --- ")

                atlasimg.save(atlaspath)

                # we only need the first solution, the others are for testing and debugging only, so breaking after the first iteration
                break
            elif atlas == atlases[-1]:
                print("WORST SOLUTION: %ix%i with %s%% free space. %s algorithm, sorted by %s." % (atlasw, atlash, freespace, pack, sortby))
            else:
                print("SOME SOLUTION: %ix%i with %s%% free space. %s algorithm, sorted by %s." % (atlasw, atlash, freespace, pack, sortby))

        # set self.atlasjson to expose the proper solution to the Atlas object, no matter if it was created or passed in
        self.atlasjson = atlasjson

    def insert(self, atlasimage, image, posx, posy):
        atlasimage.paste(image, (posx, posy))

    def get_free_space(self, freeboxes, atlaswidth, atlasheight, show=False):
        if show:
            atlas = Image.new("RGB", (atlaswidth, atlasheight), color=(100, 0, 0))

        freearea = 0
        counter = 0
        for freeb in freeboxes:
            counter += 1
            posx = freeb[1]
            posy = freeb[2]
            width = freeb[3]
            height = freeb[4]

            area = width * height
            freearea += area

            if show:
                r = randint(0, 255)
                g = randint(0, 255)
                b = randint(0, 255)

                atlas.paste((r, g, b), (posx, posy, posx + width, posy + height))
        if show:
            atlas.show()

        return freearea

    # kivy algo, free boxes will always stretch to the max atlas res to the right
    def kivy_pack(self, freeboxes, freeb, imgw, imgh):
        p = self.padding * 2

        if freeb[3] > (imgw + p):
            freeboxes.append((freeb[0], freeb[1] + (imgw + p), freeb[2], freeb[3] - (imgw + p), (imgh + p)))

        if freeb[4] > (imgh + p):
            freeboxes.append((freeb[0], freeb[1], freeb[2] + (imgh + p), freeb[3], freeb[4] - (imgh + p)))

    def js_pack(self, freeboxes, freeb, imgw, imgh, alternative=False):
        p = self.padding * 2

        dw = freeb[3] - (imgw + p)
        dh = freeb[4] - (imgh + p)

        if not alternative:
            if dw > dh:
                freeboxes.append((freeb[0], freeb[1] + (imgw + p), freeb[2], dw, freeb[4]))
                freeboxes.append((freeb[0], freeb[1], freeb[2] + (imgh + p), (imgw + p), dh))
            else:
                freeboxes.append((freeb[0], freeb[1], freeb[2] + (imgh + p), freeb[3], dh))
                freeboxes.append((freeb[0], freeb[1] + (imgw + p), freeb[2], dw, (imgh + p)))
        else:
            if dh > dw:
                freeboxes.append((freeb[0], freeb[1] + (imgw + p), freeb[2], dw, freeb[4]))
                freeboxes.append((freeb[0], freeb[1], freeb[2] + (imgh + p), (imgw + p), dh))
            else:
                freeboxes.append((freeb[0], freeb[1], freeb[2] + (imgh + p), freeb[3], dh))
                freeboxes.append((freeb[0], freeb[1] + (imgw + p), freeb[2], dw, (imgh + p)))

    def nrm_alpha_resize(self, img, width, height, newwidth, newheight):
        # separately scale the normal and alpha and then re-combine
        # this alone improves the quality and gets rid of aliasing on the inside of the normal map
        # but then there's still a subtle border on the outside, unless we don't antialias the alpha at all and keep it crisp!
        nrmbg = Image.new('RGBA', (width, height), (128, 128, 255, 255))
        normal = Image.alpha_composite(nrmbg, img)
        normalresized = normal.resize((newwidth, newheight), Image.ANTIALIAS)

        alpha = img.split()[3]
        alpharesized = alpha.resize((newwidth, newheight))

        normalresized.putalpha(alpharesized)

        return normalresized

    # creates a list of atlases, sorted from best to worst packing solution
    # if self.atlasjson is not None, packing is based on the existing, supplied solution and the atlaslist contains only this one solution
    def create_atlas(self, filenames):
        images = []
        minarea = 0
        for f in filenames:
            fp = open(f, 'rb')
            img = Image.open(fp)
            img.load()
            fp.close()
            templatefilepath = f.replace("ao_curv_height", "MAPTYPE").replace("nrm_alpha", "MAPTYPE").replace("subset", "MAPTYPE")

            img_w = img.size[0]
            img_h = img.size[1]

            if self.atlasjson is None:
                # a new pack, take the images as they are
                scale = (1, 1)
                minarea += img_w * img_h
            else:
                # a pack based on an existing solution or a re-pack with adjusted scaling
                # in both cases, scale the images accordingly
                scalex = self.atlasjson["fullboxes"][templatefilepath][4]
                scaley = self.atlasjson["fullboxes"][templatefilepath][5]
                scale = (scalex, scaley)
                img_w_scaled = int(img_w * scalex)
                img_h_scaled = int(img_h * scaley)

                if self.maptype == "nrm_alpha":  # resizing the nrm_alpha, produces aliasing artifects, so instead scale nrm and alpha separately
                    img = self.nrm_alpha_resize(img, img_w, img_h, img_w_scaled, img_h_scaled)
                else:
                    img = img.resize((img_w_scaled, img_h_scaled), Image.ANTIALIAS)
                minarea += img_w_scaled * img_h_scaled

            images.append((templatefilepath, img, scale))

        if self.atlasjson is None or self.repack is True:
            if self.repack is True:
                print(" @@@ Re-Atlasing based on size modifications")
            else:
                print()
                print(" ### Initial Atlas creation")
            minres = int(sqrt(minarea))
            print("The minimally required resolution to fit all textures is %sx%s." % (minres, minres))
        else:
            print(" >>> Packing textures based on existing solution.")

        print("Atlas Type: %s | Map Type: %s" % (self.atlastype, self.maptype))

        p = self.padding * 2

        atlassolutions = []
        if self.atlasjson is None or self.repack is True:
            # figure out the best packing by sorting images in 3 different ways and going through three different packing alorithms
            # three ways to sort the texures and freeboxes
            for sortby in ["width", "height", "area"]:
                if sortby == "width":
                    images = sorted(images, key=lambda img: img[1].size[0], reverse=True)
                elif sortby == "height":
                    images = sorted(images, key=lambda img: img[1].size[1], reverse=True)
                elif sortby == "area":
                    images = sorted(images, key=lambda img: img[1].size[0] * img[1].size[1], reverse=True)

                for pack in ["kivy", "js", "jsalt"]:
                    size_w = size_h = minres - 1
                    while True:
                        size_w += 1
                        size_h += 1

                        # free boxes are empty space in our output image set, initially everything is one big freebox
                        # (atlasidx, x, y, w, h)
                        freeboxes = [(0, 0, 0, size_w, size_h)]

                        # full boxes are areas where we have placed images in the atlas
                        # (image, atlasidx, x, y, w, h, filename)
                        fullboxes = []

                        # do the actual atlasing by sticking the largest images (sorted by), we can have into the smallest valid free boxes
                        completepack = True
                        for filename, img, scale in images:
                            imgw, imgh = img.size

                            inserted = False
                            while not inserted:
                                for idx, freeb in enumerate(freeboxes):
                                    # find the smallest free box that will contain this image
                                    if (imgw + p) <= freeb[3] and (imgh + p) <= freeb[4]:
                                        # found a spot, remove the current freebox and split the leftover space into up to two new freeboxes
                                        del freeboxes[idx]

                                        # print("inserted '%s' (%d, %d) into freebox (%d, %d)" % (os.path.basename(filename), img.size[0], img.size[1], freeb[3], freeb[4]))

                                        if pack == "kivy":
                                            self.kivy_pack(freeboxes, freeb, imgw, imgh)
                                        elif pack == "js":
                                            self.js_pack(freeboxes, freeb, imgw, imgh)
                                        elif pack == "jsalt":
                                            self.js_pack(freeboxes, freeb, imgw, imgh, alternative=True)

                                        # sorting smallest first
                                        if sortby == "width":
                                            freeboxes = sorted(freeboxes, key=lambda freeb: freeb[3])
                                        elif sortby == "height":
                                            freeboxes = sorted(freeboxes, key=lambda freeb: freeb[4])
                                        elif sortby == "area":
                                            freeboxes = sorted(freeboxes, key=lambda freeb: freeb[3] * freeb[4])

                                        fullboxes.append((img, freeb[0], freeb[1], freeb[2], imgw, imgh, scale[0], scale[1], filename))
                                        inserted = True
                                        break

                                if not inserted:
                                    # could not find freebox big enough for the imgage, so the pack will be incomplete
                                    completepack = False
                                    break

                        if completepack:
                            # calculate free area to judge efficiency
                            freearea = self.get_free_space(freeboxes, size_w, size_h, show=False)
                            totalarea = size_w * size_h
                            free = float("%0.2f" % (freearea / totalarea * 100))

                            # create atlas json
                            atlasjson = {}
                            atlasjson["fullboxes"] = {}
                            atlasjson["freeboxes"] = freeboxes
                            atlasjson["free"] = free
                            atlasjson["pack"] = pack
                            atlasjson["sortby"] = sortby
                            atlasjson["size"] = (size_w, size_h)
                            atlasjson["atlastype"] = self.atlastype

                            if self.repack:
                                # grab the downsample bool and padding int from the json when doing a repack
                                atlasjson["downsample"] = self.atlasjson["downsample"]
                                atlasjson["padding"] = self.atlasjson["padding"]
                            else:
                                # for a new pack the default values should be used (False and 1, as defined in the __init__)
                                atlasjson["downsample"] = bpy.context.scene.decals.atlasdownsample
                                atlasjson["padding"] = bpy.context.scene.decals.atlaspadding

                            # initialize atlas image
                            atlasimg = Image.new('RGBA', (size_w, size_h))

                            # insert images into atlas and fill out the json with the fullbox elements
                            for fullb in fullboxes:
                                img = fullb[0]
                                posx = int(fullb[2] + (p / 2))
                                posy = int(fullb[3] + (p / 2))
                                imgw = fullb[4]
                                imgh = fullb[5]
                                scalex = fullb[6]
                                scaley = fullb[7]
                                filename = fullb[8]

                                self.insert(atlasimg, img, posx, posy)
                                atlasjson["fullboxes"][filename] = (posx, posy, imgw, imgh, scalex, scaley)

                            # composite the atlas over an image filled with the appropriate color for the maptype
                            # this is necessary(as opposed to using the bgcolor directly on the atlasimg),
                            # because the nrm_alpha textures or color textures are transparent and inserting them would replace the bg color
                            atlasbg = Image.new('RGBA', (size_w, size_h), self.bgcolor)
                            atlas = Image.alpha_composite(atlasbg, atlasimg)

                            # when downsampling is turn on, scaled the atlas image down to the closest power of two res, that's below
                            if atlasjson["downsample"]:
                                atlas, atlasjson = self.downsample_atlas(atlas, atlasjson)

                            atlassolutions.append((atlas, atlasjson))
                            del atlasimg, atlasbg, atlas
                            break
                        else:
                            # print("Resolution or packing settings not sufficient for complete pack.")
                            pass
        else:
            # pack images using the solution supplied via the atlasjson
            size_w, size_h = self.atlasjson["size"]
            fullboxes = self.atlasjson["fullboxes"]

            # initialize atlas image
            atlasimg = Image.new('RGBA', (size_w, size_h))

            for filename, img, _ in images:
                posx = fullboxes[filename][0]
                posy = fullboxes[filename][1]
                self.insert(atlasimg, img, posx, posy)

            atlasbg = Image.new('RGBA', (size_w, size_h), self.bgcolor)
            atlas = Image.alpha_composite(atlasbg, atlasimg)

            if self.atlasjson["downsample"]:
                atlas, self.atlasjson = self.downsample_atlas(atlas, self.atlasjson)

            atlassolutions.append((atlas, self.atlasjson))
            del atlasimg, atlasbg, atlas

        return sorted(atlassolutions, key=lambda a: a[1]["size"])

    def layout_atlas(self):
        # create atlas scene and switch to it
        layoutscene = bpy.data.scenes.new("DECALatlas")
        bpy.context.screen.scene = layoutscene

        # fetch downsample bool
        layoutscene.decals.atlasdownsample = self.atlasjson["downsample"]
        layoutscene.decals.atlaspadding = self.atlasjson["padding"]

        layoutscene.render.engine = "CYCLES"
        bpy.context.space_data.viewport_shade = 'MATERIAL'

        # filmic
        if bpy.app.version >= (2, 79, 0):
            bpy.context.scene.view_settings.view_transform = 'Filmic'
            bpy.context.scene.view_settings.look = 'Filmic - Base Contrast'
            bpy.context.scene.sequencer_colorspace_settings.name = 'sRGB'
        else:
            try:  # pre-2.79 filmic
                bpy.context.scene.view_settings.view_transform = 'Filmic Log Encoding Base'
                bpy.context.scene.view_settings.look = 'Base Contrast'
                bpy.context.scene.sequencer_colorspace_settings.name = 'Filmic Log Encoding'
            except:
                pass

        # save the atlastype and maptype to the scene, we'll need these when accepting the atlas solution
        bpy.context.scene.decals.atlastype = self.atlastype
        bpy.context.scene.decals.maptype = self.maptype

        # turn off grid floor
        bpy.context.space_data.show_floor = False

        layertuple = (True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)

        # add meta data of the packing solution via text objects
        # resolution text
        bpy.ops.object.text_add(radius=0.20, view_align=False, enter_editmode=False, location=(0, 0.05, 0), layers=layertuple)
        typeres = m3.get_active()
        typeres.name = str(self.atlasjson["size"][0]) + " x " + str(self.atlasjson["size"][1])
        if self.atlasjson["downsample"]:
            typeres.data.body = str(self.atlasjson["downsamplesize"][0]) + " x " + str(self.atlasjson["downsamplesize"][1]) + "(downsampled)"
        else:
            typeres.data.body = str(self.atlasjson["size"][0]) + " x " + str(self.atlasjson["size"][1])
        typeres.hide_select = True
        m3.lock(typeres)

        # free space text
        bpy.ops.object.text_add(radius=0.15, view_align=False, enter_editmode=False, location=(0, 0.25, 0), layers=layertuple)
        typefree = m3.get_active()
        typefree.name = str(self.atlasjson["free"]) + "% free space"
        typefree.data.body = str(self.atlasjson["free"]) + "% free space"
        typefree.hide_select = True
        m3.lock(typefree)

        # algorithm text
        bpy.ops.object.text_add(radius=0.1, view_align=False, enter_editmode=False, location=(0, 0.42, 0), layers=layertuple)
        typealgo = m3.get_active()
        typealgo.name = "algorithm: " + str(self.atlasjson["pack"]) + " | " + str(self.atlasjson["sortby"])
        typealgo.data.body = "algorithm: " + str(self.atlasjson["pack"]) + " | " + str(self.atlasjson["sortby"])
        typealgo.hide_select = True
        m3.lock(typealgo)

        # background plane
        resx = self.atlasjson["size"][0] / 1000
        resy = self.atlasjson["size"][1] / 1000
        bpy.ops.mesh.primitive_plane_add(radius=0.5, view_align=False, location=(0, 0, -0.01), layers=layertuple)
        bgplane = bpy.context.active_object
        bgplane.name = "atlas_background"
        bgplane.dimensions = (resx, resy, 1)
        bgplane.location[0] = resx / 2
        bgplane.location[1] = -(resy / 2)
        m3.set_mode("EDIT")
        bpy.ops.mesh.subdivide(number_cuts=30, smoothness=0)
        bpy.ops.mesh.unsubdivide(iterations=1)
        m3.set_mode("EDGE")
        m3.unselect_all("MESH")
        m3.set_mode("OBJECT")
        bgplane.data.edges[0].select = True
        m3.set_mode("EDIT")
        bpy.ops.mesh.select_similar(type='DIR', threshold=0.01)
        bpy.ops.mesh.dissolve_mode(use_verts=True)
        m3.set_mode("OBJECT")
        bgplane.show_all_edges = True
        bgplane.show_wire = True
        bgplane.draw_type = 'BOUNDS'
        bgplane.hide_select = True

        fullboxes = self.atlasjson["fullboxes"]

        if self.atlastype == "decal":
            # decals02_31_MAPTYPE.png
            textureRegex = re.compile(r"([\w]+)\_MAPTYPE\.png")
        elif self.atlastype == "info":
            # info01_08_caution_only_use_non-magnetic_fastners.png
            textureRegex = re.compile(r"((c_)?info[\d]{2}_[\d]{2,3}_)[\w-]+\.png")

        for fullb in sorted(fullboxes):
            filename = os.path.basename(fullb)
            mo = textureRegex.match(filename)
            decalname = "atlas_" + mo.group(1)

            # set preview texture based on atlastype
            if self.atlastype == "decal":
                # previewtex = bpy.data.images[filename.replace("MAPTYPE", "ao_curv_height")]
                # usually the images in blender are called 'c_decals01_03_ao_curv_height.png'
                # but sometimes they will be 'c_decals01_03_ao_curv_height.png.001' or similar
                # this will then result in an exception as the image can't be found
                texturebasename = filename.replace("MAPTYPE", "ao_curv_height")

                try:
                    previewtex = bpy.data.images[texturebasename]
                except KeyError:
                    print(texturebasename, " not found, looking for duplicates.")
                    for image in bpy.data.images:
                        if image.name.startswith(texturebasename):
                            print(image.name, "is a match")
                            previewtex = image
                            break

            elif self.atlastype == "info":
                try:
                    previewtex = bpy.data.images[filename]
                except KeyError:
                    print(filename, " not found, looking for duplicates.")
                    for image in bpy.data.images:
                        if image.name.startswith(filename):
                            print(image.name, "is a match")
                            previewtex = image
                            break

            # create plane for each packed texture, scale and align it according to the packing solution
            # NOTE: the plane width and height can't be based on thefullbox width and height, they must be based on the imagesize * scale parameters
            scalex = fullboxes[fullb][4]
            scaley = fullboxes[fullb][5]

            width = previewtex.size[0] * scalex / 1000
            height = previewtex.size[1] * scaley / 1000

            posx = fullboxes[fullb][0] / 1000 + width / 2
            posy = -(fullboxes[fullb][1] / 1000 + height / 2)

            bpy.ops.mesh.primitive_plane_add(radius=0.5, view_align=False, location=(posx, posy, 0), layers=layertuple)
            textureplane = bpy.context.active_object
            textureplane.name = decalname
            textureplane.dimensions = (width, height, 0)
            textureplane["filepath"] = fullb

            # scale the planes according to the image size * scale values from the json
            # and make sure the scale transform in blender represents it properly
            # this way a scaled textureimage is represented by a scaled plane
            textureplane.scale = (textureplane.scale[0] * 1 / scalex, textureplane.scale[1] * 1 / scaley, 1)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            textureplane.scale = (textureplane.scale[0] * scalex, textureplane.scale[1] * scaley, 1)
            m3.lock(textureplane, scale=False)

            # apply constraint to prevent scaling above 1, which is useless as it would be above the decal texture resolution
            limitscale = textureplane.constraints.new(type="LIMIT_SCALE")
            limitscale.use_max_x = True
            limitscale.use_max_y = True
            limitscale.use_max_z = True
            limitscale.max_x = 1
            limitscale.max_y = 1
            limitscale.max_z = 1
            limitscale.use_transform_limit = True

            # do UVs + create and assign material
            m3.make_active(textureplane)
            bpy.ops.object.material_slot_add()

            m3.set_mode("EDIT")
            m3.set_mode("FACE")
            bpy.ops.uv.reset()
            m3.set_mode("OBJECT")

            mat = bpy.data.materials.new(decalname)
            textureplane.material_slots[0].material = mat
            mat.use_nodes = True
            tree = mat.node_tree

            imgnode = tree.nodes.new("ShaderNodeTexImage")
            imgnode.image = previewtex
            imgnodeout = imgnode.outputs['Color']
            diffusenode = tree.nodes['Diffuse BSDF']
            diffusenodein = diffusenode.inputs['Color']
            tree.links.new(imgnodeout, diffusenodein)

            # transparent color maps for info decals need a more complex node setup
            if self.atlastype == "info":
                imgnodealphaout = imgnode.outputs['Alpha']
                diffusenodeout = diffusenode.outputs['BSDF']
                mixnode = tree.nodes.new("ShaderNodeMixShader")
                mixnodefactor = mixnode.inputs[0]
                mixnodeshader1 = mixnode.inputs[1]
                mixnodeshader2 = mixnode.inputs[2]
                mixnodeout = mixnode.outputs['Shader']
                transparentnode = tree.nodes.new("ShaderNodeBsdfTransparent")
                transparentnodeout = transparentnode.outputs["BSDF"]
                invertnode = tree.nodes.new("ShaderNodeInvert")
                invertnodein = invertnode.inputs['Color']
                invertnodeout = invertnode.outputs['Color']
                materialoutput = tree.nodes['Material Output'].inputs['Surface']

                tree.links.new(diffusenodeout, mixnodeshader1)
                tree.links.new(transparentnodeout, mixnodeshader2)
                tree.links.new(imgnodealphaout, invertnodein)
                tree.links.new(invertnodeout, mixnodefactor)
                tree.links.new(mixnodeout, materialoutput)

                mat.game_settings.alpha_blend = 'CLIP'

        # without this, you can't undo and then redo to the latest atlas representation
        bpy.ops.ed.undo_push(message="DECALmachine: Atlasing")

    def downsample_atlas(self, atlasimg, atlasjson):
        sizex = atlasimg.size[0]
        sizey = atlasimg.size[1]

        # find the power of two resolution below the current atlas resolution
        resolutions = [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
        restuples = list(enumerate(resolutions))

        for idx, res in restuples:
            if res <= sizex < restuples[idx + 1][1]:
                resx = res

        for idx, res in restuples:
            if res <= sizey < restuples[idx + 1][1]:
                resy = res

        if self.maptype == "nrm_alpha":
            downsampled = self.nrm_alpha_resize(atlasimg, sizex, sizey, resx, resy)
        else:
            downsampled = atlasimg.resize((resx, resy), Image.ANTIALIAS)

        atlasjson["downsamplesize"] = (resx, resy)

        return downsampled, atlasjson
