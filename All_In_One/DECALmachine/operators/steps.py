import bpy
from bpy.props import BoolProperty, EnumProperty
from . init_base_material import init_base_material
from .. import M3utils as m3

# TODO: operator properties: loop mapping, use_transform_switch


wsteptypes = [
              ('POLYINTERP_LNORPROJ', "Projected Face Interpolated", ""),
              ('POLYINTERP_NEAREST', "Nearest Face Interpolated", ""),
              # ('NEAREST_POLY', "Nearest Corner of Nearest Face", ""),
              ('NEAREST_POLYNOR', "Nearest Corner and Best Matching Face Normal", "")
              # ('NEAREST_NORMAL', "Nearest Corner and Best Matching Normal", ""),
              # ('TOPOLOGY', "Topology", "")
              ]

wsteptypes.reverse()


class WStep(bpy.types.Operator):
    bl_idname = "machin3.wstep"
    bl_label = "MACHIN3: (W)Step"
    bl_options = {'REGISTER', 'UNDO'}

    wsteptype = EnumProperty(name="Type", items=wsteptypes, default="POLYINTERP_NEAREST")

    allowhard = BoolProperty(name="Allow Hard Edges", default=False)
    wstepshow = BoolProperty(name="Show in Viewport", default=True)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "wsteptype")

        column.prop(self, "allowhard")
        column.prop(self, "wstepshow")

    def execute(self, context):
        selection = m3.selected_objects()

        mode = m3.get_mode()

        if mode == "OBJECT":
            if len(selection) >= 2:
                self.copy_normals(selection)
            elif len(selection) == 1:
                self.create_weighted_normals(selection[0])
        else:
            self.apply_wstep_mat_to_mesh()

        return {'FINISHED'}

    def apply_wstep_mat_to_mesh(self):
        active = m3.get_active()
        wstepmat, wstepslot = self.get_wstep_mat(active)

        activeslot = active.active_material_index

        if activeslot != wstepslot:
            # set the active material slot
            active.active_material_index = wstepslot

            # assign the material
            bpy.ops.object.material_slot_assign()
        else:
            active.active_material_index = 0
            bpy.ops.object.material_slot_assign()

    def copy_normals(self, selection, applycustomnormals=False):
        removesharps = bpy.context.scene.decals.wstepremovesharps
        modname = "M3_copied_normals"

        nrmsrc = m3.get_active()
        selection.remove(nrmsrc)

        nrmsrc.select = False

        for obj in selection:
            if obj.modifiers.get("M3_custom_normals"):  # skip objs that have M3_custom_normals
                continue

            # always clear previous normal info before adding a new one, this prevents unwanted shading isses from previous baked in normals
            # unfortunately it acts on the active as well, not just on selected, so we need to 'un-active' the nrmsrc, by activating smth else first
            m3.make_active(obj)
            bpy.ops.mesh.customdata_custom_splitnormals_clear()

            # remove existing M3_custom_normals mod
            if obj.modifiers.get(modname):
                bpy.ops.object.modifier_remove(modifier=modname)
                print("Removed previous modifier '%s'." % (modname))

            # add data transfer mod
            self.add_data_transfer(obj, nrmsrc, modname)

            # NOTE: is this outdated with DecalBakeDown's transfer_sharps()?
            if removesharps:
                # remove all sharp edges, this is actually optional, but useful for DECALBakeDown
                m3.set_mode("EDIT")
                m3.set_mode("EDGE")
                m3.unhide_all("MESH")
                m3.select_all("MESH")

                bpy.ops.mesh.mark_sharp(clear=True)

                m3.unselect_all("MESH")
                m3.set_mode("OBJECT")

                print("Removed sharp edges.")

            # note that, applying the data transfer doesn't work well with active mirror mods
            # instead the data_transfer needs to stay active and needs to be after the mirror
            if applycustomnormals:
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modname)

    def create_weighted_normals(self, target, applycustomnormals=False):
        m3.make_active(target)  # just to make extra sure

        modname = "M3_custom_normals"
        hardname = "M3_hard_custom_normals"

        # we don't want to run custom normal creation on decals (and thereby remove the normal source)
        if target.modifiers.get("M3_copied_normals"):
            return

        # remove existing data transfer as well its normal source
        mod = target.modifiers.get(modname)
        if mod:
            nrmsrc = mod.object
            if nrmsrc:
                bpy.data.objects.remove(nrmsrc, do_unlink=True)
            target.modifiers.remove(mod)

        # remove existing data transfer for hard edges
        hard = target.modifiers.get(hardname)
        if hard:
            target.modifiers.remove(hard)

        # remove existing custom normals
        if target.data.has_custom_normals:
            bpy.ops.mesh.customdata_custom_splitnormals_clear()

        # m3.set_mode("EDIT")
        # m3.unhide_all("MESH")
        # m3.set_mode("OBJECT")

        # get bevel mod
        bevel = target.modifiers.get("Bevel")

        print("create weighted normals")

        wstepmat, wstepslot = self.get_wstep_mat(target)

        # if there's a live bevel mod "w-step" it
        if bevel:
            bevel.material = wstepslot
            bsegments = bpy.context.object.modifiers["Bevel"].segments
            bevel.segments = 1

            # bwidth = bpy.context.object.modifiers["Bevel"].width
            bprofile = bpy.context.object.modifiers["Bevel"].profile
            bclamp = bpy.context.object.modifiers["Bevel"].use_clamp_overlap
            bmethod = bpy.context.object.modifiers["Bevel"].limit_method

            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=bevel.name)

            try:
                target["hops"]["status"] = 2
            except:
                pass

            self.remove_bevel_weights(target)

        # make sure the target is smooth shaded, so the duplicate will be as well
        bpy.ops.object.shade_smooth()

        # duplicate target to create nrmsrc and remove bevel geometry from it
        bpy.ops.object.duplicate()

        nrmsrc = m3.get_active()
        self.remove_bevel_geo(nrmsrc, wstepslot)

        # parent the nrm source (not necessary in if data transfer turns off object transform)
        # nrmsrc.parent = target
        # nrmsrc.matrix_parent_inverse = target.matrix_world.inverted()

        # even better you don't need to move it to some layer, you can just unlink it!!
        # bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))
        bpy.context.scene.objects.unlink(nrmsrc)
        nrmsrc.use_fake_user = True

        # add data transfer to the target, with nrmsrc as the source and apply the mod
        m3.make_active(target)
        self.add_data_transfer(target, nrmsrc, modname)
        if self.allowhard:
            hardgroup = self.create_hard_vgroup(target)
            self.add_hard_edges(target, nrmsrc, hardname, hardgroup)

        if applycustomnormals:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modname)

            # remove nrmsrc
            m3.make_active(nrmsrc)
            bpy.ops.object.delete(use_global=False)

            m3.make_active(target)
            target.select = True
        else:
            # nrmsrc.hide = True  # no need for hiding without object transform on the data transfer
            nrmsrc.name = "normal_src_" + target.name

        m3.set_mode("EDIT")
        m3.set_mode("VERT")
        m3.select_all("MESH")
        bpy.ops.mesh.hide()
        m3.set_mode("OBJECT")

        # add a new bevel mod, if there been one before
        if bevel:
            if bmethod == "WEIGHT":
                modcount = len(target.modifiers)

                newbevel = target.modifiers.new("Bevel", type="BEVEL")

                newbevel.width = 0.1
                newbevel.segments = bsegments
                newbevel.profile = bprofile
                newbevel.use_clamp_overlap = bclamp
                newbevel.limit_method = bmethod

                for _ in range(modcount):
                    bpy.ops.object.modifier_move_up(modifier=newbevel.name)

        target.select = True

    def remove_bevel_weights(self, obj):
        mesh = obj.data
        for edge in mesh.edges:
            if edge.bevel_weight > 0:
                edge.bevel_weight = 0
                edge.use_edge_sharp = True

    def add_data_transfer(self, obj, nrmsrc, modname):
        # add data transfer mod
        data_transfer = obj.modifiers.new(modname, "DATA_TRANSFER")
        data_transfer.object = nrmsrc
        data_transfer.use_loop_data = True
        # data_transfer.loop_mapping = 'POLYINTERP_NEAREST'  # this one seems to ignore sharp edges, and so has a tendency to produce produce triangulated shading in blender, luckily it's mostly a blender (viewport?) issue and unity renders them much better, especitlly when triangulated properly befor eexporting (beauty)
        # data_transfer.loop_mapping = 'NEAREST_NORMAL'
        # data_transfer.loop_mapping = 'NEAREST_POLYNOR'  # this takes sharp edges into account and has no triangulation issues
        data_transfer.loop_mapping = self.wsteptype

        data_transfer.data_types_loops = {'CUSTOM_NORMAL'}
        data_transfer.show_expanded = False

        # if you turn this off, you don't need to parent the nrmsrc!
        data_transfer.use_object_transform = False

        # enable or disable in viewport for performance reasons
        data_transfer.show_viewport = self.wstepshow

        # make sure autosmooth is on
        obj.data.use_auto_smooth = True

        print("Added modifier '%s' to object '%s'." % (modname, obj.name))

    def add_hard_edges(self, obj, nrmsrc, hardname, hardgroup):
        # add data transfer mod
        data_transfer = obj.modifiers.new(hardname, "DATA_TRANSFER")
        data_transfer.object = nrmsrc
        data_transfer.use_loop_data = True
        data_transfer.loop_mapping = 'NEAREST_POLYNOR'  # this takes sharp edges into account and has no triangulation issues

        data_transfer.vertex_group = hardgroup.name

        data_transfer.data_types_loops = {'CUSTOM_NORMAL'}
        data_transfer.show_expanded = False

        # if you turn this off, you don't need to parent the nrmsrc!
        data_transfer.use_object_transform = False

        # enable or disable in viewport for performance reasons
        data_transfer.show_viewport = self.wstepshow

        # make sure autosmooth is on
        obj.data.use_auto_smooth = True

        print("Added modifier '%s' to object '%s'." % (hardname, obj.name))

    def create_hard_vgroup(self, obj):
        hard_edges = obj.vertex_groups.get("hard_edges")

        if hard_edges:
            obj.vertex_groups.remove(hard_edges)
            print("Removed existing 'hard_edges' vertex group.")

        hard_edges = obj.vertex_groups.new(name="hard_edges")
        print("Created new 'hard_edges' vertex group.")

        m3.set_mode("EDIT")
        m3.set_mode("EDGE")
        m3.unhide_all("MESH")
        m3.unselect_all("MESH")
        m3.set_mode("OBJECT")

        mesh = obj.data

        vids = []
        for edge in mesh.edges:
            if edge.use_edge_sharp:
                if edge.vertices[0] not in vids:
                    vids.append(edge.vertices[0])
                if edge.vertices[1] not in vids:
                    vids.append(edge.vertices[1])

        hard_edges.add(vids, 1, "REPLACE")
        return hard_edges

    def remove_bevel_geo(self, obj, matidx):
        m3.set_mode("EDIT")
        m3.set_mode("FACE")
        m3.unhide_all("MESH")
        m3.unselect_all("MESH")
        m3.set_mode("OBJECT")

        mesh = obj.data
        for face in mesh.polygons:
            if face.material_index == matidx:
                face.select = True
        # mesh.update()

        m3.set_mode("EDIT")
        bpy.ops.mesh.delete(type='FACE')
        m3.set_mode("OBJECT")

    def get_wstep_mat(self, nrmsrc):
        # make sure there is a material on the nrmsrc
        init_base_material([nrmsrc])

        # take the very first material as the nrmsrc material
        nrmsrcmat = nrmsrc.material_slots[0].material

        # look for existing wstep material in nrmsrc.material_slots
        wstepmat = None
        wstepslot = None
        for idx, slot in enumerate(nrmsrc.material_slots):
            if slot.material is not None:
                if slot.material.name.endswith("_wstep"):
                    wstepmat = slot.material
                    wstepslot = idx
                    print("found existing wstep material")
                    print(wstepmat.name, wstepslot)
                    break

        # look for existing wstep material in scene and create one if none is found
        if not wstepmat:
            print("looking for wstep material based on material '%s'." % (nrmsrcmat.name))
            wstepmat = bpy.data.materials.get(nrmsrcmat.name + "_wstep")
            if wstepmat is None:
                print("created new wstep material based on material '%s'." % (nrmsrcmat.name))
                wstepmat = nrmsrcmat.copy()
                wstepmat.name = nrmsrcmat.name + "_wstep"

                # make sure nodes are used
                wstepmat.use_nodes = True
                tree = wstepmat.node_tree

                # add rgb node
                rgb = tree.nodes.new("ShaderNodeRGB")
                rgbout = rgb.outputs['Color']
                rgbout.default_value = (1, 0, 0, 1)

                # mute it by default:
                rgb.mute = True

                glossy = tree.nodes.get("Glossy BSDF")
                if glossy:
                    glossyin = glossy.inputs['Color']
                    tree.links.new(rgbout, glossyin)

                pbr = tree.nodes.get("Principled BSDF")
                if pbr:
                    pbrin = pbr.inputs['Base Color']
                    tree.links.new(rgbout, pbrin)

                if not any([glossy, pbr]):
                    print("Neither Glossy BSDF not Principled BSDF shaders found in material '%s'." % (wstepmat.name))

            nrmsrc.data.materials.append(wstepmat)
            wstepslot = len(nrmsrc.material_slots) - 1
            print(wstepmat.name, wstepslot)

        return wstepmat, wstepslot


