import bpy
from .. import M3utils as m3
from .. utils.operators import unlink_render_result


class ChangePanelWidth(bpy.types.Operator):
    bl_idname = "machin3.change_panel_width"
    bl_label = "MACHIN3: Change Panel Width"

    def execute(self, context):
        panel_width()

        return {'FINISHED'}


class PanelFlip(bpy.types.Operator):
    bl_idname = "machin3.decal_panel_flip"
    bl_label = "MACHIN3: Decal Panel Flip"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        panel_flip()

        return {'FINISHED'}


class WireframeDisplayAll(bpy.types.Operator):
    bl_idname = "machin3.wireframe_display_all"
    bl_label = "MACHIN3: Wireframe Display All"

    def execute(self, context):
        wireframe_display("all")

        return {'FINISHED'}


class WireframeDisplayNone(bpy.types.Operator):
    bl_idname = "machin3.wireframe_display_none"
    bl_label = "MACHIN3: Wireframe Display None"

    def execute(self, context):
        wireframe_display("none")

        return {'FINISHED'}


class WireframeDisplayDecals(bpy.types.Operator):
    bl_idname = "machin3.wireframe_display_decals"
    bl_label = "MACHIN3: Wireframe Display Decals"

    def execute(self, context):
        wireframe_display("decals")

        return {'FINISHED'}


class ToggleParallax(bpy.types.Operator):
    bl_idname = "machin3.toggle_parallax"
    bl_label = "MACHIN3: Toggle Parallax"

    def execute(self, context):
        self.toggle_parallax()

        return {'FINISHED'}

    def toggle_parallax(self):
        selection = m3.selected_objects()

        if len(selection) == 0:
            # global switching parallax on or off based on the current scene property
            globalparallax = bpy.context.scene.decals.globalparallax

            for obj in bpy.data.objects:
                if "decal" in obj.name:
                    if "panel" not in obj.name and "material" not in obj.name:
                        # print(obj.name)
                        for node in obj.material_slots[0].material.node_tree.nodes:
                            if "Group" in node.name:
                                groupname = node.node_tree.name
                                if "parallax" in groupname:
                                    if globalparallax is True:
                                        node.mute = True
                                        if bpy.context.scene.decals.debugmode is True:
                                            print(" > Muted '%s's '%s'." % (obj.name, groupname))
                                    else:
                                        node.mute = False
                                        if bpy.context.scene.decals.debugmode is True:
                                            print(" > Unmuted '%s's '%s'." % (obj.name, groupname))

            if globalparallax is True:
                # self.report({'ERROR'}, "Turned parallax OFF globally!")
                print("Turned parallax OFF globally!")
                bpy.context.scene.decals.globalparallax = False
            else:
                # self.report({'ERROR'}, "Turned parallax ON globally!")
                print("Turned parallax ON globally!")
                bpy.context.scene.decals.globalparallax = True

        if len(selection) > 0:
            # toggling parallax for selection
            for obj in selection:
                if "decal" in obj.name:
                    if "panel" not in obj.name and "material" not in obj.name:
                        # print(obj.name)
                        for node in obj.material_slots[0].material.node_tree.nodes:
                            if "Group" in node.name:
                                groupname = node.node_tree.name
                                if "parallax" in groupname:
                                    if node.mute is True:
                                        node.mute = False
                                        print(" > Turned parallax on for '%s'." % (obj.name))
                                    else:
                                        node.mute = True
                                        print(" > Turned parallax off for '%s'." % (obj.name))


class ToggleGlossy(bpy.types.Operator):
    bl_idname = "machin3.toggle_glossy"
    bl_label = "MACHIN3: Toggle Glossy"

    def execute(self, context):
        self.toggle_glossy()

        return {'FINISHED'}

    def toggle_glossy(self):
        selection = m3.selected_objects()

        if len(selection) == 0:
            # global switching of cycles glossy rays on or off based on the current scene property
            globalglossy = bpy.context.scene.decals.globalglossy

            for obj in bpy.data.objects:
                if "decal" in obj.name or "info" in obj.name:
                    # print(obj.name)
                    if globalglossy is True:
                        obj.cycles_visibility.glossy = False
                        if bpy.context.scene.decals.debugmode is True:
                            print(" > Turned OFF glossy rays for '%s'." % (obj.name))
                    else:
                        obj.cycles_visibility.glossy = True
                        if bpy.context.scene.decals.debugmode is True:
                            print(" > Turned ON glossy rays for '%s'." % (obj.name))

            if globalglossy is True:
                print("Turned Glossy Rays OFF globally for all Decals!")
                bpy.context.scene.decals.globalglossy = False
            else:
                print("Turned Glossy Rays ON globally for all Decals!")
                bpy.context.scene.decals.globalglossy = True

        if len(selection) > 0:
            # toggling parallax for selection
            for obj in selection:
                if "decal" in obj.name or "info" in obj.name:
                    # print(obj.name)
                    if obj.cycles_visibility.glossy is True:
                        obj.cycles_visibility.glossy = False
                        print(" > Turned OFF glossy rays for '%s'." % (obj.name))
                    else:
                        obj.cycles_visibility.glossy = True
                        print(" > Turned ON glossy rays for '%s'." % (obj.name))


