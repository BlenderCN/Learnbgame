import bpy
import os
import shutil
from .. utils.registration import get_prefs
from .. utils import MACHIN3 as m3


# TODO: do the prefs part based on a dictionary?

# TODO: deactivate shift y/z wire toggle


class Customize(bpy.types.Operator):
    bl_idname = "machin3.customize"
    bl_label = "MACHIN3: Customize"
    bl_description = "Customize various Blender preferences, settings and keymaps."
    bl_options = {'REGISTER'}


    def execute(self, context):
        scriptspath = bpy.utils.user_resource('SCRIPTS')
        datafilespath = bpy.utils.user_resource('DATAFILES')

        resourcespath = os.path.join(get_prefs().path, "resources")


        """ no longer needed, with the PRESS box select working perfectly

        # SET Select TOOL, in object and edit mode
        if context.area.type == "VIEW_3D":
            bpy.ops.wm.tool_set_by_name(name="Select")

            if context.active_object and context.active_object.type == "MESH":
                bpy.ops.object.editmode_toggle()
                bpy.ops.wm.tool_set_by_name(name="Select")
                bpy.ops.object.editmode_toggle()


        # context override https://blender.stackexchange.com/a/27182/33919
        else:
            overrides = [{'area': area} for screen in context.workspace.screens for area in screen.areas if area.type == "VIEW_3D"]
            for o in overrides:
                bpy.ops.wm.tool_set_by_name(o, name="Select")

                if context.active_object and context.active_object.type == "MESH":
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.wm.tool_set_by_name(o, name="Select")
                    bpy.ops.object.editmode_toggle()
        """


        # THEME
        if get_prefs().custom_theme:
            self.theme(scriptspath, resourcespath)


        # MATCAPS + DEFAULT SHADING
        if get_prefs().custom_matcaps:
            self.matcaps(context, resourcespath, datafilespath)

        # OVERLAYS
        if get_prefs().custom_overlays:
            self.overlays(context)

        # PREFERENCES
        self.preferences(context)


        # START UP
        # copy and load start up file, which includes workspaces

        return {'FINISHED'}

    def customize_keymap(self, context):
        def modify_keymaps(kc):

            # WINDOW
            km = kc.keymaps.get("Window")
            for kmi in km.keymap_items:
                if kmi.idname == "wm.open_mainfile":
                    kmi.active = False

                if kmi.idname == "wm.doc_view_manual_ui_context":
                    kmi.active = False

            for kmi in km.keymap_items:
                if kmi.idname == "wm.save_as_mainfile":
                    kmi.active = False


            # SCREEN

            km = kc.keymaps.get("Screen")
            for kmi in km.keymap_items:
                if kmi.idname == "ed.undo":
                    kmi.type = "F1"
                    kmi.ctrl = False

                if kmi.idname == "ed.redo":
                    kmi.type = "F2"
                    kmi.ctrl = False
                    kmi.shift = False

                if kmi.idname == "ed.undo_history":
                    kmi.type = "F1"
                    kmi.ctrl = False
                    kmi.alt = True

                if kmi.idname == "screen.redo_last":
                    kmi.type = "BUTTON4MOUSE"

                if kmi.idname == "screen.screen_full_area":
                    if kmi.properties.use_hide_panels:
                        kmi.shift = True
                        kmi.alt = False
                        kmi.ctrl = False

                    else:
                        kmi.active = False

            # FRAMES

            km = kc.keymaps.get("Frames")
            for kmi in km.keymap_items:
                if kmi.idname == "screen.animation_play":
                    kmi.active = False


            # OUTLINER

            km = kc.keymaps.get("Outliner")
            for kmi in km.keymap_items:
                if kmi.idname == "outliner.show_active":
                    if kmi.type == "PERIOD":
                        kmi.type = "F"


            # 3D VIEW

            km = kc.keymaps.get("3D View")
            for kmi in km.keymap_items:
                if kmi.idname == "view3d.view_selected":
                    if kmi.type == "NUMPAD_PERIOD" and not kmi.properties.use_all_regions:
                        kmi.type = "F"

                if kmi.idname == "view3d.cursor3d":
                    kmi.type = "RIGHTMOUSE"
                    kmi.alt = True
                    kmi.shift = False
                    kmi.properties.orientation = "GEOM"

                # NOTE: changing these from  CLICK to PRESS seems to introduce weird behavior where blender always selects the object in the back, not in the front
                # ####: this applies only to the new "just select" tool. for it seems that work properly, it needs to remain at CLICK - but it still acts as it PRESS was set, odd
                # ####: also the new box select tool, can now be set to PRESS and will still work just fine
                if kmi.idname == "view3d.select":
                    if kmi.value == "CLICK":
                        if not any([getattr(kmi.properties, name, False) for name in ["extend", "deselect", "toggle", "center", "enumerate", "object"]]):
                            kmi.value = "PRESS"

                        elif kmi.properties.toggle and not any([getattr(kmi.properties, name, False) for name in ["extend", "deselect", "center", "enumerate", "object"]]):
                            kmi.value = "PRESS"

                        elif kmi.properties.enumerate and not any([getattr(kmi.properties, name, False) for name in ["extend", "deselect", "toggle", "center", "object"]]):
                            kmi.value = "PRESS"

                        else:
                            kmi.active = False

                if kmi.idname == "transform.translate":
                    if kmi.map_type == "TWEAK":
                        kmi.active = False

                if kmi.idname == "view3d.view_axis":
                    if kmi.map_type == "TWEAK":
                        kmi.active = False

                if kmi.idname == "transform.tosphere":
                    kmi.properties.value = 1

                # if kmi.idname == "wm.context_toggle":  # gizmo toggle
                    # kmi.active = False


            # 3D VIEW TOOLS

            km = kc.keymaps.get("3D View Tool: Cursor")
            for kmi in km.keymap_items:
                if kmi.idname == "view3d.cursor3d":
                    kmi.active = False

                if kmi.idname == "transform.translate":
                    kmi.active = False


            # OBJECT MODE

            km = kc.keymaps.get("Object Mode")
            for kmi in km.keymap_items:
                if kmi.idname == "object.select_all":
                    if kmi.properties.action == "SELECT":
                        kmi.properties.action = "TOGGLE"

                    elif kmi.properties.action == "DESELECT":
                        kmi.active = False

                if kmi.idname == "object.delete":
                    if kmi.type == "X" and kmi.shift:
                        kmi.active = False


            # OBJECT NON-MODAL

            km = kc.keymaps.get("Object Non-modal")
            for kmi in km.keymap_items:
                if kmi.idname == "object.mode_set":
                    kmi.active = False

                if kmi.idname == "view3d.object_mode_pie_or_toggle":
                    kmi.active = False


            # IMAGE

            km = kc.keymaps.get("Image")
            for kmi in km.keymap_items:
                if kmi.idname == "object.mode_set":
                    kmi.active = False


            # MESH

            km = kc.keymaps.get("Mesh")
            for kmi in km.keymap_items:

                if kmi.idname == "wm.call_menu":
                    if kmi.properties.name == "VIEW3D_MT_edit_mesh_select_mode":
                        kmi.active = False

                if kmi.idname == "mesh.select_all":
                    if kmi.properties.action == "SELECT":
                        kmi.properties.action = "TOGGLE"

                    elif kmi.properties.action == "DESELECT":
                        kmi.active = False

                if kmi.idname == "mesh.edge_face_add" and kmi.type == "F":
                    kmi.active = False

                if kmi.idname == "mesh.select_mode" and kmi.type in ["ONE", "TWO", "THREE"]:
                    kmi.active = False

                if kmi.idname == "mesh.loop_select":
                    if not any([getattr(kmi.properties, name, False) for name in ["extend", "deselect", "toggle", "ring"]]):
                        kmi.value = "PRESS"
                        kmi.alt = True
                        kmi.properties.toggle = True

                    else:
                        kmi.active = False

                if kmi.idname == "mesh.edgering_select":
                    if kmi.properties.ring and not any([getattr(kmi.properties, name, False) for name in ["extend", "deselect", "toggle"]]):
                        kmi.value = "PRESS"
                        kmi.shift = False
                        kmi.properties.toggle = True

                    else:
                        kmi.active = False

                if kmi.idname == "mesh.shortest_path_pick":
                    kmi.value = "PRESS"

                if kmi.idname == "mesh.select_more":
                    kmi.type = "WHEELUPMOUSE"
                    kmi.shift = True
                    kmi.ctrl = False

                if kmi.idname == "mesh.select_less":
                    kmi.type = "WHEELDOWNMOUSE"
                    kmi.shift = True
                    kmi.ctrl = False

                if kmi.idname == "mesh.select_next_item":
                    kmi.type = "WHEELUPMOUSE"
                    kmi.shift = False

                if kmi.idname == "mesh.select_prev_item":
                    kmi.type = "WHEELDOWNMOUSE"
                    kmi.shift = False

                if kmi.idname == "mesh.select_linked":
                    kmi.type = "LEFTMOUSE"
                    kmi.value = "DOUBLE_CLICK"
                    kmi.ctrl = False
                    kmi.shift = True

                if kmi.idname == "mesh.select_linked_pick":
                    if kmi.properties.deselect:
                        kmi.type = "LEFTMOUSE"
                        kmi.value = "DOUBLE_CLICK"
                        kmi.alt = True

                    else:
                        kmi.active = False

                if kmi.idname == "object.subdivision_set":
                    kmi.active = False

                if kmi.idname == "mesh.merge":
                    kmi.alt = False


            # CURVE

            km = kc.keymaps.get("Curve")
            for kmi in km.keymap_items:
                if kmi.idname == "curve.select_all":
                    if kmi.properties.action == "SELECT":
                        kmi.properties.action = "TOGGLE"

                    elif kmi.properties.action == "DESELECT":
                        kmi.active = False


            # ARMATURE

            km = kc.keymaps.get("Armature")
            for kmi in km.keymap_items:
                if kmi.idname == "armature.select_all":
                    if kmi.properties.action == "SELECT":
                        kmi.properties.action = "TOGGLE"

                    elif kmi.properties.action == "DESELECT":
                        kmi.active = False


            # POSE

            km = kc.keymaps.get("Pose")
            for kmi in km.keymap_items:
                if kmi.idname == "pose.select_all":
                    if kmi.properties.action == "SELECT":
                        kmi.properties.action = "TOGGLE"

                    elif kmi.properties.action == "DESELECT":
                        kmi.active = False


            # UV EDITOR

            km = kc.keymaps.get("UV Editor")
            for kmi in km.keymap_items:
                if kmi.idname == "uv.select_all":
                    if kmi.properties.action == "SELECT":
                        kmi.properties.action = "TOGGLE"

                    elif kmi.properties.action == "DESELECT":
                        kmi.active = False

                if kmi.idname == "mesh.select_mode":
                    kmi.active = False

                if kmi.idname == "wm.context_set_enum":
                    kmi.active = False

                if kmi.idname == "uv.select":
                    kmi.value = "PRESS"

                if kmi.idname == "uv.select_loop":
                    kmi.value = "PRESS"

                if kmi.idname == "uv.select_more":
                    kmi.type = "WHEELUPMOUSE"
                    kmi.shift = True
                    kmi.ctrl = False

                if kmi.idname == "uv.select_less":
                    kmi.type = "WHEELDOWNMOUSE"
                    kmi.shift = True
                    kmi.ctrl = False

                if kmi.idname == "transform.translate":
                    if kmi.map_type == "TWEAK":
                        kmi.active = False

                if kmi.idname == "uv.cursor_set":
                    kmi.alt = True
                    kmi.shift = False


            # IMAGE EDITOR TOOL: UV, CURSOR

            km = kc.keymaps.get("Image Editor Tool: Uv, Cursor")
            for kmi in km.keymap_items:
                if kmi.idname == "transform.translate":
                    if kmi.map_type == "TWEAK":
                        kmi.active = False

                if kmi.idname == "uv.cursor_set":
                    kmi.active = False


        def add_keymaps(kc):
            # MESH
            km = kc.keymaps.get("Mesh")

            kmi = km.keymap_items.new("mesh.loop_multi_select", "LEFTMOUSE", "CLICK_DRAG", alt=True)
            kmi.properties.ring = False

            kmi = km.keymap_items.new("mesh.loop_multi_select", "LEFTMOUSE", "CLICK_DRAG", alt=True, ctrl=True)
            kmi.properties.ring = True

            kmi = km.keymap_items.new("mesh.subdivide", "TWO", "PRESS", alt=True)
            # kmi.properties.smoothness = 1

            kmi = km.keymap_items.new("mesh.bridge_edge_loops", "TWO", "PRESS", ctrl=True)

        kc = context.window_manager.keyconfigs.user

        modify_keymaps(kc)

        add_keymaps(kc)

        get_prefs().custom_keymaps = False

    def preferences(self, context):
        prefs = context.preferences

        if get_prefs().custom_preferences_interface:
            print("\n» Changing Preferences: Interface")

            v = prefs.view
            s = prefs.system

            v.show_splash = False
            v.show_tooltips = True
            v.show_tooltips_python = True
            v.show_developer_ui = True

            v.header_align = 'BOTTOM'
            s.use_region_overlap = True

            v.color_picker_type = "SQUARE_SV"

            v.use_text_antialiasing = True
            v.text_hinting = "NONE"

            v.pie_animation_timeout = 0

        if get_prefs().custom_preferences_viewport:
            print("\n» Changing Preferences: Viewport")

            v = prefs.view
            s = prefs.system

            v.mini_axis_type = 'MINIMAL'

            s.gpu_viewport_quality = 1
            s.multi_sample = "8"

        if get_prefs().custom_preferences_navigation:
            print("\n» Changing Preferences: Navigation")

            i = prefs.inputs

            i.invert_mouse_zoom = True
            i.use_zoom_to_mouse = True

        if get_prefs().custom_preferences_keymap:
            print("\n» Changing Preferences: Keymap")

            keyconfigpath = bpy.utils.preset_paths(subdir='keyconfig')

            if keyconfigpath:
                keymappath = os.path.join(keyconfigpath[0], "blender_27x.py")

                bpy.ops.preferences.keyconfig_activate(filepath=keymappath)

                kcprefs = context.window_manager.keyconfigs.active.preferences
                kcprefs.select_mouse = "LEFT"

                # """
                # for some weird reason doing this 2 times is required if you edit the keymaps afterwards, TODO: check if still true
                # otherwise middle mouse mappings for zoom, pan, rotate and dolly will be missing, perhaps some other things as well
                bpy.ops.preferences.keyconfig_activate(filepath=keymappath)

                kcprefs = context.window_manager.keyconfigs.active.preferences
                kcprefs.select_mouse = "LEFT"
                # """

            self.customize_keymap(context)

        if get_prefs().custom_preferences_system:
            print("\n» Changing Preferences: System")

            c = prefs.addons['cycles'].preferences
            s = prefs.system
            e = prefs.edit

            c.compute_device_type = "CUDA"

            # TODO: as of c59370bf643f, likely a bit earlier, the c.devices collection won't update until the user switches to the SYSTEM prefs panel manually, re-investigate later
            # ####: as a consequence, the integrated gpu won't be activated

            for d in c.devices:
                d.use = True

            e.undo_steps = 64

        if get_prefs().custom_preferences_save:
            print("\n» Changing Preferences: Save & Load")
            v = prefs.view
            f = prefs.filepaths

            f.use_file_compression = True
            f.use_load_ui = False

            v.use_save_prompt = False

            f.save_version = 3
            f.recent_files = 20

    def overlays(self, context):
        print("\n» Modifying Overlays")

        areas = [area for screen in context.workspace.screens for area in screen.areas if area.type == "VIEW_3D"]

        for area in areas:
            overlay = area.spaces[0].overlay
            shading = area.spaces[0].shading

            overlay.show_face_center = True
            overlay.wireframe_threshold = 1

            shading.show_backface_culling = True

            overlay.vertex_opacity = 1

    def matcaps(self, context, resourcespath, datafilespath):
        print("\n» Adding Matcaps")

        matcapsourcepath = os.path.join(resourcespath, "matcaps")
        matcaptargetpath = m3.makedir(os.path.join(datafilespath, "studiolights", "matcap"))
        matcaps = os.listdir(matcapsourcepath)

        for matcap in sorted(matcaps):
            shutil.copy(os.path.join(matcapsourcepath, matcap), matcaptargetpath)
            print("  %s -> %s" % (matcap, matcaptargetpath))


        context.preferences.studio_lights.refresh()

        if all([mc in matcaps for mc in ["matcap_base.exr", "matcap_shiny_red.exr"]]):
            get_prefs().switchmatcap1 = "matcap_base.exr"
            get_prefs().switchmatcap2 = "matcap_shiny_red.exr"


            print("\n» Setting up Viewport Shading")

            ws = context.workspace

            shading = False
            for screen in ws.screens:
                if not shading:
                    for area in screen.areas:
                        if area.type == "VIEW_3D":
                            shading = area.spaces[0].shading

            if shading:
                shading.type = "SOLID"
                shading.light = "MATCAP"
                shading.studio_light = "matcap_base.exr"
                shading.color_type = "SINGLE"
                shading.single_color = (0.2270, 0.2270, 0.2423)  # hex 838387

                shading.cavity_ridge_factor = 0
                shading.cavity_valley_factor = 2

    def theme(self, scriptspath, resourcespath):
        print("\n» Installing and Enabling M3 theme")

        themesourcepath = os.path.join(resourcespath, "theme", "m3.xml")
        themetargetpath = m3.makedir(os.path.join(scriptspath, "presets", "interface_theme"))

        filepath = shutil.copy(themesourcepath, themetargetpath)
        bpy.ops.script.execute_preset(filepath=filepath, menu_idname="USERPREF_MT_interface_theme_presets")


class RestoreKeymaps(bpy.types.Operator):
    bl_idname = "machin3.restore_keymaps"
    bl_label = "MACHIN3: Restore Keymaps"
    bl_options = {'REGISTER'}

    def execute(self, context):
        kc = context.window_manager.keyconfigs.user

        for km in kc.keymaps:
            if km.is_user_modified:
                km.restore_to_default()

        get_prefs().dirty_keymaps = False

        return {'FINISHED'}
