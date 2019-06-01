import bpy
import os
import math
from .. import M3utils as m3


class DecalPie(bpy.types.Menu):
    bl_idname = "machin3.decal_pie"
    bl_label = "DECALmachine"

    def draw(self, context):
        selection = m3.selected_objects()
        selcount = len(selection)
        mode = bpy.context.mode
        active = bpy.context.active_object
        try:
            activemat = active.material_slots[-1].material
        except:
            activemat = None

        extraoptions = bpy.context.scene.decals.extraoptions
        hasdisplace, mod = self.checkdisplace()
        globalparallax = bpy.context.scene.decals.globalparallax
        globalglossy = bpy.context.scene.decals.globalglossy
        useDMassetloader = bpy.context.user_preferences.addons['DECALmachine'].preferences.useDMassetloader
        removemode = bpy.context.scene.decals.removemode

        layout = self.layout
        pie = layout.menu_pie()

        # LEFT
        if selcount == 0 and useDMassetloader:
            wm = context.window_manager
            box = pie.split()
            column = box.column()
            row = column.split(align=True)
            col = row.column()
            if removemode:
                op = col.operator("machin3.remove_decal01", text=" !!! REMOVE !!!")
            else:
                op = col.operator("machin3.insert_decal01", text="Insert")
            op.decal01_name = context.window_manager.decals01_preview
            col.template_icon_view(wm, "decals01_preview")
            col = row.column()
            if removemode:
                op = col.operator("machin3.remove_decal02", text=" !!! REMOVE !!!")
            else:
                op = col.operator("machin3.insert_decal02", text="Insert")

            op.decal02_name = context.window_manager.decals02_preview
            col.template_icon_view(wm, "decals02_preview")
        elif selcount >= 2:
            pie.operator("machin3.decal_project", text="Decal Project")
        else:
            pie.separator()

        # RIGHT
        if selcount == 0 and useDMassetloader:
            wm = context.window_manager
            box = pie.split()
            column = box.column()
            row = column.split(align=True)
            col = row.column()
            if removemode:
                op = col.operator("machin3.remove_info01", text=" !!! REMOVE !!!")
            else:
                op = col.operator("machin3.insert_info01", text="Insert")
            op.info01_name = context.window_manager.info01_preview
            col.template_icon_view(wm, "info01_preview")
            col = row.column()
            if removemode:
                op = col.operator("machin3.remove_panel_decal01", text=" !!! REMOVE !!!")
            else:
                op = col.operator("machin3.insert_panel_decal01", text="Insert")
            op.panel_decal01_name = context.window_manager.paneling01_preview
            col.template_icon_view(wm, "paneling01_preview")
        elif selcount == 1:
            if mode == "OBJECT":
                pie.operator("machin3.draw_slice", text="Slice (Draw)")
            else:
                pie.separator()
        elif selcount == 2:
            if mode == "OBJECT":
                box = pie.split()
                box.operator("machin3.topo_slice", text="Slice (Topo)")
                box.operator("machin3.float_slice", text="Slice (Float)")
            else:
                pie.separator()
        else:
            pie.separator()

        # BOTTOM
        box = pie.split()
        column = box.column()
        if selcount == 1:
            if "panel_decal" in active.name:
                column.operator("machin3.decal_panel_unwrap", text="Panel Unwrap")
                column.operator("machin3.decal_panel_flip", text="Panel Flip")
                column.operator("machin3.decal_panel_reconstruct_cutter", text="Reconstruct Panel Cutter")
            else:
                if mode == "OBJECT":
                    column.operator("machin3.decal_panelize", text="Panelize")
                    column.separator()

            if not active.name.startswith("normal_src_") and not active.name.startswith("surface_fix_"):
                column.operator("machin3.wstep", text="(W)Step")

            if active.mode == "EDIT" and not active.name.startswith("normal_src_") and not active.name.startswith("surface_fix_"):
                column.operator("machin3.surface_fix", text="Surface Fix")

            if active.mode == "OBJECT":
                if active.name.startswith("normal_src_"):
                    column.operator("machin3.edit_normal_source", text="Commit Normal Source")
                elif active.modifiers.get("M3_custom_normals"):
                    column.operator("machin3.edit_normal_source", text="Edit Normal Source")

                if active.name.startswith("surface_fix_"):
                    column.operator("machin3.edit_surface_fix", text="Commit Surface Fix")
                elif active.modifiers.get("M3_surface_fix"):
                    column.operator("machin3.edit_surface_fix", text="Edit Surface Fix")

            if self.checkbevel():
                if m3.HOps_check():
                    column.operator("machin3.dstep", text="(D)Step")
                column.separator()
        elif selcount == 2:
            if "panel" in selection[0].name and "panel" in selection[1].name:
                column.operator("machin3.decal_panel_transition", text="Panel Transition")
                column.separator()
            elif "panel" not in selection[0].name and "panel" not in selection[1].name:
                if mode == "OBJECT":
                    column.operator("machin3.decal_panelize", text="Panelize")
                    column.separator()
            column.operator("machin3.wstep", text="(W)Step")
            column.separator()
        elif selcount > 2:
            if mode == "OBJECT":
                if "panel" not in str([obj.name for obj in selection]):
                    column.operator("machin3.decal_panelize", text="Panelize")
                    column.separator()
            column.operator("machin3.wstep", text="(W)Step")
            column.separator()

        column.operator("machin3.cleanout_decal_texture_duplicates", text="Remove Duplicates")
        column.operator("machin3.cleanout_orphan_backups", text="Remove Orphans")

        # TOP
        box = pie.split()
        column = box.column()
        row = column.split(align=True)
        row.prop(bpy.context.scene.decals, "debugmode")
        row.prop(bpy.context.scene.decals, "extraoptions")
        column.separator()

        if extraoptions is True:
            column.prop(bpy.context.scene.decals, "removemode")
            column.separator()
            if selcount == 0:
                if globalparallax is True:
                    column.operator("machin3.toggle_parallax", text="Parallax Global OFF")
                else:
                    column.operator("machin3.toggle_parallax", text="Parallax Global ON")
                if globalglossy is True:
                    column.operator("machin3.toggle_glossy", text="Glossy Rays Global OFF")
                else:
                    column.operator("machin3.toggle_glossy", text="Glossy Rays Global ON")
            else:
                column.operator("machin3.toggle_parallax", text="Parallax Selected Toggle")
                column.operator("machin3.toggle_glossy", text="Glossy Selected Toggle")
            column.prop(bpy.context.scene.decals, "wstepremovesharps")
            column.separator()

        row = column.split(align=True)
        row.operator("machin3.wireframe_display_all", text="Wire Full")
        row.operator("machin3.wireframe_display_decals", text="Decals")
        row.operator("machin3.wireframe_display_none", text="None")
        column.separator()

        if selcount == 1:
            if hasdisplace:
                column.operator("machin3.decal_adjust_height", text="Adjust Decal Height")
                if extraoptions:
                    column.prop(active.modifiers[mod.name], "mid_level")
                column.separator()

        column.prop(bpy.context.scene.decals, "defaultpaneling")

        # TOP-LEFT
        if selcount == 1:
            if m3.get_timestamp(active) is not None:
                pie.operator("machin3.extract_decal_source", text="Extract Source")
            else:
                pie.separator()
        else:
            pie.separator()

        # TOP-RIGHT
        if selcount == 2:
            pie.operator("machin3.topo_knife", text="Knife (Topo)")
        else:
            pie.separator()

        # BOTTOM-LEFT
        box = pie.split()
        column = box.column()
        # separator spam to push the template stuff down, otherwise there would be overlap with the LEFT decal previews
        column.separator()
        column.separator()
        if selcount == 1:
            column.operator("machin3.init_base_material", text="Init Base Material")
        elif selcount == 2:
            row = column.split(align=True)
            row.operator("machin3.material_cut", text="Material Cut")
            row.operator("machin3.material_decal", text="(A)Material Decal")
            column.separator()
            column.operator("machin3.match_material", text="(V)Match")
            column.separator()
            column.operator("machin3.init_base_material", text="Init Base Material")
            column.separator()
        elif selcount > 2:
            column.operator("machin3.init_base_material", text="Init Base Material")

        # BOTTOM-RIGHT
        if selcount == 1:
            if "panel_decal" in bpy.context.active_object.name:
                pie.operator("machin3.change_panel_width", text="Change Panel Width")
        else:
            pie.separator()

    def checkdisplace(self):
        active = bpy.context.active_object

        if active is not None:
            for mod in active.modifiers:
                if "displace" in mod.name.lower():
                    return True, mod

        return False, None

    def checkbevel(self):
        active = bpy.context.active_object

        if active is not None:
            for mod in active.modifiers:
                if "bevel" in mod.name.lower():
                    return True

        return False


