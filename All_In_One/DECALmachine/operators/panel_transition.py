import bpy
from .. import M3utils as m3
from .. utils.operators import hide_meshes


class PanelTransition(bpy.types.Operator):
    bl_idname = "machin3.decal_panel_transition"
    bl_label = "MACHIN3: Decal Panel Transition"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.scene_scale = m3.get_scene_scale()
        self.add_height = 0.1 / 1000

        selection = m3.selected_objects()

        if len(selection) == 2:
            self.panel_transition(selection)
        else:
            self.report({'ERROR'}, "Select exactly two panel strips objets: a panel strip and another panel strip it should transition into!")

        return {'FINISHED'}

    def panel_transition(self, selection):
        cutterpanelorig = m3.get_active()
        selection.remove(cutterpanelorig)
        transitionpanel = selection[0]

        # if there are unjoined panel strips in the panel, the result can be unexpected
        # so first, make sure to remove doubles for both of them

        transitionpanel.select = False

        m3.set_mode("EDIT")
        m3.set_mode("VERT")
        m3.unhide_all("MESH")
        m3.select_all("MESH")
        m3.set_mode("VERT")
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        m3.set_mode("OBJECT")
        cutterpanelorig.select = False

        transitionpanel.select = True
        m3.make_active(transitionpanel)
        m3.set_mode("EDIT")
        m3.set_mode("VERT")
        m3.unhide_all("MESH")
        m3.select_all("MESH")
        m3.set_mode("VERT")
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        # also make sure nothing is selected
        m3.unselect_all("MESH")
        m3.set_mode("OBJECT")

        cutterpanelorig.select = True
        m3.make_active(cutterpanelorig)

        # duplicate cutterpanelorig
        cutterpanel = cutterpanelorig.copy()
        cutterpanel.data = cutterpanelorig.data.copy()
        bpy.context.scene.objects.link(cutterpanel)

        cutterpanelorig.select = False
        cutterpanelorig.hide = True

        # create temp material and add it to cutterpanel
        cuttermat = bpy.data.materials.new("cutter_material")
        cutterpanel.material_slots[0].material = cuttermat

        # add thickness to cutterpabel
        solidify = cutterpanel.modifiers.new(name="Solidify", type="SOLIDIFY")
        solidify.offset = 0
        solidify.thickness = 0.1

        m3.make_active(cutterpanel)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=solidify.name)

        # hide cutterpanel geometry
        transitionpanel.select = False
        hide_meshes()
        transitionpanel.select = True

        # join cutterpanel and transitionpanel
        m3.make_active(transitionpanel)
        bpy.ops.object.join()

        # revealing will now select only the cutterpanel geometry
        m3.set_mode("EDIT")
        m3.unhide_all("MESH")

        # intersect, there will be 4 parts now all separated
        if bpy.app.version < (2, 79, 0):
            bpy.ops.mesh.intersect()
        elif bpy.app.version >= (2, 79, 0):
            bpy.ops.mesh.intersect(separate_mode='ALL')

        m3.unselect_all("MESH")
        m3.set_mode("OBJECT")

        # find the slot of the cuttermat on the now joined object
        for idx, slot in enumerate(transitionpanel.material_slots):
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

        # lifting the transitional panel once
        for mod in transitionpanel.modifiers:
            if "displace" in mod.name.lower():
                mod.mid_level = mod.mid_level - (self.add_height / self.scene_scale)

        # unhiding the original panel again
        cutterpanelorig.hide = False

        return {'FINISHED'}
