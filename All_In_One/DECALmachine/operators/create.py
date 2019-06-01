import bpy
from bpy.props import IntProperty, BoolProperty
import os
from random import random
from PIL import Image, ImageEnhance, ImageChops, ImageDraw, ImageFilter
import re
from shutil import copy, rmtree
from .. utils.operators import load_json, save_json, delete_all, makedir
from .. utils.asset_loader import update_asset_loaders
from .. import M3utils as m3

# TODO: resampling after bake processing? does it improve subset mask and nrm_alpha?


class InstantDecal(bpy.types.Operator):
    bl_idname = "machin3.instant_decal"
    bl_label = "MACHIN3: Instant Decal"

    resolution = IntProperty(default=512)
    paneling = BoolProperty(default=False)

    def execute(self, context):
        global assetpath
        global createpath
        global custom

        custom = bpy.context.user_preferences.addons['DECALmachine'].preferences.usecustomdecalslib

        if custom:
            assetpath = bpy.context.user_preferences.addons['DECALmachine'].preferences.customassetpath
        else:
            assetpath = bpy.context.user_preferences.addons['DECALmachine'].preferences.assetpath

        DMpath = bpy.context.user_preferences.addons['DECALmachine'].preferences.DMpath
        createpath = os.path.join(DMpath, "assets", "create")

        # depending on user priviledges, windows and mac may not like the script saving a previously unsaved scene
        try:
            bpy.ops.wm.save_mainfile()
        except:
            self.report({'ERROR'}, "Save your scene first!")
            return {'FINISHED'}

        currentblend = bpy.data.filepath

        print(60 * "-")
        print("\t BAKING")
        print()

        D = DecalBake("instant", self.resolution, self.paneling, self)

        if D.keepgoing:
            print(60 * "-")
            print("\t BAKE PROCESSING")
            print()

            ProcessBakes("instant")

            print(60 * "-")
            print("\t CREATE DECAL")
            print()

            DecalCreate("instant", deletebakes=True)

            update_asset_loaders()

        bpy.ops.wm.open_mainfile(filepath=currentblend)

        return {'FINISHED'}


class BatchDecal(bpy.types.Operator):
    bl_idname = "machin3.batch_decal"
    bl_label = "MACHIN3: Batch Decal"

    def execute(self, context):
        global assetpath
        global createpath
        global custom

        custom = bpy.context.user_preferences.addons['DECALmachine'].preferences.usecustomdecalslib

        if custom:
            assetpath = bpy.context.user_preferences.addons['DECALmachine'].preferences.customassetpath
        else:
            assetpath = bpy.context.user_preferences.addons['DECALmachine'].preferences.assetpath

        DMpath = bpy.context.user_preferences.addons['DECALmachine'].preferences.DMpath
        createpath = os.path.join(DMpath, "assets", "create")

        currentblend = bpy.data.filepath

        print(60 * "-")
        print("\t BAKE PROCESSING")
        print()

        ProcessBakes("batch")

        print(60 * "-")
        print("\t CREATE DECAL")
        print()

        DecalCreate("batch")

        bpy.ops.wm.open_mainfile(filepath=currentblend)

        return {'FINISHED'}