class CleanoutOrphanBackups(bpy.types.Operator):
    bl_idname = "machin3.cleanout_orphan_backups"
    bl_label = "MACHIN3: Cleanout Orphan Backups"

    def execute(self, context):
        self.remove_orphan_backups()

        return {'FINISHED'}

    def remove_orphan_backups(self):
        backuplist = []
        for obj in bpy.data.objects:
            if obj.name.startswith("backup_"):
                backuplist.append((m3.get_timestamp(obj), obj))

        matches = []
        for timestamp, backup in backuplist:
            # print(str(timestamp) + " - " + backup.name)
            for obj in bpy.data.objects:
                if obj.name.startswith("backup_") is False:
                    if timestamp == m3.get_timestamp(obj):
                        # print(" > " + obj.name)
                        # print(" >> found matching timestamp")
                        matches.append(backup)

        orphans = []
        for _, backup in backuplist:
            if backup not in matches:
                orphans.append(backup)

        if len(orphans) > 0:
            m3.unselect_all("OBJECT")
            for orphan in orphans:
                orphan.use_fake_user = False
                bpy.context.scene.objects.link(orphan)
                orphan.select = True
                if bpy.context.scene.decals.debugmode:
                    print("Removing '%s'." % (orphan.name))

            # print("Found %d orphan backups." % (len(orphans)))
            self.report({'ERROR'}, "Found and removed %d orphan backups." % (len(orphans)))
            bpy.ops.object.delete(use_global=False)
        else:
            self.report({'ERROR'}, "No orphan backups found.")


class FinishDecal(bpy.types.Operator):
    bl_idname = "machin3.finish_decal"
    bl_label = "MACHIN3: Finish Decal"

    def execute(self, context):
        # for img in bpy.data.images:
            # x = img.size[0]
            # y = img.size[1]
            # break

        # bpy.context.object.dimensions = (x / 1000, y / 1000, 0)
        # bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # bpy.ops.file.autopack_toggle()
        # bpy.ops.file.unpack_all(method='USE_ORIGINAL')

        # # also turn of shadow casting
        # active = bpy.context.active_object
        # active.cycles_visibility.shadow = False

        # # set edit mode viewport behavior
        # for mod in active.modifiers:
            # if "displace" in mod.name.lower():
                # mod.show_in_editmode = True
                # mod.show_on_cage = True

        # remove SubstancePBR nodes
        nodelist = ['Accurate Fresnel.001',
                    'CausticCalc.001',
                    'DispersedGlass.001',
                    'InvertNormal.001']

        for node in bpy.data.node_groups:
            if node.name == 'SubstancePBR':
                node.use_fake_user = False
                bpy.data.node_groups.remove(node, do_unlink=True)

        for node in bpy.data.node_groups:
            if node.name in nodelist:
                bpy.data.node_groups.remove(node, do_unlink=True)

        # # # save the file
        # bpy.ops.wm.save_mainfile()

        # # open file dialog
        # bpy.ops.wm.open_mainfile('INVOKE_DEFAULT')

        return {'FINISHED'}


def panel_flip():
    mode = m3.get_mode()

    if mode == "OBJECT":
        m3.set_mode("EDIT")

    m3.set_mode("FACE")
    bpy.ops.mesh.reveal()
    m3.select_all("MESH")
    oldcontext = m3.change_context("IMAGE_EDITOR")

    # Check if it is a result image linked, if there is, then no geometry will show in the image editor and nothing can be scaled or rotated
    # so we need to unlink the render result
    unlink_render_result()

    bpy.ops.transform.mirror(constraint_axis=(False, True, False), constraint_orientation='GLOBAL', proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

    m3.change_context(oldcontext)
    m3.unselect_all("MESH")

    m3.set_mode(mode)


def panel_width():
    pivot = bpy.context.space_data.pivot_point

    mode = m3.get_mode()
    if mode == "OBJECT":
        m3.set_mode("EDIT")

    m3.set_mode("EDGE")
    bpy.ops.mesh.reveal()
    m3.select_all("MESH")
    bpy.ops.mesh.region_to_loop()
    bpy.ops.mesh.select_all(action='INVERT')

    # this makes sure the end edges on knifed panel strips are selected
    bpy.ops.mesh.loop_multi_select(ring=True)

    bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
    bpy.ops.transform.resize("INVOKE_DEFAULT")

    bpy.context.space_data.pivot_point = pivot

    """

    # the following crashes blender
    # seems like he's trying to execute this while you are still active with the resizeing
    if mode == "OBJECT":
        m3.set_mode("OBJECT")

    """


def wireframe_display(string):
    if string == "all":
        for obj in bpy.data.objects:
            if obj.type == "MESH" and not obj.name.startswith("backup_"):
                obj.show_wire = True
                obj.show_all_edges = True
    elif string == "none":
        for obj in bpy.data.objects:
            if obj.type == "MESH" and not obj.name.startswith("backup_"):
                obj.show_wire = False
    elif string == "decals":
        for obj in bpy.data.objects:
            if obj.type == "MESH" and not obj.name.startswith("backup_"):
                if "decal" in obj.name or "info" in obj.name or "paneling" in obj.name:
                    obj.show_wire = True
                    obj.show_all_edges = True
                else:
                    obj.show_wire = False
