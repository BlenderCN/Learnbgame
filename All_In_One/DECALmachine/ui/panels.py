import bpy
import os
import shutil
from .. utils.registration import get_prefs, get_path, set_new_decal_index, get_addon
from .. utils.ui import get_icon, draw_pil_warning
from .. utils.material import get_pbrnode_from_mat
from .. utils.system import abspath


class PanelDECALmachine(bpy.types.Panel):
    bl_idname = "MACHIN3_PT_decal_machine"
    bl_label = "DECALmachine"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MACHIN3"

    def draw_header(self, context):
        layout = self.layout

        dm = context.scene.DM

        row = layout.row(align=True)
        row.prop(dm, "register_panel_creation", text="", icon="SHADERFX")
        row.prop(dm, "register_panel_update_legacy", text="", icon="FILE_BACKUP")
        row.prop(dm, "register_panel_debug", text="", icon="MODIFIER")
        row.prop(dm, "register_panel_help", text="", icon="QUESTION")

    def draw(self, context):
        layout = self.layout

        dm = context.scene.DM
        wm = context.window_manager

        batchops, _, _, _ = get_addon("Batch Operations™")


        # COLLECTION

        box = layout.box()
        column = box.column()

        row = column.split(factor=0.33)
        row.label(text="Collections")
        r = row.row(align=True)
        r.prop(dm, "collection_decaltype", text="Type", toggle=True)
        r.prop(dm, "collection_decalparent", text="Parent", toggle=True)
        r.prop(dm, "collection_active", text="Active", toggle=True)


        # HIDING

        box = layout.box()
        column = box.column()

        row = column.row()
        row.label(text="Hide/Show")
        row.prop(dm, "hide_materials", text="Materials", toggle=True)
        row.prop(dm, "hide_textures", text="Textures", toggle=True)

        if batchops:
            row = column.row()
            row.label()
            row.prop(dm, "hide_decaltype_collections", text="Type Col", toggle=True)
            row.prop(dm, "hide_decalparent_collections", text="Parent Col", toggle=True)

        # QUALITY / NORMALTRANSFER

        box = layout.box()
        column = box.column()

        row = column.row()
        row.label(text="Quality")
        row.prop(dm, "glossyrays", toggle=True)
        row.prop(dm, "parallax", toggle=True)

        row = column.row()
        row.label(text="Normal Transfer")
        row.prop(dm, "normaltransfer_render", text="Render", toggle=True)
        row.prop(dm, "normaltransfer_viewport", text="Viewport", toggle=True)

        """
        # NOTE: BLENDER CRASH BUG WARNING, crash prevented as of https://developer.blender.org/rBfab573bac0e1fbc88f8208372b3a5a2f7415c517

        b = box.box()
        column = b.column()
        column.label(text="NOTE: Enabling Normal Transfers will cause frequent crashes", icon='INFO')
        row = column.row()
        row.label(text="due to this Blender bug, that needs fixing:")
        row.operator("wm.url_open", text="developer.blender.org").url = "https://developer.blender.org/T59338"
        """


        # INTERPOLATION

        box = layout.box()
        column = box.column()

        row = column.row()
        row.label(text="Normal Interpolation")
        row.prop(dm, "normalinterpolation", expand=True)

        row = column.row()
        row.label(text="Color Interpolation")
        row.prop(dm, "colorinterpolation", expand=True)

        row = column.row()
        row.label(text="Blend Mode")
        row.prop(dm, "alpha_blendmode", expand=True)

        row = column.row()
        row.label(text="AO & Invert")
        row.prop(dm, "ao_strength")
        row.prop(dm, "invert_infodecals", text="Invert", toggle=True)

        row = column.split(factor=0.33)
        row.label(text="Edge Highlights")
        r = row.row()
        r.prop(dm, "edge_highlights", expand=True)

        box = layout.box()
        column = box.column()

        row = column.split(factor=0.33)
        row.label(text="Decal Align")
        r = row.row()
        r.prop(dm, "align_mode", expand=True)

        row = column.split(factor=0.33)
        row.label(text="Auto-Match")
        r = row.row()
        r.prop(dm, "auto_match", expand=True)

        if dm.auto_match == "MATERIAL":
            row = column.split(factor=0.33)
            row.label(text="Material")
            r = row.row()
            r.prop(wm, "matchmaterial", text="")

            mat = bpy.data.materials.get(wm.matchmaterial)
            icon = "refresh" if wm.matchmaterial == "None" or (mat and get_pbrnode_from_mat(mat)) else "refresh_red"

            r.operator("machin3.update_match_materials", text="", icon_value=get_icon(icon))