class EditNormalSource(bpy.types.Operator):
    bl_idname = "machin3.edit_normal_source"
    bl_label = "MACHIN3: Edit Normal Source"

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object.mode == "OBJECT"

    def execute(self, context):
        active = m3.get_active()
        if active.name.startswith("normal_src_"):
            self.commit_normal_source(active)
        else:
            try:
                wstep = active.modifiers.get("M3_custom_normals")
            except:
                wstep = None

            if wstep:
                self.edit_normal_source(active, wstep)

        return {'FINISHED'}

    def edit_normal_source(self, active, wstep):
        # check if already in localview, if so exit
        if m3.get_localview():
            bpy.ops.view3d.localview()

        source = wstep.object

        if source:
            active.select = False

            bpy.context.scene.objects.link(source)
            source.select = True
            m3.make_active(source)

            source["wstepped"] = active.name

            bpy.ops.view3d.localview()
        else:
            return

    def commit_normal_source(self, active):
        wsteppedname = active["wstepped"]
        wstepped = bpy.data.objects[wsteppedname]

        bpy.context.scene.objects.unlink(active)

        bpy.ops.view3d.localview()

        wstepped.select = True
        wstepped = m3.make_active(wstepped)

        wstepped.data.update()


class EditSurfaceFix(bpy.types.Operator):
    bl_idname = "machin3.edit_surface_fix"
    bl_label = "MACHIN3: Edit Surface Fix"

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object.mode == "OBJECT"

    def execute(self, context):
        active = m3.get_active()
        if active.name.startswith("surface_fix_"):
            self.commit_surface_fix(active)
        else:
            try:
                sfix = active.modifiers.get("M3_surface_fix")
            except:
                sfix = None

            if sfix:
                self.edit_surface_fix(active, sfix)

        return {'FINISHED'}

    def edit_surface_fix(self, active, sfix):
        # check if already in localview, if so exit
        if m3.get_localview():
            bpy.ops.view3d.localview()

        source = sfix.object

        if source:
            active.select = False

            bpy.context.scene.objects.link(source)
            source.select = True
            m3.make_active(source)

            source["sfixed"] = active.name

            bpy.ops.view3d.localview()
        else:
            return

    def commit_surface_fix(self, active):
        sfixedname = active["sfixed"]
        sfixed = bpy.data.objects[sfixedname]

        active.use_fake_user = True
        bpy.context.scene.objects.unlink(active)

        bpy.ops.view3d.localview()

        sfixed.select = True
        sfixed = m3.make_active(sfixed)

        sfixed.data.update()

        # for seom reason the normals tend to not update, despit the update(), resetting the nrm source helps
        sfix = sfixed.modifiers.get("M3_surface_fix")
        if sfix:
            sfix.object = active