class DecalBake():
    def __init__(self, decalcreationtype, resolution, paneling, object):
        self.decalcreationtype = decalcreationtype
        self.resolution = resolution
        self.paneling = paneling

        selection = m3.selected_objects()
        if len(selection) == 0:
            self.keepgoing = False
            object.report({'ERROR'}, "Make a selection of objects first.")
            return

        self.low, self.high, self.scene = self.init_baking_geo(selection)

        bakes = self.bake_all()

        self.resize(bakes)
        self.mid_level(bakes)
        self.nrm2curv(bakes, gamma=2.2, radius=1, intensity=2, blurradius=1)
        self.keepgoing = True

    def init_baking_geo(self, selection):
        highpoly = selection
        currentscene = bpy.context.scene

        delete_all(keep=highpoly)

        m3.select(highpoly)
        m3.set_layer((True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        m3.show_only_layer(0)

        # set BI as the render for baking
        currentscene.render.engine = 'BLENDER_RENDER'

        # make sure there is a world, otherwise ao settings can't be set and an exception occurs
        if bpy.context.scene.world is None:
            world = bpy.data.worlds.new("World")
            bpy.context.scene.world = world

        # apply mods
        for obj in highpoly:
            m3.make_active(obj)
            for mod in obj.modifiers:
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

        # join
        bpy.ops.object.join()

        # set origin to center of object
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        # move to origin
        bpy.ops.object.location_clear()

        highjoined = bpy.context.active_object

        # get dimensions and find the biggest one
        dimx, dimy, dimz = highjoined.dimensions
        biggest = max([dimx, dimy, dimz])

        # normalize to be 1 unity max
        scaleratio = 1 / biggest

        highjoined.scale = highjoined.scale * scaleratio
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # get absolute object depth/height
        height = highjoined.dimensions[2]

        # create bake plane located slightly above it
        bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, height / 2 * 1.01), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        low = bpy.context.active_object

        # scale the plane to fit the highpoly geo, but be slightly smaller
        low.dimensions = highjoined.dimensions * 0.99
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # create UV's
        m3.set_mode("EDIT")
        m3.set_mode("FACE")
        bpy.ops.uv.reset()
        m3.set_mode("OBJECT")

        # align the lowpoly, this is not given, if the origin of the highpoly is offset due to angled geometry, as in 452_decal
        # the align tool, surprisingly aligns by dimension, not by origin, perfect!
        highjoined.select = True
        m3.make_active(highjoined)
        bpy.ops.object.align(align_axis={'X', 'Y'})
        low.select = False

        # for paneling we need the highpoly longer in x than the low, so as to avoid fading of AO at the borders
        # we do this by duplicating the highpoly on both sides
        if self.paneling:
            highjoinedright = highjoined.copy()
            highjoinedright.data = highjoined.data.copy()
            highjoinedleft = highjoined.copy()
            highjoinedleft.data = highjoined.data.copy()
            bpy.context.scene.objects.link(highjoinedright)
            bpy.context.scene.objects.link(highjoinedleft)
            highjoinedright.location[0] = highjoined.dimensions[0]
            highjoinedleft.location[0] = -highjoined.dimensions[0]
            highjoinedright.select = True
            highjoinedleft.select = True
            highjoined.select = True
            m3.make_active(highjoined)

            # the extended paneling should be a single merged mesh, so as to not produce an id map
            bpy.ops.object.join()
            m3.set_mode("EDIT")
            m3.set_mode("VERT")
            bpy.ops.mesh.reveal()
            m3.select_all("MESH")
            bpy.ops.mesh.remove_doubles()
            m3.set_mode("OBJECT")

        # split the highpoly object appart again in preparation for the id bake
        bpy.ops.mesh.separate(type='LOOSE')
        high = m3.selected_objects()

        m3.unselect_all("OBJECT")

        return low, high, currentscene

    def bake(self, bakestring):
        print("Baking '%s' map." % (bakestring))

        if bakestring == "ao":  # ao seems to be anti aliased, and since its also the longest back, we do it directly in 512 max
            resx = self.low.dimensions[0] / 0.99 * self.resolution
            resy = self.low.dimensions[1] / 0.99 * self.resolution
        else:  # normal and heigt, need to be scaled down to get rid of aliasing. so 1k bakes
            resx = self.low.dimensions[0] / 0.99 * self.resolution * 2
            resy = self.low.dimensions[1] / 0.99 * self.resolution * 2

        for obj in self.high:
            obj.select = True
            if bakestring == "id":
                m3.make_active(obj)
                for slot in obj.material_slots:
                    bpy.ops.object.material_slot_remove()
                mat = bpy.data.materials.new("color")
                mat.diffuse_color = random(), random(), random()
                mat.diffuse_intensity = 1
                obj.data.materials.append(mat)

        self.low.select = True
        m3.make_active(self.low)

        m3.set_mode("EDIT")
        m3.set_mode("FACE")
        m3.select_all("MESH")

        oldcontext = m3.change_context("IMAGE_EDITOR")
        bake = bpy.data.images.new(name="%s_bake" % (bakestring), width=resx, height=resy, alpha=False)
        for area in bpy.context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = bake
        m3.change_context(oldcontext)

        m3.set_mode("OBJECT")

        if bakestring == "normal":
            self.scene.render.bake_type = 'NORMALS'
            self.scene.render.bake_normal_space = 'TANGENT'
        elif bakestring == "height":
            self.scene.render.bake_type = 'DISPLACEMENT'
            self.scene.render.use_bake_normalize = False  # normalize HAS TO be off for height maps, without on, there all depths will be the same
        elif bakestring == "ao":
            bpy.context.scene.world.light_settings.use_ambient_occlusion = True
            bpy.context.scene.world.light_settings.samples = bpy.context.scene.decals.createaosamples
            self.scene.render.bake_type = 'AO'
            self.scene.render.use_bake_normalize = True
        elif bakestring == "id":
            self.scene.render.bake_type = 'TEXTURE'

        self.scene.render.use_bake_selected_to_active = True
        bpy.data.use_autopack = False

        # bake and save to temp folder
        savepath = makedir(os.path.join(createpath, self.decalcreationtype))
        bake.filepath = os.path.join(savepath, "instant_%s.png" % (bakestring))
        bpy.ops.object.bake_image()
        bake.save()

        # # paneling was scaled down in x for baking, but after baking we should put it back
        # if self.paneling:
            # bpy.ops.object.scale_clear()

        return bake.filepath, bakestring

    def bake_all(self):
        bakes = []
        bakes.append(self.bake("normal"))
        if not self.paneling:
            bakes.append(self.bake("height"))
        bakes.append(self.bake("ao"))

        if len(self.high) > 1:
            bakes.append(self.bake("id"))

        print()

        return bakes

    def resize(self, pathlist):
        size = self.resolution, self.resolution  # fallback res, should never be needed
        for path, maptype in sorted(pathlist):
            img = Image.open(path)
            if maptype == "ao":
                size = img.size  # just get the size
                del img
            else:
                print("Resampling '%s' map to %dx%d." % (maptype, size[0], size[1]))

                resized = img.resize(size, Image.ANTIALIAS)
                resized.save(path)
                del img
        print()

    def nrm2curv(self, pathlist, gamma, radius, intensity, blurradius):
        for path, maptype in pathlist:
            if maptype == "normal":
                print("Creating 'curvature' map.")
                img = Image.open(path).convert("RGB")
                img2 = self.set_gamma(img, gamma)

                r, g, _ = img2.split()

                rleft = ImageChops.offset(r, -radius, 0)
                rright = ImageChops.offset(r, radius, 0)
                gup = ImageChops.offset(g, 0, radius)
                gdown = ImageChops.offset(g, 0, -radius)

                img3x = ImageChops.subtract(rleft, rright, 1 / intensity / gamma, 128)
                img3y = ImageChops.subtract(gup, gdown, 1 / intensity / gamma, 128)

                screen = ImageChops.screen(img3x, img3y)
                multiply = ImageChops.multiply(img3x, img3y)

                curvature = Image.blend(screen, multiply, 0.5)
                curvpath = path.replace("_normal.png", "_curvature.png")

                if blurradius is None:
                    curvature.save(curvpath)
                else:
                    blurredcurv = curvature.filter(ImageFilter.GaussianBlur(radius=blurradius))
                    blurredcurv.save(curvpath)
                    del blurredcurv

                del curvature
                del multiply
                del screen
                del img3x
                del img3y
                del gdown
                del gup
                del rright
                del rleft
                del r
                del g
                del img2
                del img
                break
        print()

    def set_gamma(self, im, gamma):
        """Fast gamma correction with PIL's image.point() method"""
        # https://gist.github.com/mozbugbox/10cd35b2872628246140
        invert_gamma = 1.0 / gamma
        lut = [pow(x / 255., invert_gamma) * 255 for x in range(256)]
        lut = lut * 3  # need one set of data for each band for RGB
        im = im.point(lut)
        return im

    def mid_level(self, pathlist):
        for path, maptype in pathlist:
            if maptype == "height":
                print("Setting 'height' map mid-level.")
                img = Image.open(path)

                enhance = ImageEnhance.Contrast(img)
                img = enhance.enhance(bpy.context.scene.decals.createheightcontrast)

                enhance = ImageEnhance.Brightness(img)

                factor = 1
                while True:
                    lvl = enhance.enhance(factor)
                    p = lvl.getpixel((0, 0))
                    # print(p)

                    if p[0] == 128:
                        break
                    elif p[0] == 0:
                        # print("black heightmap")
                        data = lvl.getdata()

                        newData = []
                        for item in data:
                            newData.append((item[0] + 10, item[1] + 10, item[2] + 10, 255))

                        lvl.putdata(newData)
                        enhance = ImageEnhance.Brightness(lvl)  # without this the changes we put to lvl will be reset with the first line of the while loop
                    elif p[0] >= 129:
                        # print("small decrease")
                        factor -= 0.005
                    elif p[0] >= 123:
                        # print("small increase")
                        factor += 0.005
                    else:
                        # print("increase")
                        factor += 0.05

                # lvl.save(path[:-4] + "_mid_level.png")  # for testing: don't overwrite the height map
                lvl.save(path)

                del img
                break
        print()


class ProcessBakes():
    def __init__(self, decalcreationtype):
        maptypes, files = self.get_textures(os.path.join(createpath, decalcreationtype))
        decaldict = self.get_decal_types(maptypes, files)
        self.init_json(decaldict)

        for decal in sorted(decaldict):
            name = decal
            decaltype = decaldict[decal][0]
            bakes = sorted(decaldict[decal][1])

            self.process_textures(name, decaltype, bakes)

    def process_textures(self, decalname, decaltype, decalbakes):
        print(decalname)
        P = Process(decalname, decaltype, decalbakes)

        if decaltype == "info":
            print("info decal: copying color map")
            P.copy_color()
        elif decaltype == "subtractor":
            print("subtractor decal: creating ao_curv_height and nrm_alpha maps")
            P.create_ao_curv_height()
            P.create_nrm_alpha()
        elif decaltype == "subset":
            print("subset decal: creating ao_curv_height, nrm_alpha and subset maps")
            P.create_ao_curv_height()
            P.create_nrm_alpha()
            P.create_subset()
        elif decaltype == "paneling":
            print("panel decal: creating ao_curv_height, nrm_alpha and mat2_alpha maps")
            P.create_ao_curv_height(paneling=True)
            P.create_nrm_alpha()
            P.create_mat2_alpha()
        else:
            print("unsupported decal type: doing nothing")

        print()

    def get_textures(self, path):
        files = os.listdir(path)
        try:
            files.remove(".keep")
        except:
            pass

        mapdict = {}
        filedict = {}
        for f in files:
            # something_121_something_ao.png  > can be like this
            # something_ao.png  > needs to be at least like this
            mapRegex = re.compile(r"([\w]+)_([\w]+)\.png")
            mo = mapRegex.match(f)
            try:
                mapname = mo.group(1)
                maptype = mo.group(2)
                keepgoing = True
            except:
                keepgoing = False
                print("Skipping '%s', not properly named." % (f))

            if keepgoing:
                if mapname not in mapdict:
                    mapdict[mapname] = []
                mapdict[mapname].append(maptype)

                if mapname not in filedict:
                    filedict[mapname] = []
                filedict[mapname].append(os.path.join(path, f))

        return mapdict, filedict

    def get_decal_types(self, mapdict, filesdict):
        decaldict = {}
        for decalname in mapdict:
            decaldict[decalname] = ("", [])

        for decalname in mapdict:
            if set(mapdict[decalname]) == set(["ao", "curvature", "height", "normal", "id"]):
                decaldict[decalname] = "subset", filesdict[decalname]
            elif set(mapdict[decalname]) == set(["ao", "curvature", "height", "normal"]):
                decaldict[decalname] = "subtractor", filesdict[decalname]
            elif set(mapdict[decalname]) == set(["ao", "curvature", "normal"]):
                decaldict[decalname] = "paneling", filesdict[decalname]
            elif set(mapdict[decalname]) == set(["color"]):
                decaldict[decalname] = "info", filesdict[decalname]
            else:
                print("Skipping '%s', could not determine decaltype." % (decalname))
                decaldict.pop(decalname, None)

        print()
        return decaldict

    def init_json(self, decaldict):
        savedict = {}
        for decal in decaldict:
            savedict[decal] = {}
            savedict[decal]["type"] = decaldict[decal][0]
            savedict[decal]["maps"] = {}

        save_json(savedict, os.path.join(createpath, "processed.json"))


class Process():
    def __init__(self, decalname, decaltype, decaltextures):
        self.name = decalname
        self.type = decaltype
        self.textures = decaltextures

        if self.type == "subtractor":
            self.category = "decals01"
        elif self.type == "subset":
            self.category = "decals02"
        elif self.type == "paneling":
            self.category = "paneling01"
        elif self.type == "info":
            self.category = "info01"

        self.counter = str(self.get_decal_counter()).zfill(2)

        if self.name == "instant" or m3.DM_prefs().batchsuppressnaming:
            self.countername = self.counter  # 34
        else:
            self.countername = self.counter + "_" + self.name  # 34_awesome_decal

        if custom:
            self.filenamebase = "c_" + self.category.replace("decals", "decal") + "_" + self.countername  # c_decal02_34_awesome_decal
        else:
            self.filenamebase = self.category.replace("decals", "decal") + "_" + self.countername  # decal02_34_awesome_decal
        update_json_paths(self.name, self.category, self.countername, self.filenamebase)

    def get_map(self, maptypestring):
        maptail = "_" + maptypestring + ".png"

        for t in self.textures:
            if t.endswith(maptail):
                return t

    def build_save_path(self, maptailstring):
        basepath = os.path.join(assetpath, self.category, "blends", "textures")

        if custom:
            filename = "c_" + self.category + "_" + self.countername + maptailstring
        else:
            filename = self.category + "_" + self.countername + maptailstring

        return os.path.join(basepath, filename)

    def get_decal_counter(self):
        textures = os.listdir(os.path.join(assetpath, self.category, "blends", "textures"))

        # remove decal textures that don't follow the numbering pattern
        # and find the last decal counter
        texRegex = re.compile(r"(c_)?%s_([\d]{2})_[\w]+\.png" % (self.category))
        for b in sorted(textures):
            mo = texRegex.match(b)
            if mo is None:
                textures.remove(b)
            else:
                last = int(mo.group(2))

        try:
            if bpy.context.scene.decals.createreplacelast:
                return last
            else:
                return last + 1
        except:  # if nothing is in the folder and so last was not assigned
            return 1

    def eightbitify(self, image):
        if image.mode == "I":
            table = [i / 256 for i in range(65536)]
            return image.point(table, "L")
        else:
            return image.convert("L")

    def create_ao_curv_height(self, paneling=False):
        ao = self.eightbitify(Image.open(self.get_map("ao")))
        curv = self.eightbitify(Image.open(self.get_map("curvature")))
        if paneling is False:
            height = self.eightbitify(Image.open(self.get_map("height")))
        else:
            height = Image.new("L", ao.size, 128)

        combined = Image.merge("RGB", (ao, curv, height))

        savepath = self.build_save_path("_ao_curv_height.png")
        combined.save(savepath)
        update_json_maps(self.name, "ao_curv_height", savepath)

        del ao
        del curv
        del height
        print(" > %s_%s 'ao_curv_height' map has been created." % (self.category, self.countername))

    def create_nrm_alpha(self):
        img = Image.open(self.get_map("normal")).convert("RGBA")
        data = img.getdata()

        # flood fill has a 0 tolerance, but normal maps are imperfect and there's often slight deviations from the 128, 128, 255 normal color
        # so for floodfill to be able to work and fill all the outside parts, we need to first have that area in a unified color
        tolerance = m3.DM_prefs().normalalphatolerance

        if tolerance > 0:
            nvalue = 128

            nvalues = []
            for i in range(tolerance + 1):
                if i % 2 == 0:  # even
                    nvalue += i
                else:  # uneven
                    nvalue -= i

                nvalues.append(nvalue)

            newData = []

            for item in data:
                if item[0] in nvalues and item[1] in nvalues and item[2] == 255:
                    newData.append((128, 128, 255, 255))
                else:
                    newData.append(item)

            img.putdata(newData)

        # now we can use floodfill to fill only the outside parts, in this case with transparency!
        # do it in all 4 corners to be sure
        ImageDraw.floodfill(img, (0, 0), (0, 0, 0, 0))
        ImageDraw.floodfill(img, (img.size[0] - 1, 0), (0, 0, 0, 0))
        ImageDraw.floodfill(img, (0, img.size[1] - 1), (0, 0, 0, 0))
        ImageDraw.floodfill(img, (img.size[0] - 1, img.size[1] - 1), (0, 0, 0, 0))

        savepath = self.build_save_path("_nrm_alpha.png")
        img.save(savepath)
        update_json_maps(self.name, "nrm_alpha", savepath)

        del img
        print(" > %s_%s 'nrm_alpha' map has been created." % (self.category, self.countername))

    def create_subset(self):
        img = Image.open(self.get_map("id")).convert("RGBA")
        data = img.getdata()

        corner = img.getpixel((0, 0))

        newData = []
        for item in data:
            if item == corner:
                newData.append((0, 0, 0, 255))
            else:
                newData.append((255, 255, 255, 255))

        img.putdata(newData)

        savepath = self.build_save_path("_subset.png")
        img.save(savepath)
        update_json_maps(self.name, "subset", savepath)

        del img
        print(" > %s_%s 'subset' mask has been created." % (self.category, self.countername))

    def create_mat2_alpha(self):
        size = w, h = Image.open(self.get_map("normal")).size

        img = Image.new("L", size, 0)
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (w, h / 2)], fill=255)

        savepath = self.build_save_path("_mat2_alpha.png")
        img.save(savepath)
        update_json_maps(self.name, "mat2_alpha", savepath)

        del img
        print(" > %s_%s 'mat2_alpha' map has been created." % (self.category, self.countername))

    def copy_color(self):
        savepath = self.build_save_path(".png")
        copy(self.get_map("color"), savepath)
        update_json_maps(self.name, "color", savepath)

        print(" > %s_%s 'color' map has been created." % (self.category, self.countername))