class PanelDecalCreation(bpy.types.Panel):
    bl_idname = "MACHIN3_PT_decal_creation"
    bl_label = "Decal Creation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MACHIN3"

    def draw(self, context):
        layout = self.layout

        dm = context.scene.DM

        sel = context.selected_objects
        active = context.active_object

        # CREATE

        box = layout.box()
        box.label(text="Create")

        row = box.row()
        row.scale_y = 1.2
        row.prop(dm, "create_decaltype", expand=True)

        if dm.create_decaltype == "INFO":
            b = box.box()
            b.label(text="Texture Settings")

            row = b.split(factor=0.33)
            row.label(text="Source")
            r = row.row()
            r.prop(dm, "create_infotype", expand=True)

            if dm.create_infotype == 'IMAGE':
                self.draw_info_from_image_creation(context, dm, b)

            elif dm.create_infotype == 'FONT':
                self.draw_info_from_text_creation(context, dm, b)

            elif dm.create_infotype == 'GEOMETRY':
                self.draw_info_from_geometry_creation(context, dm, b)

        else:
            b = box.box()
            b.label(text="Bake Settings")

            self.draw_simple_subset_panel_creation(context, dm, b)

        draw_pil_warning(box)

        self.draw_create_button(dm, box, sel)


        # INSTANT DECAL LIBRARY

        if bpy.types.WindowManager.instantdecallib[1]['items']:
            box = layout.box()
            action = "Remove" if get_prefs().decalremovemode else "Load"
            box.label(text="%s Instant Decals" % (action))

            self.draw_instant_decals(context, box)

        elif get_prefs().decalremovemode:
            box = layout.box()
            box.label(text="Toggle Remove")

            row = box.row()
            row.prop(get_prefs(), "decalremovemode", text="Remove Decals")


        # ADD TO LIBRARY

        if active and active.DM.isdecal:
            box = layout.box()
            box.label(text="Add to Library")

            self.draw_add_to_library(context, dm, box)

    def draw_add_to_library(self, context, dm, layout):
        column = layout.column()

        wm = context.window_manager

        if not wm.newdecalidx:
            set_new_decal_index(self, context)

        decals = [obj for obj in context.selected_objects if obj.DM.isdecal and not obj.DM.isprojected and not obj.DM.issliced]

        decalname = dm.addlibrary_decalname
        decalidx = wm.newdecalidx
        library = context.scene.userdecallibs

        # library selection
        if context.scene.userdecallibs:
            row = column.split(factor=0.33)
            row.label(text="User Decal Library")
            row.prop(context.scene, "userdecallibs", text="")
        else:
            column.label(text="Create a new Library or Unlock an existing one.")

        row = column.split(factor=0.33)
        row.label(text="Decal Name(optional)")
        row.prop(dm, "addlibrary_decalname", text="")

        if decalname:
            pathstr = ["%s / %s / %s_%s" % (os.path.basename(get_prefs().assetspath), library, decalidx, decalname.strip().replace(" ", "_"))]
            if len(decals) == 2:
                pathstr.append("%s / %s / %s_%s" % (os.path.basename(get_prefs().assetspath), library, str(int(decalidx) + 1).zfill(3), decalname.strip().replace(" ", "_")))
            elif len(decals) > 2:
                pathstr.append("...")
                pathstr.append("%s / %s / %s_%s" % (os.path.basename(get_prefs().assetspath), library, str(int(decalidx) + len(decals) - 1).zfill(3), decalname.strip().replace(" ", "_")))
        else:
            pathstr = ["%s / %s / %s" % (os.path.basename(get_prefs().assetspath), library, decalidx)]
            if len(decals) == 2:
                pathstr.append("%s / %s / %s" % (os.path.basename(get_prefs().assetspath), library, str(int(decalidx) + 1).zfill(3)))
            elif len(decals) > 2:
                pathstr.append("...")
                pathstr.append("%s / %s / %s" % (os.path.basename(get_prefs().assetspath), library, str(int(decalidx) + len(decals) - 1).zfill(3)))

        row = column.split(factor=0.33)
        row.label(text="Path Preview")
        col = row.column()
        for ps in pathstr:
            col.label(text=ps, icon="FILE_FOLDER")

        row = column.split(factor=0.33)
        row.label(text="Thumbnail Tint")
        row.prop(dm, "create_thumbnail_tint", text="")

        column = layout.column()

        row = column.row()
        row.scale_y = 1.5
        row.operator("machin3.add_decal_to_library", text="Add %s to Library" % ("Decal" if len(decals) <= 1 else "Decals"))

    def draw_instant_decals(self, context, layout):
        wm = context.window_manager

        libraryscale = get_prefs().libraryscale
        decalsinlibraryscale = get_prefs().decalsinlibraryscale

        column = layout.column()
        column.template_icon_view(wm, "instantdecallib", show_labels=False, scale=libraryscale, scale_popup=decalsinlibraryscale)

        decalmode = get_prefs().decalmode

        if decalmode == "INSERT":
            text, icon = "", get_icon("plus")
            idname = "machin3.insert_decal"

        elif decalmode == "REMOVE":
            text, icon = ("", get_icon("cancel"))
            idname = "machin3.remove_decal"

        op = column.operator(idname, text=text, icon_value=icon)
        op.library = "INSTANT"
        op.decal = getattr(wm, "instantdecallib")
        op.instant = True

        if decalmode == "INSERT":
            op.force_cursor_align = True

        row = column.row()
        row.prop(get_prefs(), "decalremovemode", text="Remove Decals")

    def draw_info_from_geometry_creation(self, context, dm, layout):
        row = layout.split(factor=0.33)

        row.label(text="Anti Aliasing, Padding")
        r = row.row()
        r.prop(dm, "bake_supersample", expand=True)

        rr = r.row(align=True)
        rr.prop(dm, "create_infotext_padding", text="")
        rr.operator("machin3.reset_infotext_offset_padding", text="", icon="LOOP_BACK").type = "PADDING"

        row = layout.split(factor=0.33)
        row.label(text="Resolution")
        r = row.row()
        r.prop(dm, "bake_resolution", expand=True)

        row = layout.split(factor=0.33)
        row.label(text="Thumbnail Tint")
        row.prop(dm, "create_thumbnail_tint", text="")

        row = layout.split(factor=0.33)
        row.label(text="Debug")
        row.prop(dm, "bake_inspect")

    def draw_info_from_text_creation(self, context, dm, layout):
        wm = context.window_manager
        WM = bpy.types.WindowManager

        row = layout.row()

        row.scale_y = 1.2

        row.operator("machin3.load_fonts", text="Load Font")
        row.operator("machin3.clear_fonts", text="Clear Fonts")

        # check if in font collection mode, if so, turn it off  and compare current images with the excludedimages collection prop
        # to determine new images, copy these to assets/Create/info
        if wm.collectinfofonts:
            wm.collectinfofonts = False

            createpath = os.path.join(get_path(), "assets", "Create")
            fontspath = os.path.join(createpath, "infofonts")

            newfonts = ([font for font in bpy.data.fonts if font.name not in wm.excludefonts and len(font.name) < 63])

            if newfonts:
                last = newfonts[-1].name + ".ttf"

                for font in newfonts:
                    shutil.copy(abspath(font.filepath), os.path.join(fontspath, font.name + ".ttf"))
                    bpy.data.fonts.remove(font, do_unlink=True)

                wm.excludefonts.clear()

                # Note: updating the preview collection can't be done from here, so it's done using a handler watching this prop
                wm.updateinfofonts = last


        if WM.infofonts[1]['items']:
            layout.template_icon_view(wm, "infofonts", show_labels=True, scale=4, scale_popup=8)

            row = layout.split(factor=0.33)
            row.label(text="Font")
            row.label(text=wm.infofonts)
            row.prop(dm, "create_infotext_size", text="Size")

            row = layout.split(factor=0.33)
            row.scale_y = 1.5
            row.label(text="Text")
            row.prop(dm, "create_infotext", text="")

            row = layout.split(factor=0.33)
            row.label(text="Colors")
            row.prop(dm, "create_infotext_color", text="")

            row.prop(dm, "create_infotext_bgcolor", text="")

            if "\\n" in dm.create_infotext:
                row = layout.split(factor=0.33)
                row.label(text="Align Text")
                r = row.row()
                r.prop(dm, "create_infotext_align", expand=True)

            row = layout.split(factor=0.33)
            row.label(text="Padding, Offset")
            r = row.row()

            rs = r.row(align=True)
            rs.prop(dm, "create_infotext_padding", text="")
            rs.operator("machin3.reset_infotext_offset_padding", text="", icon="LOOP_BACK").type = "PADDING"

            rs = r.row(align=True)
            rs.prop(dm, "create_infotext_offset", text="")
            rs.operator("machin3.reset_infotext_offset_padding", text="", icon="LOOP_BACK").type = "OFFSET"

            row = layout.split(factor=0.33)
            row.label(text="Thumbnail Tint")
            row.prop(dm, "create_thumbnail_tint", text="")

    def draw_info_from_image_creation(self, context, dm, layout):
        wm = context.window_manager
        WM = bpy.types.WindowManager

        row = layout.row()
        row.scale_y = 1.2

        row.operator("machin3.load_images", text="Load Image(s)")
        row.operator("machin3.clear_images", text="Clear Images")

        # check if in image collection mode, if so, turn it off  and compare current images with the excludedimages collection prop
        # to determine new images, copy these to assets/Create/info
        if wm.collectinfotextures:
            wm.collectinfotextures = False

            createpath = os.path.join(get_path(), "assets", "Create")
            infopath = os.path.join(createpath, "infotextures")

            newimages = ([img for img in bpy.data.images if img.name not in wm.excludeimages and len(img.name) < 63])

            if newimages:
                last = newimages[-1].name

                for img in newimages:
                    shutil.copy(abspath(img.filepath), os.path.join(infopath, img.name))
                    bpy.data.images.remove(img, do_unlink=True)

                wm.excludeimages.clear()

                # Note: updating the preview collection can't be done from here, so it's done using a handler watching this prop
                wm.updateinfotextures = last


        if WM.infotextures[1]['items']:
            layout.template_icon_view(wm, "infotextures", show_labels=True, scale=4, scale_popup=8)


        row = layout.split(factor=0.33)
        row.label(text="Crop, Padding")
        row.prop(dm, "create_infoimg_crop", toggle=True)
        r = row.row()
        r.active = dm.create_infoimg_crop
        r.prop(dm, "create_infoimg_padding", text="")


        row = layout.split(factor=0.33)
        row.label(text="Thumbnail Tint")
        row.prop(dm, "create_thumbnail_tint", text="")

    def draw_simple_subset_panel_creation(self, context, dm, layout):
        row = layout.split(factor=0.33)
        row.label(text="Anti Aliasing")
        r = row.row()
        r.prop(dm, "bake_supersample", expand=True)

        r = row.row()
        r.active = context.scene.DM.bake_supersample != "0"
        r.prop(dm, "bake_supersamplealpha", text="Alpha", toggle=True)

        row = layout.split(factor=0.33)
        row.label(text="Resolution")
        r = row.row()
        r.prop(dm, "bake_resolution", expand=True)

        row = layout.split(factor=0.33)
        row.label(text="AO")
        r = row.row()
        r.prop(dm, "bake_aosamples", expand=True)
        row.prop(dm, "bake_aocontrast")

        row = layout.split(factor=0.33)
        row.label(text="Curvature")
        row.prop(dm, "bake_curvaturewidth")
        row.prop(dm, "bake_curvaturecontrast")

        row = layout.split(factor=0.33)
        row.label(text="Height")
        row.prop(dm, "bake_heightdistance")

        row = layout.split(factor=0.33)
        row.label(text="Alpha")
        col = row.column()
        col.prop(dm, "bake_limit_alpha_to_active", text="Limit to Active")
        col.prop(dm, "bake_limit_alpha_to_boundary", text="Limit to Boundary")
        col.prop(dm, "bake_flatten_alpha_normals", text="Flatten Normals")

        if dm.create_decaltype == "PANEL":
            row = layout.split(factor=0.33)
            row.label(text="Mask")
            row.prop(dm, "bake_maskmat2")

        row = layout.split(factor=0.33)
        row.label(text="Thumbnail Tint")
        row.prop(dm, "create_thumbnail_tint", text="")

        row = layout.split(factor=0.33)
        row.label(text="Debug")
        row.prop(dm, "bake_inspect")

    def draw_create_button(self, dm, layout, sel):
        row = layout.row()
        row.scale_y = 1.5

        if dm.create_decaltype == "SIMPLESUBSET":
            decaltype = "SIMPLE" if len(sel) == 1 else "SUBSET" if len(sel) > 1 else ""

        else:
            decaltype = dm.create_decaltype

        row.operator("machin3.create_decal", text="Create %s Decal" % (decaltype))