class DecalCreatePie(bpy.types.Menu):
    bl_idname = "machin3.decal_create_pie"
    bl_label = "DECALcreate"

    def draw(self, context):
        selection = m3.selected_objects()
        selcount = len(selection)
        filename = os.path.basename(bpy.data.filepath)

        print(filename)

        layout = self.layout
        pie = layout.menu_pie()

        # LEFT
        if selcount >= 1:
            op = pie.operator("machin3.instant_decal", text="Create Decal 64")
            op.resolution = 64
        else:
            pie.separator()

        # RIGHT
        if selcount >= 1:
            op = pie.operator("machin3.instant_decal", text="Create Decal 512")
            op.resolution = 512
        else:
            pie.separator()

        # BOTTOM
        if filename == "DECAL_create.blend":
            pie.operator("machin3.batch_decal", text="Batch Create Decals")
        else:
            box = pie.split()
            column = box.column()
            op = column.operator("machin3.instant_decal", text="Create Panel Decal 64")
            op.paneling = True
            op.resolution = 64
            op = column.operator("machin3.instant_decal", text="Create Panel Decal 128")
            op.paneling = True
            op.resolution = 128
            op = column.operator("machin3.instant_decal", text="Create Panel Decal 256")
            op.paneling = True
            op.resolution = 256
            op = column.operator("machin3.instant_decal", text="Create Panel Decal 512")
            op.paneling = True
            op.resolution = 512

        # TOP
        box = pie.split()
        column = box.column()
        row = column.split(align=True)
        row.separator()
        row.prop(bpy.context.scene.decals, "createreplacelast")
        column.separator()
        column.prop(bpy.context.scene.decals, "createheightcontrast")
        column.prop(bpy.context.scene.decals, "createparallaxvalue")
        column.separator()
        column.prop(bpy.context.scene.decals, "createaosamples")

        # TOP-LEFT
        if selcount >= 1:
            op = pie.operator("machin3.instant_decal", text="Create Decal 128")
            op.resolution = 128
        else:
            pie.separator()

        # TOP-RIGHT
        if selcount >= 1:
            op = pie.operator("machin3.instant_decal", text="Create Decal 256")
            op.resolution = 256
        else:
            pie.separator()

        # BOTTOM-LEFT
        pie.separator()

        # BOTTOM-RIGHT
        pie.separator()


