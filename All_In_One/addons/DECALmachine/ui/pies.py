import bpy
import math
from .. utils.registration import get_prefs, get_addon
from .. utils.ui import get_icon
from .. utils.modifier import get_shrinkwrap, get_subd, get_displace


class PieDecalMachine(bpy.types.Menu):
    bl_idname = "MACHIN3_MT_decal_machine"
    bl_label = "DECALmachine"

    def draw(self, context):
        mode = context.mode
        decalmode = get_prefs().decalmode

        active = context.active_object
        sel = context.selected_objects

        scene = context.scene

        decallibsCOL = get_prefs().decallibsCOL
        decallibs = [lib.name for lib in decallibsCOL if lib.isvisible]
        lockedlibs = [lib.name for lib in decallibsCOL if lib.islocked]

        if mode == "OBJECT":
            layout = self.layout
            pie = layout.menu_pie()

            # 4 - LEFT
            self.draw_decal_libraries(pie, decalmode, decallibs, lockedlibs, side="LEFT")

            # 6 - RIGHT
            self.draw_decal_libraries(pie, decalmode, decallibs, lockedlibs, side="RIGHT")

            # 2 - BOTTOM
            self.draw_extra(pie, context, active, scene, sel)

            # 8 - TOP
            box = pie.split()
            column = box.column()

            self.draw_update_check(column)
            self.draw_tools(column, context, active, sel)


        elif mode == "EDIT_MESH":
            layout = self.layout
            pie = layout.menu_pie()

            # 4 - LEFT
            pie.separator()

            # 6 - RIGHT
            pie.separator()

            # 2 - BOTTOM
            pie.separator()

            # 8 - TOP
            pie.separator()

            # 7 - TOP - LEFT
            pie.separator()

            # 9 - TOP - RIGHT
            pie.separator()

            # 1 - BOTTOM - LEFT
            pie.separator()

            # 3 - BOTTOM - RIGHT
            pie.separator()

    def draw_update_check(self, layout):
        if get_prefs().update_available:
            layout.label(text="A new version is available", icon_value=get_icon("refresh_green"))

    def draw_tools(self, layout, context, active, sel):
        grouppro, _, _, _ = get_addon("Group Pro")

        decals = [obj for obj in sel if obj.DM.isdecal]

        # group pro disolve
        if grouppro and active and active.instance_collection and active.instance_collection.created_with_gp and not active.instance_collection.library:
            row = layout.row(align=True)
            row.operator("machin3.grouppro_dissolve", text="Group Pro Dissolve", icon='OUTLINER_OB_GROUP_INSTANCE').maxDept = 0

        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("machin3.get_backup_decal", text="(B) Get Backup", icon="AXIS_TOP")
        row.operator("machin3.match_material", text="(V) Match", icon="AXIS_TOP")

        row = layout.row(align=True)
        row.scale_y = 1.5
        r = row.row(align=True)
        r.operator("machin3.project_decal", text="(D) Project", icon="AXIS_TOP")

        if decals and any(get_shrinkwrap(obj) or get_subd(obj) for obj in decals):
            r.operator("machin3.unshrinkwrap_decal", text="", icon="NORMALS_FACE")

        if decals and all(obj.DM.decaltype == "PANEL" and obj.DM.issliced for obj in decals):
            row.operator("machin3.panel_decal_unwrap", text="Unwrap", icon="AXIS_TOP")

        elif active and active.type == "GPENCIL":
            row.operator("machin3.gpanel", text="GPanel", icon="AXIS_TOP")

        else:
            row.operator("machin3.slice_decal", text="Slice", icon="AXIS_TOP")

        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator("machin3.adjust_decal", text="Adjust", icon="AXIS_TOP")
        row.operator("machin3.reapply_decal", text="Re-Apply", icon="AXIS_TOP")

    def draw_decal_libraries(self, layout, decalmode, decallibs, lockedlibs, side):
        def draw_decal_library(layout, decalmode, library, lockedlibs):
            libraryscale = get_prefs().libraryscale
            decalsinlibraryscale = get_prefs().decalsinlibraryscale

            showdecalcount = get_prefs().showdecalcount
            showdecalnames = get_prefs().showdecalnames
            showdecalbuttonname = get_prefs().showdecalbuttonname

            wmt = bpy.types.WindowManager
            wm = bpy.context.window_manager

            # library label
            if showdecalcount:
                decalcount = len(getattr(wmt, "decallib_" + library)[1]['items'])
                liblabel = "%s, %d" % (library, decalcount)
            else:
                liblabel = library

            layout.label(text=liblabel)


            # library preview
            row = layout.row()

            lib = "lockeddecallib" if decalmode == "REMOVE" and library in lockedlibs else "decallib_" + library
            row.template_icon_view(wm, lib, show_labels=showdecalnames, scale=libraryscale, scale_popup=decalsinlibraryscale)


            # insert/remove button
            decalname = getattr(wm, "decallib_" + library)


            # draw locked placeholder library
            if decalmode == "REMOVE" and library in lockedlibs:
                layout.label(text="LOCKED")

            # draw proper library content
            else:
                if decalmode == "INSERT":
                    text, icon = (decalname, 0) if showdecalbuttonname else ("", get_icon("plus"))
                    op = layout.operator("machin3.insert_decal", text=text, icon_value=icon)
                    op.force_cursor_align = False

                elif decalmode == "REMOVE":
                    text, icon = ("", get_icon("cancel"))
                    op = layout.operator("machin3.remove_decal", text=text, icon_value=icon)

                op.library = library
                op.decal = decalname
                op.instant = False

        libraryrows = get_prefs().libraryrows
        libraryoffset = get_prefs().libraryoffset
        decallibscount = len(decallibs)


        # determine what libs go on which side
        if side == "LEFT":
            count = math.ceil(decallibscount / 2)
            side_libs = decallibs[0:count + libraryoffset]

        elif side == "RIGHT":
            count = math.floor(decallibscount / 2)
            side_libs = decallibs[count + libraryoffset + decallibscount % 2:]


        # create list of lists, based on the libraryrows prop
        libs = [side_libs[i * libraryrows:i * libraryrows + libraryrows] for i in range(math.ceil(len(side_libs) / libraryrows))]

        box = layout.split()

        # for library in side_libs:
        for libraries in libs:

            col = box.column()

            for library in libraries:
                draw_decal_library(col, decalmode, library, lockedlibs)

    def draw_extra(self, layout, context, active, scene, sel):
        def draw_decal_scale(layout, active, scene, sel):
            row = layout.row()

            r = row.row(align=True)
            r.prop(scene.DM, "globalscale")

            if round(scene.DM.globalscale, 3) != 1:
                r.operator("machin3.reset_decal_scale", text="", icon="LOOP_BACK").mode = 'SCALE'

            if active and len(sel) == 1 and active in sel and active.DM.isdecal and not active.DM.isprojected and not active.DM.issliced:
                uuid = active.DM.uuid
                scales = scene.DM.individualscales
                _, _, active_scale = active.matrix_world.decompose()

                if uuid in scales:
                    if [round(s, 6) for s in scales[uuid].scale] == [round(s, 6) for s in active_scale]:
                        icon = "RADIOBUT_ON"
                    else:
                        icon = "PROP_ON"
                else:
                    icon = "RADIOBUT_OFF"

                r = row.row(align=True)
                r.operator("machin3.store_individual_decal_scale", text="", icon=icon)
                if active.DM.uuid in scene.DM.individualscales:
                    r.operator("machin3.clear_individual_decal_scale", text="", icon_value=get_icon("cancel"))

        def draw_panel_width(layout, scene):
            row = layout.row(align=True)
            row.prop(scene.DM, "panelwidth")

            if round(scene.DM.panelwidth, 2) != 0.04:
                row.operator("machin3.reset_decal_scale", text="", icon="LOOP_BACK").mode = 'WIDTH'

        def draw_decal_height(layout, active, scene):
            row = layout.row(align=True)
            row.prop(scene.DM, "height")

            displace = get_displace(active) if active else False

            if active and active.DM.isdecal and displace and round(displace.mid_level, 4) != round(scene.DM.height, 4):
                    row.operator("machin3.set_decal_scale", text="", icon="SORT_ASC").mode = 'HEIGHT'

            if round(scene.DM.height, 4) != 0.9999:
                row.operator("machin3.reset_decal_scale", text="", icon="LOOP_BACK").mode = 'HEIGHT'

        def draw_decal_remove_mode(layout, active):
            removemode = get_prefs().decalremovemode
            icon = "cancel" if removemode else "cancel_grey"

            row = layout.split(factor=0.33)
            row.separator()
            row.prop(get_prefs(), "decalremovemode", text="", icon_value=get_icon(icon))
            row.separator()

        box = layout.split()
        column = box.column()

        draw_decal_scale(column, active, scene, sel)
        draw_panel_width(column, scene)
        draw_decal_height(column, active, scene)
        draw_decal_remove_mode(column, active)
