import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty
import os
from uuid import uuid4
from .. utils.registration import get_prefs
from .. utils.ui import get_icon
from .. utils.material import get_decalmat, get_decal_textures, get_parallaxgroup_from_decalmat, get_heightgroup_from_parallaxgroup, get_decalgroup_from_decalmat
from .. items import decaltype_items


class Validate(bpy.types.Operator):
    bl_idname = "machin3.validate_decal"
    bl_label = "MACHIN3: Validate Decal"

    fixmissingtextures: BoolProperty(name="Fix missing Textures", default=False)

    generateuuid: BoolProperty(name="Generate new UUID", default=False)

    setdecaltype: BoolProperty(name="Set new decaltype", default=False)
    decaltype: EnumProperty(name="Decal Type", items=reversed(decaltype_items))

    setdecallibrary: BoolProperty(name="Set new decallibrary", default=False)
    decallibrary: StringProperty(name="Library")

    setdecalname: BoolProperty(name="Set new decalname", default=False)
    decalname: StringProperty(name="Name")

    setdecalmatname: BoolProperty(name="Set new decalmatname", default=False)
    decalmatname: StringProperty(name="Material Name")

    setdecalcreator: BoolProperty(name="Set new creator", default=False)

    @classmethod
    def poll(cls, context):
        return context.active_object in context.selected_objects

    def draw(self, context):
        layout = self.layout

        # BASIC ELEMENTS

        box = layout.box()

        column = box.column()

        if self.legacy:
            column.label(text="Legacy Decals need to be updated, before they can be used in Blender 2.80", icon_value=get_icon("info"))

        else:
            column.label(text="Basics")

            text, icon = (self.decal.name, "save") if self.decal else ("None", "error")
            column.label(text="Decal Object: %s" % (text), icon_value=get_icon(icon))

            text, icon = (self.decalmat.name, "save") if self.decalmat else ("None", "error")
            column.label(text="Decal Material: %s" % (text), icon_value=get_icon(icon))


            if self.decaltextures:
                text, icon = ("", "save") if self.hasrequiredtextures else ("missing required textures", "error")
                column.label(text="Decal Textures: %s" % (text), icon_value=get_icon(icon))
                for textype, img in sorted(self.decaltextures.items()):
                    column.label(text="  » %s: %s" % (textype, img.name), icon="BLANK1")

            else:
                column.label(text="Decal Textures: None", icon_value=get_icon("error"))


        # COMMON PROPERTIES

        if self.decal and self.decalmat and self.decaltextures:
            box = layout.box()

            column = box.column()
            column.label(text="Common Properties")

            if self.uuids and self.uuids_unique and self.uuids_complete:
                column.label(text="UUID: %s" %(self.uuids[0]), icon_value=get_icon("save"))
            else:
                row = column.row()
                row.label(text="UUID:", icon="BLANK1")
                row.label(text="present: %s" % (True if self.uuids else False), icon_value=get_icon("save") if self.uuids else get_icon("error"))
                row.label(text="unique: %s" % (self.uuids_unique), icon_value=get_icon("save") if self.uuids_unique else get_icon("error"))
                row.label(text="complete: %s" % (self.uuids_complete), icon_value=get_icon("save") if self.uuids_complete else get_icon("error"))

            if self.decaltypes and self.decaltypes_unique and self.decaltypes_complete:
                column.label(text="decaltype: %s" %(self.decaltypes[0]), icon_value=get_icon("save"))
            else:
                row = column.row()
                row.label(text="decaltype:", icon="BLANK1")
                row.label(text="present: %s" % (True if self.decaltypes else False), icon_value=get_icon("save") if self.decaltypes else get_icon("error"))
                row.label(text="unique: %s" % (self.decaltypes_unique), icon_value=get_icon("save") if self.decaltypes_unique else get_icon("error"))
                row.label(text="complete: %s" % (self.decaltypes_complete), icon_value=get_icon("save") if self.decaltypes_complete else get_icon("error"))

            if self.decallibraries and self.decallibraries_unique and self.decallibraries_complete:
                column.label(text="decallibrary: %s" %(self.decallibraries[0]), icon_value=get_icon("save"))
            else:
                row = column.row()
                row.label(text="decallibrary:", icon="BLANK1")
                row.label(text="present: %s" % (True if self.decallibraries else False), icon_value=get_icon("save") if self.decallibraries else get_icon("error"))
                row.label(text="unique: %s" % (self.decallibraries_unique), icon_value=get_icon("save") if self.decallibraries_unique else get_icon("error"))
                row.label(text="complete: %s" % (self.decallibraries_complete), icon_value=get_icon("save") if self.decallibraries_complete else get_icon("error"))


            if self.decalnames and self.decalnames_unique and self.decalnames_complete:
                column.label(text="decalname: %s" %(self.decalnames[0]), icon_value=get_icon("save"))
            else:
                row = column.row()
                row.label(text="decalname:", icon="BLANK1")
                row.label(text="present: %s" % (True if self.decalnames else False), icon_value=get_icon("save") if self.decalnames else get_icon("error"))
                row.label(text="unique: %s" % (self.decalnames_unique), icon_value=get_icon("save") if self.decalnames_unique else get_icon("error"))
                row.label(text="complete: %s" % (self.decalnames_complete), icon_value=get_icon("save") if self.decalnames_complete else get_icon("error"))


            if self.decalmatnames and self.decalmatnames_unique and self.decalmatnames_complete:
                column.label(text="decalmatname: %s" %(self.decalmatnames[0]), icon_value=get_icon("save"))
            else:
                row = column.row()
                row.label(text="decalmatname:", icon="BLANK1")
                row.label(text="present: %s" % (True if self.decalmatnames else False), icon_value=get_icon("save") if self.decalmatnames else get_icon("error"))
                row.label(text="unique: %s" % (self.decalmatnames_unique), icon_value=get_icon("save") if self.decalmatnames_unique else get_icon("error"))
                row.label(text="complete: %s" % (self.decalmatnames_complete), icon_value=get_icon("save") if self.decalmatnames_complete else get_icon("error"))


            if self.creators and self.creators_unique and self.creators_complete:
                column.label(text="creator: %s" %(self.creators[0]), icon_value=get_icon("save"))
            else:
                row = column.row()
                row.label(text="creator:", icon="BLANK1")
                row.label(text="present: %s" % (True if self.creators else False), icon_value=get_icon("save") if self.creators else get_icon("info"))
                row.label(text="unique: %s" % (self.creators_unique), icon_value=get_icon("save") if self.creators_unique else get_icon("info"))
                row.label(text="complete: %s" % (self.creators_complete), icon_value=get_icon("save") if self.creators_complete else get_icon("info"))


        # OBJECT and MATERIAL PROPERTIES

        if self.decal and self.decalmat:
            split = layout.split(factor=0.4)
        else:
            split = layout

        if self.decal:
            box = split.box()

            column = box.column()
            column.label(text="Object Properties")

            column.label(text="  » isbackup: %s" % (self.decal.DM.isbackup))
            backup = self.decal.DM.decalbackup
            column.label(text="  » decalbackup: %s" % (backup.name if backup else backup))

            column.label(text="  » isprojected: %s" % (self.decal.DM.isprojected))
            if self.decal.DM.isprojected:
                projectedon = self.decal.DM.projectedon
                column.label(text="    » projectedon: %s" % (projectedon.name if projectedon else projectedon))

            column.label(text="  » issliced: %s" % (self.decal.DM.issliced))
            if self.decal.DM.issliced:
                slicedon = self.decal.DM.slicedon
                column.label(text="    » slicedon: %s" % (slicedon.name if slicedon else slicedon))

        if self.decalmat:
            box = split.box()

            column = box.column()
            column.label(text="Material Properties")

            column.label(text="  » ismatched: %s" % (self.decalmat.DM.ismatched))
            if self.decalmat.DM.ismatched:
                matchedmaterialto = self.decalmat.DM.matchedmaterialto
                matchedmaterial2to = self.decalmat.DM.matchedmaterial2to
                matchedsubsetto = self.decalmat.DM.matchedsubsetto

                column.label(text="    » material: %s" % (matchedmaterialto.name if matchedmaterialto else matchedmaterialto))
                column.label(text="    » material2: %s" % (matchedmaterial2to.name if matchedmaterial2to else matchedmaterial2to))
                column.label(text="    » subset: %s" % (matchedsubsetto.name if matchedsubsetto else matchedsubsetto))

            column.label(text="  » isparallaxed: %s" % (self.decalmat.DM.isparallaxed))
            column.label(text="  » parallaxnodename: %s" % (self.decalmat.DM.parallaxnodename if self.decalmat.DM.parallaxnodename else "None"))

            if self.decalmat.DM.parallaxnodename:
                if self.pgroup and self.nameinsync:
                    text = "True"
                elif self.pgroup:
                    text = "True, but name differs"
                else:
                    text = "False"
                column.label(text="  » parallax group: %s" % (text))

                if self.pgroup:
                    column.label(text="    » height group texture: %s" % (True if self.heighttex else False))


        # ACTIONS

        if not self.legacy:
            box = layout.box()

            column = box.column()
            column.label(text="Actions")

            if self.decalmat:
                if not self.hasrequiredtextures:
                    column.prop(self, "fixmissingtextures")

            if self.decal and self.decalmat and self.decaltextures and not self.fixmissingtextures:
                column.prop(self, "generateuuid")

                """
                row = column.row()
                row.prop(self, "setdecaltype")
                if self.setdecaltype:
                    row.prop(self, "decaltype")

                row = column.row()
                row.prop(self, "setdecallibrary")
                if self.setdecallibrary:
                    if self.isasset:
                        row.label(text="Library: %s" % self.decallibrary)
                    else:
                        row.prop(self, "decallibrary")

                row = column.row()
                row.prop(self, "setdecalname")
                if self.setdecalname:
                    if self.isasset:
                        row.label(text="Library: %s" % self.decalname)
                    else:
                        row.prop(self, "decalname")

                row = column.row()
                row.prop(self, "setdecalmatname")
                if self.setdecalmatname:
                    if self.isasset:
                        row.label(text="Library: %s" % self.decalmatname)
                    else:
                        row.prop(self, "decalmatname")
                """
                row = column.row()
                row.prop(self, "setdecalcreator")
                if self.setdecalcreator:
                    row.label(text="Creator: %s" % get_prefs().decalcreator)

    def invoke(self, context, event):
        active = context.active_object
        self.decal, self.decalmat, self.decaltextures = self.get_basics(active)
        self.legacy = False
        self.isasset = False
        self.istemplate = False
        self.fixmissingtextures = False

        if all([self.decal, self.decalmat, self.decaltextures]):
            self.uuids, self.decaltypes, self.decallibraries, self.decalnames, self.decalmatnames, self.creators, count = self.get_sync()

            print(20 * "-")
            print("PROPERTY UNIQUENESS")

            self.uuids_unique = len(set(self.uuids)) == 1
            self.decaltypes_unique = len(set(self.decaltypes)) == 1
            self.decallibraries_unique = len(set(self.decallibraries)) == 1
            self.decalnames_unique = len(set(self.decalnames)) == 1
            self.decalmatnames_unique = len(set(self.decalmatnames)) == 1
            self.creators_unique = len(set(self.creators)) == 1

            print(" » unique UUIDs:", self.uuids_unique)
            print(" » unique decaltypes:", self.decaltypes_unique)
            print(" » unique decallibraries:", self.decallibraries_unique)
            print(" » unique decalnames:", self.decalnames_unique)
            print(" » unique decalmatnames:", self.decalmatnames_unique)
            print(" » unique creators:", self.creators_unique)


            print(20 * "-")
            print("PROPERTY SYNCHRONIZATION")

            self.uuids_complete = len(self.uuids) == count
            self.decaltypes_complete = len(self.decaltypes) == count
            self.decallibraries_complete = len(self.decallibraries) == count
            self.decalnames_complete = len(self.decalnames) == count
            self.decalmatnames_complete = len(self.decalmatnames) == count
            self.creators_complete = len(self.creators) == count

            print(" » complete UUIDs:", self.uuids_complete)
            print(" » complete decaltypes:", self.decaltypes_complete)
            print(" » complete decallibraries:", self.decallibraries_complete)
            print(" » complete decalnames:", self.decalnames_complete)
            print(" » complete decalmaterialnames:", self.decalmatnames_complete)
            print(" » complete decalcreators:", self.creators_complete)

            # initialize action props

            self.generateuuid = False

            self.setdecaltype = False
            self.decaltype = self.decal.DM.decaltype

            self.setdecallibrary = False
            self.setdecalname = False
            self.setdecalmatname = False

            # if the current blend file is a blend file in a decal library, the decallibrary, decalname and decalmatname props should be set by from the file/folder names, not by the user
            currentblend = bpy.data.filepath
            if get_prefs().assetspath in currentblend:
                self.isasset = True

                decalpath = os.path.dirname(currentblend)
                basename = os.path.basename(decalpath)
                library = os.path.basename(os.path.dirname(decalpath))
                decalmatname = "%s_%s" % (library, basename)
                decalname = decalmatname

                self.decallibrary = library
                self.decalname = decalname
                self.decalmatname = decalmatname

            # if the current blend file is TEMPLATE.blend
            elif "Templates.blend" in currentblend:
                self.isasset = True
                self.istemplate = True

                basename = self.decaltype
                library = "TEMPLATE"
                decalmatname = "%s_%s" % (library, basename)
                decalname = decalmatname

                self.decallibrary = library
                self.decalname = decalname
                self.decalmatname = decalmatname

            else:
                self.decallibrary = self.decal.DM.decallibrary if self.decal.DM.decallibrary else self.decallibraries[0] if self.decallibraries else ""
                self.decalname = self.decal.DM.decalname if self.decal.DM.decalname else self.decalnames[0] if self.decalnames else ""
                self.decalmatname = self.decal.DM.decalmatname if self.decal.DM.decalmatname else self.decalmatnames[0] if self.decalmatnames else ""

            self.setdecalcreator = False

        else:
            mat = active.active_material

            if mat:
                dg = get_decalgroup_from_decalmat(mat)

                if dg.type == "GROUP" and dg.node_tree:
                    if "Decal" in dg.node_tree.name:
                        self.legacy = True


        width = 500 if (self.decal and self.decalmat) or self.legacy else 300

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=width)

    def execute(self, context):
        if self.decalmat:
            if self.fixmissingtextures:
                textures = get_decal_textures(self.decalmat, legacy=True)

                for _, img in textures.items():
                    img.DM.isdecaltex = True


        if self.decal and self.decalmat and self.decaltextures:
            if self.istemplate:
                uuid = ""
            else:
                uuid = str(uuid4())

            # update the uuid file as well
            if self.generateuuid and self.isasset and not self.istemplate:
                currentblend = bpy.data.filepath

                decalpath = os.path.dirname(currentblend)
                uuidpath = os.path.join(decalpath, "uuid")

                with open(uuidpath, "w") as f:
                    f.write(uuid)

            for component in [self.decal] + [self.decalmat] + list(self.decaltextures.values()):

                # generate new decal UUID
                if self.generateuuid:
                    component.DM.uuid = uuid

                """
                # set new decal type
                if self.setdecaltype:
                    component.DM.decaltype = self.decaltype

                # set new decal library
                if self.setdecallibrary:
                    component.DM.decallibrary = self.decallibrary

                # set new decal name
                if self.setdecalname:
                    component.DM.decalname = self.decalname
                    self.decal.name = self.decalname

                # set new decal material name
                if self.setdecalmatname:
                    component.DM.decalmatname = self.decalmatname
                    self.decalmat.name = self.decalmatname

                """
                # set decal creator
                if self.setdecalcreator:
                    component.DM.creator = "" if self.istemplate else get_prefs().decalcreator

            """
            # set additional elemets related to the decalmatname
            if self.setdecalmatname:
                decalgroup = get_decalgroup_from_decalmat(self.decalmat)

                if decalgroup:
                    decalgroup.name = "%s.%s" % (self.decalmat.DM.decaltype.lower(), self.decalmatname)
                    decalgroup.node_tree.name = "%s.%s" % (self.decalmat.DM.decaltype.lower(), self.decalmatname)

                parallaxgroup = get_parallaxgroup_from_decalmat(self.decalmat)

                if parallaxgroup:
                    parallaxgroup.name = "parallax.%s" % (self.decalmatname)
                    parallaxgroup.node_tree.name = "parallax.%s" % (self.decalmatname)
                    self.decalmat.DM.parallaxnodename = "parallax.%s" % (self.decalmatname)

                    heightgroups = get_heightgroup_from_parallaxgroup(parallaxgroup, getall=True)

                    if heightgroups:
                        for idx, hg in enumerate(heightgroups):
                            if idx == 0:
                                hg.node_tree.name = "height.%s" % (self.decalmatname)

                            hg.name = "height.%s" % (self.decalmatname)
                else:
                    self.decalmat.DM.parallaxnodename = ""


                imagenodes = get_decal_texture_nodes(self.decalmat, height=self.decaltype in ['SIMPLE', 'SUBSET'])

                for textype, node in imagenodes.items():
                    node.label = textype
                    node.name = "%s_%s" % (self.decalmatname, textype.lower())
                    if textype != "HEIGHT":
                        node.image.name = ".%s_%s" % (self.decalmatname, textype.lower())
                        node.image.DM.decaltextype = textype
            """

        return {'FINISHED'}

    def get_sync(self):
        uuids = []
        decaltypes = []
        decallibraries = []
        decalnames = []
        decalmatnames = []
        creators = []

        # decal obj

        if self.decal.DM.uuid:
            uuids.append(self.decal.DM.uuid)

        if self.decal.DM.decaltype:
            decaltypes.append(self.decal.DM.decaltype)

        if self.decal.DM.decallibrary:
            decallibraries.append(self.decal.DM.decallibrary)

        if self.decal.DM.decalname:
            decalnames.append(self.decal.DM.decalname)

        if self.decal.DM.decalmatname:
            decalmatnames.append(self.decal.DM.decalmatname)

        if self.decal.DM.creator:
            creators.append(self.decal.DM.creator)


        # decal material

        if self.decalmat.DM.uuid:
            uuids.append(self.decalmat.DM.uuid)

        if self.decalmat.DM.decaltype:
            decaltypes.append(self.decalmat.DM.decaltype)

        if self.decalmat.DM.decallibrary:
            decallibraries.append(self.decalmat.DM.decallibrary)

        if self.decalmat.DM.decalname:
            decalnames.append(self.decalmat.DM.decalname)

        if self.decalmat.DM.decalmatname:
            decalmatnames.append(self.decalmat.DM.decalmatname)

        if self.decalmat.DM.creator:
            creators.append(self.decalmat.DM.creator)


        count = 2
        for img in self.decaltextures.values():
            count += 1

            if img.DM.uuid:
                uuids.append(img.DM.uuid)

            if img.DM.decaltype != "NONE":
                decaltypes.append(img.DM.decaltype)

            if img.DM.decallibrary:
                decallibraries.append(img.DM.decallibrary)

            if img.DM.decalname:
                decalnames.append(img.DM.decalname)

            if img.DM.decalmatname:
                decalmatnames.append(img.DM.decalmatname)

            if img.DM.creator:
                creators.append(img.DM.creator)

        return uuids, decaltypes, decallibraries, decalnames, decalmatnames, creators, count

    def get_basics(self, active):
        decal = active if active.DM.isdecal else None
        decalmat = get_decalmat(active)
        decaltextures = get_decal_textures(decalmat, legacy=False) if decalmat else None


        print(20 * "-")
        print("DECAL BASICS")

        print(" » decal object:", decal)
        print(" » decal material:", decalmat)
        print(" » decal textures:", decaltextures)

        if decal:
            print(20 * "-")
            print("OBJECT PROPERTIES")

            print(" » isbackup:", decal.DM.isbackup)
            print(" » decalbackup:", decal.DM.decalbackup)

            print(" » isprojected:", decal.DM.isprojected)
            if decal.DM.isprojected:
                print("  » projectedon:", decal.DM.projectedon)

            print(" » issliced:", decal.DM.issliced)
            if decal.DM.issliced:
                print("  » slidedon:", decal.DM.slicedon)

        if decalmat:
            print(20 * "-")
            print("MATERIAL PROPERTIES")

            if decaltextures:
                print(" » decaltype:", decalmat.DM.decaltype)
                self.hasrequiredtextures = self.has_required_textures(decalmat.DM.decaltype, decaltextures)
                print("  » has all required textures:", self.hasrequiredtextures)

            print(" » ismatched:", decalmat.DM.ismatched)
            if decalmat.DM.ismatched:
                print("  » matchedmaterialto:", decalmat.DM.matchedmaterialto)
                print("  » matchedmaterial2to:", decalmat.DM.matchedmaterial2to)
                print("  » matchedsubsetto:", decalmat.DM.matchedsubsetto)

            print(" » isparallaxed:", decalmat.DM.isparallaxed)
            print(" » parallaxnodename:", decalmat.DM.parallaxnodename)

            if decalmat.DM.parallaxnodename:
                self.pgroup, self.nameinsync = self.has_prallax_group(decalmat)

                if self.pgroup and self.nameinsync:
                    print("  » parallax group:", True)
                elif self.pgroup:
                    print("  » parallax group:", True, ", but name differs")
                else:
                    print("  » parallax group:", False)

                if self.pgroup:
                    self.heighttex = self.has_functional_height_group(self.pgroup)
                    print("    » height group texture:", True if self.heighttex else False)

        return decal, decalmat, decaltextures

    def has_functional_height_group(self, pgroup):
        hgroup = get_heightgroup_from_parallaxgroup(pgroup)

        if hgroup:
            for node in hgroup.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    return node.image

    def has_prallax_group(self, decalmat):
        pgroup = get_parallaxgroup_from_decalmat(decalmat)

        if pgroup:
            if pgroup.name == decalmat.DM.parallaxnodename:
                return pgroup, True
            else:
                return pgroup, False
        else:
            return False, False

    def has_required_textures(self, decaltype, decaltextures):
        aocurvheight = "AO_CURV_HEIGHT" in decaltextures
        nrmalpha = "NRM_ALPHA" in decaltextures
        masks = "MASKS" in decaltextures
        coloralpha = "COLOR_ALPHA" in decaltextures

        pattern = (aocurvheight, nrmalpha, masks, coloralpha)

        requiredtextures = False
        if decaltype == "SIMPLE":
            if pattern == (True, True, False, False):
                requiredtextures = True

        elif decaltype in ["SUBSET", "PANEL"]:
            if pattern == (True, True, True, False):
                requiredtextures = True

        elif decaltype == "INFO":
            if pattern == (False, False, False, True):
                requiredtextures = True

        return requiredtextures