class PanelUpdateLegacyDecalLibraries(bpy.types.Panel):
    bl_idname = "MACHIN3_PT_update_legacy_decal_libraries"
    bl_label = "Update Legacy Decal Libraries"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MACHIN3"


    def draw(self, context):
        layout = self.layout
        column = layout.column()

        dm = context.scene.DM

        box = layout.box()
        box.label(text="Update")

        column = box.column()

        row = column.split(factor=0.33)
        row.label(text="Update Library Path")
        row.prop(context.scene.DM, "updatelibrarypath", text="")

        if context.scene.userdecallibs:
            row = column.split(factor=0.33)
            row.label(text="User Decal Library")
            row.prop(context.scene, "userdecallibs", text="")
        else:
            column.label(text="Create a new Library or Unlock an existing one.")

        row = column.split(factor=0.33)
        row.label(text="Settings")

        col = row.column()
        col.prop(dm, "update_fix_legacy_normals")
        col.prop(dm, "update_store_uuid_with_old_decals")
        col.prop(dm, "update_keep_old_thumbnails")

        if not dm.update_keep_old_thumbnails:
            row = column.split(factor=0.33)
            row.label(text="Thumbnail Tint")
            row.prop(dm, "create_thumbnail_tint", text="")

        if dm.update_fix_legacy_normals:
            draw_pil_warning(box, needed="to fix legacy normals")

        column = box.column()

        row = column.row()
        row.scale_y = 1.5
        row.operator("machin3.update_legacy_decal_library", text="Update Decal Library")


