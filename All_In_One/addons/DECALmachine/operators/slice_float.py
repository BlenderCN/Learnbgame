import bpy
import bmesh
from bpy.props import FloatProperty, BoolProperty, IntProperty
from . panel_unwrap import panel_unwrap
from . init_base_material import init_base_material
from .. import M3utils as m3
from .. utils.operators import append_paneling_material, hide_meshes, intersect


# TODO: knife?


class FloatSlice(bpy.types.Operator):
    bl_idname = "machin3.float_slice"
    bl_label = "MACHIN3: Float Slice"
    bl_options = {'REGISTER', 'UNDO'}

    panelwidth = FloatProperty(name="Panel Width", default=5, min=0.01)
    height = FloatProperty(name="Decal Height", default=1)
    simplify = IntProperty(name="Simplify", default=0, min=0)
    density = IntProperty(name="Density", default=0, min=0, max=4)
    offset = FloatProperty(name="Offset (experimental)", default=0)
    shrinkwrap = BoolProperty(name="Shrink Wrap", default=True)
    rotateUVs = BoolProperty(name="Rotate UVs", default=False)
    flip = BoolProperty(name="Flip Normals", default=False)
    parent = BoolProperty(name="Parent", default=True)
    avgedges = BoolProperty(name="Average Edge Lengths (experimental, slow)", default=False)
    wstep = BoolProperty(name="Transfer Normals", default=True)
    wstepshow = BoolProperty(name="Show in Viewport", default=True)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "panelwidth")
        col.prop(self, "height")
        col.prop(self, "simplify")
        col.prop(self, "density")
        col.prop(self, "offset")
        col.prop(self, "rotateUVs")
        col.prop(self, "flip")
        col.prop(self, "shrinkwrap")
        col.prop(self, "parent")
        col.prop(self, "avgedges")

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
        self.poffset = self.offset / self.scene_scale

        selection = m3.selected_objects()

        if len(selection) == 2:
            self.target = m3.get_active()
            target = self.target
            selection.remove(target)
            cutter = selection[0]

            if "panel_source" in cutter.name:  # got the edge line from slice draw
                panelstrip = cutter
                m3.make_active(panelstrip)
                panelstrip.name = "panel_decal_" + target.name
                cutterbackup = None

                panelstrip.select = True
                target.select = False
                m3.set_mode("EDIT")

                # wstep looks funny for these for some reason, turning it off
                self.wstep = False

                if self.simplify > 0:
                    bpy.ops.mesh.remove_doubles(threshold=self.simplify / 10000 / self.scene_scale)

                # create panel decal
                create_panel_strip(self, context, cutter, target)
            else:  # create edle line by interescting cutter with target
                m3.unselect_all("OBJECT")

                # duplicating the cutter for potential future use
                cutterbackup = cutter.copy()
                cutterbackup.data = cutter.data.copy()
                # prevent it from being removed after scene reload
                cutterbackup.use_fake_user = True

                # timestamping the cutterbackup
                timestamp = m3.set_timestamp(cutterbackup, silent=False)

                # initialise the target material
                init_base_material([target])

                panelstrip = target.copy()
                panelstrip.data = target.data.copy()
                bpy.context.scene.objects.link(panelstrip)
                target.hide = True

                # timestamping the strip like the cutterbackup
                m3.set_timestamp(panelstrip, timestamp=timestamp, silent=False)

                # applying all modifiers(including bevel, so you can project on objets where the bevels arent applies yet)
                m3.make_active(panelstrip)
                for mod in panelstrip.modifiers:
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

                panelstrip.select = True
                m3.make_active(panelstrip)
                hide_meshes()

                cutter.select = True

                intersect()

                panelstrip.name = "panel_decal_" + target.name
                cutterbackup.name = "backup_" + panelstrip.name

                m3.set_mode("EDIT")
                m3.set_mode("EDGE")
                m3.select_all("MESH")
                bpy.ops.mesh.delete(type='FACE')
                m3.unhide_all("MESH")
                bpy.ops.mesh.delete(type='EDGE')

                m3.set_mode("VERT")
                m3.select_all("MESH")
                # bpy.ops.mesh.remove_doubles(threshold=self.panelwidth / 2 / 100)

                target.hide = False

                if self.simplify > 0:
                    bpy.ops.mesh.remove_doubles(threshold=self.simplify / 10000 / self.scene_scale)

                # create panel decal
                create_panel_strip(self, context, panelstrip, target)

            if self.parent:
                # panelstrip.parent = target
                # panelstrip.matrix_parent_inverse = target.matrix_world.inverted()

                # cutterbackup.parent = target
                # cutterbackup.matrix_parent_inverse = target.matrix_world.inverted()

                panelstrip.select = True
                target.select = True
                m3.make_active(target)
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

                if cutterbackup:
                    panelstrip.select = False
                    bpy.context.scene.objects.link(cutterbackup)
                    cutterbackup.select = True
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                    bpy.context.scene.objects.unlink(cutterbackup)

                target.select = False
                panelstrip.select = True
                m3.make_active(panelstrip)

            if self.avgedges:
                # select edges determening panel width
                m3.set_mode("EDIT")
                m3.set_mode("FACE")
                m3.select_all("MESH")
                bpy.ops.mesh.region_to_loop()
                m3.invert()
                bpy.ops.mesh.loop_multi_select(ring=True)
                m3.set_mode("OBJECT")

                self.avgedgelengths(panelstrip)

            # add to group pro group
            if m3.GP_check():
                if m3.DM_prefs().groupproconnection:
                    if len(bpy.context.scene.storedGroupSettings) > 0:
                        bpy.ops.object.add_to_grouppro()

        return {'FINISHED'}

    def avgedgelengths(self, obj):
        # get selected edges and their lengths
        edges, edgeids = self.get_edges(obj)

        # get everage edge length
        scalelength = sum([e[1] for e in edges]) / len(edges)
        print("average length: %f" % (scalelength))

        m3.set_mode("EDIT")
        m3.set_mode("EDGE")

        for idx, length in edges:
            m3.unselect_all("MESH")
            if length != scalelength:
                m3.make_selection("EDGE", [idx])
                scale = scalelength / length
                bpy.ops.transform.resize(value=(scale, scale, scale))
                print("scaled edge '%d' from '%f' to '%f'." % (idx, length, scalelength))
            else:
                print("left edge '%d' unchanged, already at length '%f'." % (idx, scalelength))

        m3.make_selection("EDGE", edgeids)

        m3.set_mode("OBJECT")

        return {'FINISHED'}

    def get_edges(self, obj):
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        edges = []
        edgeids = []
        for edge in bm.edges:
            if edge.select:
                edges.append((edge.index, edge.calc_length()))
                edgeids.append(edge.index)
        return edges, edgeids


