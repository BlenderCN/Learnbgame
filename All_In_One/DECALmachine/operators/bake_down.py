import bpy
from PIL import Image
import os
from .. import M3utils as m3
from .. utils.operators import makedir


class DecalBakeDown():
    def __init__(self, selection, exportpath, bakedowngroups):
        # get selection
        self.selection = selection

        # get path
        self.exportpath = makedir(os.path.join(exportpath, "DECALBakeDown"))

        # get current scene
        self.currentscene = bpy.context.scene

        # get bake settings
        bakeresolution = self.currentscene.decals.bakedownresolution
        bakedistance = self.currentscene.decals.bakedowndistance
        bakebias = self.currentscene.decals.bakedownbias
        baketransfersharps = self.currentscene.decals.bakedowntransfersharps
        bakecombine = self.currentscene.decals.bakedowncombine
        bakecombineall = self.currentscene.decals.bakedowncombineall

        print("\nBaking down to '%dx%d', distance: '%f', bias: '%f'" % (bakeresolution, bakeresolution, bakedistance, bakebias))

        # get maptypes to bake down
        decalsmaptypes, infomaptypes = self.get_maptypes()

        # create and setup DECALBakeDown scene
        self.bakedownscene = self.create_bakedown_scene()

        # create a plain material for the bake targets
        # this is done so non-normal maps can receive a properly colored background when baked according to the maptype
        targetmat = bpy.data.materials.new("baketarget")

        # prepare for baking

        materialdict = {}

        for group in bakedowngroups:
            m3.unselect_all("OBJECT")
            print()
            print("Baking down group '%s'." % (group.name))

            if bakecombine and bakecombineall:  # this overrides the per material combination and instead combines everything as if it had a single material
                group['material'] = "combined"

            target, decals, info = self.get_objects(group, materialdict, targetmat)

            # bake and keep track of what maps have been baked and their pathes (for the alpha_fix())
            bakedmaps = []

            # bake decals
            if decals:
                decalsmat = bpy.data.materials.new("bakedown_" + decals.name + "_" + target.name)
                decals.data.materials.append(decalsmat)

                if baketransfersharps:
                    self.transfer_sharps(target, decals, bakedistance)

                for bake in decalsmaptypes:
                    m3.unselect_all("OBJECT")
                    p = self.bake_down(target, targetmat, decals, decalsmat, "decals", bake, bakeresolution, bakedistance, bakebias)
                    bakedmaps.append(p)

                    # each bake gets appended to the existing map list, or iniates a list on its own
                    try:
                        materialdict[group["material"]][p[2]].append(p[0])
                    except:
                        materialdict[group["material"]][p[2]] = [p[0]]

            # bake info decals
            if info:
                infomat = bpy.data.materials.new("bakedown_" + info.name + "_" + target.name)
                info.data.materials.append(infomat)

                for bake in infomaptypes:
                    m3.unselect_all("OBJECT")
                    p = self.bake_down(target, targetmat, info, infomat, "info", bake, bakeresolution, bakedistance, bakebias)
                    bakedmaps.append(p)

                    # each bake gets appended to the existing map list, or iniated a list on its own
                    try:
                        materialdict[group["material"]][p[2]].append(p[0])
                    except:
                        materialdict[group["material"]][p[2]] = [p[0]]

            # mask out baked maps using the alpha bake and composite the result with a bg color according to the map type
            # this is done so areas outside the decals don't contribute to the bakes. otherwise the bakes might introduce some normal shading issues for instance
            self.alpha_fix(bakedmaps)

        if bakecombine:
            self.combine_materials(materialdict)

        print("\n" + 40 * "-" + "\n")

        # go back to the original scene
        bpy.context.screen.scene = self.currentscene

    def get_objects(self, group, materialdict, targetmat):
        # each material gets it's own dictionary in the materialdict
        if group["material"] not in materialdict:
            materialdict[group["material"]] = {}
            materialdict[group["material"]]["combined"] = {}

        # find decal types among selection and clear out materials
        decals = None
        info = None

        for obj in group.objects:
            self.bakedownscene.objects.link(obj)

            if obj["DM"]["isdecal"] and obj.active_material.name == "decals":
                decals = obj
            elif obj["DM"]["isdecal"] and obj.active_material.name == "info_decals":
                info = obj

            # clean out materials
            obj.data.materials.clear(update_data=True)

        # get target - determined via ExportGroup() - and assign targetmat, whose color will be changed depending on the type of bake (maptype)
        target = bpy.data.objects[group["target"]]
        target.data.materials.append(targetmat)

        return target, decals, info

    def create_bakedown_scene(self):
        bakedownscene = bpy.data.scenes.new("DECALBakeDown")
        bpy.context.screen.scene = bakedownscene

        # set BI as the render for baking
        bakedownscene.render.engine = 'BLENDER_RENDER'

        # filmic - mostly to surpress warnings(as a new scene will have no view transform at all with filmic installed), should have no effect on the bakes
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

        return bakedownscene

    def get_maptypes(self):
        bakeao = self.currentscene.decals.bakedownmapao
        bakecurvature = self.currentscene.decals.bakedownmapcurvature
        bakeheight = self.currentscene.decals.bakedownmapheight
        bakenormal = self.currentscene.decals.bakedownmapnormal
        bakesubset = self.currentscene.decals.bakedownmapsubset
        bakecolor = self.currentscene.decals.bakedownmapcolor

        sbsnaming = self.currentscene.decals.bakedownsbsnaming

        # create maptypes list

        decalsmaptypes = []
        if bakeao:
            if sbsnaming:
                decalsmaptypes.append("ambient_occlusion")
            else:
                decalsmaptypes.append("ao")
        if bakecurvature:
            decalsmaptypes.append("curvature")
        if bakeheight:
            decalsmaptypes.append("height")
        if bakenormal:
            if sbsnaming:
                decalsmaptypes.append("normal_base")
            else:
                decalsmaptypes.append("normal")
        if bakesubset:
            if sbsnaming:
                decalsmaptypes.append("id")
            else:
                decalsmaptypes.append("subset")

        infomaptypes = []
        if bakecolor:
            infomaptypes.append("color")

        # always add alpha and bakedown masks, if the maptype lists are populated
        if decalsmaptypes:
            decalsmaptypes.insert(0, "alpha")
            if "mask" not in infomaptypes:  # alpha(opacity) is maptype specific, mask is not. so mask only needs to be added to one of either, in fact adding it to both will cause problems
                decalsmaptypes.insert(1, "mask")

        if infomaptypes:
            infomaptypes.insert(0, "alpha")
            if "mask" not in decalsmaptypes:  # alpha(opacity) is maptype specific, mask is not. so mask only needs to be added to one of either, in fact adding it to both will cause problems
                infomaptypes.insert(1, "mask")

        return decalsmaptypes, infomaptypes

    def combine_materials(self, materialdict):
        """ dictionary debug
            print()

            for mat in materialdict:
                print()
                print(mat)
                for m in materialdict[mat]:
                    print(" > " + m)
                    for path in materialdict[mat][m]:
                        print("   " + path)

            print()
        """

        # NOTE: combining is done repeately via pairs, first you combine 0 and 1 and save it, then you combine 2 with the saved and save, then 3 with the saved, etc
        for mat in materialdict:
            print()
            print("Combining maps for material/textureset '%s'." % (mat))
            for bake in materialdict[mat]:
                if bake in ["mask", "combined"]:  # skipping mask bakes, also skipping over "combined"
                    continue

                maps = materialdict[mat][bake]

                # no need to attempt to combine maps, when there's only one in a maps list
                if len(maps) > 1:
                    for idx, m in enumerate(maps):
                        combinedbasepath = makedir(os.path.join(self.exportpath, "Baked_Textures_Combined"))
                        combinedpath = os.path.join(combinedbasepath, mat + "_" + bake + ".png")

                        if idx == 0:  # skip the first, as it will be the bg for the second, etc
                            continue
                        elif idx == 1:
                            bgimgpath = maps[idx - 1]
                        else:
                            bgimgpath = combinedpath

                        imgpath = m
                        maskpath = materialdict[mat]["mask"][idx]

                        bgimg = Image.open(bgimgpath).convert("RGBA")
                        img = Image.open(imgpath).convert("RGBA")
                        mask = Image.open(maskpath).convert("L")

                        img.putalpha(mask)

                        combinedimg = Image.alpha_composite(bgimg, img)
                        combinedimg.save(combinedpath)

                        if idx + 1 == len(maps):
                            print("Combined '%s' bakes to '%s'" % (bake, combinedpath))

                        # add the combined path to the dict
                        if bake not in materialdict[mat]["combined"]:
                            materialdict[mat]["combined"][bake] = combinedpath

    def transfer_sharps(self, target, decal, distance):
        m3.make_active(decal)

        bpy.ops.mesh.customdata_custom_splitnormals_clear()

        data_transfer = decal.modifiers.new("TransferSharps", "DATA_TRANSFER")
        data_transfer.object = target
        data_transfer.use_edge_data = True
        data_transfer.edge_mapping = 'EDGEINTERP_VNORPROJ'
        data_transfer.data_types_edges = {'SHARP_EDGE'}
        data_transfer.ray_radius = distance

        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="TransferSharps")

        print("Transfered sharps from '%s' to '%s'" % (target.name, decal.name))

    def alpha_fix(self, mappaths):
        # NOTE: it looks like we don't need to apply the alpha fix to the info decals maps?
        # or maybe save it alpha masked with transparency intact?
        print("\nApplying alpha to bakes.")

        decals = []
        decalsalpha = None
        for path, dtype, bake in mappaths:
            if dtype == "decals":
                decals.append((path, bake))
                if path.endswith("_alpha.png"):
                    decalsalpha = (path, bake)

        if decalsalpha:
            a = Image.open(decalsalpha[0]).convert("L")

            for path, bake in decals:
                if bake in ["alpha", "mask", "subset", "id"]:  # skip these, no need to alpha mask them
                    continue

                img = Image.open(path)
                img.putalpha(a)  # adds the alpha channel, even converts to RGBA for us

                if bake in ["ao", "ambient_occlusion"]:
                    bgcolor = (255, 255, 255, 255)
                elif bake in ["curvature", "height"]:
                    bgcolor = (128, 128, 128, 255)
                elif bake in ["normal", "normal_base"]:
                    bgcolor = (128, 128, 255, 255)

                bg = Image.new("RGBA", img.size, color=bgcolor)

                newimg = Image.alpha_composite(bg, img)

                newimg.save(path)

                print("Alpha-fixed '%s'." % (os.path.basename(path)))

                del img, bg, newimg

            del a

    def bake_down(self, tobj, tmat, dobj, dmat, dtype, bake, resolution, distance, bias):
        # LOAD + ASSIGN DECAL TEXTURE

        if bake != "mask":  # only load a source texture for non-mask bakes
            tpath = os.path.join(self.exportpath, "Atlas_Textures", dtype + "_" + bake + ".png")

            tmap = bpy.data.images.load(tpath)
            # tmap.colorspace_settings.name = 'Linear'

            texture = bpy.data.textures.new(dmat.name.upper() + "_" + bake.upper(), "IMAGE")
            texture.image = tmap
            # texture.use_alpha = False
            if bake in ["normal", "normal_base"]:
                texture.use_normal_map = True
            else:
                texture.use_normal_map = True

            slot = dmat.texture_slots.add()
            slot.texture = texture

            if bake in ["normal", "normal_base"]:
                slot.use_map_normal = True
                slot.use_map_color_diffuse = False
            else:
                slot.use_map_normal = False
                slot.use_map_color_diffuse = True
            # mat.use_cubic = True

        # SETUP BAKE TEXTURE

        tobj.select = True
        m3.make_active(tobj)

        m3.set_mode("EDIT")
        m3.set_mode("FACE")
        m3.unhide_all("MESH")
        m3.select_all("MESH")

        # create and assign a new image to the bake target
        oldcontext = m3.change_context("IMAGE_EDITOR")

        bakeddown = bpy.data.images.new(name="%s_bake" % (bake), width=resolution, height=resolution, alpha=False)
        for area in bpy.context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = bakeddown

        m3.change_context(oldcontext)
        m3.set_mode("OBJECT")

        dobj.select = True

        # SETUP BAKE SETTINGS

        # prepare bake
        if bake in ["normal", "normal_base"]:
            self.bakedownscene.render.bake_type = 'NORMALS'
        elif bake == "mask":
            self.bakedownscene.render.bake_type = 'ALPHA'
        else:
            self.bakedownscene.render.bake_type = 'TEXTURE'

        if bake == "mask":
            self.bakedownscene.render.use_bake_selected_to_active = False
        else:
            self.bakedownscene.render.use_bake_selected_to_active = True

        self.bakedownscene.render.bake_distance = distance
        self.bakedownscene.render.bake_bias = bias

        bpy.data.use_autopack = False

        # set target backround color
        tmat.diffuse_intensity = 1

        if bake in ["alpha", "subset", "id", "color"]:
            tmat.diffuse_color = (0, 0, 0)
        elif bake in ["ao", "ambient_occlusion"]:
            tmat.diffuse_color = (1, 1, 1)
        elif bake in ["curvature", "height"]:
            midgrey = pow(0.5, 2.2)
            tmat.diffuse_color = (midgrey, midgrey, midgrey)

        if dtype == "info" and bake == "alpha":
            bake = "color_alpha"

        # bake
        savepath = os.path.join(makedir(os.path.join(self.exportpath, "Baked_Textures")), tobj.name + "_" + bake + ".png")
        bakeddown.filepath = savepath
        bpy.ops.object.bake_image()
        bakeddown.save()
        print("Baked '%s' map and saved it to '%s'." % (bake, savepath))
        return savepath, dtype, bake
