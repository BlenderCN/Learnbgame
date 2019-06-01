import bpy
from bpy.props import FloatProperty, BoolProperty, IntProperty
from . panel_unwrap import panel_unwrap
from .. utils.operators import append_paneling_material
from .. import M3utils as m3


class Panelize(bpy.types.Operator):
    bl_idname = "machin3.decal_panelize"
    bl_label = "MACHIN3: Panelize"
    bl_options = {'REGISTER', 'UNDO'}

    panelwidth = FloatProperty(name="Panel Width", default=20, min=0.01)
    height = FloatProperty(name="Decal Height", default=0)

    individual = BoolProperty(name="Individual", default=False)
    individualgap = FloatProperty(name="Gap", default=1, min=0.01)

    bevel = BoolProperty(name="Bevel", default=False)
    bevelamount = FloatProperty(name="Amount", default=5, min=0.01)
    bevelsegments = IntProperty(name="Segments", default=1, min=1)

    rotateUVs = BoolProperty(name="Rotate UVs", default=True)
    flip = BoolProperty(name="Flip Normals", default=False)
    showwire = BoolProperty(name="Show Wire", default=True)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "panelwidth")
        col.prop(self, "height")

        row = col.row()
        row.prop(self, "individual")
        row.prop(self, "individualgap")

        # row = col.row()
        row = col.split(percentage=0.2)
        row.prop(self, "bevel")
        row.prop(self, "bevelamount")
        row.prop(self, "bevelsegments")

        col.prop(self, "rotateUVs")
        col.prop(self, "flip")

    def execute(self, context):
        if m3.DM_prefs().consistantscale:
            self.scene_scale = m3.get_scene_scale()
        else:
            self.scene_scale = 1

        self.midlevel = 1 - (0.0001 / self.scene_scale)  # 0.9999 for scene scale of 1.0
        self.pwidth = self.panelwidth / 100 / self.scene_scale
        self.gap = self.individualgap / 100 / self.scene_scale
        self.amount = self.bevelamount / 100 / self.scene_scale

        mode = m3.get_mode()

        if mode == "OBJECT":
            selection = m3.selected_objects()
            if len(selection) > 0:
                active = m3.get_active()
                self.panelize(selection, active)
            else:
                self.report({'ERROR'}, "Select at least one object!")
        else:
            self.report({'ERROR'}, "Execute in Object mode.")

        return {'FINISHED'}

    def panelize(self, selection, active):
        for obj in selection:
            m3.make_active(obj)

            # apply bevel mod, if there is any
            for mod in obj.modifiers:
                if mod.type == "BEVEL":
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

            m3.set_mode("EDIT")
            m3.set_mode("FACE")
            m3.unhide_all("MESH")
            m3.select_all("MESH")

            if self.individual:
                bpy.ops.mesh.inset(use_boundary=True, use_even_offset=True, thickness=self.gap, depth=0, use_outset=False, use_select_inset=True, use_individual=True, use_interpolate=True)
                bpy.ops.mesh.delete(type='FACE')
                m3.select_all("MESH")

            # inset the polygons
            bpy.ops.mesh.inset(use_boundary=True, use_even_offset=True, thickness=self.pwidth, depth=0, use_outset=False, use_select_inset=False, use_individual=False, use_interpolate=True)

            # delete the central part (still selected) - this creates the decal strip
            bpy.ops.mesh.delete(type='FACE')

            if self.bevel:
                m3.select_all("MESH")
                bpy.ops.mesh.region_to_loop()
                m3.invert()

                bpy.ops.mesh.bevel(offset=self.amount, segments=self.bevelsegments, vertex_only=False)

            # optionally flip normals
            if self.flip:
                m3.select_all("MESH")
                bpy.ops.mesh.flip_normals()
            m3.set_mode("OBJECT")
            obj.name = "panel_decal"

            # adding a slight displace to the panel decal
            displace = obj.modifiers.new(name="Displace", type="DISPLACE")

            # enough to avoid z-fighting, yet not enough to produce a noticable shadow when rendering
            displace.mid_level = self.midlevel - (self.height / 1000 / self.scene_scale)
            displace.show_in_editmode = True
            displace.show_on_cage = True

            # cleaning out all materials of the panelstrip
            for slot in obj.material_slots:
                bpy.ops.object.material_slot_remove()

            defaultpaneling = bpy.context.scene.decals.defaultpaneling
            panelingmat = bpy.data.materials.get(defaultpaneling)

            if panelingmat:
                obj.data.materials.append(panelingmat)
            else:
                try:
                    panelingmat = append_paneling_material(defaultpaneling)  # > paneling01_1
                    obj.data.materials.append(panelingmat)
                except:
                    self.report({'ERROR'}, "Could not find paneling01_01 decal and material, make sure the Decals asset library is in your DECALmachine folder!")

            # UVs
            try:
                panel_unwrap(obj, knife=self.rotateUVs)
            except:
                self.report({'ERROR'}, "Panelize only works on open meshes!")
                m3.set_mode("OBJECT")
                bpy.ops.ed.undo_push(message="MACHIN3: Panelize")
                bpy.ops.ed.undo()
                return

            # enable wire display
            if self.showwire:
                obj.show_wire = True
                obj.show_all_edges = True

            # make panel strip smooth shaded
            bpy.ops.object.shade_smooth()

        # reset original selection and active
        for obj in selection:
            obj.select = True

        m3.make_active(active)