def create_panel_strip(self, context, panelsource, target):
    panel = panelsource

    m3.unhide_all("MESH")
    m3.select_all("MESH")

    # subdividing aka "slice density", NOTE: running it with 0 will still subdide once(as does one), we dont want that
    if self.density > 0:
        bpy.ops.mesh.subdivide(number_cuts=self.density, smoothness=0)

    m3.set_mode("OBJECT")

    bpy.ops.object.convert(target='CURVE')

    panel.data.bevel_depth = self.pwidth

    # panel.data.fill_mode = 'FRONT'
    panel.data.fill_mode = 'BACK'
    panel.data.twist_mode = 'MINIMUM'

    # TODO: a curve may contain multiple splines!!
    iscyclic = panel.data.splines[0].use_cyclic_u

    # turning off cyclisity for better shrinkwrap behaviour
    if iscyclic:
        panel.data.splines[0].use_cyclic_u = False

    shrink = panel.modifiers.new(name="Shrinkwrap", type="SHRINKWRAP")
    shrink.target = target

    # NOTE: the offset only works in certain situations, it depends on how the curve lies on the surface which depends on the twisting doesnt look like you can influence this
    panel.data.offset = - (self.pwidth / 2 + self.poffset) / 100

    bpy.ops.object.convert(target='MESH')

    if self.shrinkwrap:
        shrink = panel.modifiers.new(name="Shrinkwrap", type="SHRINKWRAP")
        shrink.target = self.target
        shrink.show_on_cage = True
        shrink.show_expanded = False

    displace = panel.modifiers.new(name="Displace", type="DISPLACE")
    displace.mid_level = self.midlevel - (self.height / 1000 / self.scene_scale)
    displace.show_on_cage = True
    displace.show_in_editmode = True

    m3.set_mode("EDIT")
    m3.set_mode("FACE")
    m3.select_all("MESH")

    bpy.ops.mesh.flip_normals()

    # bridge the gap when curve was cyclic
    if iscyclic:
        print("panel strip is cyclic")
        m3.select_all("MESH")
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.select_all(action='INVERT')

        m3.set_mode("OBJECT")

        interioredges = []
        for edge in panel.data.edges:
            if edge.select:
                interioredges.append(edge.index)

        # print(interioredges)

        m3.set_mode("EDIT")
        bpy.ops.mesh.loop_multi_select(ring=True)
        m3.set_mode("OBJECT")

        ringedges = []
        for edge in panel.data.edges:
            if edge.select:
                ringedges.append(edge.index)

        # print(ringedges)

        bridgeedges = set(ringedges) - set(interioredges)

        for edge in panel.data.edges:
            if edge.index in bridgeedges:
                edge.select = True
            else:
                edge.select = False

        m3.set_mode("EDIT")
        bpy.ops.mesh.bridge_edge_loops()

    m3.unselect_all("MESH")

    # unwrap
    panel_unwrap(panel, knife=self.rotateUVs)

    # recalc normals, this seems to fix inverted pabel strips that occur sometimes?
    bpy.ops.mesh.normals_make_consistent(inside=False)

    # optionally flip normals
    if self.flip:
        bpy.ops.mesh.flip_normals()

    # append paneling material if its not in the scene and apply it to the panel strip
    m3.set_mode("OBJECT")  # you cant append things in edit mode

    defaultpaneling = bpy.context.scene.decals.defaultpaneling
    panelingmat = bpy.data.materials.get(defaultpaneling)

    if panelingmat:
        panel.data.materials.append(panelingmat)
    else:
        try:
            panelingmat = append_paneling_material(defaultpaneling)  # > paneling01_1
            panel.data.materials.append(panelingmat)

            # MACHIN3tools material viewport compensation
            if bpy.app.version >= (2, 79, 0):
                if m3.M3_check():
                    if m3.M3_prefs().viewportcompensation:
                        bpy.ops.machin3.adjust_principled_pbr_node(isdecal=True)

        except:
            self.report({'ERROR'}, "Could not find paneling01_01 decal and material, make sure the Decals asset library is in your DECALmachine folder!")

    panel.select = True
    target.select = True

    if self.wstep:
        # make active the target to prepare for wstep
        m3.make_active(target)

        # transfer the normals from the target
        bpy.ops.machin3.wstep()

        # turn off viewport visibiity for performance reasons
        if not self.wstepshow:
            mod = panel.modifiers.get("M3_copied_normals")
            mod.show_viewport = False

    target.select = False

    panel.cycles_visibility.shadow = False
    panel.cycles_visibility.glossy = False
    panel.show_wire = True
    panel.show_all_edges = True
    panel.show_x_ray = False
    bpy.ops.object.shade_smooth()