class DecalExportPie(bpy.types.Menu):
    bl_idname = "machin3.decal_export_pie"
    bl_label = "DECALexport"

    def draw(self, context):
        scene = context.scene
        selection = m3.selected_objects()
        selcount = len(selection)

        exporttype = bpy.context.scene.decals.exporttype

        existsdecalgroup = "DM_atlas_decal" in bpy.data.groups
        existsinfogroup = "DM_atlas_info" in bpy.data.groups

        atlasgroups = []
        for group in bpy.data.groups:
            if "DM_atlas_" in group.name:
                atlasgroups.append(group)

        existsatlasgroup = len(atlasgroups) > 0

        exportgroups = []
        for group in bpy.data.groups:
            if "DM_export_" in group.name:
                exportgroups.append(group)

        existsexportgroup = len(exportgroups) > 0
        # existsbakedowngroup = "DM_bakedown_" in str(bpy.data.groups.keys())

        layout = self.layout
        pie = layout.menu_pie()

        # LEFT
        if scene.name != "DECALatlas":
            if existsdecalgroup:
                pie.separator()
            else:
                pie.separator()
        else:
            op = pie.operator("machin3.decal_export_atlas", text="Re-Pack Atlas", icon="FILE_REFRESH")
            op.repack = True
            op.atlastype = scene.decals.atlastype

        # RIGHT
        if scene.name != "DECALatlas":
            if existsinfogroup:
                pie.separator()
            else:
                pie.separator()
        else:
            pie.operator("machin3.decal_export_accept_atlas", text="Accept Atlas Solution", icon="FILE_TICK")

        # BOTTOM
        if scene.name != "DECALatlas":
            if all([group["json"] for group in atlasgroups]) and existsexportgroup:
                if exporttype == "DECALBakeDown":
                    pie.operator("machin3.decal_export", text="Bake Down")
                else:
                    pie.operator("machin3.decal_export", text="Export")
            else:
                pie.separator()
        else:
            pie.separator()

        # TOP
        if scene.name != "DECALatlas":
            if selcount > 0:
                if existsatlasgroup:
                    box = pie.split()
                    column = box.column()

                    if existsexportgroup:
                        row = column.row()

                        # create columns based on the amount of exportgroups and the rows number
                        rows = 10

                        # add an ALL button when there's multiple exportgroups, so we add 1 to the len here
                        if len(exportgroups) > 1:
                            columns = math.ceil((len(exportgroups) + 1) / rows)
                        else:
                            columns = math.ceil(len(exportgroups) / rows)

                        for c in range(columns):
                            col = row.column()
                            if len(exportgroups) > 1 and c == 0:
                                col.operator("machin3.decal_export_reset_export_group", text="Reset ALL Export Groups", icon="ERROR").groupname = "ALL"
                            for group in exportgroups[c * rows: c * rows + rows]:
                                if group['uvs']:
                                    col.operator("machin3.decal_export_reset_export_group", text="Reset " + group.name, icon="ERROR").groupname = group.name

                        column.separator()
                    else:
                        column.operator("machin3.decal_export_atlas_group", text="(A) Update Atlas Group")

                    self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, op="machin3.decal_export_export_group", text="(E) Create Export Group")
                    # column.operator("machin3.decal_export_export_group", text="Create Export Group")

                else:
                    pie.operator("machin3.decal_export_atlas_group", text="(A) Create Atlas Group")

            else:
                if existsatlasgroup:
                    box = pie.split()
                    column = box.column()

                    if existsexportgroup:
                        row = column.row()

                        # create columns based on the amount of exportgroups and the rows number
                        rows = 10

                        # add an ALL button when there's multiple exportgroups, so we add 1 to the len here
                        if len(exportgroups) > 1:
                            columns = math.ceil((len(exportgroups) + 1) / rows)
                        else:
                            columns = math.ceil(len(exportgroups) / rows)

                        for c in range(columns):
                            col = row.column()
                            if len(exportgroups) > 1 and c == 0:
                                col.operator("machin3.decal_export_reset_export_group", text="Reset ALL Export Groups", icon="ERROR").groupname = "ALL"
                            for group in exportgroups[c * rows: c * rows + rows]:
                                if group['uvs']:
                                    col.operator("machin3.decal_export_reset_export_group", text="Reset " + group.name, icon="ERROR").groupname = group.name
                        column.separator()

                    # only show "Use Existing Atlas" when at least one atlasgroup has no solution yet
                    if all([group["json"] for group in atlasgroups]):
                        column.separator()
                    else:
                        column.operator("machin3.decal_export_use_existing_atlas", text="(A) Use Existing Atlas", icon="IMAGE_RGB")
                else:
                    pie.separator()

        else:
            box = pie.split()
            column = box.column()
            column.prop(bpy.context.scene.decals, "atlaspadding")
            column.prop(bpy.context.scene.decals, "atlasdownsample")

        # TOP-LEFT
        if scene.name != "DECALatlas":
            if existsdecalgroup:
                if not bpy.data.groups["DM_atlas_decal"]["json"]:
                    op = pie.operator("machin3.decal_export_atlas", text="(D) Initiate DECAL Atlas", icon="IMAGE_RGB")
                    op.atlastype = "decal"
                    op.repack = False
                else:
                    op = pie.operator("machin3.decal_export_reset_atlas", text="Reset DECAL Atlas", icon="ERROR")
                    op.atlastype = "decal"
            else:
                pie.separator()
        else:
            pie.separator()

        # TOP-RIGHT
        if scene.name != "DECALatlas":
            if existsinfogroup:
                if not bpy.data.groups["DM_atlas_info"]["json"]:
                    op = pie.operator("machin3.decal_export_atlas", text="(F) Initiate INFO Atlas", icon="IMAGE_RGB")
                    op.atlastype = "info"
                    op.repack = False
                else:
                    op = pie.operator("machin3.decal_export_reset_atlas", text="Reset INFO Atlas", icon="ERROR")
                    op.atlastype = "info"
            else:
                pie.separator()
        else:
            pie.separator()

        # BOTTOM-LEFT
        if scene.name != "DECALatlas":
            if exporttype == "DECALBakeDown":
                box = pie.split()
                column = box.column()
                column.scale_x = 1.3

                if all([group["json"] for group in atlasgroups]) and existsexportgroup:
                    column.separator()
                    column.separator()
                    column.separator()
                    column.separator()
                    column.separator()
                    column.separator()

                    if existsdecalgroup:
                        column.label("Decals")
                        column.prop(bpy.context.scene.decals, "bakedownmapao")
                        column.prop(bpy.context.scene.decals, "bakedownmapcurvature")
                        column.prop(bpy.context.scene.decals, "bakedownmapheight")
                        column.prop(bpy.context.scene.decals, "bakedownmapnormal")
                        column.prop(bpy.context.scene.decals, "bakedownmapsubset")
                    if existsinfogroup:
                        column.label("Info Decals")
                        column.prop(bpy.context.scene.decals, "bakedownmapcolor")

                    column = box.column()
                    column.separator()
                    column.separator()
                    column.separator()
                    column.separator()
                    column.separator()
                    column.separator()

                    self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, prop="exporttype")

                    if bpy.context.scene.decals.bakedownexportfbx:
                        column.prop(bpy.context.scene.decals, "exportname")

                    self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, prop="bakedownexportfbx")

                    self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, prop="bakedownresolution")
                    self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, prop="bakedowndistance")
                    self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, prop="bakedownbias")
                    self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, prop="bakedowntransfersharps")
                    self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, prop="bakedownsbsnaming")
                    self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, prop="bakedowncombine")
                    if bpy.context.scene.decals.bakedowncombine:
                        self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, prop="bakedowncombineall")
            else:
                box = pie.split()
                column = box.column()
                column.scale_x = 1.1

                if all([group["json"] for group in atlasgroups]) and existsexportgroup:
                    column.prop(bpy.context.scene.decals, "exporttype")

                    if bpy.context.scene.decals.quickexport:
                        column.prop(bpy.context.scene.decals, "exportname")

                    column.prop(bpy.context.scene.decals, "quickexport")

                    if exporttype not in ["sketchfab", "unreal_engine_4"]:
                        column.prop(bpy.context.scene.decals, "triangulize")

                    if exporttype == "sketchfab":
                        if bpy.context.scene.decals.quickexport:
                            column.prop(bpy.context.scene.decals, "createarchive")

                        row = column.row()
                        row.prop(bpy.context.scene.decals, "extradisplace")
                        row.prop(bpy.context.scene.decals, "extradisplaceamnt")

                    if exporttype == "unpacked":
                        column.prop(bpy.context.scene.decals, "normalflipgreen")

                    if exporttype not in ["sketchfab", "substance_painter"]:
                        column.prop(bpy.context.scene.decals, "assignuniquematerials")
                        if bpy.context.scene.decals.assignuniquematerials:
                            column.prop(bpy.context.scene.decals, "treatfreestyleasseam")

                        column.prop(bpy.context.scene.decals, "extrasbsatlas")
                        column.prop(bpy.context.scene.decals, "parenttoroot")

                    if bpy.context.scene.decals.parenttoroot and "unity3d" in exporttype:
                        self.confirm_atlas_groups(column, existsdecalgroup, existsinfogroup, prop="unityrotfix")

        else:
            pie.separator()

        # BOTTOM-RIGHT
        if scene.name != "DECALatlas":
            box = pie.split()
            column = box.column()
            column.separator()
            column.separator()
            column.label("Atlas Groups + Atlas Creation")
            column.prop(bpy.context.scene.decals, "autoopenfolderforexistingatlas")
            column.prop(bpy.context.scene.decals, "autoinitiateafterreset")
            column.label("Export Groups + Atlas UVs")
            column.prop(bpy.context.scene.decals, "simpleexportgroup")
            column.prop(bpy.context.scene.decals, "createnondecalsgroup")
            column.prop(bpy.context.scene.decals, "removedisplace")
            column.label("Exporting")
            column.prop(bpy.context.scene.decals, "autoopenfolderafterexport")
        else:
            pie.separator()

    def confirm_atlas_groups(self, layoutelement, existsdecalgroup, existsinfogroup, prop=None, op=None, text=None):
        if prop:
            if existsdecalgroup and existsinfogroup:
                # if bpy.data.groups["DM_atlas_decal"]["json"] and bpy.data.groups["DM_atlas_info"]["json"] and bpy.data.groups["DM_atlas_decal"]["uvs"] and bpy.data.groups["DM_atlas_info"]["uvs"]:
                if bpy.data.groups["DM_atlas_decal"]["json"] and bpy.data.groups["DM_atlas_info"]["json"]:
                        return layoutelement.prop(bpy.context.scene.decals, prop)
                else:
                    return layoutelement.separator()
            elif existsdecalgroup and not existsinfogroup:
                # if bpy.data.groups["DM_atlas_decal"]["json"] and bpy.data.groups["DM_atlas_decal"]["uvs"]:
                if bpy.data.groups["DM_atlas_decal"]["json"]:
                    return layoutelement.prop(bpy.context.scene.decals, prop)
                else:
                    return layoutelement.separator()
            elif not existsdecalgroup and existsinfogroup:
                # if bpy.data.groups["export_atlas_info"]["json"] and bpy.data.groups["export_atlas_info"]["uvs"]:
                if bpy.data.groups["export_atlas_info"]["json"]:
                    return layoutelement.prop(bpy.context.scene.decals, prop)
                else:
                    return layoutelement.separator()
            else:
                return layoutelement.separator()
        elif op and text:
            if existsdecalgroup and existsinfogroup:
                # if bpy.data.groups["DM_atlas_decal"]["json"] and bpy.data.groups["DM_atlas_info"]["json"] and bpy.data.groups["DM_atlas_decal"]["uvs"] and bpy.data.groups["DM_atlas_info"]["uvs"]:
                if bpy.data.groups["DM_atlas_decal"]["json"] and bpy.data.groups["DM_atlas_info"]["json"]:
                        layoutelement.operator(op, text=text)
                else:
                    layoutelement.separator()
            elif existsdecalgroup and not existsinfogroup:
                # if bpy.data.groups["DM_atlas_decal"]["json"] and bpy.data.groups["DM_atlas_decal"]["uvs"]:
                if bpy.data.groups["DM_atlas_decal"]["json"]:
                        layoutelement.operator(op, text=text)
                else:
                    layoutelement.separator()
            elif not existsdecalgroup and existsinfogroup:
                # if bpy.data.groups["DM_atlas_info"]["json"] and bpy.data.groups["DM_atlas_info"]["uvs"]:
                if bpy.data.groups["DM_atlas_info"]["json"]:
                        layoutelement.operator(op, text=text)
                else:
                    layoutelement.separator()
            else:
                layoutelement.separator()
