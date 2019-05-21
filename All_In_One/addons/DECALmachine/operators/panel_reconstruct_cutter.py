import bpy
from bpy.props import FloatProperty, BoolProperty
from .. import M3utils as m3


class ReconstructPanelCutter(bpy.types.Operator):
    bl_idname = "machin3.decal_panel_reconstruct_cutter"
    bl_label = "MACHIN3: Reconstruct Panel Cutter"
    bl_options = {'REGISTER', 'UNDO'}

    depth = FloatProperty(name="Cutter Depth", default=0.03, min=0.001, max=0.1)
    hidepanel = BoolProperty(name="Hide Panel Decal", default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "depth")
        column.prop(self, "hidepanel")

    def execute(self, context):
        self.panel_reconstruct_cutter()

        return {'FINISHED'}

    def panel_reconstruct_cutter(self):
        paneldecal = m3.get_active()

        # create and prepare duplicate
        cutter = paneldecal.copy()
        cutter.data = paneldecal.data.copy()
        cutter.name = "reconstructed_panel_cutter"
        try:
            del cutter["timestamp"]
        except:
            pass

        paneldecal.select = False
        paneldecal.hide = True

        bpy.context.scene.objects.link(cutter)

        cutter.select = True
        m3.make_active(cutter)

        cutter.data.materials.clear(update_data=True)

        for mod in cutter.modifiers:
            if mod.type in ["DISPLACE", "SHRINKWRAP"]:
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
            else:
                bpy.ops.object.modifier_remove(modifier=mod.name)

        # create center edge and add it to a vertex group
        m3.set_mode("EDIT")
        m3.set_mode("FACE")
        m3.unhide_all("MESH")
        m3.select_all("MESH")

        bpy.ops.mesh.region_to_loop()
        m3.invert()
        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.mesh.subdivide(number_cuts=1, smoothness=0)

        bpy.ops.mesh.region_to_loop()
        m3.invert()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=True, type="VERT")
        m3.set_mode("EDGE")
        bpy.ops.mesh.loop_multi_select(ring=False)
        m3.set_mode("OBJECT")

        centeredges = cutter.vertex_groups.new(name="CENTEREDGES")

        vids = []
        for v in cutter.data.vertices:
            if v.select is True:
                vids.append(v.index)

        centeredges.add(vids, 1, "ADD")

        m3.set_mode("EDIT")
        m3.set_mode("FACE")
        m3.select_all("MESH")
        bpy.ops.mesh.duplicate()
        bpy.ops.mesh.flip_normals()
        m3.set_mode("OBJECT")

        # add displace modifier to lift the centeredes
        displace = cutter.modifiers.new(name="Displace", type="DISPLACE")
        displace.vertex_group = "CENTEREDGES"
        displace.mid_level = 1 - self.depth
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=displace.name)

        # remove doubles and select center edges
        m3.set_mode("EDIT")
        m3.set_mode("VERT")
        m3.select_all("MESH")
        bpy.ops.mesh.remove_doubles()
        m3.unselect_all("MESH")
        m3.set_mode("OBJECT")

        for v in cutter.data.vertices:
            for g in v.groups:
                if g.group == centeredges.index:  # compare with index in VertexGroupElement
                    v.select = True

        # remove everything but centeredges and bridge them
        m3.set_mode("EDIT")
        m3.set_mode("EDGE")
        m3.invert()
        bpy.ops.mesh.delete(type='EDGE')
        m3.select_all("MESH")
        bpy.ops.mesh.bridge_edge_loops()

        m3.set_mode("OBJECT")

        # remove CENTEREDGE vertex group
        cutter.vertex_groups.remove(centeredges)

        bpy.context.space_data.show_backface_culling = False

        if not self.hidepanel:
            paneldecal.hide = False