class PanelDebug(bpy.types.Panel):
    bl_idname = "MACHIN3_PT_debug_decal_machine"
    bl_label = "Debug Decals"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MACHIN3"

    def draw(self, context):
        dm = context.scene.DM

        layout = self.layout

        box = layout.box()
        box.label(text="Validate")
        column = box.column()

        row = column.row()
        row.scale_y = 1.2
        row.operator("machin3.validate_decal", text="Validate Decal")

        box = layout.box()
        box.label(text="Texture Paths")
        column = box.column()

        row = column.row()
        row.scale_y = 1.2
        row.operator("machin3.fix_decal_texture_paths", text="Fix Texture Paths")


        if getattr(bpy.types, "MACHIN3_OT_debug_whatever", False):
            box = layout.box()
            box.label(text="Developer")
            column = box.column()

            column = box.column()
            row = column.row()
            row.scale_y = 1.2
            row.operator("machin3.debug_whatever", text="Debug Whatever")

        if dm.debug:
            box = layout.box()
            box.label(text="Update")
            column = box.column()

            if context.scene.userdecallibs:
                row = column.split(factor=0.33)
                row.label(text="User Decal Library")
                row.prop(context.scene, "userdecallibs", text="")
            else:
                column.label(text="Create a new Library or Unlock an existing one.")

            row = column.split(factor=0.33)
            row.label(text="Thumbnail Tint")
            row.prop(dm, "create_thumbnail_tint", text="")

            column = box.column()
            row = column.row()
            row.scale_y = 1.2
            row.operator("machin3.fix_legacy_normals", text="Fix Legacy Normals")

            column = box.column()
            row = column.row()
            row.scale_y = 1.2
            row.operator("machin3.rerender_decal_thumbnails", text="Re-Render Decal Thumbnails")

            column = box.column()
            row = column.row()
            row.scale_y = 1.2
            row.operator("machin3.update_decal_node_tree", text="Update Decal NodeTrees")

            column = box.column()
            row = column.row()
            row.scale_y = 1.2
            row.operator("machin3.replace_material", text="Replace Material")

            column = box.column()
            row = column.row()
            row.scale_y = 1.2
            row.operator("machin3.set_props_and_name_from_material", text="Set Props and Name from Material")

            column = box.column()
            row = column.row()
            row.scale_y = 1.2
            row.operator("machin3.update_decal_backup", text="Update Decal Backup.")