class DecalCreate():
    def __init__(self, decalcreationtype, deletebakes=True):
        bpy.context.scene.render.engine = 'CYCLES'

        self.decalcreationtype = decalcreationtype
        self.decaldict = load_json(os.path.join(createpath, "processed.json"))

        for decal in self.decaldict:
            delete_all()
            m3.set_layer((True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            m3.show_only_layer(0)

            decaltype, decalmaps, counter_name, blendpath, thumbpath = self.get_data(decal)

            self.append(decaltype)

            D = Create(counter_name, self.decalcreationtype)
            D.apply_textures(decalmaps)
            D.scale_decal()
            D.render_thumb(thumbpath, decaltype)
            D.save_decal(blendpath)

            print(30 * "-")
            print("DECAL created.")
            print()

        if deletebakes:
            if self.decalcreationtype == "instant":
                rmtree(os.path.join(createpath, "instant"))
        # let's keep the files for batch decal creation around for now

    def append(self, typestring):
        if bpy.app.version >= (2, 79, 0):
            path = os.path.join(createpath, "templates", typestring.upper() + ".blend", "Group")
        else:
            path = os.path.join(createpath, "templates", typestring.upper() + "_old.blend", "Group")

        print(path)
        bpy.ops.wm.append(directory=path, filename="Group")

    def get_data(self, decalname):
        decaltype = self.decaldict[decalname]["type"]
        decalmaps = self.decaldict[decalname]["maps"]
        counter_name = self.decaldict[decalname]["counter_name"]
        blendpath = self.decaldict[decalname]["blendpath"]
        thumbpath = self.decaldict[decalname]["thumbpath"]
        return decaltype, decalmaps, counter_name, blendpath, thumbpath


class Create():
    def __init__(self, counter_name, decalcreationtype):
        bpy.ops.group.objects_remove_all()  # ungroup, as we don't want the group in the exported decal blend

        self.counter_name = counter_name
        self.decalcreationtype = decalcreationtype

        print()
        print(self.counter_name)
        print(len(self.counter_name) * "=")
        print()

        for obj in bpy.data.objects:
            if "_TEMPLATE" in obj.name:
                bpy.context.scene.objects.active = obj
                self.active = obj
                self.active.name = obj.name.replace("TEMPLATE", self.counter_name)
                if custom:
                    self.active.name = "c_" + self.active.name
                obj.select = True
            elif "Camera" in obj.name:
                self.camera = obj
                obj.select = False
            else:
                obj.select = False

    def apply_textures(self, maps):
        mat = self.active.material_slots[0].material
        mat.name = mat.name.replace("TEMPLATE", self.counter_name)
        if custom:
            mat.name = "c_" + mat.name

        #NOTE: not sure why yet, but whith intant creation ...load(maps["nrm_alpha"] will end up as a proper relative path in the decal blend, great!
        #####  but doing the same whith batch creation will lead to absolute paths for everyone but the first one
        #####  now, doing relpath() around it, works perfectly for batching,
        #####  but will produce a ridiculously long relative path for instant creation instead of just "//textures/..."

        #NOTE: an alternative might be to assign the file normaly, save the decal blend run the make relative op and save again

        heightmap = False
        for node in mat.node_tree.nodes:
            if "Image Texture" in node.name:
                if "NRM_ALPHA" in node.label:
                    if self.decalcreationtype == "instant":
                        img = bpy.data.images.load(maps["nrm_alpha"])
                    else:
                        img = bpy.data.images.load(bpy.path.relpath(maps["nrm_alpha"]))
                    img.colorspace_settings.name = 'Linear'
                    node.image = img
                elif "AO_CURV_HEIGHT" in node.label:
                    if self.decalcreationtype == "instant":
                        img = bpy.data.images.load(maps["ao_curv_height"])
                    else:
                        img = bpy.data.images.load(bpy.path.relpath(maps["ao_curv_height"]))
                    img.colorspace_settings.name = 'Linear'
                    node.image = img
                    heightmap = img
                elif "SUBSET" in node.label:
                    if self.decalcreationtype == "instant":
                        img = bpy.data.images.load(maps["subset"])
                    else:
                        img = bpy.data.images.load(bpy.path.relpath(maps["subset"]))
                    img.colorspace_settings.name = 'Linear'
                    node.image = img
                elif "MAT2_ALPHA" in node.label:
                    if self.decalcreationtype == "instant":
                        img = bpy.data.images.load(maps["mat2_alpha"])
                    else:
                        img = bpy.data.images.load(bpy.path.relpath(maps["mat2_alpha"]))
                    img.colorspace_settings.name = 'Linear'
                    node.image = img
                elif "INFO" in node.label:
                    if self.decalcreationtype == "instant":
                        img = bpy.data.images.load(maps["color"])
                    else:
                        img = bpy.data.images.load(bpy.path.relpath(maps["color"]))

                    if bpy.app.version >= (2, 79, 0):
                        img.colorspace_settings.name = 'sRGB'
                    else:
                        try:  # pre 2.79 filmic
                            img.colorspace_settings.name = 'sRGB EOTF'
                        except:  # w/o filmic
                            img.colorspace_settings.name = 'sRGB'
                    node.image = img

        # height map
        if heightmap:
            for node in mat.node_tree.nodes:
                if "Group" in node.name:
                    groupname = node.node_tree.name
                    if "parallax" in groupname:
                        node.node_tree.name = groupname.replace("TEMPLATE", self.counter_name)
                        node.inputs['value'].default_value = bpy.context.scene.decals.createparallaxvalue
                        for n in node.node_tree.nodes:
                            if "Group" in n.name:
                                try:
                                    gname = n.node_tree.name
                                except:  # when the group input or output nodes are iterated over, there wont't be a tree below and so result in an exception
                                    gname = ""
                                if "NodeGroup." in gname:
                                    n.node_tree.name = gname.replace("TEMPLATE", self.counter_name)
                                    heightgroup = n.node_tree
                                    for node in heightgroup.nodes:
                                        if "Image Texture" in node.name:
                                            node.image = heightmap
                                            # print(heightmap)
                                            break
                                    break

        self.size = img.size[0], img.size[1]

    def scale_decal(self):
        decaldimensionx = self.size[0] / 1000
        decaldimensiony = self.size[1] / 1000

        bpy.context.object.dimensions = (decaldimensionx, decaldimensiony, 0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        self.dimension = decaldimensionx, decaldimensiony

    def render_thumb(self, thumbpath, decaltype):
        # enable color correction for info thumbs
        if bpy.context.scene.use_nodes is True:
            for node in bpy.context.scene.node_tree.nodes:
                if node.name == "Color Correction":
                    if decaltype == "info":
                        node.mute = False
                    else:
                        node.mute = True

        # set up background nodes in world.node_tree
        # this fixes pink thumbnailes when the Gaffer or similar addons are used
        if bpy.context.scene.world.use_nodes:
            tree = bpy.context.scene.world.node_tree
            for node in tree.nodes:
                if "background" in node.name.lower():
                    for input in node.inputs:
                        for link in input.links:
                            tree.links.remove(link)
                        if input.name == "Color":
                            input.default_value = 0.051, 0.051, 0.051, 1
                        elif input.name == "Strength":
                            input.default_value = 1

        if decaltype in ["subset", "subtractor"]:
            renderdimension = 0.28  # scale decal to fit into camera view
        elif decaltype == "info":
            renderdimension = 0.52  # info has a different camera, so needs a different value
        elif decaltype == "paneling":
            renderdimension = 0.035

        if self.size[0] > self.size[1]:
            scalefactor = renderdimension / self.dimension[0]
        else:
            scalefactor = renderdimension / self.dimension[1]

        bpy.ops.transform.resize(value=(scalefactor, scalefactor, scalefactor))

        if decaltype == "paneling":
            bpy.ops.transform.resize(value=(20, 1, 1))

        # thumbnail resolution
        if self.decalcreationtype == "instant":
            bpy.context.scene.render.resolution_x = 256
            bpy.context.scene.render.resolution_y = 256
        else:
            bpy.context.scene.render.resolution_x = 512
            bpy.context.scene.render.resolution_y = 512

        bpy.context.scene.render.resolution_percentage = 100

        # set render output filename
        bpy.context.scene.render.filepath = thumbpath

        # setting the tumbpath is not enough, the filetype needs to also be set to png!
        bpy.context.scene.render.image_settings.file_format = 'PNG'

        # set the active scene camera
        bpy.context.scene.camera = self.camera

        # render thumbnail
        bpy.ops.render.render(write_still=True)

    def save_decal(self, blendpath):
        # reset decal geometry size to 1,1,1
        bpy.ops.object.scale_clear()

        # remove all objects we don't need in the decal scene
        bpy.ops.object.select_all(action='INVERT')
        bpy.ops.object.delete(use_global=False)
        bpy.ops.object.select_all(action='INVERT')

        # # make sure shadow casting is turned off
        self.active.cycles_visibility.shadow = False

        # # displace mod edit mode viewport behavior
        for mod in self.active.modifiers:
            if "displace" in mod.name.lower():
                mod.show_in_editmode = True
                mod.show_on_cage = True

        # # save the decal blend file
        bpy.ops.wm.save_as_mainfile(filepath=blendpath)


def update_json_maps(decalname, maptype, texturepath):
    processed = load_json(os.path.join(createpath, "processed.json"))
    processed[decalname]["maps"][maptype] = texturepath
    save_json(processed, os.path.join(createpath, "processed.json"))


def update_json_paths(decalname, categorystring, counternamestring, filenamebasestring):
    processed = load_json(os.path.join(createpath, "processed.json"))
    processed[decalname]["counter_name"] = counternamestring
    processed[decalname]["blendpath"] = os.path.join(assetpath, categorystring, "blends", filenamebasestring + ".blend")
    processed[decalname]["thumbpath"] = os.path.join(assetpath, categorystring, "icons", filenamebasestring + ".png")
    save_json(processed, os.path.join(createpath, "processed.json"))
