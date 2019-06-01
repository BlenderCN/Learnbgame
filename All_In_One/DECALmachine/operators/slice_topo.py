import bpy
from bpy.props import FloatProperty, BoolProperty, IntProperty
from . panel_unwrap import panel_unwrap
from . init_base_material import init_base_material
from .. import M3utils as m3
from .. utils.operators import hide_meshes, intersect, append_paneling_material


# TODO: add bridge offset parameter aka 'twist', because sometimes the bridge will turn out unfortunately

class TopoSlice(bpy.types.Operator):
    bl_idname = "machin3.topo_slice"
    bl_label = "MACHIN3: Topo Slice"
    bl_options = {'REGISTER', 'UNDO'}

    panelwidth = FloatProperty(name="Panel Width", default=5, min=0.01)
    height = FloatProperty(name="Decal Height", default=0)
    twistoffset = IntProperty(name="Twist Offset", default=0)
    rotateUVs = BoolProperty(name="Rotate UVs", default=False)
    flip = BoolProperty(name="Flip Normals", default=False)
    parent = BoolProperty(name="Parent", default=True)
    wstep = BoolProperty(name="Transfer Normals", default=True)
    wstepshow = BoolProperty(name="Show in Viewport", default=True)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "panelwidth")
        col.prop(self, "height")
        col.prop(self, "twistoffset")
        col.prop(self, "rotateUVs")
        col.prop(self, "flip")
        col.prop(self, "parent")

        row = col.row()
        row.prop(self, "wstep")
        row.prop(self, "wstepshow")

    def execute(self, context):
        if m3.DM_prefs().consistantscale:
            self.scene_scale = m3.get_scene_scale()
        else:
            self.scene_scale = 1

        self.midlevel = 1 - (0.0001 / self.scene_scale)  # 0.9999 for scene scale of 1.0
        self.pwidth = self.panelwidth / 100 / self.scene_scale

        if bpy.context.scene.decals.debugmode:
            decal_slice(self)
        else:
            try:
                decal_slice(self)
            except:
                # msg = "Decal Slicing failed! Options:\n 1. Try repositioning the cutter and re-slice.\n 2. Try a to re-slice with a smaller panel width.\n 3. If there is strip geometry, but no UVs manually remove all triangles and do the UVs using Panel Unwrap.\n 4. Use the Knife, if your cut would not create a closed panel strip!"
                # self.report({'ERROR'}, msg)
                m3.change_context("VIEW_3D")
                m3.set_mode("OBJECT")

        return {'FINISHED'}


class TopoKnife(bpy.types.Operator):
    bl_idname = "machin3.topo_knife"
    bl_label = "MACHIN3: Topo Knife"
    bl_options = {'REGISTER', 'UNDO'}

    panelwidth = FloatProperty(name="Panel Width", default=5, min=0.01)
    height = FloatProperty(name="Decal Height", default=0)
    rotateUVs = BoolProperty(name="Rotate Uvs", default=True)
    flip = BoolProperty(name="Flip Normals", default=False)
    parent = BoolProperty(name="Parent", default=True)
    wstep = BoolProperty(name="Transfer Normals", default=True)
    wstepshow = BoolProperty(name="Show in Viewport", default=True)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "panelwidth")
        col.prop(self, "height")
        col.prop(self, "rotateUVs")
        col.prop(self, "flip")
        col.prop(self, "parent")

        row = col.row()
        row.prop(self, "wstep")
        row.prop(self, "wstepshow")

    def execute(self, context):
        if m3.DM_prefs().consistantscale:
            self.scene_scale = m3.get_scene_scale()
        else:
            self.scene_scale = 1

        self.midlevel = 1 - (0.0001 / self.scene_scale)  # 0.9999 for scene scale of 1.0
        self.pwidth = self.panelwidth / 100 / self.scene_scale

        if bpy.context.scene.decals.debugmode:
            decal_slice(self, knife=True)
        else:
            try:
                decal_slice(self, knife=True)
            except:
                # msg = "Decal Knife failed! The Knife is for Straight cuts, that don't create closed loops!\n 1. Try repositioning the cutter and re-knife.\n 2. Try a to re-knife with a smaller panel width.\n 3. If there is strip geometry, but no UVs manually remove all triangles and do the UVs using Panel Unwrap. 4. Use the Slice, if your cut would create c losed panel strip loop!"
                # self.report({'ERROR'}, msg)
                m3.change_context("VIEW_3D")
                m3.set_mode("OBJECT")

        return {'FINISHED'}


