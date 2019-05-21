import bpy
from bpy.props import StringProperty
from PIL import Image, ImageChops
import os
import shutil
from . bake_down import DecalBakeDown
from .. utils.operators import load_json, unlink_any_image, makedir
from .. import M3utils as m3

# TODO: sketchfab: get color, metallic and roughness values from material nodes and replicate them accordingly instead of using the same default values for all of them
# TODO: substance_painter: "remove atlas overlap" option to get the opportunity to do unique texturing on the decals(naturally the atlas has overlapping uvs of course)
# TODO: DECALBakeDown: proper id maps could be done by separating the joined decals mesh, assigning random colors to each part, rejoin and bake down as texture


class DECALexport(bpy.types.Operator):
    bl_idname = "machin3.decal_export"
    bl_label = "MACHIN3: DECALexport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # save
        # depending on user priviledges, windows and mac may not like the script saving a previously unsaved scene
        try:
            bpy.ops.wm.save_mainfile()
        except:
            self.report({'ERROR'}, "Save your scene first!")
            return {'FINISHED'}

        currentblend = bpy.data.filepath

        self.blendname = os.path.basename(currentblend)[:-6]
        self.exportpath = makedir(os.path.join(bpy.context.user_preferences.addons['DECALmachine'].preferences.DMexportpath, self.blendname))
        self.exporttype = bpy.context.scene.decals.exporttype

        print("\nDECALmachine - Export: %s" % (self.exporttype))
        print(40 * "-")

        self.selection, self.exportgroups = self.get_selection()

        # exportype specific preparations, such as copying unity shaders, merging decals and panel_decals(substance_painter, sketchfab, DECALbakedown?), add extra displace mods(sketchfab)
        getattr(self, "prepare_" + self.exporttype)()

        # export textures
        getattr(self, "export_textures_" + self.exporttype)()

        # triangulize
        if self.exporttype == "sketchfab":  # always triangulize sketchfab
            self.triangulize()
        elif self.exporttype == "unreal_engine_4":  # always triangulie unreal_engine_4, including decals
            self.triangulize(decals=True)
        elif self.exporttype == "DECALBakeDown":  # never triangulize DECALbakedown
            pass
        else:
            if bpy.context.scene.decals.triangulize:  # optionally triangulize all others
                self.triangulize()

        # parent selection to root helper, unless you are exporting to sketchfab or doing a DECALBakeDown
        if self.exporttype not in ["sketchfab", "DECALBakeDown", "substance_painter"]:
            if bpy.context.scene.decals.parenttoroot:
                self.parent_to_root_empty()

        # remove wstep materials - ideally this should be done by the user manually
        self.remove_wstep_mats()

        # apply unique materials
        if self.exporttype not in ["sketchfab", "DECALBakeDown", "substance_painter"]:
            if bpy.context.scene.decals.assignuniquematerials:
                if bpy.context.scene.decals.treatfreestyleasseam:
                    bpy.ops.machin3.convert_freestyle_to_seam()
                bpy.ops.machin3.assign_unique_materials()

        # export fbx or start DECALBakeDown
        if self.exporttype == "DECALBakeDown":
            # optionally export the fbx
            # this needs to be done before the baking, because we are messing with the materials when baking down and so cant do it afterwards, if we also want to load the mainfile again
            if bpy.context.scene.decals.bakedownexportfbx:
                getattr(self, "export_fbx_" + self.exporttype)()

            DecalBakeDown(self.selection, self.exportpath, self.bakedowngroups)
        else:
            # export fbx
            getattr(self, "export_fbx_" + self.exporttype)()

        # open export folder
        if bpy.context.scene.decals.autoopenfolderafterexport:
            m3.open_folder(os.path.join(self.exportpath, self.exporttype))

        # re-load the main file, this will also undo the root empty, unity rotation fix and also get rid of the DECALBakeDown scene
        # NOTE: can only be done when "Quick Export" is enabled, if not fbx export is called via 'INVOKE_DEFAULT' and so, the scene can't be reset
        if bpy.context.scene.decals.quickexport or self.exporttype == "DECALBakeDown":
            bpy.ops.wm.open_mainfile(filepath=currentblend)

        return {'FINISHED'}

    def get_selection(self):
        # get export groups in the scene
        exportgroups = []
        for group in bpy.data.groups:
            if group.name.startswith("DM_export_"):
                exportgroups.append(group)

        # get selection, ether from selected objects or from export groups if nothing is selected
        sel = m3.selected_objects()

        if len(sel) > 0:
            selection = sel
        else:
            selection = []
            for group in exportgroups:
                for obj in group.objects:
                    if obj["DM"]["isdecal"]:
                        if len(obj.users_scene) > 0:  # joined decals and material decals, but not the backuped ones
                            selection.append(obj)
                            obj.select = True
                    else:  # non-decal, such as the target
                        selection.append(obj)
                        obj.select = True

        return selection, exportgroups

    def join_the_joined(self):
        decals = []
        paneldecals = []
        infodecals = []

        selection = []

        # sort the joined decals in the selection
        for obj in self.selection:
            if obj.type == "MESH":
                if obj.name.startswith("panel_decals"):
                    paneldecals.append(obj)
                elif obj.name.startswith("decals"):
                    decals.append(obj)
                elif obj.name.startswith("info_decals"):
                    infodecals.append(obj)
                else:
                    selection.append(obj)

        joinedjoined = []

        # join all joined decals and joined paneldecals
        m3.unselect_all("OBJECT")
        if decals or paneldecals:
            decals += paneldecals

            for decal in decals:
                decal.select = True

            print("Joining '%s'." % (", ".join([obj.name for obj in decals + paneldecals])))
            m3.make_active(decals[0])
            bpy.ops.object.join()

            active = m3.get_active()
            active.name = "decals"

            # if there are mutliple materials, then one of is is a "panel_decals" material
            if len(active.data.materials) > 1:
                active.data.materials.clear(update_data=True)
                active.data.materials.append(bpy.data.materials["decals"])
            else:  # if not, then its either a "decals" or "panel_decals" material, which should be named just "decals"
                active.active_material.name == "decals"

            joinedjoined.append(active)

        # join all joined infodecals:
        m3.unselect_all("OBJECT")
        if infodecals:
            for decal in infodecals:
                decal.select = True

            print("Joining '%s'." % (", ".join([obj.name for obj in infodecals])))
            m3.make_active(infodecals[0])
            bpy.ops.object.join()

            active = m3.get_active()
            active.name = "info_decals"
            active.active_material.name = "info"

            joinedjoined.append(active)

        # reset selection
        for obj in joinedjoined:
            obj.select = True

        for obj in selection:
            obj.select = True

        # update self.selection (as some objects no longer exist due to the joining)
        self.selection = m3.selected_objects()

        return joinedjoined

    def triangulize(self, decals=False):
        print()
        for obj in self.selection:
            if obj.type == "MESH":
                if decals is False:
                    if any([obj.name.startswith(name) for name in ["decals", "panel_decals", "info_decals"]]):  # don't triangulate decals
                        continue
                print("Triangulizing '%s'." % (obj.name))

                m3.unselect_all("OBJECT")
                obj.select = True
                m3.make_active(obj)
                m3.set_mode("EDIT")
                m3.set_mode("FACE")
                m3.unhide_all("MESH")
                m3.select_all("MESH")
                # bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
                bpy.ops.mesh.quads_convert_to_tris(quad_method='FIXED', ngon_method='BEAUTY')
                m3.set_mode("OBJECT")

        # reset selection
        for obj in self.selection:
            obj.select = True

    def parent_to_root_empty(self):
        root = bpy.data.objects.new("root", None)
        bpy.context.scene.objects.link(root)

        exportgroupobjs = []
        for group in self.exportgroups:
            exportgroupobjs += list(group.objects)

        print()
        for obj in self.selection:
            if obj.parent is None:  # only parent if obj isn't already parented, this way existing hierarchies are maintained incl. the ones created via ExportGroup()
                if bpy.context.scene.decals.unityrotfix and "unity3d" in self.exporttype:
                    # unity rotation will do funny things if the root's children dont have their rotations reset
                    # at this point, this should only apply to objects that are exported without being in an export group
                    # and so we specifically only do it do them to avoid messing with any other matrices

                    if obj not in exportgroupobjs:
                        obj.select = True
                        m3.make_active(obj)
                        bpy.ops.object.transform_apply(rotation=True)

                        obj.parent = root

                        print("Zeroed out rotation and parented '%s' to root empty." % (obj.name))
                    else:
                        obj.parent = root
                        print("Parented '%s' to root empty." % (obj.name))
                else:
                    obj.parent = root
                    print("Parented '%s' to root empty." % (obj.name))

        m3.unselect_all('OBJECT')
        root.select = True
        m3.make_active(root)

        # fix 90° rotation in unity
        if bpy.context.scene.decals.unityrotfix and "unity3d" in self.exporttype:
            bpy.ops.transform.rotate(value=-1.5708, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL')
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.transform.rotate(value=1.5708, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL')
            print("\nApplied Unity Rotation Fix.")

        # reset selection
        for obj in self.selection:
            obj.select = True

    def remove_wstep_mats(self):
        print()

        for obj in self.selection:
            if obj.type == "MESH":
                for idx, mat in enumerate(obj.data.materials):
                    if "_wstep" in mat.name:
                        obj.data.materials.pop(idx, update_data=True)
                        print("Removed material '%s' from '%s'." % (mat.name, obj.name))

# ##### PREPARE ###############################################################

    def prepare_DECALBakeDown(self):
        initialselection = self.selection

        # find all export groups among the selection, that aren't simple export groups, we call these bakedown groups
        self.bakedowngroups = []
        for obj in self.selection:
            for group in obj.users_group:
                if group.name.startswith("DM_export_"):
                    if group["simple"] == 0:
                        if group not in self.bakedowngroups:
                            self.bakedowngroups.append(group)

        # join panel decals and decals to one object per bakedowngroup, if both are present in an export group
        for group in self.bakedowngroups:
            m3.unselect_all("OBJECT")

            decal = None
            panel_decal = None

            for obj in group.objects:
                if obj.users_scene:
                    if obj["DM"]["isdecal"]:
                        if obj.name.startswith("decals"):
                            decal = obj
                        if obj.name.startswith("panel_decals"):
                            panel_decal = obj

            if decal and panel_decal:  # if both are present in a group, join and remove the panel decal material, which is the second one
                decal.select = True
                m3.make_active(decal)
                panel_decal.select = True

                initialselection.remove(panel_decal)  # needs to be removed or obj wont exist when checking for ignored object at the end
                print("Joining '%s' with '%s'" % (panel_decal.name, decal.name))

                bpy.ops.object.join()

                decal.data.materials.pop(1, update_data=True)

            elif panel_decal:
                decalmat = bpy.data.materials.get("decals")
                if decalmat:
                    panel_decal.material_slots[0].material = decalmat
                else:
                    mat = bpy.data.materials.new("decals")
                    panel_decal.material_slots[0].material = mat

                panel_decal.name = "decals"

        # update the selection accordingly, for instance if there are simple export groups among the initial selection, or objects not in any export group, they need to be deselected
        m3.unselect_all("OBJECT")

        for group in self.bakedowngroups:
            for obj in group.objects:
                if len(obj.users_scene) > 0:
                    obj.select = True

        self.selection = m3.selected_objects()

        # output ignored objects, potentially useful for debugging
        ignoredobjs = set(initialselection) - set(self.selection)

        if ignoredobjs:
            print()
            for obj in ignoredobjs:
                print("Ignoring '%s', not part of an Export Group. Simple Export Groups are not viable for baking down decals." % (obj.name))

        # for the targets, clear out all materials but the first ones, IF you are exporting an fbx
        if bpy.context.scene.decals.bakedownexportfbx:
            targets = [bpy.data.objects[group["target"]] for group in self.bakedowngroups]

            for obj in targets:
                print()
                while len(obj.data.materials) > 1:
                    matname = obj.data.materials.pop(-1, update_data=True).name
                    print("Removed '%s's material '%s' in preperation for fxb export." % (obj.name, matname))

    def prepare_sketchfab(self):
        joinedjoined = self.join_the_joined()

        # add an extra displace mod, otherwise there will be some decals intersecting the base mesh, perhaps due to precision issues in webgl?
        extradisplace = bpy.context.scene.decals.extradisplace
        amount = bpy.context.scene.decals.extradisplaceamnt

        if m3.DM_prefs().consistantscale:
            self.scene_scale = m3.get_scene_scale()
        else:
            self.scene_scale = 1

        self.midlevel = 1 - (0.0001 / self.scene_scale)  # 0.9999 for scene scale of 1.0

        if extradisplace:
            print()
            for obj in joinedjoined:
                    displace = obj.modifiers.new(name="Displace", type="DISPLACE")
                    displace.mid_level = self.midlevel - (amount / 1000 / self.scene_scale)
                    print("Added '%0.2f' Decal Height to '%s'" % (amount, obj.name))

            # also push material decals
            for obj in self.selection:
                if obj["DM"]["isdecal"] and obj["DM"]["type"] == "Material":
                    displace = obj.modifiers.new(name="Displace", type="DISPLACE")
                    displace.mid_level = self.midlevel - (amount / 1000 / 2 / self.scene_scale)  # only half as much as the other decals
                    print("Added '%0.2f' Decal Height to '%s'" % (amount / 2, obj.name))

    def prepare_substance_painter(self):
        return self.join_the_joined()

    def prepare_unity3d_bac9_packed_advanced(self):
        resourcepath = os.path.join(m3.DM_prefs().DMpath, "assets", "resources")
        shaderpath = makedir(os.path.join(self.exportpath, self.exporttype, "Shaders"))
        exppath = makedir(os.path.join(self.exportpath, self.exporttype))

        sbsatlas = bpy.context.scene.decals.extrasbsatlas
        if sbsatlas:
            shutil.copy(os.path.join(resourcepath, "Atlas.fbx"), exppath)
            print("\nCopied '%s' to Export folder" % ("Atlas.fbx"))

        decalscopied = False
        for obj in self.selection:
            if obj.name.startswith("decals") or obj.name.startswith("panel_decals"):
                if not decalscopied:
                    shutil.copy(os.path.join(resourcepath, "bac9_shaders.txt"), shaderpath)
                    print("\nCopied '%s' to Shaders folder" % ("bac9_shaders.txt"))
                    decalscopied = True

    def prepare_unity3d_machin3(self):
        resourcepath = os.path.join(m3.DM_prefs().DMpath, "assets", "resources")
        shaderpath = makedir(os.path.join(self.exportpath, self.exporttype, "Shaders"))
        exppath = makedir(os.path.join(self.exportpath, self.exporttype))

        shutil.copy(os.path.join(resourcepath, "MACHIN3.cginc"), shaderpath)
        print("\nCopied '%s' to Shaders folder" % ("MACHIN3.cginc"))

        sbsatlas = bpy.context.scene.decals.extrasbsatlas
        if sbsatlas:
            shutil.copy(os.path.join(resourcepath, "Atlas.fbx"), exppath)
            print("\nCopied '%s' to Export folder" % ("Atlas.fbx"))

        decalscopied = False
        panelscopied = False
        infoscopied = False
        for obj in self.selection:
            if obj.name.startswith("decals"):
                if not decalscopied:
                    shutil.copy(os.path.join(resourcepath, "M3_decals_plain.shader"), shaderpath)
                    print("\nCopied '%s' to Shaders folder" % ("M3_decals_plain.shader"))
                    shutil.copy(os.path.join(resourcepath, "M3_decals_textured.shader"), shaderpath)
                    print("Copied '%s' to Shaders folder" % ("M3_decals_textured.shader"))
                    decalscopied = True
            elif obj.name.startswith("panel_decals"):
                if not panelscopied:
                    shutil.copy(os.path.join(resourcepath, "M3_panel_decals.shader"), shaderpath)
                    print("Copied '%s' to Shaders folder" % ("M3_panel_decals.shader"))
                    panelscopied = True
            elif obj.name.startswith("info_decals"):
                if not infoscopied:
                    shutil.copy(os.path.join(resourcepath, "M3_info_decals.shader"), shaderpath)
                    print("Copied '%s' to Shaders folder" % ("M3_info_decals.shader"))
                    infoscopied = True

    def prepare_unpacked(self):
        resourcepath = os.path.join(m3.DM_prefs().DMpath, "assets", "resources")
        exppath = makedir(os.path.join(self.exportpath, self.exporttype))

        sbsatlas = bpy.context.scene.decals.extrasbsatlas
        if sbsatlas:
            shutil.copy(os.path.join(resourcepath, "Atlas.fbx"), exppath)
            print("\nCopied '%s' to Export folder" % ("Atlas.fbx"))

    def prepare_unreal_engine_4(self):
        return self.prepare_unpacked()

# ##### TEXTURES ##############################################################

    def export_textures_DECALBakeDown(self):
        nrmalphapath = os.path.join(self.exportpath, "atlas_nrm_alpha.png")
        aocurvheightpath = os.path.join(self.exportpath, "atlas_ao_curv_height.png")
        subsetpath = os.path.join(self.exportpath, "atlas_subset.png")
        clralphapath = os.path.join(self.exportpath, "atlas_color.png")

        sbsnaming = bpy.context.scene.decals.bakedownsbsnaming

        exportdecal = False
        if os.path.exists(nrmalphapath) and os.path.exists(aocurvheightpath):
            nrmalpha = Image.open(nrmalphapath)
            aocurvheight = Image.open(aocurvheightpath)
            exportdecal = True

        exportinfo = False
        if os.path.exists(clralphapath):
            clralpha = Image.open(clralphapath)
            exportinfo = True

        if any([exportdecal, exportinfo]):
            path = makedir(os.path.join(self.exportpath, self.exporttype, "Atlas_Textures"))

        if exportdecal:
            if os.path.exists(subsetpath):
                subset = Image.open(subsetpath).convert("L")
            else:
                subset = Image.new("L", nrmalpha.size, color=0)

            alpha = nrmalpha.split()[3]
            ao, curvature, height = aocurvheight.convert("RGB").split()

            normal = nrmalpha.convert("RGB")

            if sbsnaming:
                normalpath = os.path.join(path, "decals_normal_base.png")
            else:
                normalpath = os.path.join(path, "decals_normal.png")

            alphapath = os.path.join(path, "decals_alpha.png")

            # TODO: alpha sbsnaming as opacity? won't be auto assigned, but would be more consitant I think

            if sbsnaming:
                aopath = os.path.join(path, "decals_ambient_occlusion.png")
            else:
                aopath = os.path.join(path, "decals_ao.png")

            curvaturepath = os.path.join(path, "decals_curvature.png")
            heightpath = os.path.join(path, "decals_height.png")

            if sbsnaming:
                subsetpath = os.path.join(path, "decals_id.png")
            else:
                subsetpath = os.path.join(path, "decals_subset.png")

            normal.save(normalpath)
            print("\nExported '%s'." % (normalpath))
            alpha.save(alphapath)
            print("Exported '%s'." % (alphapath))
            ao.save(aopath)
            print("Exported '%s'." % (aopath))
            curvature.save(curvaturepath)
            print("Exported '%s'." % (curvaturepath))
            height.save(heightpath)
            print("Exported '%s'." % (heightpath))
            subset.save(subsetpath)
            print("Exported '%s'." % (subsetpath))

        if exportinfo:
            color = clralpha.convert("RGB")
            alpha = clralpha.split()[3]

            colorpath = os.path.join(path, "info_color.png")
            alphapath = os.path.join(path, "info_alpha.png")

            color.save(colorpath)
            print("\nExported '%s'." % (colorpath))
            alpha.save(alphapath)
            print("Exported '%s'." % (alphapath))

    def export_textures_sketchfab(self):
        defaultdiffuse = m3.DM_prefs().sf_defaultdiffuse
        diffuseR = int(defaultdiffuse[0] * 255)
        diffuseG = int(defaultdiffuse[1] * 255)
        diffuseB = int(defaultdiffuse[2] * 255)
        defaultmetalness = int(m3.DM_prefs().sf_defaultmetalness / 100 * 255)
        defaultglossiness = int(m3.DM_prefs().sf_defaultglossiness / 100 * 255)

        bakeaointodiffuse = m3.DM_prefs().sf_bakeaointodiffuse
        bakeaointometalness = m3.DM_prefs().sf_bakeaointometalness
        bakeaointoglossiness = m3.DM_prefs().sf_bakeaointoglossiness

        nrmalphapath = os.path.join(self.exportpath, "atlas_nrm_alpha.png")
        aocurvheightpath = os.path.join(self.exportpath, "atlas_ao_curv_height.png")
        clralphapath = os.path.join(self.exportpath, "atlas_color.png")

        exportdecal = False
        if os.path.exists(nrmalphapath) and os.path.exists(aocurvheightpath):
            nrmalpha = Image.open(nrmalphapath)
            aocurvheight = Image.open(aocurvheightpath)
            exportdecal = True

        exportinfo = False
        if os.path.exists(clralphapath):
            clralpha = Image.open(clralphapath)
            exportinfo = True

        if any([exportdecal, exportinfo]):
            path = makedir(os.path.join(self.exportpath, self.exporttype, "Textures"))

        if exportdecal:
            # invert the green channel
            normalR, normalG, normalB = nrmalpha.convert("RGB").split()
            normal = Image.merge("RGB", (normalR, ImageChops.invert(normalG), normalB))

            alpha = nrmalpha.split()[3]
            ao = aocurvheight.split()[0]

            # bake Ambient Occlusion into...
            if bakeaointodiffuse:
                diffusebg = Image.new("RGB", nrmalpha.size, color=(diffuseR, diffuseG, diffuseB))
                diffuse = ImageChops.multiply(diffusebg, ao.convert("RGB"))
            else:
                diffuse = Image.new("RGB", (2, 2), color=(diffuseR, diffuseG, diffuseB))

            if bakeaointometalness:
                metalnessbg = Image.new("L", nrmalpha.size, color=defaultmetalness)
                metalness = ImageChops.multiply(metalnessbg, ao)
            else:
                metalness = Image.new("L", (2, 2), color=defaultmetalness)

            if bakeaointoglossiness:
                glossinessbg = Image.new("L", nrmalpha.size, color=defaultglossiness)
                glossiness = ImageChops.multiply(glossinessbg, ao)
            else:
                glossiness = Image.new("L", (2, 2,), color=defaultglossiness)

            normalpath = os.path.join(path, "decals_normal.png")
            alphapath = os.path.join(path, "decals_alpha.png")
            diffusepath = os.path.join(path, "decals_diffuse.png")
            metalnesspath = os.path.join(path, "decals_metalness.png")
            glossinesspath = os.path.join(path, "decals_glossiness.png")
            aopath = os.path.join(path, "decals_ao.png")

            normal.save(normalpath)
            print("\nExported '%s'." % (normalpath))
            alpha.save(alphapath)
            print("Exported '%s'." % (alphapath))
            metalness.save(metalnesspath)
            print("Exported '%s'." % (metalnesspath))
            glossiness.save(glossinesspath)
            print("Exported '%s'." % (glossinesspath))
            diffuse.save(diffusepath)
            print("Exported '%s'." % (diffusepath))
            ao.save(aopath)
            print("Exported '%s'." % (aopath))

        if exportinfo:
            color = clralpha.convert("RGB")
            alpha = clralpha.split()[3]

            metalness = Image.new("L", (2, 2), color=0)
            glossiness = Image.new("L", (2, 2), color=160)

            path = makedir(os.path.join(self.exportpath, self.exporttype, "Textures"))
            colorpath = os.path.join(path, "info_diffuse.png")
            alphapath = os.path.join(path, "info_alpha.png")
            metalnesspath = os.path.join(path, "info_metalness.png")
            glossinesspath = os.path.join(path, "info_glossiness.png")

            color.save(colorpath)
            print("\nExported '%s'." % (colorpath))
            alpha.save(alphapath)
            print("Exported '%s'." % (alphapath))
            metalness.save(metalnesspath)
            print("Exported '%s'." % (metalnesspath))
            glossiness.save(glossinesspath)
            print("Exported '%s'." % (glossinesspath))

        # get all non-decal materials
        materials = []
        for obj in self.selection:
            for mat in obj.data.materials:
                if mat.name != "decals" and mat.name != "info" and "_wstep" not in mat.name:
                    if mat not in materials:
                        materials.append(mat)

        for mat in materials:
            diffuse = Image.new("RGB", (2, 2), color=(diffuseR, diffuseG, diffuseB))
            metalness = Image.new("L", (2, 2), color=defaultmetalness)
            glossiness = Image.new("L", (2, 2,), color=defaultglossiness)

            diffusepath = os.path.join(path, "%s_diffuse.png" % (mat.name))
            metalnesspath = os.path.join(path, "%s_metalness.png" % (mat.name))
            glossinesspath = os.path.join(path, "%s_glossiness.png" % (mat.name))

            diffuse.save(diffusepath)
            print("\nExported '%s'." % (diffusepath))
            metalness.save(metalnesspath)
            print("Exported '%s'." % (metalnesspath))
            glossiness.save(glossinesspath)
            print("Exported '%s'." % (glossinesspath))

    def export_textures_unpacked(self, flipgreen=None):
        nrmalphapath = os.path.join(self.exportpath, "atlas_nrm_alpha.png")
        aocurvheightpath = os.path.join(self.exportpath, "atlas_ao_curv_height.png")
        subsetpath = os.path.join(self.exportpath, "atlas_subset.png")
        clralphapath = os.path.join(self.exportpath, "atlas_color.png")

        sbsatlas = bpy.context.scene.decals.extrasbsatlas
        quickexport = bpy.context.scene.decals.quickexport

        if flipgreen is None:
            flipgreen = bpy.context.scene.decals.normalflipgreen

        if quickexport:
            prefix = bpy.context.scene.decals.exportname + "_"
        else:
            prefix = ""

        exportdecal = False
        if os.path.exists(nrmalphapath) and os.path.exists(aocurvheightpath):
            nrmalpha = Image.open(nrmalphapath)
            aocurvheight = Image.open(aocurvheightpath)
            exportdecal = True

        exportinfo = False
        if os.path.exists(clralphapath):
            clralpha = Image.open(clralphapath)
            exportinfo = True

        if any([exportdecal, exportinfo]):
            path = makedir(os.path.join(self.exportpath, self.exporttype, "Textures"))

            if sbsatlas:
                sbspath = makedir(os.path.join(self.exportpath, self.exporttype, "Textures_Substance"))

        if exportdecal:
            if os.path.exists(subsetpath):
                subset = Image.open(subsetpath).convert("L")
            else:
                subset = Image.new("L", nrmalpha.size, color=0)

            alpha = nrmalpha.split()[3]
            ao, curvature, height = aocurvheight.convert("RGB").split()

            if flipgreen:
                normalR, normalG, normalB = nrmalpha.convert("RGB").split()
                normal = Image.merge("RGB", (normalR, ImageChops.invert(normalG), normalB))
            else:
                normal = nrmalpha.convert("RGB")

            normalpath = os.path.join(path, "%sdecals_normal.png" % (prefix))
            alphapath = os.path.join(path, "%sdecals_alpha.png" % (prefix))
            aopath = os.path.join(path, "%sdecals_ao.png" % (prefix))
            curvaturepath = os.path.join(path, "%sdecals_curvature.png" % (prefix))
            heightpath = os.path.join(path, "%sdecals_height.png" % (prefix))
            subsetpath = os.path.join(path, "%sdecals_subset.png" % (prefix))

            normal.save(normalpath)
            print("\nExported '%s'." % (normalpath))
            alpha.save(alphapath)
            print("Exported '%s'." % (alphapath))
            ao.save(aopath)
            print("Exported '%s'." % (aopath))
            curvature.save(curvaturepath)
            print("Exported '%s'." % (curvaturepath))
            height.save(heightpath)
            print("Exported '%s'." % (heightpath))
            subset.save(subsetpath)
            print("Exported '%s'." % (subsetpath))

            if sbsatlas:
                self.export_sbs_decal_atlas(sbspath, nrmalpha, aocurvheight, subset)

        if exportinfo:
            color = clralpha.convert("RGB")
            alpha = clralpha.split()[3]

            path = makedir(os.path.join(self.exportpath, self.exporttype, "Textures"))
            colorpath = os.path.join(path, "%sinfo_color.png" % (prefix))
            alphapath = os.path.join(path, "%sinfo_alpha.png" % (prefix))

            color.save(colorpath)
            print("\nExported '%s'." % (colorpath))
            alpha.save(alphapath)
            print("Exported '%s'." % (alphapath))

            if sbsatlas:
                self.export_sbs_info_atlas(sbspath, clralpha)

    def export_textures_substance_painter(self):
        nrmalphapath = os.path.join(self.exportpath, "atlas_nrm_alpha.png")
        aocurvheightpath = os.path.join(self.exportpath, "atlas_ao_curv_height.png")
        subsetpath = os.path.join(self.exportpath, "atlas_subset.png")
        clralphapath = os.path.join(self.exportpath, "atlas_color.png")

        exportdecal = False
        if os.path.exists(nrmalphapath) and os.path.exists(aocurvheightpath):
            nrmalpha = Image.open(nrmalphapath)
            aocurvheight = Image.open(aocurvheightpath)
            exportdecal = True

        exportinfo = False
        if os.path.exists(clralphapath):
            clralpha = Image.open(clralphapath)
            exportinfo = True

        if any([exportdecal, exportinfo]):
            path = makedir(os.path.join(self.exportpath, self.exporttype, "Textures"))

        if exportdecal:
            if os.path.exists(subsetpath):
                subset = Image.open(subsetpath).convert("L")
            else:
                subset = Image.new("L", nrmalpha.size, color=0)

            ao, curvature, _ = aocurvheight.convert("RGB").split()
            normal = nrmalpha.convert("RGB")
            alpha = nrmalpha.split()[3]

            normalpath = os.path.join(path, "decals_normal_base.png")
            aopath = os.path.join(path, "decals_ambient_occlusion.png")
            curvaturepath = os.path.join(path, "decals_curvature.png")
            alphapath = os.path.join(path, "decals_opacity.png")
            subsetpath = os.path.join(path, "decals_id.png")

            normal.save(normalpath)
            print("\nExported '%s'." % (normalpath))
            ao.save(aopath)
            print("Exported '%s'." % (aopath))
            curvature.save(curvaturepath)
            print("Exported '%s'." % (curvaturepath))
            alpha.save(alphapath)
            print("Exported '%s'." % (alphapath))
            subset.save(subsetpath)
            print("Exported '%s'." % (subsetpath))

        if exportinfo:
            color = clralpha.convert("RGB")
            alpha = clralpha.split()[3]

            path = makedir(os.path.join(self.exportpath, self.exporttype, "Textures"))
            colorpath = os.path.join(path, "info_color.png")
            alphapath = os.path.join(path, "info_opacity.png")

            color.save(colorpath)
            print("\nExported '%s'." % (colorpath))
            alpha.save(alphapath)
            print("Exported '%s'." % (alphapath))

    def export_textures_unity3d_machin3(self):
        nrmalphapath = os.path.join(self.exportpath, "atlas_nrm_alpha.png")
        aocurvheightpath = os.path.join(self.exportpath, "atlas_ao_curv_height.png")
        subsetpath = os.path.join(self.exportpath, "atlas_subset.png")
        clralphapath = os.path.join(self.exportpath, "atlas_color.png")

        sbsatlas = bpy.context.scene.decals.extrasbsatlas
        quickexport = bpy.context.scene.decals.quickexport

        if quickexport:
            prefix = bpy.context.scene.decals.exportname + "_"
        else:
            prefix = ""

        exportdecal = False
        if os.path.exists(nrmalphapath) and os.path.exists(aocurvheightpath):
            nrmalpha = Image.open(nrmalphapath)
            aocurvheight = Image.open(aocurvheightpath)
            exportdecal = True

        exportinfo = False
        if os.path.exists(clralphapath):
            clralpha = Image.open(clralphapath)
            exportinfo = True

        if any([exportdecal, exportinfo]):
            path = makedir(os.path.join(self.exportpath, self.exporttype, "Textures"))

            if sbsatlas:
                sbspath = makedir(os.path.join(self.exportpath, self.exporttype, "Textures_Substance"))

        if exportdecal:
            if os.path.exists(subsetpath):
                subset = Image.open(subsetpath).convert("L")
            else:
                subset = Image.new("L", nrmalpha.size, color=0)

            ao, curvature, height = aocurvheight.convert("RGB").split()
            aocurvheightsubset = Image.merge("RGBA", (ao, curvature, height, subset))

            normalalphapath = os.path.join(path, "%snormal_alpha.png" % (prefix))
            aocurvheightsubsetpath = os.path.join(path, "%sao_curv_height_subset.png" % (prefix))

            nrmalpha.save(normalalphapath)
            print("\nExported '%s'." % (normalalphapath))
            aocurvheightsubset.save(aocurvheightsubsetpath)
            print("Exported '%s'." % (aocurvheightsubsetpath))

            if sbsatlas:
                self.export_sbs_decal_atlas(sbspath, nrmalpha, aocurvheight, subset)

        if exportinfo:
            coloralphapath = os.path.join(path, "%scolor_alpha.png" % (prefix))

            clralpha.save(coloralphapath)
            print("\nExported '%s'." % (coloralphapath))

            if sbsatlas:
                self.export_sbs_info_atlas(sbspath, clralpha)

    def export_textures_unity3d_bac9_packed_advanced(self):
        nrmalphapath = os.path.join(self.exportpath, "atlas_nrm_alpha.png")
        aocurvheightpath = os.path.join(self.exportpath, "atlas_ao_curv_height.png")
        subsetpath = os.path.join(self.exportpath, "atlas_subset.png")
        clralphapath = os.path.join(self.exportpath, "atlas_color.png")

        sbsatlas = bpy.context.scene.decals.extrasbsatlas
        quickexport = bpy.context.scene.decals.quickexport

        if quickexport:
            prefix = bpy.context.scene.decals.exportname + "_"
        else:
            prefix = ""

        exportdecal = False
        if os.path.exists(nrmalphapath) and os.path.exists(aocurvheightpath):
            nrmalpha = Image.open(nrmalphapath)
            aocurvheight = Image.open(aocurvheightpath)
            exportdecal = True

        exportinfo = False
        if os.path.exists(clralphapath):
            clralpha = Image.open(clralphapath)
            exportinfo = True

        if any([exportdecal, exportinfo]):
            path = makedir(os.path.join(self.exportpath, self.exporttype, "Textures"))

            if sbsatlas:
                sbspath = makedir(os.path.join(self.exportpath, self.exporttype, "Textures_Substance"))

        if exportdecal:
            if os.path.exists(subsetpath):
                subset = Image.open(subsetpath).convert("L")
            else:
                subset = Image.new("L", nrmalpha.size, color=0)

            alpha = nrmalpha.split()[3]
            ao, curvature, height = aocurvheight.convert("RGB").split()
            emission = Image.new("L", nrmalpha.size, color=0)

            # NOTE: bac9's packed parallax seems to require a height map mid level of 188 for some reason, disabling for now, as it's also doesnt mask out the subsets
            # using packed advanced instead
            packedadvanced = Image.merge("RGBA", (alpha, subset, curvature, ao))

            # nrmbg = Image.new("RGBA", nrmalpha.size, color=(128, 128, 255, 255))
            # normal = Image.alpha_composite(nrmbg, nrmalpha)
            normal = nrmalpha.convert("RGB")

            emissionheight = Image.merge("RGBA", (emission, emission, emission, height))

            packedadvancedpath = os.path.join(path, "%spacked_advanced.png" % (prefix))
            normalpath = os.path.join(path, "%snormal.png" % (prefix))
            emissionheightpath = os.path.join(path, "%semissionheight.png" % (prefix))

            packedadvanced.save(packedadvancedpath)
            print("\nExported '%s'." % (packedadvancedpath))
            normal.save(normalpath)
            print("Exported '%s'." % (normalpath))
            emissionheight.save(emissionheightpath)
            print("Exported '%s'." % (emissionheightpath))

            if sbsatlas:
                self.export_sbs_decal_atlas(sbspath, nrmalpha, aocurvheight, subset)

        if exportinfo:
            coloralphapath = os.path.join(path, "%scolor_alpha.png" % (prefix))

            clralpha.save(coloralphapath)
            print("\nExported '%s'." % (clralphapath))

            if sbsatlas:
                self.export_sbs_info_atlas(sbspath, clralpha)

    def export_textures_unreal_engine_4(self):
        return self.export_textures_unpacked(flipgreen=True)

# ##### SUBSTANCE ATLAS ######################################################

    def export_sbs_decal_atlas(self, sbspath, nrmalpha, aocurvheight, subset):
        normal = nrmalpha.convert("RGB")
        alpha = nrmalpha.split()[3]

        ao = aocurvheight.split()[0]
        curvature = aocurvheight.split()[1]
        height = aocurvheight.split()[2]

        normalpath = os.path.join(sbspath, "Atlas_normal_base.png")
        alphapath = os.path.join(sbspath, "Atlas_alpha.png")
        aopath = os.path.join(sbspath, "Atlas_ambient_occlusion.png")
        curvaturepath = os.path.join(sbspath, "Atlas_curvature.png")
        heightpath = os.path.join(sbspath, "Atlas_height.png")
        subsetpath = os.path.join(sbspath, "Atlas_id.png")

        normal.save(normalpath)
        print("\nExported '%s'." % (normalpath))
        alpha.save(alphapath)
        print("Exported '%s'." % (alphapath))
        ao.save(aopath)
        print("Exported '%s'." % (aopath))
        curvature.save(curvaturepath)
        print("Exported '%s'." % (curvaturepath))
        height.save(heightpath)
        print("Exported '%s'." % (heightpath))
        subset.save(subsetpath)
        print("Exported '%s'." % (subsetpath))

    def export_sbs_info_atlas(self, sbspath, clralpha):
        color = clralpha.convert("RGB")
        opacity = clralpha.split()[3]

        colorpath = os.path.join(sbspath, "Atlas_color.png")
        opacitypath = os.path.join(sbspath, "Atlas_opacity.png")

        color.save(colorpath)
        print("\nExported '%s'." % (colorpath))
        opacity.save(opacitypath)
        print("Exported '%s'." % (opacitypath))

# ##### FBX SPECIFIC #########################################################

    def export_fbx_unity3d_machin3(self):
        return self.export_fbx_unity3d()

    def export_fbx_unity3d_bac9_packed_advanced(self):
        return self.export_fbx_unity3d()

    def export_fbx_substance_painter(self):
        apply_unit_scale=True
        mesh_smooth_type='FACE'
        use_tspace = False

        quickexport = bpy.context.scene.decals.quickexport
        name = bpy.context.scene.decals.exportname

        print()
        print(40 * "-")

        if quickexport:  # use the name entered in the export pie, no animation export, but scene will reset automatically to a pre export state(resetting triangulation and root parenting)
            path = os.path.join(self.exportpath, self.exporttype, name + ".fbx")
            execcontext = "EXEC_DEFAULT"
        else:  # without quick export, the fbx export is invoked, offering access to more fbx settings including animations etc (scene will need to be manually reverted afterwards and should not be saved after exporting!)
            path = os.path.join(self.exportpath, self.exporttype, "Untitled.fbx")
            execcontext = "INVOKE_DEFAULT"

        bpy.ops.export_scene.fbx(execcontext,
                                 filepath=path,
                                 use_selection=True,  # Export selected objects on visible layers
                                 apply_unit_scale=apply_unit_scale,
                                 mesh_smooth_type=mesh_smooth_type,  # OFF, EDGE or FACE - Export smoothing information (not mandatory if your target importer understand split normals). the OFF option is called "Normals Only" in the export menu
                                 use_tspace=use_tspace,
                                 bake_anim=False,
                                 )
        if quickexport:
            print(40 * "-")
            print("\nExported '%s'.\n" % (path))

    def export_fbx_sketchfab(self):
        apply_unit_scale=False
        mesh_smooth_type='OFF'
        use_tspace = False

        quickexport = bpy.context.scene.decals.quickexport
        createarchive = bpy.context.scene.decals.createarchive
        name = bpy.context.scene.decals.exportname

        print()
        print(40 * "-")

        # for sketchfab, we are exporting and then putting everything in an archive for easy uploading
        if quickexport:
            path = os.path.join(self.exportpath, self.exporttype, name + ".fbx")
            execcontext = "EXEC_DEFAULT"

            bpy.ops.export_scene.fbx(execcontext,
                                     filepath=path,
                                     use_selection=True,  # Export selected objects on visible layers
                                     apply_unit_scale=apply_unit_scale,
                                     mesh_smooth_type=mesh_smooth_type,  # OFF, EDGE or FACE - Export smoothing information (not mandatory if your target importer understand split normals). the OFF option is called "Normals Only" in the export menu
                                     use_tspace=use_tspace,
                                     bake_anim=False,
                                     )

            print(40 * "-")
            print("\nExported '%s'." % (path))

            if createarchive:
                src = os.path.join(self.exportpath, self.blendname)
                target = os.path.join(self.exportpath, self.exporttype)

                # creating a zip file, you can't put the archive in the same folder you are zipping or their will be a recursion and the file keeps growing
                shutil.make_archive(src, 'zip', target)

                # so move the file after archiving is done
                shutil.move(src + ".zip", os.path.join(target, name + ".zip"))

                print("\nCreated Archive '%s'." % (os.path.join(target, name + ".zip")))

                # finally remove the textures folder and the fbx
                shutil.rmtree(os.path.join(target, "Textures"))
                print("\nRemoved folder '%s'." % (os.path.join(target, "Textures")))

                os.unlink(os.path.join(target, name + ".fbx"))
                print("Removed file '%s'.\n" % (os.path.join(target, name + ".fbx")))

        else:
            path = os.path.join(self.exportpath, self.exporttype, "Untitled.fbx")
            execcontext = "INVOKE_DEFAULT"

            bpy.ops.export_scene.fbx('INVOKE_DEFAULT',
                                     filepath=path,
                                     use_selection=True,  # Export selected objects on visible layers
                                     apply_unit_scale=apply_unit_scale,
                                     mesh_smooth_type=mesh_smooth_type,  # OFF, EDGE or FACE - Export smoothing information (not mandatory if your target importer understand split normals). the OFF option is called "Normals Only" in the export menu
                                     use_tspace=use_tspace,
                                     bake_anim=False,
                                     )

    def export_fbx_unpacked(self):
        apply_unit_scale=True
        mesh_smooth_type='OFF'
        use_tspace = False

        quickexport = bpy.context.scene.decals.quickexport
        name = bpy.context.scene.decals.exportname

        print()
        print(40 * "-")

        if quickexport:  # use the name entered in the export pie, no animation export, but scene will reset automatically to a pre export state(resetting triangulation and root parenting)
            path = os.path.join(self.exportpath, self.exporttype, name + ".fbx")
            execcontext = "EXEC_DEFAULT"
        else:  # without quick export, the fbx export is invoked, offering access to more fbx settings including animations etc (scene will need to be manually reverted afterwards and should not be saved after exporting!)
            path = os.path.join(self.exportpath, self.exporttype, "Untitled.fbx")
            execcontext = "INVOKE_DEFAULT"

        bpy.ops.export_scene.fbx(execcontext,
                                 filepath=path,
                                 use_selection=True,  # Export selected objects on visible layers
                                 apply_unit_scale=apply_unit_scale,
                                 mesh_smooth_type=mesh_smooth_type,  # OFF, EDGE or FACE - Export smoothing information (not mandatory if your target importer understand split normals). the OFF option is called "Normals Only" in the export menu
                                 use_tspace=use_tspace,
                                 bake_anim=False,
                                 )

        if quickexport:
            print(40 * "-")
            print("\nExported '%s'.\n" % (path))

    def export_fbx_DECALBakeDown(self):
        # unselect everything but the targets
        for obj in self.selection:
            if obj["DM"]["isdecal"] == 0:
                obj.select = True
            else:
                obj.select = False

        # fbx settings
        # NOTE: expose these in preferences
        apply_unit_scale=False
        mesh_smooth_type='OFF'
        use_tspace = False

        name = bpy.context.scene.decals.exportname
        path = os.path.join(self.exportpath, self.exporttype, name + ".fbx")

        print()
        print(40 * "-")

        bpy.ops.export_scene.fbx(filepath=path,
                                 use_selection=True,  # Export selected objects on visible layers
                                 apply_unit_scale=apply_unit_scale,
                                 mesh_smooth_type=mesh_smooth_type,  # OFF, EDGE or FACE - Export smoothing information (not mandatory if your target importer understand split normals). the OFF option is called "Normals Only" in the export menu
                                 use_tspace=use_tspace,
                                 bake_anim=False,
                                 )

        print(40 * "-")
        print("\nExported '%s'.\n" % (path))

        # reset selection
        for obj in self.selection:
            obj.select = True

    def export_fbx_unreal_engine_4(self):
        apply_unit_scale=True
        mesh_smooth_type='FACE'
        use_tspace = True  # NOTE: will throw an exception when exporting the fbx, when there are n-gons, so as a solution we are now triangulizing everything incl decals for ue4. Alternatively we could just not use tspace?

        quickexport = bpy.context.scene.decals.quickexport
        name = bpy.context.scene.decals.exportname

        print()
        print(40 * "-")

        if quickexport:  # use the name entered in the export pie, no animation export, but scene will reset automatically to a pre export state(resetting triangulation and root parenting)
            path = os.path.join(self.exportpath, self.exporttype, name + ".fbx")
            execcontext = "EXEC_DEFAULT"
        else:  # without quick export, the fbx export is invoked, offering access to more fbx settings including animations etc (scene will need to be manually reverted afterwards and should not be saved after exporting!)
            path = os.path.join(self.exportpath, self.exporttype, "Untitled.fbx")
            execcontext = "INVOKE_DEFAULT"

        bpy.ops.export_scene.fbx(execcontext,
                                 filepath=path,
                                 use_selection=True,  # Export selected objects on visible layers
                                 apply_unit_scale=apply_unit_scale,
                                 mesh_smooth_type=mesh_smooth_type,  # OFF, EDGE or FACE - Export smoothing information (not mandatory if your target importer understand split normals). the OFF option is called "Normals Only" in the export menu
                                 use_tspace=use_tspace,
                                 bake_anim=False,
                                 )

        if quickexport:
            print(40 * "-")
            print("\nExported '%s'.\n" % (path))

# ##### FBX GENERIC ##########################################################

    def export_fbx_unity3d(self):
        apply_unit_scale=False
        mesh_smooth_type='OFF'
        use_tspace = False

        quickexport = bpy.context.scene.decals.quickexport
        name = bpy.context.scene.decals.exportname

        print()
        print(40 * "-")

        if quickexport:  # use the name entered in the export pie, no animation export, but scene will reset automatically to a pre export state(resetting triangulation and root parenting)
            path = os.path.join(self.exportpath, self.exporttype, name + ".fbx")
            execcontext = "EXEC_DEFAULT"
        else:  # without quick export, the fbx export is invoked, offering access to more fbx settings including animations etc (scene will need to be manually reverted afterwards and should not be saved after exporting!)
            path = os.path.join(self.exportpath, self.exporttype, "Untitled.fbx")
            execcontext = "INVOKE_DEFAULT"

        bpy.ops.export_scene.fbx(execcontext,
                                 filepath=path,
                                 use_selection=True,  # Export selected objects on visible layers
                                 apply_unit_scale=apply_unit_scale,
                                 mesh_smooth_type=mesh_smooth_type,  # OFF, EDGE or FACE - Export smoothing information (not mandatory if your target importer understand split normals). the OFF option is called "Normals Only" in the export menu
                                 use_tspace=use_tspace,
                                 bake_anim=False,
                                 )

        if quickexport:
            print(40 * "-")
            print("\nExported '%s'.\n" % (path))


class ResetExportGroupOp(bpy.types.Operator):
    bl_idname = "machin3.decal_export_reset_export_group"
    bl_label = "MACHIN3: Reset Export Group"
    bl_options = {'REGISTER', 'UNDO'}

    groupname = StringProperty()

    def execute(self, context):
        ResetExportGroup(self.groupname)
        return {'FINISHED'}


class ResetExportGroup():
    def __init__(self, groupname):
        self.groupname = groupname

        if self.groupname == "ALL":
            for group in bpy.data.groups:
                if group.name.startswith("DM_export_"):
                    self.reset(group)
        else:
            exportgroup = bpy.data.groups[self.groupname]
            self.reset(exportgroup)

    def reset(self, exportgroup):
        print("Resetting export group '%s'" % (exportgroup.name))

        #  undo uvs (delete the joined decal object and get back the individual unlinked/backuped ones
        if exportgroup["uvs"]:
            self.undo_decal_uvs(exportgroup)

            # before the group is removed, let's select every object in it, this way a group can easily be re-created with or without additional objects
            for obj in exportgroup.objects:
                obj.select = True

            bpy.data.groups.remove(exportgroup, do_unlink=True)

    def undo_decal_uvs(self, exportgroup):
        print("Undoing joining and uving for group '%s'" % (exportgroup.name))
        # needs to be done in steps witht the two lists, as linking objs to a scene from a list og group.objcts seems to introduce some recursion, where those objs will then be iteratated over again leading to unwanted deletion
        deletelist = []
        bringbacklist = []
        for obj in exportgroup.objects:
            if len(obj.users_scene) > 0:
                if obj["DM"]["isdecal"] and obj["DM"]["type"] != "Material":
                    deletelist.append(obj)
            else:
                bringbacklist.append(obj)

        m3.unselect_all("OBJECT")
        for obj in deletelist:
            # remove joined decal material, but only when you clear out ALL exportgroups
            if self.groupname == "ALL":
                if obj.active_material is not None:
                    bpy.data.materials.remove(obj.active_material, do_unlink=True)
            print("Deleting '%s'." % (obj.name))
            obj.select = True

        bpy.ops.object.delete(use_global=False)

        for obj in bringbacklist:
            print("Bringing back '%s'" % (obj.name))
            bpy.context.scene.objects.link(obj)
            obj.use_fake_user = False

        # actually not needed, as the groups is being deleted anyway
        exportgroup['uvs'] = False


class ExportGroup(bpy.types.Operator):
    bl_idname = "machin3.decal_export_export_group"
    bl_label = "MACHIN3: Export Group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selection = m3.selected_objects()

        # fetch the atlasjson to retrieve the atlas size and the packing details from the "fullboxes" key
        blendname = os.path.basename(bpy.data.filepath)[:-6]
        exportpath = makedir(os.path.join(bpy.context.user_preferences.addons['DECALmachine'].preferences.DMexportpath, blendname))

        decaljsonpath = os.path.join(exportpath, "atlas_decal.json")
        infojsonpath = os.path.join(exportpath, "atlas_info.json")

        if m3.path_exists(decaljsonpath):
            self.decalatlas = load_json(decaljsonpath)
            self.decalatlassize = self.decalatlas["size"]
            self.decalatlasfullboxes = self.decalatlas["fullboxes"]
        else:
            self.decalatlas = None

        if m3.path_exists(infojsonpath):
            self.infoatlas = load_json(infojsonpath)
            self.infoatlassize = self.infoatlas["size"]
            self.infoatlasfullboxes = self.infoatlas["fullboxes"]
        else:
            self.infoatlas = None

        # check if any atlas has been found on disk
        if any([self.decalatlas, self.infoatlas]):
            # find target, and make sure there is only one, also check that target for a material and set the material name as a  group property (needed for combining of bakedowns to texturesets)
            # this means a material cut object is not suited well for baking down, something to be aware of
            exportgroup = self.create_exportgroup(selection)

            if exportgroup:
                # backup decals and do all the following on duplicates
                # this way, you can get back the original decals via the 'reset atlas' tool
                self.backup_decals(exportgroup)

                # match fullbox packing data to objects by matching ao_curv_height or color image to the (template)path keys in the atlas jsons
                # and write the packing data into the objs as an id property
                self.set_packing_data(exportgroup)

                # for each decal adjust UVs based on the atlas packing data
                self.adjust_uvs_to_atlas(exportgroup)

                # join decals
                joined = self.join_decals(exportgroup)

                # create a preview material to confirm the uv adjustments were successful
                self.preview_new_uvs(joined, exportpath)

                m3.unselect_all("OBJECT")
        else:
            self.report({'ERROR'}, "Could not find Atlas json file. Did you save to a new blend file since packing the Atlas?\nIf you did, copy the json and png files from the packing solution to the new export folder.")
            m3.open_folder(exportpath)

        return {'FINISHED'}

    def preview_new_uvs(self, joinedobjs, exportpath):
        for joined in joinedobjs:
            if joined.name.startswith("decals"):
                matname = "decals"
                atlastype = "decal"
            elif joined.name.startswith("panel_decals"):
                matname = "panel_decals"
                atlastype = "decal"
            elif joined.name.startswith("info_decals"):
                matname = "info_decals"
                atlastype = "info"

            mat = bpy.data.materials.get(matname)
            if mat:
                # assign existing preview material
                joined.data.materials.append(mat)
            else:
                mat = bpy.data.materials.new(joined.name)

                # assign and set up new preview material
                joined.data.materials.append(mat)

                mat.use_nodes = True
                tree = mat.node_tree

                imgnode = tree.nodes.new("ShaderNodeTexImage")
                imgnode.color_space = 'NONE'

                if atlastype == "decal":
                    atlasimg = bpy.data.images.load(os.path.join(exportpath, "atlas_nrm_alpha.png"))
                elif atlastype == "info":
                    atlasimg = bpy.data.images.load(os.path.join(exportpath, "atlas_color.png"))

                imgnode.image = atlasimg
                imgnodeout = imgnode.outputs['Color']
                diffusenode = tree.nodes['Diffuse BSDF']

                if atlastype == "decal":
                    tree.nodes.remove(diffusenode)

                    nrmnode = tree.nodes.new("ShaderNodeNormalMap")
                    nrmnodein = nrmnode.inputs['Color']
                    nrmnodeout = nrmnode.outputs['Normal']

                    glossynode = tree.nodes.new("ShaderNodeBsdfGlossy")
                    glossynode.inputs['Color'].default_value = (0.35, 0.35, 0.35, 1)
                    glossynodein = glossynode.inputs['Normal']
                    glossynodeout = glossynode.outputs['BSDF']

                    matout = tree.nodes['Material Output'].inputs['Surface']

                    tree.links.new(imgnodeout, nrmnodein)
                    tree.links.new(nrmnodeout, glossynodein)
                    tree.links.new(glossynodeout, matout)
                elif atlastype == "info":
                    diffusenodein = diffusenode.inputs['Color']
                    diffusenodeout = diffusenode.outputs['BSDF']

                    imgnodealphaout = imgnode.outputs['Alpha']

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

                    tree.links.new(imgnodeout, diffusenodein)
                    tree.links.new(diffusenodeout, mixnodeshader1)
                    tree.links.new(transparentnodeout, mixnodeshader2)
                    tree.links.new(imgnodealphaout, invertnodein)
                    tree.links.new(invertnodeout, mixnodefactor)
                    tree.links.new(mixnodeout, materialoutput)

                    mat.game_settings.alpha_blend = 'CLIP'

    def join_decals(self, exportgroup):
        # create 3 types of joined decals: decals, panels, infos
        decals = []
        panels = []
        infos = []
        for obj in exportgroup.objects:
            if obj["DM"]["isdecal"] and obj["DM"]["type"] != "Material":
                if len(obj.users_scene) > 0:
                    matname = obj.active_material.name
                    if any([x in matname for x in ["decal01", "decal02"]]):
                        decals.append(obj)
                    elif "paneling01" in matname:
                        panels.append(obj)
                    elif "info01" in matname:
                        infos.append(obj)

        returnlist = []
        # join the decals decals
        for ds in [decals, panels, infos]:  #
            m3.unselect_all("OBJECT")
            joined = False
            for decal in ds:
                if not joined:
                    joined = m3.make_active(decal)
                decal.select = True

            if joined:
                bpy.ops.object.join()

                returnlist.append(joined)

                # make sure auto smooth is on, otherwise the custom normal info will not be used if the join target was an unprojected decal
                joined.data.use_auto_smooth = True

                joined.data.materials.clear(update_data=True)

                # name joined objects
                if ds is decals:
                    joined.name = "decals"
                elif ds is panels:
                    joined.name = "panel_decals"
                elif ds is infos:
                    joined.name = "info_decals"

                # remove residue id props from the joined
                del joined["DM"]["atlasuvs"]

                try:
                    del joined["timestamp"]  # timestamp can be present, but doesnt have to, depends on the join target
                except:
                    pass

                # make sure the joined objects rotation and scale are zeroed out otherwise, unity rotation fix might do funny things
                # TODO: manually clear the detal transforms, if there are any?
                bpy.ops.object.transform_apply(rotation=True, scale=True)

                # finally parent each joined decal to the target if that isn't already the case
                m3.unselect_all("OBJECT")
                target = bpy.data.objects[exportgroup["target"]]
                if joined.parent == target:  # already parented to the target
                    continue
                elif joined.parent is None:  # not yet parented to anything
                    joined.select = True
                    target.select = True
                    m3.make_active(target)
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                else:  # parented to the wrong object(not the target)
                    joined.select = True
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                    m3.make_active(target)
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        return returnlist

    def adjust_uvs_to_atlas(self, exportgroup):
        if self.decalatlas:
            decalatlaswidth = self.decalatlassize[0]
            decalatlasheight = self.decalatlassize[1]
            decalatlasmidx = decalatlaswidth / 2
            decalatlasmidy = decalatlasheight / 2

        if self.infoatlas:
            infoatlaswidth = self.infoatlassize[0]
            infoatlasheight = self.infoatlassize[1]
            infoatlasmidx = infoatlaswidth / 2
            infoatlasmidy = infoatlasheight / 2

        for obj in exportgroup.objects:
            if obj["DM"]["isdecal"] and obj["DM"]["type"] != "Material":
                if len(obj.users_scene) > 0:
                    m3.make_active(obj)

                    # before anything is done, all mirror modifiers need to be applied
                    # and to avoid redundant iteration later, let's also apply all others (displace, shrinkwrap, data_transfer etc)
                    for mod in obj.modifiers:
                        if "displace" in mod.name.lower() and bpy.context.scene.decals.removedisplace:
                            bpy.ops.object.modifier_remove(modifier=mod.name)
                        else:
                            try:
                                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                            except RuntimeError as e:
                                if mod.name == "M3_copied_normals" and str(e) == "Error: Modifier is disabled, skipping apply\n":
                                    target = bpy.data.objects[exportgroup['target']]
                                    mod.object = target
                                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                                    print("DataTransfer Modifier '%s' on decal '%s' had missing normal source. Added groups '%s' target object '%s' and applied the mod." % (mod.name, obj.name, exportgroup.name, target.name))
                            except:
                                print("Falled to apply  Modifier '%s' on decal '%s'" % (mod.name, obj.name))

                    m3.set_mode("EDIT")
                    m3.set_mode("FACE")
                    m3.unhide_all("MESH")
                    m3.select_all("MESH")

                    # create second uv channel for atlas UVs, turns out, its not needed however and in fact counter productive for unity for instance
                    # atlasUVs = obj.data.uv_textures.new('AtlasUVs')
                    # atlasUVs.active = True
                    # atlasUVs.active_render = True

                    oldcontext = m3.change_context("IMAGE_EDITOR")
                    unlink_any_image()

                    # this needs to be turned on, otherwise nothing will be selected in uv and so nothing will be scaled up
                    bpy.context.scene.tool_settings.use_uv_select_sync = True

                    if "panel_decal" in obj.name:
                        # ensure the panel strip UVs are perfectly centered and fit the uv space

                        # pivot point needs to be set to bounding box center first, otherwise snapping the cursor to the selection won't work as expected for some reason
                        bpy.context.space_data.pivot_point = 'CENTER'

                        # center the cursor to the selection
                        bpy.ops.uv.snap_cursor(target='SELECTED')

                        # cursor location is based on a 0-255 uv space
                        curx, cury = bpy.context.area.spaces.active.cursor_location

                        # move to the center
                        movex = (128 - curx) / 256
                        movey = (128 - cury) / 256

                        # but translaste works in 0-1 space
                        bpy.ops.transform.translate(value=(movex, movey, 0))

                        # all scaling needs to happen in relation to the center of uv space
                        bpy.context.area.spaces.active.cursor_location = (128, 128)
                        bpy.context.space_data.pivot_point = 'CURSOR'

                        # panelig will normaly extend the uv bounds
                        # so, make it fit the uv space by scaling with bounds limited
                        bpy.context.space_data.uv_editor.lock_bounds = True
                        bpy.ops.transform.resize(value=(1000, 1000, 1000))
                        bpy.context.space_data.uv_editor.lock_bounds = False

                        # make the panneling not take up the enitre width of the texture, this will avoid bleedling at the open edges of panel strip loops
                        bpy.ops.transform.resize(value=(0.9, 1, 1))

                    posx = obj["DM"]['atlasuvs'][0]
                    posy = obj["DM"]['atlasuvs'][1]
                    width = obj["DM"]['atlasuvs'][2]
                    height = obj["DM"]['atlasuvs'][3]
                    midx = posx + width / 2
                    midy = posy + height / 2

                    # scaling the island
                    # also, while we are assigning the decal to an atlas, put that information into the export group as well
                    if any([x in obj.active_material.name for x in ["decal01", "decal02", "paneling01"]]):
                        scalex = width / decalatlaswidth
                        scaley = height / decalatlasheight

                        # can't directly append to the id array prop
                        atype = list(exportgroup["atlastype"])
                        if "decal" not in atype:
                            atype.append("decal")
                        exportgroup["atlastype"] = atype

                    elif "info01" in obj.active_material.name:
                        scalex = width / infoatlaswidth
                        scaley = height / infoatlasheight

                        atype = list(exportgroup["atlastype"])
                        if "info" not in atype:
                            atype.append("info")
                        exportgroup["atlastype"] = atype

                    # all scaling needs to happen in relation to the center of uv space
                    bpy.context.area.spaces.active.cursor_location = (128, 128)
                    bpy.context.space_data.pivot_point = 'CURSOR'

                    # scaling the uv island
                    bpy.ops.transform.resize(value=(scalex, scaley, 1))

                    # moving the island
                    # NOTE: for the transform when called via script, the move values need to be adjusted to a uv 0-1 range hence the atlaswidth/atlasheight divisior
                    if any([x in obj.active_material.name for x in ["decal01", "decal02", "paneling01"]]):
                        movex = (midx - decalatlasmidx) / decalatlaswidth
                        movey = (decalatlasmidy - midy) / decalatlasheight
                    elif "info01" in obj.active_material.name:
                        movex = (midx - infoatlasmidx) / infoatlaswidth
                        movey = (infoatlasmidy - midy) / infoatlasheight

                    bpy.ops.transform.translate(value=(movex, movey, 0))

                    m3.change_context(oldcontext)

                    m3.set_mode("OBJECT")

        exportgroup["uvs"] = True

    def set_packing_data(self, exportgroup):
        for obj in exportgroup.objects:
            if obj["DM"]["isdecal"] and obj["DM"]["type"] != "Material":
                if len(obj.users_scene) > 0:  # objects with 0 scene users are backups from the previous step
                    mat = obj.material_slots[0].material

                    for node in mat.node_tree.nodes:
                        if node.type == "TEX_IMAGE":
                            path = os.path.abspath(bpy.path.abspath(node.image.filepath))
                            if "ao_curv_height" in path:
                                templatepath = path.replace("ao_curv_height", "MAPTYPE")
                                obj["DM"]["atlasuvs"] = self.decalatlasfullboxes[templatepath]
                                break
                            if "info01" in path:
                                obj["DM"]["atlasuvs"] = self.infoatlasfullboxes[path]
                                break

    def backup_decals(self, exportgroup):
        # NOTE: unlinked objects remain objects of the group
        # a way to tell linked and unlinked ones appart is by checking for the length of the obj.users_scene list
        linktogroup = []
        for obj in exportgroup.objects:
            if obj["DM"]["isdecal"] and obj["DM"]["type"] != "Material":
                # stash away the original
                bpy.context.scene.objects.unlink(obj)
                obj.use_fake_user = True

                # make a duplicate
                decalbackup = obj.copy()
                decalbackup.data = obj.data.copy()
                bpy.context.scene.objects.link(decalbackup)

                # adding the duplicatres to the group right now will hang blender, likely because you are iterating over the group right now
                linktogroup.append(decalbackup)

        for obj in linktogroup:
            exportgroup.objects.link(obj)

    def create_exportgroup(self, selection):
        simple = bpy.context.scene.decals.simpleexportgroup
        nondecals = bpy.context.scene.decals.createnondecalsgroup
        active = m3.get_active()

        decalfound = False
        targetlist = []
        for obj in selection:
            if obj.type == "MESH":
                if "material_decal" in obj.name and not obj.name.startswith("projected_"):  # we are going to ignore material decals for potential bakedowns later, so mark them here
                    obj["DM"] = {"isdecal": True, "type": "Material"}
                    print("'%s' is a material decal." % (obj.name))
                else:
                    try:
                        matname = obj.material_slots[0].material.name
                    except:
                        self.report({'ERROR'}, "No material found for the potential target '%s', aborting." % (obj.name))
                        return None
                    if any([x in matname for x in ["decal01", "decal02", "info01", "paneling01"]]):
                        decalfound = True
                        obj["DM"] = {"isdecal": True, "type": "None"}
                    else:
                        obj["DM"] = {"isdecal": False}
                        targetlist.append(obj)

        # if decals are among the selection, check for presence of a single target
        if decalfound:
            print("Decal(s) found.")

            tlen = len(targetlist)

            targetfound = False
            if tlen == 0:
                print("No target found.")
                self.report({'ERROR'}, "No target found.\nExactly one Non-Decal needs to be in the selection to create an Export Group.")
                return None
            elif tlen > 1:
                # print("Multiple targets found.")
                if simple:
                    if active in targetlist:
                        targetfound = True
                        target = active
                    else:
                        self.report({'ERROR'}, "Simple Export Group: Active object '%s' can't be a Decal!\nMake a Non-Decal active or turn off 'Simple Export Group'." % (active.name))
                else:
                    self.report({'ERROR'}, "Multiple targets found: %s\nExactly one Non-Decal needs to be in the selection to create an Export Group.\nAlternatively, turn on 'Simple Export Group'" % (", ".join([obj.name for obj in targetlist])))
                    return None
            else:
                print("One target found.")
                targetfound = True
                simple = False  # if you run with simple enabled, but still only have one target in the list, then don't make it a simple group
                target = targetlist[0]
        else:
            # print("No Decals found.")
            self.report({'ERROR'}, "No Decals found. One or more Decals need to be in the selection to create an Export Group.")
            return None

        # if decals and a single target(with a material) exists, create export group and "tag" objects if they are decal or not
        if decalfound and targetfound:

            # check if decals are actally part of the atlas groups, if not you need to abort
            # first collect objs in all atlas groups
            atlasobjs = []
            for group in bpy.data.groups:
                if group.name.startswith("DM_atlas_"):
                    for obj in group.objects:
                        atlasobjs.append(obj)

            # then match decals against those objects
            for obj in selection:
                if obj.type == "MESH":
                    if obj["DM"]["isdecal"]:
                        if obj["DM"]["type"] != "Material":
                            if obj not in atlasobjs:
                                self.report({'ERROR'}, "'%s' is not part of any atlas group!" % (obj.name))
                                return None

            # proceed if all is good
            targetmatname = target.material_slots[0].material.name

            # create export group or use existing one
            if simple:
                groupname = "DM_export_" + target.name + "_SIMPLE"
            else:
                groupname = "DM_export_" + target.name
            if groupname not in bpy.data.groups:
                exportgroup = bpy.data.groups.new(groupname)
                print("Created export group: '%s'." % (groupname))
            else:
                exportgroup = bpy.data.groups[groupname]

            # add selection to export group
            for obj in selection:
                if obj.type == "MESH":
                    exportgroup.objects.link(obj)

            # set the targets nameand set the targetmaterial name as a group id property, this will be used for combining bakedowns into material/texturesets
            exportgroup["target"] = target.name
            exportgroup["material"] = targetmatname

            # also initate the atlastype list property, which will tell us what atlas types are used by the decals in the group, useful for resetting atlas solutions
            exportgroup["atlastype"] = []

            exportgroup["simple"] = simple

            # create group containing all targets/non-decals, for conveneance
            if nondecals:
                nondecalgroup = bpy.data.groups.get("DM_non-decals")

                if nondecalgroup is None:
                    nondecalgroup = bpy.data.groups.new("DM_non-decals")

                for obj in targetlist:
                    if obj.name not in nondecalgroup.objects:  # for whatever reason blender expects the .name here????
                        nondecalgroup.objects.link(obj)
                        print("Added '%s' to 'DM_non_decals' group" % (obj.name))

            return exportgroup
