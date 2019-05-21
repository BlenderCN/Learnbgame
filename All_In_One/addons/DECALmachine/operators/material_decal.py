import bpy
from bpy.props import BoolProperty, FloatProperty
from .. import M3utils as m3
from .. utils.operators import hide_meshes, intersect


class MaterialDecal(bpy.types.Operator):
    bl_idname = "machin3.material_decal"
    bl_label = "MACHIN3: Material Decal"
    bl_options = {'REGISTER', 'UNDO'}

    height = FloatProperty(name="Decal Height", default=-0.05)
    parent = BoolProperty(name="Parent", default=True)
    wstep = BoolProperty(name="Transfer Normals", default=True)
    wstepshow = BoolProperty(name="Show in Viewport", default=True)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "height")
        column.prop(self, "parent")

        row = column.row()
        row.prop(self, "wstep")
        row.prop(self, "wstepshow")

    def execute(self, context):
        if m3.DM_prefs().consistantscale:
            self.scene_scale = m3.get_scene_scale()
        else:
            self.scene_scale = 1

        self.midlevel = 1 - (0.0001 / self.scene_scale)  # 0.9999 for scene scale of 1.0

        self.material_decal()

        return {'FINISHED'}

    def material_decal(self):
        selection = m3.selected_objects()

        if len(selection) == 2:
            target = m3.get_active()
            selection.remove(target)
            cutter = selection[0]

            # make sure target geometry is not hidden and nothing is selected
            m3.set_mode("EDIT")
            m3.set_mode("FACE")
            bpy.ops.mesh.reveal()
            m3.unselect_all("MESH")
            m3.set_mode("OBJECT")

            # duplicating and timestamping the target, this duplicate will become the material decal
            matdecal = target.copy()
            matdecal.data = matdecal.data.copy()
            matdecal.name = "material_decal_" + target.name
            bpy.context.scene.objects.link(matdecal)
            timestamp = m3.set_timestamp(matdecal)

            # duplicating the cutter for potential future use
            cutterbackup = cutter.copy()
            cutterbackup.data = cutter.data.copy()
            cutterbackup.name = "backup_" + matdecal.name
            cutterbackup.use_fake_user = True
            m3.set_timestamp(cutterbackup, timestamp=timestamp)

            # selecting the decal and hiding the original target
            matdecal.select = True
            target.select = True
            target.hide = True

            # apply modifiers
            m3.make_active(matdecal)
            for mod in matdecal.modifiers:
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

            m3.make_active(cutter)
            for mod in cutter.modifiers:
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

            # hide cutter geometry
            # applying the bevel seems to unhide the edges of objects with hidden geo for some reason,
            # to make sure all is hidden we do the hiding after applying the mods

            matdecal.select = False
            # bpy.ops.machin3.hide_meshes()
            hide_meshes()
            matdecal.select = True

            # intersect
            m3.make_active(matdecal)
            intersect()

            # removing all inerersection geometry, except for the decal
            m3.set_mode("EDIT")
            m3.set_mode("FACE")
            m3.unselect_all("MESH")
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.delete(type='FACE')
            m3.set_mode("OBJECT")

            # removing all existing materials, as the user wants to apply a new one
            for slot in matdecal.material_slots:
                bpy.ops.object.material_slot_remove()

            # adding a slight displace to the decal
            displace = matdecal.modifiers.new(name="Displace", type="DISPLACE")

            # enough to avoid z-fighting, yet not enough to produce a noticable shadow when rendering
            # displace.mid_level = 0.99992
            displace.mid_level = self.midlevel - (self.height / 1000 / self.scene_scale)

            displace.show_in_editmode = True
            displace.show_on_cage = True

            # unhide the original target and select the decal
            target.hide = False
            matdecal.select = True

            # turn off shadow casting
            matdecal.cycles_visibility.shadow = False

            if self.wstep:
                #  make active the target to prepare for wstep
                m3.make_active(target)

                # transfer the normals from the target
                bpy.ops.machin3.wstep()

                # turn off viewport visibiity for performance reasons
                if not self.wstepshow:
                    mod = matdecal.modifiers.get("M3_copied_normals")
                    mod.show_viewport = False

            if self.parent:
                # matdecal.parent = target
                # matdecal.matrix_parent_inverse = target.matrix_world.inverted()

                # cutterbackup.parent = target
                # cutterbackup.matrix_parent_inverse = target.matrix_world.inverted()

                matdecal.select = True
                target.select = True
                m3.make_active(target)
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

                matdecal.select = False
                bpy.context.scene.objects.link(cutterbackup)
                cutterbackup.select = True
                bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                bpy.context.scene.objects.unlink(cutterbackup)

                target.select = False
                matdecal.select = True
                m3.make_active(matdecal)

            # unselect the target and make the material decal active, which might not be the case if self.wstep and self.paretn are both False
            target.select = False
            m3.make_active(matdecal)

            # add to group pro group
            if m3.GP_check():
                if m3.DM_prefs().groupproconnection:
                    if len(bpy.context.scene.storedGroupSettings) > 0:
                        bpy.ops.object.add_to_grouppro()

        else:
            # print("Select exactly two objets: the cutter and the object to cut!")
            self.report({'ERROR'}, "Select exactly two objets: the cutter and the object to project the material on!")

        return {'FINISHED'}
