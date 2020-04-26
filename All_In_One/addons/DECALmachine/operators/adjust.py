import bpy
from bpy.props import EnumProperty
import bmesh
from .. items import adjust_mode_items
from .. utils.decal import set_props_and_node_names_of_library_decal, set_decalobj_props_from_material, set_decalobj_name, set_defaults, change_panel_width
from .. utils.modifier import get_displace, get_nrmtransfer
from .. utils.raycast import get_origin_from_face, find_nearest
from .. utils.material import get_parallaxgroup_from_decalmat, get_decalmat, get_decalgroup_from_decalmat, get_decal_texture_nodes, get_panel_material, auto_match_material
from .. utils.math import get_loc_matrix, get_rot_matrix, get_sca_matrix
from .. utils.ui import draw_init, draw_title, draw_prop, wrap_mouse
from mathutils import Matrix, Vector
from math import radians


class Adjust(bpy.types.Operator):
    bl_idname = "machin3.adjust_decal"
    bl_label = "MACHIN3: Adjust Decal"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Adjust Decal Height, Parallax and Various Other Properties"

    mode: EnumProperty(name="Mode", items=adjust_mode_items, default="HEIGHT")

    @classmethod
    def poll(cls, context):
        return any(obj.DM.isdecal for obj in context.selected_objects)

    def draw_HUD(self, args):
        _, context, event = args

        draw_init(self)
        draw_title(self, "Adjust Decals" if len(self.decals) > 1 else "Adjust Decal")

        draw_prop(self, "Mode", self.mode, offset=0, hint="switch Q, W, E, A, S", hint_offset=280)

        if self.mode == "HEIGHT":
            draw_prop(self, "Δ Height", self.delta_x, decimal=5 if event.shift else 3 if event.ctrl else 4, offset=18, hint="move LEFT/RIGHT, X to set %0.4f" % (context.scene.DM.height), hint_offset=280)

        elif self.mode == "WIDTH":
            draw_prop(self, "Δ Width", self.delta_x + 1, decimal=4 if event.shift else 2 if event.ctrl else 3, offset=18, hint="move LEFT/RIGHT, X to set 1", hint_offset=280)

        elif self.mode == "PARALLAX":
            draw_prop(self, "Δ Amount", self.delta_x, decimal=3 if event.shift else 1 if event.ctrl else 2, offset=18, hint="move LEFT/RIGHT, X to set 0.1", hint_offset=280)

        elif self.mode == "AO":
            draw_prop(self, "Δ AO Strength", self.delta_x, decimal=3 if event.shift else 1 if event.ctrl else 2, offset=18, hint="move LEFT/RIGHT, X to set 1", hint_offset=280)

        elif self.mode == "STRETCH":
            draw_prop(self, "Panel UV Stretch", self.delta_x + 1, decimal=3 if event.shift else 1 if event.ctrl else 2, offset=18, hint="move LEFT/RIGHT, X to set 1", hint_offset=280)

        if self.panel_decals:
            self.offset += 18
            draw_prop(self, "Panel", self.panel_decals[0].active_material.DM.decalname, offset=18, hint="CTRL scroll UP/DOWN", hint_offset=280)


        self.offset += 18
        draw_prop(self, "Rotate", self.rotate, offset=18, hint="scroll UP/DOWN, SHIFT: 5°, SHIFT + CTRL: 1°", hint_offset=280)
        draw_prop(self, "Rotate UVs", self.uvrotate, offset=18, hint="ALT scroll UP/DOWN", hint_offset=280)
        draw_prop(self, "Mirror U", self.umirror, offset=18, hint="toggle U", hint_offset=280)
        draw_prop(self, "Mirror V", self.vmirror, offset=18, hint="toggle V", hint_offset=280)

        self.offset += 18
        draw_prop(self, "Glossy Rays", "", offset=18, hint="toggle G", hint_offset=280)
        if any(mat[4] for mat in self.decaltypemats):
            draw_prop(self, "Mute Parallax", "", offset=18, hint="toggle P", hint_offset=280)

        self.offset += 18
        if any(mat[2] is not None for mat in self.decalmats):
            draw_prop(self, "Invert Info Decals", "", offset=18, hint="toggle I", hint_offset=280)
        draw_prop(self, "Custom Normals", "", offset=18, hint="toggle N", hint_offset=280)
        if any(mat[7] for mat in self.decaltypemats):
            draw_prop(self, "Closest/Linear Interpolation", "", offset=18, hint="toggle C", hint_offset=280)
        draw_prop(self, "Alpha Blend/Hashed", "", offset=18, hint="toggle B", hint_offset=280)

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y


        events = ['MOUSEMOVE', 'WHEELUPMOUSE', 'ONE', 'WHEELDOWNMOUSE', 'TWO', 'X', 'Q', 'W', 'E', 'A', 'S', 'C', 'I', 'N', 'G', 'P', 'U', 'V', "B"]

        if event.type in events:

            # CONTROL displace height and parallax

            if event.type == 'MOUSEMOVE':
                wrap_mouse(self, context, event, x=True)

                offset_x = self.mouse_x - self.last_mouse_x

                if self.mode == "HEIGHT":
                    divisor = 100000 if event.shift else 1000 if event.ctrl else 10000

                    offset_height = offset_x / divisor
                    self.delta_x += offset_height

                    for obj, displace, init_mid_level, _, _, glossy in self.decals:
                        if init_mid_level is not None:
                            displace.mid_level -= offset_height


                elif self.mode == "WIDTH":
                    divisor = 10000 if event.shift else 100 if event.ctrl else 1000

                    offset_width = offset_x / divisor
                    self.delta_x += offset_width

                    self.adjust_panel_width(context.scene)


                elif self.mode == "PARALLAX":
                    divisor = 10000 if event.shift else 100 if event.ctrl else 1000

                    offset_parallax = offset_x / divisor
                    self.delta_x += offset_parallax

                    for mat, _, _, _, pg, _, init_parallax, _, _, _, _ in self.decaltypemats:
                        if init_parallax is not None:
                            amount = pg.inputs["Amount"].default_value
                            newamount = amount + offset_parallax

                            if 0 <= newamount <= 0.5:
                                pg.inputs["Amount"].default_value = newamount
                                pg.mute = False


                elif self.mode == "AO":
                    divisor = 10000 if event.shift else 100 if event.ctrl else 1000

                    offset_ao = offset_x / divisor
                    self.delta_x += offset_ao

                    for mat, _, _, init_ao, _, _, _, _, _, _, _ in self.decaltypemats:
                        if init_ao is not None:
                            i = get_decalgroup_from_decalmat(mat).inputs["AO Strength"]
                            ao = i.default_value
                            newamount = ao + offset_ao

                            if 0 <= newamount <= 1:
                                i.default_value = newamount

                elif self.mode == "STRETCH":
                    divisor = 10000 if event.shift else 100 if event.ctrl else 1000

                    offset_stretch = offset_x / divisor
                    self.delta_x += offset_stretch

                    self.adjust_panel_uv_stretch()

            # CONTROL mode

            elif event.type == 'Q' and event.value == "PRESS":
                self.mode = "HEIGHT"

            elif event.type == 'W' and event.value == "PRESS":
                self.mode = "WIDTH"

            elif event.type == 'E' and event.value == "PRESS":
                self.mode = "PARALLAX"

            elif event.type == 'A' and event.value == "PRESS":
                self.mode = "AO"

            elif event.type == 'S' and event.value == "PRESS":
                self.mode = "STRETCH"


            # RETURN to defaults

            elif event.type == 'X' and event.value == "PRESS":
                if self.mode == "HEIGHT":
                    for obj, displace, init_mid_level, _, _, _ in self.decals:
                        if init_mid_level:
                            get_displace(obj).mid_level = context.scene.DM.height

                elif self.mode == "WIDTH":
                    for obj, initbm in self.init_bms:
                        initbm.to_mesh(obj.data)


                elif self.mode == "PARALLAX":
                    for mat, _, _, _, pg, _, init_parallax, _, _, _, _ in self.decaltypemats:
                        if init_parallax is not None:
                            pg.inputs["Amount"].default_value = 0.1

                elif self.mode == "AO":
                    for mat, _, dg, init_ao, _, _, _, _, _, _, _ in self.decaltypemats:
                        if init_ao is not None:
                            dg.inputs["AO Strength"].default_value = 1

                elif self.mode == "STRETCH":
                    for obj, initbm in self.init_bms:
                        initbm.to_mesh(obj.data)

                self.delta_x = 0


            # TOGGLE linear/clostest normal map interpolation

            elif event.type == 'C' and event.value == "PRESS":
                for mat, _, _, _, _, _, _, nrmnode, init_nrminterp, colornode, init_colorinterp in self.decaltypemats:
                    if nrmnode:
                        nrmnode.interpolation = "Linear" if nrmnode.interpolation == "Closest" else "Closest"

                    if colornode:
                        colornode.interpolation = "Linear" if colornode.interpolation == "Closest" else "Closest"

            # TOGGLE invert

            elif event.type == 'I' and event.value == "PRESS":
                for mat, dg, init_invert in self.decalmats:
                    if init_invert is not None:
                        dg.inputs["Invert"].default_value = 1 - dg.inputs["Invert"].default_value


            # TOGGLE custom normals

            elif event.type == 'N' and event.value == "PRESS":
                for obj, _, _, nrmtransfer, init_shownrms, _ in self.decals:
                    if init_shownrms is not None:
                        nrmtransfer.show_render = not nrmtransfer.show_render
                        nrmtransfer.show_viewport = nrmtransfer.show_render

            # TOGGLE glossy

            elif event.type == 'G' and event.value == "PRESS":
                for obj, _, _, _, _, _ in self.decals:
                    obj.cycles_visibility.glossy = not obj.cycles_visibility.glossy
                    obj.data.update()

            # TOGGLE parallax muting

            elif event.type == 'P' and event.value == "PRESS":
                for mat, _, _, _, pg, _, _, _, _, _, _ in self.decaltypemats:
                    if pg:
                        pg.mute = not pg.mute

            # TOGGLE blend method

            elif event.type == 'B' and event.value == "PRESS":
                for mat, _, _, _, pg, _, _, _, _, _, _ in self.decaltypemats:
                    mat.blend_method = "HASHED" if mat.blend_method == "BLEND" else "BLEND"


            # MIRROR Decal UVs
            elif event.type == 'U' and event.value == "PRESS":
                self.mirror_uvs(u=True)

            elif event.type == 'V' and event.value == "PRESS":
                self.mirror_uvs(v=True)


            # ROTATE Decals and Decal UVs

            elif event.type in {'WHEELUPMOUSE', 'ONE'} and event.value == 'PRESS':

                # panel decal material change
                if event.ctrl and not event.alt and not event.shift:
                    self.change_panel_decal(context, 1)

                # uv rotation
                elif event.alt:
                    self.rotate_uvs("CCW")

                # decal rotation
                else:
                    if event.shift and event.ctrl:
                        self.rotate += 1
                        rmx = Matrix.Rotation(radians(1), 4, "Z")
                    elif event.shift:
                        self.rotate += 5
                        rmx = Matrix.Rotation(radians(5), 4, "Z")
                    else:
                        self.rotate += 45
                        rmx = Matrix.Rotation(radians(45), 4, "Z")

                    for obj, _, _, _, _, _ in self.decals:
                        if not obj.DM.issliced and not obj.DM.isprojected:
                            loc, rot, sca = obj.matrix_basis.decompose()
                            obj.matrix_basis = get_loc_matrix(loc) @ get_rot_matrix(rot) @ rmx @ get_sca_matrix(sca)



            elif event.type in {'WHEELDOWNMOUSE', 'TWO'} and event.value == 'PRESS':

                # panel decal material change
                if event.ctrl and not event.alt and not event.shift:
                        self.change_panel_decal(context, -1)

                # uv rotation
                elif event.alt:
                    self.rotate_uvs("CW")

                # decal rotation
                else:
                    if event.shift and event.ctrl:
                        self.rotate -= 1
                        rmx = Matrix.Rotation(radians(-1), 4, "Z")
                    elif event.shift:
                        self.rotate -= 5
                        rmx = Matrix.Rotation(radians(-5), 4, "Z")
                    else:
                        self.rotate -= 45
                        rmx = Matrix.Rotation(radians(-45), 4, "Z")

                    for obj, _, _, _, _, _ in self.decals:
                        if not obj.DM.issliced and not obj.DM.isprojected:
                            loc, rot, sca = obj.matrix_basis.decompose()
                            obj.matrix_basis = get_loc_matrix(loc) @ get_rot_matrix(rot) @ rmx @ get_sca_matrix(sca)

        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in {'LEFTMOUSE', 'SPACE'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            return {'CANCELLED'}

        self.last_mouse_x = self.mouse_x
        self.last_mouse_y = self.mouse_y

        return {"RUNNING_MODAL"}

    def cancel_modal(self, removeHUD=True):
        if removeHUD:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

        # reset the mid levels to their initial state
        for obj, displace, init_mid_level, nrmtransfer, init_shownrms, init_glossy in self.decals:
            if init_mid_level:
                displace.mid_level = init_mid_level

            if init_shownrms:
                nrmtransfer.show_render = init_shownrms
                nrmtransfer.show_viewport = init_shownrms

            obj.cycles_visibility.glossy = init_glossy


        # reset material changes
        for mat, dg, init_invert in self.decalmats:
            if init_invert:
                dg.inputs["Invert"].default_value = init_invert

        for mat, init_blend, dg, init_ao, pg, init_pmute, init_parallax, nrmnode, init_nrminterp, colornode, init_colorinterp in self.decaltypemats:
            mat.blend_method = init_blend

            if init_ao:
                dg.inputs["AO Strength"].default_value = init_ao

            if init_pmute is not None:
                pg.mute = init_pmute

            if init_parallax:
                pg.inputs["Amount"].default_value = init_parallax

            if nrmnode:
                nrmnode.interpolation = init_nrminterp

            if colornode:
                colornode.interpolation = init_colorinterp

        # reset mesh/uv changes
        for obj, initbm in self.init_bms:
            initbm.to_mesh(obj.data)
            initbm.clear()

    def invoke(self, context, event):
        # get all decals in the selection
        decals = [obj for obj in context.selected_objects if obj.DM.isdecal]

        # get all decalmats in the selection
        decalmats = {obj.active_material for obj in decals if obj.active_material is not None}

        # get unqiue material uuids in among the selected
        decalmatuuids = {get_decalmat(obj).DM.uuid for obj in decals if get_decalmat(obj)}

        # collect all materials with those uuids
        decaltypemats = {mat for mat in bpy.data.materials if mat.DM.uuid in decalmatuuids}

        # create decals list, that stores the selected decals and their mid_level values
        self.decals = []

        for obj in decals:
            displace = get_displace(obj)
            midvalue = displace.mid_level if displace else None

            nrmtransfer = get_nrmtransfer(obj)
            shownrms = nrmtransfer.show_viewport if nrmtransfer else None

            glossy = obj.cycles_visibility.glossy

            self.decals.append((obj, displace, midvalue, nrmtransfer, shownrms, glossy))

        # create decal materials list, that stores materials and various initial values
        self.decalmats = []

        for mat in decalmats:
            decalgroup = get_decalgroup_from_decalmat(mat)
            invert = decalgroup.inputs["Invert"].default_value if mat.DM.decaltype == "INFO" else None

            self.decalmats.append((mat, decalgroup, invert))


        # create decal type  materials list, that stores materials and various initial values
        self.decaltypemats = []

        for mat in decaltypemats:
            blendmethod = mat.blend_method

            decalgroup = get_decalgroup_from_decalmat(mat)
            ao = decalgroup.inputs["AO Strength"].default_value if mat.DM.decaltype != "INFO" else None

            parallaxgroup = get_parallaxgroup_from_decalmat(mat) if mat.DM.decaltype in ["SIMPLE", "SUBSET"] else None
            parallaxmute = parallaxgroup.mute if parallaxgroup else None
            parallax = parallaxgroup.inputs["Amount"].default_value if parallaxgroup else None

            nrmnode = get_decal_texture_nodes(mat)["NRM_ALPHA"] if mat.DM.decaltype != "INFO" else None
            nrminterpolation = nrmnode.interpolation if nrmnode else None

            colornode = get_decal_texture_nodes(mat)["COLOR_ALPHA"] if mat.DM.decaltype == "INFO" else None
            colorinterpolation = colornode.interpolation if colornode else None

            self.decaltypemats.append((mat, blendmethod, decalgroup, ao, parallaxgroup, parallaxmute, parallax, nrmnode, nrminterpolation, colornode, colorinterpolation))

        # save this initial mesh states, this will be used when canceling the modal and to reset it for each mousemove event
        self.init_bms = []

        for obj in decals:
            initbm = bmesh.new()
            initbm.from_mesh(obj.data)
            initbm.normal_update()
            initbm.verts.ensure_lookup_table()

            self.init_bms.append((obj, initbm))

        # get panel decals
        self.panel_decals = [obj for obj in decals if obj.DM.decaltype == "PANEL" and obj.active_material]


        # initialize
        self.mode = "HEIGHT"
        self.rotate = 0
        self.uvrotate = 0
        self.umirror = False
        self.vmirror = False

        # mouse positions
        self.mouse_x = self.last_mouse_x = event.mouse_region_x
        self.mouse_y = self.last_mouse_y = event.mouse_region_y
        self.delta_x = 0
        self.delta_y = 0

        args = (self, context, event)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def rotate_uvs(self, direction):
        self.uvrotate += 90 if direction == "CW" else -90

        rmx = Matrix.Rotation(radians(self.uvrotate), 2, "Z")

        for obj, initbm in self.init_bms:
            bm = initbm.copy()
            bm.verts.ensure_lookup_table()

            uvs = bm.loops.layers.uv.active

            # determine potential offset based on rotation angle
            fraction = self.uvrotate / 360 % 1
            offset = Vector((1, 0)) if fraction == 0.25 else Vector((1, 1)) if fraction == 0.5 else Vector((0, 1)) if fraction == 0.75 else None

            for face in bm.faces:
                for loop in face.loops:
                    loop[uvs].uv = rmx @ loop[uvs].uv

                    if offset:
                        loop[uvs].uv += offset

            bm.to_mesh(obj.data)
            bm.clear()

    def mirror_uvs(self, u=False, v=False):
        if u:
            self.umirror = not self.umirror
        elif v:
            self.vmirror = not self.vmirror

        us = []
        vs = []
        mir_us = []
        mir_vs = []

        for obj, initbm in self.init_bms:
            bm = initbm.copy()
            bm.verts.ensure_lookup_table()

            if any([self.umirror, self.vmirror]):
                uvs = bm.loops.layers.uv.active

                for face in bm.faces:
                    for loop in face.loops:
                        # original uvs
                        uv = loop[uvs].uv

                        us.append(uv[0])
                        vs.append(uv[1])

                        if self.umirror:
                            loop[uvs].uv = uv.reflect(Vector((1, 0)))

                        if self.vmirror:
                            loop[uvs].uv = uv.reflect(Vector((0, 1)))

                        # mirrord uvs
                        uv = loop[uvs].uv

                        mir_us.append(uv[0])
                        mir_vs.append(uv[1])


                # do an offset, to put the mirrored uvs into the same location as the original uvs
                for face in bm.faces:
                    for loop in face.loops:
                        loop[uvs].uv += Vector((min(us) - min(mir_us), min(vs) - min(mir_vs)))

            bm.to_mesh(obj.data)
            bm.clear()

    def adjust_panel_uv_stretch(self):
        smx = Matrix.Scale(1 + self.delta_x, 2, (1, 0)).inverted()

        for obj, initbm in self.init_bms:
            if obj.DM.issliced:
                pass

                bm = initbm.copy()
                bm.verts.ensure_lookup_table()

                uvs = bm.loops.layers.uv.active

                for face in bm.faces:
                    for loop in face.loops:
                        loop[uvs].uv = smx @ loop[uvs].uv


                bm.to_mesh(obj.data)
                bm.clear()

    def adjust_panel_width(self, scene):
        for obj, initbm in self.init_bms:
            if obj.DM.issliced:
                bm = initbm.copy()
                bm.verts.ensure_lookup_table()

                # if only one panel is selected, set the panelwidth scene prop as well
                change_panel_width(bm, 1 + self.delta_x, obj, scene, len(self.panel_decals) == 1)

                bm.to_mesh(obj.data)
                bm.clear()

    def change_panel_decal(self, context, direction):
        dm = context.scene.DM

        # get the first panel obj's position in the paneldecals tuple list
        availablepanels = bpy.types.WindowManager.paneldecals[1]['items']

        if self.panel_decals:
            currentuuid = self.panel_decals[0].DM.uuid

            currentidx = None
            for idx, panel in enumerate(availablepanels):
                if panel[0] == currentuuid:
                    currentidx = idx
                    break

            # find either the next or previous panel decal
            if currentidx is not None:
                newidx = currentidx - direction

                if newidx < 0:
                    newidx = len(availablepanels) - 1
                elif newidx == len(availablepanels):
                    newidx = 0

                newpanel = availablepanels[newidx]

                # check if an unmatched  material of this type is already in the blend file
                mat = None

                uuid = newpanel[0]
                name = newpanel[1]
                library = newpanel[2]

                mat, appended, _, _ = get_panel_material(uuid)

                if mat:
                    if appended:
                        # set node names and props of the panel material and textures (not the panel objs, they are done in the next step)
                        set_props_and_node_names_of_library_decal(library, name, decalobj=None, decalmat=mat)

                        # set material defaults
                        set_defaults(decalmat=mat)

                    for panel in self.panel_decals:

                        # set panel obj props, based on the exsiting material in the blend file
                        set_decalobj_props_from_material(panel, mat)

                        # apply the material
                        panel.active_material = mat

                        # and set the panel obj name
                        set_decalobj_name(panel, decalname=mat.DM.decalname, uuid=uuid)

                        # auto match the material

                        if mat.DM.decaltype != 'INFO':
                            automatch = dm.auto_match

                            if automatch == "AUTO":
                                # auto match material, by taking the first face of the panel strip as the origin
                                origin, direction = get_origin_from_face(panel)

                                # get the target for the panel
                                targets = [panel.DM.slicedon] if panel.DM.slicedon else [panel.parent] if panel.parent else [obj for obj in context.visisble_objects if obj.type == "MESH" and not obj.DM.isdecal]

                                # then find the nearest polygon on the target and match its material
                                obj, _, _, index, _ = find_nearest(targets, origin)

                                if obj and index is not None:
                                    auto_match_material(panel, panel.active_material, matchobj=obj, face_idx=index)

                            elif automatch == "MATERIAL":
                                auto_match_material(panel, panel.active_material, matchmatname=context.window_manager.matchmaterial)


                    # finally, set the new "current decal" in the paneldecalenum, used by the slice tool
                    context.window_manager.paneldecals = uuid