class Unlink(bpy.types.Operator):
    bl_idname = "machin3.unlink"
    bl_label = "MACHIN3: Unlink"
    bl_options = {'REGISTER', 'UNDO'}

    sfprefix = BoolProperty(name="Add 'surface_fix_' Prefix", default=True)
    nsprefix = BoolProperty(name="Add 'normal_src_' Prefix", default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "sfprefix")
        column.prop(self, "nsprefix")

    def execute(self, context):
        active = m3.get_active()

        if self.sfprefix:
            active.name = "surface_fix_" + active.name

        if self.nsprefix:
            active.name = "normal_src_" + active.name

        active.use_fake_user = True
        bpy.context.scene.objects.unlink(active)

        return {'FINISHED'}


class SurfaceFix(bpy.types.Operator):
    bl_idname = "machin3.surface_fix"
    bl_label = "MACHIN3: Surface Fix"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object.mode == "EDIT"

    def execute(self, context):
        m3.clear()

        active = m3.get_active()
        vids = m3.get_selection("VERT")

        m3.set_mode("OBJECT")

        surface_fix = self.add_surface_fix_vgroup(active, vids)

        nrmsrc = self.create_normal_source(active)

        self.add_surface_fix(active, nrmsrc, "M3_surface_fix", surface_fix)

        return {'FINISHED'}

    def add_surface_fix(self, obj, nrmsrc, surfacefixname, surfacefixgroup):
        # add data transfer mod
        data_transfer = obj.modifiers.new(surfacefixname, "DATA_TRANSFER")
        data_transfer.object = nrmsrc
        data_transfer.use_loop_data = True
        data_transfer.loop_mapping = 'POLYINTERP_NEAREST'
        data_transfer.vertex_group = surfacefixgroup.name

        data_transfer.data_types_loops = {'CUSTOM_NORMAL'}
        data_transfer.show_expanded = False

        # if you turn this off, you don't need to parent the nrmsrc!
        data_transfer.use_object_transform = False

        # make sure autosmooth is on
        obj.data.use_auto_smooth = True

        print("Added modifier '%s' to object '%s'." % (surfacefixname, obj.name))

    def create_normal_source(self, obj):
        bpy.ops.object.duplicate()
        nrmsrc = m3.get_active()

        nrmsrc.name = "surface_fix_" + obj.name
        nrmsrc["sfixed"] = obj.name

        while nrmsrc.modifiers:
            nrmsrc.modifiers.remove(nrmsrc.modifiers[0])

        while nrmsrc.vertex_groups:
            nrmsrc.vertex_groups.remove(nrmsrc.vertex_groups[0])

        bpy.ops.view3d.localview()

        m3.set_mode("EDIT")

        return nrmsrc

    def add_surface_fix_vgroup(self, obj, vids):
        surface_fix = obj.vertex_groups.get("surface_fix")

        if surface_fix:
            print("Use existing 'surface_fix' vertex group.")
        else:
            surface_fix = obj.vertex_groups.new(name="surface_fix")
            print("Created new 'surface_fix' vertex group.")

        surface_fix.add(vids, 1, "ADD")

        return surface_fix


class DStep(bpy.types.Operator):
    bl_idname = "machin3.dstep"
    bl_label = "MACHIN3: (D)Step"

    def execute(self, context):
        active = bpy.context.active_object

        if "_unstepped" in active.name:
            active.name.replace("_unstepped", "")

        # timestamp active
        m3.set_timestamp(active)

        # duplicate active
        dstepbackup = active.copy()
        dstepbackup.data = active.data.copy()

        # prevent it from being removed after scene reload
        dstepbackup.use_fake_user = True

        dstepbackup.name = "backup_dstep_" + active.name

        # step it
        bpy.ops.hops.step()

        m3.set_mode("EDIT")
        bpy.ops.mesh.reveal()

        return {'FINISHED'}