class PanelHelp(bpy.types.Panel):
    bl_idname = "MACHIN3_PT_help_decal_machine"
    bl_label = "DECALmachine Help"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MACHIN3"

    def draw(self, context):
        layout = self.layout

        resources_path = os.path.join(get_path(), "resources")
        example_path = os.path.join(resources_path, "Example.blend")
        example_decalcreation_path = os.path.join(resources_path, "Example_DecalCreation.blend")

        box = layout.box()
        box.label(text="Help")

        b = box.box()
        b.label(text="Examples")
        column = b.column()

        row = column.row()
        row.scale_y = 1.2
        row.operator_context = 'EXEC_DEFAULT'
        op = row.operator("wm.open_mainfile", text="Decals", icon="FILE_FOLDER")
        op.filepath=example_path
        op.load_ui = True
        op = row.operator("wm.open_mainfile", text="Decal Creation", icon="FILE_FOLDER")
        op.filepath=example_decalcreation_path
        op.load_ui = True

        b = box.box()
        b.label(text="Documentation")
        column = b.column()

        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text="Local", icon='FILE_BACKUP').url = os.path.join(get_path(), "docs", "index.html")
        row.operator("wm.url_open", text="Online", icon='FILE_BLEND').url = "https://machin3.io/DECALmachine/docs"

        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text="FAQ", icon='QUESTION').url = "https://machin3.io/DECALmachine/docs/faq"
        row.operator("wm.url_open", text="Youtube", icon='FILE_MOVIE').url = "https://www.youtube.com/playlist?list=PLcEiZ9GDvSdWiU2BPQp99HglGGg1OGiHs"

        b = box.box()
        b.label(text="Decal Resources")
        column = b.column()

        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text="Decal Packs", icon='RENDER_RESULT').url = "https://machin3.io/DECALmachine/docs/decal_resources"


        b = box.box()
        b.label(text="Discussion")
        column = b.column()

        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text="Blender Artists", icon="COMMUNITY").url = "https://blenderartists.org/t/decalmachine/688181"
        row.operator("wm.url_open", text="polycount", icon="COMMUNITY").url = "https://polycount.com/discussion/210294/blender-decalmachine-surface-detailing-using-mesh-decals"


        b = box.box()
        b.label(text="Support")
        column = b.column()

        row = column.row()
        row.scale_y = 1.2
        row.operator("machin3.get_decalmachine_support", text="Request Support", icon='GREASEPENCIL')


        b = box.box()
        b.label(text="Follow Development")
        column = b.column()

        row = column.row()
        row.scale_y = 1.2
        row.operator("wm.url_open", text="Twitter @machin3io").url = "https://twitter.com/machin3io"
        row.operator("wm.url_open", text="Twitter #DECALmachine").url = "https://twitter.com/search?q=%23DECALmachine"
