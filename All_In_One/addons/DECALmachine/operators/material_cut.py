import bpy
from bpy.props import BoolProperty, FloatProperty
from .. import M3utils as m3
from .. utils.operators import hide_meshes


class MaterialCut(bpy.types.Operator):
    bl_idname = "machin3.material_cut"
    bl_label = "MACHIN3: Material Cut"
    bl_options = {'REGISTER', 'UNDO'}

    mergeparts = BoolProperty(name="Merge Parts", default=True)
    mergethreshold = FloatProperty(name="Threshold", default=0.0001, min=0, precision=4, step=0.01)

    markseams = BoolProperty(name="Mark Seams", default=True)
    markfreestyle = BoolProperty(name="Mark Freestyle", default=False)
    showwire = BoolProperty(name="Turn on Wire", default=True)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()

        row.prop(self, "mergeparts")
        row.prop(self, "mergethreshold")

        row = column.row()
        row.prop(self, "markseams")
        row.prop(self, "markfreestyle")

        column.prop(self, "showwire")

    def execute(self, context):
        selection = m3.selected_objects()

        if len(selection) == 2:
            self.material_cut(selection)
        else:
            self.report({'ERROR'}, "Select exactly two objets: the cutter and the object to cut!")

        return {'FINISHED'}

    def material_cut(self, selection):
        target = m3.get_active()
        selection.remove(target)
        cutter = selection[0]

        # make sure target geometry is not hidden and nothing is selected
        m3.set_mode("EDIT")
        m3.set_mode("FACE")
        bpy.ops.mesh.reveal()
        m3.unselect_all("MESH")
        m3.set_mode("OBJECT")

        # apply modifiers
        for mod in target.modifiers:
            if mod.type == "BEVEL":
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

        m3.make_active(cutter)
        for mod in cutter.modifiers:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

        # hide cutter geometry
        # applying the bevel seems to unhide the edges for some reason,
        # to make sure all is hidden we do the hiding after applying the mods
        # for the cutter
        target.select = False
        m3.make_active(cutter)
        # bpy.ops.machin3.hide_meshes()
        hide_meshes()

        # cleanout all material of the cutter, while it is active
        for slot in cutter.material_slots:
            bpy.ops.object.material_slot_remove()

        # create temporary cutter material
        cuttermat = bpy.data.materials.new("cutter_material")

        # assign it
        cutter.data.materials.append(cuttermat)

        # reselecting the target
        target.select = True

        # join cutter and target
        m3.make_active(target)
        bpy.ops.object.join()

        # revealing will now select only the cutter geometry
        m3.set_mode("EDIT")
        bpy.ops.mesh.reveal()

        # intersect, there will be 4 parts now all separated
        if bpy.app.version < (2, 79, 0):
            bpy.ops.mesh.intersect()
        elif bpy.app.version >= (2, 79, 0):
            bpy.ops.mesh.intersect(separate_mode='ALL')

        # we are now removing the cutter by selecting the cutter mat polygons
        m3.set_mode("OBJECT")

        # find the slot of the cuttermat on the now joined object
        for idx, slot in enumerate(target.material_slots):
            if slot.material.name == "cutter_material":
                cuttermatslot = idx
                break

        # select all the cutter polygons
        mesh = bpy.context.active_object.data

        for f in mesh.polygons:
            if f.material_index == cuttermatslot:
                f.select = True
            else:
                f.select = False

        # remove just the cutter_material from the object
        bpy.context.object.active_material_index = cuttermatslot
        bpy.ops.object.material_slot_remove()

        # remove it from the scene as well
        bpy.data.materials.remove(cuttermat, do_unlink=True)

        # delete the cutter polygons
        m3.set_mode("EDIT")
        bpy.ops.mesh.delete(type='FACE')

        # the parts are still separate at this point, so mark the boundary edges as seams and remove doubles
        m3.select_all("MESH")
        bpy.ops.mesh.region_to_loop()

        if self.markseams:
            bpy.ops.mesh.mark_seam(clear=False)

        if self.markfreestyle:
            bpy.ops.mesh.mark_freestyle_edge(clear=False)

        if self.mergeparts:
            bpy.ops.mesh.remove_doubles(threshold=self.mergethreshold)

        if self.showwire:
            target.show_wire = True
            target.show_all_edges = True

        m3.set_mode("OBJECT")

        return {'FINISHED'}


class ConvertSeamToFreestyle(bpy.types.Operator):
    bl_idname = "machin3.convert_seam_to_freestyle"
    bl_label = "MACHIN3: Convert Seam To Freestyle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        for obj in m3.selected_objects():
            if obj.type == "MESH":
                mesh = obj.data

                for edge in mesh.edges:
                    if edge.use_seam:
                        edge.use_seam = False
                        edge.use_freestyle_mark = True

        return {'FINISHED'}


class ConvertFreestyletoSeam(bpy.types.Operator):
    bl_idname = "machin3.convert_freestyle_to_seam"
    bl_label = "MACHIN3: Convert Freestyle To Seam"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in m3.selected_objects():
            if obj.type == "MESH":
                mesh = obj.data
                mesh.show_edge_seams = True

                for edge in mesh.edges:
                    if edge.use_freestyle_mark:
                        edge.use_freestyle_mark = False
                        edge.use_seam = True

        return {'FINISHED'}
