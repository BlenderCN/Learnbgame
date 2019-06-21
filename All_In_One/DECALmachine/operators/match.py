import bpy
from bpy.props import BoolProperty
from .. utils.material import set_match_material_enum, match_material, remove_decalmat
from .. utils.ui import draw_init, draw_title, draw_prop
from .. utils.property import step_list


class Match(bpy.types.Operator):
    bl_idname = "machin3.match_material"
    bl_label = "MACHIN3: Match Material"
    bl_description = "Matches Decal Materials, Material 2 or Subset elements to Principled Shader Materials."
    bl_options = {'REGISTER', 'UNDO'}

    matchmaterial: BoolProperty(name="Match Material", default=False)
    matchmaterial2: BoolProperty(name="Match Material 2", default=False)
    matchsubset: BoolProperty(name="Match Material", default=False)

    @classmethod
    def poll(cls, context):
        return [obj for obj in context.selected_objects if obj.DM.isdecal and obj.active_material.DM.isdecalmat and not obj.active_material.DM.decaltype == "INFO"]

    def draw_HUD(self, args):
        _, _, event = args

        draw_init(self)
        draw_title(self, "Match Materials")

        if self.hassub:
            draw_prop(self, "Subset", self.subset, active=self.matchsub, hint="toggle S, scroll UP/DOWN", hint_offset=280)

        if self.hasmat:
            draw_prop(self, "Material", self.material, offset=18, active=self.matchmat, hint="toggle D, SHIFT scroll UP/DOWN", hint_offset=280)

        if self.hasmat2:
            draw_prop(self, "Material 2", self.material2, offset=18, active=self.matchmat2, hint="toggle F, CTRL scroll UP/DOWN", hint_offset=280)

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['WHEELUPMOUSE', 'ONE', 'WHEELDOWNMOUSE', 'TWO', 'S', 'D', 'F']

        if event.type in events:

            # STEP through matchable materials

            match = False

            if len(self.mats) > 1:
                if event.type in {'WHEELUPMOUSE', 'ONE'} and event.value == 'PRESS':
                    if event.shift and self.matchmat:
                        self.material = step_list(self.material, self.mats, 1, loop=True)
                        match = True
                    elif event.ctrl and self.matchmat2:
                        self.material2 = step_list(self.material2, self.mats, 1, loop=True)
                        match = True
                    elif not event.shift and not event.ctrl and self.matchsub:
                        self.subset = step_list(self.subset, self.mats, 1, loop=True)
                        match = True


                elif event.type in {'WHEELDOWNMOUSE', 'TWO'} and event.value == 'PRESS':
                    if event.shift and self.matchmat:
                        self.material = step_list(self.material, self.mats, -1, loop=True)
                        match = True
                    elif event.ctrl and self.matchmat2:
                        self.material2 = step_list(self.material2, self.mats, -1, loop=True)
                        match = True
                    elif not event.shift and not event.ctrl and self.matchsub:
                        self.subset = step_list(self.subset, self.mats, -1, loop=True)
                        match = True


            # TOGGLE match materials

            if event.type == 'S' and event.value == "PRESS" and self.hassub:
                self.matchsub = not self.matchsub
                match = True

            elif event.type == 'D' and event.value == "PRESS" and self.hasmat:
                self.matchmat = not self.matchmat
                match = True

            elif event.type == 'F' and event.value == "PRESS" and self.hasmat2:
                self.matchmat2 = not self.matchmat2
                match = True


            # MATCH MATERIALS
            if match:
                if any([self.matchsub, self.matchmat, self.matchmat2]):
                    for obj, init_mat in self.decals:
                        matchmatname = self.material if self.matchmat else None
                        matchmat2name = self.material2 if self.matchmat2 and init_mat.DM.decaltype == "PANEL" else None
                        matchsubname = self.subset if self.matchsub and init_mat.DM.decaltype in ["SUBSET", "PANEL"] else None

                        mat, matched_type = match_material(obj, init_mat, matchmatname=matchmatname, matchmat2name=matchmat2name, matchsubname=matchsubname)

                        if matched_type == "MATCHED":
                            self.created_mats.append(mat)

                else:
                    # reapply initial material, if all matches are toggled off
                    for obj, init_mat in self.decals:
                        obj.active_material = init_mat

        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in {'LEFTMOUSE', 'SPACE'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

            # remove materials, that were created in the process of matching, except the ones currently applied
            active_mats = [obj.active_material for obj, _ in self.decals]
            purge_mats = [mat for mat in self.created_mats if mat not in active_mats]

            # print("active materials:", [mat.name for mat in active_mats])
            # print("purging:", [mat.name for mat in purge_mats])

            for mat in purge_mats:
                if mat.users < 1:
                    remove_decalmat(mat)

            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cancel_modal(self, removeHUD=True):
        if removeHUD:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

        # reapply original materials
        for obj, init_mat in self.decals:
            obj.active_material = init_mat

        # remove materials, that were created in the process of matching
        for mat in self.created_mats:
            remove_decalmat(mat)

    def invoke(self, context, event):
        # update the enum, while at it and get the matchable materials this way
        self.mats = [mat.name for mat in set_match_material_enum()]

        # insiert the None/default white material
        self.mats.insert(0, "None")

        self.decals = [(obj, obj.active_material) for obj in context.selected_objects if obj.DM.isdecal and obj.active_material.DM.isdecalmat and obj.active_material.DM.decaltype != "INFO"]

        self.hasmat = True if any(mat.DM.decaltype in ["SIMPLE", "SUBSET", "PANEL"] for _, mat in self.decals) else False
        self.hasmat2 = True if any(mat.DM.decaltype in ["PANEL"] for _, mat in self.decals) else False
        self.hassub = True if any(mat.DM.decaltype in ["SUBSET", "PANEL"] for _, mat in self.decals) else False

        self.matchmat = True if self.hasmat and not self.hasmat2 and not self.hassub else False
        self.matchmat2 = False
        self.matchsub = True if self.hassub else False

        # set up initial match materials according to and matchedto props
        if len(self.decals) == 1:
            self.material = self.decals[0][0].active_material.DM.matchedmaterialto.name if self.decals[0][0].active_material.DM.matchedmaterialto else self.mats[0]
            self.material2 = self.decals[0][0].active_material.DM.matchedmaterial2to.name if self.decals[0][0].active_material.DM.matchedmaterial2to else self.mats[0]
            self.subset = self.decals[0][0].active_material.DM.matchedsubsetto.name if self.decals[0][0].active_material.DM.matchedsubsetto else self.mats[0]

        # unless there are multiple objects in the selection
        else:
            self.material = self.mats[0]
            self.material2 = self.mats[0]
            self.subset = self.mats[0]

        # initial match
        if any([self.matchsub, self.matchmat, self.matchmat2]):

            # collect all materials that going to be created
            self.created_mats = []

            for obj, init_mat in self.decals:

                matchmatname = self.material if self.matchmat else None
                matchmat2name = self.material2 if self.matchmat2 and init_mat.DM.decaltype == "PANEL" else None
                matchsubname = self.subset if self.matchsub and init_mat.DM.decaltype in ["SUBSET", "PANEL"] else None

                mat, matched_type = match_material(obj, init_mat, matchmatname=matchmatname, matchmat2name=matchmat2name, matchsubname=matchsubname)

                if matched_type == "MATCHED":
                    self.created_mats.append(mat)


        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y

        args = (self, context, event)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), "WINDOW", "POST_PIXEL")

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