def decal_slice(self, knife=False):
    selection = m3.selected_objects()

    if len(selection) == 2:
        target = m3.get_active()
        selection.remove(target)
        cutter = selection[0]

        init_base_material([target])

        # duplicating the target, which will become the panel decal
        panelstrip = target.copy()
        panelstrip.data = target.data.copy()
        bpy.context.scene.objects.link(panelstrip)

        # hiding the original target object
        target.hide = True

        # applying all modifiers(including bevel, so you can project on objets where the bevels arent applies yet)
        m3.make_active(panelstrip)
        for mod in panelstrip.modifiers:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

        # hiding the panelstrip geo
        cutter.select = False
        panelstrip.select = True
        hide_meshes()

        # also, making sure the cutter geometry is not hidden
        panelstrip.select = False
        cutter.select = True
        m3.make_active(cutter)
        m3.set_mode("EDIT")
        m3.set_mode("FACE")
        bpy.ops.mesh.reveal()
        m3.set_mode("OBJECT")

        # make sure scale of the cutter is 1,1,1(so the solidify will be consistant)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # reselecting the panelstrip
        panelstrip.select = True

        # duplicating the cutter for potential future use
        cutterbackup = cutter.copy()
        cutterbackup.data = cutter.data.copy()
        # prevent it from being removed after scene reload
        cutterbackup.use_fake_user = True

        # timestamping the cutterbackup
        timestamp = m3.set_timestamp(cutterbackup)

        # add thickness to cutter
        solidify = cutter.modifiers.new(name="Solidify", type="SOLIDIFY")
        solidify.offset = 0
        solidify.thickness = self.pwidth

        m3.make_active(panelstrip)

        # boolean intersection
        intersect()

        panelstrip.name = "panel_decal_" + target.name
        cutterbackup.name = "backup_" + panelstrip.name

        # timestamping the strip like the cutterbackup
        m3.set_timestamp(panelstrip, timestamp=timestamp)

        # remove unwanted parts and leave only the "projected decal"
        panelstrip.select = True
        m3.set_mode("EDIT")
        m3.select_all("MESH")
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.mesh.reveal()

        # rebuilding the strip geo from the boundary loops
        # this way we don't have to clear n-gones created on big polygons where a panel strip bends by hand
        if not knife:
            m3.select_all("MESH")
            bpy.ops.mesh.region_to_loop()
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='EDGE_FACE')
            m3.select_all("MESH")
            bpy.ops.mesh.bridge_edge_loops(twist_offset=self.twistoffset)

        # optionally flip normals
        if self.flip:
            bpy.ops.mesh.flip_normals()

        m3.set_mode("OBJECT")

        # adding a slight displace to the panel decal
        displace = panelstrip.modifiers.new(name="Displace", type="DISPLACE")

        # enough to avoid z-fighting, yet not enough to produce a noticable shadow when rendering
        displace.mid_level = self.midlevel - (self.height / 1000 / self.scene_scale)
        displace.show_in_editmode = True
        displace.show_on_cage = True

        # enable wire display
        panelstrip.show_wire = True
        panelstrip.show_all_edges = True

        # make panel strip smooth shaded
        bpy.ops.object.shade_smooth()

        # cleaning out all materials of the panelstrip
        panelstrip.select = True
        for slot in panelstrip.material_slots:
            bpy.ops.object.material_slot_remove()

        defaultpaneling = bpy.context.scene.decals.defaultpaneling
        panelingmat = bpy.data.materials.get(defaultpaneling)

        if panelingmat:
            panelstrip.data.materials.append(panelingmat)
        else:
            try:
                panelingmat = append_paneling_material(defaultpaneling)  # > paneling01_1
                panelstrip.data.materials.append(panelingmat)

                # MACHIN3tools material viewport compensation
                if bpy.app.version >= (2, 79, 0):
                    if m3.M3_check():
                        if m3.M3_prefs().viewportcompensation:
                            bpy.ops.machin3.adjust_principled_pbr_node(isdecal=True)

            except:
                self.report({'ERROR'}, "Could not find paneling01_01 decal and material, make sure the Decals asset library is in your DECALmachine folder!")

        # UVs
        panel_unwrap(panelstrip, knife=self.rotateUVs)

        # selecting the panel decal
        panelstrip.select = True

        # unhiding and original target object (which also selects it)
        target.hide = False
        target.select = True

        if self.wstep:
            # make active the target to prepare for wstep
            m3.make_active(target)

            # transfer the normals from the target
            bpy.ops.machin3.wstep()

            # turn off viewport visibiity for performance reasons
            if not self.wstepshow:
                mod = panelstrip.modifiers.get("M3_copied_normals")
                mod.show_viewport = False

            # unselecting the target
            target.select = False

        # turn off shadow casting for panel strip
        panelstrip.cycles_visibility.shadow = False

        # if bpy.context.scene.decals.parentslice:
        if self.parent:
            # panelstrip.parent = target
            # panelstrip.matrix_parent_inverse = target.matrix_world.inverted()

            # cutterbackup.parent = target
            # cutterbackup.matrix_parent_inverse = target.matrix_world.inverted()

            # the above doesn't quite work once a decal is brought back and used to cut or
            # project again and then brought back again, doing it via ops seems to work
            # another issue is: hops adjust bevel also interferes as it seems to apply transforms times
            # to fis this line 33 in adjust_bevel.py (bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)) needs to be commented out

            panelstrip.select = True
            target.select = True
            m3.make_active(target)
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

            panelstrip.select = False
            bpy.context.scene.objects.link(cutterbackup)
            cutterbackup.select = True
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            bpy.context.scene.objects.unlink(cutterbackup)

            target.select = False
            panelstrip.select = True
            m3.make_active(panelstrip)

        # add to group pro group
        if m3.GP_check():
            if m3.DM_prefs().groupproconnection:
                if len(bpy.context.scene.storedGroupSettings) > 0:
                    bpy.ops.object.add_to_grouppro()

    else:
        # print("Select exactly two objects: the cutter and the object to receive the paneling!")
        self.report({'ERROR'}, "Select exactly two objects: the cutter and the object to receive the paneling!")
